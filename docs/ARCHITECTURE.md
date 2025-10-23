# System Architecture Diagram

## Overview: How Everything Connects

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR BUSINESS                            │
│  (Claro Distribution - 3 Cities, Multiple Business Lines)       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Data Entry
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         ODOO SYSTEM                              │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Business   │  │   Contact    │  │    Sales     │          │
│  │    Lines     │  │   Centers    │  │   Records    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────────────────────┐            │
│  │     Cost     │  │     Standard Odoo            │            │
│  │   Records    │  │  (Accounting, CRM, etc.)     │            │
│  └──────────────┘  └──────────────────────────────┘            │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ MCP Server (Our Module)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP API ENDPOINTS                           │
│                                                                   │
│  /mcp/health         - Server status check                      │
│  /mcp/resources      - List available data types                │
│  /mcp/resource/read  - Get specific data                        │
│  /mcp/tools          - List analysis tools                      │
│  /mcp/tool/call      - Run analysis                             │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTPS + API Key
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CLAUDE (AI Assistant)                       │
│                                                                   │
│  "What were our sales last month?"                              │
│  "Which office has highest costs?"                              │
│  "Show me performance trends"                                    │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Natural Language Answers
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                            YOU                                   │
│                   (Business Decision Maker)                      │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Examples

### Example 1: Entering a Sale

```
1. Employee enters sale in Odoo web interface
      │
      ▼
2. Odoo saves to database:
   - Date: 2025-10-21
   - Business Line: "Postpaid Mobile"
   - Center: "Bogotá Office"
   - Amount: 500,000 COP
      │
      ▼
3. Odoo automatically calculates:
   - Updates business line total sales
   - Updates contact center metrics
      │
      ▼
4. Data is now available through MCP server
```

### Example 2: Claude Answering a Question

```
1. You ask Claude: "What were sales in Bogotá last month?"
      │
      ▼
2. Claude calls MCP endpoint:
   POST /mcp/tool/call
   {
     "name": "get_sales_by_business_line",
     "arguments": {
       "start_date": "2025-09-01",
       "end_date": "2025-09-30"
     }
   }
      │
      ▼
3. MCP Server queries Odoo database:
   - Filters sales by date range
   - Filters by Bogotá center
   - Groups by business line
   - Calculates totals
      │
      ▼
4. Returns data to Claude:
   {
     "success": true,
     "data": [
       {"business_line": "Postpaid", "total": 45000000},
       {"business_line": "Internet", "total": 32000000}
     ]
   }
      │
      ▼
5. Claude analyzes and responds:
   "Last month, Bogotá office had total sales of 77M COP:
   - Postpaid Mobile: 45M COP
   - Internet: 32M COP"
```

## Module Components Explained

### Models (Data Structure)

```
┌─────────────────────────────────────────────────────────────┐
│ BUSINESS LINE MODEL                                          │
├─────────────────────────────────────────────────────────────┤
│ Fields:                                                      │
│  - id              (automatic)                               │
│  - name            (e.g., "Postpaid Mobile")                │
│  - code            (e.g., "POST")                           │
│  - description     (text)                                    │
│  - total_sales     (calculated automatically)               │
│  - sales_count     (calculated automatically)               │
│  - sales_records   (link to sales)                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ CONTACT CENTER MODEL                                         │
├─────────────────────────────────────────────────────────────┤
│ Fields:                                                      │
│  - id                    (automatic)                         │
│  - name                  (e.g., "Bogotá Office")            │
│  - city                  (dropdown: Bogotá, Medellín, etc.) │
│  - address               (text)                              │
│  - employee_count        (number)                            │
│  - monthly_rent          (currency - COP)                    │
│  - monthly_utilities     (currency - COP)                    │
│  - total_monthly_cost    (calculated automatically)         │
│  - cost_records          (link to costs)                     │
│  - sales_records         (link to sales)                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ SALES RECORD MODEL                                           │
├─────────────────────────────────────────────────────────────┤
│ Fields:                                                      │
│  - id                    (automatic)                         │
│  - name                  (auto: REF001, REF002, etc.)       │
│  - date                  (date picker)                       │
│  - business_line_id      (link to business line)            │
│  - contact_center_id     (link to contact center)           │
│  - amount                (currency - COP)                    │
│  - customer_name         (text, optional)                    │
│  - notes                 (text, optional)                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ COST RECORD MODEL                                            │
├─────────────────────────────────────────────────────────────┤
│ Fields:                                                      │
│  - id                    (automatic)                         │
│  - name                  (description of cost)              │
│  - date                  (date picker)                       │
│  - contact_center_id     (link to contact center)           │
│  - cost_type             (dropdown: Marketing, Rent, etc.)  │
│  - amount                (currency - COP)                    │
│  - notes                 (text, optional)                    │
└─────────────────────────────────────────────────────────────┘
```

### MCP Tools (What Claude Can Do)

```
┌─────────────────────────────────────────────────────────────┐
│ TOOL 1: get_sales_by_business_line                          │
├─────────────────────────────────────────────────────────────┤
│ Input:  start_date, end_date (optional)                     │
│ Output: Total sales per business line                       │
│ Use:    "What are our top selling services?"               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TOOL 2: get_costs_by_center                                 │
├─────────────────────────────────────────────────────────────┤
│ Input:  center_id (optional), start/end dates               │
│ Output: Cost breakdown by center and type                   │
│ Use:    "Where are we spending the most money?"            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TOOL 3: get_monthly_trends                                  │
├─────────────────────────────────────────────────────────────┤
│ Input:  months (default: 6)                                 │
│ Output: Month-by-month sales, costs, profit                │
│ Use:    "Are we growing?"                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TOOL 4: get_center_performance                              │
├─────────────────────────────────────────────────────────────┤
│ Input:  none                                                 │
│ Output: Comparative metrics for all centers                 │
│ Use:    "Which office is most efficient?"                  │
└─────────────────────────────────────────────────────────────┘
```

## Security Flow

```
┌────────────────────────────────────────────────────────────┐
│ 1. YOU set API key in Odoo                                 │
│    Settings → System Parameters → mcp.api_key              │
└────────────────┬───────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────┐
│ 2. CLAUDE includes API key in every request               │
│    { "api_key": "your-secret-key" }                        │
└────────────────┬───────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────┐
│ 3. MCP SERVER checks if key matches                       │
│    If YES → Process request                                │
│    If NO  → Return "Invalid API key" error                 │
└────────────────┬───────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────┐
│ 4. ODOO checks user permissions                            │
│    (Uses standard Odoo security)                           │
└────────────────┬───────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────┐
│ 5. Data returned only if all checks pass                  │
└────────────────────────────────────────────────────────────┘
```

## File Organization

```
claro_distribution_mcp/
│
├── __init__.py              ← Python says: "This is a module"
│                               Loads models and controllers
│
├── __manifest__.py          ← Odoo says: "Here's module info"
│                               Name, version, dependencies
│
├── models/                  ← "Here's our data structure"
│   ├── __init__.py             Loads all model files
│   ├── business_line.py        Defines business line table
│   ├── contact_center.py       Defines center table
│   └── sales_record.py         Defines sales & cost tables
│
├── views/                   ← "Here's the user interface"
│   ├── business_line_views.xml   Forms and lists for lines
│   ├── contact_center_views.xml  Forms and lists for centers
│   └── menu_views.xml            Menu structure
│
├── security/                ← "Here's who can access what"
│   └── ir.model.access.csv       Access control rules
│
├── controllers/             ← "Here's the MCP server"
│   ├── __init__.py             Loads controller
│   └── mcp_server.py           API endpoints
│
└── Documentation/
    ├── README.md               Full installation guide
    ├── API_REFERENCE.md        Technical API docs
    └── QUICK_START.md          Fast setup guide
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (What you see)                                      │
├─────────────────────────────────────────────────────────────┤
│ - HTML/XML for forms and views                              │
│ - Odoo's web interface                                       │
│ - Your web browser                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ BACKEND (What processes data)                                │
├─────────────────────────────────────────────────────────────┤
│ - Python 3 (programming language)                           │
│ - Odoo Framework (business app platform)                    │
│ - PostgreSQL (database)                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ MCP LAYER (AI integration)                                   │
├─────────────────────────────────────────────────────────────┤
│ - RESTful API (HTTP endpoints)                              │
│ - JSON (data format)                                         │
│ - MCP Protocol (Anthropic standard)                          │
└─────────────────────────────────────────────────────────────┘
```

## Why This Architecture?

**Separation of Concerns:**
- Models handle DATA (what to store)
- Views handle INTERFACE (what to show)
- Controllers handle API (how to share)

**Scalability:**
- Add new business lines? Just add a record
- Add new centers? Just add a record
- Add new analysis tools? Add a function to controller

**Security:**
- Multiple layers of protection
- API key authentication
- Odoo user permissions
- HTTPS encryption

**Flexibility:**
- Use Odoo directly (manual interface)
- Use Claude (AI analysis)
- Use other tools (through API)
- Combine approaches

This architecture makes it easy to:
✅ Understand what each part does
✅ Find and fix problems
✅ Add new features
✅ Scale as your business grows
