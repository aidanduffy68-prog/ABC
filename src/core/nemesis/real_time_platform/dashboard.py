"""
Threat Monitoring Dashboard
Real-time dashboard for monitoring compiled intelligence and threats

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

from .api_server import compilation_engine, federal_monitor
from .database import (
    create_dashboard_database,
    CompilationRecord,
    DashboardDatabase,
    InMemoryDashboardDatabase
)


import os
import secrets

app = Flask(__name__)
# SECURITY: Use environment variable for secret key, generate random if not set
app.config['SECRET_KEY'] = os.getenv('DASHBOARD_SECRET_KEY', secrets.token_hex(32))

# SECURITY: CORS configuration from environment variable
allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if os.getenv('CORS_ALLOWED_ORIGINS') else []
if not allowed_origins or allowed_origins == ['']:
    allowed_origins = []
socketio = SocketIO(app, cors_allowed_origins=allowed_origins if allowed_origins else None)

# Database backend (PostgreSQL if available, otherwise in-memory)
db = create_dashboard_database()


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
    metrics = db.get_metrics()
    return jsonify(metrics)


@app.route('/api/v1/dashboard/recent')
def get_recent_threats():
    """Get recent threats with optional filters"""
    agency = request.args.get('agency')
    threat_level = request.args.get('threat_level')
    limit = int(request.args.get('limit', 50))
    
    recent = db.get_recent_compilations(
        limit=limit,
        agency=agency,
        threat_level=threat_level
    )
    
    return jsonify({
        "threats": recent,
        "count": len(recent),
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/v1/dashboard/historical')
def get_historical_metrics():
    """Get historical metrics for charts"""
    hours = int(request.args.get('hours', 24))
    interval_minutes = int(request.args.get('interval_minutes', 60))
    
    historical = db.get_historical_metrics(
        hours=hours,
        interval_minutes=interval_minutes
    )
    
    return jsonify({
        "data": historical,
        "hours": hours,
        "interval_minutes": interval_minutes,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/v1/dashboard/search')
def search_compilations():
    """Search compilations"""
    query = request.args.get('q', '').strip()
    limit = int(request.args.get('limit', 50))
    
    if not query:
        return jsonify({"error": "Query parameter 'q' required"}), 400
    
    results = db.search_compilations(query=query, limit=limit)
    
    return jsonify({
        "results": results,
        "count": len(results),
        "query": query,
        "timestamp": datetime.now().isoformat()
    })


def update_threat_store(compilation_data: Dict[str, Any]):
    """Update database with new compilation"""
    compilation_id = compilation_data.get("compilation_id", str(uuid.uuid4()))
    
    record = CompilationRecord(
        compilation_id=compilation_id,
        actor_id=compilation_data.get("actor_id"),
        actor_name=compilation_data.get("actor_name"),
        target_agency=compilation_data.get("target_agency"),
        threat_level=compilation_data.get("threat_level", "unknown"),
        confidence_score=compilation_data.get("confidence_score", 0.0),
        compilation_time_ms=compilation_data.get("compilation_time_ms", 0.0),
        timestamp=datetime.fromisoformat(compilation_data.get("timestamp", datetime.now().isoformat())),
        metadata=compilation_data.get("metadata", {}),
        intelligence_hash=compilation_data.get("intelligence_hash")
    )
    
    db.store_compilation(record)
    
    # Emit WebSocket event
    socketio.emit('intelligence_compiled', compilation_data)


if __name__ == '__main__':
    print("Starting ABC Threat Monitoring Dashboard...")
    print("Dashboard: http://localhost:5001/dashboard")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)

