# Changelog

All notable changes to the Copyright Certificate Extractor skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

- **1.0.0** (2024-01-22): Initial Claude Code skill release
- **0.1.0** (Pre-release): Original Python scripts version
