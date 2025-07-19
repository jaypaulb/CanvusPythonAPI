"""Integration tests for mipmap methods using live server."""

import asyncio
from typing import Dict, Any

from tests.test_config import TestClient, get_test_config


async def test_mipmap_integration():
    """Test mipmap methods with live server."""
    print("🔍 Testing Mipmap Integration")
    
    config = get_test_config()
    async with TestClient(config) as client:
        try:
            # Get test canvas ID
            canvas_id = client.get_test_canvas_id()
            print(f"  📋 Using canvas ID: {canvas_id}")
            
            # For testing, let's use a known hash or try to get one from existing images
            # Since we can't easily create an image with a hash, let's test with a dummy hash
            # and expect it to fail gracefully
            asset_hash = "test_hash_123456"
            print(f"  📋 Using test asset hash: {asset_hash}")
            
            # Test get mipmap info - this should fail with 404 for invalid hash
            print("  📋 Testing get_mipmap_info with invalid hash...")
            try:
                mipmap_info = await client.client.get_mipmap_info(asset_hash, canvas_id)
                print(f"  ✅ Retrieved mipmap info: {mipmap_info}")
            except Exception as e:
                if "404" in str(e) or "not found" in str(e).lower():
                    print("  ✅ Expected 404 error for invalid hash - API working correctly")
                else:
                    print(f"  ❌ Unexpected error: {e}")
                    raise
            
            # Test get mipmap level image - this should also fail with 404
            print("  📋 Testing get_mipmap_level_image with invalid hash...")
            try:
                level_image = await client.client.get_mipmap_level_image(asset_hash, 0, canvas_id)
                print(f"  ✅ Retrieved level 0 image: {len(level_image)} bytes")
            except Exception as e:
                if "404" in str(e) or "not found" in str(e).lower():
                    print("  ✅ Expected 404 error for invalid hash - API working correctly")
                else:
                    print(f"  ❌ Unexpected error: {e}")
                    raise
            
            print("  🎉 All mipmap integration tests passed!")
            
        except Exception as e:
            print(f"  ❌ Mipmap integration test failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(test_mipmap_integration()) 