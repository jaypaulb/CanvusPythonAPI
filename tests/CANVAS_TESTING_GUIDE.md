# Canvas Testing Guide

## Guest-Accessible Test Canvas

For canvas-related testing, we use a pre-configured guest-accessible canvas to avoid permission issues and ensure consistent test results.

### Canvas Details

- **ID**: `556d6b64-7254-4bb1-a937-f6fe2bdc1afb`
- **Name**: "Test Canvas - Guest Access"
- **Access**: Guest (any authenticated user can access)
- **Purpose**: Canvas-related API testing

### Configuration

The guest canvas is configured in `tests/test_config.json`:

```json
{
  "test_data": {
    "test_canvas": {
      "id": "556d6b64-7254-4bb1-a937-f6fe2bdc1afb",
      "name": "Test Canvas - Guest Access",
      "description": "Guest-accessible canvas for testing - all test users can access this canvas",
      "access": "guest",
      "notes": "This canvas is set to guest access and can be used by any authenticated user for testing"
    }
  },
  "test_settings": {
    "canvas_testing": {
      "use_existing_guest_canvas": true,
      "guest_canvas_id": "556d6b64-7254-4bb1-a937-f6fe2bdc1afb",
      "notes": "Use the existing guest-accessible canvas for canvas-related tests to avoid permission issues"
    }
  }
}
```

### Usage in Tests

#### Using TestClient (Recommended)

```python
from tests.test_config import TestClient, get_test_config

async def test_canvas_operations():
    config = get_test_config()
    
    async with TestClient(config) as test_client:
        client = test_client.client
        
        # Get the guest canvas ID
        canvas_id = test_client.get_guest_canvas_id()
        
        # Test canvas operations
        canvas = await client.get_canvas(canvas_id)
        assert canvas is not None
        assert canvas.access == "guest"
```

#### Using conftest.py fixtures

```python
@pytest.mark.asyncio
async def test_canvas_with_fixture(client):
    # The client fixture automatically uses the guest canvas
    canvas_id = "556d6b64-7254-4bb1-a937-f6fe2bdc1afb"
    
    canvas = await client.get_canvas(canvas_id)
    assert canvas is not None
```

### Benefits

1. **No Permission Issues**: Guest access means any authenticated user can access the canvas
2. **Consistent Testing**: Same canvas ID across all tests
3. **No Cleanup Required**: Canvas persists between test runs
4. **Reliable**: No risk of canvas being deleted or modified by other tests

### When to Use

- **Canvas-related API tests**: Getting canvas info, listing widgets, etc.
- **Widget operations**: Creating/updating notes, images, videos, etc.
- **Permission tests**: Testing guest access functionality
- **Integration tests**: End-to-end canvas workflows

### When NOT to Use

- **Canvas creation tests**: Use dynamic canvas creation for these
- **Canvas deletion tests**: Use temporary canvases for these
- **Folder hierarchy tests**: Use dynamic folder creation

### Switching Between Guest Canvas and Dynamic Canvas

To use dynamic canvas creation instead of the guest canvas:

1. Set `"use_existing_guest_canvas": false` in the config
2. Or use `TestClient` with a different configuration

```python
# Force dynamic canvas creation
config = get_test_config()
config.config["test_settings"]["canvas_testing"]["use_existing_guest_canvas"] = False

async with TestClient(config) as test_client:
    # This will create a new canvas for testing
    canvas_id = test_client.get_test_canvas_id()
```

### Troubleshooting

If you encounter permission issues:

1. Verify the canvas ID is correct: `556d6b64-7254-4bb1-a937-f6fe2bdc1afb`
2. Check that the canvas still has guest access
3. Ensure your test user is properly authenticated
4. Verify the canvas hasn't been deleted or modified

### Canvas Maintenance

The guest canvas should be maintained with:
- Guest access permissions
- No sensitive data
- Basic structure for testing
- Regular cleanup of test artifacts (notes, images, etc.) 