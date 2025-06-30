import json
import os
import uuid
import datetime
import boto3
import mysql.connector
from mysql.connector import pooling
import pandas as pd
from io import BytesIO
import xmltodict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from botocore.exceptions import ClientError



# Database connection pool
db_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="export_pool",
    pool_size=5,
    host=os.environ.get('DB_HOST', 'localhost'),
    user=os.environ.get('DB_USER', 'root'),
    password=os.environ.get('DB_PASSWORD', 'root'),
    database=os.environ.get('DB_NAME', 'grc')
)

# S3 client setup
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION', 'us-east-1')
)

BUCKET_NAME = os.environ.get('S3_BUCKET', 'orcashoimages')

# Ensure S3 bucket exists
def ensure_bucket_exists():
    """Create the S3 bucket if it doesn't exist"""
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket {BUCKET_NAME} exists")
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == '404' or error_code == 'NoSuchBucket':
            print(f"Bucket {BUCKET_NAME} does not exist, creating...")
            try:
                region = os.environ.get('AWS_REGION', 'us-east-1')
                if region == 'us-east-1':
                    s3_client.create_bucket(Bucket=BUCKET_NAME)
                else:
                    s3_client.create_bucket(
                        Bucket=BUCKET_NAME,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                print(f"Bucket {BUCKET_NAME} created successfully")
            except ClientError as create_error:
                print(f"Failed to create bucket: {str(create_error)}")
                raise
        else:
            print(f"Error checking bucket: {str(e)}")
            raise

# Try to ensure bucket exists on module import
try:
    ensure_bucket_exists()
except Exception as e:
    print(f"Warning: Could not ensure S3 bucket exists: {str(e)}")
    print("File uploads to S3 may fail - will save files locally instead")

# Sample data for testing
# SAMPLE_DATA = [
#     {"id": 1, "name": "John Doe", "email": "john@example.com", "department": "IT", "salary": 75000},
#     {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "department": "HR", "salary": 65000},
#     {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "department": "Marketing", "salary": 60000},
#     {"id": 4, "name": "Alice Brown", "email": "alice@example.com", "department": "Finance", "salary": 80000},
#     {"id": 5, "name": "Charlie Wilson", "email": "charlie@example.com", "department": "IT", "salary": 70000}
# ]

def get_db_connection():
    """Get a connection from the connection pool"""
    return db_pool.get_connection()

def save_export_record(export_data):
    """Save export record to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        INSERT INTO exported_files 
        (export_data, file_type, user_id, s3_url, file_name, status, metadata, created_at, updated_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.datetime.now()
        
        cursor.execute(query, (
            json.dumps(export_data.get('export_data')),
            export_data.get('file_type'),
            export_data.get('user_id'),
            export_data.get('s3_url', ''),  # S3 URL initially empty
            export_data.get('file_name'),
            export_data.get('status', 'pending'),
            json.dumps(export_data.get('metadata', {})),
            now,
            now
        ))
        
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def update_export_status(export_id, status, error=None):
    """Update export record status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        UPDATE exported_files 
        SET status = %s, error = %s, updated_at = %s
        """
        
        params = [status, error, datetime.datetime.now()]
        
        if status == 'completed':
            query += ", completed_at = %s"
            params.append(datetime.datetime.now())
            
        query += " WHERE id = %s"
        params.append(export_id)
        
        cursor.execute(query, params)
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def update_export_metadata(export_id, metadata):
    """Update export metadata"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get existing metadata
        cursor.execute("SELECT metadata FROM exported_files WHERE id = %s", (export_id,))
        result = cursor.fetchone()
        
        if result:
            existing_metadata = json.loads(result[0] or '{}')
            updated_metadata = {**existing_metadata, **metadata}
            
            cursor.execute(
                "UPDATE exported_files SET metadata = %s, updated_at = %s WHERE id = %s",
                (json.dumps(updated_metadata), datetime.datetime.now(), export_id)
            )
            conn.commit()
    finally:
        cursor.close()
        conn.close()

def update_export_url(export_id, s3_url):
    """Update export record with S3 URL"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE exported_files SET s3_url = %s, updated_at = %s WHERE id = %s",
            (s3_url, datetime.datetime.now(), export_id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def export_to_excel(data):
    """Export data to Excel format"""
    try:
        df = pd.DataFrame(data)
        output = BytesIO()
        
        # Try to use xlsxwriter engine
        try:
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Export', index=False)
                workbook = writer.book
                worksheet = writer.sheets['Export']
                
                # Format the header
                header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    
                # Adjust column width
                for i, col in enumerate(df.columns):
                    column_width = max(df[col].astype(str).map(len).max(), len(col))
                    worksheet.set_column(i, i, column_width + 2)
        except ImportError:
            # Fall back to openpyxl if xlsxwriter is not available
            print("xlsxwriter not found, trying openpyxl instead...")
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Export', index=False)
    
        output.seek(0)
        return output.getvalue()
        
    except ImportError as e:
        # If neither excel writer is available, save as CSV instead
        print(f"Excel libraries not available: {str(e)}. Saving as CSV instead.")
        csv_data = export_to_csv(data)
        # Update the error message for clarity
        raise ImportError(f"Excel export failed - missing libraries. File saved as CSV instead: {str(e)}")

def export_to_csv(data):
    """Export data to CSV format"""
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output.getvalue()

def export_to_json(data):
    """Export data to JSON format"""
    return json.dumps(data, indent=2).encode('utf-8')

def export_to_xml(data):
    """Export data to XML format"""
    root_name = 'export'
    if isinstance(data, list):
        xml_data = {root_name: {'item': data}}
    else:
        xml_data = {root_name: data}
    
    xml_string = xmltodict.unparse(xml_data, pretty=True)
    return xml_string.encode('utf-8')

def export_to_pdf(data):
    """Export data to PDF format"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(width/2 - 50, height - 50, "Export Report")
    
    # Add data
    c.setFont("Helvetica", 12)
    y_position = height - 100
    
    if isinstance(data, list):
        for i, item in enumerate(data):
            c.drawString(50, y_position, f"Item {i+1}:")
            y_position -= 20
            
            for key, value in item.items():
                c.drawString(70, y_position, f"{key}: {value}")
                y_position -= 20
                
                if y_position < 50:  # Add a new page if needed
                    c.showPage()
                    y_position = height - 50
    else:
        for key, value in data.items():
            c.drawString(50, y_position, f"{key}: {value}")
            y_position -= 20
            
            if y_position < 50:  # Add a new page if needed
                c.showPage()
                y_position = height - 50
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

def export_to_txt(data):
    """Export data to Text format"""
    buffer = BytesIO()
    
    buffer.write(b"Export Report\n")
    buffer.write(b"=" * 50 + b"\n\n")
    buffer.write(f"Generated: {datetime.datetime.now().isoformat()}\n\n".encode('utf-8'))
    
    def format_item(item, level=0):
        indent = "  " * level
        
        if isinstance(item, list):
            for i, element in enumerate(item):
                buffer.write(f"{indent}Item {i+1}:\n".encode('utf-8'))
                format_item(element, level + 1)
        elif isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, (dict, list)):
                    buffer.write(f"{indent}{key}:\n".encode('utf-8'))
                    format_item(value, level + 1)
                else:
                    buffer.write(f"{indent}{key}: {value}\n".encode('utf-8'))
        else:
            buffer.write(f"{indent}{item}\n".encode('utf-8'))
    
    format_item(data)
    
    buffer.write(b"\n" + b"=" * 50 + b"\n")
    buffer.write(b"End of Report")
    
    buffer.seek(0)
    return buffer.getvalue()

def upload_to_s3(file_buffer, file_name, content_type):
    """Upload file to S3 bucket"""
    key = f"exports/{file_name}"
    
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=file_buffer,
            ContentType=content_type
        )
        
        # Generate URL for the uploaded file
        url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"
        
        return {
            'url': url,
            'bucket': BUCKET_NAME,
            'key': key,
            'region': os.environ.get('AWS_REGION', 'us-east-1')
        }
    except ClientError as e:
        print(f"S3 upload failed: {str(e)}")
        # Save locally as fallback
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        local_path = os.path.join(downloads_path, file_name)
        
        with open(local_path, 'wb') as f:
            f.write(file_buffer)
            
        print(f"File saved locally instead at: {local_path}")
        return {
            'url': f"file://{local_path}",
            'bucket': 'local',
            'key': local_path,
            'region': 'local'
        }

def get_content_type(file_type):
    """Get content type based on file extension"""
    content_types = {
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'csv': 'text/csv',
        'json': 'application/json',
        'xml': 'application/xml',
        'txt': 'text/plain'
    }
    
    return content_types.get(file_type, 'application/octet-stream')

def export_data(data=None, file_format='xlsx', user_id='user123', options=None):
    """
    Export data to the specified format and save to S3
    
    Args:
        data: The data to export (uses sample data if None)
        file_format: Format to export (xlsx, pdf, csv, json, xml, txt)
        user_id: ID of the user requesting the export
        options: Additional export options
        
    Returns:
        Dictionary with export results
    """
    if data is None:
        data = SAMPLE_DATA
        
    if options is None:
        options = {}
    
    export_id = None
    timestamp = datetime.datetime.now().timestamp()
    file_name = f"export_{user_id}_{int(timestamp)}.{file_format}"
    local_path = None
    
    try:
        # Validate format
        export_functions = {
            'xlsx': export_to_excel,
            'pdf': export_to_pdf,
            'csv': export_to_csv,
            'json': export_to_json,
            'xml': export_to_xml,
            'txt': export_to_txt
        }
        
        if file_format not in export_functions:
            raise ValueError(f"Unsupported export format: {file_format}")
        
        # Create export record
        export_id = save_export_record({
            'export_data': data,
            'file_type': file_format,
            'user_id': user_id,
            'file_name': file_name,
            'status': 'pending',
            'metadata': {
                'record_count': len(data) if isinstance(data, list) else 1,
                'filters': options.get('filters', {}),
                'columns': options.get('columns', [])
            }
        })
        
        # Update status to processing
        update_export_status(export_id, 'processing')
        
        # Export to file
        print(f"Converting data to {file_format} format...")
        start_time = datetime.datetime.now()
        file_buffer = export_functions[file_format](data)
        print(f"Data converted successfully. File size: {len(file_buffer)} bytes")
        
        # Save locally first
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        local_path = os.path.join(downloads_path, file_name)
        with open(local_path, 'wb') as f:
            f.write(file_buffer)
        print(f"File saved locally at: {local_path}")
        
        # Try S3 upload
        s3_result = None
        try:
            print(f"Attempting to upload file to S3: {file_name}")
            content_type = get_content_type(file_format)
            s3_result = upload_to_s3(file_buffer, file_name, content_type)
            print(f"File uploaded successfully to S3: {s3_result['url']}")
            
            # Update the S3 URL in the database
            update_export_url(export_id, s3_result['url'])
        except Exception as s3_error:
            print(f"S3 upload failed: {str(s3_error)}")
            # Use local file as fallback
            s3_result = {
                'url': f"file://{local_path}",
                'bucket': 'local',
                'key': local_path,
                'region': 'local'
            }
            # Update with local file URL
            update_export_url(export_id, s3_result['url'])
        
        # Update export record with metadata
        duration = (datetime.datetime.now() - start_time).total_seconds() * 1000
        update_export_metadata(export_id, {
            'file_size': len(file_buffer),
            'export_duration': duration,
            's3_metadata': {
                'bucket': s3_result['bucket'],
                'key': s3_result['key'],
                'region': s3_result['region'],
                'upload_time': datetime.datetime.now().isoformat()
            }
        })
        
        # Update status to completed
        update_export_status(export_id, 'completed')
        
        return {
            'success': True,
            'export_id': export_id,
            'file_url': s3_result['url'],
            'file_name': file_name,
            'local_path': local_path,
            'metadata': {
                'file_size': len(file_buffer),
                'format': file_format,
                'record_count': len(data) if isinstance(data, list) else 1,
                'export_duration': duration
            }
        }
        
    except Exception as e:
        print(f"Export error: {str(e)}")
        if export_id:
            update_export_status(export_id, 'failed', str(e))
            update_export_metadata(export_id, {
                'error': {
                    'message': str(e),
                    'timestamp': datetime.datetime.now().isoformat(),
                    'local_path': local_path
                }
            })
            
            # Update with local file URL if available
            if local_path:
                update_export_url(export_id, f"file://{local_path}")
        
        # Re-raise but provide local path information if available
        if local_path:
            raise Exception(f"{str(e)} (File saved locally at: {local_path})")
        else:
            raise

# # Example usage with sample data
# if __name__ == "__main__":
#     result = export_data(SAMPLE_DATA, 'xlsx', 'test_user')
#     print(f"Export successful. File URL: {result['file_url']}") 