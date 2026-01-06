"""
Database Backend for Real-Time Dashboard
PostgreSQL storage for metrics, compilations, and historical data

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, execute_values
    from psycopg2.pool import SimpleConnectionPool
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("Warning: psycopg2 not installed. Install with: pip install psycopg2-binary")


@dataclass
class CompilationRecord:
    """Record of an intelligence compilation"""
    compilation_id: str
    actor_id: Optional[str]
    actor_name: Optional[str]
    target_agency: Optional[str]
    threat_level: str
    confidence_score: float
    compilation_time_ms: float
    timestamp: datetime
    metadata: Dict[str, Any]
    intelligence_hash: Optional[str] = None


@dataclass
class MetricSnapshot:
    """Snapshot of dashboard metrics at a point in time"""
    snapshot_id: str
    timestamp: datetime
    total_compilations: int
    avg_compilation_time_ms: float
    critical_threats: int
    high_threats: int
    medium_threats: int
    low_threats: int
    federal_scans: int
    compilations_by_agency: Dict[str, int]


class DashboardDatabase:
    """
    PostgreSQL database backend for dashboard data
    
    Stores:
    - Compilation records (with metadata)
    - Metric snapshots (for historical trends)
    - Federal AI scan results
    - Alerts
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            connection_string: PostgreSQL connection string
                              Defaults to DATABASE_URL environment variable
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 not installed. Install with: pip install psycopg2-binary")
        
        self.connection_string = connection_string or os.getenv(
            'DATABASE_URL',
            'postgresql://user:password@localhost:5432/abc_db'
        )
        
        # Connection pool (min 1, max 10 connections)
        self.pool = SimpleConnectionPool(1, 10, self.connection_string)
        self._ensure_tables()
    
    def _get_connection(self):
        """Get connection from pool"""
        return self.pool.getconn()
    
    def _return_connection(self, conn):
        """Return connection to pool"""
        self.pool.putconn(conn)
    
    def _ensure_tables(self):
        """Create tables if they don't exist"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # Compilations table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dashboard_compilations (
                        compilation_id VARCHAR(255) PRIMARY KEY,
                        actor_id VARCHAR(255),
                        actor_name VARCHAR(255),
                        target_agency VARCHAR(255),
                        threat_level VARCHAR(50),
                        confidence_score FLOAT,
                        compilation_time_ms FLOAT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB,
                        intelligence_hash VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_compilations_timestamp 
                    ON dashboard_compilations(timestamp DESC)
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_compilations_agency 
                    ON dashboard_compilations(target_agency)
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_compilations_threat_level 
                    ON dashboard_compilations(threat_level)
                """)
                
                # Metric snapshots table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dashboard_metric_snapshots (
                        snapshot_id VARCHAR(255) PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_compilations INTEGER,
                        avg_compilation_time_ms FLOAT,
                        critical_threats INTEGER,
                        high_threats INTEGER,
                        medium_threats INTEGER,
                        low_threats INTEGER,
                        federal_scans INTEGER,
                        compilations_by_agency JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp 
                    ON dashboard_metric_snapshots(timestamp DESC)
                """)
                
                # Federal AI scans table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dashboard_federal_scans (
                        scan_id VARCHAR(255) PRIMARY KEY,
                        agency VARCHAR(255),
                        scan_type VARCHAR(100),
                        risk_score FLOAT,
                        vulnerabilities_found INTEGER,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_scans_timestamp 
                    ON dashboard_federal_scans(timestamp DESC)
                """)
                
                # Alerts table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dashboard_alerts (
                        alert_id VARCHAR(255) PRIMARY KEY,
                        alert_type VARCHAR(100),
                        severity VARCHAR(50),
                        message TEXT,
                        compilation_id VARCHAR(255),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        acknowledged BOOLEAN DEFAULT FALSE,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
                    ON dashboard_alerts(timestamp DESC)
                """)
                
                conn.commit()
        finally:
            self._return_connection(conn)
    
    def store_compilation(self, compilation: CompilationRecord) -> bool:
        """
        Store compilation record
        
        Args:
            compilation: CompilationRecord to store
            
        Returns:
            True if successful
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO dashboard_compilations 
                    (compilation_id, actor_id, actor_name, target_agency, threat_level,
                     confidence_score, compilation_time_ms, timestamp, metadata, intelligence_hash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (compilation_id) DO UPDATE SET
                        actor_id = EXCLUDED.actor_id,
                        actor_name = EXCLUDED.actor_name,
                        target_agency = EXCLUDED.target_agency,
                        threat_level = EXCLUDED.threat_level,
                        confidence_score = EXCLUDED.confidence_score,
                        compilation_time_ms = EXCLUDED.compilation_time_ms,
                        timestamp = EXCLUDED.timestamp,
                        metadata = EXCLUDED.metadata,
                        intelligence_hash = EXCLUDED.intelligence_hash
                """, (
                    compilation.compilation_id,
                    compilation.actor_id,
                    compilation.actor_name,
                    compilation.target_agency,
                    compilation.threat_level,
                    compilation.confidence_score,
                    compilation.compilation_time_ms,
                    compilation.timestamp,
                    json.dumps(compilation.metadata),
                    compilation.intelligence_hash
                ))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error storing compilation: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def get_recent_compilations(
        self,
        limit: int = 50,
        agency: Optional[str] = None,
        threat_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent compilations with optional filters
        
        Args:
            limit: Maximum number of records
            agency: Filter by target agency
            threat_level: Filter by threat level
            
        Returns:
            List of compilation records
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT * FROM dashboard_compilations
                    WHERE 1=1
                """
                params = []
                
                if agency:
                    query += " AND target_agency = %s"
                    params.append(agency)
                
                if threat_level:
                    query += " AND threat_level = %s"
                    params.append(threat_level)
                
                query += " ORDER BY timestamp DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                results = cur.fetchall()
                
                # Convert to dicts and parse JSON
                compilations = []
                for row in results:
                    comp = dict(row)
                    if comp.get('metadata'):
                        comp['metadata'] = json.loads(comp['metadata']) if isinstance(comp['metadata'], str) else comp['metadata']
                    compilations.append(comp)
                
                return compilations
        finally:
            self._return_connection(conn)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current dashboard metrics
        
        Returns:
            Metrics dictionary
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Total compilations
                cur.execute("SELECT COUNT(*) as count FROM dashboard_compilations")
                total_compilations = cur.fetchone()['count']
                
                # Average compilation time
                cur.execute("""
                    SELECT AVG(compilation_time_ms) as avg_time 
                    FROM dashboard_compilations
                """)
                avg_time = cur.fetchone()['avg_time'] or 0.0
                
                # Threat level counts
                cur.execute("""
                    SELECT threat_level, COUNT(*) as count
                    FROM dashboard_compilations
                    GROUP BY threat_level
                """)
                threat_counts = {row['threat_level']: row['count'] for row in cur.fetchall()}
                
                # Agency counts
                cur.execute("""
                    SELECT target_agency, COUNT(*) as count
                    FROM dashboard_compilations
                    WHERE target_agency IS NOT NULL
                    GROUP BY target_agency
                """)
                agency_counts = {row['target_agency']: row['count'] for row in cur.fetchall()}
                
                # Federal scans count
                cur.execute("SELECT COUNT(*) as count FROM dashboard_federal_scans")
                federal_scans = cur.fetchone()['count']
                
                # Alerts count (unacknowledged)
                cur.execute("""
                    SELECT COUNT(*) as count 
                    FROM dashboard_alerts 
                    WHERE acknowledged = FALSE
                """)
                alerts = cur.fetchone()['count']
                
                return {
                    "total_compilations": total_compilations,
                    "avg_compilation_time_ms": float(avg_time),
                    "critical_threats": threat_counts.get('critical', 0),
                    "high_threats": threat_counts.get('high', 0),
                    "medium_threats": threat_counts.get('medium', 0),
                    "low_threats": threat_counts.get('low', 0),
                    "federal_scans": federal_scans,
                    "alerts": alerts,
                    "compilations_by_agency": agency_counts,
                    "timestamp": datetime.now().isoformat()
                }
        finally:
            self._return_connection(conn)
    
    def get_historical_metrics(
        self,
        hours: int = 24,
        interval_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Get historical metrics for time series visualization
        
        Args:
            hours: Number of hours to look back
            interval_minutes: Interval for aggregation (minutes)
            
        Returns:
            List of metric snapshots
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cutoff = datetime.now() - timedelta(hours=hours)
                
                # Aggregate compilations by time interval
                cur.execute("""
                    SELECT 
                        DATE_TRUNC('hour', timestamp) + 
                        INTERVAL '%s minutes' * FLOOR(EXTRACT(MINUTE FROM timestamp) / %s) as time_bucket,
                        COUNT(*) as count,
                        AVG(compilation_time_ms) as avg_time,
                        COUNT(*) FILTER (WHERE threat_level = 'critical') as critical,
                        COUNT(*) FILTER (WHERE threat_level = 'high') as high,
                        COUNT(*) FILTER (WHERE threat_level = 'medium') as medium,
                        COUNT(*) FILTER (WHERE threat_level = 'low') as low
                    FROM dashboard_compilations
                    WHERE timestamp >= %s
                    GROUP BY time_bucket
                    ORDER BY time_bucket ASC
                """, (interval_minutes, interval_minutes, cutoff))
                
                results = cur.fetchall()
                return [dict(row) for row in results]
        finally:
            self._return_connection(conn)
    
    def store_federal_scan(
        self,
        scan_id: str,
        agency: str,
        scan_type: str,
        risk_score: float,
        vulnerabilities_found: int,
        metadata: Dict[str, Any]
    ) -> bool:
        """Store federal AI scan result"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO dashboard_federal_scans
                    (scan_id, agency, scan_type, risk_score, vulnerabilities_found, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (scan_id) DO UPDATE SET
                        agency = EXCLUDED.agency,
                        scan_type = EXCLUDED.scan_type,
                        risk_score = EXCLUDED.risk_score,
                        vulnerabilities_found = EXCLUDED.vulnerabilities_found,
                        metadata = EXCLUDED.metadata
                """, (
                    scan_id, agency, scan_type, risk_score, vulnerabilities_found,
                    json.dumps(metadata)
                ))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error storing federal scan: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def store_alert(
        self,
        alert_id: str,
        alert_type: str,
        severity: str,
        message: str,
        compilation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store alert"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO dashboard_alerts
                    (alert_id, alert_type, severity, message, compilation_id, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (alert_id) DO UPDATE SET
                        alert_type = EXCLUDED.alert_type,
                        severity = EXCLUDED.severity,
                        message = EXCLUDED.message,
                        compilation_id = EXCLUDED.compilation_id,
                        metadata = EXCLUDED.metadata
                """, (
                    alert_id, alert_type, severity, message, compilation_id,
                    json.dumps(metadata or {})
                ))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error storing alert: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def search_compilations(
        self,
        query: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search compilations by text (actor name, agency, etc.)
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching compilations
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                search_term = f"%{query}%"
                cur.execute("""
                    SELECT * FROM dashboard_compilations
                    WHERE actor_name ILIKE %s
                       OR target_agency ILIKE %s
                       OR actor_id ILIKE %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (search_term, search_term, search_term, limit))
                
                results = cur.fetchall()
                compilations = []
                for row in results:
                    comp = dict(row)
                    if comp.get('metadata'):
                        comp['metadata'] = json.loads(comp['metadata']) if isinstance(comp['metadata'], str) else comp['metadata']
                    compilations.append(comp)
                
                return compilations
        finally:
            self._return_connection(conn)


# Fallback in-memory database for development
class InMemoryDashboardDatabase:
    """In-memory database for development/testing when PostgreSQL not available"""
    
    def __init__(self):
        self.compilations: List[CompilationRecord] = []
        self.federal_scans: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
    
    def store_compilation(self, compilation: CompilationRecord) -> bool:
        """Store compilation in memory"""
        # Remove existing if present
        self.compilations = [c for c in self.compilations if c.compilation_id != compilation.compilation_id]
        self.compilations.append(compilation)
        # Keep only last 1000
        if len(self.compilations) > 1000:
            self.compilations = self.compilations[-1000:]
        return True
    
    def get_recent_compilations(
        self,
        limit: int = 50,
        agency: Optional[str] = None,
        threat_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent compilations from memory"""
        results = self.compilations[-limit:]
        
        if agency:
            results = [c for c in results if c.target_agency == agency]
        if threat_level:
            results = [c for c in results if c.threat_level == threat_level]
        
        return [asdict(c) for c in reversed(results)]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics from memory"""
        if not self.compilations:
            return {
                "total_compilations": 0,
                "avg_compilation_time_ms": 0.0,
                "critical_threats": 0,
                "high_threats": 0,
                "medium_threats": 0,
                "low_threats": 0,
                "federal_scans": len(self.federal_scans),
                "alerts": len([a for a in self.alerts if not a.get('acknowledged', False)]),
                "compilations_by_agency": {},
                "timestamp": datetime.now().isoformat()
            }
        
        threat_counts = {}
        agency_counts = {}
        total_time = 0.0
        
        for comp in self.compilations:
            threat_counts[comp.threat_level] = threat_counts.get(comp.threat_level, 0) + 1
            if comp.target_agency:
                agency_counts[comp.target_agency] = agency_counts.get(comp.target_agency, 0) + 1
            total_time += comp.compilation_time_ms
        
        return {
            "total_compilations": len(self.compilations),
            "avg_compilation_time_ms": total_time / len(self.compilations),
            "critical_threats": threat_counts.get('critical', 0),
            "high_threats": threat_counts.get('high', 0),
            "medium_threats": threat_counts.get('medium', 0),
            "low_threats": threat_counts.get('low', 0),
            "federal_scans": len(self.federal_scans),
            "alerts": len([a for a in self.alerts if not a.get('acknowledged', False)]),
            "compilations_by_agency": agency_counts,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_historical_metrics(self, hours: int = 24, interval_minutes: int = 60) -> List[Dict[str, Any]]:
        """Get historical metrics (simplified for in-memory)"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [c for c in self.compilations if c.timestamp >= cutoff]
        
        # Simple aggregation by hour
        hourly = {}
        for comp in recent:
            hour_key = comp.timestamp.replace(minute=0, second=0, microsecond=0)
            if hour_key not in hourly:
                hourly[hour_key] = {
                    'time_bucket': hour_key,
                    'count': 0,
                    'avg_time': 0.0,
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0
                }
            hourly[hour_key]['count'] += 1
            hourly[hour_key]['avg_time'] += comp.compilation_time_ms
            hourly[hour_key][comp.threat_level] = hourly[hour_key].get(comp.threat_level, 0) + 1
        
        # Calculate averages
        for bucket in hourly.values():
            if bucket['count'] > 0:
                bucket['avg_time'] = bucket['avg_time'] / bucket['count']
        
        return sorted(hourly.values(), key=lambda x: x['time_bucket'])
    
    def store_federal_scan(self, scan_id: str, agency: str, scan_type: str, risk_score: float, vulnerabilities_found: int, metadata: Dict[str, Any]) -> bool:
        """Store federal scan in memory"""
        self.federal_scans.append({
            'scan_id': scan_id,
            'agency': agency,
            'scan_type': scan_type,
            'risk_score': risk_score,
            'vulnerabilities_found': vulnerabilities_found,
            'metadata': metadata,
            'timestamp': datetime.now()
        })
        return True
    
    def store_alert(self, alert_id: str, alert_type: str, severity: str, message: str, compilation_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store alert in memory"""
        self.alerts.append({
            'alert_id': alert_id,
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'compilation_id': compilation_id,
            'metadata': metadata or {},
            'timestamp': datetime.now(),
            'acknowledged': False
        })
        return True
    
    def search_compilations(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search compilations in memory"""
        query_lower = query.lower()
        results = []
        for comp in reversed(self.compilations):
            if (comp.actor_name and query_lower in comp.actor_name.lower()) or \
               (comp.target_agency and query_lower in comp.target_agency.lower()) or \
               (comp.actor_id and query_lower in comp.actor_id.lower()):
                results.append(asdict(comp))
                if len(results) >= limit:
                    break
        return results


def create_dashboard_database(connection_string: Optional[str] = None):
    """
    Factory function to create dashboard database
    
    Args:
        connection_string: PostgreSQL connection string
        
    Returns:
        DashboardDatabase or InMemoryDashboardDatabase
    """
    if PSYCOPG2_AVAILABLE:
        try:
            return DashboardDatabase(connection_string)
        except Exception as e:
            print(f"Warning: Could not connect to PostgreSQL: {e}")
            print("Falling back to in-memory database")
            return InMemoryDashboardDatabase()
    else:
        print("Warning: psycopg2 not installed. Using in-memory database.")
        return InMemoryDashboardDatabase()

