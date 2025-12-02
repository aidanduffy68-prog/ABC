# Getting Started: Reach Your Magic Moment in 60 Seconds

**The Magic Moment:** Successfully compile intelligence in <500ms and see the cryptographic proof. This is when you understand the value and are unlikely to churn.

---

## 🎯 Fastest Path to Magic Moment (60 seconds)

**One command. No setup required.**

```bash
# Option 1: Run directly from GitHub (requires git clone first)
git clone https://github.com/aidanduffy68-prog/ABC.git
cd ABC
bash scripts/instant_demo.sh

# Option 2: If you already have the repo cloned
bash scripts/instant_demo.sh
```

**Prerequisites:**
- Python 3.8+ installed
- Dependencies installed: `pip install -r requirements.txt`

**What happens:**
1. ✅ Sets up demo environment automatically
2. ✅ Compiles sample intelligence
3. ✅ Shows you the <500ms result
4. ✅ Displays the cryptographic proof
5. 🎉 **Celebrates your Magic Moment!**

**Expected output:**
```
⏱️  Compilation Time: <500ms
📊 Confidence Score: 38-88%
🔐 Cryptographic Hash: Generated
✅ Status: VERIFIED

🎉 MAGIC MOMENT ACHIEVED! 🎉
```

---

## 🚀 Full Setup (5 minutes)

**If you want to customize and build on top:**

### Step 1: Install Dependencies

```bash
# Clone the repository
git clone https://github.com/aidanduffy68-prog/ABC.git
cd ABC

# Install Python dependencies
pip install -r requirements.txt
pip install -r security/requirements-security.txt
```

### Step 2: Configure Security (Optional for demo)

```bash
# Generate environment variables (required for production)
./security/setup_security.sh

# Verify setup
python3 security/test_security_setup.py
```

### Step 3: Your First Compilation

```bash
# Create sample intelligence file
cat > sample_intel.json << 'EOF'
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
  }
]
EOF

# Compile intelligence (this is your Magic Moment!)
python3 scripts/compile_intelligence.py \
  --actor-id "demo_001" \
  --actor-name "Demo Threat Actor" \
  --intel-file sample_intel.json
```

**You've reached your Magic Moment when you see:**
- ✅ Compilation time <500ms
- ✅ Confidence score displayed
- ✅ Cryptographic receipt generated
- ✅ "MAGIC MOMENT ACHIEVED!" message

---

## 🎯 What You Just Experienced

**The Problem:** When AGI generates threat assessments, agencies disagree (CIA: 85%, DHS: 60%). There's no objective truth layer.

**The Solution:** GH Systems ABC provides:
- ✅ **Cryptographically verifiable intelligence** - SHA-256 hash proof
- ✅ **<500ms compilation** - vs. 14+ days traditional
- ✅ **Objective truth layer** - No political bias, instant consensus
- ✅ **Mathematical proof** - Verifiable methodology

**This is what government agencies need for the Genesis Mission** - the largest AI infrastructure deployment in government history.

---

## 📚 Next Steps After Your Magic Moment

### For Developers

1. **Explore the API**
   ```bash
   # Start the FastAPI server
   python3 scripts/run_api_server.py
   
   # View API docs
   # Swagger UI: http://localhost:8000/docs
   # ReDoc: http://localhost:8000/redoc
   ```

2. **Try Federal AI Compilation**
   ```bash
   python3 scripts/compile_intelligence.py \
     --federal-ai \
     --agency "DoD" \
     --vuln-file vulnerabilities.json
   ```

3. **Review Examples**
   - [Department of War & DHS Assessment](examples/intelligence_audits/INTELLIGENCE_AUDIT_DOD_DHS_002.md) - 88% risk, <500ms
   - [Treasury Assessment](examples/intelligence_audits/INTELLIGENCE_AUDIT_TREASURY_003.md) - 85% risk, <500ms

### For Government Agencies

1. **Review Proof Points**
   - [Department of War & DHS Assessment](examples/intelligence_audits/INTELLIGENCE_AUDIT_DOD_DHS_002.md) - 88% risk, <500ms
   - [Treasury Assessment](examples/intelligence_audits/INTELLIGENCE_AUDIT_TREASURY_003.md) - 85% risk, <500ms

2. **Understand the Oracle**
   - Read [Oracle Positioning Framework](docs/ORACLE_POSITIONING_FRAMEWORK.md)
   - Review [architecture specification](docs/ARCHITECTURE_SPEC.md)

### For Security Researchers

1. **Try Intelligence Audits**
   - Review [intelligence audit format](examples/intelligence_audits/INTELLIGENCE_AUDIT_DOD_DHS_002.md)
   - Understand the [audit generator](src/core/nemesis/intelligence_audit/audit_generator.py)

---

## 🎯 Common Use Cases

### Compile Threat Intelligence

```bash
python3 scripts/compile_intelligence.py \
  --actor-id "threat_actor_001" \
  --actor-name "Threat Actor" \
  --intel-file intelligence.json \
  --transaction-file transactions.json \
  --output compiled_output.json
```

### Compile Federal AI Intelligence

```bash
python3 scripts/compile_intelligence.py \
  --federal-ai \
  --agency "DoD" \
  --vuln-file vulnerabilities.json \
  --ai-system-file ai_systems.json
```

### Run API Server

```bash
# Development mode (auto-reload)
python3 scripts/run_api_server.py

# Production mode
python3 scripts/run_api_server.py --production --host 0.0.0.0 --port 8080

# API docs available at:
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
# - Health: http://localhost:8000/api/v1/status/health
```

---

## ❓ Troubleshooting

### Import Errors

```bash
# Ensure project root is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Missing Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r security/requirements-security.txt
```

### Environment Variables

```bash
# Check environment variables are set
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('FLASK_SECRET_KEY:', 'SET' if os.getenv('FLASK_SECRET_KEY') else 'NOT SET')"
```

### Magic Moment Not Achieved?

If compilation takes >500ms or fails:
1. Check Python version: `python3 --version` (need 3.11+)
2. Verify dependencies: `pip list | grep -E "fastapi|pydantic|networkx"`
3. Check the error message - most issues are dependency-related
4. Try the instant demo script again: `bash scripts/instant_demo.sh`

---

## 📖 Full Documentation

- **[📄 Full Architecture Specification](docs/ARCHITECTURE_SPEC.md)** - Complete technical spec
- **[⚖️ Oracle Positioning Framework](docs/ORACLE_POSITIONING_FRAMEWORK.md)** - Sales framework
- **[📊 Intelligence Audit Examples](examples/intelligence_audits/)** - Operational assessments
- **[🧠 Ontology Specification](Deal%20Room/GH_ONTOLOGY_SPEC.md)** - Behavioral Intelligence Graph schema
- **[🔒 Security Documentation](security/README.md)** - Security audit, configuration, and deployment guide
- **[🔧 CLI Tools](scripts/README.md)** - Command-line utilities

---

## 🆘 Need Help?

- **Technical Issues:** [GitHub Issues](https://github.com/aidanduffy68-prog/ABC/issues)
- **Questions:** See documentation links above
- **Magic Moment Not Working?** Check troubleshooting section above

---

**Ready to verify truth in post-AGI intelligence? Start with the one-command demo above.**

**Your Magic Moment is 60 seconds away.** ⚡
