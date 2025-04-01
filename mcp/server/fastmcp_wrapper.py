"""
Wrapper for FastMCP server to ensure compatibility
"""

import logging
import sys
import json
from typing import Any, Callable, Dict, List, Optional, Union

try:
    from fastmcp import FastMCP, Context
except ImportError:
    # Mock implementation for testing
    class Context:
        def __init__(self):
            self.data = {}
            self.session_id = None
            self.request = None
            self.response = None
            
        def get(self, key, default=None):
            """Get a value from the context data dictionary"""
            return self.data.get(key, default)
            
        def set(self, key, value):
            """Set a value in the context data dictionary"""
            self.data[key] = value
            return self
            
        def update(self, data_dict):
            """Update the context data dictionary with another dictionary"""
            if data_dict and isinstance(data_dict, dict):
                self.data.update(data_dict)
            return self
    
    class FastMCP:
        def __init__(self, name: str):
            self.name = name
            self._tools = {}
            self._prompts = {}
            self._resources = {}
            self.logger = logging.getLogger(__name__)
            self.logger.warning("Using mock FastMCP implementation")
        
        def tool(self):
            def decorator(func):
                self._tools[func.__name__] = func
                return func
            return decorator
            
        def prompt(self, prompt_name: str = None):
            def decorator(func):
                name = prompt_name or func.__name__
                self._prompts[name] = func
                return func
            return decorator
            
        def resource(self, path: str):
            def decorator(func):
                self._resources[path] = func
                return func
            return decorator
                
        def run(self, transport: str = 'stdio', host: str = None, port: int = None):
            """Run the MCP server with the specified transport.
            
            Args:
                transport (str): Transport protocol to use ('stdio' or 'http')
                host (str, optional): Host to bind to when using HTTP transport
                port (int, optional): Port to bind to when using HTTP transport
            
            In stdio mode, the server:
            1. Logs startup info
            2. Waits for JSON input on stdin
            3. Processes commands and returns results on stdout
            4. Continues until EOF or shutdown command
            
            In http mode, the server:
            1. Creates a simple HTTP server
            2. Listens for requests at the specified host and port
            3. Processes requests and returns JSON responses
            """
            self.logger.info(f"Mock FastMCP server '{self.name}' running with transport '{transport}'")
            self.logger.info(f"Registered tools: {list(self._tools.keys())}")
            self.logger.info(f"Registered prompts: {list(self._prompts.keys())}")
            self.logger.info(f"Registered resources: {list(self._resources.keys())}")
            
            if transport == 'stdio':
                self._run_stdio()
            elif transport == 'http':
                if host is None or port is None:
                    self.logger.error("HTTP transport requires host and port")
                    return
                self._run_http(host, port)
            else:
                self.logger.error(f"Unsupported transport: {transport}")
                return
                
        def _run_stdio(self):
            """Run the server in stdio mode"""
            try:
                while True:
                    # Read JSON input from stdin
                    try:
                        line = sys.stdin.readline()
                        if not line:  # EOF
                            break
                            
                        request = json.loads(line)
                        
                        # Process the request
                        response = self._handle_request(request)
                        
                        # Send response
                        print(json.dumps(response))
                        sys.stdout.flush()
                        
                    except json.JSONDecodeError:
                        self.logger.error("Invalid JSON input")
                        continue
                        
            except KeyboardInterrupt:
                self.logger.info("Server stopped by user")
            except Exception as e:
                self.logger.error(f"Server error: {str(e)}")
                raise
                
        def _run_http(self, host: str, port: int):
            """Run the server in HTTP mode
            
            Args:
                host (str): Host to bind to
                port (int): Port to bind to
            """
            try:
                import http.server
                import socketserver
                from urllib.parse import urlparse, parse_qs
                
                self.logger.info(f"Starting HTTP server on {host}:{port}")
                
                class MCPHandler(http.server.BaseHTTPRequestHandler):
                    def do_POST(self):
                        try:
                            content_length = int(self.headers['Content-Length'])
                            post_data = self.rfile.read(content_length)
                            request = json.loads(post_data.decode('utf-8'))
                            
                            # Process the request
                            response = self._handle_request(request)
                            
                            # Send response
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps(response).encode('utf-8'))
                            
                        except json.JSONDecodeError:
                            self.send_response(400)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode('utf-8'))
                        except Exception as e:
                            self.send_response(500)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
                    
                    # Make the handle_request method accessible to the handler
                    def _handle_request(self, request):
                        outer_self = self.server.mcp_server
                        return outer_self._handle_request(request)
                
                # Create the HTTP server
                httpd = socketserver.TCPServer((host, port), MCPHandler)
                httpd.mcp_server = self  # Make the MCP server accessible to the handler
                
                # Start the server
                self.logger.info(f"HTTP server running on http://{host}:{port}/")
                httpd.serve_forever()
                
            except KeyboardInterrupt:
                self.logger.info("HTTP server stopped by user")
            except Exception as e:
                self.logger.error(f"HTTP server error: {str(e)}")
                raise
                
        def _handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
            """Handle an MCP request and return the response."""
            try:
                command = request.get('command')
                if not command:
                    return {'error': 'Missing command'}
                    
                if command == 'tool':
                    tool_name = request.get('tool')
                    if not tool_name or tool_name not in self._tools:
                        return {'error': f'Unknown tool: {tool_name}'}
                    
                    tool = self._tools[tool_name]
                    args = request.get('args', {})
                    result = tool(**args)
                    return {'result': result}
                    
                elif command == 'prompt':
                    prompt_name = request.get('prompt')
                    if not prompt_name or prompt_name not in self._prompts:
                        return {'error': f'Unknown prompt: {prompt_name}'}
                    
                    prompt = self._prompts[prompt_name]
                    result = prompt()
                    return {'result': result}
                    
                elif command == 'resource':
                    path = request.get('path')
                    if not path or path not in self._resources:
                        return {'error': f'Unknown resource: {path}'}
                    
                    resource = self._resources[path]
                    result = resource()
                    return {'result': result}
                    
                elif command == 'shutdown':
                    self.logger.info("Shutdown requested")
                    sys.exit(0)
                    
                else:
                    return {'error': f'Unknown command: {command}'}
                    
            except Exception as e:
                self.logger.error(f"Error handling request: {str(e)}")
                return {'error': str(e)}

# Export the required classes
__all__ = ["FastMCP", "Context"]
