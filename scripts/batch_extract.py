#!/usr/bin/env python3
"""
Batch processing script for copyright certificates

Extracts OCR text and parses information from multiple copyright certificate files.
"""

import sys
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Import the main extraction functions
sys.path.insert(0, str(Path(__file__).parent))
from extract_ocr import extract_text
from parse_copyright import parse_copyright_text
from generate_excel import generate_excel

def batch_extract(folder_path: Path, output_excel: Path, lang: str = 'chi_sim'):
    """
    Extract and parse all certificate files in a folder and generate Excel
    """
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Folder not found: {folder_path}", file=sys.stderr)
        return []

    # Supported file extensions
    supported_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}

    results = []
    processed_count = 0

    print(f"Scanning folder: {folder_path}")

    # Iterate through all files in the folder
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            print(f"\nProcessing: {file_path.name}")

            # Extract text
            print(f"  Extracting text...")
            text = extract_text(file_path, lang)

            if not text:
                print(f"  Warning: No text extracted from {file_path.name}", file=sys.stderr)
                continue
                
            # Parse text
            print(f"  Parsing information...")
            data_list = parse_copyright_text(text)
            
            # Handle both list (new format) and dict (legacy/fallback)
            if isinstance(data_list, dict):
                data_list = [data_list]
            
            if not data_list:
                print(f"  Warning: No copyright info found in {file_path.name}")
                continue

            is_image_file = file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']

            for data in data_list:
                # Add file info
                data['file_name'] = file_path.name
                data['file_path'] = str(file_path)
                
                # Filename Fallback for Images
                # If it's an image file and software name is missing, looks like garbage (short),
                # or contains labels/keywords indicating extraction failure.
                current_name = data.get('软件名称', '').strip()
                # Remove all whitespace for keyword checking
                clean_name = current_name.replace(' ', '').replace('\t', '').replace('\n', '')
                is_bad_name = (not current_name) or (len(current_name) < 4) or \
                              any(kw in clean_name for kw in ['著作权人', '软件名称', '登记号'])
                
                if is_image_file and is_bad_name:
                    print(f"  ! Using filename fallback for software name: {file_path.stem}")
                    data['软件名称'] = file_path.stem
                
                results.append(data)
                print(f"  ✓ Found: {data.get('软件名称', 'Unknown')}")
            
            processed_count += 1

    if results:
        # Sort results (optional)
        # results.sort(key=lambda x: x.get('序号', ''))
        
        # Generate Excel
        print(f"\nGenerating Excel file...")
        generate_excel(output_excel, results)
        print(f"Batch processing completed. Total files: {processed_count}")
        print(f"Output saved to: {output_excel}")
    else:
        print("No files processed or no valid data extracted.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python batch_extract.py <folder_path> <output_excel_path> [language_code]")
        sys.exit(1)

    folder_path = Path(sys.argv[1])
    output_excel = Path(sys.argv[2])
    lang = sys.argv[3] if len(sys.argv) > 3 else 'chi_sim'

    batch_extract(folder_path, output_excel, lang)
