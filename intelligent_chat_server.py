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

# Anthropic client (initialized on first use)
_client = None

def get_anthropic_client():
    """Get or create Anthropic client"""
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    return _client


def get_all_available_tools():
    """Get all tools including dynamic ones"""
    all_tools = list(MCP_TOOLS)  # Copy static tools

    # Fetch dynamic tools from MCP server
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
                logger.info(f"Loaded {len(all_tools)} total tools ({len(mcp_tools) - len(MCP_TOOLS)} dynamic)")
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


def call_mcp_tool(tool_name, arguments):
    """Call the MCP server to execute a tool"""
    try:
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
        return {"error": str(e)}


def process_tool_calls(tool_calls):
    """Process Claude's tool use requests"""
    tool_results = []

    for tool_use in tool_calls:
        if tool_use.type == "tool_use":
            tool_name = tool_use.name
            tool_input = tool_use.input

            # Call MCP server
            result = call_mcp_tool(tool_name, tool_input)

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": json.dumps(result)
            })

    return tool_results


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
            system="""You are an intelligent business intelligence assistant with comprehensive access to Odoo ERP data.
You can analyze all aspects of the business: financials, sales, HR, operations, projects, and provide KPI insights.

When users ask questions:
1. Use the appropriate tools to get data from Odoo
2. ALWAYS display the actual data in a clear, formatted way (tables, lists with numbers)
3. After showing the data, provide analysis and actionable insights
4. Format currency as "COP $X,XXX,XXX" (Colombian Pesos with thousand separators)
5. Be conversational and helpful

CRITICAL FORMATTING RULES:
- When you execute a report or query, you MUST show the RAW DATA FIRST
- Use STYLED HTML tables with class="data-table" or class="report-table" for structured data
- Show ALL rows of data, not just a summary
- NEVER say "The report shows..." without actually showing the data
- Format: Show data table → Add charts if helpful → Then provide insights below

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

**CHART INTEGRATION:**
IMPORTANT: When users request charts (bar chart, pie chart, line chart, etc.), you MUST use the chart syntax below, NOT HTML tables or code blocks.

For visual data, you can embed charts using this syntax:
[CHART:uniqueId]{"type":"bar","title":"Chart Title","data":{"labels":["Label1","Label2"],"datasets":[{"label":"Dataset","data":[10,20],"backgroundColor":["#667eea","#764ba2"]}]}}

Available chart types: "bar", "line", "pie", "doughnut"

Example employee distribution chart:
[CHART:emp1]{"type":"bar","title":"Employee Distribution by Department","data":{"labels":["Operations","HR","Sales"],"datasets":[{"label":"Employees","data":[54,18,12],"backgroundColor":["#667eea","#764ba2","#f093fb"]}]}}

Example purchase spending bar chart:
[CHART:purchases1]{"type":"bar","title":"Top Vendors by Purchase Spending","data":{"labels":["Vendor A","Vendor B","Vendor C"],"datasets":[{"label":"Spending (Millions)","data":[915.2,346.0,188.3],"backgroundColor":["#667eea","#764ba2","#f093fb"]}]}}

NEVER use HTML tables or ```html code blocks when users ask for a chart. Always use the [CHART:id]{...} syntax.

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
        while response.stop_reason == "tool_use":
            logger.info("Processing tool calls...")
            # Process tool calls
            tool_results = process_tool_calls(response.content)
            logger.info(f"Tool results: {tool_results}")

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
