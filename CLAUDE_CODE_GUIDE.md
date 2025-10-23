# Setting Up Your Project with Claude Code

## Initial Project Setup

### 1. Create Your Project Directory

```bash
# Create main project folder
mkdir claro-mcp-server
cd claro-mcp-server

# Initialize Git
git init

# Create basic structure
mkdir docs
mkdir tests
```

### 2. Copy Your Files

Copy these files from your downloads into the project:

```
claro-mcp-server/
├── standalone_mcp_server.py
├── requirements.txt
├── .env.example
├── Procfile
├── .gitignore
├── README.md  (rename README_STANDALONE.md to this)
├── docs/
│   ├── ODOO_CLOUD_GUIDE.md
│   ├── ARCHITECTURE.md
│   └── COMPLETE_SUMMARY.md
└── tests/
    └── test_mcp_server.py
```

### 3. Create README.md

```bash
# Rename the standalone README
cp README_STANDALONE.md README.md
```

### 4. Initial Commit (Before Using Claude Code)

```bash
# Check what will be committed
git status

# Add all files
git add .

# First commit
git commit -m "Initial commit: Claro MCP Server for Odoo Cloud

- Add standalone MCP server implementation
- Include Odoo API integration via OdooRPC
- Add deployment files (Procfile, requirements.txt)
- Include comprehensive documentation
- Add .gitignore to protect sensitive data"
```

### 5. Create GitHub Repository

**Option A: Via GitHub Web Interface**
1. Go to https://github.com/new
2. Repository name: `claro-mcp-server`
3. Description: "MCP Server for Claro Distribution - Connects to Odoo Cloud"
4. Choose Private (recommended) or Public
5. DON'T initialize with README (you already have one)
6. Create repository

**Option B: Via GitHub CLI**
```bash
# Install GitHub CLI if you don't have it
# Mac: brew install gh
# Windows: winget install GitHub.cli
# Linux: See https://github.com/cli/cli#installation

# Login
gh auth login

# Create repository
gh repo create claro-mcp-server --private --source=. --remote=origin --push
```

**Manual Connection (if using web interface):**
```bash
# Add remote
git remote add origin https://github.com/YOUR-USERNAME/claro-mcp-server.git

# Push
git branch -M main
git push -u origin main
```

---

## Using Claude Code

### Starting Claude Code

```bash
# Navigate to your project
cd claro-mcp-server

# Start Claude Code
claude-code

# Or with npx (no installation)
npx @anthropic-ai/claude-code
```

### What Claude Code Can Do For You

Claude Code will help you with:
- ✅ Writing clean, documented code
- ✅ Following Python best practices
- ✅ Creating proper Git commits
- ✅ Adding new features
- ✅ Writing tests
- ✅ Debugging issues
- ✅ Refactoring code

---

## Example Conversations with Claude Code

### 1. Initial Code Review

```
You: "Review the standalone_mcp_server.py file and suggest improvements 
for production readiness."

Claude Code will:
- Review your code
- Suggest error handling improvements
- Recommend logging enhancements
- Point out security considerations
- Suggest adding docstrings
```

### 2. Add New Features

```
You: "Add a new MCP tool that analyzes sales by city/region from Odoo data."

Claude Code will:
- Add the new function to the code
- Update the tools list
- Add proper error handling
- Include docstrings
- Test the implementation
- Create a git commit with good message
```

### 3. Improve Error Handling

```
You: "Add better error handling and retry logic for Odoo API connections."

Claude Code will:
- Implement retry mechanism
- Add proper exception handling
- Log errors appropriately
- Update documentation
- Commit changes
```

### 4. Add Tests

```
You: "Create unit tests for all the MCP tools."

Claude Code will:
- Create test files
- Write test cases
- Add mock Odoo responses
- Set up test fixtures
- Run tests to verify
```

### 5. Git Best Practices

```
You: "Help me commit these changes following best practices."

Claude Code will:
- Review your changes
- Create meaningful commit message
- Follow conventional commits format
- Split large changes into logical commits
```

---

## Best Practices for Git Commits (Claude Code Style)

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples:

**Good commit messages:**
```bash
feat(mcp): add sales analysis by region tool

Implement new MCP tool to analyze sales data grouped by geographical
regions. Queries Odoo partner locations and aggregates sales data.

- Add get_sales_by_region function
- Update MCP tools endpoint
- Add region mapping utilities
- Include error handling for missing location data

Closes #12
```

```bash
fix(auth): handle expired Odoo sessions gracefully

Add automatic reconnection when Odoo session expires during long-running
operations. Implements exponential backoff retry logic.

- Add session validation before API calls
- Implement retry decorator with backoff
- Log reconnection attempts
- Update error messages

Fixes #8
```

```bash
docs(readme): add Railway deployment instructions

Expand README with step-by-step Railway deployment guide including
screenshots and troubleshooting section.
```

**Bad commit messages (avoid these):**
```bash
git commit -m "fixed stuff"
git commit -m "updates"
git commit -m "changes"
git commit -m "wip"
```

---

## Typical Workflow with Claude Code

### 1. Start a New Feature

```bash
# Create feature branch
git checkout -b feature/add-city-analysis

# Start Claude Code
claude-code

# In Claude Code:
You: "I want to add a feature to analyze sales by city. The cities are 
Bogotá, Medellín, and Cali. Help me implement this."
```

Claude Code will:
1. Understand the requirement
2. Write the code
3. Add it to the right place
4. Test it works
5. Update documentation
6. Create a good commit

### 2. Review and Commit

```bash
# Review changes
git status
git diff

# If Claude Code hasn't committed yet, you can ask:
You: "Create a proper git commit for these changes following 
conventional commits format."

# Push to GitHub
git push origin feature/add-city-analysis
```

### 3. Create Pull Request

```
You: "Help me create a pull request for this feature with a good 
description and checklist."

Claude Code will generate PR template:
```

### 4. Code Review

```
You: "Review my pull request and suggest any improvements before merging."

Claude Code will:
- Review code quality
- Check for edge cases
- Suggest tests
- Verify documentation
```

---

## Project Structure Best Practices

### Recommended Structure

```
claro-mcp-server/
├── .github/
│   ├── workflows/
│   │   └── tests.yml          # CI/CD pipeline
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/
│   ├── ODOO_CLOUD_GUIDE.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
├── src/
│   ├── __init__.py
│   ├── mcp_server.py          # Main server code
│   ├── odoo_client.py         # Odoo API wrapper
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── sales.py           # Sales analysis tools
│   │   ├── customers.py       # Customer tools
│   │   └── expenses.py        # Expense tools
│   └── utils/
│       ├── __init__.py
│       ├── auth.py            # Authentication utilities
│       └── logger.py          # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── test_mcp_server.py
│   ├── test_odoo_client.py
│   └── test_tools.py
├── .env.example
├── .gitignore
├── Procfile
├── README.md
├── requirements.txt
├── requirements-dev.txt       # Dev dependencies
└── setup.py                   # Package setup
```

**Ask Claude Code to help restructure:**

```
You: "Help me refactor the code into this better structure with separate 
modules for tools and utilities."
```

---

## Advanced Claude Code Usage

### 1. Refactoring

```
You: "Refactor standalone_mcp_server.py to separate concerns:
- Move Odoo connection to odoo_client.py
- Move tools to separate files in tools/
- Add proper logging
- Create configuration management"
```

### 2. Adding Features Incrementally

```
# Feature 1
You: "Add caching for Odoo API responses to improve performance."

# Feature 2
You: "Add rate limiting to prevent API abuse."

# Feature 3
You: "Add health checks for Odoo connection with automatic reconnection."
```

### 3. Documentation

```
You: "Generate comprehensive API documentation from the code including 
all endpoints, parameters, and response formats."
```

### 4. Testing

```
You: "Create integration tests that mock Odoo API responses and verify 
all MCP tools work correctly."
```

### 5. Deployment

```
You: "Help me create a Docker container for this application with 
best practices."

You: "Generate a GitHub Actions workflow for automated testing and 
deployment to Railway."
```

---

## Asking Claude Code for Help

### Good Questions:

✅ "How can I improve error handling in the Odoo connection code?"

✅ "Add logging to track API call performance and errors."

✅ "Refactor the tools to be more modular and testable."

✅ "Create a configuration system using environment variables and config files."

✅ "Add request validation using Pydantic models."

✅ "Help me set up pre-commit hooks for code quality checks."

✅ "Generate comprehensive docstrings for all functions."

✅ "Create a CONTRIBUTING.md guide for other developers."

### Questions that Get Great Results:

✅ **Specific:** "Add retry logic with exponential backoff to the Odoo API client"

✅ **Context:** "The server sometimes loses connection to Odoo after being idle. Add automatic reconnection."

✅ **Complete:** "Create a new MCP tool that gets sales by business line with these requirements: [list requirements]"

---

## Git Workflow Best Practices

### Branch Naming

```
feature/short-description    # New features
fix/issue-description        # Bug fixes  
docs/what-changed           # Documentation
refactor/component-name     # Code refactoring
test/what-testing           # Adding tests
chore/maintenance-task      # Maintenance
```

### Typical Flow

```bash
# 1. Start new feature
git checkout -b feature/add-expense-tracking

# 2. Work with Claude Code
claude-code
# "Help me add expense tracking functionality..."

# 3. Review changes
git status
git diff

# 4. Commit (Claude Code can do this)
git commit -m "feat(tools): add expense tracking analysis

Implement expense tracking tool that analyzes company expenses
by category and time period from Odoo hr.expense module."

# 5. Push
git push origin feature/add-expense-tracking

# 6. Create PR on GitHub
gh pr create --title "Add expense tracking analysis tool" \
  --body "Adds new MCP tool for expense analysis. Closes #15"

# 7. After review and approval, merge
gh pr merge --squash
```

---

## Common Tasks with Claude Code

### Task 1: Code Review

```bash
claude-code

You: "Review my code and create a checklist of improvements needed 
for production readiness."
```

### Task 2: Add Feature

```bash
You: "Add support for filtering sales by date range and business line. 
Include proper validation and error messages."
```

### Task 3: Fix Bug

```bash
You: "The server crashes when Odoo returns an empty result. Add proper 
error handling for this case."
```

### Task 4: Improve Documentation

```bash
You: "Update README.md with:
- Better getting started section
- Environment variables table
- Deployment troubleshooting
- API endpoint examples"
```

### Task 5: Add Tests

```bash
You: "Create pytest tests for all MCP tools with mocked Odoo responses."
```

### Task 6: Prepare for Production

```bash
You: "Add production-ready features:
- Structured logging with levels
- Request ID tracking
- Performance monitoring
- Health check endpoint with detailed status
- Graceful shutdown handling"
```

---

## Tips for Working with Claude Code

### 1. Be Specific
❌ "Make the code better"
✅ "Add input validation for date parameters using Python datetime"

### 2. Provide Context
❌ "Fix the bug"
✅ "The Odoo connection fails after 1 hour of inactivity. Add keep-alive 
or reconnection logic"

### 3. Ask for Explanations
✅ "Explain why you chose this approach for error handling"

### 4. Request Best Practices
✅ "Show me the industry best practices for structuring a Flask API"

### 5. Iterate
✅ Start simple, then enhance:
   - "First, create basic functionality"
   - "Now add error handling"
   - "Now add logging"
   - "Now add tests"

---

## GitHub Best Practices

### 1. Repository Setup

Create these files (Claude Code can help):

```
claro-mcp-server/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── tests.yml
│       └── deploy.yml
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── SECURITY.md
```

**Ask Claude Code:**
```
You: "Create GitHub issue and PR templates following best practices."
```

### 2. Protect Main Branch

On GitHub:
1. Settings → Branches
2. Add branch protection rule for `main`
3. Enable:
   - Require pull request reviews
   - Require status checks (tests)
   - Require branches up to date

### 3. Use GitHub Actions

**Ask Claude Code:**
```
You: "Create a GitHub Actions workflow that:
- Runs tests on every PR
- Checks code formatting
- Deploys to Railway on merge to main"
```

---

## Example: Complete Feature Development

Let's walk through adding a complete feature:

### Step 1: Plan

```bash
# Create issue on GitHub first
gh issue create --title "Add sales forecasting tool" \
  --body "Implement ML-based sales forecasting using historical data"
```

### Step 2: Branch

```bash
git checkout -b feature/sales-forecasting
```

### Step 3: Develop with Claude Code

```bash
claude-code

You: "I want to add a sales forecasting tool. It should:
1. Analyze historical sales data from Odoo
2. Use simple linear regression to forecast next month
3. Return forecast with confidence interval
4. Handle edge cases (not enough data, missing data)

Let's start with the basic implementation, then add tests."
```

Claude Code will:
1. Create the new tool function
2. Add it to the MCP server
3. Write proper docstrings
4. Add error handling
5. Create tests
6. Update documentation

### Step 4: Review

```bash
git status
git diff
```

### Step 5: Commit

```
You (in Claude Code): "Create a proper commit message for these changes."
```

### Step 6: Push and PR

```bash
git push origin feature/sales-forecasting

gh pr create --title "feat(tools): add sales forecasting with linear regression" \
  --body "Implements sales forecasting tool using historical data.

Features:
- Linear regression model for forecasting
- Confidence intervals
- Handles missing/insufficient data
- Comprehensive tests

Closes #23"
```

### Step 7: Review and Merge

After approval:
```bash
gh pr merge --squash
git checkout main
git pull
```

---

## Maintenance with Claude Code

### Regular Tasks

```
# Weekly
You: "Review code for potential improvements and security issues."

# Before releases
You: "Check all dependencies are up to date and secure."

# After issues
You: "Analyze the bug report and suggest a fix with tests."

# Documentation
You: "Update documentation to reflect recent changes."
```

---

## Summary: Your Complete Workflow

1. **Setup Project** (one time)
   ```bash
   mkdir claro-mcp-server && cd claro-mcp-server
   git init
   # Copy files
   git add .
   git commit -m "Initial commit"
   gh repo create --private
   ```

2. **Daily Development**
   ```bash
   git checkout -b feature/new-feature
   claude-code
   # Work with Claude Code
   git push
   gh pr create
   ```

3. **Code Quality**
   - Claude Code reviews code
   - Suggests improvements
   - Creates tests
   - Updates docs

4. **Deployment**
   - Push to GitHub
   - GitHub Actions run tests
   - Auto-deploy to Railway

---

## Next Steps

1. **Set up your project:**
   ```bash
   mkdir claro-mcp-server
   cd claro-mcp-server
   # Copy your files here
   ```

2. **Install Claude Code:**
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

3. **Initialize Git:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Claro MCP Server"
   ```

4. **Create GitHub repo:**
   ```bash
   gh repo create claro-mcp-server --private --source=. --push
   ```

5. **Start using Claude Code:**
   ```bash
   claude-code
   ```

You're ready to build professionally! 🚀
