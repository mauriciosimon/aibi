"""
Intelligent Chat Backend - Connects Claude API to Odoo MCP Server

This creates a ChatGPT-like experience where Claude can intelligently
query your Odoo data through the MCP server.
"""

import os
import json
import anthropic
import requests
import logging
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import dynamic_tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)
CORS(app)

# Configuration
CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY', 'your-claude-api-key-here')
MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'https://mcp-odoo-production.up.railway.app')
MCP_API_KEY = os.getenv('MCP_API_KEY', 'odoo-mcp-2025')

# Power BI Configuration
POWERBI_CLIENT_ID = os.getenv('POWERBI_CLIENT_ID')
POWERBI_TENANT_ID = os.getenv('POWERBI_TENANT_ID')
POWERBI_CLIENT_SECRET = os.getenv('POWERBI_CLIENT_SECRET')

# Power BI MCP Server URL (for future deployment)
POWERBI_MCP_SERVER_URL = os.getenv('POWERBI_MCP_SERVER_URL', 'http://localhost:5003')

# Anthropic client (initialized on first use)
_client = None

def get_anthropic_client():
    """Get or create Anthropic client"""
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    return _client


def generate_chart_from_mcp_data(user_message, captured_data):
    """
    Generate chart JSON directly from MCP tool data.

    This is more reliable than parsing Claude's HTML output because we work
    with structured data from the tools.

    Args:
        user_message: Original user request
        captured_data: Dict with 'tool_name' and 'result' from MCP call

    Returns:
        Chart JSON string in [CHART:id]{...} format, or None if no chart needed
    """
    import re
    import hashlib

    if not captured_data:
        return None

    tool_name = captured_data.get('tool_name')
    result = captured_data.get('result', {})

    # Detect chart type from user message
    chart_type = "bar"  # default
    if 'pie' in user_message.lower():
        chart_type = "pie"
    elif 'line' in user_message.lower():
        chart_type = "line"
    elif 'doughnut' in user_message.lower():
        chart_type = "doughnut"

    # Extract limit from user message ("top 5", "top 10", etc.)
    limit_match = re.search(r'top\s+(\d+)', user_message.lower())
    limit = int(limit_match.group(1)) if limit_match else 10

    chart_data = None

    # Handle different MCP tools
    if tool_name == "get_purchase_analysis" and result.get('by_vendor'):
        vendors = result['by_vendor'][:limit]

        chart_data = {
            "type": chart_type,
            "title": f"Top {len(vendors)} Vendors by Purchase Spending",
            "data": {
                "labels": [v['vendor'] for v in vendors],
                "datasets": [{
                    "label": "Spending (COP)",
                    "data": [v['total_spent'] for v in vendors],
                    "backgroundColor": [
                        "#667eea", "#764ba2", "#f093fb", "#4facfe", "#00f2fe",
                        "#43e97b", "#fa709a", "#fee140", "#30cfd0", "#a8edea",
                        "#667eea", "#764ba2", "#f093fb", "#4facfe", "#00f2fe"
                    ][:len(vendors)]
                }]
            }
        }

    elif tool_name == "get_top_customers" and result.get('customers'):
        customers = result['customers'][:limit]

        chart_data = {
            "type": chart_type,
            "title": f"Top {len(customers)} Customers by Revenue",
            "data": {
                "labels": [c['name'] for c in customers],
                "datasets": [{
                    "label": "Revenue (COP)",
                    "data": [c['total_revenue'] for c in customers],
                    "backgroundColor": [
                        "#667eea", "#764ba2", "#f093fb", "#4facfe", "#00f2fe",
                        "#43e97b", "#fa709a", "#fee140", "#30cfd0", "#a8edea"
                    ][:len(customers)]
                }]
            }
        }

    elif tool_name == "get_sales_summary" and result.get('by_product'):
        products = result['by_product'][:limit]

        chart_data = {
            "type": chart_type,
            "title": f"Sales by Product",
            "data": {
                "labels": [p['product'] for p in products],
                "datasets": [{
                    "label": "Revenue (COP)",
                    "data": [p['total_revenue'] for p in products],
                    "backgroundColor": [
                        "#667eea", "#764ba2", "#f093fb", "#4facfe", "#00f2fe",
                        "#43e97b", "#fa709a", "#fee140", "#30cfd0", "#a8edea"
                    ][:len(products)]
                }]
            }
        }

    elif tool_name == "get_revenue_by_period" and result.get('periods'):
        periods = result['periods']

        chart_data = {
            "type": "line" if chart_type == "bar" else chart_type,  # Periods work better as line charts
            "title": "Revenue Trends",
            "data": {
                "labels": [p['period'] for p in periods],
                "datasets": [{
                    "label": "Revenue (COP)",
                    "data": [p['revenue'] for p in periods],
                    "backgroundColor": "#667eea",
                    "borderColor": "#667eea",
                    "fill": False
                }]
            }
        }

    if chart_data:
        # Generate unique ID
        chart_id = hashlib.md5(f"{user_message}{tool_name}".encode()).hexdigest()[:8]
        chart_embed = f"[CHART:{chart_id}]{json.dumps(chart_data)}"

        logger.info(f"✅ Generated {chart_type} chart from {tool_name} with {len(chart_data['data']['labels'])} data points")
        return chart_embed

    return None


def get_all_available_tools():
    """Get all tools including dynamic ones from both Odoo and Power BI"""
    # Start with Odoo static tools
    all_tools = list(MCP_TOOLS)

    # Add Power BI static tools
    all_tools.extend(POWERBI_MCP_TOOLS)

    # Fetch dynamic tools from Odoo MCP server
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/tools",
            json={"api_key": MCP_API_KEY},
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                mcp_tools = result.get('data', [])
                # Add tools that aren't already in our static list
                static_tool_names = {t['name'] for t in MCP_TOOLS}
                for tool in mcp_tools:
                    if tool['name'] not in static_tool_names:
                        all_tools.append(tool)
                logger.info(f"Loaded {len(all_tools)} total tools (Odoo: {len(MCP_TOOLS)}, Power BI: {len(POWERBI_MCP_TOOLS)}, Dynamic: {len(mcp_tools) - len(MCP_TOOLS)})")
    except Exception as e:
        logger.warning(f"Could not fetch dynamic tools: {str(e)}")

    return all_tools

# MCP Tools definition for Claude - Comprehensive Business Intelligence
MCP_TOOLS = [
    # Financial & Sales
    {
        "name": "get_top_customers",
        "description": "Get top customers by revenue from Odoo. Returns customer name, total revenue, and invoice count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "number", "description": "Number of top customers to return (default: 10)"}
            }
        }
    },
    {
        "name": "get_sales_summary",
        "description": "Get sales summary by product/service from Odoo for a specific date range. Returns product name, total revenue, and quantity sold.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"}
            },
            "required": ["start_date", "end_date"]
        }
    },
    {
        "name": "get_revenue_by_period",
        "description": "Get revenue breakdown by time period (month, quarter, or year) from Odoo. Returns revenue for each period.",
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {"type": "string", "description": "Time period: 'month', 'quarter', or 'year'", "enum": ["month", "quarter", "year"]},
                "count": {"type": "number", "description": "Number of periods to retrieve (default: 6)"}
            },
            "required": ["period"]
        }
    },
    {
        "name": "get_expense_analysis",
        "description": "Analyze company expenses from Odoo for a specific date range. Returns total expenses, expense count, and breakdown by category or recent bills.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"}
            },
            "required": ["start_date", "end_date"]
        }
    },
    # HR & Workforce
    {
        "name": "get_employee_metrics",
        "description": "Get employee headcount, department distribution, and workforce analytics. Essential for HR KPIs and workforce planning.",
        "input_schema": {
            "type": "object",
            "properties": {
                "group_by": {"type": "string", "description": "Group by: department, job, or contract_type"}
            }
        }
    },
    {
        "name": "get_attendance_analysis",
        "description": "Analyze employee attendance patterns, work hours, and identify trends. Great for workforce management KPIs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
                "employee_id": {"type": "number", "description": "Optional: specific employee ID"}
            }
        }
    },
    {
        "name": "get_timesheet_summary",
        "description": "Get timesheet data by project, employee, or task. Shows how time is being spent across the organization.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
                "group_by": {"type": "string", "description": "Group by: employee, project, or task"}
            }
        }
    },
    {
        "name": "get_recruitment_pipeline",
        "description": "Get recruitment metrics: open positions, applicant counts, hiring funnel by stage. Track hiring performance.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"}
            }
        }
    },
    # CRM & Sales Pipeline
    {
        "name": "get_crm_pipeline",
        "description": "Get CRM pipeline: leads, opportunities, conversion rates by stage. Shows sales funnel health and forecast.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"}
            }
        }
    },
    {
        "name": "get_sales_team_performance",
        "description": "Analyze sales team performance: quotas, achievements, win rates by team and rep. Sales performance KPIs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
                "team_id": {"type": "number", "description": "Optional: specific team ID"}
            }
        }
    },
    # Operations & Inventory
    {
        "name": "get_inventory_status",
        "description": "Get inventory levels, stock movements, and warehouse analytics. Identify low stock and inventory health.",
        "input_schema": {
            "type": "object",
            "properties": {
                "warehouse_id": {"type": "number", "description": "Optional: specific warehouse ID"},
                "low_stock_threshold": {"type": "number", "description": "Alert threshold for low stock items"}
            }
        }
    },
    {
        "name": "get_purchase_analysis",
        "description": "Analyze purchase orders: spending by vendor, delivery performance, procurement KPIs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"}
            }
        }
    },
    # Project Management
    {
        "name": "get_project_status",
        "description": "Get project status: progress, task completion rates, resource allocation. Project management KPIs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {"type": "number", "description": "Optional: specific project ID"},
                "include_archived": {"type": "boolean", "description": "Include archived projects"}
            }
        }
    },
    # Comprehensive KPIs
    {
        "name": "get_business_kpis",
        "description": "Get comprehensive business KPIs: revenue, profit margins, employee productivity, customer metrics, trends. Executive dashboard.",
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {"type": "string", "description": "month, quarter, or year"},
                "include_trends": {"type": "boolean", "description": "Include period-over-period growth trends"}
            }
        }
    }
]

# Power BI MCP Tools - Business Intelligence Data Warehouse
POWERBI_MCP_TOOLS = [
    {
        "name": "powerbi_list_workspaces",
        "description": "List all Power BI workspaces (data lakes) available. Use this to discover what data sources exist in Power BI.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "powerbi_list_datasets",
        "description": "List all datasets in a Power BI workspace. Datasets contain the actual business data models and tables.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string", "description": "The workspace/group ID to query"}
            },
            "required": ["workspace_id"]
        }
    },
    {
        "name": "powerbi_get_dataset_schema",
        "description": "Get the schema (tables, columns, measures) of a Power BI dataset. Essential for understanding what data is available before querying.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string", "description": "The workspace/group ID"},
                "dataset_id": {"type": "string", "description": "The dataset ID to inspect"}
            },
            "required": ["workspace_id", "dataset_id"]
        }
    },
    {
        "name": "powerbi_execute_dax",
        "description": "Execute a DAX query against a Power BI dataset to retrieve data. Use this to get actual business data from Power BI data warehouse.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string", "description": "The workspace/group ID"},
                "dataset_id": {"type": "string", "description": "The dataset ID to query"},
                "dax_query": {"type": "string", "description": "The DAX query to execute (e.g., EVALUATE 'SalesTable')"}
            },
            "required": ["workspace_id", "dataset_id", "dax_query"]
        }
    }
]


def call_mcp_tool(tool_name, arguments):
    """Call the appropriate MCP server to execute a tool"""
    try:
        # Route to Power BI MCP server for Power BI tools
        if tool_name.startswith('powerbi_'):
            # Map tool name from our naming convention to Power BI MCP server convention
            powerbi_tool_map = {
                'powerbi_list_workspaces': 'list_workspaces',
                'powerbi_list_datasets': 'list_datasets',
                'powerbi_get_dataset_schema': 'get_dataset_schema',
                'powerbi_execute_dax': 'execute_dax_query'
            }

            actual_tool_name = powerbi_tool_map.get(tool_name, tool_name)

            # For now, call Power BI MCP HTTP server when it's deployed
            # TODO: Update this URL when Power BI MCP is deployed to Railway
            response = requests.post(
                f"{POWERBI_MCP_SERVER_URL}/mcp/tool/call",
                json={
                    "api_key": MCP_API_KEY,
                    "name": actual_tool_name,
                    "arguments": arguments
                },
                timeout=30
            )
        else:
            # Route to Odoo MCP server for Odoo tools
            response = requests.post(
                f"{MCP_SERVER_URL}/mcp/tool/call",
                json={
                    "api_key": MCP_API_KEY,
                    "name": tool_name,
                    "arguments": arguments
                },
                timeout=30
            )

        response.raise_for_status()
        result = response.json()

        if result.get('success'):
            return result.get('data')
        else:
            return {"error": result.get('error', 'Unknown error')}
    except Exception as e:
        logger.error(f"Error calling MCP tool '{tool_name}': {str(e)}")
        return {"error": str(e)}


def process_tool_calls(tool_calls):
    """Process Claude's tool use requests and capture chart-worthy data"""
    tool_results = []
    captured_data = None  # Store data that could be charted

    for tool_use in tool_calls:
        if tool_use.type == "tool_use":
            tool_name = tool_use.name
            tool_input = tool_use.input

            # Call MCP server
            result = call_mcp_tool(tool_name, tool_input)

            # Capture chart-worthy data from specific tools
            chart_worthy_tools = ['get_purchase_analysis', 'get_top_customers', 'get_sales_summary', 'get_revenue_by_period']
            if tool_name in chart_worthy_tools and result:
                captured_data = {
                    'tool_name': tool_name,
                    'result': result
                }
                logger.info(f"📊 Captured chart-worthy data from {tool_name}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": json.dumps(result)
            })

    return tool_results, captured_data


@app.route('/')
def index():
    """Serve the chat interface"""
    return send_from_directory('.', 'intelligent_chat_interface.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Intelligent Chat Backend',
        'mcp_server': MCP_SERVER_URL
    })


@app.route('/develop', methods=['POST'])
def develop():
    """Development endpoint - Generate new tools dynamically using Claude Code"""
    try:
        logger.info("=== DEVELOP REQUEST RECEIVED ===")

        data = request.get_json()
        admin_password = data.get('admin_password', '')
        development_request = data.get('request', '')

        # Simple password protection
        ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'onecontact2025')
        if admin_password != ADMIN_PASSWORD:
            return jsonify({
                'success': False,
                'error': 'Invalid admin password'
            }), 401

        if not development_request:
            return jsonify({'error': 'No development request provided'}), 400

        logger.info(f"Development request: {development_request}")

        # Use Claude Sonnet to generate code
        client = get_anthropic_client()

        code_generation_prompt = f"""You are an expert Python developer creating MCP tools for Odoo integration.

User Request: {development_request}

Generate a complete, working tool with:
1. Tool definition (JSON format with name, description, input_schema)
2. Python function implementation

The function signature should be: `def tool_name(odoo, args):`

Available Odoo models you can use:
- odoo.env['hr.employee'] - Employees
- odoo.env['res.partner'] - Partners/Customers
- odoo.env['sale.order'] - Sales Orders
- odoo.env['account.move'] - Invoices/Bills
- odoo.env['purchase.order'] - Purchase Orders
- odoo.env['project.project'] - Projects
- odoo.env['crm.lead'] - CRM Leads/Opportunities
- odoo.env['stock.quant'] - Inventory
- And any other standard Odoo model

Return ONLY valid JSON in this exact format:
{{
  "tool_definition": {{
    "name": "tool_name_in_snake_case",
    "description": "Clear description of what the tool does",
    "input_schema": {{
      "type": "object",
      "properties": {{
        "param1": {{"type": "string", "description": "Parameter description"}},
        "param2": {{"type": "string", "description": "Parameter description"}}
      }},
      "required": ["param1"]
    }}
  }},
  "function_code": "def tool_name(odoo, args):\\n    # Implementation\\n    return result"
}}

IMPORTANT:
- Use proper error handling with try/except
- Return data in JSON-serializable format
- Include helpful comments
- Use .search_read() for queries
- Return dictionaries or lists, never Odoo objects directly"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            messages=[{
                "role": "user",
                "content": code_generation_prompt
            }]
        )

        # Extract the generated code
        generated_text = ""
        for block in response.content:
            if block.type == "text":
                generated_text += block.text

        logger.info(f"Generated code: {generated_text[:500]}...")

        # Parse JSON response
        try:
            # Try to find JSON in the response
            json_start = generated_text.find('{')
            json_end = generated_text.rfind('}') + 1
            json_str = generated_text[json_start:json_end]

            code_data = json.loads(json_str)
            tool_definition = code_data['tool_definition']
            function_code = code_data['function_code']

        except Exception as e:
            logger.error(f"Failed to parse generated code: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Failed to parse generated code: {str(e)}',
                'raw_output': generated_text
            }), 500

        # Register the tool on MCP server
        tool_name = tool_definition['name']

        try:
            # Send tool to MCP server for registration
            mcp_response = requests.post(
                f"{MCP_SERVER_URL}/mcp/register-tool",
                json={
                    "api_key": MCP_API_KEY,
                    "tool_definition": tool_definition,
                    "function_code": function_code
                },
                timeout=30
            )

            if mcp_response.status_code == 200:
                logger.info(f"✅ Tool '{tool_name}' registered on MCP server successfully!")
            else:
                logger.warning(f"⚠️ MCP server registration failed (non-critical): {mcp_response.text}")

        except Exception as e:
            logger.warning(f"⚠️ Error registering tool on MCP server (non-critical): {str(e)}")

        logger.info(f"✅ Tool '{tool_name}' created successfully!")

        return jsonify({
            'success': True,
            'tool_name': tool_name,
            'tool_definition': tool_definition,
            'function_code': function_code,
            'message': f"Tool '{tool_name}' has been created and is now available!"
        })

    except Exception as e:
        logger.error(f"=== DEVELOP REQUEST FAILED ===")
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint that uses Claude API with MCP tools"""
    try:
        logger.info("=== CHAT REQUEST RECEIVED ===")

        data = request.get_json()
        logger.info(f"Request data: {data}")

        user_message = data.get('message', '')
        conversation_history = data.get('history', [])

        logger.info(f"User message: {user_message}")
        logger.info(f"History length: {len(conversation_history)}")

        if not user_message:
            logger.warning("No message provided")
            return jsonify({'error': 'No message provided'}), 400

        # Build messages for Claude
        messages = conversation_history + [
            {
                "role": "user",
                "content": user_message
            }
        ]

        logger.info(f"Total messages for Claude: {len(messages)}")

        # Get Anthropic client
        logger.info("Getting Anthropic client...")
        client = get_anthropic_client()
        logger.info(f"Client type: {type(client)}")

        # Get all available tools (static + dynamic)
        all_tools = get_all_available_tools()

        # Initial call to Claude with tools
        logger.info("Making initial call to Claude API...")
        logger.info(f"Model: claude-3-haiku-20240307")
        logger.info(f"Tools count: {len(all_tools)}")

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            tools=all_tools,
            messages=messages,
            system="""You are an intelligent multi-source business intelligence assistant with comprehensive access to:

**DATA SOURCES:**
1. **Odoo ERP** - Operational data: sales, purchases, HR, inventory, projects, CRM, invoices
2. **Power BI** - Data warehouse: aggregated analytics, historical trends, complex business models

**YOUR ROLE:**
Act as a senior business analyst who can:
- Access and correlate data from multiple sources
- Provide executive summaries and actionable insights
- Identify trends, anomalies, and opportunities
- Answer complex questions requiring cross-source analysis

**INTELLIGENT SOURCE SELECTION:**
- Use **Odoo tools** (get_*) for: transactional data, real-time operations, detailed records
- Use **Power BI tools** (powerbi_*) for: data warehouse queries, complex analytics, historical trends
- For comprehensive analysis, query BOTH sources and correlate findings

**POWER BI WORKFLOW:**
1. First, use `powerbi_list_workspaces` to discover available data lakes
2. Then use `powerbi_list_datasets` to find relevant datasets
3. Use `powerbi_get_dataset_schema` to understand table structure
4. Finally, use `powerbi_execute_dax` to query data using DAX syntax

**RESPONSE FORMAT:**
1. Use appropriate tools to get data from the right source(s)
2. ALWAYS display actual data in clear, formatted tables
3. Provide analysis with actionable business insights
4. Format currency as "COP $X,XXX,XXX" (Colombian Pesos)
5. Be conversational and proactive

CRITICAL FORMATTING RULES:
- When users ask for a CHART or GRAPH, use ONLY the [CHART:id]{...} syntax (see below)
- For DATA TABLES (not charts), use HTML tables with class="data-table" or class="report-table"
- Show ALL rows of data, not just a summary
- NEVER say "The report shows..." without actually showing the data

**PROFESSIONAL TABLE FORMATTING:**
Use HTML tables with the class "data-table" or "report-table" for all structured data:

<table class="data-table">
<thead>
<tr><th>Department</th><th>Employee Count</th></tr>
</thead>
<tbody>
<tr><td>Operations</td><td>54</td></tr>
<tr><td>HR</td><td>18</td></tr>
<tr><td>Sales</td><td>12</td></tr>
</tbody>
</table>

**CHART INTEGRATION - MANDATORY FOR ALL VISUALIZATIONS:**

🚨 CRITICAL: When users say "create a bar chart", "make a pie chart", "show a graph", etc., you MUST respond with ONLY the [CHART:id]{...} syntax below.
🚫 DO NOT create HTML ```html code blocks - they will NOT render as charts!
🚫 DO NOT create standalone HTML files - the system cannot use them!
✅ ONLY use: [CHART:id]{...json...}

Chart syntax (this is the ONLY way to create visual charts):
[CHART:uniqueId]{"type":"bar","title":"Chart Title","data":{"labels":["Label1","Label2"],"datasets":[{"label":"Dataset","data":[10,20],"backgroundColor":["#667eea","#764ba2"]}]}}

Available chart types: "bar", "line", "pie", "doughnut"

REAL EXAMPLE - Purchase spending bar chart (copy this pattern):
[CHART:purchases123]{"type":"bar","title":"Top Vendors by Purchase Spending - September 2025","data":{"labels":["DIAN","ONE CONTACT","JVP PERALTA","JACKTEK","Nomina Portabilidad"],"datasets":[{"label":"Spending (Millions COP)","data":[915.2,346.0,188.3,160.7,155.7],"backgroundColor":["#667eea","#764ba2","#f093fb","#4facfe","#00f2fe"]}]}}

When user asks "create a bar chart of purchases", your ENTIRE response should be:
[CHART:purchases456]{...the JSON data...}

That's it! Just the chart syntax. The interface will render it beautifully.

**METRIC CARDS:**
For key metrics, use metric cards:
<div class="metric-card">
<div class="metric-value">1,169</div>
<div class="metric-label">Total Employees</div>
</div>

**INSIGHTS:**
- Operations is the largest department
- Consider rebalancing resources

Available business intelligence across:

**Financial & Sales:**
- Customer revenue analysis
- Sales by product/service
- Revenue trends over time
- Expense analysis and vendor spending

**HR & Workforce:**
- Employee headcount and distribution (by department, job title)
- Attendance patterns and work hours
- Timesheet data (by employee, project, or task)
- Recruitment pipeline and hiring metrics

**CRM & Sales Pipeline:**
- Lead and opportunity pipeline
- Sales team performance metrics
- Win rates and conversion analysis

**Operations & Inventory:**
- Inventory levels and stock status
- Purchase order analysis
- Vendor spending patterns

**Project Management:**
- Project status and completion rates
- Task analytics
- Resource allocation

**Executive KPIs:**
- Revenue, growth trends
- Employee productivity metrics
- Customer acquisition and retention
- Cross-functional performance indicators

**CRITICAL DATE HANDLING:**
- ALWAYS calculate explicit dates when users mention relative periods like "last month", "this year", "October 2025"
- Today's date is November 3, 2025
- "Last month" = October 1, 2025 to October 31, 2025
- "This month" = November 1, 2025 to November 3, 2025
- "This year" = January 1, 2025 to November 3, 2025
- When users mention a specific month/year (e.g., "October 2025"), use the full month range
- ALWAYS use YYYY-MM-DD format for dates
- NEVER omit start_date and end_date when they are available as parameters

For HR and workforce questions, intelligently identify patterns and trends."""
        )

        logger.info(f"Initial response received. Stop reason: {response.stop_reason}")

        # Handle tool use
        captured_data = None  # Will store chart-worthy data from tools
        while response.stop_reason == "tool_use":
            logger.info("Processing tool calls...")
            # Process tool calls and capture chart-worthy data
            tool_results, tool_data = process_tool_calls(response.content)
            if tool_data:
                captured_data = tool_data  # Store for later chart generation
            logger.info(f"Tool results received")

            # Continue conversation with tool results
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            messages.append({
                "role": "user",
                "content": tool_results
            })

            # Get Claude's response after tool use
            logger.info("Making follow-up call to Claude API...")
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=8192,
                tools=all_tools,
                messages=messages
            )
            logger.info(f"Follow-up response received. Stop reason: {response.stop_reason}")

        # Extract text response
        assistant_message = ""
        for block in response.content:
            if block.type == "text":
                assistant_message += block.text

        # SMART CHART GENERATION: If user requested a chart and we have data, inject chart
        chart_keywords = ['chart', 'graph', 'plot', 'visualiz']
        user_wants_chart = any(keyword in user_message.lower() for keyword in chart_keywords)

        if user_wants_chart and captured_data:
            chart_embed = generate_chart_from_mcp_data(user_message, captured_data)
            if chart_embed:
                # Add chart to message
                assistant_message += "\n\n" + chart_embed
                logger.info("✅ Chart generated and injected into response")

        logger.info(f"Final assistant message length: {len(assistant_message)}")
        logger.info("=== CHAT REQUEST SUCCESSFUL ===")

        return jsonify({
            'success': True,
            'message': assistant_message,
            'usage': {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens
            }
        })

    except anthropic.AuthenticationError as e:
        logger.error(f"Authentication error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Invalid Claude API key. Please set ANTHROPIC_API_KEY environment variable.'
        }), 401
    except Exception as e:
        logger.error(f"=== CHAT REQUEST FAILED ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/powerbi/list', methods=['GET'])
def powerbi_list():
    """
    List available Power BI workspaces and reports
    """
    try:
        # Check if Power BI credentials are configured
        if not all([POWERBI_CLIENT_ID, POWERBI_TENANT_ID, POWERBI_CLIENT_SECRET]):
            return jsonify({
                'success': False,
                'error': 'Power BI credentials not configured. Please set POWERBI_CLIENT_ID, POWERBI_TENANT_ID, and POWERBI_CLIENT_SECRET environment variables.'
            }), 500

        # Get Azure AD access token
        token_url = f'https://login.microsoftonline.com/{POWERBI_TENANT_ID}/oauth2/v2.0/token'
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': POWERBI_CLIENT_ID,
            'client_secret': POWERBI_CLIENT_SECRET,
            'scope': 'https://analysis.windows.net/powerbi/api/.default'
        }

        logger.info("Fetching Power BI workspaces and reports")

        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        access_token = token_response.json().get('access_token')

        if not access_token:
            raise Exception('Failed to get access token from Azure AD')

        # Get workspaces (groups)
        headers = {'Authorization': f'Bearer {access_token}'}
        workspaces_url = 'https://api.powerbi.com/v1.0/myorg/groups'
        workspaces_response = requests.get(workspaces_url, headers=headers)
        workspaces_response.raise_for_status()
        workspaces = workspaces_response.json().get('value', [])

        # Get reports for each workspace
        all_reports = []
        for workspace in workspaces:
            workspace_id = workspace['id']
            workspace_name = workspace['name']

            reports_url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports'
            reports_response = requests.get(reports_url, headers=headers)

            if reports_response.status_code == 200:
                reports = reports_response.json().get('value', [])
                for report in reports:
                    all_reports.append({
                        'report_id': report['id'],
                        'report_name': report['name'],
                        'workspace_id': workspace_id,
                        'workspace_name': workspace_name,
                        'web_url': report.get('webUrl', '')
                    })

        logger.info(f"Found {len(all_reports)} reports across {len(workspaces)} workspaces")

        return jsonify({
            'success': True,
            'workspaces': workspaces,
            'reports': all_reports
        })

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error listing Power BI reports: {str(e)}")
        logger.error(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
        return jsonify({
            'success': False,
            'error': f'Failed to list Power BI reports: {str(e)}'
        }), 500
    except Exception as e:
        logger.error(f"Error listing Power BI reports: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/powerbi/token', methods=['POST'])
def powerbi_token():
    """
    Get Power BI embed token for a report
    """
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        workspace_id = data.get('workspace_id')

        if not report_id or not workspace_id:
            return jsonify({
                'success': False,
                'error': 'Missing report_id or workspace_id'
            }), 400

        # Check if Power BI credentials are configured
        if not all([POWERBI_CLIENT_ID, POWERBI_TENANT_ID, POWERBI_CLIENT_SECRET]):
            return jsonify({
                'success': False,
                'error': 'Power BI credentials not configured. Please set POWERBI_CLIENT_ID, POWERBI_TENANT_ID, and POWERBI_CLIENT_SECRET environment variables.'
            }), 500

        # Get Azure AD access token
        token_url = f'https://login.microsoftonline.com/{POWERBI_TENANT_ID}/oauth2/v2.0/token'
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': POWERBI_CLIENT_ID,
            'client_secret': POWERBI_CLIENT_SECRET,
            'scope': 'https://analysis.windows.net/powerbi/api/.default'
        }

        logger.info(f"Requesting Power BI token for report {report_id} in workspace {workspace_id}")

        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        access_token = token_response.json().get('access_token')

        if not access_token:
            raise Exception('Failed to get access token from Azure AD')

        logger.info(f"Successfully obtained Power BI access token")

        return jsonify({
            'success': True,
            'access_token': access_token
        })

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error getting Power BI token: {str(e)}")
        logger.error(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
        return jsonify({
            'success': False,
            'error': f'Failed to authenticate with Power BI: {str(e)}'
        }), 500
    except Exception as e:
        logger.error(f"Error getting Power BI token: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Intelligent Chat Backend - Claude + Odoo MCP")
    logger.info("=" * 60)
    logger.info(f"MCP Server: {MCP_SERVER_URL}")
    logger.info(f"MCP API Key: {'Set' if MCP_API_KEY != 'odoo-mcp-2025' else 'NOT SET'}")
    logger.info(f"Claude API Key: {'Set' if CLAUDE_API_KEY != 'your-claude-api-key-here' else 'NOT SET'}")
    logger.info(f"Claude API Key (first 20 chars): {CLAUDE_API_KEY[:20]}...")
    logger.info("\nStarting server on http://localhost:5001")
    logger.info("=" * 60)

    app.run(host='0.0.0.0', port=5001, debug=True)
