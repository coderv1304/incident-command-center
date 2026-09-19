import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    fetchIncidents();
    const refreshInterval = setInterval(fetchIncidents, 30000);
    const clockInterval = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => {
      clearInterval(refreshInterval);
      clearInterval(clockInterval);
    };
  }, []);

  const fetchIncidents = () => {
    axios.get('http://localhost:8081/api/incidents')
      .then(response => {
        setIncidents(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching incidents:', error);
        setLoading(false);
      });
  };

  const getSeverityColor = (severity) => {
    if (severity === 'HIGH') return '#ef4444';
    if (severity === 'MEDIUM') return '#f59e0b';
    return '#10b981';
  };

  const getSeverityGlow = (severity) => {
    if (severity === 'HIGH') return '0 0 20px rgba(239, 68, 68, 0.4)';
    if (severity === 'MEDIUM') return '0 0 20px rgba(245, 158, 11, 0.4)';
    return '0 0 20px rgba(16, 185, 129, 0.4)';
  };

  // Stats
  const totalIncidents = incidents.length;
  const openIncidents = incidents.filter(i => i.status === 'OPEN').length;
  const highSeverity = incidents.filter(i => i.severity === 'HIGH').length;
  const resolvedIncidents = incidents.filter(i => i.status === 'RESOLVED').length;
  const resolutionRate = totalIncidents ? Math.round((resolvedIncidents / totalIncidents) * 100) : 0;

  const highCount = incidents.filter(i => i.severity === 'HIGH').length;
  const medCount = incidents.filter(i => i.severity === 'MEDIUM').length;
  const lowCount = incidents.filter(i => i.severity === 'LOW').length;

  // Filtered
  const filteredIncidents = incidents.filter(i => {
    const matchesSearch =
      i.incident_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      i.ai_explanation.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = severityFilter === 'ALL' || i.severity === severityFilter;
    return matchesSearch && matchesSeverity;
  });

  // Donut chart calc
  const donutTotal = highCount + medCount + lowCount || 1;
  const highPct = (highCount / donutTotal) * 100;
  const medPct = (medCount / donutTotal) * 100;
  const lowPct = (lowCount / donutTotal) * 100;

  // Donut offsets
  const circumference = 2 * Math.PI * 70;
  const highDash = (highPct / 100) * circumference;
  const medDash = (medPct / 100) * circumference;
  const lowDash = (lowPct / 100) * circumference;

  return (
    <div className="App">
      {/* Top ticker */}
      <div className="ticker">
        <div className="ticker-content">
          ⚡ LIVE MONITORING · {totalIncidents} incidents tracked · {openIncidents} open · Auto-refresh every 30s ·
          ⚡ LIVE MONITORING · {totalIncidents} incidents tracked · {openIncidents} open · Auto-refresh every 30s ·
        </div>
      </div>

      {/* Header */}
      <header className="header">
        <div className="header-left">
          <div className="logo">⚡</div>
          <div>
            <h1>AI Incident Command Center</h1>
            <p>Real-time pipeline failure detection & AI explanation</p>
          </div>
        </div>
        <div className="header-right">
          <div className="clock">
            <div className="clock-time">
              {currentTime.toLocaleTimeString('en-US', { hour12: false })}
            </div>
            <div className="clock-date">
              {currentTime.toLocaleDateString('en-US', {
                weekday: 'short', month: 'short', day: 'numeric'
              })}
            </div>
          </div>
          <div className="live-badge">
            <span className="live-dot"></span>
            LIVE
          </div>
        </div>
      </header>

      {/* KPI Stats */}
      <div className="stats-grid">
        <div className="stat-card stat-blue">
          <div className="stat-top">
            <span className="stat-icon">📊</span>
            <span className="stat-trend trend-up">+100%</span>
          </div>
          <div className="stat-value">{totalIncidents}</div>
          <div className="stat-label">Total Incidents</div>
          <div className="stat-glow"></div>
        </div>

        <div className="stat-card stat-red">
          <div className="stat-top">
            <span className="stat-icon">🔴</span>
            <span className="stat-trend trend-up">Active</span>
          </div>
          <div className="stat-value">{openIncidents}</div>
          <div className="stat-label">Open Incidents</div>
          <div className="stat-glow"></div>
        </div>

        <div className="stat-card stat-orange">
          <div className="stat-top">
            <span className="stat-icon">⚠️</span>
            <span className="stat-trend trend-up">Critical</span>
          </div>
          <div className="stat-value">{highSeverity}</div>
          <div className="stat-label">High Severity</div>
          <div className="stat-glow"></div>
        </div>

        <div className="stat-card stat-green">
          <div className="stat-top">
            <span className="stat-icon">✅</span>
            <span className="stat-trend trend-down">{resolutionRate}%</span>
          </div>
          <div className="stat-value">{resolvedIncidents}</div>
          <div className="stat-label">Resolved</div>
          <div className="stat-glow"></div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="charts-grid">
        {/* Donut Chart */}
        <div className="chart-card">
          <h3 className="chart-title">Severity Distribution</h3>
          <div className="donut-container">
            <svg width="200" height="200" viewBox="0 0 200 200" className="donut-svg">
              <circle cx="100" cy="100" r="70" fill="none" stroke="#1e293b" strokeWidth="20" />
              <circle
                cx="100" cy="100" r="70" fill="none"
                stroke="#ef4444" strokeWidth="20"
                strokeDasharray={`${highDash} ${circumference}`}
                strokeDashoffset="0"
                transform="rotate(-90 100 100)"
                strokeLinecap="round"
              />
              <circle
                cx="100" cy="100" r="70" fill="none"
                stroke="#f59e0b" strokeWidth="20"
                strokeDasharray={`${medDash} ${circumference}`}
                strokeDashoffset={`-${highDash}`}
                transform="rotate(-90 100 100)"
                strokeLinecap="round"
              />
              <circle
                cx="100" cy="100" r="70" fill="none"
                stroke="#10b981" strokeWidth="20"
                strokeDasharray={`${lowDash} ${circumference}`}
                strokeDashoffset={`-${highDash + medDash}`}
                transform="rotate(-90 100 100)"
                strokeLinecap="round"
              />
              <text x="100" y="95" textAnchor="middle" fill="#f1f5f9" fontSize="28" fontWeight="700">
                {donutTotal}
              </text>
              <text x="100" y="118" textAnchor="middle" fill="#64748b" fontSize="11" fontWeight="600">
                TOTAL
              </text>
            </svg>
            <div className="donut-legend">
              <div className="legend-row">
                <span className="legend-dot" style={{ background: '#ef4444' }}></span>
                <span className="legend-label">High</span>
                <span className="legend-value">{highCount}</span>
              </div>
              <div className="legend-row">
                <span className="legend-dot" style={{ background: '#f59e0b' }}></span>
                <span className="legend-label">Medium</span>
                <span className="legend-value">{medCount}</span>
              </div>
              <div className="legend-row">
                <span className="legend-dot" style={{ background: '#10b981' }}></span>
                <span className="legend-label">Low</span>
                <span className="legend-value">{lowCount}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Bars */}
        <div className="chart-card">
          <h3 className="chart-title">System Health</h3>
          <div className="progress-list">
            <div className="progress-item">
              <div className="progress-header">
                <span>Resolution Rate</span>
                <span className="progress-value">{resolutionRate}%</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${resolutionRate}%`, background: 'linear-gradient(90deg, #10b981, #34d399)' }}></div>
              </div>
            </div>
            <div className="progress-item">
              <div className="progress-header">
                <span>Critical Ratio</span>
                <span className="progress-value">{totalIncidents ? Math.round((highCount / totalIncidents) * 100) : 0}%</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${totalIncidents ? (highCount / totalIncidents) * 100 : 0}%`, background: 'linear-gradient(90deg, #ef4444, #f87171)' }}></div>
              </div>
            </div>
            <div className="progress-item">
              <div className="progress-header">
                <span>Open Incidents</span>
                <span className="progress-value">{totalIncidents ? Math.round((openIncidents / totalIncidents) * 100) : 0}%</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${totalIncidents ? (openIncidents / totalIncidents) * 100 : 0}%`, background: 'linear-gradient(90deg, #f59e0b, #fbbf24)' }}></div>
              </div>
            </div>
          </div>
          <div className="status-summary">
            <div className="status-item">
              <div className="status-dot" style={{ background: '#10b981', boxShadow: '0 0 12px #10b981' }}></div>
              <div>
                <div className="status-number">{resolvedIncidents}</div>
                <div className="status-label">Resolved</div>
              </div>
            </div>
            <div className="status-item">
              <div className="status-dot" style={{ background: '#ef4444', boxShadow: '0 0 12px #ef4444' }}></div>
              <div>
                <div className="status-number">{openIncidents}</div>
                <div className="status-label">Open</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <div className="search-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="search-box"
            placeholder="Search incidents by ID or explanation..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-buttons">
          {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map(sev => (
            <button
              key={sev}
              className={`filter-btn ${severityFilter === sev ? 'active' : ''} filter-${sev.toLowerCase()}`}
              onClick={() => setSeverityFilter(sev)}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Incident List */}
      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading incidents...</p>
        </div>
      ) : filteredIncidents.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">✓</div>
          <h3>No incidents match your filters</h3>
          <p>Try changing the search or filter settings</p>
        </div>
      ) : (
        <div className="incident-list">
          <div className="list-header">
            <h3>Incident Feed</h3>
            <span className="list-count">{filteredIncidents.length} shown</span>
          </div>
          {filteredIncidents.map(incident => (
            <div
              key={incident.incident_id}
              className="incident-card"
              style={{ boxShadow: getSeverityGlow(incident.severity) }}
            >
              <div className="incident-accent" style={{ background: getSeverityColor(incident.severity) }}></div>

              <div className="incident-header">
                <div className="incident-title">
                  <span className="incident-id">{incident.incident_id}</span>
                  <span className={`status-pill ${incident.status.toLowerCase()}`}>
                    {incident.status}
                  </span>
                </div>
                <span
                  className="severity-badge"
                  style={{
                    backgroundColor: getSeverityColor(incident.severity),
                    boxShadow: getSeverityGlow(incident.severity)
                  }}
                >
                  {incident.severity}
                </span>
              </div>

              <div className="incident-meta">
                <span className="meta-item">
                  <span className="meta-icon">🕐</span>
                  {new Date(incident.timestamp).toLocaleString()}
                </span>
                <span className="meta-item">
                  <span className="meta-icon">📦</span>
                  {incident.source}
                </span>
                <span className="meta-item">
                  <span className="meta-icon">⚙️</span>
                  pipeline
                </span>
              </div>

              <div className="ai-explanation">
                <div className="ai-label">
                  <span className="ai-dot"></span>
                  AI ROOT CAUSE ANALYSIS
                </div>
                <p>{incident.ai_explanation}</p>
              </div>

              <details className="raw-log">
                <summary>
                  <span className="log-icon">▸</span> View raw log
                </summary>
                <pre>{incident.raw_log}</pre>
              </details>
            </div>
          ))}
        </div>
      )}

      <footer className="footer">
        <div>Code&Chill · First Commit Hackathon 2026</div>
        <div className="footer-team">Varun · Rahul · Prapti</div>
      </footer>
    </div>
  );
}

export default App;