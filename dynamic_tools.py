"""
Dynamic Tool Generator - Self-Improving MCP Server
===================================================

This module allows the system to generate and hot-reload new tools dynamically
based on user requests, without requiring redeployment.
"""

import os
import importlib
import sys
import json
from datetime import datetime


# Store dynamically generated tools
DYNAMIC_TOOLS_REGISTRY = {}
DYNAMIC_FUNCTIONS = {}


def register_dynamic_tool(tool_definition, function_code):
    """
    Register a new tool dynamically

    Args:
        tool_definition: Dict with tool metadata (name, description, input_schema)
        function_code: String containing the Python function implementation
    """
    tool_name = tool_definition['name']

    # Store tool definition
    DYNAMIC_TOOLS_REGISTRY[tool_name] = tool_definition

    # Execute function code and store it
    exec_globals = {
        'datetime': datetime,
        'odoo': None,  # Will be passed when called
        'logger': None  # Will be passed when called
    }
    exec(function_code, exec_globals)

    # Find the function that was defined
    function_name = tool_name  # Assume function name matches tool name
    if function_name in exec_globals:
        DYNAMIC_FUNCTIONS[tool_name] = exec_globals[function_name]

    return True


def get_all_dynamic_tools():
    """Get all registered dynamic tools"""
    return list(DYNAMIC_TOOLS_REGISTRY.values())


def call_dynamic_tool(tool_name, odoo, arguments, logger):
    """Execute a dynamic tool"""
    if tool_name not in DYNAMIC_FUNCTIONS:
        raise ValueError(f"Dynamic tool '{tool_name}' not found")

    function = DYNAMIC_FUNCTIONS[tool_name]

    # Call with odoo connection and arguments
    # Most functions expect (odoo, args) signature
    try:
        result = function(odoo, arguments)
        return result
    except Exception as e:
        logger.error(f"Error executing dynamic tool {tool_name}: {str(e)}")
        return {'error': str(e)}


def save_dynamic_tool_to_file(tool_name, tool_definition, function_code):
    """
    Save a dynamic tool to a file for persistence across restarts

    This creates a Python file in the dynamic_tools directory
    """
    tools_dir = os.path.join(os.path.dirname(__file__), 'dynamic_tools')
    os.makedirs(tools_dir, exist_ok=True)

    file_path = os.path.join(tools_dir, f"{tool_name}.py")

    # Convert tool definition to a properly formatted string
    tool_def_str = json.dumps(tool_definition, indent=4)

    content = f'''"""
Dynamically Generated Tool: {tool_name}
Generated: {datetime.now().isoformat()}
"""

import json
from datetime import datetime, timedelta

# Tool Definition
TOOL_DEFINITION = {tool_def_str}

# Tool Implementation
{function_code}
'''

    with open(file_path, 'w') as f:
        f.write(content)

    return file_path


def load_persisted_tools():
    """Load all persisted dynamic tools from files"""
    tools_dir = os.path.join(os.path.dirname(__file__), 'dynamic_tools')

    if not os.path.exists(tools_dir):
        return

    for filename in os.listdir(tools_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            file_path = os.path.join(tools_dir, filename)

            # Read the file
            with open(file_path, 'r') as f:
                content = f.read()

            # Execute to get tool definition and function
            exec_globals = {}
            exec(content, exec_globals)

            if 'TOOL_DEFINITION' in exec_globals:
                tool_def = exec_globals['TOOL_DEFINITION']
                tool_name = tool_def['name']

                # Extract function code (everything after the tool definition)
                func_start = content.find('# Tool Implementation')
                if func_start > 0:
                    function_code = content[func_start + len('# Tool Implementation'):].strip()
                    register_dynamic_tool(tool_def, function_code)


# Load persisted tools on import
load_persisted_tools()
