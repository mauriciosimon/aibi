#!/usr/bin/env python3
"""
Power BI MCP Server
===================
MCP (Model Context Protocol) server for Power BI data access.
Provides structured tools for querying Power BI datasets, executing DAX queries,
and retrieving metadata.

Architecture:
    Claude AI → MCP Protocol → This Server → Power BI REST API

Tools Provided:
    - list_workspaces: Get all available Power BI workspaces
    - list_datasets: Get datasets in a workspace
    - get_dataset_schema: Get tables, columns, measures for a dataset
    - execute_dax_query: Run DAX queries against a dataset
    - list_reports: Get all reports in a workspace
    - get_report_pages: Get pages from a specific report
"""

import sys
import json
import logging
import os
from typing import Any, Dict, List, Optional
import requests
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Power BI Configuration from environment
POWERBI_CLIENT_ID = os.getenv('POWERBI_CLIENT_ID')
POWERBI_TENANT_ID = os.getenv('POWERBI_TENANT_ID')
POWERBI_CLIENT_SECRET = os.getenv('POWERBI_CLIENT_SECRET')

# Power BI API Base URL
POWERBI_API_BASE = 'https://api.powerbi.com/v1.0/myorg'

# Token cache (simple in-memory cache)
_token_cache = {
    'token': None,
    'expires_at': None
}


def get_access_token() -> str:
    """
    Get Azure AD access token for Power BI API.
    Uses client credentials flow with caching.
    """
    # Check cache
    if _token_cache['token'] and _token_cache['expires_at']:
        if datetime.now() < _token_cache['expires_at']:
            return _token_cache['token']

    # Get new token
    token_url = f'https://login.microsoftonline.com/{POWERBI_TENANT_ID}/oauth2/v2.0/token'
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': POWERBI_CLIENT_ID,
        'client_secret': POWERBI_CLIENT_SECRET,
        'scope': 'https://analysis.windows.net/powerbi/api/.default'
    }

    try:
        response = requests.post(token_url, data=token_data, timeout=30)
        response.raise_for_status()
        token_response = response.json()

        access_token = token_response.get('access_token')
        expires_in = token_response.get('expires_in', 3600)

        # Cache token (expire 5 minutes early for safety)
        _token_cache['token'] = access_token
        _token_cache['expires_at'] = datetime.now() + timedelta(seconds=expires_in - 300)

        logger.info("Successfully obtained Power BI access token")
        return access_token

    except Exception as e:
        logger.error(f"Failed to get access token: {str(e)}")
        raise Exception(f"Authentication failed: {str(e)}")


def make_powerbi_request(endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict:
    """
    Make authenticated request to Power BI API.

    Args:
        endpoint: API endpoint (e.g., '/groups')
        method: HTTP method
        data: Request body for POST requests

    Returns:
        Response JSON
    """
    access_token = get_access_token()
    url = f"{POWERBI_API_BASE}{endpoint}"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=60)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=60)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        error_msg = f"Power BI API error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise


# ===== MCP TOOL IMPLEMENTATIONS =====

def list_workspaces() -> Dict[str, Any]:
    """
    List all Power BI workspaces (groups) accessible to the service principal.

    Returns:
        Dict with workspaces list and count
    """
    try:
        result = make_powerbi_request('/groups')
        workspaces = result.get('value', [])

        return {
            'success': True,
            'workspaces': [
                {
                    'id': ws['id'],
                    'name': ws['name'],
                    'type': ws.get('type', 'Unknown'),
                    'state': ws.get('state', 'Unknown')
                }
                for ws in workspaces
            ],
            'count': len(workspaces)
        }
    except Exception as e:
        logger.error(f"Error listing workspaces: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def list_datasets(workspace_id: str) -> Dict[str, Any]:
    """
    List all datasets in a specific workspace.

    Args:
        workspace_id: Power BI workspace (group) ID

    Returns:
        Dict with datasets list and metadata
    """
    try:
        result = make_powerbi_request(f'/groups/{workspace_id}/datasets')
        datasets = result.get('value', [])

        return {
            'success': True,
            'workspace_id': workspace_id,
            'datasets': [
                {
                    'id': ds['id'],
                    'name': ds['name'],
                    'configured_by': ds.get('configuredBy', 'Unknown'),
                    'is_refreshable': ds.get('isRefreshable', False),
                    'is_effective_identity_required': ds.get('isEffectiveIdentityRequired', False),
                    'is_effective_identity_roles_required': ds.get('isEffectiveIdentityRolesRequired', False),
                    'target_storage_mode': ds.get('targetStorageMode', 'Unknown')
                }
                for ds in datasets
            ],
            'count': len(datasets)
        }
    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def get_dataset_schema(workspace_id: str, dataset_id: str) -> Dict[str, Any]:
    """
    Get the schema (tables, columns, measures, relationships) for a dataset.

    Args:
        workspace_id: Power BI workspace ID
        dataset_id: Dataset ID

    Returns:
        Dict with dataset schema including tables, columns, and measures
    """
    try:
        # Get dataset tables
        result = make_powerbi_request(f'/groups/{workspace_id}/datasets/{dataset_id}/datasources')

        # For now, we'll return basic dataset info
        # Note: Full schema introspection requires XMLA endpoint or specific API calls
        dataset_info = make_powerbi_request(f'/groups/{workspace_id}/datasets/{dataset_id}')

        return {
            'success': True,
            'workspace_id': workspace_id,
            'dataset_id': dataset_id,
            'dataset_name': dataset_info.get('name', 'Unknown'),
            'note': 'Full schema introspection requires executing DAX queries. Use execute_dax_query with EVALUATE queries to explore tables.',
            'configured_by': dataset_info.get('configuredBy', 'Unknown'),
            'is_refreshable': dataset_info.get('isRefreshable', False)
        }
    except Exception as e:
        logger.error(f"Error getting dataset schema: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def execute_dax_query(workspace_id: str, dataset_id: str, dax_query: str) -> Dict[str, Any]:
    """
    Execute a DAX query against a Power BI dataset.

    Args:
        workspace_id: Power BI workspace ID
        dataset_id: Dataset ID
        dax_query: DAX query to execute (e.g., "EVALUATE 'Sales'")

    Returns:
        Dict with query results
    """
    try:
        endpoint = f'/groups/{workspace_id}/datasets/{dataset_id}/executeQueries'

        payload = {
            'queries': [
                {
                    'query': dax_query
                }
            ],
            'serializerSettings': {
                'includeNulls': True
            }
        }

        result = make_powerbi_request(endpoint, method='POST', data=payload)

        # Parse results
        if 'results' in result and len(result['results']) > 0:
            query_result = result['results'][0]

            if 'error' in query_result:
                return {
                    'success': False,
                    'error': query_result['error'].get('message', 'Query execution failed')
                }

            tables = query_result.get('tables', [])

            if tables:
                table = tables[0]
                rows = table.get('rows', [])

                return {
                    'success': True,
                    'workspace_id': workspace_id,
                    'dataset_id': dataset_id,
                    'query': dax_query,
                    'row_count': len(rows),
                    'rows': rows[:1000],  # Limit to first 1000 rows
                    'truncated': len(rows) > 1000
                }
            else:
                return {
                    'success': True,
                    'workspace_id': workspace_id,
                    'dataset_id': dataset_id,
                    'query': dax_query,
                    'row_count': 0,
                    'rows': []
                }
        else:
            return {
                'success': False,
                'error': 'No results returned from query'
            }

    except Exception as e:
        logger.error(f"Error executing DAX query: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def list_reports(workspace_id: str) -> Dict[str, Any]:
    """
    List all reports in a workspace.

    Args:
        workspace_id: Power BI workspace ID

    Returns:
        Dict with reports list
    """
    try:
        result = make_powerbi_request(f'/groups/{workspace_id}/reports')
        reports = result.get('value', [])

        return {
            'success': True,
            'workspace_id': workspace_id,
            'reports': [
                {
                    'id': rpt['id'],
                    'name': rpt['name'],
                    'web_url': rpt.get('webUrl', ''),
                    'embed_url': rpt.get('embedUrl', ''),
                    'dataset_id': rpt.get('datasetId', '')
                }
                for rpt in reports
            ],
            'count': len(reports)
        }
    except Exception as e:
        logger.error(f"Error listing reports: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def get_report_pages(workspace_id: str, report_id: str) -> Dict[str, Any]:
    """
    Get pages from a specific Power BI report.

    Args:
        workspace_id: Power BI workspace ID
        report_id: Report ID

    Returns:
        Dict with report pages
    """
    try:
        result = make_powerbi_request(f'/groups/{workspace_id}/reports/{report_id}/pages')
        pages = result.get('value', [])

        return {
            'success': True,
            'workspace_id': workspace_id,
            'report_id': report_id,
            'pages': [
                {
                    'name': page['name'],
                    'display_name': page['displayName'],
                    'order': page.get('order', 0)
                }
                for page in pages
            ],
            'count': len(pages)
        }
    except Exception as e:
        logger.error(f"Error getting report pages: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


# ===== MCP SERVER IMPLEMENTATION =====

def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route tool calls to appropriate handlers.
    """
    logger.info(f"Handling tool call: {tool_name} with args: {arguments}")

    if tool_name == 'list_workspaces':
        return list_workspaces()

    elif tool_name == 'list_datasets':
        workspace_id = arguments.get('workspace_id')
        if not workspace_id:
            return {'success': False, 'error': 'workspace_id is required'}
        return list_datasets(workspace_id)

    elif tool_name == 'get_dataset_schema':
        workspace_id = arguments.get('workspace_id')
        dataset_id = arguments.get('dataset_id')
        if not workspace_id or not dataset_id:
            return {'success': False, 'error': 'workspace_id and dataset_id are required'}
        return get_dataset_schema(workspace_id, dataset_id)

    elif tool_name == 'execute_dax_query':
        workspace_id = arguments.get('workspace_id')
        dataset_id = arguments.get('dataset_id')
        dax_query = arguments.get('dax_query')
        if not workspace_id or not dataset_id or not dax_query:
            return {'success': False, 'error': 'workspace_id, dataset_id, and dax_query are required'}
        return execute_dax_query(workspace_id, dataset_id, dax_query)

    elif tool_name == 'list_reports':
        workspace_id = arguments.get('workspace_id')
        if not workspace_id:
            return {'success': False, 'error': 'workspace_id is required'}
        return list_reports(workspace_id)

    elif tool_name == 'get_report_pages':
        workspace_id = arguments.get('workspace_id')
        report_id = arguments.get('report_id')
        if not workspace_id or not report_id:
            return {'success': False, 'error': 'workspace_id and report_id are required'}
        return get_report_pages(workspace_id, report_id)

    else:
        return {'success': False, 'error': f'Unknown tool: {tool_name}'}


def handle_initialize(params: Dict) -> Dict:
    """Handle MCP initialize request."""
    logger.info("Initializing Power BI MCP Server")

    # Check if credentials are configured
    if not all([POWERBI_CLIENT_ID, POWERBI_TENANT_ID, POWERBI_CLIENT_SECRET]):
        logger.error("Power BI credentials not configured!")
        return {
            'protocolVersion': '2024-11-05',
            'serverInfo': {
                'name': 'powerbi-mcp-server',
                'version': '1.0.0'
            },
            'capabilities': {
                'tools': {}
            },
            'error': 'Power BI credentials not configured. Set POWERBI_CLIENT_ID, POWERBI_TENANT_ID, and POWERBI_CLIENT_SECRET environment variables.'
        }

    return {
        'protocolVersion': '2024-11-05',
        'serverInfo': {
            'name': 'powerbi-mcp-server',
            'version': '1.0.0'
        },
        'capabilities': {
            'tools': {}
        }
    }


def handle_list_tools(params: Dict) -> Dict:
    """Handle MCP tools/list request."""
    return {
        'tools': [
            {
                'name': 'list_workspaces',
                'description': 'List all Power BI workspaces (groups) accessible to the service principal',
                'inputSchema': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            },
            {
                'name': 'list_datasets',
                'description': 'List all datasets in a specific Power BI workspace',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'workspace_id': {
                            'type': 'string',
                            'description': 'Power BI workspace (group) ID'
                        }
                    },
                    'required': ['workspace_id']
                }
            },
            {
                'name': 'get_dataset_schema',
                'description': 'Get schema information (tables, columns, measures) for a Power BI dataset',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'workspace_id': {
                            'type': 'string',
                            'description': 'Power BI workspace ID'
                        },
                        'dataset_id': {
                            'type': 'string',
                            'description': 'Dataset ID'
                        }
                    },
                    'required': ['workspace_id', 'dataset_id']
                }
            },
            {
                'name': 'execute_dax_query',
                'description': 'Execute a DAX query against a Power BI dataset. Use EVALUATE statements to query tables.',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'workspace_id': {
                            'type': 'string',
                            'description': 'Power BI workspace ID'
                        },
                        'dataset_id': {
                            'type': 'string',
                            'description': 'Dataset ID'
                        },
                        'dax_query': {
                            'type': 'string',
                            'description': 'DAX query to execute (e.g., "EVALUATE \'Sales\'" or "EVALUATE TOPN(10, \'Sales\', [Amount], DESC)")'
                        }
                    },
                    'required': ['workspace_id', 'dataset_id', 'dax_query']
                }
            },
            {
                'name': 'list_reports',
                'description': 'List all reports in a Power BI workspace',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'workspace_id': {
                            'type': 'string',
                            'description': 'Power BI workspace ID'
                        }
                    },
                    'required': ['workspace_id']
                }
            },
            {
                'name': 'get_report_pages',
                'description': 'Get pages from a specific Power BI report',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'workspace_id': {
                            'type': 'string',
                            'description': 'Power BI workspace ID'
                        },
                        'report_id': {
                            'type': 'string',
                            'description': 'Report ID'
                        }
                    },
                    'required': ['workspace_id', 'report_id']
                }
            }
        ]
    }


def handle_call_tool(params: Dict) -> Dict:
    """Handle MCP tools/call request."""
    tool_name = params.get('name')
    arguments = params.get('arguments', {})

    result = handle_tool_call(tool_name, arguments)

    return {
        'content': [
            {
                'type': 'text',
                'text': json.dumps(result, indent=2)
            }
        ]
    }


def main():
    """Main MCP server loop using stdio transport."""
    logger.info("Starting Power BI MCP Server")

    for line in sys.stdin:
        try:
            message = json.loads(line)
            method = message.get('method')
            params = message.get('params', {})
            msg_id = message.get('id')

            if method == 'initialize':
                response = handle_initialize(params)
            elif method == 'tools/list':
                response = handle_list_tools(params)
            elif method == 'tools/call':
                response = handle_call_tool(params)
            else:
                response = {'error': f'Unknown method: {method}'}

            # Send response
            if msg_id is not None:
                output = {
                    'jsonrpc': '2.0',
                    'id': msg_id,
                    'result': response
                }
            else:
                output = {
                    'jsonrpc': '2.0',
                    'result': response
                }

            print(json.dumps(output), flush=True)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)


if __name__ == '__main__':
    main()
