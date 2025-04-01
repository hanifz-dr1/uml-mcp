"""
Core MCP server implementation
"""

import os
import logging
import json
import datetime
from typing import Dict, Optional, Any, List

# Import MCP server framework - try to use the wrapper
try:
    from ..server.fastmcp_wrapper import FastMCP, Context
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP, Context
    except ImportError:
        from fastmcp import FastMCP, Context

# Import configuration
from .config import MCP_SETTINGS
from .utils import setup_logging

# Import tools and resources
from ..tools.diagram_tools import register_diagram_tools
from ..resources.diagram_resources import register_diagram_resources
from ..prompts.diagram_prompts import register_diagram_prompts

# Get logger
logger = logging.getLogger(__name__)

def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all tools and resources.
    
    Returns:
        Configured FastMCP server instance
    """
    # Initialize MCP server
    logger.info(f"Creating MCP server: {MCP_SETTINGS.server_name}")
    server = FastMCP(MCP_SETTINGS.server_name)
    
    # Register all tools, resources, and prompts
    tool_names = register_diagram_tools(server)
    resource_names = register_diagram_resources(server)
    prompt_names = register_diagram_prompts(server)
    
    # Update settings with registered tools and prompts
    MCP_SETTINGS.tools = tool_names
    MCP_SETTINGS.prompts = prompt_names
    MCP_SETTINGS.resources = resource_names
    
    logger.info(f"MCP server created with {len(MCP_SETTINGS.tools)} tools, {len(MCP_SETTINGS.prompts)} prompts, and {len(MCP_SETTINGS.resources)} resources")
    return server

# Create a singleton MCP server instance
_mcp_server = None

def get_mcp_server() -> FastMCP:
    """Get the singleton MCP server instance.
    
    Returns:
        FastMCP server instance
    """
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = create_mcp_server()
    return _mcp_server

def start_server(transport='stdio', host=None, port=None):
    """Start the MCP server
    
    Args:
        transport (str): Transport protocol to use ('stdio' or 'http')
        host (str, optional): Host to bind to when using HTTP transport
        port (int, optional): Port to bind to when using HTTP transport
    """
    # Get the server
    server = get_mcp_server()
    
    # Start the server
    logger.info(f"Starting MCP server with transport: {transport}")
    
    # Log the registered tools, prompts, and resources
    logger.info(f"Registered tools: {MCP_SETTINGS.tools}")
    logger.info(f"Registered prompts: {MCP_SETTINGS.prompts}")
    logger.info(f"Registered resources: {MCP_SETTINGS.resources}")
    
    # Currently only stdio is supported in the mock implementation
    # This can be expanded when http transport is implemented
    if transport != 'stdio' and hasattr(server, '_transport_http'):
        logger.info(f"Starting HTTP server on {host}:{port}")
        server.run(transport='http', host=host, port=port)
    else:
        if transport != 'stdio':
            logger.warning(f"Transport '{transport}' not supported, falling back to stdio")
        server.run(transport='stdio')
