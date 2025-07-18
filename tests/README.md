# Integration Testing Framework

This directory contains the integration testing framework for the Canvus Python API client.

## Overview

The testing framework provides:
- **Configuration management** for test settings
- **Automatic test data setup/cleanup** 
- **Layered testing approach** (create → test → cleanup)
- **Authentication handling** for admin and regular users
- **File upload testing** with sample files

## Files

- `test_config.json` - Test configuration (update with your server details)
- `test_config.py` - Configuration loader and test utilities
- `test_integration_example.py` - Example integration tests
- `test_files/` - Sample files for upload testing

## Setup Instructions

### 1. Configure Your Server

Edit `tests/test_config.json` and update the following:

```json
{
  "server": {
    "base_url": "http://your-canvus-server:3000",
    "api_version": "v1"
  },
  "authentication": {
    "admin_user": {
      "email": "admin@your-domain.com",
      "password": "your_admin_password"
    },
    "regular_user": {
      "email": "user@your-domain.com", 
      "password": "your_user_password"
    },
    "api_key": "your_api_key_here"
  }
}
```

### 2. Test Data Setup

The framework will automatically create:
- **Test Folder** - For organizing test canvases
- **Test Canvas** - For testing canvas operations
- **Test Group** - For testing group operations  
- **Test User** - For testing user operations

### 3. Sample Files

The `test_files/` directory contains:
- `test_image.jpg` - Sample image for upload testing
- `test_video.mp4` - Sample video for upload testing
- `test_pdf.pdf` - Sample PDF for upload testing

## Usage

### Basic Integration Test

```python
import pytest
from tests.test_config import TestClient, get_test_config

@pytest.mark.asyncio
async def test_canvas_operations():
    # Use context manager for automatic setup/cleanup
    async with TestClient(get_test_config()) as test_client:
        client = test_client.client
        canvas_id = test_client.get_test_canvas_id()
        
        # Your test code here
        canvas = await client.get_canvas(canvas_id)
        assert canvas is not None
```

### Manual Setup/Cleanup

```python
async def test_with_manual_control():
    test_client = TestClient(get_test_config())
    await test_client.authenticate(use_admin=True)
    await test_client.data_manager.setup_test_environment()
    
    try:
        # Your test code here
        pass
    finally:
        await test_client.data_manager.cleanup_test_environment()
```

## Test Configuration Options

### Server Settings
- `base_url` - Your Canvus server URL
- `timeout` - Request timeout in seconds
- `max_retries` - Number of retry attempts

### Authentication
- `admin_user` - Admin credentials for privileged operations
- `regular_user` - Regular user credentials for permission testing
- `api_key` - API key for direct authentication

### Test Settings
- `cleanup_after_tests` - Automatically clean up test data
- `create_test_data` - Create test data during setup
- `parallel_tests` - Enable/disable parallel test execution
- `test_timeout` - Overall test timeout

### File Settings
- `image` - Path to test image file
- `video` - Path to test video file
- `pdf` - Path to test PDF file

## Running Tests

### Run All Integration Tests
```bash
pytest tests/test_integration_example.py -v
```

### Run Specific Test
```bash
pytest tests/test_integration_example.py::test_canvas_operations_integration -v
```

### Run with Custom Config
```python
from tests.test_config import TestConfig, TestClient

custom_config = TestConfig("path/to/custom_config.json")
async with TestClient(custom_config) as test_client:
    # Your test code
```

## Best Practices

### 1. Use Context Managers
Always use the `TestClient` as a context manager to ensure proper cleanup:

```python
async with TestClient(get_test_config()) as test_client:
    # Test code here
```

### 2. Test Data Isolation
Each test should create its own test data and clean it up:

```python
async def test_specific_operation():
    async with TestClient(get_test_config()) as test_client:
        # Create specific test data
        new_canvas = await test_client.client.create_canvas({
            "name": "Test Specific Canvas"
        })
        
        # Test the operation
        result = await test_client.client.some_operation(new_canvas.id)
        
        # Cleanup is automatic via context manager
```

### 3. Error Handling
Handle expected errors gracefully:

```python
async def test_error_conditions():
    async with TestClient(get_test_config()) as test_client:
        # Test non-existent resource
        with pytest.raises(CanvusAPIError):
            await test_client.client.get_canvas("non-existent-id")
```

### 4. File Upload Testing
Use the provided sample files for consistent testing:

```python
async def test_file_upload():
    async with TestClient(get_test_config()) as test_client:
        image_path = get_test_config().test_files["image"]
        image = await test_client.client.create_image(
            test_client.get_test_canvas_id(), 
            image_path
        )
        assert image is not None
```

## Troubleshooting

### Authentication Issues
- Verify admin and user credentials in `test_config.json`
- Check if the server requires specific authentication methods
- Ensure API key has proper permissions

### File Upload Issues
- Verify test files exist in `test_files/` directory
- Check file permissions and sizes
- Ensure server supports the file types

### Cleanup Issues
- Check if `cleanup_after_tests` is enabled
- Verify test data IDs are properly captured
- Check server permissions for deletion operations

### Network Issues
- Verify server URL and port in configuration
- Check firewall and network connectivity
- Increase timeout values if needed

## Security Notes

- **Never commit real credentials** to version control
- Use environment variables for sensitive data in production
- Consider using a dedicated test server
- Regularly rotate test user passwords

## Environment Variables

You can override configuration using environment variables:

```bash
export CANVUS_SERVER_URL="http://your-server:3000"
export CANVUS_API_KEY="your-api-key"
export CANVUS_ADMIN_EMAIL="admin@domain.com"
export CANVUS_ADMIN_PASSWORD="admin-password"
```

The test configuration will automatically use these if available. 