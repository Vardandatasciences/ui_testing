"""
Test script to check the S3 microservice integration from Python.
"""

import os
import sys
from grc.s3_fucntions import S3Client

def test_s3_health():
    """Test if the S3 microservice is running."""
    client = S3Client()
    health = client.check_health()
    
    if health["is_running"]:
        print("✅ S3 microservice is running")
        print(f"Message: {health['message']}")
    else:
        print("❌ S3 microservice is not running")
        print(f"Error: {health['message']}")
        print("\nPlease start the S3 microservice with:")
        print("cd ../frontend && node start-s3-service.js")
        sys.exit(1)

def test_upload_file():
    """Test uploading a file to S3."""
    client = S3Client()
    
    # Create a test file
    test_file_path = "test_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file for S3 upload.")
    
    try:
        print("Uploading test file...")
        result = client.upload_file(
            file_path=test_file_path,
            user_id="test-user",
            test_param="test-value"
        )
        
        if result.get("success"):
            print("✅ File upload successful")
            print(f"File URL: {result['file']['url']}")
            
            # Test file metadata
            file_id = result['file']['id']
            print("\nFetching file metadata...")
            metadata = client.get_file_metadata(file_id)
            print(f"✅ File metadata: {metadata}")
            
            # Test file deletion
            print("\nDeleting test file from S3...")
            delete_result = client.delete_file(file_id)
            if delete_result.get("success"):
                print("✅ File deletion successful")
            else:
                print("❌ File deletion failed")
        else:
            print("❌ File upload failed")
            print(f"Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error during upload test: {str(e)}")
    finally:
        # Clean up local test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    print("Testing S3 microservice integration...")
    test_s3_health()
    test_upload_file()
    print("\nAll tests completed.") 