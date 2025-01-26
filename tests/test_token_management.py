"""
Test suite for token management operations.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the tests directory to Python path
test_dir = Path(__file__).parent
if str(test_dir) not in sys.path:
    sys.path.append(str(test_dir))

from canvus_api import CanvusClient, CanvusAPIError
from test_utils import (
    print_success, print_error, print_info, 
    print_warning, print_header, load_config
)

async def test_token_lifecycle(client: CanvusClient, user_id: int) -> None:
    """Test the complete lifecycle of a token."""
    print_header("Testing Token Lifecycle")
    
    token_id = None
    try:
        # List existing tokens
        tokens = await client.list_tokens(user_id)
        print_success(f"Found {len(tokens)} existing tokens")
        
        # Create a new token
        token = await client.create_token(user_id, "Test token")
        token_id = token.id
        print_success(f"Created token: {token.id}")
        print_success(f"Plain token value: {token.plain_token}")
        
        # Get token details
        retrieved = await client.get_token(user_id, token.id)
        print_success(f"Retrieved token: {retrieved.id}")
        
        # Update token description
        updated = await client.update_token(user_id, token.id, "Updated test token")
        print_success(f"Updated token description")
        
        # Delete token
        await client.delete_token(user_id, token.id)
        print_success(f"Deleted token: {token.id}")
        
        # Verify deletion by trying to get it (should fail with 404)
        try:
            await client.get_token(user_id, token.id)
            raise Exception("Token still exists after deletion!")
        except CanvusAPIError as e:
            if e.status_code == 404:
                print_success("Verified token deletion (404 response as expected)")
            else:
                raise Exception(f"Unexpected error checking token deletion: {e}")
                
    except Exception as e:
        print_error(f"Token operations error: {e}")
        if token_id:
            try:
                await client.delete_token(user_id, token_id)
            except:
                pass

async def test_token_management(client: CanvusClient) -> None:
    """Main test function."""
    print_header("Starting Token Management Tests")
    
    # Get user ID from config or use default
    config = load_config()
    user_id = config.get("user_id", 1000)  # Default to 1000 if not specified
    
    await test_token_lifecycle(client, user_id)

if __name__ == "__main__":
    async def run():
        config = load_config()
        print_success("Configuration loaded")
        
        async with CanvusClient(
            base_url=config["base_url"],
            api_key=config["api_key"]
        ) as client:
            print_success("Client initialized")
            await test_token_management(client)
            
    asyncio.run(run()) 