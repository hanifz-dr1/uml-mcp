"""
Tests for the Kroki API integration.
"""
import pytest
from unittest.mock import patch, MagicMock
import base64
import zlib
import httpx

from kroki.kroki import Kroki, KrokiHTTPError, KrokiConnectionError

@pytest.fixture
def mock_httpx_client():
    """Mock the httpx client for testing."""
    with patch('httpx.Client') as mock_client:
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<svg>test content</svg>"
        mock_response.raise_for_status = MagicMock()
        
        # Make client.get return the mock response
        client_instance = mock_client.return_value
        client_instance.get.return_value = mock_response
        
        yield client_instance

def test_kroki_initialization():
    """Test Kroki client initialization."""
    # Test with default URL
    client = Kroki()
    assert client.base_url == "https://kroki.io"
    
    # Test with custom URL
    custom_url = "http://custom-kroki.example.com"
    client = Kroki(base_url=custom_url)
    assert client.base_url == custom_url

def test_get_url():
    """Test URL generation for a diagram."""
    client = Kroki()
    diagram_type = "plantuml"
    diagram_text = "@startuml\nclass Test\n@enduml"
    output_format = "svg"
    
    url = client.get_url(diagram_type, diagram_text, output_format)
    
    # URL should contain the encoded diagram
    assert url.startswith(f"https://kroki.io/{diagram_type}/{output_format}/")
    
    # Verify encoding by manually encoding the diagram text
    encoded = client.deflate_and_encode(diagram_text)
    assert encoded in url

def test_get_playground_url():
    """Test playground URL generation."""
    client = Kroki()
    
    # Test PlantUML playground
    plantuml_url = client.get_playground_url("plantuml", "@startuml\nclass Test\n@enduml")
    assert plantuml_url is not None
    assert plantuml_url.startswith("https://www.plantuml.com/plantuml/uml/")
    
    # Test Mermaid playground
    mermaid_url = client.get_playground_url("mermaid", "graph TD;\nA-->B;")
    assert mermaid_url is not None
    assert mermaid_url.startswith("https://mermaid.live/edit#")
    
    # Test non-existent playground
    nonexistent_url = client.get_playground_url("nonexistent", "test")
    assert nonexistent_url is None

def test_render_diagram_success(mock_httpx_client):
    """Test successful diagram rendering."""
    client = Kroki()
    
    # Test rendering
    result = client.render_diagram("plantuml", "@startuml\nclass Test\n@enduml", "svg")
    
    # Verify result and mock calls
    assert result == b"<svg>test content</svg>"
    mock_httpx_client.get.assert_called_once()
    url_arg = mock_httpx_client.get.call_args[0][0]
    assert url_arg.startswith("https://kroki.io/plantuml/svg/")

def test_render_diagram_http_error(mock_httpx_client):
    """Test HTTP error handling."""
    # Setup mock to raise HTTP error
    mock_response = mock_httpx_client.get.return_value
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP Error", request=httpx.Request("GET", "https://kroki.io"), response=mock_response
    )
    
    client = Kroki()
    
    # Test error handling
    with pytest.raises(KrokiHTTPError):
        client.render_diagram("plantuml", "@startuml\nclass Test\n@enduml", "svg")

def test_render_diagram_connection_error(mock_httpx_client):
    """Test connection error handling."""
    # Setup mock to raise connection error
    mock_httpx_client.get.side_effect = httpx.RequestError("Connection error", request=None)
    
    client = Kroki()
    
    # Test error handling
    with pytest.raises(KrokiConnectionError):
        client.render_diagram("plantuml", "@startuml\nclass Test\n@enduml", "svg")

def test_generate_diagram(mock_httpx_client):
    """Test the generate_diagram method."""
    client = Kroki()
    
    # Test diagram generation
    result = client.generate_diagram("plantuml", "@startuml\nclass Test\n@enduml", "svg")
    
    # Verify result structure
    assert "url" in result
    assert "content" in result
    assert "playground" in result
    assert result["content"] == b"<svg>test content</svg>"
    
    # Verify URL format
    assert result["url"].startswith("https://kroki.io/plantuml/svg/")
    
    # Verify playground URL
    assert result["playground"].startswith("https://www.plantuml.com/plantuml/uml/")

def test_deflate_and_encode():
    """Test the deflate_and_encode method."""
    client = Kroki()
    text = "test text"
    
    encoded = client.deflate_and_encode(text)
    
    # Verify the result is non-empty and doesn't contain invalid characters
    assert encoded
    assert "+" not in encoded  # + should be replaced with -
    assert "/" not in encoded  # / should be replaced with _
    
    # Manual compression and encoding to verify
    compress_obj = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=15,
                                   memLevel=8, strategy=zlib.Z_DEFAULT_STRATEGY)
    compressed_data = compress_obj.compress(text.encode('utf-8'))
    compressed_data += compress_obj.flush()
    
    expected = base64.urlsafe_b64encode(compressed_data).decode('ascii')
    expected = expected.replace('+', '-').replace('/', '_')
    
    assert encoded == expected

def test_unsupported_diagram_type():
    """Test error handling for unsupported diagram types."""
    client = Kroki()
    
    with pytest.raises(ValueError, match="Unsupported diagram type"):
        client.get_url("nonexistent_type", "test code", "svg")

def test_unsupported_output_format():
    """Test error handling for unsupported output formats."""
    client = Kroki()
    
    with pytest.raises(ValueError, match="Unsupported output format"):
        client.get_url("plantuml", "test code", "nonexistent_format")