"""
Real-Time Threat Intelligence Platform API
WebSocket and REST API for real-time threat intelligence delivery

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from nemesis.compilation_engine import ABCCompilationEngine, CompiledIntelligence
from nemesis.signal_intake.federal_ai_monitor import FederalAIMonitor, monitor_federal_ai_systems
from nemesis.real_time_platform.alert_system import alert_system
from nemesis.on_chain_receipt.bitcoin_integration import BitcoinOnChainIntegration


app = Flask(__name__)
app.config['SECRET_KEY'] = 'gh-systems-abc-platform'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize engines
compilation_engine = ABCCompilationEngine()
federal_monitor = FederalAIMonitor()
bitcoin_integration = BitcoinOnChainIntegration()


# REST API Endpoints

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/v1/compile', methods=['POST'])
def compile_intelligence():
    """
    Compile intelligence through Hades → Echo → Nemesis pipeline
    
    Request body:
    {
        "actor_id": "lazarus_001",
        "actor_name": "Lazarus Group",
        "raw_intelligence": [...],
        "transaction_data": [...],
        "network_data": {...}
    }
    """
    try:
        data = request.json or {}
        
        actor_id = data.get('actor_id')
        actor_name = data.get('actor_name', actor_id)
        raw_intelligence = data.get('raw_intelligence', [])
        transaction_data = data.get('transaction_data')
        network_data = data.get('network_data')
        
        if not actor_id:
            return jsonify({"error": "actor_id is required"}), 400
        
        # Compile intelligence
        compiled = compilation_engine.compile_intelligence(
            actor_id=actor_id,
            actor_name=actor_name,
            raw_intelligence=raw_intelligence,
            transaction_data=transaction_data,
            network_data=network_data,
            generate_receipt=True
        )
        
        # Evaluate for alerts
        compilation_dict = {
            "compilation_id": compiled.compilation_id,
            "actor_id": compiled.actor_id,
            "confidence_score": compiled.confidence_score,
            "compilation_time_ms": compiled.compilation_time_ms,
            "targeting_package": compiled.targeting_package,
            "target_agency": None
        }
        alerts = alert_system.evaluate_compilation(compilation_dict)
        
        # Submit receipt to Bitcoin if present
        receipt = compiled.targeting_package.get("receipt")
        tx_result = None
        if receipt:
            try:
                tx_result = bitcoin_integration.submit_receipt_to_blockchain(receipt)
            except Exception as e:
                print(f"Bitcoin submission error: {e}")
        
        # Emit real-time update via WebSocket
        socketio.emit('intelligence_compiled', {
            "compilation_id": compiled.compilation_id,
            "actor_id": compiled.actor_id,
            "compilation_time_ms": compiled.compilation_time_ms,
            "confidence_score": compiled.confidence_score,
            "timestamp": compiled.compiled_at.isoformat(),
            "tx_hash": tx_result.get("tx_hash") if tx_result else None
        })
        
        # Emit alerts if any
        for alert in alerts:
            socketio.emit('alert', {
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "title": alert.title,
                "description": alert.description,
                "timestamp": alert.created_at.isoformat()
            })
        
        # Return compiled intelligence
        return jsonify({
            "status": "success",
            "compilation_id": compiled.compilation_id,
            "compilation_time_ms": compiled.compilation_time_ms,
            "confidence_score": compiled.confidence_score,
            "targeting_package": compiled.targeting_package,
            "receipt": receipt,
            "tx_hash": tx_result.get("tx_hash") if tx_result else None,
            "alerts_generated": len(alerts)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/federal-ai/scan', methods=['POST'])
def scan_federal_ai():
    """
    Scan federal AI systems for vulnerabilities
    
    Request body (optional):
    {
        "agencies": ["NASA", "DoD", "DHS"]  # If not provided, scans all
    }
    """
    try:
        data = request.json or {}
        agencies = data.get('agencies', ['NASA', 'DoD', 'DHS'])
        
        systems = []
        if 'NASA' in agencies:
            systems.extend(federal_monitor.scan_nasa_systems())
        if 'DoD' in agencies:
            systems.extend(federal_monitor.scan_dod_systems())
        if 'DHS' in agencies:
            systems.extend(federal_monitor.scan_dhs_systems())
        
        # Extract vulnerabilities
        vulnerabilities = federal_monitor.extract_vulnerabilities(systems)
        
        # Generate intelligence feed
        intelligence_feed = federal_monitor.generate_intelligence_feed(systems)
        
        # Evaluate for alerts
        scan_data = {
            "systems_scanned": len(systems),
            "vulnerabilities": [
                {
                    "vulnerability_id": v.vulnerability_id,
                    "system_id": v.system_id,
                    "type": v.vulnerability_type,
                    "severity": v.severity,
                    "confidence": v.confidence
                }
                for v in vulnerabilities
            ]
        }
        alerts = alert_system.evaluate_federal_ai_scan(scan_data)
        
        # Emit real-time update
        socketio.emit('federal_ai_scan_complete', {
            "systems_scanned": len(systems),
            "vulnerabilities_found": len(vulnerabilities),
            "timestamp": datetime.now().isoformat()
        })
        
        # Emit alerts if any
        for alert in alerts:
            socketio.emit('alert', {
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "title": alert.title,
                "description": alert.description,
                "timestamp": alert.created_at.isoformat()
            })
        
        return jsonify({
            "status": "success",
            "systems_scanned": len(systems),
            "vulnerabilities_found": len(vulnerabilities),
            "systems": [
                {
                    "agency": s.agency,
                    "system_name": s.system_name,
                    "system_type": s.system_type,
                    "vulnerability_count": len(s.vulnerabilities)
                }
                for s in systems
            ],
            "vulnerabilities": [
                {
                    "vulnerability_id": v.vulnerability_id,
                    "system_id": v.system_id,
                    "type": v.vulnerability_type,
                    "severity": v.severity,
                    "confidence": v.confidence
                }
                for v in vulnerabilities
            ],
            "intelligence_feed": intelligence_feed
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/alerts', methods=['GET'])
def get_alerts():
    """Get active alerts"""
    from nemesis.real_time_platform.alert_system import AlertSeverity
    
    severity = request.args.get('severity')
    severity_enum = None
    if severity:
        try:
            severity_enum = AlertSeverity[severity.upper()]
        except KeyError:
            pass
    
    active_alerts = alert_system.get_active_alerts(severity=severity_enum)
    
    return jsonify({
        "alerts": [
            {
                "alert_id": a.alert_id,
                "alert_type": a.alert_type.value,
                "severity": a.severity.value,
                "title": a.title,
                "description": a.description,
                "created_at": a.created_at.isoformat(),
                "actor_id": a.actor_id,
                "target_agency": a.target_agency,
                "confidence_score": a.confidence_score
            }
            for a in active_alerts
        ],
        "count": len(active_alerts),
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/v1/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge alert"""
    success = alert_system.acknowledge_alert(alert_id)
    return jsonify({
        "acknowledged": success,
        "alert_id": alert_id,
        "timestamp": datetime.now().isoformat()
    }), 200 if success else 404


@app.route('/api/v1/alerts/stats', methods=['GET'])
def get_alert_stats():
    """Get alert statistics"""
    stats = alert_system.get_alert_stats()
    return jsonify(stats), 200


@app.route('/api/v1/receipts/verify', methods=['POST'])
def verify_receipt():
    """Verify cryptographic receipt"""
    from nemesis.on_chain_receipt.receipt_verifier import ReceiptVerifier
    
    data = request.json or {}
    receipt = data.get('receipt')
    intelligence_package = data.get('intelligence_package')
    verify_on_chain = data.get('verify_on_chain', True)
    
    if not receipt:
        return jsonify({"error": "receipt is required"}), 400
    
    verifier = ReceiptVerifier()
    result = verifier.verify_receipt(receipt, intelligence_package, verify_on_chain)
    
    return jsonify(result), 200


@app.route('/api/v1/federal-ai/compile', methods=['POST'])
def compile_federal_ai_intelligence():
    """
    Compile federal AI security intelligence
    
    Request body:
    {
        "target_agency": "NASA",
        "ai_system_data": {...},
        "vulnerability_data": [...]
    }
    """
    try:
        data = request.json or {}
        
        target_agency = data.get('target_agency')
        ai_system_data = data.get('ai_system_data', {})
        vulnerability_data = data.get('vulnerability_data', [])
        
        if not target_agency:
            return jsonify({"error": "target_agency is required"}), 400
        
        # Compile federal AI intelligence
        compiled = compilation_engine.compile_federal_ai_intelligence(
            target_agency=target_agency,
            ai_system_data=ai_system_data,
            vulnerability_data=vulnerability_data,
            generate_receipt=True
        )
        
        # Emit real-time update
        socketio.emit('federal_ai_intelligence_compiled', {
            "compilation_id": compiled.compilation_id,
            "target_agency": target_agency,
            "compilation_time_ms": compiled.compilation_time_ms,
            "confidence_score": compiled.confidence_score,
            "timestamp": compiled.compiled_at.isoformat()
        })
        
        return jsonify({
            "status": "success",
            "compilation_id": compiled.compilation_id,
            "target_agency": target_agency,
            "compilation_time_ms": compiled.compilation_time_ms,
            "confidence_score": compiled.confidence_score,
            "targeting_package": compiled.targeting_package,
            "receipt": compiled.targeting_package.get("receipt")
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# WebSocket Events

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'message': 'Connected to ABC Real-Time Platform'})
    print(f"Client connected: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print(f"Client disconnected: {request.sid}")


@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to real-time updates"""
    subscription_type = data.get('type', 'all')  # all, federal_ai, specific_actor
    emit('subscribed', {'type': subscription_type})


if __name__ == '__main__':
    print("Starting ABC Real-Time Threat Intelligence Platform...")
    print("API: http://localhost:5000")
    print("WebSocket: ws://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

