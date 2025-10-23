# Claude Code Quick Reference Card

## 🚀 Getting Started

```bash
# Install
npm install -g @anthropic-ai/claude-code

# Start in project
cd your-project
claude-code

# Or use without installing
npx @anthropic-ai/claude-code
```

---

## 💬 Common Commands & Questions

### Code Review
```
"Review my code and suggest improvements"
"Check this file for security issues"
"Find potential bugs in this function"
```

### Adding Features
```
"Add a new function that does X"
"Implement feature Y with proper error handling"
"Create a new endpoint for Z"
```

### Refactoring
```
"Refactor this file to be more modular"
"Split this large function into smaller ones"
"Improve the structure of this code"
```

### Testing
```
"Create unit tests for this module"
"Add integration tests for the API"
"Generate test cases for edge scenarios"
```

### Documentation
```
"Add docstrings to all functions"
"Update the README with deployment instructions"
"Create API documentation"
```

### Git & Commits
```
"Create a proper commit message for these changes"
"Help me create a pull request"
"Review my commit history and suggest improvements"
```

### Debugging
```
"This code is throwing error X, help me fix it"
"Why isn't this function working as expected?"
"Debug the connection issue with Odoo"
```

### Best Practices
```
"Show me Python best practices for this code"
"Add proper logging to this module"
"Implement error handling following best practices"
```

---

## 🔄 Git Workflow Cheat Sheet

### Branch Management
```bash
# Create feature branch
git checkout -b feature/description

# Create fix branch
git checkout -b fix/issue-description

# Switch branches
git checkout branch-name

# List branches
git branch -a
```

### Committing
```bash
# Check status
git status

# See changes
git diff

# Stage files
git add .
git add filename

# Commit
git commit -m "type(scope): message"

# Amend last commit
git commit --amend
```

### Pushing & PRs
```bash
# Push branch
git push origin branch-name

# Create PR (GitHub CLI)
gh pr create --title "Title" --body "Description"

# Merge PR
gh pr merge --squash
```

---

## 📝 Commit Message Format

```
<type>(<scope>): <short description>

<longer description if needed>

<footer: issues, breaking changes>
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

### Examples:
```
feat(mcp): add sales forecasting tool
fix(auth): handle expired Odoo sessions
docs(readme): update deployment instructions
refactor(tools): split tools into separate modules
test(mcp): add integration tests
```

---

## 🎯 Project Setup Commands

```bash
# Create project
mkdir project-name && cd project-name

# Initialize Git
git init

# Create .gitignore
echo -e ".env\n__pycache__/\n*.pyc" > .gitignore

# First commit
git add .
git commit -m "Initial commit"

# Create GitHub repo
gh repo create project-name --private --source=. --push

# Create branch protection
gh repo edit --enable-require-pr-reviews
```

---

## 🧪 Python Development

```bash
# Create virtual environment
python -m venv venv

# Activate (Mac/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Freeze dependencies
pip freeze > requirements.txt

# Run tests
pytest

# Run with coverage
pytest --cov=src

# Format code
black .

# Lint code
flake8 src/
```

---

## 🚀 Deployment

### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway init

# Deploy
railway up

# View logs
railway logs
```

### Heroku
```bash
# Login
heroku login

# Create app
heroku create app-name

# Set config
heroku config:set KEY=value

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

## 🔍 Debugging Tips

### Check Odoo Connection
```python
import odoorpc
odoo = odoorpc.ODOO('host', port=443)
odoo.login('db', 'user', 'pass')
print("Connected!")
```

### Test API Locally
```bash
# Start server
python standalone_mcp_server.py

# Test health
curl http://localhost:5000/mcp/health

# Test with auth
curl -X POST http://localhost:5000/mcp/resources \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-key"}'
```

### Check Logs
```bash
# Railway
railway logs

# Heroku
heroku logs --tail

# Local Python
tail -f app.log
```

---

## 📚 Useful Claude Code Prompts

### For This Project

```
"Review the standalone_mcp_server.py and suggest production improvements"

"Add rate limiting to prevent API abuse"

"Create a caching layer for Odoo API responses"

"Add comprehensive error handling with proper logging"

"Restructure the code into separate modules (server, client, tools)"

"Create integration tests that mock Odoo responses"

"Add a new tool for analyzing customer retention"

"Generate OpenAPI/Swagger documentation"

"Add health checks for all dependencies"

"Implement graceful shutdown handling"

"Add request ID tracking for debugging"

"Create a deployment checklist"

"Add monitoring and alerting capabilities"

"Implement automatic retries for failed Odoo requests"

"Add support for multiple Odoo instances"
```

### General Development

```
"Explain this code in simple terms"

"What are the security issues in this code?"

"How can I make this code more efficient?"

"What edge cases am I missing?"

"Create a comprehensive README for this project"

"Set up pre-commit hooks for code quality"

"Add type hints to all functions"

"Create a Docker container for this app"

"Set up CI/CD with GitHub Actions"

"Add telemetry and monitoring"
```

---

## 🎓 Quick Tips

### Working with Claude Code

✅ **Be specific:** "Add retry logic with exponential backoff"
❌ **Too vague:** "Make it better"

✅ **Provide context:** "The Odoo connection times out after 1 hour idle"
❌ **No context:** "Fix the connection"

✅ **Break it down:** Work on one feature at a time
❌ **Too much:** "Add 10 features at once"

✅ **Ask for explanations:** "Why did you choose this approach?"
✅ **Request alternatives:** "Show me another way to do this"

### Git Best Practices

✅ Commit often with clear messages
✅ One feature per branch
✅ Keep commits focused and atomic
✅ Write descriptive PR descriptions
✅ Review code before committing

❌ Don't commit secrets (.env files)
❌ Don't commit large binary files
❌ Don't have huge commits with many changes
❌ Don't use vague commit messages

---

## 🆘 Emergency Commands

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Discard all local changes
git reset --hard origin/main

# Recover deleted file
git checkout HEAD -- filename

# See who changed what
git blame filename

# Search commit history
git log --grep="search term"

# Create backup branch
git branch backup-branch-name
```

---

## 📞 Getting Help

### In Claude Code
```
"I'm stuck on X, can you help?"
"Explain how this works"
"What's the best way to do Y?"
"Review my approach to this problem"
```

### Resources
- Claude Code Docs: https://docs.claude.com/claude-code
- Python Docs: https://docs.python.org
- Flask Docs: https://flask.palletsprojects.com
- Git Docs: https://git-scm.com/doc
- GitHub CLI: https://cli.github.com/manual

---

## ⌨️ Keyboard Shortcuts (Terminal)

```
Ctrl + C    Stop running process
Ctrl + D    Exit/logout
Ctrl + L    Clear screen
Ctrl + R    Search command history
Ctrl + A    Go to line start
Ctrl + E    Go to line end
↑ / ↓       Navigate command history
Tab         Auto-complete
```

---

**Print this page and keep it handy while developing! 📌**
