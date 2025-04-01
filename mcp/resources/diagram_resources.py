"""
MCP resources for diagram information
"""
import logging
from typing import Dict, List, Any

from mcp.server.fastmcp_wrapper import FastMCP
from ..core.config import MCP_SETTINGS
from kroki.kroki_templates import DiagramTemplates, DiagramExamples

logger = logging.getLogger(__name__)

def register_diagram_resources(server: FastMCP):
    """
    Register diagram resources with the MCP server
    
    Args:
        server: The MCP server instance
    """
    logger.info("Registering diagram resources")
    
    @server.resource("uml://types")
    def get_diagram_types():
        """Get available diagram types"""
        types = {}
        for name, config in MCP_SETTINGS.diagram_types.items():
            types[name] = {
                "backend": config.backend,
                "description": config.description,
                "formats": config.formats
            }
        return types
    
    @server.resource("uml://templates")
    def get_diagram_templates():
        """Get diagram templates for different diagram types"""
        templates = {}
        for name in MCP_SETTINGS.diagram_types:
            templates[name] = DiagramTemplates.get_template(name)
        return templates
    
    @server.resource("uml://examples")
    def get_diagram_examples():
        """Get diagram examples for different diagram types"""
        examples = {}
        for name in MCP_SETTINGS.diagram_types:
            examples[name] = DiagramExamples.get_example(name)
        return examples
    
    @server.resource("uml://formats")
    def get_output_formats():
        """Get supported output formats for each diagram type"""
        formats = {}
        for name, config in MCP_SETTINGS.diagram_types.items():
            formats[name] = config.formats
        return formats
    
    @server.resource("uml://server-info")
    def get_server_info():
        """Get MCP server information"""
        return {
            "server_name": MCP_SETTINGS.server_name,
            "version": MCP_SETTINGS.version,
            "description": MCP_SETTINGS.description,
            "tools": MCP_SETTINGS.tools,
            "prompts": MCP_SETTINGS.prompts,
            "kroki_server": MCP_SETTINGS.kroki_server,
            "plantuml_server": MCP_SETTINGS.plantuml_server
        }
    
    logger.info("Diagram resources registered successfully")
