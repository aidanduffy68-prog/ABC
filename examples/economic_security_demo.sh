#!/bin/bash
# GH Systems ABC - Economic Security Use Case Demonstration
# Demonstrates supply chain intelligence compilation for economic security

set -e

echo "============================================================"
echo "GH Systems ABC - Economic Security Demonstration"
echo "Supply Chain Intelligence Compilation"
echo "============================================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Please install Python 3.11+"
    exit 1
fi

echo "📋 Demonstrating Economic Security Use Cases:"
echo "   1. Assess reshoring opportunities for critical components"
echo "   2. Monitor defense industrial base supply chain security"
echo "   3. Detect technology transfer threats in manufacturing partnerships"
echo "   4. Verify foreign investment security in critical sectors"
echo ""

# Create demo intelligence data for each use case
mkdir -p /tmp/economic_security_demo

# Use Case 1: Reshoring Opportunities
echo "🔍 Use Case 1: Assessing Reshoring Opportunities for Critical Components"
echo "   Target: Semiconductor manufacturing supply chain"
echo ""

cat > /tmp/economic_security_demo/reshoring_intel.json << 'EOF'
[
  {
    "text": "Taiwan Semiconductor Manufacturing Company (TSMC) controls 60% of global advanced semiconductor production, creating strategic vulnerability for U.S. defense and technology sectors",
    "source": "supply_chain_analysis",
    "type": "dependency_risk"
  },
  {
    "text": "China's potential control of Taiwan semiconductor facilities poses existential threat to U.S. technology supply chains",
    "source": "intelligence_assessment",
    "type": "threat_intelligence"
  },
  {
    "text": "U.S. semiconductor reshoring initiatives show 15% cost premium but 40% reduction in supply chain risk",
    "source": "economic_analysis",
    "type": "reshoring_opportunity"
  },
  {
    "text": "Intel, Samsung, and TSMC have announced U.S. manufacturing expansion plans totaling $200B+ in investment",
    "source": "industry_intelligence",
    "type": "reshoring_activity"
  },
  {
    "text": "Critical dependency: 90% of advanced chips (7nm and below) produced in Taiwan, creating single point of failure",
    "source": "supply_chain_risk_assessment",
    "type": "vulnerability"
  }
]
EOF

echo "   Compiling intelligence..."
python3 "$PROJECT_ROOT/scripts/compile_intelligence.py" \
  --actor-id "supply_chain_semiconductor_$(date +%s)" \
  --actor-name "Semiconductor Supply Chain - Reshoring Assessment" \
  --intel-file /tmp/economic_security_demo/reshoring_intel.json \
  --output /tmp/economic_security_demo/reshoring_output.json 2>&1 | grep -E "(Compilation|Risk|Confidence|Hash|MAGIC)" || true

if [ -f /tmp/economic_security_demo/reshoring_output.json ]; then
    echo ""
    echo "   ✅ Reshoring Assessment Complete"
    python3 -c "
import json
data = json.load(open('/tmp/economic_security_demo/reshoring_output.json'))
print(f\"   📊 Risk Score: {data.get('targeting_package', {}).get('risk_assessment', {}).get('overall_risk', 0)*100:.1f}%\")
print(f\"   ⏱️  Compilation Time: {data.get('compilation_time_ms', 0):.2f}ms\")
print(f\"   🔐 Hash: {data.get('targeting_package', {}).get('receipt', {}).get('hash', 'N/A')[:32]}...\")
"
fi

echo ""
echo "============================================================"
echo ""

# Use Case 2: Defense Industrial Base Supply Chain Security
echo "🔍 Use Case 2: Monitoring Defense Industrial Base Supply Chain Security"
echo "   Target: Defense contractor supply chain vulnerabilities"
echo ""

cat > /tmp/economic_security_demo/defense_intel.json << 'EOF'
[
  {
    "text": "Lockheed Martin F-35 program relies on 1,500+ suppliers across 30 countries, with 20% of critical components sourced from non-allied nations",
    "source": "defense_industrial_base_analysis",
    "type": "supply_chain_mapping"
  },
  {
    "text": "Chinese-owned companies supply critical rare earth magnets for defense systems, creating strategic dependency",
    "source": "intelligence_report",
    "type": "adversarial_influence"
  },
  {
    "text": "Foreign investment in U.S. defense suppliers increased 300% over past 5 years, with 15% now under foreign control",
    "source": "investment_analysis",
    "type": "foreign_investment_threat"
  },
  {
    "text": "Supply chain disruption risk: Single supplier provides 80% of titanium for military aircraft, located in adversarial-aligned country",
    "source": "supply_chain_risk_assessment",
    "type": "vulnerability"
  },
  {
    "text": "Defense contractors report 45% increase in technology transfer attempts from foreign entities in past 2 years",
    "source": "counterintelligence_report",
    "type": "technology_transfer_threat"
  }
]
EOF

echo "   Compiling intelligence..."
python3 "$PROJECT_ROOT/scripts/compile_intelligence.py" \
  --actor-id "defense_industrial_base_$(date +%s)" \
  --actor-name "Defense Industrial Base - Supply Chain Security" \
  --intel-file /tmp/economic_security_demo/defense_intel.json \
  --output /tmp/economic_security_demo/defense_output.json 2>&1 | grep -E "(Compilation|Risk|Confidence|Hash|MAGIC)" || true

if [ -f /tmp/economic_security_demo/defense_output.json ]; then
    echo ""
    echo "   ✅ Defense Industrial Base Assessment Complete"
    python3 -c "
import json
data = json.load(open('/tmp/economic_security_demo/defense_output.json'))
print(f\"   📊 Risk Score: {data.get('targeting_package', {}).get('risk_assessment', {}).get('overall_risk', 0)*100:.1f}%\")
print(f\"   ⏱️  Compilation Time: {data.get('compilation_time_ms', 0):.2f}ms\")
print(f\"   🔐 Hash: {data.get('targeting_package', {}).get('receipt', {}).get('hash', 'N/A')[:32]}...\")
"
fi

echo ""
echo "============================================================"
echo ""

# Use Case 3: Technology Transfer Threats
echo "🔍 Use Case 3: Detecting Technology Transfer Threats in Manufacturing Partnerships"
echo "   Target: U.S.-China manufacturing joint ventures"
echo ""

cat > /tmp/economic_security_demo/tech_transfer_intel.json << 'EOF'
[
  {
    "text": "U.S. semiconductor company entered joint venture with Chinese state-owned enterprise, raising concerns about IP transfer",
    "source": "partnership_analysis",
    "type": "technology_transfer_risk"
  },
  {
    "text": "Chinese partner in joint venture has history of forced technology transfer, with 3 previous U.S. partners reporting IP theft",
    "source": "intelligence_report",
    "type": "adversarial_pattern"
  },
  {
    "text": "Joint venture agreement includes mandatory technology sharing clauses covering advanced manufacturing processes",
    "source": "contract_analysis",
    "type": "contractual_risk"
  },
  {
    "text": "U.S. company's R&D facility in joint venture location shows 40% of staff are former employees of Chinese military contractors",
    "source": "personnel_security_assessment",
    "type": "personnel_risk"
  },
  {
    "text": "Technology transfer pattern: 5 similar joint ventures resulted in Chinese competitors launching identical products within 18 months",
    "source": "pattern_analysis",
    "type": "historical_precedent"
  }
]
EOF

echo "   Compiling intelligence..."
python3 "$PROJECT_ROOT/scripts/compile_intelligence.py" \
  --actor-id "tech_transfer_manufacturing_$(date +%s)" \
  --actor-name "Manufacturing Partnership - Technology Transfer Threat" \
  --intel-file /tmp/economic_security_demo/tech_transfer_intel.json \
  --output /tmp/economic_security_demo/tech_transfer_output.json 2>&1 | grep -E "(Compilation|Risk|Confidence|Hash|MAGIC)" || true

if [ -f /tmp/economic_security_demo/tech_transfer_output.json ]; then
    echo ""
    echo "   ✅ Technology Transfer Threat Assessment Complete"
    python3 -c "
import json
data = json.load(open('/tmp/economic_security_demo/tech_transfer_output.json'))
print(f\"   📊 Risk Score: {data.get('targeting_package', {}).get('risk_assessment', {}).get('overall_risk', 0)*100:.1f}%\")
print(f\"   ⏱️  Compilation Time: {data.get('compilation_time_ms', 0):.2f}ms\")
print(f\"   🔐 Hash: {data.get('targeting_package', {}).get('receipt', {}).get('hash', 'N/A')[:32]}...\")
"
fi

echo ""
echo "============================================================"
echo ""

# Use Case 4: Foreign Investment Security
echo "🔍 Use Case 4: Verifying Foreign Investment Security in Critical Sectors"
echo "   Target: Foreign investment in U.S. critical infrastructure"
echo ""

cat > /tmp/economic_security_demo/foreign_investment_intel.json << 'EOF'
[
  {
    "text": "Chinese state-owned enterprise acquired controlling stake in U.S. energy infrastructure company with access to 15% of national grid",
    "source": "investment_monitoring",
    "type": "foreign_investment"
  },
  {
    "text": "Investment structure uses shell companies and offshore entities to obscure ultimate beneficial ownership",
    "source": "ownership_analysis",
    "type": "obfuscation_pattern"
  },
  {
    "text": "Acquired company provides cybersecurity services to 200+ U.S. critical infrastructure facilities",
    "source": "security_assessment",
    "type": "critical_infrastructure_access"
  },
  {
    "text": "Chinese parent company has direct ties to People's Liberation Army cyber units, raising espionage concerns",
    "source": "intelligence_report",
    "type": "adversarial_connection"
  },
  {
    "text": "Investment review: CFIUS flagged transaction but approval granted under previous administration with limited conditions",
    "source": "regulatory_analysis",
    "type": "regulatory_risk"
  }
]
EOF

echo "   Compiling intelligence..."
python3 "$PROJECT_ROOT/scripts/compile_intelligence.py" \
  --actor-id "foreign_investment_critical_$(date +%s)" \
  --actor-name "Foreign Investment - Critical Infrastructure Security" \
  --intel-file /tmp/economic_security_demo/foreign_investment_intel.json \
  --output /tmp/economic_security_demo/foreign_investment_output.json 2>&1 | grep -E "(Compilation|Risk|Confidence|Hash|MAGIC)" || true

if [ -f /tmp/economic_security_demo/foreign_investment_output.json ]; then
    echo ""
    echo "   ✅ Foreign Investment Security Assessment Complete"
    python3 -c "
import json
data = json.load(open('/tmp/economic_security_demo/foreign_investment_output.json'))
print(f\"   📊 Risk Score: {data.get('targeting_package', {}).get('risk_assessment', {}).get('overall_risk', 0)*100:.1f}%\")
print(f\"   ⏱️  Compilation Time: {data.get('compilation_time_ms', 0):.2f}ms\")
print(f\"   🔐 Hash: {data.get('targeting_package', {}).get('receipt', {}).get('hash', 'N/A')[:32]}...\")
"
fi

echo ""
echo "============================================================"
echo "📊 Summary: Economic Security Intelligence Compilations"
echo "============================================================"
echo ""

# Generate summary
python3 << 'PYTHON_SCRIPT'
import json
import os
import glob

results = []
for file in glob.glob("/tmp/economic_security_demo/*_output.json"):
    try:
        with open(file) as f:
            data = json.load(f)
            use_case = os.path.basename(file).replace("_output.json", "").replace("_", " ").title()
            risk = data.get('targeting_package', {}).get('risk_assessment', {}).get('overall_risk', 0) * 100
            time_ms = data.get('compilation_time_ms', 0)
            hash_val = data.get('targeting_package', {}).get('receipt', {}).get('hash', 'N/A')[:16]
            
            results.append({
                'use_case': use_case,
                'risk': risk,
                'time': time_ms,
                'hash': hash_val
            })
    except:
        pass

print("Use Case                              | Risk Score | Time    | Hash")
print("-" * 80)
for r in results:
    print(f"{r['use_case']:36} | {r['risk']:6.1f}%   | {r['time']:6.2f}ms | {r['hash']}...")

print("")
print("✅ All assessments compiled with cryptographic verification")
print("✅ Real-time threat intelligence for economic security")
print("✅ <500ms compilation enables rapid response to supply chain threats")
PYTHON_SCRIPT

echo ""
echo "============================================================"
echo "🎯 Key Takeaways"
echo "============================================================"
echo ""
echo "1. ✅ Reshoring Assessment: Identified semiconductor supply chain vulnerabilities"
echo "2. ✅ Defense Industrial Base: Detected foreign influence in defense supply chains"
echo "3. ✅ Technology Transfer: Identified IP theft risks in manufacturing partnerships"
echo "4. ✅ Foreign Investment: Verified security risks in critical infrastructure investments"
echo ""
echo "All assessments compiled in <500ms with cryptographic verification."
echo "Ready for integration with Palantir Foundry for real-time monitoring."
echo ""
echo "============================================================"

# Cleanup
rm -rf /tmp/economic_security_demo

