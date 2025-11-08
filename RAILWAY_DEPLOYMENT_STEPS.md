# Railway Deployment Steps - Power BI MCP Service

## Current Status
- ✅ intelligent-chat service: Running
- ✅ mcp-odoo service: Running
- ⏳ powerbi-mcp service: **Ready to deploy**

## Power BI MCP Service Deployment

### Method 1: Railway Dashboard (Recommended)

1. **Go to Railway Dashboard**
   - Visit: https://railway.app/project/mcp-odoo-standalone
   - Navigate to your `mcp-odoo-standalone` project

2. **Create New Service**
   - Click "+ New Service"
   - Select "Empty Service"
   - Name it: `powerbi-mcp`

3. **Configure the Service**
   - Go to Settings tab
   - Under "Build & Deploy":
     - **Start Command**: `python3 powerbi_mcp_http_server.py`
     - **Build Command**: (leave empty, Python doesn't need building)

4. **Set Environment Variables**
   Go to Variables tab and add:
   ```
   POWERBI_CLIENT_ID=your-azure-client-id
   POWERBI_TENANT_ID=your-azure-tenant-id
   POWERBI_CLIENT_SECRET=your-azure-client-secret
   MCP_API_KEY=your-mcp-api-key
   POWERBI_MCP_PORT=$PORT
   ```

   ⚠️ **Important**: Railway automatically provides `PORT` env variable. We map it to `POWERBI_MCP_PORT`.

5. **Deploy the Code**
   - Go to Deployments tab
   - Click "Deploy"
   - Select deployment source:
     - **Option A**: Connect to GitHub repo
     - **Option B**: Railway CLI: `railway up --service powerbi-mcp`
     - **Option C**: Manual upload from dashboard

6. **Get the Service URL**
   - Once deployed, Railway will provide a URL like:
   - `https://powerbi-mcp-production.up.railway.app`
   - Copy this URL - you'll need it for the next step

### Method 2: Railway CLI with Service Configuration

If you prefer CLI deployment:

```bash
# Ensure you're in the project directory
cd /Users/mauricio/Documents/Pantaia/MCPs/claro-mcp-server-standalone

# Link to the project (if not already linked)
railway link

# Set environment variables for the new service
railway variables set POWERBI_CLIENT_ID=your-azure-client-id --service powerbi-mcp
railway variables set POWERBI_TENANT_ID=your-azure-tenant-id --service powerbi-mcp
railway variables set POWERBI_CLIENT_SECRET=your-azure-client-secret --service powerbi-mcp
railway variables set MCP_API_KEY=your-mcp-api-key --service powerbi-mcp
railway variables set POWERBI_MCP_PORT='$PORT' --service powerbi-mcp

# Deploy
railway up --service powerbi-mcp
```

**Note**: You may need to create the service in the dashboard first before using `--service powerbi-mcp`.

## Step 2: Update intelligent-chat Service

Once Power BI MCP is deployed and you have the URL:

### Set the Power BI MCP URL in intelligent-chat

```bash
# Replace with your actual Power BI MCP URL from Railway
railway variables set POWERBI_MCP_SERVER_URL=https://powerbi-mcp-production.up.railway.app --service intelligent-chat

# Redeploy intelligent-chat to pick up the new variable
railway up --service intelligent-chat
```

### Verify Environment Variables

```bash
# Check intelligent-chat variables
railway variables --service intelligent-chat

# You should see:
# POWERBI_MCP_SERVER_URL=https://powerbi-mcp-production.up.railway.app
# ANTHROPIC_API_KEY=...
# MCP_SERVER_URL=https://mcp-odoo-production.up.railway.app
# ...etc
```

## Step 3: Test the Integration

### Test Power BI MCP Health

```bash
# Test the Power BI MCP service directly
curl https://powerbi-mcp-production.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Power BI MCP HTTP Server",
  "mcp_process_alive": true
}
```

### Test through Intelligent Chat

1. Open your intelligent chat UI: `https://intelligent-chat-production.up.railway.app`

2. Try these queries:
   ```
   "What Power BI workspaces do we have?"
   "List the datasets available in Power BI"
   "Show me the schema of a Power BI dataset"
   ```

3. Check logs for successful multi-source access:
   ```bash
   railway logs --service intelligent-chat
   ```

   Look for:
   ```
   Loaded X total tools (Odoo: Y, Power BI: 4, Dynamic: Z)
   ```

## Step 4: Monitor Deployments

### Check Deployment Status

```bash
# Power BI MCP logs
railway logs --service powerbi-mcp

# Intelligent Chat logs
railway logs --service intelligent-chat

# All services
railway logs
```

### Common Issues & Solutions

#### Power BI MCP won't start

**Issue**: Service crashes on startup

**Solution**:
1. Check logs: `railway logs --service powerbi-mcp`
2. Verify all environment variables are set
3. Ensure `powerbi_mcp_server.py` file is included in deployment
4. Check that Python dependencies are installed (Railway auto-detects `requirements.txt`)

#### Intelligent Chat can't connect to Power BI MCP

**Issue**: `POWERBI_MCP_SERVER_URL` connection error

**Solution**:
1. Verify Power BI MCP is running: `curl https://powerbi-mcp-production.up.railway.app/health`
2. Check `POWERBI_MCP_SERVER_URL` is set correctly in intelligent-chat
3. Ensure both services are in the same Railway project (they can communicate internally)
4. Try using Railway's internal service URL: `http://powerbi-mcp.railway.internal:5003`

#### Azure AD Authentication Fails

**Issue**: Power BI returns authentication errors

**Solution**:
1. Verify Power BI credentials in environment variables
2. Check Azure AD app has required permissions (`Dataset.Read.All`)
3. Ensure service principal has access to Power BI workspaces
4. Test credentials locally first before deploying

## Architecture After Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                 Railway Project: mcp-odoo-standalone         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Service: intelligent-chat                          │     │
│  │ URL: intelligent-chat-production.up.railway.app    │     │
│  │ Port: 5000                                         │     │
│  │ Env:                                               │     │
│  │   - ANTHROPIC_API_KEY                              │     │
│  │   - MCP_SERVER_URL (Odoo MCP)                      │     │
│  │   - POWERBI_MCP_SERVER_URL (Power BI MCP) ← NEW!  │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Service: mcp-odoo                                  │     │
│  │ URL: mcp-odoo-production.up.railway.app            │     │
│  │ Port: 6000                                         │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Service: powerbi-mcp ← NEW SERVICE!               │     │
│  │ URL: powerbi-mcp-production.up.railway.app         │     │
│  │ Port: Auto-assigned by Railway                     │     │
│  │ Env:                                               │     │
│  │   - POWERBI_CLIENT_ID                              │     │
│  │   - POWERBI_TENANT_ID                              │     │
│  │   - POWERBI_CLIENT_SECRET                          │     │
│  │   - MCP_API_KEY                                    │     │
│  │   - POWERBI_MCP_PORT=$PORT                         │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Files Deployed

Both `intelligent-chat` and `powerbi-mcp` services deploy from the same codebase but run different entry points:

### intelligent-chat service
- **Start command**: `python3 intelligent_chat_server.py`
- **Files used**:
  - `intelligent_chat_server.py`
  - `intelligent_chat_interface.html`
  - `powerbi_mcp_server.py` (referenced but not used directly)

### powerbi-mcp service
- **Start command**: `python3 powerbi_mcp_http_server.py`
- **Files used**:
  - `powerbi_mcp_http_server.py`
  - `powerbi_mcp_server.py` (subprocess)

## Verification Checklist

After deployment, verify:

- [ ] Power BI MCP service is running
- [ ] Power BI MCP health endpoint returns `200 OK`
- [ ] Intelligent chat has `POWERBI_MCP_SERVER_URL` set
- [ ] Intelligent chat logs show "Loaded X total tools (Odoo: Y, Power BI: 4...)"
- [ ] Can query: "What Power BI workspaces do we have?"
- [ ] Can query: "List datasets in Power BI"
- [ ] Cross-source queries work: "Compare Odoo sales with Power BI trends"

## Next Steps After Deployment

1. **Test multi-source queries** - Try questions that require both Odoo and Power BI
2. **Monitor logs** - Watch for any authentication or connection errors
3. **Document Power BI schema** - Help Claude understand your Power BI data model
4. **Create example DAX queries** - Test complex analytics scenarios
5. **Set up alerts** - Monitor service health and uptime

## Support

If you encounter issues:
1. Check Railway logs: `railway logs --service powerbi-mcp`
2. Test health endpoint: `curl https://powerbi-mcp-production.up.railway.app/health`
3. Verify environment variables: `railway variables --service powerbi-mcp`
4. Review `POWERBI_INTEGRATION.md` for troubleshooting tips

---

**Last Updated**: 2025-11-07
**Status**: Ready for deployment
