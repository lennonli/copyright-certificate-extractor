---
skill_name: copyright-certificate-extractor
description: Extract structured information from Chinese software copyright certificates (PDF/images) using OCR and intelligent parsing
version: 1.0.0
author: lennonli
---

# Copyright Certificate Extractor Skill

Extract structured information from Chinese Software Copyright Registration Certificates (软件著作权登记证书) in PDF or image formats.

## When to Use This Skill

Claude should automatically invoke this skill when the user:
- Mentions "软件著作权证书", "copyright certificate", or "著作权登记"
- Asks to extract information from certificate files
- Needs to process multiple certificates in batch
- Wants to generate Excel reports from certificate data
- Says "extract copyright info", "parse certificate", or "批量处理证书"

## Core Capabilities

### 1. Multi-Format Support
- **PDF files**: Supports multi-page PDFs with multiple certificates
- **Image formats**: JPG, PNG, BMP, TIFF
- **Automatic format detection**: Handles both scanned and digital files

### 2. High-Precision OCR
- **Image preprocessing**: Automatic contrast enhancement and grayscale conversion
- **Chinese text recognition**: Optimized for Chinese characters using Tesseract
- **Multi-page handling**: Processes all pages in PDF files separately

### 3. Intelligent Field Extraction
Automatically extracts these key fields:
- **序号** (Serial Number): e.g., "No. 0123456"
- **著作权人** (Copyright Owner): Company or individual name
- **软件名称** (Software Name): Full software name including version
- **首次发表日期** (First Publication Date): Format: YYYY年MM月DD日
- **权利取得方式** (Acquisition Method): e.g., "原始取得"
- **权利范围** (Rights Scope): e.g., "全部权利"
- **登记号** (Registration Number): Format: YYYYSRxxxxxx

### 4. Automatic Error Correction
- **Filename fallback**: When OCR quality is poor, uses filename as software name
- **Regex enhancement**: Handles OCR noise and formatting variations
- **Smart validation**: Detects and filters invalid extractions

### 5. Batch Processing
- **Directory scanning**: Process entire folders of certificates
- **Excel report generation**: Consolidated output with all extracted data
- **Progress tracking**: Real-time feedback during batch operations

## System Requirements

### Dependencies
The skill will automatically check for and guide installation of:

**System packages** (macOS):
```bash
brew install tesseract tesseract-lang poppler
```

**System packages** (Ubuntu/Debian):
```bash
apt-get install tesseract-ocr tesseract-ocr-chi-sim poppler-utils
```

**Python packages**:
```bash
pip install pytesseract pdf2image Pillow openpyxl
```

## Usage Examples

### Example 1: Single File Extraction
**User**: "Please extract information from this copyright certificate"
**Claude**:
1. Checks if file is provided
2. Runs OCR extraction
3. Parses structured fields
4. Displays extracted data in formatted output

### Example 2: Batch Processing
**User**: "I have a folder with 50 copyright certificates, please extract all data to Excel"
**Claude**:
1. Scans the directory for certificate files
2. Processes each file (OCR + parsing)
3. Generates consolidated Excel report
4. Shows summary and file location

### Example 3: Quality Issues
**User**: "The OCR result looks wrong, the software name is missing"
**Claude**:
1. Applies filename fallback mechanism
2. Re-parses with enhanced regex
3. If still problematic, suggests using LLM-assisted extraction
4. Provides manual verification tips

## Workflow

```
┌─────────────────────┐
│   Input Files       │
│ (PDF/Images)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Image Preprocessing│
│  - Grayscale        │
│  - Contrast Enhance │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Tesseract OCR     │
│   (chi_sim)         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Regex Parsing      │
│  - Extract fields   │
│  - Validate data    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Fallback Logic     │
│  (if needed)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Output Generation  │
│  - JSON/Excel       │
└─────────────────────┘
```

## Implementation Guidelines

### When User Provides Certificate Files

1. **Check dependencies first**:
   ```bash
   # Verify Tesseract is installed
   which tesseract || echo "Please install: brew install tesseract tesseract-lang"

   # Check for Chinese language pack
   tesseract --list-langs | grep chi_sim || echo "Install Chinese pack: brew install tesseract-lang"
   ```

2. **For single files**:
   ```bash
   cd /tmp/copyright-certificate-extractor
   python scripts/extract_ocr.py "<file_path>" > extracted_text.txt
   python scripts/parse_copyright.py extracted_text.txt > data.json
   ```

3. **For batch processing**:
   ```bash
   cd /tmp/copyright-certificate-extractor
   python scripts/batch_extract.py "<certificate_directory>" "<output.xlsx>"
   ```

4. **Display results**:
   - Show extracted fields in a formatted table
   - Highlight any fields that failed to extract
   - Provide the Excel file path for batch operations

### Quality Recommendations

- **Optimal scan resolution**: ≥300 DPI
- **File format preference**: High-quality PDF > PNG > JPG
- **Clear text**: Avoid blurry or low-contrast scans
- **Manual verification**: Always recommend user to verify critical fields

### Error Handling

Common issues and solutions:

| Issue | Detection | Solution |
|-------|-----------|----------|
| No text extracted | Empty OCR output | Check file format, suggest re-scan |
| Missing software name | Field is empty/short | Apply filename fallback |
| Garbled text | Contains label keywords | Increase contrast, try LLM parsing |
| Multiple certificates | Multi-page PDF | Process each page separately |

## Advanced: LLM-Assisted Extraction

For extremely difficult cases, use the LLM prompt template in `references/llm_prompt.md`:

1. Extract raw OCR text
2. Send to Claude with the structured prompt
3. Get JSON output with extracted fields
4. Validate and merge with batch results

## File Structure

```
copyright-certificate-extractor/
├── skill.md                    # This file
├── marketplace.json            # Skill metadata
├── README.md                   # User documentation
├── requirements.txt            # Python dependencies
├── .claudeignore              # Files to ignore
├── scripts/
│   ├── extract_ocr.py         # OCR extraction logic
│   ├── parse_copyright.py     # Regex parsing engine
│   ├── batch_extract.py       # Batch processing workflow
│   └── generate_excel.py      # Excel report generator
└── references/
    └── llm_prompt.md          # LLM fallback prompt template
```

## Best Practices

1. **Always verify system dependencies** before processing
2. **Show progress feedback** during batch operations
3. **Validate extracted data** and flag suspicious results
4. **Suggest manual review** for critical fields
5. **Provide clear error messages** with actionable solutions
6. **Save intermediate results** (OCR text) for debugging

## Limitations

- Requires Tesseract OCR installation (not portable)
- Best results need good scan quality (≥300 DPI)
- May struggle with severely degraded or handwritten text
- Regex patterns specific to Chinese copyright certificate format
- No built-in validation against copyright office database

## Future Enhancements

- PaddleOCR integration for better Chinese recognition
- Machine learning-based field detection
- Web interface for drag-and-drop upload
- Real-time confidence scoring
- Support for other certificate types (trademark, patent)
