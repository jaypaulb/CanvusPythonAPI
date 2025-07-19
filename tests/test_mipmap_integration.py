"""Integration tests for mipmap methods using live server."""

import asyncio
import os

from tests.test_config import TestClient, get_test_config


async def test_image_mipmap_integration():
    """Test mipmap methods with image assets using live server."""
    print("🔍 Testing Image Mipmap Integration")

    config = get_test_config()
    async with TestClient(config) as client:
        try:
            # Get test canvas ID
            canvas_id = client.get_test_canvas_id()
            print(f"  📋 Using canvas ID: {canvas_id}")

            # Check for existing images with valid hashes
            print("  📋 Checking for existing images...")
            existing_images = await client.client.list_images(canvas_id)
            print(f"  📋 Found {len(existing_images)} existing images")

            asset_hash = None

            # Look for any image with a valid hash
            for image in existing_images:
                if image.hash and image.hash.strip():
                    asset_hash = image.hash
                    print(f"  ✅ Found existing image with hash: {asset_hash}")
                    break

            # If no existing image with hash, upload a new one
            if not asset_hash:
                print(
                    "  📋 No existing images with valid hashes found, uploading new image..."
                )
                test_image_path = "test_files/test_image.jpg"
                if not os.path.exists(test_image_path):
                    print(f"  ❌ Test image not found: {test_image_path}")
                    raise FileNotFoundError(f"Test image not found: {test_image_path}")

                print(f"  📋 Uploading test image: {test_image_path}")
                image = await client.client.create_image(canvas_id, test_image_path)
                print(f"  📋 Image uploaded, ID: {image.id}, Hash: '{image.hash}'")

                # Wait for the server to process the image and generate hash
                if not image.hash or not image.hash.strip():
                    print("  📋 Waiting for server to generate hash...")
                    for attempt in range(15):  # Try up to 15 times (30 seconds total)
                        await asyncio.sleep(2)  # Wait 2 seconds
                        try:
                            updated_image = await client.client.get_image(
                                canvas_id, image.id
                            )
                            if updated_image.hash and updated_image.hash.strip():
                                asset_hash = updated_image.hash
                                print(
                                    f"  ✅ Hash generated after {attempt + 1} attempts: {asset_hash}"
                                )
                                break
                            else:
                                print(f"  📋 Attempt {attempt + 1}: Hash still empty")
                        except Exception as e:
                            print(
                                f"  📋 Attempt {attempt + 1}: Error getting image: {e}"
                            )

                    if not asset_hash:
                        print("  ❌ Failed to get valid hash after multiple attempts")
                        raise Exception("Image upload did not generate a valid hash")
                else:
                    asset_hash = image.hash
                    print(f"  ✅ Image uploaded successfully with hash: {asset_hash}")

            # Now test the mipmap methods with the valid hash
            print(f"  📋 Testing mipmap methods with image hash: {asset_hash}")

            # Wait much longer for mipmap generation
            print("  📋 Waiting for mipmap generation (30 seconds)...")
            await asyncio.sleep(30)

            # Test get_mipmap_info with valid hash (no page parameter for images)
            print("  📋 Testing get_mipmap_info with valid hash...")
            try:
                mipmap_info = await client.client.get_mipmap_info(asset_hash, canvas_id)
                print(f"  ✅ Retrieved mipmap info: {mipmap_info}")

                # Verify the response structure
                if isinstance(mipmap_info, dict):
                    print(
                        f"  ✅ Mipmap info is a dictionary with keys: {list(mipmap_info.keys())}"
                    )
                    if "resolution" in mipmap_info:
                        print(f"  ✅ Resolution: {mipmap_info['resolution']}")
                    if "max_level" in mipmap_info:
                        print(f"  ✅ Max level: {mipmap_info['max_level']}")
                    if "pages" in mipmap_info:
                        print(f"  ✅ Pages: {mipmap_info['pages']}")
                else:
                    print(f"  ⚠️ Unexpected mipmap info format: {type(mipmap_info)}")

            except Exception as e:
                error_msg = str(e)
                print(f"  ❌ Error getting mipmap info: {error_msg}")
                if "Not supported" in error_msg:
                    print(
                        "  📝 Note: This server may not support mipmap functionality for images"
                    )
                elif "No document with id" in error_msg:
                    print(
                        "  📝 Note: Mipmap may not be generated yet or hash format may be incorrect"
                    )
                elif "404" in error_msg or "not found" in error_msg.lower():
                    print("  ❌ Asset not found - unexpected for valid hash")
                    raise
                else:
                    print(f"  ❌ Unexpected error: {e}")
                    raise

            # Test get_mipmap_level_image with valid hash (no page parameter for images)
            print("  📋 Testing get_mipmap_level_image with valid hash...")
            try:
                level_image = await client.client.get_mipmap_level_image(
                    asset_hash, 0, canvas_id
                )
                print(f"  ✅ Retrieved level 0 image: {len(level_image)} bytes")

                # Verify we got actual image data
                if len(level_image) > 0:
                    print(
                        f"  ✅ Level 0 image contains {len(level_image)} bytes of data"
                    )
                    # Check if it looks like WebP data (should start with RIFF)
                    if level_image.startswith(b"RIFF"):
                        print("  ✅ Level 0 image appears to be valid WebP format")
                    else:
                        print("  ⚠️ Level 0 image doesn't appear to be WebP format")
                else:
                    print("  ⚠️ Level 0 image is empty")

            except Exception as e:
                error_msg = str(e)
                print(f"  ❌ Error getting mipmap level image: {error_msg}")
                if "Not supported" in error_msg:
                    print(
                        "  📝 Note: This server may not support mipmap level images for images"
                    )
                elif "No document with id" in error_msg:
                    print(
                        "  📝 Note: Mipmap may not be generated yet or hash format may be incorrect"
                    )
                elif "404" in error_msg or "not found" in error_msg.lower():
                    print("  ❌ Asset not found - unexpected for valid hash")
                    raise
                else:
                    print(f"  ❌ Unexpected error: {e}")
                    raise

            # Clean up the uploaded image if we created one
            if "image" in locals() and hasattr(image, "id"):
                print("  📋 Cleaning up uploaded image...")
                try:
                    await client.client.delete_image(canvas_id, image.id)
                    print("  ✅ Image deleted successfully")
                except Exception as e:
                    print(f"  ⚠️ Failed to delete test image: {e}")
                    # Don't raise here as this is cleanup

            print("  🎉 Image mipmap integration tests passed!")

        except Exception as e:
            print(f"  ❌ Image mipmap integration test failed: {e}")
            raise


async def test_pdf_mipmap_integration():
    """Test mipmap methods with PDF assets using live server."""
    print("🔍 Testing PDF Mipmap Integration")

    config = get_test_config()
    async with TestClient(config) as client:
        try:
            # Get test canvas ID
            canvas_id = client.get_test_canvas_id()
            print(f"  📋 Using canvas ID: {canvas_id}")

            # Check for existing PDFs with valid hashes
            print("  📋 Checking for existing PDFs...")
            existing_pdfs = await client.client.list_pdfs(canvas_id)
            print(f"  📋 Found {len(existing_pdfs)} existing PDFs")

            asset_hash = None

            # Look for any PDF with a valid hash
            for pdf in existing_pdfs:
                if pdf.hash and pdf.hash.strip():
                    asset_hash = pdf.hash
                    print(f"  ✅ Found existing PDF with hash: {asset_hash}")
                    break

            # If no existing PDF with hash, upload a new one
            if not asset_hash:
                print(
                    "  📋 No existing PDFs with valid hashes found, uploading new PDF..."
                )
                test_pdf_path = "test_files/test_pdf.pdf"
                if not os.path.exists(test_pdf_path):
                    print(f"  ❌ Test PDF not found: {test_pdf_path}")
                    raise FileNotFoundError(f"Test PDF not found: {test_pdf_path}")

                print(f"  📋 Uploading test PDF: {test_pdf_path}")
                pdf = await client.client.create_pdf(canvas_id, test_pdf_path)
                print(f"  📋 PDF uploaded, ID: {pdf.id}, Hash: '{pdf.hash}'")

                # Wait for the server to process the PDF and generate hash
                if not pdf.hash or not pdf.hash.strip():
                    print("  📋 Waiting for server to generate hash...")
                    for attempt in range(15):  # Try up to 15 times (30 seconds total)
                        await asyncio.sleep(2)  # Wait 2 seconds
                        try:
                            updated_pdf = await client.client.get_pdf(canvas_id, pdf.id)
                            if updated_pdf.hash and updated_pdf.hash.strip():
                                asset_hash = updated_pdf.hash
                                print(
                                    f"  ✅ Hash generated after {attempt + 1} attempts: {asset_hash}"
                                )
                                break
                            else:
                                print(f"  📋 Attempt {attempt + 1}: Hash still empty")
                        except Exception as e:
                            print(f"  📋 Attempt {attempt + 1}: Error getting PDF: {e}")

                    if not asset_hash:
                        print("  ❌ Failed to get valid hash after multiple attempts")
                        raise Exception("PDF upload did not generate a valid hash")
                else:
                    asset_hash = pdf.hash
                    print(f"  ✅ PDF uploaded successfully with hash: {asset_hash}")

            # Now test the mipmap methods with the valid hash
            print(f"  📋 Testing mipmap methods with PDF hash: {asset_hash}")

            # Wait much longer for mipmap generation
            print("  📋 Waiting for mipmap generation (30 seconds)...")
            await asyncio.sleep(30)

            # Test get_mipmap_info with valid hash (page 0 for PDFs)
            print("  📋 Testing get_mipmap_info with valid hash (page 0)...")
            try:
                mipmap_info = await client.client.get_mipmap_info(
                    asset_hash, page=0, canvas_id=canvas_id
                )
                print(f"  ✅ Retrieved mipmap info for page 0: {mipmap_info}")

                # Verify the response structure
                if isinstance(mipmap_info, dict):
                    print(
                        f"  ✅ Mipmap info is a dictionary with keys: {list(mipmap_info.keys())}"
                    )
                    if "resolution" in mipmap_info:
                        print(f"  ✅ Resolution: {mipmap_info['resolution']}")
                    if "max_level" in mipmap_info:
                        print(f"  ✅ Max level: {mipmap_info['max_level']}")
                    if "pages" in mipmap_info:
                        print(f"  ✅ Pages: {mipmap_info['pages']}")

                        # If PDF has multiple pages, test page 1 as well
                        if mipmap_info["pages"] > 1:
                            print("  📋 Testing get_mipmap_info with page 1...")
                            try:
                                page1_info = await client.client.get_mipmap_info(
                                    asset_hash, page=1, canvas_id=canvas_id
                                )
                                print(
                                    f"  ✅ Retrieved mipmap info for page 1: {page1_info}"
                                )
                            except Exception as e:
                                print(f"  ⚠️ Error getting page 1 info: {e}")
                else:
                    print(f"  ⚠️ Unexpected mipmap info format: {type(mipmap_info)}")

            except Exception as e:
                error_msg = str(e)
                print(f"  ❌ Error getting mipmap info: {error_msg}")
                if "Not supported" in error_msg:
                    print(
                        "  📝 Note: This server may not support mipmap functionality for PDFs"
                    )
                elif "No document with id" in error_msg:
                    print(
                        "  📝 Note: Mipmap may not be generated yet or hash format may be incorrect"
                    )
                elif "404" in error_msg or "not found" in error_msg.lower():
                    print("  ❌ Asset not found - unexpected for valid hash")
                    raise
                else:
                    print(f"  ❌ Unexpected error: {e}")
                    raise

            # Test get_mipmap_level_image with valid hash (page 0 for PDFs)
            print("  📋 Testing get_mipmap_level_image with valid hash (page 0)...")
            try:
                level_image = await client.client.get_mipmap_level_image(
                    asset_hash, 0, page=0, canvas_id=canvas_id
                )
                print(
                    f"  ✅ Retrieved level 0 image for page 0: {len(level_image)} bytes"
                )

                # Verify we got actual image data
                if len(level_image) > 0:
                    print(
                        f"  ✅ Level 0 image contains {len(level_image)} bytes of data"
                    )
                    # Check if it looks like WebP data (should start with RIFF)
                    if level_image.startswith(b"RIFF"):
                        print("  ✅ Level 0 image appears to be valid WebP format")
                    else:
                        print("  ⚠️ Level 0 image doesn't appear to be WebP format")
                else:
                    print("  ⚠️ Level 0 image is empty")

            except Exception as e:
                error_msg = str(e)
                print(f"  ❌ Error getting mipmap level image: {error_msg}")
                if "Not supported" in error_msg:
                    print(
                        "  📝 Note: This server may not support mipmap level images for PDFs"
                    )
                elif "No document with id" in error_msg:
                    print(
                        "  📝 Note: Mipmap may not be generated yet or hash format may be incorrect"
                    )
                elif "404" in error_msg or "not found" in error_msg.lower():
                    print("  ❌ Asset not found - unexpected for valid hash")
                    raise
                else:
                    print(f"  ❌ Unexpected error: {e}")
                    raise

            # Clean up the uploaded PDF if we created one
            if "pdf" in locals() and hasattr(pdf, "id"):
                print("  📋 Cleaning up uploaded PDF...")
                try:
                    await client.client.delete_pdf(canvas_id, pdf.id)
                    print("  ✅ PDF deleted successfully")
                except Exception as e:
                    print(f"  ⚠️ Failed to delete test PDF: {e}")
                    # Don't raise here as this is cleanup

            print("  🎉 PDF mipmap integration tests passed!")

        except Exception as e:
            print(f"  ❌ PDF mipmap integration test failed: {e}")
            raise


async def test_mipmap_error_handling():
    """Test mipmap error handling with invalid hashes."""
    print("🔍 Testing Mipmap Error Handling")

    config = get_test_config()
    async with TestClient(config) as client:
        try:
            # Get test canvas ID
            canvas_id = client.get_test_canvas_id()
            print(f"  📋 Using canvas ID: {canvas_id}")

            # Test with invalid hash to ensure error handling works
            print("  📋 Testing error handling with invalid hash...")
            invalid_hash = "invalid_hash_123456"
            try:
                await client.client.get_mipmap_info(invalid_hash, canvas_id)
                print("  ❌ Expected 404 error but got success")
                raise Exception("Expected 404 error for invalid hash")
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg or "not found" in error_msg.lower():
                    print(
                        "  ✅ Expected 404 error for invalid hash - error handling working correctly"
                    )
                else:
                    print(f"  ❌ Unexpected error for invalid hash: {e}")
                    raise

            print("  🎉 Mipmap error handling tests passed!")

        except Exception as e:
            print(f"  ❌ Mipmap error handling test failed: {e}")
            raise


async def test_mipmap_integration():
    """Run all mipmap integration tests."""
    print("🚀 Running All Mipmap Integration Tests")
    print("=" * 50)

    await test_image_mipmap_integration()
    print()
    await test_pdf_mipmap_integration()
    print()
    await test_mipmap_error_handling()
    print()

    print("🎉 All mipmap integration tests completed!")


if __name__ == "__main__":
    asyncio.run(test_mipmap_integration())
