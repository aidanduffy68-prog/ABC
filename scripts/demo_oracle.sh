#!/bin/bash
# ABC Oracle Demo

echo "============================================================"
echo "🔗 ABC Oracle Demo - Chainlink for Foundry AML"
echo "============================================================"
echo ""

# Check Bitcoin node
echo "Checking Bitcoin node connection..."
if ! command -v bitcoin-cli &> /dev/null; then
    echo "⚠️  Bitcoin CLI not found. Oracle will run in mock mode."
    echo "   To use real Bitcoin node, install Bitcoin Core and start with:"
    echo "   bitcoind -daemon -txindex"
    echo ""
fi

# Run oracle test
echo "Testing Bitcoin oracle..."
python3 scripts/test_bitcoin_oracle.py

echo ""
echo "============================================================"
echo "✅ Oracle Demo Complete"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Start API: python src/cli/run_api_server.py"
echo "  2. Test WebSocket: wscat -c ws://localhost:8000/api/v1/oracle/stream/bitcoin"
echo "  3. Ingest blocks: curl -X POST http://localhost:8000/api/v1/oracle/ingest/bitcoin/block/825000"
echo ""

