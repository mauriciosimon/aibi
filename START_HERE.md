# 🚀 Quick Setup Guide

## What's in This Package

This is the **Claro MCP Server** - a standalone server that connects to Odoo Cloud via API, allowing Claude to analyze your business data.

## 📁 Files Included

### Core Files:
- `standalone_mcp_server.py` - The MCP server (main application)
- `requirements.txt` - Python dependencies
- `.env.example` - Configuration template
- `Procfile` - For Railway/Heroku deployment
- `.gitignore` - Protects sensitive files
- `README.md` - Project overview

### Documentation:
- `ODOO_CLOUD_GUIDE.md` - **START HERE!** Complete setup guide
- `CLAUDE_CODE_GUIDE.md` - How to use Claude Code for development
- `QUICK_REFERENCE.md` - Command cheat sheet
- `docs/` - Additional technical documentation

## ⚡ Quick Start (3 Steps)

### 1. Extract & Navigate
```bash
# Extract this zip to your desired location
# Example: ~/Documents/Pantaia/MCPs/

cd ~/Documents/Pantaia/MCPs/claro-mcp-server-standalone
```

### 2. Set Up with Claude Code
```bash
# Start Claude Code to help with setup
npx @anthropic-ai/claude-code
```

**Then ask Claude Code:**
```
Help me set up this MCP server project:
1. Review the files
2. Create a Python virtual environment
3. Set up git repository
4. Initialize the project for development
```

### 3. Configure for Your Odoo
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your Odoo credentials
nano .env  # or use your preferred editor
```

## 📖 What to Read First

1. **README.md** (5 min) - Project overview
2. **ODOO_CLOUD_GUIDE.md** (15 min) - Complete setup instructions
3. **CLAUDE_CODE_GUIDE.md** (10 min) - How to use Claude Code

## 🎯 First Prompt for Claude Code

Once Claude Code is running in your project directory:

```
I just extracted this MCP server project. Help me:
1. Review the project structure
2. Create a Python virtual environment
3. Install dependencies from requirements.txt
4. Initialize git repository
5. Create an initial commit
6. Explain what this project does
```

## 🔐 Configuration Required

Before deploying, you need:
- Odoo Cloud URL (e.g., yourcompany.odoo.com)
- Odoo database name
- Odoo username & password
- A secure MCP API key

These go in your `.env` file (copy from `.env.example`).

## 🚀 Deployment Options

**Easiest:** Railway.app
- Free tier available
- Automatic HTTPS
- Dead simple deployment

**Also Good:** Heroku, DigitalOcean, PythonAnywhere

See `ODOO_CLOUD_GUIDE.md` for detailed deployment instructions.

## 💡 What This Does

This server:
- ✅ Connects to your Odoo Cloud via API
- ✅ Exposes data through MCP protocol
- ✅ Lets Claude analyze your business data
- ✅ Requires no changes to your Odoo

## 📞 Getting Help

1. **Read the guides** - Start with ODOO_CLOUD_GUIDE.md
2. **Use Claude Code** - It can help with everything
3. **Ask Claude** (in this chat) - I'm here to help!

## ✅ Setup Checklist

- [ ] Extract zip file
- [ ] Navigate to project folder
- [ ] Start Claude Code: `npx @anthropic-ai/claude-code`
- [ ] Let Claude Code help set up the project
- [ ] Create `.env` file with your Odoo credentials
- [ ] Test locally: `python standalone_mcp_server.py`
- [ ] Deploy to Railway/Heroku
- [ ] Test with Claude!

## 🎉 You're Ready!

Everything you need is in this package. Follow the guides, use Claude Code for help, and you'll have your MCP server running in no time!

---

**Made for Claro Distribution - Colombia**
*Empower your business decisions with AI-powered data analysis*
