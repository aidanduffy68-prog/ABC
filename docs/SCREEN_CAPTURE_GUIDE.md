# Screen Capture Guide for ABC Demo Video

**What to screen capture for the Foundry-integrated ABC demo video**

---

## 🎬 Priority Screen Captures

### 1. **Terminal: Compilation Command & Output** ⭐⭐⭐
**Location:** Terminal/CLI  
**Duration:** 15-20 seconds  
**What to show:**

```bash
# Start with this command visible
python scripts/compile_intelligence.py \
  --mode federal_ai \
  --target Treasury \
  --foundry-push

# Then show the output:
# - Compilation time (<500ms)
# - Risk score (85%)
# - Confidence scores
# - "MAGIC MOMENT ACHIEVED!" message
# - Cryptographic hash
```

**Why:** Shows the core value proposition - fast compilation with verifiable results.

**File to reference:** `scripts/compile_intelligence.py`

---

### 2. **API Documentation (Swagger UI)** ⭐⭐⭐
**Location:** Browser  
**URL:** `http://localhost:8000/docs` (after running `python scripts/run_api_server.py`)

**What to show:**
- Foundry integration endpoints (`/api/v1/foundry/*`)
- Schema endpoint showing Foundry dataset structure
- Push endpoint with example request/response
- Export endpoints (JSON, CSV, Parquet)

**Why:** Demonstrates Foundry-native integration and professional API design.

**How to capture:**
1. Start API server: `python scripts/run_api_server.py`
2. Open browser to `http://localhost:8000/docs`
3. Navigate to Foundry endpoints section
4. Show endpoint details and schemas

---

### 3. **Threat Intel Compilation Report** ⭐⭐
**Location:** Markdown file in editor or rendered view  
**File:** `examples/intelligence_audits/INTELLIGENCE_AUDIT_TREASURY_003.md`

**What to show:**
- Executive Summary (risk score, key insights)
- Risk Assessment section with scores
- Cryptographic Verification section (hash)
- Key Takeaways

**Why:** Shows the final deliverable - professional, actionable intelligence.

**Alternative:** Use the DoW assessment: `examples/intelligence_audits/INTELLIGENCE_AUDIT_DOD_DHS_002.md`

---

### 4. **Foundry Workspace (If Available)** ⭐⭐⭐
**Location:** Palantir Foundry workspace  
**What to show:**
- ABC dataset in Foundry
- Compiled intelligence data visible
- Schema matching Foundry ontology
- Data visualization (if available)

**Why:** Proves Foundry integration works end-to-end.

**Note:** If you don't have Foundry access, you can:
- Mock it with a screenshot of Foundry UI (with ABC dataset name)
- Show the export files (JSON/CSV/Parquet) that would be imported
- Use the Foundry integration documentation as a placeholder

---

### 5. **Export Files (JSON/CSV/Parquet)** ⭐
**Location:** File explorer or terminal  
**What to show:**
- `foundry_exports/` directory
- Multiple format files (JSON, CSV, Parquet)
- File sizes and structure

**Why:** Shows Foundry-compatible export formats.

**How to generate:**
```bash
python scripts/export_to_foundry.py \
  --input compiled_output.json \
  --format all \
  --output-dir foundry_exports
```

---

### 6. **API Server Running** ⭐
**Location:** Terminal  
**What to show:**
- Server startup logs
- "Uvicorn running on http://0.0.0.0:8000"
- Health check endpoint response

**Why:** Shows the system is operational and ready.

**Command:**
```bash
python scripts/run_api_server.py
# Then in another terminal:
curl http://localhost:8000/api/v1/status/health
```

---

### 7. **Code Structure (Optional)** ⭐
**Location:** IDE/Editor  
**What to show:**
- `src/integrations/foundry/` directory
- `FoundryConnector` class
- Export functions

**Why:** Shows technical depth and Foundry integration code.

**Files:**
- `src/integrations/foundry/connector.py`
- `src/integrations/foundry/export.py`
- `src/api/routes/foundry.py`

---

## 📋 Screen Capture Checklist

### Must Have (Core Demo):
- [ ] Terminal: Compilation command and <500ms output
- [ ] Terminal: "MAGIC MOMENT ACHIEVED!" message
- [ ] API Docs: Foundry endpoints visible
- [ ] Threat Intel Report: Risk score and hash visible

### Should Have (Foundry Integration):
- [ ] Foundry workspace with ABC dataset (or mock)
- [ ] Export files (JSON/CSV/Parquet) in file explorer
- [ ] API server running and healthy

### Nice to Have (Technical Depth):
- [ ] Code structure showing Foundry integration
- [ ] Multiple compilation examples
- [ ] Drift detection alerts (if any)

---

## 🎥 Recording Tips

### Terminal Recording:
1. **Use a clean terminal** with readable font (Fira Code, JetBrains Mono)
2. **Increase font size** (16-18pt) for better visibility
3. **Use dark theme** (matches GH Systems branding)
4. **Clear terminal** before each command (`clear`)
5. **Type slowly** or use `script` command to replay

### Browser Recording:
1. **Full screen** the browser window
2. **Zoom in** on relevant sections (150-200%)
3. **Hide bookmarks bar** for cleaner look
4. **Use dark mode** if available

### File Explorer:
1. **List view** for better readability
2. **Show file sizes** and dates
3. **Highlight** relevant files

---

## 🎬 Suggested Recording Sequence

### Sequence 1: The Magic Moment (30 seconds)
1. Terminal: Show compilation command
2. Terminal: Show <500ms output
3. Terminal: Show "MAGIC MOMENT ACHIEVED!"
4. Terminal: Show cryptographic hash

### Sequence 2: Foundry Integration (45 seconds)
1. API Docs: Navigate to Foundry endpoints
2. API Docs: Show schema endpoint
3. API Docs: Show push endpoint
4. Terminal: Show export command
5. File Explorer: Show export files

### Sequence 3: Real Results (30 seconds)
1. Editor: Open Treasury assessment
2. Editor: Scroll to risk score (85%)
3. Editor: Scroll to cryptographic verification
4. Editor: Show key takeaways

---

## 🔧 Setup Commands (Before Recording)

```bash
# 1. Start API server (in one terminal)
python scripts/run_api_server.py

# 2. Generate export files (in another terminal)
python scripts/compile_intelligence.py \
  --mode federal_ai \
  --target Treasury \
  --output treasury_compiled.json

python scripts/export_to_foundry.py \
  --input treasury_compiled.json \
  --format all \
  --output-dir foundry_exports

# 3. Test compilation (for terminal recording)
python scripts/compile_intelligence.py \
  --mode federal_ai \
  --target Treasury \
  --foundry-push
```

---

## 📸 Screenshot Alternatives (If No Video)

If you can't record video, these screenshots work:

1. **Terminal output** showing compilation results
2. **API documentation** page (Swagger UI)
3. **Threat intel report** (rendered markdown)
4. **Foundry workspace** (if available) or export files
5. **Code structure** showing Foundry integration

---

## 🎨 Visual Enhancements

### Terminal Styling:
- **Font:** Fira Code or JetBrains Mono (monospace)
- **Theme:** Dark background, green text for success
- **Size:** 16-18pt for readability
- **Width:** 80-100 characters

### Browser Styling:
- **Zoom:** 150-200% for better visibility
- **Theme:** Dark mode if available
- **Full screen:** Hide unnecessary UI elements

---

## 📝 Notes

- **Foundry workspace:** If you don't have access, you can use the integration documentation or mock screenshots
- **Terminal speed:** Record at normal speed, can speed up in post-production
- **Multiple takes:** Record each section separately for easier editing
- **Audio:** Record narration separately or use text overlays

---

**Ready to record? Start with the Terminal compilation demo - that's your strongest visual proof of the <500ms magic moment.**

