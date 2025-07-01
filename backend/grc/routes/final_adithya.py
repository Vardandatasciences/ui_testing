def extract_document_sections(pdf_path, output_dir='extracted_sections'):
    """
    Extract document sections and subheadings from a PDF document.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Output directory for extracted sections (default: 'extracted_sections')
        
    Returns:
        Path to the extracted sections folder
    """
    import sys
    sys.setrecursionlimit(3000)  # default is 1000, this raises it safely

    import os
    import re
    import pandas as pd
    import PyPDF2
    import glob
    import pdfplumber
    from pypdf import PdfReader
    import json
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create temporary files
    toc_file = os.path.join(output_dir, 'table_of_contents.txt')
    excel_file = os.path.join(output_dir, 'structured_toc.xlsx')
    
    def find_toc_page(pdf_path):
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page_num, page in enumerate(reader.pages, start=1):
                try:
                    text = page.extract_text()
                    if "Table of Contents" in text or "Contents" in text:
                        return page_num
                except Exception as e:
                    print(f"Error reading page {page_num}: {e}")
        return None

    def extract_toc_to_text(pdf_path, toc_page_num, text_file_path):
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            toc_page = reader.pages[toc_page_num - 1]
            toc_text = toc_page.extract_text()

        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(toc_text)
        print(f"Table of Contents saved to {text_file_path}")

    def process_toc_and_save_to_excel(txt_file_path, excel_file_path):
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        toc_data = []
        toc_pattern = re.compile(r"^(?P<section>[0-9]+(\.[0-9]+)*)?\s*(?P<section_name>.+?)\s+(?P<page>\d+)$")
        
        for line in lines:
            line = line.strip()
            match = toc_pattern.match(line)
            if match:
                section = match.group('section') if match.group('section') else ''
                section_name = match.group('section_name').rstrip('. ').strip()
                page = int(match.group('page'))
                toc_data.append({'Section': section, 'Section Name': section_name, 'Page Number': page})

        df = pd.DataFrame(toc_data)
        df.to_excel(excel_file_path, index=False)
        print(f"Structured TOC saved to {excel_file_path}")

    def find_offset(pdf_path):
        heading_pattern = re.compile(r'^\s*chapter one\s*$', re.IGNORECASE)
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for pdf_page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                lines = text.splitlines()
                for line in lines:
                    if heading_pattern.match(line.strip()):
                        return pdf_page_num
        return None

    def extract_text_with_styles_from_pages(pdf_path, start_page, end_page):
        """Extract text with styles from specific page range (0-indexed)"""
        with pdfplumber.open(pdf_path) as pdf:
            text_data = []
            for page_num in range(start_page, min(end_page, len(pdf.pages))):
                page = pdf.pages[page_num]
                for char in page.chars:
                    text_data.append({
                        "text": char["text"],
                        "page": page_num - start_page + 1,  # Relative page numbering within section
                        "fontname": char.get("fontname", ""),
                        "fontsize": char.get("size", 0),
                        "x": char.get("x0", 0),
                        "y": char.get("top", 0),
                    })
            return text_data

    def group_text_by_position(text_data, line_tolerance=2):
        grouped_lines = []
        current_line = []

        for char_data in sorted(text_data, key=lambda x: (x["page"], x["y"], x["x"])):
            if not current_line:
                current_line.append(char_data)
            else:
                last_char = current_line[-1]
                same_line = (
                    abs(char_data["y"] - last_char["y"]) <= line_tolerance and
                    char_data["page"] == last_char["page"]
                )
                if same_line:
                    current_line.append(char_data)
                else:
                    grouped_lines.append(current_line)
                    current_line = [char_data]

        if current_line:
            grouped_lines.append(current_line)

        return grouped_lines

    def is_all_caps(text):
        filtered = ''.join(c for c in text if c.isalpha())
        return filtered.isupper() if filtered else False

    def is_bold(fontname):
        return "Bold" in fontname or "bold" in fontname

    def extract_all_subheadings_with_style(lines, fontname, fontsize, all_caps, bold):
        matched_subheadings = []
        for line in lines:
            text = "".join(char["text"] for char in line).strip()
            if not text:
                continue
            total_chars = len(line)
            if total_chars == 0:
                continue
            total_bold_chars = sum(1 for char in line if is_bold(char.get("fontname", "")))
            overall_line_bold = total_bold_chars / total_chars >= 0.7
            font_counts = {}
            for char in line:
                fnt = char.get("fontname", "")
                font_counts[fnt] = font_counts.get(fnt, 0) + 1
            majority_fontname = max(font_counts, key=font_counts.get) if font_counts else ""

            char_style_matches = []
            for char in line:
                c_fontname = char.get("fontname", "")
                c_fontsize = char.get("fontsize", char.get("size", 0))
                c_text = char["text"]
                c_all_caps = c_text.isalpha() and c_text.isupper()
                c_bold = is_bold(c_fontname)
                fontname_match = (c_fontname == fontname)
                fontsize_match = abs(c_fontsize - fontsize) < 1
                all_caps_match = (c_all_caps == all_caps)
                bold_match = (overall_line_bold == bold)
                is_char_matching = fontname_match and fontsize_match and all_caps_match and bold_match
                char_style_matches.append(is_char_matching)

            start_noise = 0
            for match in char_style_matches:
                if not match:
                    start_noise += 1
                else:
                    break

            end_noise = 0
            for match in reversed(char_style_matches):
                if not match:
                    end_noise += 1
                else:
                    break

            if (start_noise + end_noise) / total_chars > 0.3:
                continue

            start_idx = start_noise
            end_idx = total_chars - 1 - end_noise

            while start_idx <= end_idx and line[start_idx]["text"].isspace():
                start_idx += 1
            while end_idx >= start_idx and line[end_idx]["text"].isspace():
                end_idx -= 1

            if start_idx > end_idx:
                continue

            cleaned_text = "".join(char["text"] for char in line[start_idx:end_idx+1]).strip()

            if all_caps and not is_all_caps(cleaned_text):
                continue

            matched_subheadings.append({
                "text": cleaned_text,
                "page": line[0]["page"],
                "fontname": majority_fontname,
                "fontsize": fontsize,
                "all_caps": all_caps,
                "bold": bold,
                "y": line[0]["y"],
            })
        return matched_subheadings

    def merge_successive_subheadings(subheadings, y_tolerance=25):
        if not subheadings:
            return []
        merged = []
        prev = subheadings[0]
        for curr in subheadings[1:]:
            same_page = (curr["page"] == prev["page"])
            y_close = abs(curr["y"] - prev["y"]) < y_tolerance
            if same_page and y_close:
                prev["text"] += " " + curr["text"]
                prev["y"] = min(prev["y"], curr["y"])
            else:
                merged.append(prev)
                prev = curr
        merged.append(prev)
        return merged

    def detect_first_subheading(lines):
        main_heading = None
        found_main_heading = False
        main_heading_page = None
        main_heading_y = None
        candidates = []
        for line in lines:
            text = "".join(char["text"] for char in line).strip()
            if not text:
                continue
            font_counts = {}
            for char in line:
                fnt = char.get("fontname", "")
                font_counts[fnt] = font_counts.get(fnt, 0) + 1
            majority_fontname = max(font_counts, key=font_counts.get) if font_counts else ""
            fontname = majority_fontname
            fontsize = line[0].get("fontsize", line[0].get("size", 0))
            page = line[0]["page"]
            y = line[0]["y"]

            if not found_main_heading:
                if len(text.split()) <= 10 and fontsize > 10:
                    main_heading = {
                        "text": text,
                        "page": page,
                        "fontname": fontname,
                        "fontsize": fontsize,
                        "y": y,
                    }
                    main_heading_page = page
                    main_heading_y = y
                    found_main_heading = True
            else:
                if page == main_heading_page and y > main_heading_y + 0.5:
                    total_chars = len(line)
                    if total_chars == 0:
                        continue
                    total_bold_chars = sum(1 for char in line if is_bold(char.get("fontname", "")))
                    line_bold = (total_bold_chars / total_chars) >= 0.7
                    candidates.append({
                        "text": text,
                        "page": page,
                        "fontname": fontname,
                        "fontsize": fontsize,
                        "y": y,
                        "all_caps": is_all_caps(text),
                        "bold": line_bold,
                    })

        if not candidates:
            return []

        filtered_candidates = [c for c in candidates if main_heading and c["y"] > main_heading["y"] + 0.5]
        if not filtered_candidates:
            return []

        filtered_candidates.sort(key=lambda x: (
            -x["fontsize"],
            -int(x["all_caps"]),
            -int(x["bold"]),
        ))

        first_subheading = filtered_candidates[0]

        matched_subheadings = extract_all_subheadings_with_style(
            lines,
            first_subheading["fontname"],
            first_subheading["fontsize"],
            first_subheading["all_caps"],
            first_subheading["bold"],
        )

        return merge_successive_subheadings(matched_subheadings)

    def extract_policy_id_from_text(text):
        """Extract policy ID from subheading text (e.g., 'MP-1 POLICY AND PROCEDURES' -> 'MP-1')"""
        import re
        # Pattern to match policy IDs like AC-1, AT-1, MP-1, etc.
        pattern = r'^([A-Z]{2,3}-\d+(?:\(\d+\))?)'
        match = re.match(pattern, text.strip())
        if match:
            return match.group(1)
        return None

    def extract_last_subheading_to_section_end(last_subheading, line_number_map, output_path, json_dir):
        start_regex = re.escape(last_subheading['text'][:10].strip().lower())
        start_found = False
        extracted_lines = []
        for entry in line_number_map:
            line_text = "".join(char["text"] for char in entry["line"]).strip()
            line_text_lower = line_text.lower()
            if len(line_text) < 4:
                continue
            if not start_found:
                if re.search(start_regex, line_text_lower):
                    start_found = True
                    extracted_lines.append(line_text)
                continue
            else:
                extracted_lines.append(line_text)
        if extracted_lines:
            full_text = "\n".join(extracted_lines)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_text)
            
            # Extract policy ID for JSON filename
            policy_id = extract_policy_id_from_text(last_subheading['text'])
            if policy_id:
                json_filename = f"{policy_id}.json"
            else:
                json_filename = os.path.basename(output_path).replace(".txt", ".json")
            
            json_path = os.path.join(json_dir, json_filename)
            json_data = {
                "subheading": last_subheading['text'],
                "start_text": full_text[:50],
                "content": full_text
            }
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(json_data, jf, indent=2)
            print(f"✅ Saved last subheading extract to {output_path} and JSON")

    # Main execution flow
    toc_page = find_toc_page(pdf_path)
    if toc_page:
        extract_toc_to_text(pdf_path, toc_page, toc_file)
        process_toc_and_save_to_excel(toc_file, excel_file)
    else:
        print("TOC not found.")
        return None

    offset = find_offset(pdf_path)
    if offset:
        offset -= 1
    else:
        print("Offset not found.")
        return None

    # Prepare section metadata
    reader = PyPDF2.PdfReader(pdf_path)
    total_pages = len(reader.pages)
    df = pd.read_excel(excel_file, dtype={'Section': str})
    df = df.sort_values('Page Number').reset_index(drop=True)

    # Create section metadata with page ranges
    section_metadata = []
    for i in range(len(df)):
        start_section = df.iloc[i]
        end_page_number = df.iloc[i + 1]['Page Number'] if i < len(df) - 1 else total_pages

        start_page = int(start_section['Page Number']) + offset - 1
        end_page = int(end_page_number) + offset - 1

        section_id = str(start_section['Section']).strip()
        section_name = str(start_section['Section Name']).strip().replace('/', '-')
        section_folder = os.path.join(output_dir, f"{section_id} {section_name}")
        os.makedirs(section_folder, exist_ok=True)

        section_metadata.append({
            'section_id': section_id,
            'section_name': section_name,
            'folder_path': section_folder,
            'start_page': start_page,
            'end_page': end_page,
            'folder_name': f"{section_id} {section_name}"
        })
        print(f"[+] Prepared section: {section_id} {section_name} (pages {start_page+1}-{end_page})")

    # Process each section
    for section_meta in section_metadata:
        section_id = section_meta['section_id']
        section_name = section_meta['section_name']
        folder_path = section_meta['folder_path']
        start_page = section_meta['start_page']
        end_page = section_meta['end_page']
        folder_name = section_meta['folder_name']

        txt_dir = os.path.join(folder_path, "txt_chunks")
        json_dir = os.path.join(folder_path, "json_chunks")
        os.makedirs(txt_dir, exist_ok=True)
        os.makedirs(json_dir, exist_ok=True)

        print(f"\n[🔍] Subheading extraction for: {folder_name} (pages {start_page+1}-{end_page})")

        try:
            text_data = extract_text_with_styles_from_pages(pdf_path, start_page, end_page)
            if not text_data:
                print(f"[⚠️] No text data extracted from {folder_name}")
                continue

            grouped_lines = group_text_by_position(text_data)
            if not grouped_lines:
                print(f"[⚠️] No grouped lines found in {folder_name}")
                continue

            page_line_counter = {}
            line_number_map = []
            for line in grouped_lines:
                if not line:
                    continue
                page = line[0]["page"]
                page_line_counter[page] = page_line_counter.get(page, 0) + 1
                line_number_map.append({
                    "line": line,
                    "page": page,
                    "line_on_page": page_line_counter[page]
                })

            subheadings = detect_first_subheading(grouped_lines)
            if not subheadings:
                print(f"[⚠️] No subheadings found in {folder_name}")
                continue

            print(f"[✅] Found {len(subheadings)} subheadings in {folder_name}")

            # Create Excel file for subheadings
            excel_path = os.path.join(folder_path, f"{section_id}_subheadings.xlsx")
            df_sub = pd.DataFrame([{"Subheading": s["text"], "Page No": s["page"]} for s in subheadings])
            df_sub.to_excel(excel_path, index=False)

            # Extract text between subheadings
            for i in range(len(subheadings) - 1):
                start_regex = re.escape(subheadings[i]['text'][:10].strip().lower())
                end_regex = re.escape(subheadings[i+1]['text'][:10].strip().lower())
                extracted_lines = []
                start_found = False
                for entry in line_number_map:
                    line_text = "".join(char["text"] for char in entry["line"]).strip()
                    line_text_lower = line_text.lower()
                    if len(line_text) < 4:
                        continue
                    if not start_found:
                        if re.search(start_regex, line_text_lower):
                            start_found = True
                            extracted_lines.append(line_text)
                        continue
                    else:
                        if re.search(end_regex, line_text_lower):
                            break
                        extracted_lines.append(line_text)
                if extracted_lines:
                    # Extract policy ID from current subheading
                    policy_id = extract_policy_id_from_text(subheadings[i]['text'])
                    
                    if policy_id:
                        filename_base = policy_id
                    else:
                        # Fallback to original naming if no policy ID found
                        filename_base = f"extracted_{i+1}_{subheadings[i]['text'][:10].replace(' ','_')}"
                    
                    txt_path = os.path.join(txt_dir, f"{filename_base}.txt")
                    json_path = os.path.join(json_dir, f"{filename_base}.json")
                    full_text = "\n".join(extracted_lines)

                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(full_text)

                    json_data = {
                        "subheading": subheadings[i]['text'],
                        "start_text": full_text[:50],
                        "content": full_text
                    }
                    with open(json_path, "w", encoding="utf-8") as jf:
                        json.dump(json_data, jf, indent=2)

                    print(f"[✅] Saved chunk {i+1}: {filename_base}")

            # Handle last subheading to section end
            if subheadings:
                last_sh = subheadings[-1]
                last_policy_id = extract_policy_id_from_text(last_sh['text'])
                
                if last_policy_id:
                    last_filename = last_policy_id
                else:
                    last_filename = f"extracted_last_{last_sh['text'][:10].replace(' ','_')}_to_end"
                
                last_out_txt = os.path.join(txt_dir, f"{last_filename}.txt")
                extract_last_subheading_to_section_end(last_sh, line_number_map, last_out_txt, json_dir)

            # Clean up Excel file
            try:
                os.remove(excel_path)
            except Exception as e:
                print(f"[❌] Failed to delete Excel {excel_path}: {e}")

        except Exception as e:
            print(f"[❌] Error processing section {folder_name}: {e}")
            continue

    # Clean up temporary files
    try:
        os.remove(toc_file)
        os.remove(excel_file)
    except Exception as e:
        print(f"[❌] Failed to delete temporary files: {e}")

    print("\n[🎉] Processing completed! All text chunks saved to respective folders.")
    return os.path.abspath(output_dir)

# Example usage:
# extracted_path = extract_document_sections("NIST.SP.800-53r5.pdf")    