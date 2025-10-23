# Claro Distribution MCP for Odoo Cloud

## 🎯 The Solution for Cloud Users

Since your client uses **Odoo Cloud** (not on-premise), you cannot install custom modules directly. Instead, we'll create a **standalone MCP server** that connects to their existing Odoo via API.

### What This Means:
- ✅ No changes needed to their Odoo
- ✅ Uses Odoo's built-in API
- ✅ Works with standard Odoo Cloud
- ✅ You control and host the MCP server separately
- ✅ Claude can still analyze their data!

---

## 📊 Architecture Overview

```
┌──────────────────────────────────────────┐
│  CLIENT'S ODOO CLOUD                     │
│  (yourcompany.odoo.com)                  │
│                                          │
│  - Sales Orders                          │
│  - Products/Services                     │
│  - Invoices                              │
│  - Customers                             │
│  - Expenses                              │
│  - Standard Odoo modules                 │
└──────────────┬───────────────────────────┘
               │
               │ Odoo XML-RPC API
               │ (Built-in, always available)
               │ Authenticated with username/password
               │
               ▼
┌──────────────────────────────────────────┐
│  YOUR MCP SERVER                         │
│  (Hosted separately - Railway, Heroku,   │
│   DigitalOcean, AWS, etc.)               │
│                                          │
│  Python Flask app:                       │
│  - Connects to Odoo API                  │
│  - Exposes MCP endpoints                 │
│  - Processes and analyzes data           │
└──────────────┬───────────────────────────┘
               │
               │ MCP Protocol
               │ (JSON over HTTPS)
               │ Authenticated with API key
               │
               ▼
┌──────────────────────────────────────────┐
│  CLAUDE                                  │
│  (AI Assistant for analysis)             │
└──────────────────────────────────────────┘
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Get Odoo API Credentials (5 minutes)

You need these from your client's Odoo:

1. **Odoo URL**: e.g., `yourcompany.odoo.com`
2. **Database name**: Found in URL or ask Odoo admin
3. **Username**: An Odoo user with access (ideally admin)
4. **Password**: That user's password

**How to test if you have correct credentials:**
- Try logging into their Odoo web interface
- If you can log in, the credentials work for API too!

### Step 2: Deploy MCP Server (15-30 minutes)

You need to host the Python server somewhere. Options:

**Easy Options (Recommended for beginners):**
- **Railway.app** - Free tier, very easy
- **Heroku** - Free tier, well-documented
- **PythonAnywhere** - Python-specific hosting

**Professional Options:**
- **DigitalOcean** - $5/month
- **AWS EC2** - Pay per use
- **Google Cloud Run** - Serverless

**I'll show you Railway (easiest):**

### Step 3: Configure & Test (10 minutes)

Set up environment variables and test the connection.

---

## 📦 What You Have

### Files Created:

1. **standalone_mcp_server.py** - The complete MCP server
2. **.env.example** - Configuration template
3. **requirements.txt** - Python dependencies

---

## 🛠️ Detailed Setup Guide

### Option A: Deploy to Railway (Easiest)

**Railway.app** is the easiest way to deploy Python apps. Here's how:

#### 1. Prepare Your Files

Create a project folder with these files:
```
claro-mcp-server/
├── standalone_mcp_server.py  (the MCP server code)
├── requirements.txt           (dependencies)
├── .env                       (your configuration - DO NOT commit to Git)
├── Procfile                   (tells Railway how to run it)
└── README.md                  (documentation)
```

#### 2. Create Procfile

Create a file named `Procfile` (no extension) with this content:
```
web: gunicorn standalone_mcp_server:app
```

#### 3. Create .env File

Copy `.env.example` to `.env` and fill in your client's details:
```bash
ODOO_HOST=yourclient.odoo.com
ODOO_DATABASE=yourclient-db
ODOO_USERNAME=admin@yourclient.com
ODOO_PASSWORD=their-password
MCP_API_KEY=create-a-strong-unique-key-here
```

⚠️ **IMPORTANT**: Never commit `.env` to Git! Add it to `.gitignore`

#### 4. Deploy to Railway

1. Go to https://railway.app/
2. Sign up (free with GitHub)
3. Click "New Project" → "Deploy from GitHub repo"
4. Connect your GitHub and select your repository
5. Railway automatically detects Python and installs dependencies
6. Add environment variables in Railway dashboard (copy from your .env)
7. Deploy!

Railway will give you a URL like: `https://your-app.railway.app`

#### 5. Test It

Visit: `https://your-app.railway.app/mcp/health`

You should see:
```json
{
  "status": "healthy",
  "service": "Claro Distribution MCP Server (Standalone)",
  "version": "2.0",
  "odoo_status": "connected"
}
```

If `odoo_status` is "connected", you're all set! ✅

---

### Option B: Deploy to Heroku

1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
2. Login: `heroku login`
3. Create app: `heroku create claro-mcp-server`
4. Set environment variables:
   ```bash
   heroku config:set ODOO_HOST=yourclient.odoo.com
   heroku config:set ODOO_DATABASE=yourclient-db
   heroku config:set ODOO_USERNAME=admin@yourclient.com
   heroku config:set ODOO_PASSWORD=their-password
   heroku config:set MCP_API_KEY=your-secure-key
   ```
5. Deploy:
   ```bash
   git add .
   git commit -m "Deploy MCP server"
   git push heroku main
   ```
6. Test: `https://your-app.herokuapp.com/mcp/health`

---

### Option C: Run Locally (For Testing)

If you want to test on your computer first:

#### 1. Install Python Dependencies

```bash
cd /path/to/your/project
pip install -r requirements.txt
```

#### 2. Create .env File

Copy `.env.example` to `.env` and fill in real values.

#### 3. Run the Server

```bash
python standalone_mcp_server.py
```

You should see:
```
============================================================
Claro Distribution MCP Server - Standalone Version
============================================================

Odoo Host: yourclient.odoo.com
Odoo Database: yourclient-db

Starting server...

Health check: http://localhost:5000/mcp/health
============================================================
 * Running on http://0.0.0.0:5000
```

#### 4. Test Locally

Open browser: http://localhost:5000/mcp/health

---

## 🧪 Testing the Server

### Test 1: Health Check

```bash
curl https://your-server.railway.app/mcp/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "Claro Distribution MCP Server (Standalone)",
  "odoo_status": "connected"
}
```

### Test 2: List Resources

```bash
curl -X POST https://your-server.railway.app/mcp/resources \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-mcp-api-key"}'
```

### Test 3: Get Sales Data

```bash
curl -X POST https://your-server.railway.app/mcp/tool/call \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your-mcp-api-key",
    "name": "get_sales_summary",
    "arguments": {}
  }'
```

---

## 🤖 Using with Claude

Once deployed, tell Claude:

"I have an MCP server at https://your-server.railway.app with API key [your-key]. Can you analyze my Claro distribution sales data?"

Then ask questions like:
- "What are our total sales this month?"
- "Show me our top 10 customers"
- "What's our revenue trend over the last 6 months?"
- "Which products/services are selling best?"

---

## 📊 What Data It Can Access

This standalone server uses **standard Odoo models** that exist in every Odoo Cloud:

### ✅ Available Data:

1. **Products/Services** (`product.product`)
   - All services your client sells
   - Prices, categories

2. **Sales Orders** (`sale.order`)
   - All sales transactions
   - Dates, amounts, customers

3. **Invoices** (`account.move`)
   - Customer invoices
   - Revenue data

4. **Customers** (`res.partner`)
   - Customer information
   - Contact details

5. **Expenses** (if module installed)
   - Company expenses
   - Cost tracking

### 🎯 Analysis Tools Included:

1. **get_sales_summary** - Sales by product/service
2. **get_revenue_by_period** - Monthly/quarterly trends
3. **get_top_customers** - Best customers by revenue
4. **get_expense_analysis** - Expense breakdown

---

## 🏢 For Your Claro Distribution Use Case

### Mapping to Your Business Needs:

**Your Need** → **Odoo Equivalent**

- **Business Lines** → Product Categories
- **Contact Centers** → Analytic Accounts or Tags
- **Sales per Line** → Sales by Product Category
- **Costs per Center** → Expenses by Analytic Account

### Setting Up in Odoo Cloud:

1. **Create Product Categories** for each business line:
   - Go to Sales → Products → Product Categories
   - Create: "Postpaid Mobile", "Internet", "TV", etc.

2. **Tag Customers/Orders** by center:
   - Use Tags or Analytic Accounts
   - Tag each sale with the center location

3. **Track Expenses** by center:
   - Use Analytic Accounts
   - Assign each expense to a center

This way, the standard Odoo data structure works for your needs!

---

## 💰 Cost Comparison

### Hosting Costs:

**Free Tiers:**
- Railway: Free for hobby projects
- Heroku: Free tier available
- PythonAnywhere: Free basic tier

**Paid Options:**
- Railway: $5/month for production
- Heroku: $7/month for basic
- DigitalOcean: $5/month droplet
- AWS/GCP: ~$5-10/month

**vs. Odoo.sh:**
- Odoo.sh: $250+/month (way more expensive!)

### Total Cost:
**This solution: $0-10/month**
**Odoo.sh custom modules: $250+/month**

---

## 🔐 Security Considerations

### Best Practices:

1. **Use Environment Variables**
   - Never hardcode passwords
   - Use `.env` file locally
   - Use platform's config for production

2. **Strong API Key**
   - Generate: `openssl rand -hex 32`
   - Keep it secret
   - Rotate periodically

3. **HTTPS Only**
   - Railway/Heroku provide HTTPS automatically
   - Never use HTTP in production

4. **Odoo User Permissions**
   - Create a dedicated API user
   - Give minimum necessary permissions
   - Not your personal admin account

5. **Monitor Access**
   - Check server logs regularly
   - Watch for unusual API calls

---

## 🐛 Troubleshooting

### Problem: "odoo_status": "disconnected"

**Solutions:**
- Check ODOO_HOST is correct (no https://, just domain)
- Verify ODOO_DATABASE name
- Test credentials by logging into Odoo web interface
- Check if Odoo API is enabled (it should be by default)

### Problem: "Invalid API key"

**Solutions:**
- Check MCP_API_KEY in environment variables
- Make sure you're sending the same key in requests
- No extra spaces or quotes

### Problem: "Module 'xyz' not found" error

**Solutions:**
- Your client may not have that Odoo module installed
- Check which modules they have: Settings → Apps
- Modify the code to use available modules

### Problem: Server not starting

**Solutions:**
- Check all dependencies installed: `pip install -r requirements.txt`
- Verify Python version (3.8+)
- Check environment variables are set
- Look at error logs

---

## 🔄 Updating the Server

When you need to add features or fix bugs:

1. **Make changes locally**
2. **Test** locally
3. **Commit** to Git
4. **Push** to GitHub
5. Railway/Heroku automatically redeploys

Or manually redeploy:
```bash
git push heroku main  # for Heroku
git push origin main  # Railway auto-deploys
```

---

## 📈 Scaling Considerations

### Current Setup:
- Good for: 1-100 requests/minute
- Single server instance
- Suitable for: Small to medium business

### If You Need More:
- Add caching (Redis)
- Multiple server instances
- Load balancer
- Database connection pooling

But for most Claro distribution use cases, the basic setup is plenty!

---

## ✅ Deployment Checklist

- [ ] Created Railway/Heroku account
- [ ] Prepared all files (server, requirements, Procfile)
- [ ] Got Odoo credentials from client
- [ ] Created strong MCP API key
- [ ] Deployed server
- [ ] Set environment variables
- [ ] Tested /mcp/health endpoint
- [ ] Verified odoo_status is "connected"
- [ ] Tested with Claude
- [ ] Documented API key securely
- [ ] Set up monitoring/alerts

---

## 🎓 For Beginners

If this is your first time deploying a Python app:

### Don't worry! Here's what each thing does:

**Python** = Programming language (like Spanish or English, but for computers)

**Flask** = Tool to create web servers in Python (handles web requests)

**OdooRPC** = Library to talk to Odoo's API (like a translator)

**Railway/Heroku** = Platforms that run your code 24/7 (like renting a computer in the cloud)

**.env file** = Secret configuration file (like a safe for passwords)

**API** = Way for programs to talk to each other (like a phone line)

**MCP** = Standard way for AI to get data (like a universal adapter)

### Learning Resources:
- Flask Tutorial: https://flask.palletsprojects.com/
- Odoo API Docs: https://www.odoo.com/documentation/18.0/developer/reference/external_api.html
- Railway Docs: https://docs.railway.app/
- Python Basics: https://docs.python.org/3/tutorial/

---

## 🎉 You're Ready!

You now have everything to implement MCP for Odoo Cloud:

1. ✅ Standalone MCP server code
2. ✅ Deployment instructions
3. ✅ Configuration templates
4. ✅ Testing procedures
5. ✅ Troubleshooting guide

**Next steps:**
1. Get Odoo credentials from your client
2. Deploy to Railway (easiest option)
3. Configure environment variables
4. Test the connection
5. Start asking Claude questions!

---

## 💡 Pro Tips

1. **Start with Railway** - It's the easiest for beginners
2. **Test locally first** - Make sure everything works on your computer
3. **Use strong API keys** - Generate with `openssl rand -hex 32`
4. **Monitor your logs** - Railway/Heroku dashboards show errors
5. **Keep credentials safe** - Never commit .env to Git

---

**Need help?** Ask me (Claude) anything as you go through the setup! 🚀
