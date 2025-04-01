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
    parser.add_argument("--list-tools", action="store_true", help="List available tools and exit")
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

# Function to display the tools
def display_tools(mcp_settings):
    # Get real tool names from FastMCP server if available
    tool_names = getattr(mcp_settings, 'registered_tool_names', [])
    if not tool_names and hasattr(mcp_settings, 'server') and hasattr(mcp_settings.server, '_tools'):
        tool_names = list(mcp_settings.server._tools.keys())
    
    # If we still don't have tool names, try to log them
    if not tool_names:
        # Looking for tools in server logs
        import re
        import glob
        log_files = glob.glob('logs/*.log')
        for log_file in sorted(log_files, reverse=True):
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    match = re.search(r'Registered tools: \[(.*?)\]', content)
                    if match:
                        tools_str = match.group(1)
                        tool_names = [t.strip("'") for t in tools_str.split(', ')]
                        break
            except Exception:
                pass
    
    # Create tools table
    tools_table = Table(title="[bold blue]Available UML-MCP Tools[/bold blue]")
    tools_table.add_column("Tool Name", style="cyan")
    tools_table.add_column("Description", style="green")
    tools_table.add_column("Parameters", style="yellow")
    
    # If we have tool names, use them
    if tool_names:
        # For each tool name, try to get its description and parameters
        for tool_name in tool_names:
            # Skip the tool_function which is not a user-facing tool
            if tool_name == 'tool_function':
                continue
                
            description = "Generate diagrams based on text descriptions"
            parameters = "No parameters info"
            
            # Set appropriate descriptions based on tool name
            if "class_diagram" in tool_name:
                description = "Generate UML class diagram from PlantUML code"
                parameters = "code: str, output_dir: str"
            elif "sequence_diagram" in tool_name:
                description = "Generate UML sequence diagram from PlantUML code"
                parameters = "code: str, output_dir: str"
            elif "activity_diagram" in tool_name:
                description = "Generate UML activity diagram from PlantUML code"
                parameters = "code: str, output_dir: str"
            elif "generate_uml" == tool_name:
                description = "Generate any UML diagram based on diagram type"
                parameters = "diagram_type: str, code: str, output_dir: str"
            elif "mermaid" in tool_name:
                description = "Generate diagrams using Mermaid syntax"
                parameters = "code: str, output_dir: str"
            elif "d2" in tool_name:
                description = "Generate diagrams using D2 syntax"
                parameters = "code: str, output_dir: str"
            elif "graphviz" in tool_name:
                description = "Generate diagrams using Graphviz DOT syntax"
                parameters = "code: str, output_dir: str"
            elif "erd" in tool_name:
                description = "Generate Entity-Relationship diagrams"
                parameters = "code: str, output_dir: str"
                
            tools_table.add_row(tool_name, description, parameters)
    else:
        # Fallback to the original approach
        if isinstance(mcp_settings.tools, dict):
            tools_to_display = [(name, info) for name, info in mcp_settings.tools.items()]
        else:
            tools_to_display = []
            for i, tool in enumerate(mcp_settings.tools):
                tool_name = getattr(tool, "__name__", f"tool_{i}")
                tools_to_display.append((tool_name, tool))
        
        for tool_name, tool_info in tools_to_display:
            description = "No description available"
            parameters = "No parameters info"
            
            if hasattr(tool_info, "__doc__") and tool_info.__doc__:
                description = tool_info.__doc__.strip().split('\n')[0]
            
            if hasattr(tool_info, "__annotations__"):
                param_list = []
                for param_name, param_type in tool_info.__annotations__.items():
                    if param_name != "return":
                        type_name = getattr(param_type, "__name__", str(param_type))
                        param_list.append(f"{param_name}: {type_name}")
                parameters = ", ".join(param_list) if param_list else "No parameters"
            
            tools_table.add_row(tool_name, description, parameters)
    
    console.print(tools_table)
    
    # Get prompt names from logs if available
    prompt_names = getattr(mcp_settings, 'registered_prompt_names', [])
    if not prompt_names:
        # Looking for prompts in server logs
        import re
        import glob
        log_files = glob.glob('logs/*.log')
        for log_file in sorted(log_files, reverse=True):
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    match = re.search(r'Registered prompts: \[(.*?)\]', content)
                    if match:
                        prompts_str = match.group(1)
                        prompt_names = [p.strip("'") for p in prompts_str.split(', ')]
                        break
            except Exception:
                pass
    
    # Create prompts table
    prompts_table = Table(title="[bold blue]Available Prompts[/bold blue]")
    prompts_table.add_column("Prompt Name", style="cyan")
    prompts_table.add_column("Description", style="green")
    
    # If we have prompt names, use them
    if prompt_names:
        for prompt_name in prompt_names:
            description = "Generate UML diagrams"
            
            if prompt_name == "class_diagram":
                description = "Create a UML class diagram showing classes, attributes, methods, and relationships"
            elif prompt_name == "sequence_diagram":
                description = "Create a UML sequence diagram showing interactions between objects over time"
            elif prompt_name == "activity_diagram":
                description = "Create a UML activity diagram showing workflows and business processes"
            
            prompts_table.add_row(prompt_name, description)
    else:
        # Fallback to original approach
        if isinstance(mcp_settings.prompts, dict):
            prompts_to_display = [(name, info) for name, info in mcp_settings.prompts.items()]
        else:
            prompts_to_display = []
            for i, prompt in enumerate(mcp_settings.prompts):
                prompt_name = getattr(prompt, "name", f"prompt_{i}")
                prompts_to_display.append((prompt_name, prompt))
        
        for prompt_name, prompt_info in prompts_to_display:
            description = "No description available"
            if hasattr(prompt_info, "description"):
                description = prompt_info.description
            elif hasattr(prompt_info, "__doc__") and prompt_info.__doc__:
                description = prompt_info.__doc__.strip().split('\n')[0]
            
            prompts_table.add_row(prompt_name, description)
    
    console.print(prompts_table)
    
    # Get resource names from logs if available
    resource_names = []
    import re
    import glob
    log_files = glob.glob('logs/*.log')
    for log_file in sorted(log_files, reverse=True):
        try:
            with open(log_file, 'r') as f:
                content = f.read()
                match = re.search(r'Registered resources: \[(.*?)\]', content)
                if match:
                    resources_str = match.group(1)
                    resource_names = [r.strip("'") for r in resources_str.split(', ')]
                    break
        except Exception:
            pass
    
    # Display resources
    if resource_names:
        resources_table = Table(title="[bold blue]Available Resources[/bold blue]")
        resources_table.add_column("Resource URI", style="cyan")
        resources_table.add_column("Description", style="green")
        
        resource_descriptions = {
            "uml://types": "List of available UML diagram types",
            "uml://templates": "Templates for creating UML diagrams",
            "uml://examples": "Example UML diagrams for reference",
            "uml://formats": "Supported output formats for diagrams",
            "uml://server-info": "Information about the UML-MCP server"
        }
        
        for resource_name in resource_names:
            description = resource_descriptions.get(resource_name, "Resource information")
            resources_table.add_row(resource_name, description)
        
        console.print(resources_table)

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
        
        # Display tools list if requested
        list_tools = args.list_tools or os.environ.get("LIST_TOOLS", "").lower() == "true"
        if list_tools:
            display_tools(MCP_SETTINGS)
        
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
