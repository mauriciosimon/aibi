#!/bin/bash

# Startup script for Railway deployment
# Determines which server to start based on SERVICE_NAME environment variable

if [ "$SERVICE_NAME" = "mcp-odoo" ]; then
    echo "Starting MCP Server..."
    exec gunicorn standalone_mcp_server:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2
else
    echo "Starting Intelligent Chat Server..."
    exec gunicorn intelligent_chat_server:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2
fi
