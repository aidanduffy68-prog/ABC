# Using Ethereum Risk Data with Bubblemaps.io

## About Bubblemaps.io

[Bubblemaps.io](https://v2.bubblemaps.io/) is a platform for creating interactive bubble/network visualizations. While primarily designed for blockchain token holder analysis, the data format can be adapted for risk analysis visualizations.

## Quick Start

### Option 1: Direct Upload (if supported)
1. Go to https://v2.bubblemaps.io/
2. Look for "Upload Data" or "Import" option
3. Upload the JSON file: `ethereum_risks_bubblemaps.json`
   - OR upload CSV files: `ethereum_risks_nodes.csv` and `ethereum_risks_links.csv`

### Option 2: iFrame Integration (if you have Partner ID)
If you have a Bubblemaps partner ID, you can embed the visualization:

```html
<iframe
  src="https://iframe.bubblemaps.io/map?data=[your_data_url]&partnerId=[partner_id]"
  style="width:100%;height:700px;border:none;"
></iframe>
```

### Option 3: Data API (if available)
Contact Bubblemaps for API access to programmatically create visualizations.

## Alternative: Use Data with Other Tools

If bubblemaps.io doesn't support custom risk data uploads, you can use the exported data with:
- **D3.js** - Interactive network visualizations
- **Cytoscape.js** - Graph visualization library
- **Gephi** - Network analysis tool
- **Observable** - Interactive data visualization platform

## Data Structure

### Nodes (Risks)
- **P0:** Chain-Agnostic Architecture (92% - Critical)
- **P1:** Ethereum Integration (88% - High)
- **P2:** Multi-Agency Deployment (75% - Medium)

### Links (Relationships)
- P0 ↔ P1: EVM Support Enables Market Expansion
- P0 ↔ P2: Multi-Agency Enables Market Expansion
- P1 ↔ P2: EVM Support Enables Multi-Agency

## Customization

In bubblemaps.io, you can:
- Adjust bubble sizes based on 'value' or 'size' field
- Color-code by 'category' (Critical/High/Medium)
- Show/hide connection lines
- Add labels and descriptions

## Files Generated

- `ethereum_risks_bubblemaps.json` - Complete data in JSON format
- `ethereum_risks_nodes.csv` - Node data (risks)
- `ethereum_risks_links.csv` - Link data (connections)
