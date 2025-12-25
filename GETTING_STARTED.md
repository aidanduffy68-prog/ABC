# Getting Started: Foundry Chain Integration

**Foundry Chain** transforms Palantir Foundry into blockchain-verified intelligence. ABC provides cryptographic proof that all agencies analyzed the same source data, enabling transparent conflict resolution.

---

## 🎯 Fastest Path to Magic Moment (60 seconds)

**Quick setup, then one command:**

```bash
# Step 1: Clone the repository
git clone https://github.com/aidanduffy68-prog/ABC.git
cd ABC

# Step 2: Install dependencies (one-time setup)
pip install -r requirements.txt

# Step 3: Run the instant demo
bash scripts/instant_demo.sh
```

**Prerequisites:**
- Python 3.8+ installed (`python3 --version` to check)
- pip installed (usually comes with Python)

**That's it!** The script will handle the rest and get you to your Magic Moment.

**What happens:**
1. ✅ Sets up demo environment automatically
2. ✅ Compiles sample intelligence
3. ✅ Shows you the <500ms result
4. ✅ Displays the cryptographic proof
5. 🎉 **Celebrates your Magic Moment!**

**Expected output:**
```
THE PROBLEM:

When AI Systems Disagree, Who's Right?

CIA says 78% confidence. NSA says 85%. DHS says 62%.

Same threat. Three different answers.

ABC provides cryptographic proof they analyzed
identical source data.

📊 Intelligence Input: APT41 Cyber Operations

   - Targeting defense sector supply chains
   - Suspicious network traffic detected
   - Malware signatures match previous campaigns
   - C2 servers activated

🔍 Compiling intelligence...

THE SOLUTION:

✅ ABC compiled threat intelligence

   Confidence Score: 39.7%
   Compilation Time: 3.03ms
   Cryptographic Hash: 4ecbdeb7a884f503...
   Status: VERIFIED ✓

   Different AI systems can now analyze this data.
   ABC proves they all used identical source intelligence.

🔗 This is how we verify truth in the age of AI.
```

**Note:** Demo uses limited sample data, so confidence may be lower (30-50%). Real deployments with full intelligence feeds achieve 75-90% confidence. See our [Department of War & DHS assessment](examples/intelligence_audits/INTELLIGENCE_AUDIT_DOD_DHS_002.md) (88% confidence) and [Treasury assessment](examples/intelligence_audits/INTELLIGENCE_AUDIT_TREASURY_003.md) (85% confidence) for production examples.

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
./docs/security/setup_security.sh

# Verify setup
python3 docs/security/test_security_setup.py
```

### Step 3: Your First Compilation

```bash
# Create sample intelligence file (APT41 scenario)
cat > sample_intel.json << 'EOF'
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

# Compile intelligence (this is your Magic Moment!)
python3 src/cli/compile_intelligence.py \
  --actor-id "demo_001" \
  --actor-name "Demo Threat Actor" \
  --intel-file sample_intel.json

# Compile with security tier (for government deployments)
python3 src/cli/compile_intelligence.py \
  --actor-id "demo_001" \
  --actor-name "Demo Threat Actor" \
  --intel-file sample_intel.json \
  --security-tier unclassified \
  --blockchain ethereum

# Or use classification string (auto-determines tier)
python3 src/cli/compile_intelligence.py \
  --actor-id "demo_001" \
  --actor-name "Demo Threat Actor" \
  --intel-file sample_intel.json \
  --classification "SBU" \
  --blockchain polygon
```

**You've reached your Magic Moment when you see:**
- ✅ THE SOLUTION section displayed
- ✅ Compilation time <500ms
- ✅ Confidence score displayed
- ✅ Cryptographic hash generated
- ✅ Status: VERIFIED ✓
- ✅ Message: "This is how we verify truth in the age of AI."

---

## 🎯 What You Just Experienced

**THE PROBLEM:**

When AI Systems Disagree, Who's Right?

CIA says 78% confidence. NSA says 85%. DHS says 62%.

Same threat. Three different answers.

**THE SOLUTION:**

ABC provides cryptographic proof they analyzed identical source data.

GH Systems ABC enables:
- ✅ **Cryptographically verifiable intelligence** - SHA-256 hash proof (RSA-PSS in production)
- ✅ **<500ms compilation** - vs. 14+ days traditional (typically 0.5-2ms in practice)
- ✅ **Chain-agnostic architecture** - Works with Bitcoin, Ethereum, Polygon, Arbitrum, Base, Optimism
- ✅ **Objective truth layer** - No political bias, instant consensus
- ✅ **Mathematical proof** - Verifiable methodology

**Different AI systems can now analyze the same data. ABC proves they all used identical source intelligence.**

**This is how we verify truth in the age of AI.**

---

## 🔒 Security Tiers

ABC supports three security tiers for government deployments:

### Tier 1: Unclassified
- **Blockchains**: Bitcoin, Ethereum, Polygon, Arbitrum, Base, Optimism
- **Data Exposure**: Full intelligence hash and metadata committed
- **Verification**: Public, anyone can verify
- **Use Case**: Public threat intelligence, unclassified assessments

### Tier 2: SBU (Sensitive But Unclassified)
- **Blockchains**: Permissioned chains (Hyperledger, Corda, Quorum, Besu)
- **Data Exposure**: Controlled access, encrypted metadata
- **Verification**: Permissioned, authorized parties only
- **Use Case**: Sensitive but unclassified intelligence

### Tier 3: Classified
- **Blockchains**: Any (Bitcoin, Ethereum for hash-only)
- **Data Exposure**: Zero - only cryptographic hash committed
- **Verification**: Hash-only verification
- **Use Case**: Classified intelligence, zero data exposure

**Example:**
```bash
# Tier 1 (Unclassified) - Public blockchain
python3 src/cli/compile_intelligence.py \
  --actor-id "threat_001" \
  --actor-name "Threat Actor" \
  --intel-file sample_intel.json \
  --security-tier unclassified \
  --blockchain ethereum

# Tier 3 (Classified) - Hash-only commitment
python3 src/cli/compile_intelligence.py \
  --actor-id "threat_001" \
  --actor-name "Threat Actor" \
  --intel-file sample_intel.json \
  --security-tier classified \
  --blockchain bitcoin
```

## 📚 Next Steps After Your Magic Moment

### For Developers

1. **Explore the API**
   ```bash
   # Start the FastAPI server
   python3 src/cli/run_api_server.py
   
   # View API docs
   # Swagger UI: http://localhost:8000/docs
   # ReDoc: http://localhost:8000/redoc
   ```

2. **Try Federal AI Compilation**
   ```bash
   python3 src/cli/compile_intelligence.py \
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

2. **Understand the Architecture**
   - Review [architecture specification](docs/architecture/ARCHITECTURE_SPEC.md)
   - Read [Foundry Chain specification](docs/integrations/FOUNDRY_CHAIN_SPEC.md)

### For Security Researchers

1. **Try Intelligence Audits**
   - Review [intelligence audit format](examples/intelligence_audits/INTELLIGENCE_AUDIT_DOD_DHS_002.md)
   - Understand the [audit generator](src/core/nemesis/intelligence_audit/audit_generator.py)

---

## 🎯 Common Use Cases

### Compile Threat Intelligence

```bash
python3 src/cli/compile_intelligence.py \
  --actor-id "threat_actor_001" \
  --actor-name "Threat Actor" \
  --intel-file intelligence.json \
  --transaction-file transactions.json \
  --output compiled_output.json
```

### Compile Federal AI Intelligence

```bash
python3 src/cli/compile_intelligence.py \
  --federal-ai \
  --agency "DoD" \
  --vuln-file vulnerabilities.json \
  --ai-system-file ai_systems.json
```

### Run API Server

```bash
# Development mode (auto-reload)
python3 src/cli/run_api_server.py

# Production mode
python3 src/cli/run_api_server.py --production --host 0.0.0.0 --port 8080

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

- **[📄 Full Architecture Specification](docs/architecture/ARCHITECTURE_SPEC.md)** - Complete technical spec
- **[📊 Intelligence Audit Examples](examples/intelligence_audits/)** - Operational assessments
- **[🔗 Foundry Chain Specification](docs/integrations/FOUNDRY_CHAIN_SPEC.md)** - Foundry integration guide
- **[🧠 Ontology Specification](Deal%20Room/GH_ONTOLOGY_SPEC.md)** - Behavioral Intelligence Graph schema
- **[🔒 Security Documentation](docs/security/README.md)** - Security audit, configuration, and deployment guide
- **[🔧 CLI Tools](scripts/README.md)** - Command-line utilities

---

## 🆘 Need Help?

- **Technical Issues:** [GitHub Issues](https://github.com/aidanduffy68-prog/ABC/issues)
- **Questions:** See documentation links above
- **Magic Moment Not Working?** Check troubleshooting section above

---

**Ready to verify truth in post-AGI intelligence? Start with the one-command demo above.**

**Your Magic Moment is 60 seconds away.** ⚡
