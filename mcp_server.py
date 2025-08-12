#!/usr/bin/env python3
"""
UML Diagram Generator - Simplified MCP Server

A minimal MCP server for generating UML diagrams using FastMCP, Typer, and Rich.
"""

import os
import zlib
import base64
from typing import Dict, Any

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, PromptMessage, GetPromptResult

# Configuration: Use PlantUML server (can be overridden with env var)
# Check for local PlantUML server first, fallback to public server
USE_LOCAL_PLANTUML = os.environ.get("USE_LOCAL_PLANTUML", "true").lower() == "true"
LOCAL_PLANTUML_SERVER = "http://localhost:8080"  # Docker PlantUML server
PUBLIC_PLANTUML_SERVER = "http://www.plantuml.com/plantuml"

# Use local server if enabled, otherwise use environment variable or public server
if USE_LOCAL_PLANTUML:
    PLANTUML_SERVER = os.environ.get("PLANTUML_SERVER", LOCAL_PLANTUML_SERVER)
else:
    PLANTUML_SERVER = os.environ.get("PLANTUML_SERVER", PUBLIC_PLANTUML_SERVER)


def encode_plantuml(text: str) -> str:
    """Encode PlantUML text using zlib and base64."""
    compressed = zlib.compress(text.encode("utf-8"))
    # Use full compressed data and add ~1 prefix for HUFFMAN encoding
    encoded = base64.urlsafe_b64encode(compressed[2:-4]).decode("utf-8").rstrip("=")
    return encoded


def generate_diagram(code: str, fmt: str = "svg") -> Dict[str, Any]:
    """Generate a diagram URL using the PlantUML server."""
    encoded = encode_plantuml(code)
    # Add ~1 prefix to indicate HUFFMAN encoding
    url = f"{PLANTUML_SERVER}/{fmt}/~1{encoded}"
    return {"url": url, "code": code}


# Create a FastMCP server instance
server = FastMCP("UML Diagram Generator")


# Register an MCP tool to generate a UML diagram
@server.tool(name="generate_uml", description="Generate a UML diagram using PlantUML")
def generate_uml(diagram_type: str, code: str) -> Dict[str, Any]:
    # For simplicity, the diagram_type parameter is not used.
    return generate_diagram(code)


# Register an MCP resource to expose server info
@server.resource("uml://info")
def get_info() -> Dict[str, Any]:
    return {
        "server": "UML Diagram Generator",
        "version": "1.0",
        "plantuml_server": PLANTUML_SERVER,
        "mode": "local" if USE_LOCAL_PLANTUML else "remote"
    }


# Register an MCP prompt with a simple template
@server.prompt(name="simple_prompt", description="Simple prompt for diagram generation")
def simple_prompt(context: Dict[str, Any]) -> GetPromptResult:
    code = context.get("code", "@startuml\nAlice -> Bob: Hello\n@enduml")
    return GetPromptResult(
        description="Simple prompt for UML diagram",
        messages=[PromptMessage(role="user", content=TextContent(text=code))]
    )


# Set up the CLI using Typer and Rich
cli = typer.Typer()


@cli.command()
def run():
    """Run the MCP server using stdio transport."""
    console = Console()
    console.print("[bold green]Starting UML Diagram Generator MCP Server...[/bold green]")
    server.run()


@cli.command()
def info():
    """Display server information."""
    console = Console()
    table = Table("Property", "Value")
    table.add_row("Server", "UML Diagram Generator")
    table.add_row("Version", "1.0")
    table.add_row("PlantUML Server", PLANTUML_SERVER)
    table.add_row("Mode", "Local" if USE_LOCAL_PLANTUML else "Remote")
    console.print(table)


if __name__ == "__main__":
    cli()
