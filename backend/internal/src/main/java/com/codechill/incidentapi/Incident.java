package com.codechill.incidentapi;

public class Incident {
    private String incident_id;
    private String timestamp;
    private String source;
    private String raw_log;
    private String ai_explanation;
    private String severity;
    private String status;

    public Incident(String incident_id, String timestamp, String source,
                    String raw_log, String ai_explanation,
                    String severity, String status) {
        this.incident_id = incident_id;
        this.timestamp = timestamp;
        this.source = source;
        this.raw_log = raw_log;
        this.ai_explanation = ai_explanation;
        this.severity = severity;
        this.status = status;
    }

    public String getIncident_id() { return incident_id; }
    public String getTimestamp() { return timestamp; }
    public String getSource() { return source; }
    public String getRaw_log() { return raw_log; }
    public String getAi_explanation() { return ai_explanation; }
    public String getSeverity() { return severity; }
    public String getStatus() { return status; }
}