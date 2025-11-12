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
from flask_cors import CORS
import odoorpc
from dotenv import load_dotenv
import dynamic_tools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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

    dynamic_count = len(dynamic_tools.DYNAMIC_FUNCTIONS)

    return jsonify({
        'status': 'healthy',
        'service': 'Claro Distribution MCP Server (Standalone)',
        'version': '2.0',
        'odoo_status': odoo_status,
        'dynamic_tools_count': dynamic_count,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/mcp/reload', methods=['POST'])
def reload_tools():
    """Reload dynamic tools from disk"""
    try:
        data = request.get_json()
        if not authenticate(data.get('api_key')):
            return build_response(False, error='Invalid API key'), 401

        # Reload dynamic tools
        dynamic_tools.load_persisted_tools()

        return build_response(True, {
            'message': 'Dynamic tools reloaded successfully',
            'dynamic_tools_count': len(dynamic_tools.DYNAMIC_FUNCTIONS)
        })
    except Exception as e:
        logger.error(f"Error in reload_tools: {str(e)}")
        return build_response(False, error=str(e)), 500


@app.route('/mcp/register-tool', methods=['POST'])
def register_tool():
    """Register a new dynamic tool"""
    try:
        data = request.get_json()
        if not authenticate(data.get('api_key')):
            return build_response(False, error='Invalid API key'), 401

        tool_definition = data.get('tool_definition')
        function_code = data.get('function_code')

        if not tool_definition or not function_code:
            return build_response(False, error='Missing tool_definition or function_code'), 400

        tool_name = tool_definition['name']

        # Register the tool in memory
        dynamic_tools.register_dynamic_tool(tool_definition, function_code)

        # Save to file for persistence
        file_path = dynamic_tools.save_dynamic_tool_to_file(
            tool_name,
            tool_definition,
            function_code
        )

        logger.info(f"✅ Tool '{tool_name}' registered successfully on MCP server!")

        return build_response(True, {
            'message': f"Tool '{tool_name}' registered successfully",
            'tool_name': tool_name,
            'file_path': file_path,
            'dynamic_tools_count': len(dynamic_tools.DYNAMIC_FUNCTIONS)
        })
    except Exception as e:
        logger.error(f"Error in register_tool: {str(e)}")
        return build_response(False, error=str(e)), 500


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
            # Financial & Sales
            {
                'name': 'get_sales_summary',
                'description': 'Get sales summary by product/service',
                'input_schema': {
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
                'input_schema': {
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
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'limit': {'type': 'integer', 'description': 'Number of customers (default: 10)'}
                    }
                }
            },
            {
                'name': 'get_expense_analysis',
                'description': 'Analyze company expenses',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'start_date': {'type': 'string'},
                        'end_date': {'type': 'string'}
                    }
                }
            },
            # HR & Workforce
            {
                'name': 'get_employee_metrics',
                'description': 'Get employee headcount, department distribution, and workforce analytics',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'group_by': {'type': 'string', 'description': 'Group by: department, job, contract_type'}
                    }
                }
            },
            {
                'name': 'get_attendance_analysis',
                'description': 'Analyze employee attendance patterns and work hours',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'start_date': {'type': 'string'},
                        'end_date': {'type': 'string'},
                        'employee_id': {'type': 'integer', 'description': 'Optional: specific employee'}
                    }
                }
            },
            {
                'name': 'get_timesheet_summary',
                'description': 'Get timesheet data by project, employee, or task',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'start_date': {'type': 'string'},
                        'end_date': {'type': 'string'},
                        'group_by': {'type': 'string', 'description': 'Group by: employee, project, task'}
                    }
                }
            },
            {
                'name': 'get_recruitment_pipeline',
                'description': 'Get recruitment metrics: open positions, applicants, hiring funnel',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'start_date': {'type': 'string'},
                        'end_date': {'type': 'string'}
                    }
                }
            },
            # CRM & Sales Pipeline
            {
                'name': 'get_crm_pipeline',
                'description': 'Get CRM pipeline: leads, opportunities, conversion rates by stage',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'start_date': {'type': 'string'},
                        'end_date': {'type': 'string'}
                    }
                }
            },
            {
                'name': 'get_sales_team_performance',
                'description': 'Analyze sales team performance: quotas, achievements, win rates',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'start_date': {'type': 'string'},
                        'end_date': {'type': 'string'},
                        'team_id': {'type': 'integer', 'description': 'Optional: specific team'}
                    }
                }
            },
            # Operations & Inventory
            {
                'name': 'get_inventory_status',
                'description': 'Get inventory levels, stock movements, and warehouse analytics',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'warehouse_id': {'type': 'integer', 'description': 'Optional: specific warehouse'},
                        'low_stock_threshold': {'type': 'number', 'description': 'Alert threshold'}
                    }
                }
            },
            {
                'name': 'get_purchase_analysis',
                'description': 'Analyze purchase orders: spending by vendor, delivery performance',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'start_date': {'type': 'string'},
                        'end_date': {'type': 'string'}
                    }
                }
            },
            # Project Management
            {
                'name': 'get_project_status',
                'description': 'Get project status: progress, task completion, resource allocation',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'project_id': {'type': 'integer', 'description': 'Optional: specific project'},
                        'include_archived': {'type': 'boolean', 'description': 'Include archived projects'}
                    }
                }
            },
            # KPIs & Cross-functional Analytics
            {
                'name': 'get_business_kpis',
                'description': 'Get comprehensive business KPIs: revenue, profit margins, employee productivity, customer satisfaction',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'period': {'type': 'string', 'description': 'month, quarter, year'},
                        'include_trends': {'type': 'boolean', 'description': 'Include period-over-period trends'}
                    }
                }
            }
        ]

        # Add dynamic tools
        dynamic_tool_list = dynamic_tools.get_all_dynamic_tools()
        tools.extend(dynamic_tool_list)

        logger.info(f"Total tools (including {len(dynamic_tool_list)} dynamic): {len(tools)}")

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

        # Financial & Sales
        if tool_name == 'get_sales_summary':
            result = get_sales_summary(odoo, arguments)
        elif tool_name == 'get_revenue_by_period':
            result = get_revenue_by_period(odoo, arguments)
        elif tool_name == 'get_top_customers':
            result = get_top_customers(odoo, arguments)
        elif tool_name == 'get_expense_analysis':
            result = get_expense_analysis(odoo, arguments)
        # HR & Workforce
        elif tool_name == 'get_employee_metrics':
            result = get_employee_metrics(odoo, arguments)
        elif tool_name == 'get_attendance_analysis':
            result = get_attendance_analysis(odoo, arguments)
        elif tool_name == 'get_timesheet_summary':
            result = get_timesheet_summary(odoo, arguments)
        elif tool_name == 'get_recruitment_pipeline':
            result = get_recruitment_pipeline(odoo, arguments)
        # CRM & Sales Pipeline
        elif tool_name == 'get_crm_pipeline':
            result = get_crm_pipeline(odoo, arguments)
        elif tool_name == 'get_sales_team_performance':
            result = get_sales_team_performance(odoo, arguments)
        # Operations & Inventory
        elif tool_name == 'get_inventory_status':
            result = get_inventory_status(odoo, arguments)
        elif tool_name == 'get_purchase_analysis':
            result = get_purchase_analysis(odoo, arguments)
        # Project Management
        elif tool_name == 'get_project_status':
            result = get_project_status(odoo, arguments)
        # KPIs
        elif tool_name == 'get_business_kpis':
            result = get_business_kpis(odoo, arguments)
        # Try dynamic tools
        elif tool_name in dynamic_tools.DYNAMIC_FUNCTIONS:
            logger.info(f"Calling dynamic tool: {tool_name}")
            result = dynamic_tools.call_dynamic_tool(tool_name, odoo, arguments, logger)
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


### HR & WORKFORCE FUNCTIONS ###

def get_employee_metrics(odoo, args):
    """Get employee metrics and workforce analytics"""
    try:
        Employee = odoo.env['hr.employee']
        group_by = args.get('group_by', 'department')

        employees = Employee.search_read(
            [('active', '=', True)],
            ['name', 'department_id', 'job_id', 'contract_id', 'work_email']
        )

        total_count = len(employees)

        if group_by == 'department':
            groups = {}
            for emp in employees:
                dept = emp['department_id'][1] if emp.get('department_id') else 'No Department'
                groups[dept] = groups.get(dept, 0) + 1

            return {
                'total_employees': total_count,
                'by_department': [{'department': k, 'count': v} for k, v in groups.items()]
            }

        elif group_by == 'job':
            groups = {}
            for emp in employees:
                job = emp['job_id'][1] if emp.get('job_id') else 'No Job Title'
                groups[job] = groups.get(job, 0) + 1

            return {
                'total_employees': total_count,
                'by_job': [{'job_title': k, 'count': v} for k, v in groups.items()]
            }

        return {'total_employees': total_count, 'employees': employees[:50]}

    except Exception as e:
        logger.error(f"Error in get_employee_metrics: {str(e)}")
        return {'error': str(e), 'total_employees': 0}


def get_attendance_analysis(odoo, args):
    """Analyze attendance patterns"""
    try:
        Attendance = odoo.env['hr.attendance']

        domain = []
        if args.get('start_date'):
            domain.append(('check_in', '>=', args['start_date']))
        if args.get('end_date'):
            domain.append(('check_in', '<=', args['end_date']))
        if args.get('employee_id'):
            domain.append(('employee_id', '=', args['employee_id']))

        attendances = Attendance.search_read(
            domain,
            ['employee_id', 'check_in', 'check_out', 'worked_hours'],
            limit=1000
        )

        # Calculate metrics
        total_hours = sum(a.get('worked_hours', 0) for a in attendances)
        employee_hours = {}

        for att in attendances:
            emp_id = att['employee_id'][0]
            emp_name = att['employee_id'][1]
            if emp_id not in employee_hours:
                employee_hours[emp_id] = {'employee': emp_name, 'total_hours': 0, 'days': 0}
            employee_hours[emp_id]['total_hours'] += att.get('worked_hours', 0)
            employee_hours[emp_id]['days'] += 1

        return {
            'total_hours_worked': total_hours,
            'total_attendance_records': len(attendances),
            'by_employee': list(employee_hours.values())[:20]
        }

    except Exception as e:
        logger.error(f"Error in get_attendance_analysis: {str(e)}")
        return {'error': str(e), 'message': 'Attendance module may not be installed'}


def get_timesheet_summary(odoo, args):
    """Get timesheet data"""
    try:
        Timesheet = odoo.env['account.analytic.line']
        group_by = args.get('group_by', 'employee')

        domain = [('project_id', '!=', False)]
        if args.get('start_date'):
            domain.append(('date', '>=', args['start_date']))
        if args.get('end_date'):
            domain.append(('date', '<=', args['end_date']))

        timesheets = Timesheet.search_read(
            domain,
            ['employee_id', 'project_id', 'task_id', 'unit_amount', 'date'],
            limit=1000
        )

        if group_by == 'employee':
            groups = {}
            for ts in timesheets:
                emp = ts['employee_id'][1] if ts.get('employee_id') else 'Unknown'
                if emp not in groups:
                    groups[emp] = {'employee': emp, 'hours': 0, 'entries': 0}
                groups[emp]['hours'] += ts.get('unit_amount', 0)
                groups[emp]['entries'] += 1

            return list(groups.values())

        elif group_by == 'project':
            groups = {}
            for ts in timesheets:
                proj = ts['project_id'][1] if ts.get('project_id') else 'No Project'
                if proj not in groups:
                    groups[proj] = {'project': proj, 'hours': 0, 'entries': 0}
                groups[proj]['hours'] += ts.get('unit_amount', 0)
                groups[proj]['entries'] += 1

            return list(groups.values())

        return timesheets[:50]

    except Exception as e:
        logger.error(f"Error in get_timesheet_summary: {str(e)}")
        return {'error': str(e), 'message': 'Timesheet/Project module may not be installed'}


def get_recruitment_pipeline(odoo, args):
    """Get recruitment metrics"""
    try:
        Job = odoo.env['hr.job']
        Applicant = odoo.env['hr.applicant']

        # Open positions
        jobs = Job.search_read(
            [('state', '=', 'recruit')],
            ['name', 'no_of_recruitment', 'no_of_hired_employee']
        )

        # Applicants
        domain = []
        if args.get('start_date'):
            domain.append(('create_date', '>=', args['start_date']))
        if args.get('end_date'):
            domain.append(('create_date', '<=', args['end_date']))

        applicants = Applicant.search_read(
            domain,
            ['name', 'job_id', 'stage_id', 'create_date'],
            limit=200
        )

        # Group by stage
        stages = {}
        for app in applicants:
            stage = app['stage_id'][1] if app.get('stage_id') else 'Unknown'
            stages[stage] = stages.get(stage, 0) + 1

        return {
            'open_positions': len(jobs),
            'total_applicants': len(applicants),
            'by_stage': [{'stage': k, 'count': v} for k, v in stages.items()],
            'jobs': jobs
        }

    except Exception as e:
        logger.error(f"Error in get_recruitment_pipeline: {str(e)}")
        return {'error': str(e), 'message': 'Recruitment module may not be installed'}


### CRM & SALES FUNCTIONS ###

def get_crm_pipeline(odoo, args):
    """Get CRM pipeline metrics"""
    try:
        Lead = odoo.env['crm.lead']

        domain = [('type', '=', 'opportunity')]
        if args.get('start_date'):
            domain.append(('create_date', '>=', args['start_date']))
        if args.get('end_date'):
            domain.append(('create_date', '<=', args['end_date']))

        opportunities = Lead.search_read(
            domain,
            ['name', 'partner_id', 'expected_revenue', 'probability', 'stage_id', 'user_id'],
            limit=200
        )

        # Calculate metrics
        total_value = sum(o.get('expected_revenue', 0) for o in opportunities)
        weighted_value = sum(o.get('expected_revenue', 0) * o.get('probability', 0) / 100 for o in opportunities)

        # Group by stage
        stages = {}
        for opp in opportunities:
            stage = opp['stage_id'][1] if opp.get('stage_id') else 'Unknown'
            if stage not in stages:
                stages[stage] = {'stage': stage, 'count': 0, 'total_value': 0}
            stages[stage]['count'] += 1
            stages[stage]['total_value'] += opp.get('expected_revenue', 0)

        return {
            'total_opportunities': len(opportunities),
            'total_pipeline_value': total_value,
            'weighted_pipeline_value': weighted_value,
            'by_stage': list(stages.values())
        }

    except Exception as e:
        logger.error(f"Error in get_crm_pipeline: {str(e)}")
        return {'error': str(e), 'message': 'CRM module may not be installed'}


def get_sales_team_performance(odoo, args):
    """Analyze sales team performance"""
    try:
        Team = odoo.env['crm.team']
        SaleOrder = odoo.env['sale.order']

        teams = Team.search_read([], ['name', 'user_id', 'member_ids'])

        domain = [('state', 'in', ['sale', 'done'])]
        if args.get('start_date'):
            domain.append(('date_order', '>=', args['start_date']))
        if args.get('end_date'):
            domain.append(('date_order', '<=', args['end_date']))
        if args.get('team_id'):
            domain.append(('team_id', '=', args['team_id']))

        orders = SaleOrder.search_read(
            domain,
            ['team_id', 'user_id', 'amount_total'],
            limit=1000
        )

        # Group by team
        team_performance = {}
        for order in orders:
            team = order['team_id'][1] if order.get('team_id') else 'No Team'
            if team not in team_performance:
                team_performance[team] = {'team': team, 'revenue': 0, 'orders': 0}
            team_performance[team]['revenue'] += order['amount_total']
            team_performance[team]['orders'] += 1

        return {
            'teams': teams,
            'performance': list(team_performance.values())
        }

    except Exception as e:
        logger.error(f"Error in get_sales_team_performance: {str(e)}")
        return {'error': str(e)}


### OPERATIONS & INVENTORY FUNCTIONS ###

def get_inventory_status(odoo, args):
    """Get inventory levels and analytics"""
    try:
        Product = odoo.env['product.product']
        Quant = odoo.env['stock.quant']

        domain = []
        if args.get('warehouse_id'):
            domain.append(('location_id.warehouse_id', '=', args['warehouse_id']))

        quants = Quant.search_read(
            domain,
            ['product_id', 'location_id', 'quantity', 'reserved_quantity'],
            limit=500
        )

        # Calculate available quantity by product
        products = {}
        for quant in quants:
            prod_id = quant['product_id'][0]
            prod_name = quant['product_id'][1]
            available = quant['quantity'] - quant.get('reserved_quantity', 0)

            if prod_id not in products:
                products[prod_id] = {'product': prod_name, 'available': 0, 'reserved': 0}
            products[prod_id]['available'] += available
            products[prod_id]['reserved'] += quant.get('reserved_quantity', 0)

        # Filter low stock if threshold provided
        result = list(products.values())
        if args.get('low_stock_threshold'):
            threshold = args['low_stock_threshold']
            result = [p for p in result if p['available'] < threshold]

        return result[:100]

    except Exception as e:
        logger.error(f"Error in get_inventory_status: {str(e)}")
        return {'error': str(e), 'message': 'Inventory module may not be installed'}


def get_purchase_analysis(odoo, args):
    """Analyze purchase orders"""
    try:
        Purchase = odoo.env['purchase.order']

        domain = [('state', 'in', ['purchase', 'done'])]
        if args.get('start_date'):
            domain.append(('date_order', '>=', args['start_date']))
        if args.get('end_date'):
            domain.append(('date_order', '<=', args['end_date']))

        purchases = Purchase.search_read(
            domain,
            ['name', 'partner_id', 'date_order', 'amount_total', 'state'],
            limit=200
        )

        # Group by vendor
        vendors = {}
        for po in purchases:
            vendor = po['partner_id'][1] if po.get('partner_id') else 'Unknown'
            if vendor not in vendors:
                vendors[vendor] = {'vendor': vendor, 'total_spent': 0, 'order_count': 0}
            vendors[vendor]['total_spent'] += po['amount_total']
            vendors[vendor]['order_count'] += 1

        total_spent = sum(po['amount_total'] for po in purchases)

        return {
            'total_purchase_orders': len(purchases),
            'total_spent': total_spent,
            'by_vendor': sorted(list(vendors.values()), key=lambda x: x['total_spent'], reverse=True)[:20]
        }

    except Exception as e:
        logger.error(f"Error in get_purchase_analysis: {str(e)}")
        return {'error': str(e), 'message': 'Purchase module may not be installed'}


### PROJECT MANAGEMENT FUNCTIONS ###

def get_project_status(odoo, args):
    """Get project status and task completion"""
    try:
        Project = odoo.env['project.project']
        Task = odoo.env['project.task']

        domain = []
        if args.get('project_id'):
            domain.append(('id', '=', args['project_id']))
        if not args.get('include_archived', False):
            domain.append(('active', '=', True))

        projects = Project.search_read(
            domain,
            ['name', 'user_id', 'task_count', 'task_ids'],
            limit=50
        )

        project_data = []
        for proj in projects:
            # Get tasks for this project
            tasks = Task.search_read(
                [('project_id', '=', proj['id'])],
                ['name', 'stage_id', 'user_ids', 'date_deadline']
            )

            completed = len([t for t in tasks if t.get('stage_id') and 'done' in t['stage_id'][1].lower()])

            project_data.append({
                'project': proj['name'],
                'total_tasks': len(tasks),
                'completed_tasks': completed,
                'completion_rate': (completed / len(tasks) * 100) if tasks else 0
            })

        return project_data

    except Exception as e:
        logger.error(f"Error in get_project_status: {str(e)}")
        return {'error': str(e), 'message': 'Project module may not be installed'}


### BUSINESS KPIs FUNCTION ###

def get_business_kpis(odoo, args):
    """Get comprehensive business KPIs"""
    try:
        period = args.get('period', 'month')

        # Calculate date ranges
        end_date = datetime.now().date()
        if period == 'month':
            start_date = end_date - timedelta(days=30)
            previous_start = start_date - timedelta(days=30)
        elif period == 'quarter':
            start_date = end_date - timedelta(days=90)
            previous_start = start_date - timedelta(days=90)
        else:  # year
            start_date = end_date - timedelta(days=365)
            previous_start = start_date - timedelta(days=365)

        Invoice = odoo.env['account.move']

        # Current period revenue
        current_invoices = Invoice.search_read(
            [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', start_date.isoformat()),
                ('invoice_date', '<=', end_date.isoformat())
            ],
            ['amount_total']
        )
        current_revenue = sum(inv['amount_total'] for inv in current_invoices)

        # Previous period revenue (for trends)
        if args.get('include_trends', False):
            previous_invoices = Invoice.search_read(
                [
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('invoice_date', '>=', previous_start.isoformat()),
                    ('invoice_date', '<', start_date.isoformat())
                ],
                ['amount_total']
            )
            previous_revenue = sum(inv['amount_total'] for inv in previous_invoices)
            revenue_growth = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue else 0
        else:
            revenue_growth = None

        # Employee count
        try:
            Employee = odoo.env['hr.employee']
            employee_count = Employee.search_count([('active', '=', True)])
        except:
            employee_count = 0

        # Customer count
        Partner = odoo.env['res.partner']
        customer_count = Partner.search_count([('customer_rank', '>', 0)])

        kpis = {
            'period': period,
            'revenue': current_revenue,
            'invoice_count': len(current_invoices),
            'employee_count': employee_count,
            'customer_count': customer_count,
            'revenue_per_employee': current_revenue / employee_count if employee_count > 0 else 0,
        }

        if revenue_growth is not None:
            kpis['revenue_growth_percent'] = revenue_growth

        return kpis

    except Exception as e:
        logger.error(f"Error in get_business_kpis: {str(e)}")
        return {'error': str(e)}


if __name__ == '__main__':
    # Get port from environment variable (Railway provides this) or default to 5000
    port = int(os.getenv('PORT', 5000))

    print("=" * 60)
    print("Claro Distribution MCP Server - Standalone Version")
    print("=" * 60)
    print(f"\nOdoo Host: {ODOO_HOST}")
    print(f"Odoo Database: {ODOO_DATABASE}")
    print(f"\nStarting server on port {port}...")
    print(f"\nHealth check: http://localhost:{port}/mcp/health")
    print("=" * 60)

    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
