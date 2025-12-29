"""
Demo Usage Examples
Load demo data and test API endpoints
"""

import json
import requests
from pathlib import Path

# Load demo data
DEMO_DATA_PATH = Path(__file__).parent / "demo_data.json"

def load_demo_data():
    """Load demo data from JSON file"""
    with open(DEMO_DATA_PATH, 'r') as f:
        return json.load(f)

def demo_process_intelligence(base_url="http://localhost:5000"):
    """Demo: Process intelligence feed"""
    data = load_demo_data()
    
    payload = {
        "intelligence": data["intelligence_feeds"][:2],  # First 2 feeds
        "transaction_data": data["transaction_data"][:2]  # First 2 transactions
    }
    
    response = requests.post(
        f"{base_url}/api/v1/intelligence/process",
        json=payload
    )
    
    print("=== Process Intelligence Demo ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Entities extracted: {len(result.get('result', {}).get('entities', []))}")
        print(f"Relationships found: {len(result.get('result', {}).get('relationships', []))}")
    else:
        print(f"Error: {response.text}")
    print()

def demo_threat_dossier(base_url="http://localhost:5000", actor_id="LAZARUS_GROUP", format="markdown"):
    """Demo: Generate threat dossier"""
    response = requests.get(
        f"{base_url}/api/v1/actors/{actor_id}/dossier",
        params={"format": format}
    )
    
    print(f"=== Threat Dossier Demo ({actor_id}) ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        if format == "markdown":
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        else:
            dossier = response.json()
            print(f"Dossier ID: {dossier.get('dossier', {}).get('dossier_id', 'N/A')}")
            print(f"Threat Level: {dossier.get('dossier', {}).get('threat_level', 'N/A')}")
    else:
        print(f"Error: {response.text}")
    print()

def demo_natural_language_query(base_url="http://localhost:5000", query=None):
    """Demo: Natural language query"""
    data = load_demo_data()
    
    if query is None:
        query = data["sample_queries"][0]
    
    payload = {
        "query": query,
        "user": "demo_user"
    }
    
    response = requests.post(
        f"{base_url}/api/v1/query",
        json=payload
    )
    
    print("=== Natural Language Query Demo ===")
    print(f"Query: {query}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result.get('result', {}).get('response', {}).get('response_text', 'N/A')}")
        print(f"Confidence: {result.get('result', {}).get('response', {}).get('confidence', 0):.2f}")
    else:
        print(f"Error: {response.text}")
    print()

def demo_targeting_package(base_url="http://localhost:5000", actor_id="LAZARUS_GROUP", include_dossier=False):
    """Demo: Get targeting package"""
    response = requests.get(
        f"{base_url}/api/v1/actors/{actor_id}/targeting-package",
        params={"include_dossier": str(include_dossier).lower()}
    )
    
    print(f"=== Targeting Package Demo ({actor_id}) ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        package = response.json()
        print(f"Package status: {package.get('status', 'N/A')}")
        if include_dossier:
            print("Dossier included: Yes")
        else:
            print("Dossier included: No")
    else:
        print(f"Error: {response.text}")
    print()

def demo_health_check(base_url="http://localhost:5000"):
    """Demo: Health check"""
    response = requests.get(f"{base_url}/api/v1/health")
    
    print("=== Health Check Demo ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        health = response.json()
        print(f"Service: {health.get('service', 'N/A')}")
        print(f"Version: {health.get('version', 'N/A')}")
        print(f"Status: {health.get('status', 'N/A')}")
    else:
        print(f"Error: {response.text}")
    print()

def run_all_demos(base_url="http://localhost:5000"):
    """Run all demo scenarios"""
    print("=" * 60)
    print("GH SYSTEMS ABC AI ONTOLOGY - DEMO SUITE")
    print("=" * 60)
    print()
    
    # Health check first
    demo_health_check(base_url)
    
    # Process intelligence
    demo_process_intelligence(base_url)
    
    # Natural language query
    demo_natural_language_query(base_url)
    
    # Threat dossier
    demo_threat_dossier(base_url, actor_id="LAZARUS_GROUP", format="json")
    
    # Targeting package
    demo_targeting_package(base_url, actor_id="LAZARUS_GROUP", include_dossier=False)
    
    print("=" * 60)
    print("Demo suite complete!")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    run_all_demos(base_url)

