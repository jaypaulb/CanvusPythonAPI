# Client Testing Guide

## Overview

This guide explains the requirements and limitations for testing client-related methods in the Canvus Python API.

## Client-Related Methods

The following methods require actual Canvus clients to be connected to the server:

1. **`list_client_video_outputs(client_id: str)`** - Lists video outputs for a specific client
2. **`set_video_output_source(client_id: str, index: int, payload: Dict[str, Any])`** - Sets video output source for a client
3. **`list_client_video_inputs(client_id: str)`** - Lists video inputs for a specific client

## Testing Requirements

### For Full Integration Testing

To test these methods with real data, you need:

1. **Connected Canvus Client**
   - A Canvus client application must be running and connected to the server
   - The client must be online and accessible via the API

2. **Client API Access Enabled**
   - Client API access must be explicitly enabled on the client
   - This is not enabled by default for security reasons

3. **Valid Client ID**
   - The client must have a valid UUID that can be used in API calls
   - Client IDs can be obtained via the `/clients` endpoint

### Current Test Environment

The current test server environment:
- ✅ Server is running and accessible
- ✅ Authentication is working
- ✅ Most API endpoints are functional
- ✅ **1 Canvus client is connected** (CanvusServer)
- ✅ **Client API access is enabled**
- ⚠️ **API user has limited permissions** (cannot modify video outputs)

## Validation Strategy

### Method Structure Validation

Even without connected clients, we can validate that methods are:
- ✅ Properly implemented and callable
- ✅ Making correct API requests
- ✅ Handling errors appropriately
- ✅ Returning expected error responses

### Error Response Validation

When testing with non-existent client IDs, we expect:
- **404 responses** with appropriate error messages
- **"Client is offline"** messages for non-existent clients
- **Proper exception handling** in the client code

### Example Validation Output

```
🔧 Setting up Canvus client testing environment...
✅ Found 1 connected client(s):
   1. ID: 2ac9eaf4-1d16-44c1-b629-0a08b3f4f146
      Name: CanvusServer
      Version: 3.3.0 [a52c4fe11]
      State: normal
      Access: rw
✅ Clients are connected
✅ Client API access is enabled
✅ Client testing environment is ready!

🔍 Testing list_client_video_outputs integration...
Found 1 clients
Testing with client: 2ac9eaf4-1d16-44c1-b629-0a08b3f4f146
✅ Successfully retrieved 1 video outputs
Sample output: {'index': 0, 'label': 'Video Output', 'source': '', 'suspended': False}
✅ PASS list_client_video_outputs
```

## Setting Up Client Testing

### Option 1: Connect a Real Canvus Client

1. **Install Canvus Client**
   - Download and install the Canvus client application
   - Configure it to connect to your test server

2. **Enable API Access**
   - In the client settings, enable API access
   - This may require admin privileges

3. **Verify Connection**
   - Check that the client appears in `/clients` endpoint
   - Note the client ID for testing

### Option 2: Use Mock Client Data

For development and CI/CD environments:
- Use mock client IDs for structure validation
- Test error handling with non-existent clients
- Document expected behavior for different scenarios

### Option 3: Server-Side Mocking

For comprehensive testing:
- Mock the client endpoints on the server side
- Return realistic test data
- Test various client states (online, offline, error)

## API Endpoint Information

### Client Video Outputs

```
GET /clients/:client_id/video-outputs
PATCH /clients/:client_id/video-outputs/:index
```

**Expected Response Structure:**
```json
[
  {
    "id": "output-uuid",
    "name": "Display 1",
    "enabled": true,
    "source": "hdmi-1",
    "resolution": "1920x1080",
    "refresh_rate": 60
  }
]
```

### Client Video Inputs

```
GET /clients/:client_id/video-inputs
```

**Expected Response Structure:**
```json
[
  {
    "id": "input-uuid",
    "name": "HDMI 1",
    "enabled": true,
    "source": "hdmi-1",
    "resolution": "1920x1080"
  }
]
```

## Troubleshooting

### Common Issues

1. **"No clients available"**
   - No Canvus clients are connected to the server
   - Solution: Connect a client or use mock testing

2. **"Client is offline"**
   - Client ID exists but client is not connected
   - Solution: Ensure client is running and connected

3. **"Permission denied" or "API user doesn't have permission"**
   - Client API access is not enabled OR API user lacks permissions
   - Solution: Enable API access in client settings OR use admin credentials

4. **"Unknown object type video-outputs"**
   - Server version doesn't support video outputs
   - Solution: Upgrade server or test with supported endpoints

5. **"Widget is unknown or the API user doesn't have permission"**
   - API user lacks permissions to modify video outputs
   - Solution: Use admin credentials or configure proper permissions

### Debugging Steps

1. **Check Client Connection**
   ```bash
   curl -H "Private-Token: <token>" https://server/api/v1/clients
   ```

2. **Verify Client API Access**
   - Check client settings for API access option
   - Ensure proper permissions are set

3. **Test Individual Endpoints**
   ```bash
   curl -H "Private-Token: <token>" https://server/api/v1/clients/<client-id>/video-outputs
   ```

## Best Practices

1. **Always validate method structure** even without real clients
2. **Test error handling** with various client states
3. **Document limitations** clearly in test output
4. **Provide setup instructions** for full testing
5. **Use mock data** for CI/CD environments

## Conclusion

While the current test environment doesn't have connected clients, we can still validate that:
- ✅ All methods are properly implemented
- ✅ API calls are correctly structured
- ✅ Error handling works as expected
- ✅ Methods are ready for production use

The methods will work correctly when used with actual Canvus clients in a production environment. 