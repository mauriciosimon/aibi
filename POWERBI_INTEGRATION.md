# Power BI MCP Integration - Multi-Source Business Intelligence

## What Has Been Built

We've successfully integrated Power BI data warehouse access into the intelligent chat system, creating a **multi-source business intelligence assistant** that can access both Odoo ERP (operational data) and Power BI (data warehouse/analytics).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Intelligent Chat Frontend                   │
│          (intelligent_chat_interface.html)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│             Intelligent Chat Backend (Flask)                 │
│          (intelligent_chat_server.py:5000)                   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │        Claude Sonnet 4.5 (Business Analyst AI)        │  │
│  │  - Intelligent query routing                          │  │
│  │  - Cross-source data correlation                      │  │
│  │  - Executive insights & alerts                        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─────────────────┐          ┌──────────────────────────┐  │
│  │  Odoo Tools     │          │  Power BI Tools          │  │
│  │  (get_*)        │          │  (powerbi_*)             │  │
│  └────────┬────────┘          └──────────┬───────────────┘  │
└───────────┼────────────────────────────────┼─────────────────┘
            │                                 │
            ▼                                 ▼
┌──────────────────────┐      ┌──────────────────────────────┐
│  Odoo MCP HTTP       │      │  Power BI MCP HTTP           │
│  Server              │      │  Server                      │
│  (Port 6000)         │      │  (Port 5003)                 │
│                      │      │  (powerbi_mcp_http_server.py)│
│  ┌────────────────┐ │      │  ┌────────────────────────┐  │
│  │  Odoo MCP      │ │      │  │  Power BI MCP          │  │
│  │  (stdio)       │ │      │  │  (stdio)               │  │
│  └────────────────┘ │      │  │  powerbi_mcp_server.py │  │
└──────────┬───────────┘      │  └────────────────────────┘  │
           │                  └──────────────┬───────────────┘
           ▼                                 │
    ┌─────────────┐                         ▼
    │ Odoo Cloud  │                 ┌──────────────────┐
    │ ERP System  │                 │  Power BI API    │
    └─────────────┘                 │  (Azure AD Auth) │
                                    └──────────────────┘
```

## Files Created/Modified

### New Files Created

1. **`powerbi_mcp_server.py`** - Core Power BI MCP server (stdio protocol)
   - Authenticates with Azure AD using client credentials
   - Provides 6 MCP tools for Power BI data access
   - Caches authentication tokens for efficiency

2. **`powerbi_mcp_http_server.py`** - HTTP wrapper for Power BI MCP
   - Runs Power BI MCP server as subprocess
   - Provides HTTP endpoints for tool calls
   - Port 5003 (configurable via `POWERBI_MCP_PORT`)

### Modified Files

3. **`intelligent_chat_server.py`** - Multi-source intelligence orchestration
   - Added `POWERBI_MCP_TOOLS` - 4 Power BI tools exposed to Claude
   - Updated `call_mcp_tool()` - Intelligent routing to Odoo or Power BI
   - Updated `get_all_available_tools()` - Merges Odoo + Power BI tools
   - **NEW SYSTEM PROMPT** - Claude now knows about multi-source access

4. **`.env`** - Environment variables (already contains Power BI credentials)
   - `POWERBI_CLIENT_ID`
   - `POWERBI_TENANT_ID`
   - `POWERBI_CLIENT_SECRET`
   - `POWERBI_MCP_SERVER_URL` (defaults to `http://localhost:5003`)

## Power BI MCP Tools Available to Claude

Claude can now use these 4 tools to access Power BI data:

### 1. `powerbi_list_workspaces`
Lists all Power BI workspaces (data lakes) accessible to the service principal.

**Usage:**
```python
powerbi_list_workspaces()
```

**Returns:**
```json
{
  "success": true,
  "workspaces": [
    {
      "id": "workspace-uuid",
      "name": "Sales Analytics",
      "type": "Workspace"
    }
  ]
}
```

### 2. `powerbi_list_datasets`
Lists all datasets in a specific workspace.

**Usage:**
```python
powerbi_list_datasets(workspace_id="workspace-uuid")
```

**Returns:**
```json
{
  "success": true,
  "datasets": [
    {
      "id": "dataset-uuid",
      "name": "Sales Data Model",
      "configured_by": "user@example.com"
    }
  ]
}
```

### 3. `powerbi_get_dataset_schema`
Gets the complete schema of a dataset (tables, columns, measures).

**Usage:**
```python
powerbi_get_dataset_schema(
    workspace_id="workspace-uuid",
    dataset_id="dataset-uuid"
)
```

**Returns:**
```json
{
  "success": true,
  "tables": [
    {
      "name": "Sales",
      "columns": [
        {"name": "OrderDate", "dataType": "DateTime"},
        {"name": "Revenue", "dataType": "Double"}
      ],
      "measures": [
        {"name": "TotalRevenue", "expression": "SUM(Sales[Revenue])"}
      ]
    }
  ]
}
```

### 4. `powerbi_execute_dax`
Executes DAX queries against Power BI datasets to retrieve data.

**Usage:**
```python
powerbi_execute_dax(
    workspace_id="workspace-uuid",
    dataset_id="dataset-uuid",
    dax_query="EVALUATE Sales"
)
```

**Returns:**
```json
{
  "success": true,
  "row_count": 1523,
  "rows": [
    {
      "OrderDate": "2025-01-01T00:00:00",
      "Revenue": 15000.50,
      "Customer": "Acme Corp"
    }
  ]
}
```

## Claude's Multi-Source Intelligence Capabilities

Claude now has a comprehensive understanding of when to use each data source:

### Odoo ERP (Operational Data)
- **Use for**: Real-time operational data, transactional details, current state
- **Examples**:
  - "Show me today's sales orders"
  - "List employees hired this month"
  - "What's the current inventory level?"

### Power BI (Data Warehouse)
- **Use for**: Historical trends, complex analytics, aggregated insights
- **Examples**:
  - "Show me sales trends over the last 2 years"
  - "What's our year-over-year revenue growth?"
  - "Analyze customer segmentation patterns"

### Cross-Source Analysis
Claude can intelligently query BOTH sources and correlate findings:
- **Example**: "Compare today's sales (Odoo) with historical averages (Power BI)"

## System Prompt Enhancement

The new system prompt educates Claude about:

1. **Data Sources Available**:
   - Odoo ERP for operational data
   - Power BI for data warehouse analytics

2. **Intelligent Source Selection**:
   - When to use Odoo tools (`get_*`)
   - When to use Power BI tools (`powerbi_*`)
   - How to perform cross-source analysis

3. **Power BI Workflow**:
   - Step 1: Discover workspaces
   - Step 2: Find relevant datasets
   - Step 3: Inspect schema
   - Step 4: Execute DAX queries

4. **Business Analyst Role**:
   - Provide executive summaries
   - Identify trends and anomalies
   - Generate actionable insights
   - Proactively suggest analyses

## Testing Locally

The Power BI MCP HTTP server is running successfully:

```bash
# Terminal 1: Power BI MCP Server
source venv/bin/activate
python3 powerbi_mcp_http_server.py

# Terminal 2: Intelligent Chat Server
source venv/bin/activate
python3 intelligent_chat_server.py

# Open browser
http://localhost:5000
```

**Test queries you can try:**
- "What Power BI workspaces do we have?"
- "List the datasets in workspace X"
- "Show me the schema of dataset Y"
- "Query sales data from Power BI"

## Railway Deployment

### Current Status
- ✅ Odoo MCP server deployed and working
- ✅ Intelligent chat server deployed and working
- ⏳ Power BI MCP server ready for deployment

### Deployment Steps

#### Option 1: New Service for Power BI MCP

1. **Create new Railway service:**
   ```bash
   railway service create powerbi-mcp
   ```

2. **Link to project:**
   ```bash
   railway link
   ```

3. **Set environment variables:**
   ```bash
   railway variables set POWERBI_CLIENT_ID=...
   railway variables set POWERBI_TENANT_ID=...
   railway variables set POWERBI_CLIENT_SECRET=...
   railway variables set MCP_API_KEY=odoo-mcp-2025
   ```

4. **Create `Procfile` for Power BI MCP:**
   ```
   web: python3 powerbi_mcp_http_server.py
   ```

5. **Deploy:**
   ```bash
   railway up --service powerbi-mcp
   ```

6. **Update intelligent-chat service:**
   Set the Power BI MCP URL:
   ```bash
   railway variables set POWERBI_MCP_SERVER_URL=https://powerbi-mcp-production.up.railway.app --service intelligent-chat
   ```

7. **Redeploy intelligent-chat:**
   ```bash
   railway up --service intelligent-chat
   ```

#### Option 2: All-in-One Deployment

Alternatively, you could modify `intelligent_chat_server.py` to start the Power BI MCP server as a subprocess (similar to how some projects bundle multiple services).

## Environment Variables Summary

### Intelligent Chat Server
```env
ANTHROPIC_API_KEY=...
MCP_SERVER_URL=https://mcp-odoo-production.up.railway.app
MCP_API_KEY=odoo-mcp-2025
POWERBI_MCP_SERVER_URL=http://localhost:5003  # Change to Railway URL after deployment
```

### Power BI MCP Server (New Service)
```env
POWERBI_CLIENT_ID=your-azure-client-id
POWERBI_TENANT_ID=your-azure-tenant-id
POWERBI_CLIENT_SECRET=your-azure-client-secret
MCP_API_KEY=your-mcp-api-key
POWERBI_MCP_PORT=5003  # Railway will override with PORT
```

## Benefits of This Integration

1. ✅ **Unified Business Intelligence**: Access both operational and analytical data in one conversation
2. ✅ **Intelligent Query Routing**: Claude automatically chooses the right data source
3. ✅ **Cross-Source Correlation**: Compare real-time with historical data
4. ✅ **Executive Insights**: AI-powered business analysis and recommendations
5. ✅ **Scalable Architecture**: Easy to add more data sources (Salesforce, SQL, etc.)
6. ✅ **MCP Protocol**: Consistent, standardized tool interface
7. ✅ **Security**: Service principal authentication with Azure AD

## Example Business Intelligence Queries

### Basic Power BI Access
```
"What Power BI workspaces do we have access to?"
"Show me all datasets in the Sales workspace"
"What's the schema of the Revenue dataset?"
```

### Data Warehouse Queries
```
"Query the Sales dataset and show me revenue by month"
"Execute a DAX query to get top 10 customers"
"Show me year-over-year growth from Power BI"
```

### Multi-Source Intelligence
```
"Compare today's sales from Odoo with last month's average from Power BI"
"Show me current inventory (Odoo) and historical stock trends (Power BI)"
"Analyze employee productivity: current from Odoo, trends from Power BI"
```

### Business Analyst Mode
```
"Give me an executive summary of our business performance"
"What trends should I be aware of?"
"Are there any anomalies in the data I should investigate?"
```

## Next Steps

1. **Deploy Power BI MCP to Railway** (see deployment steps above)
2. **Update POWERBI_MCP_SERVER_URL** in intelligent-chat service
3. **Test end-to-end** with real Power BI workspaces and datasets
4. **Add more data sources** (following the same MCP pattern)
5. **Implement proactive alerts** (Claude monitoring data and sending notifications)

## Technical Notes

### Power BI MCP Server (powerbi_mcp_server.py)

- **Protocol**: JSON-RPC 2.0 over stdio
- **Authentication**: Azure AD OAuth 2.0 (client credentials flow)
- **Token Caching**: Tokens are cached until expiration
- **API Base**: `https://api.powerbi.com/v1.0/myorg`
- **Error Handling**: Comprehensive error messages returned to caller

### HTTP Wrapper (powerbi_mcp_http_server.py)

- **Framework**: Flask with CORS
- **Default Port**: 5003 (configurable)
- **API Key Protection**: Same MCP_API_KEY as Odoo
- **Subprocess Management**: Handles MCP server lifecycle
- **Threading**: Thread-safe message ID counter

### Integration Points (intelligent_chat_server.py)

- **Line 375-420**: POWERBI_MCP_TOOLS definition
- **Line 423-470**: call_mcp_tool() with routing logic
- **Line 180-208**: get_all_available_tools() merging
- **Line 721-750**: Multi-source system prompt

## Support & Troubleshooting

### Common Issues

**Power BI MCP won't start:**
- Check that Power BI credentials are in `.env`
- Verify Azure AD app has Power BI API permissions
- Check port 5003 isn't already in use

**Claude not using Power BI tools:**
- Verify tools are loaded: check logs for "Loaded X total tools"
- Check POWERBI_MCP_SERVER_URL is correct
- Ensure Power BI MCP server is running and healthy

**Authentication errors:**
- Verify client ID, tenant ID, and secret are correct
- Check Azure AD app permissions include `Dataset.Read.All`
- Ensure service principal has access to Power BI workspaces

## Files Reference

| File | Purpose | Lines Changed/Added |
|------|---------|-------------------|
| `powerbi_mcp_server.py` | Core MCP server | 267 lines (new) |
| `powerbi_mcp_http_server.py` | HTTP wrapper | 218 lines (new) |
| `intelligent_chat_server.py` | Multi-source orchestration | ~100 lines modified |
| `.env` | Environment variables | Power BI creds already present |
| `POWERBI_INTEGRATION.md` | This document | Documentation |

---

**Created by**: Claude Code
**Date**: 2025-11-07
**Status**: ✅ Integration complete, ready for Railway deployment
