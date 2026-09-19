package com.codechill.incidentapi.service;

import com.codechill.incidentapi.Incident;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
public class IncidentService {

    private static final String TABLE_NAME = "IncidentRecords";

    @Autowired
    private DynamoDbClient dynamoDbClient;

    public List<Incident> getAllIncidents() {
        ScanRequest scanRequest = ScanRequest.builder()
                .tableName(TABLE_NAME)
                .build();
        ScanResponse response = dynamoDbClient.scan(scanRequest);

        List<Incident> incidents = new ArrayList<>();
        for (Map<String, AttributeValue> item : response.items()) {
            incidents.add(mapToIncident(item));
        }

        // most recent first
        incidents.sort((a, b) -> {
            String ta = a.getTimestamp() == null ? "" : a.getTimestamp();
            String tb = b.getTimestamp() == null ? "" : b.getTimestamp();
            return tb.compareTo(ta);
        });

        return incidents;
    }

    private Incident mapToIncident(Map<String, AttributeValue> item) {
        Incident incident = new Incident();
        incident.setIncident_id(getStringValue(item, "incident_id"));
        incident.setTimestamp(getStringValue(item, "timestamp"));
        incident.setSource(getStringValue(item, "source"));
        incident.setRaw_log(getStringValue(item, "raw_log"));
        incident.setAi_explanation(getStringValue(item, "ai_explanation"));
        incident.setSuggested_fix(getStringValue(item, "suggested_fix"));
        incident.setSeverity(getStringValue(item, "severity"));
        incident.setStatus(getStringValue(item, "status"));
        return incident;
    }

    private String getStringValue(Map<String, AttributeValue> item, String key) {
        AttributeValue value = item.get(key);
        return (value != null && value.s() != null) ? value.s() : "";
    }
}