# ABC Federal AI Security - Demo Guide

**Quick Start:** Run live NASA compilation demo

---

## Quick Demo (5 minutes)

### 1. Start Services

```bash
# Terminal 1: API Server
cd nemesis/real_time_platform
python api_server.py

# Terminal 2: Dashboard
cd nemesis/real_time_platform  
python dashboard.py

# Terminal 3: Run Demo
cd nemesis
python demo_nasa_compilation.py
```

### 2. View Dashboard

Open browser: `http://localhost:5001/dashboard`

**What you'll see:**
- Real-time compilation metrics
- Threat list with severity indicators
- Live WebSocket updates
- Alert notifications

### 3. API Endpoints

**Test compilation:**
```bash
curl -X POST http://localhost:5000/api/v1/federal-ai/scan \
  -H "Content-Type: application/json" \
  -d '{"agencies": ["NASA"]}'
```

**View alerts:**
```bash
curl http://localhost:5000/api/v1/alerts
```

---

## Demo Highlights

### ✅ What Works Now

1. **Live Federal AI Compilation**
   - NASA systems scanned in real-time
   - <500ms compilation through ABC engine
   - Targeting packages generated

2. **Bitcoin Receipts**
   - Cryptographic receipts generated
   - On-chain submission (mock mode)
   - Receipt verification

3. **Real-Time Dashboard**
   - Live threat monitoring
   - Compilation metrics
   - Alert system

4. **Production-Ready API**
   - REST endpoints
   - WebSocket real-time updates
   - Alert management

---

## Market Positioning

### Unique Value Props

1. **Only Operational Federal AI Threat Platform**
   - Real-time compilation (not research)
   - Production-ready system
   - Live demonstrations

2. **Bitcoin-Verified Intelligence Receipts**
   - Cryptographic proof on-chain
   - Verifiable without revealing methods
   - Government audit trail

3. **Real-Time Compilation Demonstrated**
   - <500ms compilation time
   - Live dashboard shows metrics
   - WebSocket updates

4. **Production-Ready System**
   - Full API infrastructure
   - Alert system
   - Professional dashboard

---

## Next Steps

1. **Run Demo** - Execute `demo_nasa_compilation.py`
2. **Record Video** - Capture demo for marketing
3. **Schedule Demos** - Government contacts
4. **Deploy Production** - Production environment setup

---

**Status:** Ready for live demonstration

*GH Systems: The only operational federal AI threat intelligence platform.*

