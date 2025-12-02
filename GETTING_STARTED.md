# Getting Started with GH Systems ABC

**Truth verification for post-AGI intelligence in 5 minutes**

---

## 🎯 Your Magic Moment

**The Magic Moment:** Successfully compile intelligence in <500ms and see the cryptographic proof.

**Why it matters:** Once you experience this, you understand the value and are unlikely to churn.

**Fastest path (60 seconds):**
```bash
curl -s https://raw.githubusercontent.com/aidanduffy68-prog/ABC/main/scripts/instant_demo.sh | bash
```

---

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
# Clone the repository
git clone https://github.com/aidanduffy68-prog/ABC.git
cd ABC

# Install Python dependencies
pip install -r requirements.txt
pip install -r security/requirements-security.txt
```

### Step 2: Configure Security

```bash
# Generate environment variables
./security/setup_security.sh

# Verify setup
python3 security/test_deployment.py
```

### Step 3: Try Your First Compilation

```bash
# Create a sample intelligence file
cat > sample_intel.json << EOF
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

# Compile intelligence
python3 scripts/compile_intelligence.py \
  --actor-id "demo_001" \
  --actor-name "Demo Threat Actor" \
  --intel-file sample_intel.json
```

**Expected output:** Compilation in <500ms with risk score, behavioral signature, and cryptographic receipt.

---

## 📚 Next Steps

### For Developers

1. **Explore the API**
   - Review [API documentation](src/core/nemesis/ai_ontology/api_documentation.md)
   - Check out [example usage](src/core/nemesis/ai_ontology/examples/basic_usage.py)

2. **Run a Demo**
   - Try the [NASA compilation demo](src/core/nemesis/demo_nasa_compilation.py)
   - Review [intelligence audit examples](examples/intelligence_audits/)

3. **Integrate**
   - See [integration guide](docs/ARCHITECTURE_SPEC.md)
   - Review [security configuration](security/README.md)

### For Government Agencies

1. **Review Proof Points**
   - [Department of War & DHS Assessment](examples/intelligence_audits/INTELLIGENCE_AUDIT_DOD_DHS_002.md) - 88% risk, <500ms
   - [Treasury Assessment](examples/intelligence_audits/INTELLIGENCE_AUDIT_TREASURY_003.md) - 85% risk, <500ms

2. **Understand the Oracle**
   - Read [Oracle Positioning Framework](docs/ORACLE_POSITIONING_FRAMEWORK.md)
   - Review [architecture specification](docs/ARCHITECTURE_SPEC.md)

3. **Request a Demo**
   - Contact: [Your contact information]
   - Schedule: [Demo scheduling link]

### For Security Researchers

1. **Try Intelligence Audits**
   - Review [intelligence audit format](examples/intelligence_audits/INTELLIGENCE_AUDIT_DOD_DHS_002.md)
   - Understand the [audit generator](src/core/nemesis/intelligence_audit/audit_generator.py)

2. **Explore the Ontology**
   - Read [ontology specification](Deal%20Room/GH_ONTOLOGY_SPEC.md)
   - Review [behavioral intelligence graph](docs/ARCHITECTURE_SPEC.md)

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
python3 -m src.core.nemesis.real_time_platform.api_server
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

---

## 📖 Documentation

- **[Full Architecture](docs/ARCHITECTURE_SPEC.md)** - Complete technical specification
- **[Oracle Framework](docs/ORACLE_POSITIONING_FRAMEWORK.md)** - Sales and positioning
- **[Security Guide](security/README.md)** - Security configuration and deployment
- **[Scripts](scripts/README.md)** - CLI tools and utilities

---

## 🆘 Need Help?

- **Technical Issues:** [GitHub Issues](https://github.com/aidanduffy68-prog/ABC/issues)
- **Questions:** [Contact information]
- **Demo Request:** [Demo scheduling]

---

**Ready to verify truth in post-AGI intelligence? Start with Step 1 above.**

