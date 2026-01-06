"""
Real-Time Threat Intelligence Platform API
WebSocket and REST API for real-time threat intelligence delivery

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import os
import secrets
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from src.verticals.ai_verification.core.nemesis.compilation_engine import ABCCompilationEngine, CompiledIntelligence
from src.verticals.ai_verification.core.nemesis.signal_intake.federal_ai_monitor import FederalAIMonitor, monitor_federal_ai_systems
from src.verticals.ai_verification.core.nemesis.real_time_platform.alert_system import alert_system
from src.verticals.ai_verification.core.nemesis.on_chain_receipt.bitcoin_integration import BitcoinOnChainIntegration
from src.shared.middleware.auth import require_auth, require_role
from src.shared.middleware.rate_limit import rate_limit
from src.shared.middleware.log_sanitizer import safe_log
from src.shared.middleware.request_limits import limit_request_size, check_request_size
from src.shared.middleware.error_handler import register_flask_error_handlers, SecureErrorHandler
from src.shared.middleware.audit_log import log_intelligence_compiled, log_federal_ai_scan


app = Flask(__name__)
# SECURITY: Use environment variable for secret key, generate random if not set
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

# SECURITY: CORS configuration from environment variable
allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if os.getenv('CORS_ALLOWED_ORIGINS') else []
if not allowed_origins or allowed_origins == ['']:
    # Default to no CORS if not configured (most secure)
    allowed_origins = []
socketio = SocketIO(app, cors_allowed_origins=allowed_origins if allowed_origins else None)

# Initialize engines
compilation_engine = ABCCompilationEngine()
federal_monitor = FederalAIMonitor()
bitcoin_integration = BitcoinOnChainIntegration()

# SECURITY: Register error handlers
register_flask_error_handlers(app)

# SECURITY: Add request size limit check
@app.before_request
def before_request():
    """Check request size before processing"""
    result = check_request_size()
    if result:
        return result


# REST API Endpoints

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint (public, no auth required)"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/v1/compile', methods=['POST'])
@require_auth  # SECURITY: Require authentication
@rate_limit(max_requests=10, window_seconds=60)  # SECURITY: Rate limiting
@limit_request_size(max_size=10 * 1024 * 1024)  # SECURITY: 10MB limit
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
        
        # SECURITY: Input validation and sanitization
        actor_id = data.get('actor_id', '').strip()
        actor_name = data.get('actor_name', actor_id).strip()
        raw_intelligence = data.get('raw_intelligence', [])
        transaction_data = data.get('transaction_data')
        network_data = data.get('network_data')
        
        # Validate actor_id format (alphanumeric, underscore, hyphen only)
        import re
        if not actor_id or not re.match(r'^[a-zA-Z0-9_-]+$', actor_id):
            return jsonify({"error": "Invalid actor_id format"}), 400
        
        if len(actor_id) > 100:
            return jsonify({"error": "actor_id too long (max 100 characters)"}), 400
        
        # SECURITY: Log sanitized request
        safe_log(app.logger, 'info', 'Compiling intelligence for actor: %s', actor_id)
        
        # SECURITY: Audit log intelligence compilation
        user_id = getattr(g, 'user_id', 'anonymous')
        ip_address = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', 'unknown')
        
        # Extract security tier parameters
        security_tier = None
        classification = data.get('classification')
        security_tier_str = data.get('security_tier')
        
        if security_tier_str:
            from src.verticals.ai_verification.core.nemesis.on_chain_receipt.security_tier import SecurityTier
            tier_map = {
                'unclassified': SecurityTier.TIER_1_UNCLASSIFIED,
                'sbu': SecurityTier.TIER_2_SBU,
                'classified': SecurityTier.TIER_3_CLASSIFIED
            }
            security_tier = tier_map.get(security_tier_str.lower())
        
        preferred_blockchain = data.get('preferred_blockchain', 'bitcoin')
        
        # Compile intelligence
        compiled = compilation_engine.compile_intelligence(
            actor_id=actor_id,
            actor_name=actor_name,
            raw_intelligence=raw_intelligence,
            transaction_data=transaction_data,
            network_data=network_data,
            generate_receipt=True,
            preferred_blockchain=preferred_blockchain,
            security_tier=security_tier,
            classification=classification
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
        
        # SECURITY: Audit log successful compilation
        log_intelligence_compiled(
            user_id=user_id,
            ip_address=ip_address,
            actor_id=actor_id,
            compilation_id=compiled.compilation_id
        )
        
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
        # SECURITY: Use secure error handling
        return SecureErrorHandler.handle_flask_error(e)


@app.route('/api/v1/federal-ai/scan', methods=['POST'])
@require_auth  # SECURITY: Require authentication
@require_role('admin', 'operator')  # SECURITY: Require elevated privileges
@rate_limit(max_requests=5, window_seconds=60)  # SECURITY: Stricter rate limit for sensitive operations
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
        # SECURITY: Input validation
        agencies = data.get('agencies', ['NASA', 'DoD', 'DHS'])
        if not isinstance(agencies, list):
            return jsonify({"error": "agencies must be a list"}), 400
        if len(agencies) > 10:
            return jsonify({"error": "Too many agencies (max 10)"}), 400
        
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
        
        # SECURITY: Audit log federal AI scan
        user_id = getattr(g, 'user_id', 'anonymous')
        ip_address = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', 'unknown')
        log_federal_ai_scan(
            user_id=user_id,
            ip_address=ip_address,
            agencies=agencies
        )
        
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
        # SECURITY: Use secure error handling
        return SecureErrorHandler.handle_flask_error(e)


@app.route('/api/v1/alerts', methods=['GET'])
@require_auth  # SECURITY: Require authentication
@rate_limit(max_requests=20, window_seconds=60)  # SECURITY: Rate limiting
def get_alerts():
    """Get active alerts"""
    from src.verticals.ai_verification.core.nemesis.real_time_platform.alert_system import AlertSeverity
    
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
@require_auth  # SECURITY: Require authentication
@require_role('admin', 'operator')  # SECURITY: Require elevated privileges
@rate_limit(max_requests=10, window_seconds=60)  # SECURITY: Rate limiting
def acknowledge_alert(alert_id):
    """Acknowledge alert"""
    success = alert_system.acknowledge_alert(alert_id)
    return jsonify({
        "acknowledged": success,
        "alert_id": alert_id,
        "timestamp": datetime.now().isoformat()
    }), 200 if success else 404


@app.route('/api/v1/alerts/stats', methods=['GET'])
@require_auth  # SECURITY: Require authentication
@rate_limit(max_requests=30, window_seconds=60)  # SECURITY: Rate limiting
def get_alert_stats():
    """Get alert statistics"""
    stats = alert_system.get_alert_stats()
    return jsonify(stats), 200


@app.route('/api/v1/receipts/verify', methods=['POST'])
@require_auth  # SECURITY: Require authentication
@rate_limit(max_requests=20, window_seconds=60)  # SECURITY: Rate limiting
def verify_receipt():
    """Verify cryptographic receipt"""
    from src.verticals.ai_verification.core.nemesis.on_chain_receipt.receipt_verifier import ReceiptVerifier
    
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
@require_auth  # SECURITY: Require authentication
@require_role('admin', 'operator')  # SECURITY: Require elevated privileges
@rate_limit(max_requests=5, window_seconds=60)  # SECURITY: Stricter rate limit
@limit_request_size(max_size=10 * 1024 * 1024)  # SECURITY: 10MB limit
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
        
        # SECURITY: Input validation
        target_agency = data.get('target_agency', '').strip()
        ai_system_data = data.get('ai_system_data', {})
        vulnerability_data = data.get('vulnerability_data', [])
        
        if not target_agency:
            return jsonify({"error": "target_agency is required"}), 400
        
        # Validate target_agency format
        import re
        if not re.match(r'^[a-zA-Z0-9\s_-]+$', target_agency):
            return jsonify({"error": "Invalid target_agency format"}), 400
        
        if len(target_agency) > 100:
            return jsonify({"error": "target_agency too long (max 100 characters)"}), 400
        
        # Extract security tier parameters
        security_tier = None
        classification = data.get('classification')
        security_tier_str = data.get('security_tier')
        
        if security_tier_str:
            from src.verticals.ai_verification.core.nemesis.on_chain_receipt.security_tier import SecurityTier
            tier_map = {
                'unclassified': SecurityTier.TIER_1_UNCLASSIFIED,
                'sbu': SecurityTier.TIER_2_SBU,
                'classified': SecurityTier.TIER_3_CLASSIFIED
            }
            security_tier = tier_map.get(security_tier_str.lower())
        
        preferred_blockchain = data.get('preferred_blockchain', 'bitcoin')
        
        # Compile federal AI intelligence
        compiled = compilation_engine.compile_federal_ai_intelligence(
            target_agency=target_agency,
            ai_system_data=ai_system_data,
            vulnerability_data=vulnerability_data,
            generate_receipt=True,
            preferred_blockchain=preferred_blockchain,
            security_tier=security_tier,
            classification=classification
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
        # SECURITY: Use secure error handling
        return SecureErrorHandler.handle_flask_error(e)


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
    # SECURITY: Disable debug mode in production
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
    
    print("Starting ABC Real-Time Threat Intelligence Platform...")
    print("API: http://localhost:5000")
    print("WebSocket: ws://localhost:5000")
    print(f"Debug mode: {debug_mode}")
    socketio.run(app, host='0.0.0.0', port=5000, debug=debug_mode)

