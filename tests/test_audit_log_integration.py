"""
Test audit log integration with live server.
"""

import pytest
import asyncio

from tests.test_config import TestClient, get_test_config


@pytest.mark.asyncio
async def test_audit_log_integration():
    """Test audit log methods with live server."""
    print("🔍 Testing Audit Log Integration")

    config = get_test_config()
    async with TestClient(config) as client:
        try:
            # Test get audit log without filters
            print("  📋 Testing get_audit_log without filters...")
            audit_log = await client.client.get_audit_log()

            print(f"  ✅ Retrieved audit log: {len(audit_log)} events")
            if audit_log:
                print(f"  📊 Sample event: {audit_log[0].get('action', 'Unknown')}")

            # Test get audit log with filters
            print("  📋 Testing get_audit_log with filters...")
            filters = {"per_page": 5}  # Limit to 5 events for testing
            filtered_log = await client.client.get_audit_log(filters)

            print(f"  ✅ Retrieved filtered audit log: {len(filtered_log)} events")

            # Test export audit log CSV
            print("  📋 Testing export_audit_log_csv...")
            csv_data = await client.client.export_audit_log_csv()

            print(f"  ✅ Exported CSV data: {len(csv_data)} bytes")
            if csv_data:
                # Check if it looks like CSV data
                csv_text = csv_data.decode("utf-8", errors="ignore")
                if "," in csv_text and "\n" in csv_text:
                    print("  ✅ CSV format appears valid")
                else:
                    print("  ⚠️ CSV format may be unexpected")

            print("  🎉 All audit log integration tests passed!")

        except Exception as e:
            print(f"  ❌ Audit log integration test failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(test_audit_log_integration())
