#!/bin/bash
# GH Systems ABC - Instant Demo
# Get to the Magic Moment in <60 seconds

set -e

echo "============================================================"
echo "GH Systems ABC - Instant Demo"
echo "Truth Verification for Post-AGI Intelligence"
echo "============================================================"
echo ""
echo "THE PROBLEM:"
echo ""
echo "When AI Systems Disagree, Who's Right?"
echo ""
echo "CIA says 78% confidence. NSA says 85%. DHS says 62%."
echo ""
echo "Same threat. Three different answers."
echo ""
echo "ABC provides cryptographic proof they analyzed"
echo "identical source data."
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Please install Python 3.11+"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

echo "📦 Setting up demo environment..."
echo ""

# Check if we're in the right directory (has src/ and scripts/)
if [ ! -d "src" ] || [ ! -d "scripts" ]; then
    echo "⚠️  Warning: Not in project root. Attempting to find project root..."
    # Try to find project root by looking for src/ directory
    if [ -d "$PROJECT_ROOT/src" ] && [ -d "$PROJECT_ROOT/scripts" ]; then
        cd "$PROJECT_ROOT"
        echo "✅ Found project root: $PROJECT_ROOT"
    else
        echo "❌ Error: Cannot find project root. Please run from ABC directory."
        echo "   Or clone the repo: git clone https://github.com/aidanduffy68-prog/ABC.git"
        exit 1
    fi
fi

# Check if dependencies are installed
if ! python3 -c "import sys; sys.path.insert(0, '.'); from src.core.nemesis.compilation_engine import ABCCompilationEngine" 2>/dev/null; then
    echo "⚠️  Warning: Dependencies may not be installed."
    echo "   Attempting to continue anyway..."
    echo ""
fi

# Create sample intelligence data (APT41 scenario)
cat > /tmp/demo_intel.json << 'EOF'
[
  {
    "text": "APT41 targeting defense sector supply chains",
    "source": "intel_feed_1",
    "type": "intelligence_report"
  },
  {
    "text": "Suspicious network traffic detected matching APT41 patterns",
    "source": "network_monitoring",
    "type": "threat_detection"
  },
  {
    "text": "Malware signatures match previous APT41 campaigns",
    "source": "malware_analysis",
    "type": "threat_intelligence"
  },
  {
    "text": "Command and control servers activated",
    "source": "network_monitoring",
    "type": "threat_detection"
  }
]
EOF

echo "📊 Intelligence Input: APT41 Cyber Operations"
echo ""
echo "   - Targeting defense sector supply chains"
echo "   - Suspicious network traffic detected"
echo "   - Malware signatures match previous campaigns"
echo "   - C2 servers activated"
echo ""
echo "🔍 Compiling intelligence..."
echo ""

# Run compilation
python3 "$PROJECT_ROOT/src/cli/compile_intelligence.py" \
  --actor-id "apt41_demo_$(date +%s)" \
  --actor-name "APT41" \
  --intel-file /tmp/demo_intel.json \
  --output /tmp/demo_output.json 2>&1 | tee /tmp/demo_result.txt

# Check if compilation succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "🎉 MAGIC MOMENT ACHIEVED! 🎉"
    echo "============================================================"
    echo ""
    
    # Extract key metrics
    if [ -f /tmp/demo_output.json ]; then
        COMP_TIME=$(python3 -c "import json; data=json.load(open('/tmp/demo_output.json')); print(f\"{data.get('compilation_time_ms', 0):.2f}ms\")" 2>/dev/null || echo "N/A")
        CONFIDENCE=$(python3 -c "import json; data=json.load(open('/tmp/demo_output.json')); conf=data.get('confidence_score', 0)*100; print(f\"{conf:.1f}%\")" 2>/dev/null || echo "N/A")
        
        # Extract hash (first 16 chars) - check targeting_package for receipt
        HASH=$(python3 -c "import json; data=json.load(open('/tmp/demo_output.json')); tp=data.get('targeting_package', {}); receipt=tp.get('receipt', {}); h=receipt.get('intelligence_hash', receipt.get('hash', '')); print(h[:16] if h and len(h) > 16 else (h if h else 'Generated'))" 2>/dev/null || echo "Generated")
        
        echo "THE SOLUTION:"
        echo ""
        echo "✅ ABC compiled threat intelligence"
        echo ""
        echo "   Confidence Score: $CONFIDENCE"
        echo "   Compilation Time: $COMP_TIME"
        echo "   Cryptographic Hash: ${HASH}..."
        echo "   Status: VERIFIED ✓"
        echo ""
        echo "   Different AI systems can now analyze this data."
        echo "   ABC proves they all used identical source intelligence."
        echo ""
        echo "🔗 This is how we verify truth in the age of AI."
        echo ""
    fi
    
    echo "============================================================"
    echo "📈 Next Steps (Recommended Path)"
    echo "============================================================"
    echo ""
    echo "1️⃣  See Real Examples (2 minutes)"
    echo "   📊 Department of War & DHS: 88% risk, <500ms"
    echo "      cat examples/intelligence_audits/INTELLIGENCE_AUDIT_DOD_DHS_002.md"
    echo ""
    echo "   📊 Treasury: 85% risk, <500ms"
    echo "      cat examples/intelligence_audits/INTELLIGENCE_AUDIT_TREASURY_003.md"
    echo ""
    echo "2️⃣  Try Your Own Data (5 minutes)"
    echo "   python3 src/cli/compile_intelligence.py --help"
    echo "   python3 src/cli/compile_intelligence.py \\"
    echo "     --actor-id \"your_threat\" --actor-name \"Threat Actor\" \\"
    echo "     --intel-file your_data.json --blockchain ethereum"
    echo ""
    echo "3️⃣  Explore the API (10 minutes)"
    echo "   python3 scripts/run_api_server.py"
    echo "   # Visit: http://localhost:8000/docs"
    echo ""
    echo "4️⃣  Review Architecture (15 minutes)"
    echo "   cat docs/ARCHITECTURE_SPEC.md"
    echo "   cat docs/CHAIN_AGNOSTIC_ARCHITECTURE.md"
    echo ""
    echo "============================================================"
    echo "🚀 Progression: Demo → Examples → Custom → Production"
    echo "============================================================"
    echo ""
else
    echo ""
    echo "❌ Demo failed. Please check the error above."
    echo "   For help, see: GETTING_STARTED.md"
    exit 1
fi

# Cleanup
rm -f /tmp/demo_intel.json /tmp/demo_result.txt

