import re
import json
import os
import pandas as pd
import shutil
import time
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from django.conf import settings

# Global progress tracking
progress_tracker = {}

def update_progress(task_id, progress, message):
    """Update progress for a specific task"""
    progress_tracker[task_id] = {
        'progress': progress,
        'message': message,
        'timestamp': time.time()
    }

def get_progress(task_id):
    """Get progress for a specific task"""
    return progress_tracker.get(task_id, {'progress': 0, 'message': 'Starting...'})

def extract_policy_sections(input_text, task_id=None):
    if task_id:
        update_progress(task_id, 10, "Initializing AI model...")
    
    llm = OllamaLLM(model="llama3.2:3b", temperature=0)

    if task_id:
        update_progress(task_id, 20, "Preparing extraction template...")

    # Enhanced prompt template with specific focus on control requirements
    prompt_template = PromptTemplate(
        input_variables=["text"],
        template="""
You are an AI assistant trained to extract specific sections from policy documents.

From the following policy text, extract these exact fields:
- Sub_policy_id: The unique ID or code of the policy or control
- sub_policy_name: The full official name or title of the policy or control
- control: The main control requirement or directive. Format it with proper structure:
  * Use a letter followed by period (e.g., "a.") to start main points
  * Use numbers (e.g., "1.") for sub-points under a main point
  * Each main point should start on a new line
  * Present imperatives and requirements clearly
  * Focus on capturing requirements with terms like MUST, SHALL, SHOULD, MAY
  * Retain the exact original wording of requirements
- related_controls: A list of all other referenced or linked controls
- control_enhancements: Any numbered or named enhancements to the main control
- references: Citations, external documents, standards, or publications referenced

IMPORTANT: For the control section, ensure you format it professionally:
1. Each distinct requirement should be on its own line or bullet point
2. Use appropriate letter/number formatting (a., b., c. or 1., 2., 3.)
3. Use newline characters \\n to separate points
4. Maintain the original hierarchy of the requirements
5. Do not add extra explanations or interpretations

Return the output as plain text, structured like:

Sub_policy_id:
Content

sub_policy_name:
Content

control:
Content

... and so on.

If a field is not present in the document, include the heading but leave the content blank.
DO NOT provide any explanations, markdown, or JSON — only the headings and their content.

Policy text:

{text}
"""
    )

    if task_id:
        update_progress(task_id, 30, "Creating processing chain...")

    chain = LLMChain(llm=llm, prompt=prompt_template)

    if task_id:
        update_progress(task_id, 50, "Processing document with AI...")

    print("Processing document...")
    response = chain.invoke({"text": input_text})["text"]

    if task_id:
        update_progress(task_id, 70, "Parsing extracted content...")

    # Parse response by dynamically detecting headings (lines that end with colon)
    def parse_dynamic_headings(text):
        # Split text by lines that look like headings (any line ending with colon)
        pattern = re.compile(r'^(.*?):\s*$', re.MULTILINE)
        splits = pattern.split(text)

        parsed = []
        for i in range(1, len(splits), 2):
            heading = splits[i].strip()
            content = splits[i + 1].strip() if (i + 1) < len(splits) else ""
            parsed.append((heading, content))
        return parsed

    parsed_data = parse_dynamic_headings(response)
    
    if task_id:
        update_progress(task_id, 85, "Structuring extracted data...")
    
    # Convert to JSON
    result = {}
    for heading, content in parsed_data:
        result[heading] = content
    
    if task_id:
        update_progress(task_id, 95, "Finalizing extraction...")
    
    return result

def process_checked_sections(task_id):
    """
    Process all text files in the checked_sections folder, extract policy sections,
    and save the results to an Excel file.
    
    Args:
        task_id: The task ID used to identify the checked_sections folder
        
    Returns:
        Path to the generated Excel file
    """
    update_progress(task_id, 5, "Initializing policy extraction...")
    
    # Get the path to the task-specific checked_sections folder
    media_root = settings.MEDIA_ROOT
    checked_sections_dir = os.path.join(media_root, 'checked_sections', task_id)
    
    if not os.path.exists(checked_sections_dir):
        print(f"Directory not found: {checked_sections_dir}")
        return None
    
    update_progress(task_id, 10, "Setting up output directory...")
    
    # Create task-specific output directory for extracted policies
    extracted_policies_dir = os.path.join(media_root, 'extracted_policies', task_id)
    if os.path.exists(extracted_policies_dir):
        print(f"Removing existing directory: {extracted_policies_dir}")
        shutil.rmtree(extracted_policies_dir)
    
    os.makedirs(extracted_policies_dir, exist_ok=True)
    print(f"Created directory: {extracted_policies_dir}")
    
    update_progress(task_id, 15, "Scanning text files...")
    
    # Create a list to store all extracted data
    all_extracted_data = []
    
    # Count total files for progress tracking
    total_files = 0
    for root, dirs, files in os.walk(checked_sections_dir):
        for file in files:
            if file.endswith('.txt'):
                total_files += 1
    
    if total_files == 0:
        update_progress(task_id, 100, "No text files found to process.")
        return None
    
    processed_files = 0
    
    # Walk through all subdirectories in the checked_sections folder
    for root, dirs, files in os.walk(checked_sections_dir):
        for file in files:
            if file.endswith('.txt'):
                processed_files += 1
                progress_percent = 15 + (processed_files / total_files) * 70  # 15% to 85%
                
                # Get the section name from the directory structure
                section_name = os.path.basename(root)
                if section_name == 'txt_chunks':
                    section_name = os.path.basename(os.path.dirname(root))
                
                file_path = os.path.join(root, file)
                update_progress(task_id, int(progress_percent), f"Processing file {processed_files}/{total_files}: {file}")
                print(f"Processing file: {file_path}")
                
                try:
                    # Read the text file
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                    
                    # Skip empty files
                    if not file_content.strip():
                        print(f"Skipping empty file: {file_path}")
                        continue
                    
                    # Extract policy sections with progress tracking
                    extracted_data = extract_policy_sections(file_content, f"{task_id}_file_{processed_files}")
                    
                    # Add section name and file name to the extracted data
                    extracted_data['section_name'] = section_name
                    extracted_data['file_name'] = file
                    
                    # Add to the list of all extracted data
                    all_extracted_data.append(extracted_data)
                    
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    # Add error entry to maintain record
                    all_extracted_data.append({
                        'section_name': section_name,
                        'file_name': file,
                        'Sub_policy_id': f'ERROR: {str(e)}',
                        'sub_policy_name': '',
                        'control': '',
                        'discussion': '',
                        'related_controls': '',
                        'control_enhancements': '',
                        'references': ''
                    })
    
    update_progress(task_id, 90, "Compiling extracted policies...")
    
    if not all_extracted_data:
        update_progress(task_id, 100, "No data extracted from text files.")
        print("No data extracted from text files.")
        return None
    
    # Create a DataFrame from the extracted data
    df = pd.DataFrame(all_extracted_data)
    
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
    
    update_progress(task_id, 95, "Saving to Excel file...")
    
    # Save to Excel in the extracted_policies directory
    output_file = os.path.join(extracted_policies_dir, f"extracted_policies_{task_id}.xlsx")
    df.to_excel(output_file, index=False)
    
    update_progress(task_id, 100, f"Policy extraction complete! {len(all_extracted_data)} policies extracted.")
    
    print(f"Saved extracted data to {output_file}")
    print(f"Total policies extracted: {len(all_extracted_data)}")
    return output_file

# # Example usage
# if __name__ == "__main__":
#     input_file_path = "ac1.txt"
#     
#     with open(input_file_path, "r", encoding="utf-8") as file:
#         document_text = file.read()
#     
#     result_json = extract_policy_sections(document_text)
#     print(json.dumps(result_json, indent=2))