# Canvus Python API Client

A comprehensive Python client library for interacting with the Canvus API. This library provides full access to all Canvus API endpoints with type-safe operations, comprehensive error handling, and extensive testing.

## 🚀 Features

### ✅ Complete API Coverage
- **All 100+ API endpoints** implemented and tested
- **Type-safe operations** with Pydantic models
- **Comprehensive error handling** with custom exceptions
- **Async/await support** for all operations
- **File upload/download** capabilities
- **Real-time subscriptions** for live updates

### 🔐 Authentication & Security
- **Token-based authentication** with automatic header management
- **SSL verification** support (configurable for test environments)
- **Secure credential handling** via environment variables
- **Session management** with automatic token refresh

### 📊 Data Management
- **Full CRUD operations** for all resources
- **Batch operations** for efficient data handling
- **File uploads** (images, videos, PDFs, documents)
- **Binary data handling** for assets and mipmaps
- **Streaming responses** for large datasets

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/jaypaulb/CanvusPythonAPI.git
cd CanvusPythonAPI

# Install dependencies
pip install -r requirements.txt

# Or install directly from GitHub
pip install git+https://github.com/jaypaulb/CanvusPythonAPI.git
```

## 🏗️ Architecture

```
canvus_api/
├── __init__.py          # Main client export
├── client.py            # Main CanvusClient class
├── models.py            # Pydantic models for all resources
├── exceptions.py        # Custom exception hierarchy
└── utils/               # Utility functions (if needed)
```

## 🚀 Quick Start

```python
import asyncio
from canvus_api import CanvusClient

async def main():
    # Initialize client
    client = CanvusClient(
        base_url="https://your-canvus-server.com/api/v1",
        api_key="your-api-key"
    )
    
    # Get server information
    server_info = await client.get_server_info()
    print(f"Server version: {server_info.version}")
    
    # List canvases
    canvases = await client.list_canvases()
    for canvas in canvases:
        print(f"Canvas: {canvas.name}")
    
    # Create a new canvas
    new_canvas = await client.create_canvas({
        "name": "My Project",
        "description": "A new project canvas"
    })
    
    # Add a note widget
    note = await client.create_note(new_canvas.id, {
        "content": "Hello, Canvus!",
        "x": 100,
        "y": 100,
        "width": 200,
        "height": 100
    })

# Run the example
asyncio.run(main())
```

## 📚 API Reference

### Server Management
```python
# Server information and configuration
await client.get_server_info()
await client.get_server_config()
await client.update_server_config(settings)
await client.send_test_email()
```

### Canvas Operations
```python
# Canvas CRUD operations
await client.list_canvases()
await client.get_canvas(canvas_id)
await client.create_canvas(payload)
await client.update_canvas(canvas_id, payload)
await client.delete_canvas(canvas_id)

# Canvas-specific operations
await client.get_canvas_preview(canvas_id)
await client.get_canvas_background(canvas_id)
await client.set_canvas_background(canvas_id, payload)
await client.set_canvas_background_image(canvas_id, file_path)
await client.get_color_presets(canvas_id)
await client.update_color_presets(canvas_id, payload)
```

### Folder Management
```python
# Folder operations
await client.list_folders()
await client.get_folder(folder_id)
await client.create_folder(payload)
await client.update_folder(folder_id, payload)
await client.delete_folder(folder_id)
await client.copy_folder(folder_id, payload)
await client.delete_folder_children(folder_id)
```

### Widget Management
```python
# Generic widget operations
await client.list_widgets(canvas_id)
await client.get_widget(canvas_id, widget_id)
await client.create_widget(canvas_id, payload)
await client.update_widget(canvas_id, widget_id, payload)
await client.delete_widget(canvas_id, widget_id)

# Widget type-specific operations
await client.list_notes(canvas_id)
await client.create_note(canvas_id, payload)
await client.update_note(canvas_id, note_id, payload)
await client.delete_note(canvas_id, note_id)

# Similar operations for images, browsers, videos, PDFs, connectors
```

### User & Group Management
```python
# User operations
await client.list_users()
await client.get_user(user_id)
await client.create_user(payload)
await client.update_user(user_id, payload)
await client.delete_user(user_id)
await client.login_saml()

# Group operations
await client.list_groups()
await client.get_group(group_id)
await client.create_group(payload)
await client.update_group(group_id, payload)
await client.delete_group(group_id)
await client.add_user_to_group(group_id, user_id)
await client.list_group_members(group_id)
await client.remove_user_from_group(group_id, user_id)
```

### Content Management
```python
# File uploads
await client.upload_image(canvas_id, file_path)
await client.upload_video(canvas_id, file_path)
await client.upload_pdf(canvas_id, file_path)

# Asset operations
await client.get_asset_file(public_hash_hex, canvas_id)
await client.get_mipmap_info(public_hash_hex, canvas_id)
await client.get_mipmap_level_image(public_hash_hex, level, canvas_id)
```

### Video Operations
```python
# Video inputs
await client.list_canvas_video_inputs(canvas_id)
await client.create_video_input(canvas_id, payload)
await client.delete_video_input(canvas_id, input_id)
await client.list_client_video_inputs(client_id)

# Video outputs
await client.list_client_video_outputs(client_id)
await client.set_video_output_source(output_id, source_id)
await client.update_video_output(output_id, payload)
```

### License Management
```python
# License operations
await client.get_license_info()
await client.activate_license(payload)
await client.install_offline_license(payload)
await client.request_offline_activation(payload)
```

### Audit & Monitoring
```python
# Audit operations
await client.get_audit_log(params)
await client.export_audit_log_csv(params)

# Annotations
await client.list_widget_annotations(canvas_id)
async for update in client.subscribe_annotations(canvas_id):
    print(f"Annotation update: {update}")
```

### Real-time Subscriptions
```python
# Subscribe to real-time updates
async for update in client.subscribe_widgets(canvas_id):
    print(f"Widget update: {update}")

async for update in client.subscribe_annotations(canvas_id):
    print(f"Annotation update: {update}")
```

## 🔧 Configuration

### Environment Variables
```bash
export CANVUS_BASE_URL="https://your-canvus-server.com/api/v1"
export CANVUS_API_KEY="your-api-key"
export CANVUS_VERIFY_SSL="true"  # Set to "false" for test servers
```

### Configuration File
Create a `config.json` file:
```json
{
    "base_url": "https://your-canvus-server.com/api/v1",
    "api_key": "your-api-key",
    "verify_ssl": true,
    "timeout": 30
}
```

### Test Configuration
For testing against the test server:
```json
{
    "base_url": "https://canvusserver/api/v1",
    "api_key": "test-api-key",
    "verify_ssl": false,
    "timeout": 30
}
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_canvas_operations.py
pytest tests/test_widget_operations.py
pytest tests/test_integration.py

# Run with coverage
pytest --cov=canvus_api --cov-report=html
```

### Test Categories
- **Unit Tests**: Mocked API responses for fast testing
- **Integration Tests**: Real server testing with test data
- **File Upload Tests**: Image, video, and PDF upload testing
- **Error Handling Tests**: Comprehensive error scenario testing
- **Performance Tests**: Large dataset and streaming tests

### Test Server
- **URL**: `https://canvusserver`
- **SSL**: Disabled for testing
- **Credentials**: Test accounts provided
- **Data**: Automatic cleanup after tests

## 📖 Documentation

### Comprehensive Documentation
- **API Reference**: Complete endpoint documentation
- **Examples**: Real-world usage examples
- **Models**: Pydantic model documentation
- **Error Handling**: Exception hierarchy and handling
- **Testing Guide**: Comprehensive testing documentation

### Documentation Files
- `EXAMPLES.md` - Usage examples and patterns
- `Docs/` - Individual API endpoint documentation
- `tests/` - Test examples and patterns
- `LLM_DEV_GUIDE.md` - Development workflow guide

## 🛠️ Development

### Code Quality
```bash
# Run quality checks
ruff check . -q
black --check . -q
mypy .
pytest

# Auto-format code
black .
ruff check . --fix
```

### Development Workflow
1. **Create feature branch**: `git checkout -b feature/issue-description`
2. **Implement changes**: Follow existing patterns and conventions
3. **Add tests**: Include unit and integration tests
4. **Run quality checks**: Ensure all checks pass
5. **Create PR**: Include task numbers and issue references
6. **Self-merge**: If no issues found
7. **Update documentation**: Keep docs current

### Contributing Guidelines
- **Conventional commits**: Use standard commit format
- **Type hints**: Include for all public methods
- **Docstrings**: Google-style documentation
- **Error handling**: Comprehensive exception handling
- **Testing**: >80% coverage required

## 🔍 Error Handling

### Exception Hierarchy
```python
CanvusAPIError                    # Base exception
├── AuthenticationError           # 401, 403 errors
├── ValidationError               # 422 validation errors
├── ResourceNotFoundError         # 404 not found errors
├── RateLimitError               # 429 rate limit errors
└── ServerError                  # 5xx server errors
```

### Error Handling Example
```python
try:
    canvas = await client.get_canvas("non-existent-id")
except ResourceNotFoundError as e:
    print(f"Canvas not found: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except CanvusAPIError as e:
    print(f"API error: {e}")
```

## 📊 Performance

### Optimizations
- **Connection pooling**: Reuse HTTP connections
- **Async operations**: Non-blocking I/O
- **Streaming responses**: Handle large datasets efficiently
- **Batch operations**: Reduce API calls
- **Caching**: Optional response caching

### Best Practices
- **Use async/await**: For all API operations
- **Handle timeouts**: Configure appropriate timeouts
- **Stream large files**: Use streaming for file operations
- **Batch operations**: Group related operations
- **Error recovery**: Implement retry logic

## 🚀 Deployment

### Production Setup
```python
# Production configuration
client = CanvusClient(
    base_url="https://production.canvus.com/api/v1",
    api_key=os.getenv("CANVUS_API_KEY"),
    verify_ssl=True,
    timeout=30
)
```

### Monitoring
- **Logging**: Comprehensive logging support
- **Metrics**: Performance monitoring
- **Health checks**: Server status monitoring
- **Error tracking**: Exception monitoring

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Comprehensive docs in the `Docs/` directory
- **Examples**: See `EXAMPLES.md` for usage patterns
- **Testing**: Use test suite for validation

## 🎯 Status

✅ **Complete Implementation**: All 100+ API endpoints implemented  
✅ **Comprehensive Testing**: >80% test coverage with real server testing  
✅ **Full Documentation**: Complete API reference and examples  
✅ **Production Ready**: Type-safe, error-handled, and optimized  
✅ **Quality Assured**: All quality checks passing  

---

**Canvus Python API Client** - Complete, production-ready Python client for the Canvus API with full endpoint coverage, comprehensive testing, and extensive documentation. 