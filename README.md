# Claro Distribution MCP Server - Standalone Version

## 🎯 For Odoo Cloud Users

This is a standalone MCP (Model Context Protocol) server that connects to **Odoo Cloud** via API. No custom modules needed - works with standard Odoo!

## 🚀 Quick Start

### 1. Get Odoo Credentials
From your Odoo Cloud instance, you need:
- Odoo URL (e.g., `yourcompany.odoo.com`)
- Database name
- Username (with API access)
- Password

### 2. Deploy the Server

**Easiest option: Railway.app**
1. Sign up at https://railway.app
2. Create new project from GitHub
3. Add environment variables (see below)
4. Deploy!

### 3. Configure Environment Variables

Create a `.env` file or set in your hosting platform:

```env
ODOO_HOST=yourcompany.odoo.com
ODOO_PORT=443
ODOO_PROTOCOL=jsonrpc+ssl
ODOO_DATABASE=yourcompany-db
ODOO_USERNAME=admin@yourcompany.com
ODOO_PASSWORD=your-password
MCP_API_KEY=your-secure-api-key
```

### 4. Test

Visit: `https://your-server.railway.app/mcp/health`

Expected response:
```json
{
  "status": "healthy",
  "odoo_status": "connected"
}
```

## 📁 Files Included

- `standalone_mcp_server.py` - The MCP server
- `requirements.txt` - Python dependencies
- `.env.example` - Configuration template
- `Procfile` - For Railway/Heroku deployment
- `.gitignore` - Protects sensitive files
- `ODOO_CLOUD_GUIDE.md` - Complete setup guide

## 🔧 Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
cp .env.example .env
# Edit .env with your actual values

# Run server
python standalone_mcp_server.py

# Test
curl http://localhost:5000/mcp/health
```

## 🤖 Using with Claude

Once deployed, you can ask Claude to analyze your Odoo data:

"I have an MCP server at https://your-server.com with API key [key]. What were our total sales last month?"

## 📊 Available Tools

1. **get_sales_summary** - Sales by product/service
2. **get_revenue_by_period** - Monthly/quarterly trends
3. **get_top_customers** - Best customers by revenue
4. **get_expense_analysis** - Expense breakdown

## 🌐 Deployment Options

### Railway (Recommended)
- Free tier available
- Automatic HTTPS
- Easy GitHub integration
- https://railway.app

### Heroku
- Free tier available
- Well-documented
- https://heroku.com

### DigitalOcean
- $5/month
- More control
- https://digitalocean.com

## 📖 Full Documentation

See `ODOO_CLOUD_GUIDE.md` for:
- Detailed setup instructions
- Architecture diagrams
- Troubleshooting guide
- Security best practices
- Scaling considerations

## 🔐 Security

- ✅ Use HTTPS in production
- ✅ Keep `.env` file secret (never commit to Git)
- ✅ Use strong API keys
- ✅ Create dedicated Odoo API user
- ✅ Monitor access logs

## 🐛 Troubleshooting

**odoo_status: "disconnected"**
- Check ODOO_HOST (no https://)
- Verify credentials work in Odoo web interface
- Ensure database name is correct

**"Invalid API key"**
- Check MCP_API_KEY matches in both places
- No extra spaces or quotes

See `ODOO_CLOUD_GUIDE.md` for more troubleshooting.

## 💡 Tips

- Start with Railway - it's easiest
- Test locally before deploying
- Use environment variables, never hardcode passwords
- Monitor your server logs
- Keep dependencies updated

## 📞 Support

- Full guide: See `ODOO_CLOUD_GUIDE.md`
- Odoo API docs: https://www.odoo.com/documentation/18.0/developer/reference/external_api.html
- Flask docs: https://flask.palletsprojects.com/
- Ask Claude for help!

## ✅ Deployment Checklist

- [ ] Got Odoo credentials
- [ ] Created hosting account (Railway/Heroku)
- [ ] Uploaded files
- [ ] Set environment variables
- [ ] Deployed server
- [ ] Tested /mcp/health
- [ ] Verified Odoo connection
- [ ] Tested with Claude

## 🎉 You're Ready!

Your standalone MCP server lets Claude analyze your Odoo Cloud data without any custom modules!

---

**Made for Claro Distribution - Colombia**
*Track sales, analyze costs, make data-driven decisions with AI*
