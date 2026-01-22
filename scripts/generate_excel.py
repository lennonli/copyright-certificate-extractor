#!/usr/bin/env python3
import sys
import json
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path

def generate_excel(output_file, data_list):
    """
    Generate Excel file from list of copyright data.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "著作权清单"
    
    # Define headers
    headers = ["序号", "著作权人", "软件名称", "首次发表日期", "权利取得方式", "权利范围", "登记号"]
    
    # Style configuration
    header_font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
    header_fill = openpyxl.styles.PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    centered_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                         top=Side(style='thin'), bottom=Side(style='thin'))
    
    # Write headers
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = centered_alignment
        cell.border = thin_border
        
    # Write data
    for row_idx, item in enumerate(data_list, 2):
        # Map JSON keys to headers order
        row_data = [
            item.get("序号", ""),
            item.get("著作权人", ""),
            item.get("软件名称", ""),
            item.get("首次发表日期", ""),
            item.get("权利取得方式", ""),
            item.get("权利范围", ""),
            item.get("登记号", "")
        ]
        
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.alignment = centered_alignment
            cell.border = thin_border
            
    # Auto-adjust column widths
    for col_idx, _ in enumerate(headers, 1):
        column_letter = get_column_letter(col_idx)
        max_length = 0
        for cell in ws[column_letter]:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[column_letter].width = min(adjusted_width, 50)  # Cap at 50

    # Save file
    try:
        wb.save(output_file)
        print(f"Excel file generated: {output_file}")
    except Exception as e:
        print(f"Error saving Excel file: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_excel.py <output_file.xlsx> <data.json>")
        sys.exit(1)
        
    output_file = sys.argv[1]
    input_data_path = sys.argv[2]
    
    try:
        with open(input_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Ensure data is a list
        if isinstance(data, dict):
            data = [data]
            
        generate_excel(output_file, data)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
