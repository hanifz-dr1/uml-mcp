# Configuration

UML-MCP can be configured using environment variables and configuration files.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_OUTPUT_DIR` | Directory to save generated diagrams | `./output` |
| `KROKI_SERVER` | URL of the Kroki server | `https://kroki.io` |
| `PLANTUML_SERVER` | URL of the PlantUML server | `http://plantuml-server:8080` |
| `USE_LOCAL_KROKI` | Use local Kroki server (true/false) | `false` |
| `USE_LOCAL_PLANTUML` | Use local PlantUML server (true/false) | `false` |

## IDE Configuration

### Cursor

Cursor configuration is stored in:

- Windows: `%APPDATA%\Cursor\config.json`
- macOS: `~/Library/Application Support/Cursor/config.json`
- Linux: `~/.config/Cursor/config.json`

Example configuration:

```json
{
  "mcpServers": {
    "UML-MCP-Server": {
      "command": "python",
      "args": ["/path/to/uml-mcp/mcp_server.py"],
      "output_dir": "/path/to/output"
    }
  }
}
```

### Claude Desktop

Claude Desktop configuration is stored in the app settings:

Example configuration:

```json
{
  "mcpServers": {
    "UML-MCP-Server": {
      "command": "python",
      "args": ["/path/to/uml-mcp/mcp_server.py"],
      "output_dir": "/path/to/output"
    }
  }
}
```

## Advanced Configuration

### Custom Templates

You can customize diagram templates by modifying the templates in the `kroki/kroki_templates.py` file.

### Output Formats

Each diagram type supports specific output formats:

| Diagram Type | Supported Formats |
|--------------|-------------------|
| PlantUML     | png, svg, pdf, txt |
| Mermaid      | svg, png |
| D2           | svg, png |
| Graphviz     | png, svg, pdf, jpeg |

You can specify the output format when generating diagrams through the MCP tools.
