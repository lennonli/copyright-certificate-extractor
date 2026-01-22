#!/usr/bin/env python3
import sys
import re
import json
from pathlib import Path

def _parse_single_block(text):
    """
    Parse structured information from a single certificate text block.
    """
    data = {
        "序号": "",
        "著作权人": "",
        "软件名称": "",
        "首次发表日期": "",
        "权利取得方式": "",
        "权利范围": "",
        "登记号": ""
    }
    
    # Clean text: remove extra whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    cleaned_text = '\n'.join(lines)
    
    # Registration Number (e.g., 2021SR0123456)
    # Allow spaces in keyword: 登 记 号
    reg_match = re.search(r'登\s*记\s*号\s*[:：;]?\s*([0-9]{4}SR[0-9]+)', cleaned_text)
    if reg_match:
        data["登记号"] = reg_match.group(1)
        
    # Serial Number (No. 0000000)
    serial_match = re.search(r'No\.\s*(\d{6,})', cleaned_text)
    if serial_match:
        data["序号"] = serial_match.group(1)
        
    # Copyright Owner
    # Allow spaces in keyword: 著 作 权 人
    # Handle optional leading chars like -, .
    owner_match = re.search(r'著\s*作\s*权\s*人\s*[:：;,]?\s*([^\n]+)', cleaned_text)
    if owner_match:
        # Clean up leading punctuation from the value if present (OCR noise)
        raw_owner = owner_match.group(1).strip()
        data["著作权人"] = re.sub(r'^[:：,，.\-]\s*', '', raw_owner)
        
    # Software Name
    # Allow spaces in keyword: 软 件 名 称
    # Capture until next keyword or end of block. This is tricky with simple regex.
    # We'll try to capture the line and potentially the next line if it doesn't look like a keyword.
    name_match = re.search(r'软\s*件\s*名\s*称\s*[:：;,]?\s*([^\n]+)(?:\n\s*[:：]?\s*([^\n]+))?', cleaned_text)
    if name_match:
        part1 = name_match.group(1).strip()
        part2 = name_match.group(2)
        
        full_name = part1
        # If part2 exists and doesn't look like a keyword (e.g. doesn't start with "著作权人")
        if part2:
            part2 = part2.strip()
            # Check if part2 is likely a continuation (not a new field)
            if not re.match(r'(著作权人|版本号|V\d|首次发表|权利|开发完成)', part2):
                # Check if part1 ends with incomplete sentence or part2 starts with continuation
                # For this specific case: part2 might just be the second line.
                # Remove leading colon/spaces from part2 if OCR added them as noise
                part2 = re.sub(r'^[:：]\s*', '', part2)
                full_name += " " + part2
        
        data["软件名称"] = full_name
        
    # First Publication Date
    date_match = re.search(r'首次发表日期\s*[:：;,]?\s*(\d{4}年\d{1,2}月\d{1,2}日|未发表)', cleaned_text)
    if date_match:
        data["首次发表日期"] = date_match.group(1)
        
    # Acquisition Method
    method_match = re.search(r'权利取得方式\s*[:：;,]?\s*([^\n]+)', cleaned_text)
    if method_match:
        data["权利取得方式"] = method_match.group(1).strip()
        
    # Rights Scope
    scope_match = re.search(r'权\s*利\s*范\s*围\s*[:：;,]?\s*([^\n]+)', cleaned_text)
    if scope_match:
        data["权利范围"] = scope_match.group(1).strip()

    return data

def parse_copyright_text(text):
    """
    Parse structured information from copyright certificate text.
    Handles multiple pages separated by '--- Page X ---'.
    Returns a LIST of dictionaries.
    """
    # Split by page delimiter
    pages = re.split(r'--- Page \d+ ---', text)
    
    results = []
    for page in pages:
        if not page.strip():
            continue
        
        # Parse each page block
        data = _parse_single_block(page)
        
        # Only add if we found at least one key field
        if any([data["序号"], data["登记号"], data["软件名称"], data["著作权人"]]):
            results.append(data)
            
    # Fallback: if no pages found (e.g. text didn't have separators), parse as one block
    if not results and text.strip():
         data = _parse_single_block(text)
         if any([data["序号"], data["登记号"], data["软件名称"], data["著作权人"]]):
             results.append(data)
             
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_copyright.py <text_file_path>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        data_list = parse_copyright_text(text)
        print(json.dumps(data_list, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"Error parsing file: {e}", file=sys.stderr)
        sys.exit(1)
