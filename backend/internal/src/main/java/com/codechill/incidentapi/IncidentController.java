package com.codechill.incidentapi;

import com.codechill.incidentapi.service.IncidentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "http://localhost:3000")
public class IncidentController {

    @Autowired
    private IncidentService incidentService;

    @GetMapping("/incidents")
    public List<Incident> getIncidents() {
        return incidentService.getAllIncidents();
    }
}