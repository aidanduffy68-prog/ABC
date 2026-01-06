"""
Threat Monitoring Dashboard
Real-time dashboard for monitoring compiled intelligence and threats

Copyright (c) 2026 GH Systems. All rights reserved.
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
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
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
        .charts-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .chart-card {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
        }
        .chart-title {
            color: #0099ff;
            margin-bottom: 15px;
            font-size: 18px;
        }
        .chart-wrapper {
            position: relative;
            height: 300px;
        }
        .filter-controls {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        .filter-controls label {
            color: #888;
            margin-right: 5px;
        }
        .filter-controls select, .filter-controls input {
            background: #0f0f0f;
            border: 1px solid #333;
            color: #fff;
            padding: 8px 12px;
            border-radius: 4px;
        }
        .filter-controls button {
            background: #0066cc;
            border: none;
            color: #fff;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }
        .filter-controls button:hover {
            background: #0088ff;
        }
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
    
    <div class="filter-controls">
        <label>Time Range:</label>
        <select id="time-range">
            <option value="24">Last 24 Hours</option>
            <option value="48">Last 48 Hours</option>
            <option value="168">Last Week</option>
            <option value="720">Last Month</option>
        </select>
        <label>Interval:</label>
        <select id="interval">
            <option value="15">15 Minutes</option>
            <option value="30">30 Minutes</option>
            <option value="60" selected>1 Hour</option>
            <option value="240">4 Hours</option>
            <option value="1440">1 Day</option>
        </select>
        <button onclick="loadHistoricalCharts()">Refresh Charts</button>
    </div>
    
    <div class="charts-container">
        <div class="chart-card">
            <div class="chart-title">Compilations Over Time</div>
            <div class="chart-wrapper">
                <canvas id="compilations-chart"></canvas>
            </div>
        </div>
        <div class="chart-card">
            <div class="chart-title">Average Compilation Time</div>
            <div class="chart-wrapper">
                <canvas id="time-chart"></canvas>
            </div>
        </div>
        <div class="chart-card">
            <div class="chart-title">Threat Level Distribution</div>
            <div class="chart-wrapper">
                <canvas id="threat-levels-chart"></canvas>
            </div>
        </div>
        <div class="chart-card">
            <div class="chart-title">Threat Levels Over Time</div>
            <div class="chart-wrapper">
                <canvas id="threat-timeline-chart"></canvas>
            </div>
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
        
        // Chart instances
        let compilationsChart = null;
        let timeChart = null;
        let threatLevelsChart = null;
        let threatTimelineChart = null;
        
        // Initialize charts
        function initCharts() {
            const chartOptions = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#fff' }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#888' },
                        grid: { color: '#333' }
                    },
                    y: {
                        ticks: { color: '#888' },
                        grid: { color: '#333' }
                    }
                }
            };
            
            // Compilations over time
            const compCtx = document.getElementById('compilations-chart').getContext('2d');
            compilationsChart = new Chart(compCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Compilations',
                        data: [],
                        borderColor: '#0099ff',
                        backgroundColor: 'rgba(0, 153, 255, 0.1)',
                        tension: 0.4
                    }]
                },
                options: chartOptions
            });
            
            // Average compilation time
            const timeCtx = document.getElementById('time-chart').getContext('2d');
            timeChart = new Chart(timeCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Avg Time (ms)',
                        data: [],
                        borderColor: '#00ff00',
                        backgroundColor: 'rgba(0, 255, 0, 0.1)',
                        tension: 0.4
                    }]
                },
                options: chartOptions
            });
            
            // Threat level distribution (pie chart)
            const threatCtx = document.getElementById('threat-levels-chart').getContext('2d');
            threatLevelsChart = new Chart(threatCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: [
                            '#ff0000',
                            '#ff4444',
                            '#ffaa00',
                            '#00ff00'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#fff' },
                            position: 'bottom'
                        }
                    }
                }
            });
            
            // Threat levels over time
            const timelineCtx = document.getElementById('threat-timeline-chart').getContext('2d');
            threatTimelineChart = new Chart(timelineCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Critical',
                            data: [],
                            borderColor: '#ff0000',
                            backgroundColor: 'rgba(255, 0, 0, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'High',
                            data: [],
                            borderColor: '#ff4444',
                            backgroundColor: 'rgba(255, 68, 68, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Medium',
                            data: [],
                            borderColor: '#ffaa00',
                            backgroundColor: 'rgba(255, 170, 0, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Low',
                            data: [],
                            borderColor: '#00ff00',
                            backgroundColor: 'rgba(0, 255, 0, 0.1)',
                            tension: 0.4
                        }
                    ]
                },
                options: chartOptions
            });
        }
        
        // Load historical charts
        function loadHistoricalCharts() {
            const hours = parseInt(document.getElementById('time-range').value);
            const intervalMinutes = parseInt(document.getElementById('interval').value);
            
            fetch(`/api/v1/dashboard/historical?hours=${hours}&interval_minutes=${intervalMinutes}`)
                .then(r => r.json())
                .then(data => {
                    if (!data.data || data.data.length === 0) {
                        console.log('No historical data available');
                        return;
                    }
                    
                    // Format timestamps
                    const labels = data.data.map(d => {
                        const date = new Date(d.time_bucket);
                        return date.toLocaleString();
                    });
                    
                    // Update compilations chart
                    compilationsChart.data.labels = labels;
                    compilationsChart.data.datasets[0].data = data.data.map(d => d.count);
                    compilationsChart.update();
                    
                    // Update time chart
                    timeChart.data.labels = labels;
                    timeChart.data.datasets[0].data = data.data.map(d => d.avg_time || 0);
                    timeChart.update();
                    
                    // Update threat timeline chart
                    threatTimelineChart.data.labels = labels;
                    threatTimelineChart.data.datasets[0].data = data.data.map(d => d.critical || 0);
                    threatTimelineChart.data.datasets[1].data = data.data.map(d => d.high || 0);
                    threatTimelineChart.data.datasets[2].data = data.data.map(d => d.medium || 0);
                    threatTimelineChart.data.datasets[3].data = data.data.map(d => d.low || 0);
                    threatTimelineChart.update();
                    
                    // Update threat levels pie chart with latest data
                    const latest = data.data[data.data.length - 1];
                    if (latest) {
                        threatLevelsChart.data.datasets[0].data = [
                            latest.critical || 0,
                            latest.high || 0,
                            latest.medium || 0,
                            latest.low || 0
                        ];
                        threatLevelsChart.update();
                    }
                })
                .catch(err => {
                    console.error('Error loading historical data:', err);
                });
        }
        
        // Initial load
        initCharts();
        updateMetrics();
        loadHistoricalCharts();
        setInterval(updateMetrics, 5000);
        setInterval(loadHistoricalCharts, 60000); // Refresh charts every minute
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

