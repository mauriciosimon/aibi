#!/usr/bin/env python3
"""
Power BI MCP HTTP Server - Wraps powerbi_mcp_server.py for HTTP access

This server provides HTTP endpoints that communicate with the Power BI MCP server
via stdio, making it accessible to the intelligent chat backend.
"""

import os
import json
import subprocess
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
CORS(app)

# Configuration
MCP_API_KEY = os.getenv('MCP_API_KEY', 'odoo-mcp-2025')
PORT = int(os.getenv('POWERBI_MCP_PORT', 5003))

# Power BI MCP subprocess
mcp_process = None
mcp_lock = threading.Lock()
message_id_counter = 0


def start_mcp_server():
    """Start the Power BI MCP server as a subprocess"""
    global mcp_process
    try:
        logger.info("Starting Power BI MCP server subprocess...")
        mcp_process = subprocess.Popen(
            ['python3', 'powerbi_mcp_server.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        logger.info(f"Power BI MCP server started with PID {mcp_process.pid}")
    except Exception as e:
        logger.error(f"Failed to start Power BI MCP server: {str(e)}")
        raise


def call_mcp_server(method, params=None):
    """Call the Power BI MCP server via stdio"""
    global message_id_counter

    with mcp_lock:
        message_id_counter += 1
        msg_id = message_id_counter

        request_message = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": method,
            "params": params or {}
        }

        try:
            # Send request
            request_json = json.dumps(request_message) + '\n'
            logger.debug(f"Sending to MCP: {request_json.strip()}")
            mcp_process.stdin.write(request_json)
            mcp_process.stdin.flush()

            # Read response
            response_line = mcp_process.stdout.readline()
            logger.debug(f"Received from MCP: {response_line.strip()}")

            if not response_line:
                raise Exception("No response from MCP server")

            response = json.loads(response_line)

            if 'error' in response:
                raise Exception(response['error'].get('message', 'Unknown MCP error'))

            return response.get('result')

        except Exception as e:
            logger.error(f"Error calling MCP server: {str(e)}")
            raise


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Power BI MCP HTTP Server',
        'mcp_process_alive': mcp_process is not None and mcp_process.poll() is None
    })


@app.route('/mcp/tools', methods=['POST'])
def list_tools():
    """List all available Power BI MCP tools"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '')

        if api_key != MCP_API_KEY:
            return jsonify({'success': False, 'error': 'Invalid API key'}), 401

        # Call MCP server to list tools
        result = call_mcp_server('tools/list')

        if result and 'tools' in result:
            return jsonify({
                'success': True,
                'data': result['tools']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get tools from MCP server'
            }), 500

    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/mcp/tool/call', methods=['POST'])
def call_tool():
    """Execute a Power BI MCP tool"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '')
        tool_name = data.get('name', '')
        arguments = data.get('arguments', {})

        if api_key != MCP_API_KEY:
            return jsonify({'success': False, 'error': 'Invalid API key'}), 401

        if not tool_name:
            return jsonify({'success': False, 'error': 'Tool name required'}), 400

        logger.info(f"Calling Power BI MCP tool: {tool_name} with args: {arguments}")

        # Call MCP server
        result = call_mcp_server('tools/call', {
            'name': tool_name,
            'arguments': arguments
        })

        if result:
            # Extract content from MCP response
            content = result.get('content', [])
            if content and len(content) > 0:
                tool_result = content[0]
                if tool_result.get('type') == 'text':
                    # Parse the JSON result
                    try:
                        data_result = json.loads(tool_result.get('text', '{}'))
                        return jsonify({
                            'success': True,
                            'data': data_result
                        })
                    except json.JSONDecodeError:
                        return jsonify({
                            'success': True,
                            'data': {'result': tool_result.get('text', '')}
                        })
                else:
                    return jsonify({
                        'success': True,
                        'data': tool_result
                    })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Empty response from MCP server'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'No result from MCP server'
            }), 500

    except Exception as e:
        logger.error(f"Error calling tool: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


def shutdown_mcp_server():
    """Shutdown the MCP server subprocess"""
    global mcp_process
    if mcp_process:
        logger.info("Shutting down Power BI MCP server...")
        try:
            mcp_process.terminate()
            mcp_process.wait(timeout=5)
        except:
            mcp_process.kill()
        logger.info("Power BI MCP server shut down")


if __name__ == '__main__':
    try:
        # Start MCP server
        start_mcp_server()

        # Initialize MCP server
        logger.info("Initializing Power BI MCP server...")
        init_result = call_mcp_server('initialize', {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {
                'name': 'powerbi-mcp-http-server',
                'version': '1.0.0'
            }
        })
        logger.info(f"Power BI MCP server initialized: {init_result.get('serverInfo', {})}")

        logger.info("=" * 60)
        logger.info("Power BI MCP HTTP Server")
        logger.info("=" * 60)
        logger.info(f"Server starting on http://localhost:{PORT}")
        logger.info("=" * 60)

        # Start Flask server
        app.run(
            host='0.0.0.0',
            port=PORT,
            debug=False
        )

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        shutdown_mcp_server()
