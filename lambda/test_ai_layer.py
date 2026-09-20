import unittest
import json
from bedrock_service import analyze_log_with_bedrock, _clean_and_parse_json, _heuristic_fallback
from log_handler import build_incident_record
from anomaly_detector import calculate_z_score_anomaly


class TestBedrockAILayer(unittest.TestCase):
    """
    Unit test suite for Rahul's Bedrock AI Layer and Incident Record pipeline.
    Runs locally without needing live AWS credentials.
    """

    def setUp(self):
        self.sample_error_log = (
            "ERROR: npm install failed\n"
            "Reason: Could not resolve dependency 'react-router-dom@7.0.0'\n"
            "peer react@\"^18.0.0\" from react-router-dom@7.0.0\n"
            "Found: react@17.0.2\n"
            "Fix the version mismatch and re-run the pipeline."
        )

    def test_json_clean_and_parse_valid(self):
        """Verify markdown JSON stripping and parsing."""
        raw_model_response = """```json
{
  "ai_explanation": "React router version conflict.",
  "suggested_fix": "Upgrade React to 18.",
  "severity": "HIGH"
}
```"""
        parsed = _clean_and_parse_json(raw_model_response)
        self.assertEqual(parsed["severity"], "HIGH")
        self.assertEqual(parsed["suggested_fix"], "Upgrade React to 18.")
        self.assertIn("React router", parsed["ai_explanation"])

    def test_heuristic_fallback_high_severity(self):
        """Verify fallback detects critical dependency/syntax errors as HIGH severity."""
        result = _heuristic_fallback(self.sample_error_log)
        self.assertEqual(result["severity"], "HIGH")
        self.assertTrue(len(result["ai_explanation"]) > 0)
        self.assertTrue(len(result["suggested_fix"]) > 0)

    def test_heuristic_fallback_medium_severity(self):
        """Verify fallback detects standard runtime errors as MEDIUM severity."""
        type_error_log = "TypeError: Cannot read property 'map' of undefined at Component.js:24"
        result = _heuristic_fallback(type_error_log)
        self.assertEqual(result["severity"], "MEDIUM")

    def test_analyze_empty_log_handled_gracefully(self):
        """Verify empty log strings do not raise unhandled exceptions."""
        result = analyze_log_with_bedrock("")
        self.assertIn("ai_explanation", result)
        self.assertEqual(result["severity"], "LOW")

    def test_build_incident_record_contract(self):
        """Verify generated incident record conforms strictly to the DynamoDB & API schema."""
        record = build_incident_record(self.sample_error_log, source="github-actions-test")

        # Required fields in locked contract
        required_keys = [
            "incident_id",
            "timestamp",
            "source",
            "raw_log",
            "ai_explanation",
            "suggested_fix",
            "severity",
            "status"
        ]
        for key in required_keys:
            self.assertIn(key, record, f"Missing required contract key: {key}")

        self.assertEqual(record["source"], "github-actions-test")
        self.assertEqual(record["raw_log"], self.sample_error_log)
        self.assertIn(record["severity"], ["HIGH", "MEDIUM", "LOW"])
        self.assertIn(record["status"], ["OPEN", "new"])

    def test_anomaly_detector_detects_spike(self):
        """Verify z-score anomaly check flags sudden error frequency surges."""
        # Baseline of 1-2 errors per hour, followed by sudden spike of 8 errors
        baseline = [1, 2, 1, 1, 2, 1]
        spike_count = 8
        result = calculate_z_score_anomaly(baseline, spike_count)

        self.assertTrue(result["is_anomaly"])
        self.assertGreaterEqual(result["z_score"], 2.0)
        self.assertEqual(result["classification"], "SPIKE_ANOMALY")

    def test_anomaly_detector_normal_baseline(self):
        """Verify normal variations within baseline are NOT flagged as anomalies."""
        baseline = [2, 2, 3, 2, 2, 3]
        normal_count = 2
        result = calculate_z_score_anomaly(baseline, normal_count)

        self.assertFalse(result["is_anomaly"])
        self.assertLess(result["z_score"], 2.0)
        self.assertEqual(result["classification"], "NORMAL_PATTERN")


if __name__ == "__main__":
    unittest.main()

