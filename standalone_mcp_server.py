"""
Claro Distribution MCP Server - Standalone Version for Odoo Cloud
==================================================================

This is a standalone MCP server that connects to Odoo Cloud via the Odoo API.
No custom modules needed in Odoo - works with standard Odoo Cloud!

Requirements:
- Python 3.8+
- Flask (web framework)
- OdooRPC (to connect to Odoo)
- Access to Odoo Cloud instance

Install dependencies:
    pip install flask odoorpc python-dotenv

Run:
    python standalone_mcp_server.py
"""

import os
import json
import logging
import ssl
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import odoorpc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Configuration
ODOO_HOST = os.getenv('ODOO_HOST', 'yourcompany.odoo.com')
ODOO_PORT = int(os.getenv('ODOO_PORT', '443'))
ODOO_PROTOCOL = os.getenv('ODOO_PROTOCOL', 'jsonrpc+ssl')
ODOO_DATABASE = os.getenv('ODOO_DATABASE', 'yourcompany-main-123456')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin@yourcompany.com')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'your-odoo-password')
MCP_API_KEY = os.getenv('MCP_API_KEY', 'your-mcp-api-key-change-this')

# Global Odoo connection (will be initialized on first request)
odoo_connection = None


def get_odoo_connection():
    """Get or create Odoo connection"""
    global odoo_connection

    if odoo_connection is None:
        try:
            logger.info(f"Connecting to Odoo at {ODOO_HOST}...")
            # Disable SSL verification for Odoo Cloud
            ssl._create_default_https_context = ssl._create_unverified_context
            odoo = odoorpc.ODOO(ODOO_HOST, protocol=ODOO_PROTOCOL, port=ODOO_PORT)
            odoo.config['timeout'] = 300  # 5 minutes timeout
            logger.info(f"Logging in to database {ODOO_DATABASE} with user {ODOO_USERNAME}...")
            odoo.login(ODOO_DATABASE, ODOO_USERNAME, ODOO_PASSWORD)
            odoo_connection = odoo
            logger.info(f"Successfully connected to Odoo! User ID: {odoo.env.uid}")
        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {str(e)}")
            raise

    return odoo_connection


def authenticate(api_key):
    """Verify API key"""
    return api_key == MCP_API_KEY


def build_response(success=True, data=None, error=None):
    """Build standardized JSON response"""
    return jsonify({
        'success': success,
        'data': data,
        'error': error,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/mcp/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Try to connect to Odoo
        odoo = get_odoo_connection()
        odoo_status = "connected"
    except:
        odoo_status = "disconnected"
    
    return jsonify({
        'status': 'healthy',
        'service': 'Claro Distribution MCP Server (Standalone)',
        'version': '2.0',
        'odoo_status': odoo_status,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/mcp/resources', methods=['POST'])
def list_resources():
    """List available MCP resources"""
    try:
        data = request.get_json()
        if not authenticate(data.get('api_key')):
            return build_response(False, error='Invalid API key'), 401

        resources = [
            {
                'uri': 'claro://products',
                'name': 'Products',
                'description': 'All products/services (Business Lines) in Odoo',
                'mimeType': 'application/json'
            },
            {
                'uri': 'claro://sales-orders',
                'name': 'Sales Orders',
                'description': 'Sales orders from Odoo',
                'mimeType': 'application/json'
            },
            {
                'uri': 'claro://invoices',
                'name': 'Invoices',
                'description': 'Customer invoices',
                'mimeType': 'application/json'
            },
            {
                'uri': 'claro://expenses',
                'name': 'Expenses',
                'description': 'Company expenses',
                'mimeType': 'application/json'
            },
            {
                'uri': 'claro://partners',
                'name': 'Partners',
                'description': 'Customers and suppliers',
                'mimeType': 'application/json'
            }
        ]

        return build_response(True, resources)

    except Exception as e:
        logger.error(f"Error in list_resources: {str(e)}")
        return build_response(False, error=str(e)), 500


@app.route('/mcp/tools', methods=['POST'])
def list_tools():
    """List available MCP tools"""
    try:
        data = request.get_json()
        if not authenticate(data.get('api_key')):
            return build_response(False, error='Invalid API key'), 401

        tools = [
            {
                'name': 'get_sales_summary',
                'description': 'Get sales summary by product/service',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'start_date': {'type': 'string', 'description': 'Start date (YYYY-MM-DD)'},
                        'end_date': {'type': 'string', 'description': 'End date (YYYY-MM-DD)'}
                    }
                }
            },
            {
                'name': 'get_revenue_by_period',
                'description': 'Get revenue breakdown by time period',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'period': {'type': 'string', 'description': 'Period: month, quarter, year'},
                        'count': {'type': 'integer', 'description': 'Number of periods'}
                    }
                }
            },
            {
                'name': 'get_top_customers',
                'description': 'Get top customers by revenue',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'limit': {'type': 'integer', 'description': 'Number of customers (default: 10)'}
                    }
                }
            },
            {
                'name': 'get_expense_analysis',
                'description': 'Analyze company expenses',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'start_date': {'type': 'string'},
                        'end_date': {'type': 'string'}
                    }
                }
            }
        ]

        return build_response(True, tools)

    except Exception as e:
        logger.error(f"Error in list_tools: {str(e)}")
        return build_response(False, error=str(e)), 500


@app.route('/mcp/resource/read', methods=['POST'])
def read_resource():
    """Read data from a specific resource"""
    try:
        data = request.get_json()
        if not authenticate(data.get('api_key')):
            return build_response(False, error='Invalid API key'), 401

        uri = data.get('uri')
        odoo = get_odoo_connection()

        if uri == 'claro://products':
            # Get all products
            Product = odoo.env['product.product']
            products = Product.search_read(
                [('sale_ok', '=', True)],
                ['name', 'list_price', 'categ_id'],
                limit=100
            )
            result = products

        elif uri == 'claro://sales-orders':
            # Get recent sales orders
            SaleOrder = odoo.env['sale.order']
            orders = SaleOrder.search_read(
                [('state', 'in', ['sale', 'done'])],
                ['name', 'date_order', 'partner_id', 'amount_total', 'state'],
                limit=50,
                order='date_order desc'
            )
            result = orders

        elif uri == 'claro://invoices':
            # Get customer invoices
            Invoice = odoo.env['account.move']
            invoices = Invoice.search_read(
                [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')],
                ['name', 'invoice_date', 'partner_id', 'amount_total'],
                limit=50,
                order='invoice_date desc'
            )
            result = invoices

        elif uri == 'claro://partners':
            # Get customers
            Partner = odoo.env['res.partner']
            partners = Partner.search_read(
                [('customer_rank', '>', 0)],
                ['name', 'email', 'phone', 'city'],
                limit=50
            )
            result = partners

        else:
            return build_response(False, error=f'Unknown resource URI: {uri}'), 404

        return build_response(True, result)

    except Exception as e:
        logger.error(f"Error in read_resource: {str(e)}")
        return build_response(False, error=str(e)), 500


@app.route('/mcp/tool/call', methods=['POST'])
def call_tool():
    """Execute a tool with given parameters"""
    try:
        data = request.get_json()
        if not authenticate(data.get('api_key')):
            return build_response(False, error='Invalid API key'), 401

        tool_name = data.get('name')
        arguments = data.get('arguments', {})

        odoo = get_odoo_connection()

        if tool_name == 'get_sales_summary':
            result = get_sales_summary(odoo, arguments)
        elif tool_name == 'get_revenue_by_period':
            result = get_revenue_by_period(odoo, arguments)
        elif tool_name == 'get_top_customers':
            result = get_top_customers(odoo, arguments)
        elif tool_name == 'get_expense_analysis':
            result = get_expense_analysis(odoo, arguments)
        else:
            return build_response(False, error=f'Unknown tool: {tool_name}'), 404

        return build_response(True, result)

    except Exception as e:
        logger.error(f"Error in call_tool: {str(e)}")
        return build_response(False, error=str(e)), 500


def get_sales_summary(odoo, args):
    """Get sales summary by product"""
    SaleOrderLine = odoo.env['sale.order.line']
    
    domain = [('order_id.state', 'in', ['sale', 'done'])]
    
    if args.get('start_date'):
        domain.append(('order_id.date_order', '>=', args['start_date']))
    if args.get('end_date'):
        domain.append(('order_id.date_order', '<=', args['end_date']))
    
    lines = SaleOrderLine.search_read(
        domain,
        ['product_id', 'price_subtotal', 'product_uom_qty']
    )
    
    # Group by product
    products = {}
    for line in lines:
        product_id = line['product_id'][0]
        product_name = line['product_id'][1]
        
        if product_id not in products:
            products[product_id] = {
                'product': product_name,
                'total_revenue': 0,
                'quantity_sold': 0
            }
        
        products[product_id]['total_revenue'] += line['price_subtotal']
        products[product_id]['quantity_sold'] += line['product_uom_qty']
    
    return list(products.values())


def get_revenue_by_period(odoo, args):
    """Get revenue by time period"""
    period = args.get('period', 'month')
    count = args.get('count', 6)
    
    Invoice = odoo.env['account.move']
    
    # Get invoices from last N periods
    end_date = datetime.now().date()
    if period == 'month':
        start_date = end_date - timedelta(days=30 * count)
    elif period == 'quarter':
        start_date = end_date - timedelta(days=90 * count)
    else:  # year
        start_date = end_date - timedelta(days=365 * count)
    
    invoices = Invoice.search_read(
        [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', start_date.isoformat()),
            ('invoice_date', '<=', end_date.isoformat())
        ],
        ['invoice_date', 'amount_total']
    )
    
    # Group by period
    periods = {}
    for inv in invoices:
        date = datetime.strptime(inv['invoice_date'], '%Y-%m-%d')
        
        if period == 'month':
            key = date.strftime('%Y-%m')
        elif period == 'quarter':
            quarter = (date.month - 1) // 3 + 1
            key = f"{date.year}-Q{quarter}"
        else:
            key = str(date.year)
        
        if key not in periods:
            periods[key] = 0
        periods[key] += inv['amount_total']
    
    result = [{'period': k, 'revenue': v} for k, v in sorted(periods.items())]
    return result


def get_top_customers(odoo, args):
    """Get top customers by revenue"""
    limit = args.get('limit', 10)
    
    Invoice = odoo.env['account.move']
    
    invoices = Invoice.search_read(
        [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')],
        ['partner_id', 'amount_total']
    )
    
    # Group by customer
    customers = {}
    for inv in invoices:
        partner_id = inv['partner_id'][0]
        partner_name = inv['partner_id'][1]
        
        if partner_id not in customers:
            customers[partner_id] = {
                'customer': partner_name,
                'total_revenue': 0,
                'invoice_count': 0
            }
        
        customers[partner_id]['total_revenue'] += inv['amount_total']
        customers[partner_id]['invoice_count'] += 1
    
    # Sort and limit
    result = sorted(customers.values(), key=lambda x: x['total_revenue'], reverse=True)
    return result[:limit]


def get_expense_analysis(odoo, args):
    """Analyze expenses"""
    # Note: This uses Odoo's expense module if available
    # Adjust based on your Odoo setup
    
    try:
        Expense = odoo.env['hr.expense']
        
        domain = [('state', '=', 'done')]
        if args.get('start_date'):
            domain.append(('date', '>=', args['start_date']))
        if args.get('end_date'):
            domain.append(('date', '<=', args['end_date']))
        
        expenses = Expense.search_read(
            domain,
            ['name', 'date', 'total_amount', 'product_id', 'employee_id']
        )
        
        # Group by category
        categories = {}
        for exp in expenses:
            category = exp['product_id'][1] if exp.get('product_id') else 'Other'
            
            if category not in categories:
                categories[category] = {
                    'category': category,
                    'total': 0,
                    'count': 0
                }
            
            categories[category]['total'] += exp['total_amount']
            categories[category]['count'] += 1
        
        return list(categories.values())
    
    except:
        # If hr.expense module not installed, use account moves
        Invoice = odoo.env['account.move']
        
        domain = [('move_type', '=', 'in_invoice'), ('state', '=', 'posted')]
        if args.get('start_date'):
            domain.append(('invoice_date', '>=', args['start_date']))
        if args.get('end_date'):
            domain.append(('invoice_date', '<=', args['end_date']))
        
        bills = Invoice.search_read(
            domain,
            ['name', 'invoice_date', 'amount_total', 'partner_id']
        )
        
        return {
            'total_expenses': sum(b['amount_total'] for b in bills),
            'expense_count': len(bills),
            'bills': bills[:20]  # Return first 20
        }


if __name__ == '__main__':
    print("=" * 60)
    print("Claro Distribution MCP Server - Standalone Version")
    print("=" * 60)
    print(f"\nOdoo Host: {ODOO_HOST}")
    print(f"Odoo Database: {ODOO_DATABASE}")
    print(f"\nStarting server...")
    print(f"\nHealth check: http://localhost:5000/mcp/health")
    print("=" * 60)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
