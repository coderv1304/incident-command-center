package com.codechill.incidentapi;

import org.springframework.web.bind.annotation.*;
import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "http://localhost:3000")
public class IncidentController {

    @GetMapping("/incidents")
    public List<Incident> getIncidents() {
        List<Incident> incidents = new ArrayList<>();

        incidents.add(new Incident(
                "INC-001",
                "2026-09-17T10:30:00",
                "github-actions",
                "Error: Cannot find module 'express'",
                "The build failed because the 'express' package is missing. Run 'npm install express' and try again.",
                "HIGH",
                "OPEN"
        ));

        incidents.add(new Incident(
                "INC-002",
                "2026-09-17T11:15:00",
                "github-actions",
                "TypeError: undefined is not a function at line 42",
                "There is a type error on line 42. You are calling a function on something that is undefined. Check that the variable is initialized before use.",
                "MEDIUM",
                "OPEN"
        ));

        incidents.add(new Incident(
                "INC-003",
                "2026-09-17T09:05:00",
                "github-actions",
                "npm ERR! code ENOENT - package.json not found",
                "The build system could not find package.json. This usually means the working directory is wrong or the file was accidentally deleted.",
                "HIGH",
                "RESOLVED"
        ));

        incidents.add(new Incident(
                "INC-004",
                "2026-09-16T16:20:00",
                "github-actions",
                "Error: EADDRINUSE: address already in use :::3000",
                "Port 3000 is already in use by another process. Kill the process using 'npx kill-port 3000' or change to a different port.",
                "LOW",
                "RESOLVED"
        ));

        incidents.add(new Incident(
                "INC-005",
                "2026-09-16T14:10:00",
                "github-actions",
                "FAIL src/tests/auth.test.js - Expected 200 but received 401",
                "An authentication test failed. The endpoint returned 401 Unauthorized instead of 200 OK. Check the auth token handling in your request.",
                "MEDIUM",
                "RESOLVED"
        ));

        incidents.add(new Incident(
                "INC-006",
                "2026-09-16T11:45:00",
                "github-actions",
                "docker: Error response from daemon: pull access denied",
                "Docker could not pull the image. Either the image name is wrong, or you need to run 'docker login' first.",
                "HIGH",
                "RESOLVED"
        ));

        incidents.add(new Incident(
                "INC-007",
                "2026-09-15T17:30:00",
                "github-actions",
                "ERROR: Missing required environment variable DATABASE_URL",
                "The app tried to start but DATABASE_URL was not set. Add it to your .env file or set it in your CI environment variables.",
                "HIGH",
                "RESOLVED"
        ));

        incidents.add(new Incident(
                "INC-008",
                "2026-09-15T13:00:00",
                "github-actions",
                "warning: LF will be replaced by CRLF in index.js",
                "Just a line-ending warning, not a real failure. Safe to ignore or configure .gitattributes to fix.",
                "LOW",
                "RESOLVED"
        ));

        return incidents;
    }
}