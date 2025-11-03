"""
Intelligent Chat Backend - Connects Claude API to Odoo MCP Server

This creates a ChatGPT-like experience where Claude can intelligently
query your Odoo data through the MCP server.
"""

import os
import json
import anthropic
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

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

# MCP Tools definition for Claude
MCP_TOOLS = [
    {
        "name": "get_top_customers",
        "description": "Get top customers by revenue from Odoo. Returns customer name, total revenue, and invoice count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "number",
                    "description": "Number of top customers to return (default: 10)"
                }
            }
        }
    },
    {
        "name": "get_sales_summary",
        "description": "Get sales summary by product/service from Odoo for a specific date range. Returns product name, total revenue, and quantity sold.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format"
                }
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
                "period": {
                    "type": "string",
                    "description": "Time period: 'month', 'quarter', or 'year'",
                    "enum": ["month", "quarter", "year"]
                },
                "count": {
                    "type": "number",
                    "description": "Number of periods to retrieve (default: 6)"
                }
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
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format"
                }
            },
            "required": ["start_date", "end_date"]
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


@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint that uses Claude API with MCP tools"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Build messages for Claude
        messages = conversation_history + [
            {
                "role": "user",
                "content": user_message
            }
        ]

        # Get Anthropic client
        client = get_anthropic_client()

        # Initial call to Claude with tools
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            tools=MCP_TOOLS,
            messages=messages,
            system="""You are an intelligent business assistant with access to Odoo ERP data.
You can help users analyze their business data including sales, customers, revenue, and expenses.

When users ask questions:
1. Use the appropriate tools to get data from Odoo
2. Analyze the data and provide clear, actionable insights
3. Format currency in Colombian Pesos (COP) when showing financial data
4. Be conversational and helpful

Available data:
- Customer information and revenue
- Sales by product/service
- Revenue trends over time
- Expense analysis

Always be specific with dates and use YYYY-MM-DD format when calling tools."""
        )

        # Handle tool use
        while response.stop_reason == "tool_use":
            # Process tool calls
            tool_results = process_tool_calls(response.content)

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
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                tools=MCP_TOOLS,
                messages=messages
            )

        # Extract text response
        assistant_message = ""
        for block in response.content:
            if block.type == "text":
                assistant_message += block.text

        return jsonify({
            'success': True,
            'message': assistant_message,
            'usage': {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens
            }
        })

    except anthropic.AuthenticationError:
        return jsonify({
            'success': False,
            'error': 'Invalid Claude API key. Please set ANTHROPIC_API_KEY environment variable.'
        }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Intelligent Chat Backend - Claude + Odoo MCP")
    print("=" * 60)
    print(f"MCP Server: {MCP_SERVER_URL}")
    print(f"Claude API Key: {'Set' if CLAUDE_API_KEY != 'your-claude-api-key-here' else 'NOT SET'}")
    print("\nStarting server on http://localhost:5001")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5001, debug=True)
