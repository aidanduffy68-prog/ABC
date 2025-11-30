"""
Threat Monitoring Dashboard
Real-time dashboard for monitoring compiled intelligence and threats

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO, emit
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

from .api_server import compilation_engine, federal_monitor


app = Flask(__name__)
app.config['SECRET_KEY'] = 'gh-systems-dashboard'
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage (in production, use database)
threat_store = {
    "compilations": [],
    "federal_ai_scans": [],
    "alerts": [],
    "metrics": {
        "total_compilations": 0,
        "avg_compilation_time_ms": 0.0,
        "threats_by_level": defaultdict(int),
        "compilations_by_agency": defaultdict(int)
    }
}


# Dashboard HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ABC Threat Intelligence Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }
        .header {
            border-bottom: 2px solid #0066cc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #0099ff;
        }
        .metric-label {
            color: #888;
            margin-top: 5px;
        }
        .threat-list {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            max-height: 500px;
            overflow-y: auto;
        }
        .threat-item {
            border-left: 4px solid #ff4444;
            padding: 15px;
            margin-bottom: 10px;
            background: #0f0f0f;
        }
        .threat-item.critical { border-color: #ff0000; }
        .threat-item.high { border-color: #ff4444; }
        .threat-item.medium { border-color: #ffaa00; }
        .threat-item.low { border-color: #00ff00; }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-online { background: #00ff00; }
        .status-offline { background: #ff0000; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ABC Threat Intelligence Dashboard</h1>
        <p>Real-time monitoring of compiled intelligence and federal AI threats</p>
        <span class="status-indicator status-online" id="status"></span>
        <span id="status-text">Connected</span>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <div class="metric-value" id="total-compilations">0</div>
            <div class="metric-label">Total Compilations</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="avg-time">0ms</div>
            <div class="metric-label">Avg Compilation Time</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="critical-threats">0</div>
            <div class="metric-label">Critical Threats</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="federal-scans">0</div>
            <div class="metric-label">Federal AI Scans</div>
        </div>
    </div>
    
    <div class="threat-list">
        <h2>Recent Threats</h2>
        <div id="threat-list"></div>
    </div>
    
    <script>
        const socket = io();
        
        socket.on('connect', () => {
            document.getElementById('status').className = 'status-indicator status-online';
            document.getElementById('status-text').textContent = 'Connected';
        });
        
        socket.on('disconnect', () => {
            document.getElementById('status').className = 'status-indicator status-offline';
            document.getElementById('status-text').textContent = 'Disconnected';
        });
        
        socket.on('intelligence_compiled', (data) => {
            updateMetrics();
            addThreatItem(data);
        });
        
        socket.on('federal_ai_scan_complete', (data) => {
            updateMetrics();
        });
        
        socket.on('alert', (data) => {
            addThreatItem(data, true);
        });
        
        function updateMetrics() {
            fetch('/api/v1/dashboard/metrics')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('total-compilations').textContent = data.total_compilations;
                    document.getElementById('avg-time').textContent = data.avg_compilation_time_ms.toFixed(2) + 'ms';
                    document.getElementById('critical-threats').textContent = data.critical_threats;
                    document.getElementById('federal-scans').textContent = data.federal_scans;
                });
        }
        
        function addThreatItem(data, isAlert = false) {
            const list = document.getElementById('threat-list');
            const item = document.createElement('div');
            item.className = 'threat-item ' + (data.threat_level || 'medium');
            item.innerHTML = `
                <strong>${data.actor_id || data.target_agency || 'Unknown'}</strong>
                ${isAlert ? '<span style="color: #ff0000;">[ALERT]</span>' : ''}
                <br>
                <small>Confidence: ${(data.confidence_score * 100).toFixed(1)}% | Time: ${data.compilation_time_ms?.toFixed(2) || 0}ms</small>
                <br>
                <small>${new Date(data.timestamp || Date.now()).toLocaleString()}</small>
            `;
            list.insertBefore(item, list.firstChild);
            
            // Keep only last 50 items
            while (list.children.length > 50) {
                list.removeChild(list.lastChild);
            }
        }
        
        // Initial load
        updateMetrics();
        setInterval(updateMetrics, 5000);
    </script>
</body>
</html>
"""


@app.route('/dashboard')
def dashboard():
    """Render threat monitoring dashboard"""
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/v1/dashboard/metrics')
def get_metrics():
    """Get dashboard metrics"""
    metrics = threat_store["metrics"]
    
    # Calculate critical threats
    critical_threats = sum(
        1 for comp in threat_store["compilations"]
        if comp.get("threat_level") == "critical"
    )
    
    return jsonify({
        "total_compilations": metrics["total_compilations"],
        "avg_compilation_time_ms": metrics["avg_compilation_time_ms"],
        "critical_threats": critical_threats,
        "federal_scans": len(threat_store["federal_ai_scans"]),
        "alerts": len(threat_store["alerts"]),
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/v1/dashboard/recent')
def get_recent_threats():
    """Get recent threats"""
    recent = threat_store["compilations"][-20:]  # Last 20
    return jsonify({
        "threats": recent,
        "count": len(recent),
        "timestamp": datetime.now().isoformat()
    })


def update_threat_store(compilation_data: Dict[str, Any]):
    """Update threat store with new compilation"""
    threat_store["compilations"].append(compilation_data)
    
    # Update metrics
    metrics = threat_store["metrics"]
    metrics["total_compilations"] += 1
    
    # Update average compilation time
    total_time = sum(c.get("compilation_time_ms", 0) for c in threat_store["compilations"])
    metrics["avg_compilation_time_ms"] = total_time / len(threat_store["compilations"])
    
    # Update threat level counts
    threat_level = compilation_data.get("threat_level", "unknown")
    metrics["threats_by_level"][threat_level] += 1
    
    # Update agency counts
    agency = compilation_data.get("target_agency")
    if agency:
        metrics["compilations_by_agency"][agency] += 1
    
    # Keep only last 1000 compilations
    if len(threat_store["compilations"]) > 1000:
        threat_store["compilations"] = threat_store["compilations"][-1000:]


if __name__ == '__main__':
    print("Starting ABC Threat Monitoring Dashboard...")
    print("Dashboard: http://localhost:5001/dashboard")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)

