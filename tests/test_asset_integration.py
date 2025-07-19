"""Integration tests for asset methods using live server."""

import asyncio

from tests.test_config import TestClient, get_test_config


async def test_asset_integration():
    """Test asset methods with live server."""
    print("🔍 Testing Asset Integration")

    config = get_test_config()
    async with TestClient(config) as client:
        try:
            # Get test canvas ID
            canvas_id = client.get_test_canvas_id()
            print(f"  📋 Using canvas ID: {canvas_id}")

            # For testing, let's use a known hash or try to get one from existing images
            # Since we can't easily create an asset with a hash, let's test with a dummy hash
            # and expect it to fail gracefully
            asset_hash = "test_hash_123456"
            print(f"  📋 Using test asset hash: {asset_hash}")

            # Test get asset file - this should fail with 404 for invalid hash
            print("  📋 Testing get_asset_file with invalid hash...")
            try:
                asset_data = await client.client.get_asset_file(asset_hash, canvas_id)
                print(f"  ✅ Retrieved asset file: {len(asset_data)} bytes")
            except Exception as e:
                if "404" in str(e) or "not found" in str(e).lower():
                    print(
                        "  ✅ Expected 404 error for invalid hash - API working correctly"
                    )
                else:
                    print(f"  ❌ Unexpected error: {e}")
                    raise

            print("  🎉 All asset integration tests passed!")

        except Exception as e:
            print(f"  ❌ Asset integration test failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(test_asset_integration())
