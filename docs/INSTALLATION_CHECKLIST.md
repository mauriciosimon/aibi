# Installation Checklist

Use this checklist to track your progress installing and setting up the Claro Distribution MCP module.

## Prerequisites ✓

- [ ] I have access to Odoo 18
- [ ] I can log in as an administrator
- [ ] I know my Odoo URL (e.g., https://mycompany.odoo.com)
- [ ] I have the claro_distribution_mcp.zip file

## Phase 1: Installation (15-20 minutes)

### Step 1: Upload Module
- [ ] Contact IT team or server administrator
- [ ] Send them the claro_distribution_mcp.zip file
- [ ] Ask them to:
  - [ ] Extract the zip file
  - [ ] Copy the `claro_distribution_mcp` folder to Odoo addons directory
  - [ ] Restart the Odoo service
  - [ ] Confirm module is in the right location

**OR** (if you have server access):
- [ ] SSH into the Odoo server
- [ ] Navigate to addons directory: `cd /opt/odoo/addons/`
- [ ] Upload and extract the module
- [ ] Restart Odoo: `sudo systemctl restart odoo`

### Step 2: Install in Odoo
- [ ] Open Odoo in web browser
- [ ] Log in as administrator
- [ ] Go to **Apps** menu
- [ ] Click the ⋯ menu → **Update Apps List**
- [ ] Wait for update to complete
- [ ] Remove any default filters (click X on filter tags)
- [ ] Search for: "Claro Distribution"
- [ ] Verify you can see the module
- [ ] Click **Install** button
- [ ] Wait for installation to complete (may take 1-2 minutes)
- [ ] Refresh the page

### Step 3: Verify Installation
- [ ] Look for "Claro Distribution" in the top menu
- [ ] Click on it
- [ ] You should see: Configuration submenu
- [ ] No errors displayed

## Phase 2: Configuration (10-15 minutes)

### Step 4: Activate Developer Mode
- [ ] Go to **Settings** (bottom left)
- [ ] Scroll to the very bottom
- [ ] Click "Activate the developer mode"
- [ ] Wait for page reload

### Step 5: Set API Key
- [ ] Still in Settings, find **Technical** menu
- [ ] Click **Parameters → System Parameters**
- [ ] Click **Create** button
- [ ] Fill in:
  - [ ] Key: `mcp.api_key`
  - [ ] Value: (create a strong, unique password)
- [ ] Example: `claro-colombia-2025-ABC123xyz!`
- [ ] Click **Save**
- [ ] **IMPORTANT**: Write down your API key somewhere safe!

**My API Key:** _________________________________
(Write it here and keep this document secure)

### Step 6: Test MCP Server
- [ ] Open a new browser tab
- [ ] Go to: `https://your-odoo-url.com/mcp/health`
- [ ] You should see JSON response with "status": "healthy"
- [ ] If you see this, MCP server is working! ✅

## Phase 3: Initial Setup (30-45 minutes)

### Step 7: Add Business Lines
- [ ] Go to **Claro Distribution → Configuration → Business Lines**
- [ ] Click **Create**
- [ ] Add your first business line:
  - [ ] Name: (e.g., "Postpaid Mobile Plans")
  - [ ] Code: (e.g., "POST")
  - [ ] Description: (optional)
- [ ] Click **Save**
- [ ] Repeat for all your business lines:
  - [ ] Postpaid Mobile
  - [ ] Prepaid Mobile
  - [ ] Internet/Fiber
  - [ ] Cable TV
  - [ ] Business Solutions
  - [ ] (Add others as needed)

**My Business Lines:**
1. _________________ (Code: ______)
2. _________________ (Code: ______)
3. _________________ (Code: ______)
4. _________________ (Code: ______)
5. _________________ (Code: ______)

### Step 8: Add Contact Centers
- [ ] Go to **Claro Distribution → Configuration → Contact Centers**
- [ ] Click **Create**
- [ ] Add your first center:
  - [ ] Name: (e.g., "Bogotá Main Office")
  - [ ] City: (select from dropdown)
  - [ ] Address: (full address)
  - [ ] Employee Count: (number)
  - [ ] Monthly Rent: (amount in COP)
  - [ ] Monthly Utilities: (amount in COP)
- [ ] Click **Save**
- [ ] Repeat for all your offices

**My Contact Centers:**
1. _________________ (City: _______) (Employees: _____)
2. _________________ (City: _______) (Employees: _____)
3. _________________ (City: _______) (Employees: _____)

### Step 9: Add Sample Data (for testing)
- [ ] Go to **Claro Distribution → Business Lines**
- [ ] Open any business line
- [ ] Click on **Sales Records** tab
- [ ] Click **Add a line**
- [ ] Fill in:
  - [ ] Date: (today's date)
  - [ ] Contact Center: (select one)
  - [ ] Amount: (e.g., 500000)
  - [ ] Customer Name: "Test Customer"
- [ ] Click **Save**
- [ ] Add 5-10 more sample sales with different:
  - [ ] Dates (spread over last 2 months)
  - [ ] Business lines
  - [ ] Contact centers
  - [ ] Amounts

**Sample Sales Added:** _____ / 10

### Step 10: Add Sample Costs
- [ ] Go to **Configuration → Contact Centers**
- [ ] Open any center
- [ ] Click on **Cost Records** tab
- [ ] Click **Add a line**
- [ ] Fill in:
  - [ ] Date: (this month)
  - [ ] Name: "Marketing Campaign"
  - [ ] Cost Type: Marketing
  - [ ] Amount: (e.g., 2000000)
- [ ] Click **Save**
- [ ] Add 3-5 more sample costs

**Sample Costs Added:** _____ / 5

## Phase 4: Testing (15 minutes)

### Step 11: Test with Python Script (Optional)
If you know how to run Python:
- [ ] Save the test_mcp_server.py file
- [ ] Edit the file:
  - [ ] Update BASE_URL with your Odoo URL
  - [ ] Update API_KEY with your actual key
- [ ] Run: `python test_mcp_server.py`
- [ ] All tests should pass ✅

### Step 12: Test with Claude (The Fun Part!)
- [ ] Ask Claude: "Can you check if my MCP server is healthy at [your-url]/mcp/health?"
- [ ] If health check works, ask:
  - [ ] "What business lines do I have?"
  - [ ] "Show me my contact centers"
  - [ ] "What were sales by business line last month?"
  - [ ] "Compare performance across my centers"

**Claude Test Results:**
- [ ] Health check works
- [ ] Can list business lines
- [ ] Can list contact centers
- [ ] Can analyze sales
- [ ] Can compare performance

## Phase 5: Going Live (Ongoing)

### Step 13: Train Your Team
- [ ] Create user accounts for team members
- [ ] Show them how to:
  - [ ] Log into Odoo
  - [ ] Navigate to Claro Distribution
  - [ ] Enter sales records
  - [ ] Add cost records
- [ ] Set up data entry schedule (daily? weekly?)

### Step 14: Import Historical Data (Optional)
If you have existing data:
- [ ] Prepare data in Excel/CSV format
- [ ] Ensure correct column headers
- [ ] Use Odoo's Import feature:
  - [ ] Go to any list view
  - [ ] Click Favorites → Import records
  - [ ] Upload your file
  - [ ] Map columns
  - [ ] Import

**Data Imported:**
- [ ] Historical sales (___ records)
- [ ] Historical costs (___ records)

### Step 15: Regular Usage
- [ ] Set up daily data entry routine
- [ ] Review reports weekly
- [ ] Use Claude for monthly insights
- [ ] Adjust as needed

## Troubleshooting Checklist

If something doesn't work:

### Module Won't Install
- [ ] Checked if module folder is in correct location
- [ ] Ran "Update Apps List"
- [ ] Checked Odoo logs for errors
- [ ] Restarted Odoo service
- [ ] Verified all files are present

### Can't See Menu
- [ ] Logged in as administrator
- [ ] Module shows as "Installed" in Apps
- [ ] Refreshed browser
- [ ] Cleared browser cache

### MCP Health Check Fails
- [ ] Verified module is installed
- [ ] Checked URL is correct
- [ ] Odoo service is running
- [ ] No firewall blocking request

### API Key Not Working
- [ ] Checked spelling: `mcp.api_key`
- [ ] No extra spaces in key value
- [ ] Saved the system parameter
- [ ] Using correct key in requests

### No Data Showing
- [ ] Added business lines first
- [ ] Added contact centers
- [ ] Added some sales records
- [ ] Added some cost records
- [ ] Checked date filters

## Success Criteria ✅

You're done when:
- [ ] Module is installed and visible in Odoo
- [ ] API key is set and working
- [ ] At least 2 business lines created
- [ ] At least 1 contact center created
- [ ] At least 10 sample sales entered
- [ ] At least 5 sample costs entered
- [ ] /mcp/health returns "healthy"
- [ ] Claude can answer questions about your data
- [ ] Team knows how to enter data
- [ ] You've made at least one data-driven decision using the system

## Next Steps After Installation

- [ ] Read COMPLETE_SUMMARY.md for full understanding
- [ ] Review API_REFERENCE.md for technical details
- [ ] Check ARCHITECTURE.md to understand how it works
- [ ] Start entering real business data
- [ ] Schedule weekly reviews using Claude
- [ ] Customize as needed for your workflows

## Support Contacts

**For Odoo Issues:**
- Your IT administrator: ___________________
- Odoo support: https://support.odoo.com

**For MCP/Claude Issues:**
- Ask me (Claude) for help!
- MCP Documentation: https://docs.anthropic.com

**For This Module:**
- Check the included documentation
- Review code comments
- Ask Claude for explanations

---

## Installation Notes

Use this space to track any issues, solutions, or customizations:

_______________________________________________________________

_______________________________________________________________

_______________________________________________________________

_______________________________________________________________

_______________________________________________________________

## Completion

Installation completed on: ___________________

Installed by: ___________________

Team trained on: ___________________

Ready for production: ☐ Yes  ☐ No (why: _____________)

---

**Congratulations on completing the installation!** 🎉

Remember:
- Keep your API key secure
- Back up your data regularly  
- Enter data consistently
- Use Claude for insights
- Iterate and improve

You now have a powerful tool for managing your Claro distribution business with AI-powered analytics!
