package com.codechill.incidentapi;

public class Incident {
    private String incident_id;
    private String timestamp;
    private String source;
    private String raw_log;
    private String ai_explanation;
    private String suggested_fix;
    private String severity;
    private String status;

    public Incident() {}

    public Incident(String incident_id, String timestamp, String source,
                    String raw_log, String ai_explanation, String suggested_fix,
                    String severity, String status) {
        this.incident_id = incident_id;
        this.timestamp = timestamp;
        this.source = source;
        this.raw_log = raw_log;
        this.ai_explanation = ai_explanation;
        this.suggested_fix = suggested_fix;
        this.severity = severity;
        this.status = status;
    }

    public String getIncident_id() { return incident_id; }
    public void setIncident_id(String incident_id) { this.incident_id = incident_id; }

    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }

    public String getSource() { return source; }
    public void setSource(String source) { this.source = source; }

    public String getRaw_log() { return raw_log; }
    public void setRaw_log(String raw_log) { this.raw_log = raw_log; }

    public String getAi_explanation() { return ai_explanation; }
    public void setAi_explanation(String ai_explanation) { this.ai_explanation = ai_explanation; }

    public String getSuggested_fix() { return suggested_fix; }
    public void setSuggested_fix(String suggested_fix) { this.suggested_fix = suggested_fix; }

    public String getSeverity() { return severity; }
    public void setSeverity(String severity) { this.severity = severity; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}