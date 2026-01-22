# Changelog

All notable changes to the Copyright Certificate Extractor skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-01-22

### Added - Excel Quality Improvements
- **Smart data cleaning**: Automatic removal of OCR noise (|, ||, ，, 。, extra spaces)
- **Auto-numbering**: Sequential numbering (1, 2, 3...) instead of inconsistent OCR numbers
- **OCR error correction**: Common Chinese OCR mistakes (基浮→悬浮, 折又→折叠, 钦件→软件)
- **Data validation**: Automatic filtering of invalid/garbage OCR results
- **Notes column**: Preserves original OCR serial numbers for reference

### Improved - Excel Formatting
- **Professional styling**: Blue header with white data area
- **Frozen header row**: Title row stays visible when scrolling
- **Smart alignment**: Numbers centered, text left-aligned
- **Optimized column widths**:
  - Serial: 8 chars
  - Owner: 30 chars
  - Software name: 50 chars (widest for long names)
  - Registration: 20 chars
- **Microsoft YaHei font**: Cleaner, more professional appearance

### Fixed
- Fixed inconsistent serial numbers (None, gaps, non-sequential)
- Fixed OCR noise pollution in all text fields
- Fixed excessive punctuation and symbols
- Fixed data quality issues from poor OCR

### Technical
- Added `clean_text()` function for intelligent text cleaning
- Added `validate_and_clean_data()` for data validation
- Enhanced `generate_excel()` with auto-numbering and formatting
- Improved data filtering to skip invalid OCR results

## [1.0.0] - 2024-01-22

### Added - Claude Code Skill Integration
- **skill.md**: Complete skill definition with usage guidelines
- **marketplace.json**: Skill metadata and dependency specifications
- **.claudeignore**: Ignore patterns for Claude Code
- **CHANGELOG.md**: Version history tracking
- Comprehensive documentation for Claude integration
- Automatic skill triggering based on keywords
- Workflow diagrams and best practices

### Existing Features (Preserved)
- Multi-format support (PDF, JPG, PNG, BMP, TIFF)
- Tesseract OCR integration with Chinese language support
- Image preprocessing (grayscale conversion, contrast enhancement)
- Intelligent regex-based field extraction for 7 key fields:
  - Serial Number (序号)
  - Copyright Owner (著作权人)
  - Software Name (软件名称)
  - First Publication Date (首次发表日期)
  - Acquisition Method (权利取得方式)
  - Rights Scope (权利范围)
  - Registration Number (登记号)
- Filename fallback mechanism for poor OCR quality
- Batch processing with directory scanning
- Excel report generation
- Multi-page PDF support
- LLM-assisted extraction prompt template

### Technical Details
- Python 3.7+ compatibility
- Modular script architecture
- Error handling and validation
- Progress feedback during batch operations

## [Unreleased]

### Planned
- PaddleOCR integration for improved Chinese text recognition
- Web interface with drag-and-drop upload
- Confidence scoring for extracted fields
- Parallel processing for large batches
- Docker containerization
- Additional certificate type support (trademark, patent)
- Machine learning-based field detection
- Real-time validation against copyright office database

---

## Version History

- **1.1.0** (2024-01-22): Excel quality improvements - clean data, auto-numbering, professional formatting
- **1.0.0** (2024-01-22): Initial Claude Code skill release
- **0.1.0** (Pre-release): Original Python scripts version
