"""
Main test runner for the Canvus API test suite.
Runs all specialized test files in sequence.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the tests directory to Python path
test_dir = Path(__file__).parent
if str(test_dir) not in sys.path:
    sys.path.append(str(test_dir))

from test_utils import (
    print_header, print_success, print_error, print_info, 
    print_warning, load_config
)

async def run_test_suite():
    """Run all tests in sequence."""
    print_header("\nStarting Canvus API Test Suite\n")
    
    try:
        # Initialize client (will be used by all tests)
        config = load_config()
        print_success("Configuration loaded")
        
        from canvus_api import CanvusClient
        async with CanvusClient(
            base_url=config["base_url"],
            api_key=config["api_key"]
        ) as client:
            print_success("Client initialized")
            
            # 1. Test server functions first (basic connectivity)
            print_header("\nRunning Server Function Tests\n")
            from test_server_functions import test_server_functions
            await test_server_functions(client)
            
            # 2. Test token management
            print_header("\nRunning Token Management Tests\n")
            from test_token_management import test_token_management
            await test_token_management(client)
            
            # 3. Test client discovery and workspace operations
            print_header("\nRunning Client Operations Tests\n")
            from test_client_operations import test_client_discovery, test_workspace_operations
            admin_client_id = await test_client_discovery(client)
            if admin_client_id:
                await test_workspace_operations(client, admin_client_id)
            else:
                print_error("Skipping workspace operations - no admin client found")
            
            # 4. Test canvas resources
            print_header("\nRunning Canvas Resource Tests\n")
            from test_canvas_resources import test_canvas_resources
            await test_canvas_resources(client)
            
            print_header("\nTest Suite Complete\n")
            print_success("All test modules executed")
            
    except Exception as e:
        print_error(f"Test suite error: {e}")
        raise

def main():
    """Main entry point."""
    try:
        asyncio.run(run_test_suite())
    except KeyboardInterrupt:
        print_warning("\nTest suite interrupted by user")
    except Exception as e:
        print_error(f"\nTest suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 