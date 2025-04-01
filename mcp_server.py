#!/usr/bin/env python3
"""
UML-MCP-Server: UML diagram generation server with MCP interface

This module provides the main entry point for the MCP server that generates UML
diagrams through the Model Context Protocol (MCP).
"""

import os
import sys
import logging
import argparse
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

# Configure rich console
console = Console()

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="UML-MCP Diagram Generation Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--transport", type=str, choices=["stdio", "http"], default="stdio", 
                        help="Transport protocol (default: stdio)")
    return parser.parse_args()

# Configure logging based on arguments
def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger(__name__)

# Centralized error handling for imports
def safe_import(module_name, display_name=None):
    try:
        return __import__(module_name)
    except ImportError as e:
        display_name = display_name or module_name
        console.print(f"[bold red]Error importing {display_name}:[/bold red] {str(e)}")
        return None

def main():
    # Parse arguments and set up logging
    args = parse_args()
    logger = setup_logging(args.debug)
    
    logger.info(f"Starting UML-MCP Server with transport: {args.transport}")
    
    # Check required modules
    required_modules = {
        "mcp.server": "MCP Server",
        "kroki.kroki": "Kroki",
        "plantuml": "PlantUML",
        "mermaid.mermaid": "Mermaid",
        "D2.run_d2": "D2"
    }
    
    missing_modules = []
    for module_name, display_name in required_modules.items():
        if not safe_import(module_name, display_name):
            missing_modules.append(display_name)

    if missing_modules:
        console.print(f"[bold red]Error:[/bold red] Missing required modules: {', '.join(missing_modules)}")
        console.print("Please ensure all project components are correctly installed.")
        sys.exit(1)

    # Import core server
    try:
        from mcp.core.server import create_mcp_server, get_mcp_server
        from mcp.core.config import MCP_SETTINGS
        
        # Update settings from command line args if applicable
        if hasattr(MCP_SETTINGS, 'update_from_args'):
            MCP_SETTINGS.update_from_args(args)
        
        # Initialize the server which will register tools and prompts
        server = get_mcp_server()
        
        # Display server info (after tools and prompts are registered)
        console.print(Panel(f"[bold green]UML-MCP Server v{MCP_SETTINGS.version}[/bold green]"))
        
        # Create a table for server info
        table = Table(title="Server Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Server Name", MCP_SETTINGS.server_name)
        table.add_row("Transport", args.transport)
        table.add_row("Available Tools", str(len(MCP_SETTINGS.tools)))
        table.add_row("Available Prompts", str(len(MCP_SETTINGS.prompts)))
        if args.transport == "http":
            table.add_row("Host", args.host)
            table.add_row("Port", str(args.port))
        
        console.print(table)
        
        # Start MCP server
        from mcp.core.server import start_server
        start_server(transport=args.transport, host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.critical(f"Server error: {str(e)}", exc_info=True)
    finally:
        logger.info("Server shut down")

if __name__ == "__main__":
    main()
