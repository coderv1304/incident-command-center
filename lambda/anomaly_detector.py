import math
from typing import List, Dict, Any

def calculate_z_score_anomaly(history_counts: List[int], current_count: int) -> Dict[str, Any]:
    """
    Computes a simple statistical z-score check to detect unusual error spikes
    before they escalate into full system outages.
    
    Stretch Goal for Rahul (AI Layer) per project specifications:
    Kept simple, lightweight, and statistical — no heavy ML training required.
    """
    if not history_counts:
        return {
            "z_score": 0.0,
            "is_anomaly": False,
            "confidence": "insufficient_data",
            "message": "First failure observed; baseline establishing."
        }

    n = len(history_counts)
    mean = sum(history_counts) / n
    variance = sum((x - mean) ** 2 for x in history_counts) / n
    std_dev = math.sqrt(variance)

    if std_dev == 0:
        z_score = 0.0 if current_count == mean else 3.0
    else:
        z_score = (current_count - mean) / std_dev

    # Threshold of z >= 2.0 flags an anomaly (95th percentile spike in standard normal distribution)
    is_anomaly = z_score >= 2.0

    return {
        "z_score": round(z_score, 2),
        "mean_baseline": round(mean, 2),
        "current_frequency": current_count,
        "is_anomaly": is_anomaly,
        "classification": "SPIKE_ANOMALY" if is_anomaly else "NORMAL_PATTERN",
        "message": f"Failure rate is {'statistically anomalous (+%.1f std dev)' % z_score if is_anomaly else 'within expected baseline bounds.'}"
    }

