import requests
import os
import mimetypes
from typing import Dict, List, Optional, Union, BinaryIO
import json

class S3Client:
    """Client for interacting with the S3 microservice API."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize the S3 client.
        
        Args:
            base_url: Base URL of the S3 microservice API
        """
        self.base_url = base_url.rstrip('/')
        
        # Initialize mimetypes
        mimetypes.init()
        
        # Add common extensions that might be missing
        self._add_missing_mimetypes()
    
    def _add_missing_mimetypes(self):
        """Add common MIME types that might be missing from the system."""
        types_map = {
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.csv': 'text/csv',
            '.pdf': 'application/pdf',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.7z': 'application/x-7z-compressed',
        }
        
        for ext, mime_type in types_map.items():
            mimetypes.add_type(mime_type, ext)
    
    def _detect_file_type(self, file_path: str) -> Dict[str, str]:
        """
        Detect file type based on file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict containing file_type (extension) and content_type (MIME type)
        """
        # Get file extension (without the dot)
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension.startswith('.'):
            file_extension = file_extension[1:]
        
        # Get MIME type
        mime_type, encoding = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'  # Default to binary
        
        # Get document category
        document_category = self._categorize_document(file_extension, mime_type)
        
        return {
            'file_type': file_extension,
            'content_type': mime_type,
            'document_category': document_category
        }
    
    def _categorize_document(self, extension: str, mime_type: str) -> str:
        """
        Categorize document based on extension and MIME type.
        
        Args:
            extension: File extension
            mime_type: MIME type
            
        Returns:
            Document category string
        """
        # Spreadsheets
        if extension in ['xlsx', 'xls', 'csv'] or 'spreadsheet' in mime_type:
            return 'spreadsheet'
            
        # Documents
        if extension in ['doc', 'docx', 'odt', 'rtf', 'txt'] or 'document' in mime_type:
            return 'document'
            
        # Presentations
        if extension in ['ppt', 'pptx', 'odp'] or 'presentation' in mime_type:
            return 'presentation'
            
        # PDFs
        if extension == 'pdf' or mime_type == 'application/pdf':
            return 'pdf'
            
        # Images
        if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'] or mime_type.startswith('image/'):
            return 'image'
            
        # Videos
        if extension in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'] or mime_type.startswith('video/'):
            return 'video'
            
        # Audio
        if extension in ['mp3', 'wav', 'ogg', 'flac', 'aac'] or mime_type.startswith('audio/'):
            return 'audio'
            
        # Archives
        if extension in ['zip', 'rar', '7z', 'tar', 'gz'] or 'compressed' in mime_type:
            return 'archive'
            
        # Default
        return 'other'
    
    def upload_file(self, 
                   file_path: str, 
                   user_id: str = "default-user", 
                   file_name: Optional[str] = None, 
                   **params) -> Dict:
        """
        Upload a file to S3 via the microservice.
        
        Args:
            file_path: Path to the file to upload
            user_id: User ID for file ownership
            file_name: Custom file name (defaults to original file name)
            **params: Additional parameters to include in the file metadata
            
        Returns:
            Response from the API containing file info
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        url = f"{self.base_url}/api/upload"
        
        # If file_name not provided, use the original file name
        if not file_name:
            file_name = os.path.basename(file_path)
        
        # Detect file type and add to params
        file_info = self._detect_file_type(file_path)
        
        # Prepare form data
        form_data = {
            "userId": user_id,
            "fileName": file_name,
        }
        
        # Add file type information to params if not explicitly provided
        if 'document_type' not in params:
            params['document_type'] = file_info['document_category']
        
        if 'file_type' not in params:
            params['file_type'] = file_info['file_type']
            
        # Add additional parameters
        form_data.update(params)
        
        # Prepare file data
        with open(file_path, 'rb') as file:
            files = {'file': (file_name, file, file_info['content_type'])}
            response = requests.post(url, data=form_data, files=files)
            
        # Check if request was successful
        response.raise_for_status()
        
        return response.json()
    
    def get_user_files(self, user_id: str, **filters) -> Dict:
        """
        Get all files uploaded by a user, with optional filtering.
        
        Args:
            user_id: User ID to fetch files for
            **filters: Optional filters for metadata
            
        Returns:
            List of files matching the criteria
        """
        url = f"{self.base_url}/api/files/{user_id}"
        
        # Add filters as query parameters
        response = requests.get(url, params=filters)
        response.raise_for_status()
        
        return response.json()
    
    def get_file_metadata(self, file_id: str) -> Dict:
        """
        Get metadata for a specific file.
        
        Args:
            file_id: ID of the file
            
        Returns:
            File metadata
        """
        url = f"{self.base_url}/api/file/{file_id}"
        
        response = requests.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def get_download_url(self, file_id: str, expires_in: int = 3600) -> Dict:
        """
        Get a pre-signed URL for downloading a file.
        
        Args:
            file_id: ID of the file
            expires_in: URL expiration time in seconds
            
        Returns:
            Download URL information
        """
        url = f"{self.base_url}/api/download/{file_id}"
        
        params = {"expiresIn": expires_in}
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def download_file(self, file_id: str, destination_path: str) -> str:
        """
        Download a file to a local destination.
        
        Args:
            file_id: ID of the file to download
            destination_path: Path where the file should be saved
            
        Returns:
            Path to the downloaded file
        """
        try:
            # Get the download URL
            download_info = self.get_download_url(file_id)
            
            if not download_info.get('success'):
                raise Exception(f"Failed to get download URL: {download_info}")
            
            # Get the file content - use the URL as-is without any modification
            download_url = download_info['downloadUrl']
            print(f"Attempting to download from: {download_url}")
            
            # Simple direct download attempt using the pre-signed URL directly
            response = requests.get(download_url)
            
            if response.status_code == 200:
                # Determine the filename
                file_name = download_info.get('fileName', f"download_{file_id}")
                
                # If destination_path is a directory, append the filename
                if os.path.isdir(destination_path):
                    full_path = os.path.join(destination_path, file_name)
                else:
                    full_path = destination_path
                
                # Write the file
                with open(full_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"File successfully downloaded to: {full_path}")
                return full_path
            else:
                # If the direct download failed, try using the original URL
                metadata = self.get_file_metadata(file_id)
                original_url = metadata['file']['url']
                
                print(f"Pre-signed URL download failed with status {response.status_code}, trying direct URL")
                print(f"Attempting direct download from: {original_url}")
                
                direct_response = requests.get(original_url)
                
                if direct_response.status_code == 200:
                    # If destination_path is a directory, append the filename
                    file_name = download_info.get('fileName', f"download_{file_id}")
                    if os.path.isdir(destination_path):
                        full_path = os.path.join(destination_path, file_name)
                    else:
                        full_path = destination_path
                    
                    # Write the file
                    with open(full_path, 'wb') as f:
                        f.write(direct_response.content)
                    
                    print(f"File successfully downloaded to: {full_path}")
                    return full_path
                else:
                    raise Exception(f"Both pre-signed and direct URL downloads failed with status codes {response.status_code} and {direct_response.status_code}")
        
        except Exception as e:
            print(f"Download error: {str(e)}")
            raise Exception(f"Failed to download file: {str(e)}")
    
    def extract_bucket_name(self, url: str) -> str:
        """Extract the bucket name from an S3 URL."""
        # Parse the URL
        parsed_url = requests.utils.urlparse(url)
        
        # Extract hostname which will be something like bucket-name.s3.region.amazonaws.com
        hostname = parsed_url.netloc
        
        # Extract the bucket name
        if '.s3.' in hostname:
            return hostname.split('.s3.')[0]
        
        # Alternative format: s3.region.amazonaws.com/bucket-name/
        if hostname.startswith('s3.') and parsed_url.path.startswith('/'):
            path_parts = parsed_url.path.split('/')
            if len(path_parts) > 1:
                return path_parts[1]
        
        # If we can't determine the bucket name, return the hostname
        return hostname
    
    def delete_file(self, file_id: str) -> Dict:
        """
        Delete a file from S3 and database.
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            Result of the deletion operation
        """
        url = f"{self.base_url}/api/file/{file_id}"
        
        response = requests.delete(url)
        response.raise_for_status()
        
        return response.json()
    
    def search_files(self, user_id: str, **search_params) -> List[Dict]:
        """
        Search for files with specific metadata parameters.
        
        Args:
            user_id: User ID to search files for
            **search_params: Search parameters for metadata fields
            
        Returns:
            List of matching files
        """
        try:
            # Get all files for the user
            result = self.get_user_files(user_id)
            
            if not result.get('success'):
                return []
            
            # Filter files client-side based on metadata
            if search_params:
                files = result.get('files', [])
                filtered_files = []
                
                for file in files:
                    file_metadata = file.get('metadata', {})
                    match = True
                    
                    # Check if all search parameters match
                    for key, value in search_params.items():
                        if key not in file_metadata or str(file_metadata[key]) != str(value):
                            match = False
                            break
                    
                    if match:
                        filtered_files.append(file)
                        
                return filtered_files
            else:
                return result.get('files', [])
        except Exception as e:
            print(f"Error searching files: {str(e)}")
            return []
    
    def simple_upload(self, file_name: str, user_id: str = "default-user") -> Dict:
        """
        Upload a file to S3 using just the file name.
        
        Args:
            file_name: Name of the file to upload
            user_id: User ID for file ownership
            
        Returns:
            Response from the API containing file info
        """
        if not os.path.exists(file_name):
            raise FileNotFoundError(f"File not found: {file_name}")
            
        url = f"{self.base_url}/api/upload"
        
        # Detect file type and add to params
        file_info = self._detect_file_type(file_name)
        
        # Prepare form data
        form_data = {
            "userId": user_id,
            "fileName": os.path.basename(file_name),
            "document_type": file_info['document_category'],
            "file_type": file_info['file_type']
        }
        
        # Prepare file data
        with open(file_name, 'rb') as file:
            files = {'file': (os.path.basename(file_name), file, file_info['content_type'])}
            response = requests.post(url, data=form_data, files=files)
            
        # Check if request was successful
        response.raise_for_status()
        
        return response.json()
    
    def simple_download(self, file_name: str, destination_folder: str = "./downloads") -> str:
        """
        Download a file by its name to a local destination.
        
        Args:
            file_name: Name of the file to download
            destination_folder: Folder where the file should be saved
            
        Returns:
            Path to the downloaded file
        """
        try:
            # First get all files to find the one with matching name
            all_files = self.get_user_files("default-user")
            
            if not all_files.get('success'):
                raise Exception("Failed to get user files")
            
            # Find file with matching name
            file_id = None
            for file in all_files.get('files', []):
                if file.get('name') == file_name or file.get('originalName') == file_name:
                    file_id = file.get('id')
                    break
            
            if not file_id:
                raise Exception(f"File with name '{file_name}' not found")
            
            # Make sure destination folder exists
            os.makedirs(destination_folder, exist_ok=True)
            
            # Download using existing method
            return self.download_file(file_id, destination_folder)
            
        except Exception as e:
            print(f"Download error: {str(e)}")
            raise Exception(f"Failed to download file: {str(e)}")
