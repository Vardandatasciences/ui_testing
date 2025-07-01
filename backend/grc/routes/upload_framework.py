from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import threading
import time
import shutil
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.cache import cache
import pandas as pd
import re
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from grc.models import Framework, Policy, SubPolicy, Compliance

# Import the processing function from final_adithya.py
from grc.routes.final_adithya import extract_document_sections
from grc.routes.policy_text_extract import process_checked_sections

# Global progress tracking
processing_status = {}

def update_progress(task_id, progress, message):
    """Update processing progress"""
    processing_status[task_id] = {
        'progress': progress,
        'message': message,
        'timestamp': time.time()
    }
    cache.set(f'processing_{task_id}', processing_status[task_id], timeout=3600)

def process_pdf_framework(pdf_path, task_id, output_dir):
    """Main PDF processing function with progress tracking"""
    try:
        update_progress(task_id, 5, "Starting PDF processing...")
        
        # Call the extract_document_sections function with progress updates
        def progress_callback(progress, message):
            update_progress(task_id, progress, message)
        
        # Process the PDF using the extract_document_sections function with custom output directory
        update_progress(task_id, 10, "Extracting document sections...")
        result_output_dir = extract_document_sections(pdf_path, output_dir)
        
        if not result_output_dir:
            update_progress(task_id, 100, "Error: Failed to extract document sections")
            return False
            
        # Store the output directory path for later use
        cache.set(f'output_dir_{task_id}', result_output_dir, timeout=3600)
        
        update_progress(task_id, 100, "PDF processing completed successfully!")
        return True
        
    except Exception as e:
        update_progress(task_id, 100, f"Error: {str(e)}")
        return False

@csrf_exempt
@require_http_methods(["POST"])
def upload_framework_file(request):
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        uploaded_file = request.FILES['file']
        
        # Validate file type
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls']
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'error': f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'
            }, status=400)
        
        # Generate task ID for progress tracking
        task_id = f"upload_{int(time.time())}_{uploaded_file.name}"
        
        # Create task-specific upload directory
        upload_dir = os.path.join('framework_uploads', task_id)
        full_upload_dir = os.path.join(settings.MEDIA_ROOT, upload_dir)
        if not os.path.exists(full_upload_dir):
            os.makedirs(full_upload_dir)
        
        # Save file in task-specific directory
        file_path = os.path.join(upload_dir, uploaded_file.name)
        saved_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))
        full_file_path = os.path.join(settings.MEDIA_ROOT, saved_path)
        
        # Create output directory for extracted sections
        output_dir = os.path.join(settings.MEDIA_ROOT, 'extracted_sections', task_id)
        
        # Start actual PDF processing in background thread
        def background_process():
            try:
                update_progress(task_id, 5, "Starting PDF processing...")
                
                # Only process PDF files with the extraction function
                if file_extension.lower() == '.pdf':
                    update_progress(task_id, 10, "Extracting document sections from PDF...")
                    result = process_pdf_framework(full_file_path, task_id, output_dir)
                    
                    if result:
                        update_progress(task_id, 100, "PDF processing completed successfully!")
                    else:
                        update_progress(task_id, 100, "Error: PDF processing failed")
                else:
                    # For non-PDF files, create a simple structure
                    update_progress(task_id, 20, f"Processing {file_extension} file...")
                    
                    # Create basic output structure for non-PDF files
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Create a simple section based on filename
                    filename_base = os.path.splitext(uploaded_file.name)[0]
                    section_dir = os.path.join(output_dir, f"1 {filename_base}")
                    json_dir = os.path.join(section_dir, "json_chunks")
                    txt_dir = os.path.join(section_dir, "txt_chunks")
                    
                    os.makedirs(json_dir, exist_ok=True)
                    os.makedirs(txt_dir, exist_ok=True)
                    
                    # Read file content based on type
                    content = ""
                    if file_extension.lower() in ['.txt']:
                        with open(full_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                    elif file_extension.lower() in ['.doc', '.docx']:
                        try:
                            import docx
                            doc = docx.Document(full_file_path)
                            content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                        except:
                            content = f"Could not extract content from {uploaded_file.name}"
                    elif file_extension.lower() in ['.xlsx', '.xls']:
                        try:
                            df = pd.read_excel(full_file_path)
                            content = df.to_string()
                        except:
                            content = f"Could not extract content from {uploaded_file.name}"
                    
                    # Save content to files
                    with open(os.path.join(txt_dir, f"{filename_base}.txt"), 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    json_data = {
                        "subheading": filename_base,
                        "start_text": content[:50],
                        "content": content
                    }
                    with open(os.path.join(json_dir, f"{filename_base}.json"), 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2)
                    
                    # Store the output directory path for later use
                    cache.set(f'output_dir_{task_id}', output_dir, timeout=3600)
                    
                    update_progress(task_id, 100, f"{file_extension.upper()} file processed successfully!")
                    
            except Exception as e:
                update_progress(task_id, 100, f"Error: {str(e)}")
        
        thread = threading.Thread(target=background_process)
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            'message': 'File uploaded successfully. Processing started.',
            'filename': uploaded_file.name,
            'file_path': saved_path,
            'file_size': uploaded_file.size,
            'task_id': task_id,
            'processing': True,
            'file_type': file_extension
        }, status=200)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_processing_status(request, task_id):
    """Get processing status for a task"""
    try:
        status = cache.get(f'processing_{task_id}')
        if status:
            return JsonResponse(status)
        else:
            return JsonResponse({
                'progress': 0,
                'message': 'Task not found or expired',
                'error': True
            }, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_sections(request, task_id):
    """Get extracted sections for a processed document"""
    try:
        # Get the output directory from cache
        output_dir = cache.get(f'output_dir_{task_id}')
        if not output_dir or not os.path.exists(output_dir):
            return JsonResponse({'error': 'Extracted sections not found'}, status=404)
        
        sections = []
        
        # List all directories in the extracted_sections folder
        dir_list = [d for d in os.listdir(output_dir) 
                    if os.path.isdir(os.path.join(output_dir, d))]
        
        # Sort directories to ensure consistent order
        dir_list.sort()
        
        for section_dir in dir_list:
            section_path = os.path.join(output_dir, section_dir)
            section = {
                'name': section_dir,
                'subsections': []
            }
            
            # Check for subdirectories like json_chunks and txt_chunks
            subdir_list = [d for d in os.listdir(section_path) 
                          if os.path.isdir(os.path.join(section_path, d))]
            
            for subdir in subdir_list:
                subdir_path = os.path.join(section_path, subdir)
                
                # Get all files in the subdir
                try:
                    files = [f for f in os.listdir(subdir_path) 
                            if os.path.isfile(os.path.join(subdir_path, f))]
                    
                    for file_name in files:
                        file_path = os.path.join(subdir_path, file_name)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # Try to parse as JSON if it's in json_chunks
                            if subdir == "json_chunks":
                                try:
                                    json_data = json.loads(content)
                                    content = json.dumps(json_data, indent=2)
                                except json.JSONDecodeError:
                                    pass
                            
                            # Include the subdir in the name for clarity
                            display_name = f"{subdir}/{file_name}"
                            
                            section['subsections'].append({
                                'name': display_name,
                                'content': content
                            })
                        except Exception as e:
                            section['subsections'].append({
                                'name': f"{subdir}/{file_name}",
                                'content': f"Error reading file: {str(e)}"
                            })
                except Exception as e:
                    print(f"Error listing files in {subdir_path}: {str(e)}")
            
            # Also check for files directly in the section directory
            direct_files = [f for f in os.listdir(section_path) 
                           if os.path.isfile(os.path.join(section_path, f))]
            
            for file_name in direct_files:
                file_path = os.path.join(section_path, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Try to parse as JSON if it ends with .json
                    if file_name.endswith('.json'):
                        try:
                            json_data = json.loads(content)
                            content = json.dumps(json_data, indent=2)
                        except json.JSONDecodeError:
                            pass
                    
                    section['subsections'].append({
                        'name': file_name,
                        'content': content
                    })
                except Exception as e:
                    section['subsections'].append({
                        'name': file_name,
                        'content': f"Error reading file: {str(e)}"
                    })
            
            # Add section even if empty
            sections.append(section)
        
        return JsonResponse(sections, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_section(request):
    """Update section content"""
    try:
        data = json.loads(request.body)
        section_name = data.get('section')
        subsection_name = data.get('subsection')
        content = data.get('content')
        task_id = data.get('task_id')
        
        if not all([section_name, subsection_name, content, task_id]):
            return JsonResponse({'error': 'Missing required data'}, status=400)
        
        # Get the output directory from cache
        output_dir = cache.get(f'output_dir_{task_id}')
        if not output_dir or not os.path.exists(output_dir):
            return JsonResponse({'error': 'Extracted sections not found'}, status=404)
        
        # Handle subsection paths that include subdirectories like "json_chunks/file.json"
        if '/' in subsection_name:
            subdir, file_name = subsection_name.split('/', 1)
            file_path = os.path.join(output_dir, section_name, subdir, file_name)
        else:
            file_path = os.path.join(output_dir, section_name, subsection_name)
        
        # Check if content is JSON
        is_json = False
        if subsection_name.endswith('.json') or ('json_chunks' in subsection_name):
            try:
                json_content = json.loads(content)
                is_json = True
            except json.JSONDecodeError:
                is_json = False
        
        # Write the content
        with open(file_path, 'w', encoding='utf-8') as f:
            if is_json:
                json.dump(json_content, f, indent=2)
            else:
                f.write(content)
        
        return JsonResponse({'message': 'Section updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_checked_structure(request):
    """Create structure with checked items"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        sections_data = data.get('sections', [])
        
        if not task_id or not sections_data:
            return JsonResponse({'error': 'Missing required data'}, status=400)
        
        # Get the output directory from cache
        output_dir = cache.get(f'output_dir_{task_id}')
        if not output_dir or not os.path.exists(output_dir):
            return JsonResponse({'error': 'Extracted sections not found'}, status=404)
        
        # Create output directory for checked items
        checked_output_dir = os.path.join(settings.MEDIA_ROOT, 'checked_sections', task_id)
        
        # Delete existing checked_sections directory if it exists
        if os.path.exists(checked_output_dir):
            print(f"Removing existing checked_sections directory: {checked_output_dir}")
            shutil.rmtree(checked_output_dir)
        
        os.makedirs(checked_output_dir, exist_ok=True)
        print(f"Created checked_sections directory: {checked_output_dir}")
        
        # Process each section
        for section in sections_data:
            section_name = section.get('name')
            subsections = section.get('subsections', [])
            
            # Skip sections with no subsections
            if not section_name or not subsections:
                continue
            
            # Create section directory
            section_dir = os.path.join(checked_output_dir, section_name)
            os.makedirs(section_dir, exist_ok=True)
            
            # Process each subsection
            for subsection in subsections:
                subsection_name = subsection.get('name')
                content = subsection.get('content')
                
                if not subsection_name or content is None:
                    continue
                
                # Handle subsection paths that include subdirectories like "json_chunks/file.json"
                if '/' in subsection_name:
                    subdir, file_name = subsection_name.split('/', 1)
                    subdir_path = os.path.join(section_dir, subdir)
                    os.makedirs(subdir_path, exist_ok=True)
                    file_path = os.path.join(subdir_path, file_name)
                else:
                    file_path = os.path.join(section_dir, subsection_name)
                
                # Write the content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        # Start processing in background thread
        def background_process():
            # Process the checked sections to extract policy information
            update_progress(task_id, 50, "Processing checked sections to extract policy information...")
            excel_path = process_checked_sections(task_id)
            
            if excel_path:
                update_progress(task_id, 100, "Policy extraction completed successfully!")
                # Cache the Excel file path for later retrieval
                cache.set(f'policy_excel_{task_id}', excel_path, timeout=3600)
            else:
                update_progress(task_id, 100, "Error: Failed to extract policy information")
        
        thread = threading.Thread(target=background_process)
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            'message': 'Checked sections created successfully. Policy extraction has started.',
            'task_id': task_id,
            'status': 'processing'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_extracted_policies(request, task_id):
    """Get extracted policy information from Excel file"""
    try:
        # First check if we have cached policies
        cached_policies = cache.get(f'extracted_policies_{task_id}')
        if cached_policies:
            return JsonResponse({
                'policies': cached_policies,
                'filename': f"cached_policies_{task_id}.xlsx",
                'excel_path': f"cached_policies_{task_id}.xlsx",
                'total_policies': len(cached_policies),
                'source': 'cache'
            })
        
        # If not in cache, check in the extracted_policies directory
        media_root = settings.MEDIA_ROOT
        extracted_policies_dir = os.path.join(media_root, 'extracted_policies', task_id)
        
        if not os.path.exists(extracted_policies_dir):
            os.makedirs(extracted_policies_dir, exist_ok=True)
            
            # No directory exists, create a sample Excel file with default data
            # This ensures we always have something to show even if processing failed
            sample_policies = [
                {
                    'section_name': '3.1 ACCESS CONTROL',
                    'file_name': 'sample.txt',
                    'Sub_policy_id': 'AC-1',
                    'sub_policy_name': 'Access Control Policy and Procedures',
                    'control': 'Develop, document, and disseminate to all personnel: Access control policy that addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance.',
                    'discussion': '',
                    'related_controls': 'PM-9, PS-8, SI-12',
                    'control_enhancements': '',
                    'references': 'NIST SP 800-12, NIST SP 800-30'
                }
            ]
            
            # Create a DataFrame and save to Excel
            df = pd.DataFrame(sample_policies)
            output_file = os.path.join(extracted_policies_dir, f"extracted_policies_{task_id}.xlsx")
            df.to_excel(output_file, index=False)
            
            # Cache the policies
            cache.set(f'extracted_policies_{task_id}', sample_policies, timeout=3600)
            
            return JsonResponse({
                'policies': sample_policies,
                'filename': os.path.basename(output_file),
                'excel_path': os.path.basename(output_file),
                'total_policies': len(sample_policies),
                'source': 'generated_sample'
            })
        
        # Look for any Excel file in the directory
        excel_files = [f for f in os.listdir(extracted_policies_dir) if f.endswith('.xlsx')]
        
        if not excel_files:
            # No Excel files found, create an empty one
            empty_df = pd.DataFrame(columns=[
                'section_name', 'file_name', 'Sub_policy_id', 'sub_policy_name', 
                'control', 'discussion', 'related_controls', 'control_enhancements', 'references'
            ])
            
            output_file = os.path.join(extracted_policies_dir, f"extracted_policies_{task_id}.xlsx")
            empty_df.to_excel(output_file, index=False)
            
            return JsonResponse({
                'policies': [],
                'filename': os.path.basename(output_file),
                'excel_path': os.path.basename(output_file),
                'total_policies': 0,
                'source': 'empty_generated'
            })
            
        # Use the first Excel file found
        excel_path = os.path.join(extracted_policies_dir, excel_files[0])
        
        # Read the Excel file
        df = pd.read_excel(excel_path)
        
        # Convert DataFrame to list of dictionaries
        policies = df.fillna('').to_dict(orient='records')
        
        # Cache the policies for future use
        cache.set(f'extracted_policies_{task_id}', policies, timeout=3600)
        
        return JsonResponse({
            'policies': policies,
            'filename': os.path.basename(excel_path),
            'excel_path': os.path.basename(excel_path),
            'total_policies': len(policies),
            'source': 'excel_file'
        })
    
    except Exception as e:
        print(f"Error in get_extracted_policies: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def direct_process_checked_sections(request):
    """
    Directly process the existing checked_sections directory without requiring upload or selection.
    This is a shortcut for development and testing.
    """
    try:
        # Create a task ID
        task_id = f"direct_{int(time())}"
        
        # Update progress status
        update_progress(task_id, 10, "Starting direct policy extraction...")
        
        # Get the checked_sections directory
        checked_sections_dir = os.path.join(settings.MEDIA_ROOT, 'checked_sections')
        
        if not os.path.exists(checked_sections_dir):
            return JsonResponse({'error': 'Checked sections directory not found'}, status=404)
            
        # Process the checked sections in the background
        def background_process():
            update_progress(task_id, 50, "Processing checked sections to extract policy information...")
            excel_path = process_checked_sections(task_id)
            
            if excel_path:
                update_progress(task_id, 100, "Policy extraction completed successfully!")
                # Cache the Excel file path for later retrieval
                cache.set(f'policy_excel_{task_id}', excel_path, timeout=3600)
            else:
                update_progress(task_id, 100, "Error: Failed to extract policy information")
        
        thread = threading.Thread(target=background_process)
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            'message': 'Direct policy extraction started',
            'task_id': task_id,
            'status': 'processing'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_updated_policies(request):
    """Save updated policy data to a new Excel file"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        policies = data.get('policies', [])
        
        if not task_id or not policies:
            return JsonResponse({'error': 'Missing required data'}, status=400)
        
        # Create DataFrame from updated policies
        df = pd.DataFrame(policies)
        
        # Ensure all expected columns exist (even if empty)
        expected_columns = [
            'section_name', 'file_name', 'Sub_policy_id', 'sub_policy_name', 
            'control', 'discussion', 'related_controls', 'control_enhancements', 'references'
        ]
        
        for col in expected_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Reorder columns to have section_name and file_name first
        df = df[expected_columns]
        
        # Create output directory for updated policies
        media_root = settings.MEDIA_ROOT
        updated_policies_dir = os.path.join(media_root, 'updated_policies')
        os.makedirs(updated_policies_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = int(time.time())
        output_file = os.path.join(updated_policies_dir, f"updated_policies_{task_id}_{timestamp}.xlsx")
        
        # Save to Excel
        df.to_excel(output_file, index=False)
        
        # Cache the updated Excel file path
        cache.set(f'updated_policy_excel_{task_id}', output_file, timeout=3600)
        
        return JsonResponse({
            'message': 'Policies updated successfully',
            'excel_path': os.path.basename(output_file),
            'file_path': output_file
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_policies(request):
    """Save all policies to Excel file with timestamp"""
    try:
        data = json.loads(request.body)
        policies = data.get('policies', [])
        filename = data.get('filename', 'policies')
        task_id = data.get('task_id', 'unknown')
        
        if not policies:
            return JsonResponse({'error': 'No policies provided'}, status=400)
        
        # Create DataFrame from policies
        df = pd.DataFrame(policies)
        
        # Ensure all expected columns exist (even if empty)
        expected_columns = [
            'section_name', 'file_name', 'Sub_policy_id', 'sub_policy_name', 
            'control', 'discussion', 'related_controls', 'control_enhancements', 'references'
        ]
        
        for col in expected_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Reorder columns
        df = df[expected_columns]
        
        # 1. Save to extracted_policies (original location)
        media_root = settings.MEDIA_ROOT
        extracted_policies_dir = os.path.join(media_root, 'extracted_policies', task_id)
        os.makedirs(extracted_policies_dir, exist_ok=True)
        
        source_file = os.path.join(extracted_policies_dir, f"extracted_policies_{task_id}.xlsx")
        df.to_excel(source_file, index=False)
        
        # 2. Create a copy in updated_policies with timestamp
        updated_policies_dir = os.path.join(media_root, 'updated_policies', task_id)
        os.makedirs(updated_policies_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = int(time.time())
        safe_filename = filename.replace('.xlsx', '').replace('.xls', '')
        output_file = os.path.join(updated_policies_dir, f"{safe_filename}_bulk_save_{timestamp}.xlsx")
        
        # Save to Excel
        df.to_excel(output_file, index=False)
        
        # Also update the cache for the task
        cache.set(f'extracted_policies_{task_id}', policies, timeout=3600)
        
        return JsonResponse({
            'message': 'All policies saved successfully',
            'original_file': os.path.basename(source_file),
            'updated_file': os.path.basename(output_file),
            'total_policies': len(policies),
            'timestamp': timestamp
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_single_policy(request):
    """Save a single updated policy and create new Excel file with timestamp"""
    try:
        data = json.loads(request.body)
        policy = data.get('policy')
        task_id = data.get('task_id', 'unknown')
        
        if not policy:
            return JsonResponse({'error': 'No policy provided'}, status=400)
        
        # Get current policies from cache or load from Excel
        cache_key = f'extracted_policies_{task_id}'
        cached_policies = cache.get(cache_key)
        
        if not cached_policies:
            # Try to load from the original Excel file
            try:
                media_root = settings.MEDIA_ROOT
                extracted_policies_dir = os.path.join(media_root, 'extracted_policies', task_id)
                
                if not os.path.exists(extracted_policies_dir):
                    os.makedirs(extracted_policies_dir, exist_ok=True)
                
                # Look for any Excel file in the directory
                excel_files = [f for f in os.listdir(extracted_policies_dir) if f.endswith('.xlsx')]
                
                if excel_files:
                    excel_path = os.path.join(extracted_policies_dir, excel_files[0])
                    df = pd.read_excel(excel_path)
                    cached_policies = df.fillna('').to_dict(orient='records')
                else:
                    cached_policies = []
            except Exception as e:
                return JsonResponse({'error': f'Failed to load policies: {str(e)}'}, status=500)
        
        # Find and update the policy
        policy_updated = False
        for i, cached_policy in enumerate(cached_policies):
            if cached_policy.get('Sub_policy_id') == policy.get('Sub_policy_id'):
                cached_policies[i] = policy
                policy_updated = True
                break
        
        if not policy_updated:
            # If policy not found, add it as new
            cached_policies.append(policy)
        
        # Update the cache
        cache.set(cache_key, cached_policies, timeout=3600)
        
        # Create output directory with task-specific subfolder for original and updated files
        media_root = settings.MEDIA_ROOT
        
        # 1. Save to extracted_policies (original location) to update the source file
        extracted_policies_dir = os.path.join(media_root, 'extracted_policies', task_id)
        os.makedirs(extracted_policies_dir, exist_ok=True)
        
        source_file = os.path.join(extracted_policies_dir, f"extracted_policies_{task_id}.xlsx")
        df = pd.DataFrame(cached_policies)
        
        # Ensure all expected columns exist
        expected_columns = [
            'section_name', 'file_name', 'Sub_policy_id', 'sub_policy_name', 
            'control', 'discussion', 'related_controls', 'control_enhancements', 'references'
        ]
        
        for col in expected_columns:
            if col not in df.columns:
                df[col] = ''
        
        df = df[expected_columns]
        
        # Save updated source file
        df.to_excel(source_file, index=False)
        
        # 2. Also save a copy to updated_policies with timestamp
        updated_policies_dir = os.path.join(media_root, 'updated_policies', task_id)
        os.makedirs(updated_policies_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = int(time.time())
        output_file = os.path.join(updated_policies_dir, f"updated_policy_{policy.get('Sub_policy_id')}_{timestamp}.xlsx")
        
        # Save to Excel
        df.to_excel(output_file, index=False)
        
        return JsonResponse({
            'message': 'Policy saved successfully',
            'original_file': os.path.basename(source_file),
            'updated_file': os.path.basename(output_file),
            'policy_id': policy.get('Sub_policy_id'),
            'updated': policy_updated,
            'timestamp': timestamp
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_saved_excel_files(request, task_id):
    """Get list of all saved Excel files for a task"""
    try:
        media_root = settings.MEDIA_ROOT
        updated_policies_dir = os.path.join(media_root, 'updated_policies', task_id)
        
        if not os.path.exists(updated_policies_dir):
            return JsonResponse({
                'files': [],
                'message': 'No saved files found for this task'
            })
        
        files = []
        for filename in os.listdir(updated_policies_dir):
            if filename.endswith('.xlsx'):
                file_path = os.path.join(updated_policies_dir, filename)
                file_stats = os.stat(file_path)
                
                # Extract timestamp from filename
                timestamp_match = filename.split('_')[-1].replace('.xlsx', '')
                try:
                    timestamp = int(timestamp_match)
                    created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
                except:
                    created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime))
                
                # Determine file type
                file_type = 'bulk_save' if 'bulk_save' in filename else 'single_edit'
                
                files.append({
                    'filename': filename,
                    'file_path': os.path.join('updated_policies', task_id, filename),
                    'size': file_stats.st_size,
                    'created_time': created_time,
                    'type': file_type
                })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x['created_time'], reverse=True)
        
        return JsonResponse({
            'files': files,
            'total_files': len(files),
            'task_id': task_id
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_policy_details(request):
    """Save policy details information (step 6)"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        details = data.get('details', {})
        
        if not task_id:
            return JsonResponse({'error': 'Task ID is required'}, status=400)
        
        # Get cached policy details or create new
        cached_details = cache.get(f'policy_details_{task_id}')
        if not cached_details:
            cached_details = {}
        
        # Update cached details with new data
        for key, value in details.items():
            cached_details[key] = value
        
        # Save updated details to cache
        cache.set(f'policy_details_{task_id}', cached_details, timeout=86400)  # 24-hour cache
        
        # Create policy details directory if it doesn't exist
        media_root = settings.MEDIA_ROOT
        policy_details_dir = os.path.join(media_root, 'policy_details', task_id)
        os.makedirs(policy_details_dir, exist_ok=True)
        
        # Save details to JSON file
        json_file_path = os.path.join(policy_details_dir, f"policy_details_{task_id}.json")
        with open(json_file_path, 'w') as f:
            json.dump(cached_details, f, indent=2)
        
        return JsonResponse({
            'message': 'Policy details saved successfully',
            'json_file': json_file_path
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_complete_policy_package(request):
    """Save complete policy package with 4-level hierarchy: Framework -> Policy -> Sub-Policy -> Compliance"""
    try:
        print("===== STARTING SAVE COMPLETE POLICY PACKAGE =====")
        data = json.loads(request.body)
        task_id = data.get('task_id')
        framework_details = data.get('framework_details', {})
        policy_forms = data.get('policy_forms', {})
        sub_policies = data.get('sub_policies', [])
        compliance_data = data.get('compliance_data', {})
        unique_sections = data.get('unique_sections', [])
        
        print(f"Task ID: {task_id}")
        print(f"Framework details: {framework_details.get('title', 'Untitled')}")
        print(f"Number of policies: {len(policy_forms)}")
        print(f"Number of sub-policies: {len(sub_policies)}")
        print(f"Number of compliance sections: {len(compliance_data)}")
        print(f"Unique sections: {unique_sections}")
        
        if not task_id:
            return JsonResponse({'error': 'Task ID is required'}, status=400)
        
        # Create directories if they don't exist
        media_root = settings.MEDIA_ROOT
        complete_package_dir = os.path.join(media_root, 'complete_packages', task_id)
        os.makedirs(complete_package_dir, exist_ok=True)
        
        # Create hierarchical JSON structure
        hierarchical_data = {
            "metadata": {
                "task_id": task_id,
                "creation_timestamp": int(time.time()),
                "creation_date": time.strftime('%Y-%m-%d %H:%M:%S'),
                "total_policies": len(policy_forms),
                "total_sub_policies": len(sub_policies),
                "total_compliance_items": sum(len(items) for items in compliance_data.values()),
                "unique_sections": unique_sections,
                "hierarchy_levels": 4
            },
            "hierarchy": {
                "level_1_framework": {
                    "level": 1,
                    "type": "framework",
                    "data": framework_details,
                    "children": []
                }
            }
        }
        
        # We'll skip creating Compliance records here and let save_framework_to_database handle it
        # Just build the hierarchical structure
        
        flat_data = []  # Initialize flat_data here
        
        # Build hierarchy: Framework -> Policies -> Sub-policies
        for section_index, section_name in enumerate(unique_sections):
            # Level 2: Policy for this section
            policy_data = policy_forms.get(section_name, {})
            policy_node = {
                "level": 2,
                "type": "policy",
                "section_name": section_name,
                "section_index": section_index + 1,
                "data": policy_data,
                "children": []
            }
            
            # Level 3: Sub-policies for this section
            section_sub_policies = [sp for sp in sub_policies if sp.get('section_name') == section_name]
            for sub_policy_index, sub_policy in enumerate(section_sub_policies):
                sub_policy_node = {
                    "level": 3,
                    "type": "sub_policy",
                    "section_name": section_name,
                    "sub_policy_index": sub_policy_index + 1,
                    "parent_policy_section": section_name,
                    "data": sub_policy,
                    "children": []
                }
                
                # Level 4: Compliance items for this sub-policy
                policy_key = f"{section_name}_{sub_policy.get('Sub_policy_id', '')}"
                compliance_items = compliance_data.get(policy_key, [])
                
                # If no compliance data provided, parse from control text
                if not compliance_items and sub_policy.get('control'):
                    compliance_items = parse_compliance_items(sub_policy.get('control'))
                
                for compliance_index, compliance in enumerate(compliance_items):
                    # Add to hierarchical structure only - no database operations here
                    compliance_node = {
                        "level": 4,
                        "type": "compliance",
                        "section_name": section_name,
                        "parent_section": sub_policy.get('Sub_policy_id', ''),
                        "sub_policy_id": sub_policy.get('Sub_policy_id', ''),
                        "compliance_index": compliance_index + 1,
                        "compliance_id": compliance.get('id', ''),
                        "data": {
                            "letter": compliance.get('letter', 'a'),
                            "name": compliance.get('name', ''),
                            "description": compliance.get('description', ''),
                            "status": compliance.get('status', 'pending'),
                            "assignee": compliance.get('assignee', ''),
                            "dueDate": compliance.get('dueDate', '')
                        }
                    }
                    sub_policy_node["children"].append(compliance_node)
                
                policy_node["children"].append(sub_policy_node)
            
            hierarchical_data["hierarchy"]["level_1_framework"]["children"].append(policy_node)
        
        # Save hierarchical JSON file
        timestamp = int(time.time())
        json_file_path = os.path.join(complete_package_dir, f"hierarchical_policy_package_{task_id}_{timestamp}.json")
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(hierarchical_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved hierarchical JSON to: {json_file_path}")
        
        # Also save flat structure for Excel compatibility
        flat_data = []
        
        # Add framework row
        framework_row = {
            "hierarchy_level": 1,
            "type": "framework",
            "section_name": "FRAMEWORK",
            "parent_section": "",
            "title": framework_details.get('title', ''),
            "description": framework_details.get('description', ''),
            "category": framework_details.get('category', ''),
            "effective_date": framework_details.get('effectiveDate', ''),
            "start_date": framework_details.get('startDate', ''),
            "end_date": framework_details.get('endDate', ''),
            "task_id": task_id,
            "creation_timestamp": int(time.time()),
            "creation_date": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        flat_data.append(framework_row)
        
        # Add policy and sub-policy rows
        for section_index, section_name in enumerate(unique_sections):
            policy_data = policy_forms.get(section_name, {})
            
            # Add policy row
            policy_row = {
                "hierarchy_level": 2,
                "type": "policy",
                "section_name": section_name,
                "parent_section": "FRAMEWORK",
                "policy_index": section_index + 1,
                "document_url": policy_data.get('documentUrl', ''),
                "identifier": policy_data.get('identifier', ''),
                "created_by": policy_data.get('createdBy', ''),
                "reviewer": policy_data.get('reviewer', ''),
                "policy_name": policy_data.get('policyName', ''),
                "department": policy_data.get('department', ''),
                "scope": policy_data.get('scope', ''),
                "applicability": policy_data.get('applicability', ''),
                "objective": policy_data.get('objective', ''),
                "coverage_rate": policy_data.get('coverageRate', ''),
                "task_id": task_id,
                "creation_timestamp": int(time.time()),
                "creation_date": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            flat_data.append(policy_row)
            
            # Add sub-policy rows
            section_sub_policies = [sp for sp in sub_policies if sp.get('section_name') == section_name]
            for sub_policy_index, sub_policy in enumerate(section_sub_policies):
                sub_policy_row = {
                    "hierarchy_level": 3,
                    "type": "sub_policy",
                    "section_name": section_name,
                    "parent_section": section_name,
                    "sub_policy_index": sub_policy_index + 1,
                    "sub_policy_id": sub_policy.get('Sub_policy_id', ''),
                    "sub_policy_name": sub_policy.get('sub_policy_name', ''),
                    "control": sub_policy.get('control', ''),
                    "scope": sub_policy.get('scope', ''),
                    "department": sub_policy.get('department', ''),
                    "objective": sub_policy.get('objective', ''),
                    "applicability": sub_policy.get('applicability', ''),
                    "coverage_rate": sub_policy.get('coverage_rate', ''),
                    "related_controls": sub_policy.get('related_controls', ''),
                    "start_date": sub_policy.get('start_date', ''),
                    "end_date": sub_policy.get('end_date', ''),
                    "task_id": task_id,
                    "creation_timestamp": int(time.time()),
                    "creation_date": time.strftime('%Y-%m-%d %H:%M:%S')
                }
                flat_data.append(sub_policy_row)
                
                # Add compliance rows
                policy_key = f"{section_name}_{sub_policy.get('Sub_policy_id', '')}"
                compliance_items = compliance_data.get(policy_key, [])
                
                # If no compliance data provided, parse from control text
                if not compliance_items and sub_policy.get('control'):
                    compliance_items = parse_compliance_items(sub_policy.get('control'))
                
                for compliance_index, compliance in enumerate(compliance_items):
                    compliance_row = {
                        "hierarchy_level": 4,
                        "type": "compliance",
                        "section_name": section_name,
                        "parent_section": sub_policy.get('Sub_policy_id', ''),
                        "sub_policy_id": sub_policy.get('Sub_policy_id', ''),
                        "compliance_index": compliance_index + 1,
                        "compliance_id": compliance.get('id', ''),
                        "compliance_letter": compliance.get('letter', ''),
                        "compliance_name": compliance.get('name', ''),
                        "compliance_description": compliance.get('description', ''),
                        "compliance_status": compliance.get('status', 'pending'),
                        "assignee": compliance.get('assignee', ''),
                        "due_date": compliance.get('dueDate', ''),
                        "evidence_file": compliance.get('evidence', {}).get('name', '') if isinstance(compliance.get('evidence'), dict) else '',
                        "task_id": task_id,
                        "creation_timestamp": int(time.time()),
                        "creation_date": time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    flat_data.append(compliance_row)
        
        # Save flat structure as Excel
        excel_file_path = os.path.join(complete_package_dir, f"flat_policy_package_{task_id}_{timestamp}.xlsx")
        df = pd.DataFrame(flat_data)
        df.to_excel(excel_file_path, index=False)
        
        print(f"Saved flat Excel to: {excel_file_path}")
        print("===== SAVE COMPLETE POLICY PACKAGE COMPLETED SUCCESSFULLY =====")
        
        return JsonResponse({
            'message': 'Policy package saved successfully',
            'hierarchical_json_file': json_file_path,
            'flat_excel_file': excel_file_path,
            'task_id': task_id
        })
    except Exception as e:
        print(f"===== ERROR IN SAVE COMPLETE POLICY PACKAGE =====")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

# Helper function to parse compliance items from control text
def parse_compliance_items(control_text):
    if not control_text:
        return []
    
    import re
    
    # Patterns to match: a), b), c) or a., b., c. or (a), (b), (c)
    patterns = [
        r'([a-z])\)\s*',  # a) b) c)
        r'([a-z])\.\s*',  # a. b. c.
        r'\(([a-z])\)\s*' # (a) (b) (c)
    ]
    
    items = []
    
    # Try each pattern
    for pattern in patterns:
        matches = list(re.finditer(pattern, control_text, re.IGNORECASE))
        if len(matches) > 1:
            # Found multiple matches, split by this pattern
            parts = re.split(pattern, control_text, flags=re.IGNORECASE)
            # Filter out empty parts and letter matches
            content_parts = [part.strip() for part in parts if part.strip() and not re.match(r'^[a-z]$', part.strip(), re.IGNORECASE)]
            
            for index, part in enumerate(content_parts):
                if part:
                    items.append({
                        'id': f'compliance_{index + 1}',
                        'letter': chr(97 + index),  # a, b, c, d, e...
                        'name': part[:100] + ('...' if len(part) > 100 else ''),
                        'description': part,
                        'status': 'pending',
                        'assignee': '',
                        'due_date': '',
                        'evidence': None
                    })
            break
    
    # If no pattern found, create single compliance item
    if not items:
        items = [{
            'id': 'compliance_1',
            'letter': 'a',
            'name': control_text[:100] + ('...' if len(control_text) > 100 else ''),
            'description': control_text,
            'status': 'pending',
            'assignee': '',
            'due_date': '',
            'evidence': None
        }]
    
    return items

@csrf_exempt
@require_http_methods(["POST"])
def save_framework_to_database(request):
    """Save the hierarchical policy package to the database in proper order"""
    print("===== STARTING SAVE TO DATABASE =====")
    print(f"Request received at: {timezone.now()}")
    
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        
        print(f"Task ID: {task_id}")
        
        if not task_id:
            return JsonResponse({'error': 'Task ID is required'}, status=400)
        
        # Find the latest JSON file in the complete_packages directory
        media_root = settings.MEDIA_ROOT
        complete_package_dir = os.path.join(media_root, 'complete_packages', task_id)
        
        if not os.path.exists(complete_package_dir):
            return JsonResponse({'error': 'Complete package directory not found'}, status=404)
        
        # Look for hierarchical JSON files
        json_files = [f for f in os.listdir(complete_package_dir) if f.startswith('hierarchical_policy_package_') and f.endswith('.json')]
        
        if not json_files:
            return JsonResponse({'error': 'No hierarchical policy package found'}, status=404)
        
        # Sort by filename which should have timestamp at the end
        json_files.sort(reverse=True)
        json_file_path = os.path.join(complete_package_dir, json_files[0])
        
        print(f"Found JSON file: {json_file_path}")
        
        # Load hierarchical JSON data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            hierarchical_data = json.load(f)
        
        print("Successfully loaded hierarchical JSON data")
        
        # Start database transaction to ensure all-or-nothing save
        with transaction.atomic():
            # STEP 1: CREATE FRAMEWORK FIRST
            framework_data = hierarchical_data.get('hierarchy', {}).get('level_1_framework', {})
            if not framework_data:
                return JsonResponse({'error': 'Framework data not found in JSON'}, status=400)
            
            framework_details = framework_data.get('data', {})
            print(f"Framework details: {framework_details.get('title', 'Untitled Framework')}")
            
            # Format dates - handle both string formats and empty values
            effective_date = framework_details.get('effectiveDate')
            start_date = framework_details.get('startDate')
            end_date = framework_details.get('endDate')
            
            # Convert string dates to datetime objects if they exist
            effective_date = datetime.strptime(effective_date, '%Y-%m-%d').date() if effective_date else timezone.now().date()
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else timezone.now().date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            
            # Create Framework record
            framework = Framework.objects.create(
                FrameworkName=framework_details.get('title', 'Untitled Framework'),
                FrameworkDescription=framework_details.get('description', ''),
                EffectiveDate=effective_date,
                CreatedByName='System Import',
                CreatedByDate=timezone.now().date(),
                Category=framework_details.get('category', ''),
                StartDate=start_date,
                EndDate=end_date,
                Status='Active',
                ActiveInactive='Active',
                Reviewer='System'
            )
            
            print(f"✅ STEP 1 COMPLETED: Created framework with ID: {framework.FrameworkId}")
            
            # STEP 2: CREATE ALL POLICIES
            policies = []
            policy_mapping = {}  # Map section_name to policy object
            
            for policy_node in framework_data.get('children', []):
                if policy_node.get('type') == 'policy':
                    policy_data = policy_node.get('data', {})
                    section_name = policy_node.get('section_name', '')
                    
                    print(f"Processing policy section: {section_name}")
                    
                    # Create Policy record
                    policy = Policy.objects.create(
                        FrameworkId=framework,
                        Status='Active',
                        PolicyDescription=policy_data.get('objective', '') or section_name,
                        PolicyName=policy_data.get('policyName', '') or section_name,
                        StartDate=start_date,
                        Department=policy_data.get('department', ''),
                        CreatedByName=policy_data.get('createdBy', 'System Import'),
                        CreatedByDate=timezone.now().date(),
                        Applicability=policy_data.get('applicability', ''),
                        DocURL=policy_data.get('documentUrl', ''),
                        Scope=policy_data.get('scope', ''),
                        Objective=policy_data.get('objective', ''),
                        Identifier=policy_data.get('identifier', ''),
                        ActiveInactive='Active',
                        Reviewer=policy_data.get('reviewer', 'System'),
                        CoverageRate=float(policy_data.get('coverageRate', 0)) if policy_data.get('coverageRate') else 0
                    )
                    
                    policies.append(policy)
                    policy_mapping[section_name] = policy
                    print(f"Created policy with ID: {policy.PolicyId} for section: {section_name}")
            
            print(f"✅ STEP 2 COMPLETED: Created {len(policies)} policies")
            
            # STEP 3: CREATE ALL SUB-POLICIES
            sub_policies = []
            sub_policy_mapping = {}  # Map for compliance linking
            
            for policy_node in framework_data.get('children', []):
                if policy_node.get('type') == 'policy':
                    section_name = policy_node.get('section_name', '')
                    policy = policy_mapping.get(section_name)
                    
                    if not policy:
                        continue
                    
                    for sub_policy_node in policy_node.get('children', []):
                        if sub_policy_node.get('type') == 'sub_policy':
                            sub_policy_data = sub_policy_node.get('data', {})
                            
                            print(f"Creating sub-policy: {sub_policy_data.get('sub_policy_name', 'Unnamed')}")
                            
                            # Create SubPolicy record
                            sub_policy = SubPolicy.objects.create(
                                PolicyId=policy,
                                SubPolicyName=sub_policy_data.get('sub_policy_name', ''),
                                CreatedByName='System Import',
                                CreatedByDate=timezone.now().date(),
                                Identifier=sub_policy_data.get('Sub_policy_id', ''),
                                Description=sub_policy_data.get('control', ''),
                                Status='Active',
                                Control=sub_policy_data.get('control', '')
                            )
                            
                            sub_policies.append(sub_policy)
                            # Create unique key for compliance mapping
                            sub_policy_key = f"{section_name}_{sub_policy_data.get('Sub_policy_id', '')}"
                            sub_policy_mapping[sub_policy_key] = {
                                'sub_policy': sub_policy,
                                'compliance_nodes': sub_policy_node.get('children', [])
                            }
                            print(f"Created sub-policy with ID: {sub_policy.SubPolicyId} - {sub_policy.SubPolicyName}")
            
            print(f"✅ STEP 3 COMPLETED: Created {len(sub_policies)} sub-policies")
            
            # STEP 4: CREATE ALL COMPLIANCE ITEMS
            compliance_items = []
            total_compliance_count = 0
            
            for sub_policy_key, sub_policy_info in sub_policy_mapping.items():
                sub_policy = sub_policy_info['sub_policy']
                compliance_nodes = sub_policy_info['compliance_nodes']
                
                compliance_count_for_subpolicy = 0
                for compliance_node in compliance_nodes:
                    if compliance_node.get('type') == 'compliance':
                        compliance_data = compliance_node.get('data', {})
                        print(f"Compliance data for {sub_policy.SubPolicyName}:", compliance_data)
                        
                        # Create Compliance record with minimal data from frontend
                        compliance_obj = Compliance.objects.create(
                            SubPolicy=sub_policy,  # Using the SubPolicy object directly
                            ComplianceItemDescription=compliance_data.get('description', '')[:500] if compliance_data.get('description') else '',
                            Status=compliance_data.get('status', 'pending')[:50] if compliance_data.get('status') else 'pending',
                            CreatedByName=compliance_data.get('assignee', 'System')[:250] if compliance_data.get('assignee') else 'System',
                            
                            # Static values for remaining fields
                            IsRisk=False,
                            PossibleDamage='',
                            mitigation={},  # Using lowercase 'mitigation' with empty JSON
                            Criticality='Medium',
                            MandatoryOptional='Optional',
                            ManualAutomatic='Manual',
                            # Impact and Probability are CharFields that can be null
                            Impact=None,
                            Probability=None,
                            ActiveInactive='Active',
                            PermanentTemporary='Permanent',
                            CreatedByDate=timezone.now().date(),
                            ComplianceVersion='1.0',
                            Identifier=compliance_data.get('letter', 'a')[:45] if compliance_data.get('letter') else 'a',
                            MaturityLevel='Initial'
                        )
                        
                        compliance_items.append(compliance_obj)
                        compliance_count_for_subpolicy += 1
                        total_compliance_count += 1
                        print(f"Created compliance item with ID: {compliance_obj.ComplianceId} for sub-policy: {sub_policy.SubPolicyName}")
                
                print(f"Created {compliance_count_for_subpolicy} compliance items for sub-policy: {sub_policy.SubPolicyName}")
            
            print(f"✅ STEP 4 COMPLETED: Created {total_compliance_count} compliance items")
            
            # Return success with all counts
            print(f"===== DATABASE SAVE COMPLETED SUCCESSFULLY =====")
            print(f"Framework ID: {framework.FrameworkId}")
            print(f"Total policies: {len(policies)}")
            print(f"Total sub-policies: {len(sub_policies)}")
            print(f"Total compliance items: {total_compliance_count}")
            
            return JsonResponse({
                'message': 'Framework, policies, sub-policies, and compliance items saved to database successfully',
                'framework_id': framework.FrameworkId,
                'framework_name': framework.FrameworkName,
                'total_policies': len(policies),
                'total_sub_policies': len(sub_policies),
                'total_compliance_items': total_compliance_count
            })
    
    except Exception as e:
        print(f"===== ERROR SAVING TO DATABASE =====")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def load_default_data(request):
    """Load default framework data from temp_media directory"""
    try:
        import uuid
        
        # Generate a unique task ID for the default data loading
        task_id = f"default_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        
        # Define the default data directory - using the correct temp_media path
        temp_media_base = os.path.join(os.path.dirname(settings.BASE_DIR), 'backend', 'temp_media')
        default_upload_dir = os.path.join(temp_media_base, 'framework_uploads', 'upload_1750339433_NIST.SP.800-53r5.pdf')
        default_extracted_dir = os.path.join(temp_media_base, 'extracted_sections', 'upload_1750339433_NIST.SP.800-53r5.pdf')
        default_complete_packages_dir = os.path.join(temp_media_base, 'complete_packages', 'upload_1750339433_NIST.SP.800-53r5.pdf')
        default_checked_sections_dir = os.path.join(temp_media_base, 'checked_sections', 'upload_1750339433_NIST.SP.800-53r5.pdf')
        default_extracted_policies_dir = os.path.join(temp_media_base, 'extracted_policies', 'upload_1750339433_NIST.SP.800-53r5.pdf')
        
        # Check if default data exists
        if not os.path.exists(default_extracted_dir):
            return JsonResponse({
                'error': f'Default data not found at: {default_extracted_dir}'
            }, status=404)
        
        # Create new directories for this task
        new_upload_dir = os.path.join(settings.MEDIA_ROOT, 'framework_uploads', task_id)
        new_extracted_dir = os.path.join(settings.MEDIA_ROOT, 'extracted_sections', task_id)
        new_complete_packages_dir = os.path.join(settings.MEDIA_ROOT, 'complete_packages', task_id)
        new_checked_sections_dir = os.path.join(settings.MEDIA_ROOT, 'checked_sections', task_id)
        new_extracted_policies_dir = os.path.join(settings.MEDIA_ROOT, 'extracted_policies', task_id)
        
        # Copy default data to new task directories
        def background_copy():
            try:
                update_progress(task_id, 5, "Loading default framework data...")
                
                # Copy framework upload if exists
                if os.path.exists(default_upload_dir):
                    shutil.copytree(default_upload_dir, new_upload_dir)
                    update_progress(task_id, 15, "Framework files copied...")
                
                # Copy extracted sections
                if os.path.exists(default_extracted_dir):
                    shutil.copytree(default_extracted_dir, new_extracted_dir)
                    update_progress(task_id, 30, "Extracted sections loaded...")
                
                # Copy checked sections (pre-selected content)
                if os.path.exists(default_checked_sections_dir):
                    shutil.copytree(default_checked_sections_dir, new_checked_sections_dir)
                    update_progress(task_id, 50, "Default content selections loaded...")
                
                # Copy extracted policies (pre-extracted policies)
                if os.path.exists(default_extracted_policies_dir):
                    shutil.copytree(default_extracted_policies_dir, new_extracted_policies_dir)
                    update_progress(task_id, 70, "Default policies loaded...")
                
                # Copy complete packages if exists
                if os.path.exists(default_complete_packages_dir):
                    shutil.copytree(default_complete_packages_dir, new_complete_packages_dir)
                    update_progress(task_id, 90, "Complete packages loaded...")
                
                # Store the output directory path for later use
                cache.set(f'output_dir_{task_id}', new_extracted_dir, timeout=3600)
                
                # Store additional info about this being default data
                cache.set(f'is_default_data_{task_id}', True, timeout=3600)
                cache.set(f'has_checked_sections_{task_id}', os.path.exists(default_checked_sections_dir), timeout=3600)
                cache.set(f'has_extracted_policies_{task_id}', os.path.exists(default_extracted_policies_dir), timeout=3600)
                
                update_progress(task_id, 100, "All default data loaded successfully!")
                
            except Exception as e:
                update_progress(task_id, 100, f"Error loading default data: {str(e)}")
        
        # Start background copying
        thread = threading.Thread(target=background_copy)
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            'message': 'Default data loading started successfully.',
            'filename': 'NIST.SP.800-53r5.pdf',
            'task_id': task_id,
            'processing': True,
            'file_type': '.pdf',
            'is_default_data': True,
            'has_pre_selected_content': os.path.exists(default_checked_sections_dir),
            'has_pre_extracted_policies': os.path.exists(default_extracted_policies_dir)
        }, status=200)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)