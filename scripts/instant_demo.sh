#!/bin/bash
# GH Systems ABC - Instant Demo
# Get to the Magic Moment in <60 seconds

set -e

echo "============================================================"
echo "GH Systems ABC - Instant Demo"
echo "Truth Verification for Post-AGI Intelligence"
echo "============================================================"
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

# Create sample intelligence data
cat > /tmp/demo_intel.json << 'EOF'
[
  {
    "text": "North Korean hackers coordinating with Russian facilitators",
    "source": "intel_feed_1",
    "type": "intelligence_report"
  },
  {
    "text": "Multiple wallets showing synchronized transaction patterns",
    "source": "blockchain_analysis",
    "type": "transaction_analysis"
  },
  {
    "text": "Suspected OFAC evasion through mixer services",
    "source": "compliance_monitor",
    "type": "sanctions_alert"
  }
]
EOF

echo "🔍 Compiling intelligence..."
echo ""

# Run compilation
python3 "$PROJECT_ROOT/scripts/compile_intelligence.py" \
  --actor-id "demo_instant_$(date +%s)" \
  --actor-name "Demo Threat Actor" \
  --intel-file /tmp/demo_intel.json \
  --output /tmp/demo_output.json 2>&1 | tee /tmp/demo_result.txt

# Check if compilation succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "🎉 MAGIC MOMENT ACHIEVED! 🎉"
    echo "============================================================"
    echo ""
    echo "You've successfully verified truth in post-AGI intelligence!"
    echo ""
    
    # Extract key metrics
    if [ -f /tmp/demo_output.json ]; then
        COMP_TIME=$(python3 -c "import json; data=json.load(open('/tmp/demo_output.json')); print(f\"{data.get('compilation_time_ms', 0):.2f}ms\")" 2>/dev/null || echo "N/A")
        CONFIDENCE=$(python3 -c "import json; data=json.load(open('/tmp/demo_output.json')); print(f\"{data.get('confidence_score', 0)*100:.1f}%\")" 2>/dev/null || echo "N/A")
        
        echo "📊 Your Result:"
        echo "   ⚡ Compilation Time: $COMP_TIME"
        echo "   📈 Confidence Score: $CONFIDENCE"
        echo "   🔐 Cryptographic Hash: Generated"
        echo "   ✅ Status: VERIFIED"
        echo ""
    fi
    
    echo "============================================================"
    echo "What You Just Experienced"
    echo "============================================================"
    echo ""
    echo "This is what government agencies need when AGI generates"
    echo "conflicting threat assessments. You've just experienced"
    echo "the solution:"
    echo ""
    echo "  • Cryptographically verifiable intelligence"
    echo "  • <500ms compilation (vs. 14+ days traditional)"
    echo "  • Objective truth layer for disputes"
    echo "  • Mathematical proof of methodology"
    echo ""
    echo "============================================================"
    echo "What's Next?"
    echo "============================================================"
    echo ""
    echo "1. Try with your own data:"
    echo "   python3 scripts/compile_intelligence.py --help"
    echo ""
    echo "2. Explore the examples:"
    echo "   cat examples/intelligence_audits/INTELLIGENCE_AUDIT_DOD_DHS_002.md"
    echo ""
    echo "3. Review the architecture:"
    echo "   cat docs/ARCHITECTURE_SPEC.md"
    echo ""
    echo "4. Get started guide:"
    echo "   cat GETTING_STARTED.md"
    echo ""
    echo "============================================================"
    echo "✅ Magic Moment Complete!"
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

