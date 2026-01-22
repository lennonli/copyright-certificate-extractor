# Contributing to Copyright Certificate Extractor

Thank you for your interest in contributing! This document provides guidelines for contributing to this Claude Code skill.

## How to Contribute

### Reporting Issues
- Use GitHub Issues to report bugs or suggest features
- Include detailed steps to reproduce bugs
- Provide sample files (anonymized) when possible
- Specify your environment (OS, Python version, Tesseract version)

### Suggesting Enhancements
- Check existing issues first to avoid duplicates
- Clearly describe the use case and expected behavior
- Explain why this enhancement would be useful

### Code Contributions

#### Setting Up Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/lennonli/copyright-certificate-extractor.git
   cd copyright-certificate-extractor
   ```

2. **Install dependencies**:
   ```bash
   # System dependencies (macOS)
   brew install tesseract tesseract-lang poppler

   # Python dependencies
   pip install -r requirements.txt
   ```

3. **Test your setup**:
   ```bash
   # Test OCR extraction
   python scripts/extract_ocr.py <test_certificate.pdf>
   ```

#### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow coding standards**:
   - Use Python 3.7+ type hints
   - Follow PEP 8 style guide
   - Add docstrings to functions
   - Keep functions focused and testable

3. **Test your changes**:
   ```bash
   # Test with various certificate formats
   python scripts/batch_extract.py test_data/ output.xlsx
   ```

4. **Update documentation**:
   - Update README.md if usage changes
   - Update skill.md for Claude integration changes
   - Add entry to CHANGELOG.md
   - Update version in marketplace.json

5. **Commit with clear messages**:
   ```bash
   git commit -m "Add: Support for new certificate field extraction"
   ```

#### Pull Request Process

1. **Ensure your PR**:
   - Passes all existing tests
   - Includes new tests for new features
   - Updates relevant documentation
   - Follows the coding standards

2. **PR Description should include**:
   - What changes were made and why
   - How to test the changes
   - Screenshots/examples if applicable
   - Related issue numbers

3. **Review process**:
   - Maintainers will review your PR
   - Address any requested changes
   - Once approved, your PR will be merged

### Improving OCR Accuracy

If you want to improve OCR accuracy:

1. **Add new preprocessing methods**:
   - Modify `scripts/extract_ocr.py`
   - Add new image enhancement techniques
   - Test with low-quality scans

2. **Enhance regex patterns**:
   - Update `scripts/parse_copyright.py`
   - Add test cases for edge cases
   - Document pattern changes

3. **Integrate new OCR engines**:
   - Add PaddleOCR or other engines
   - Make engine selection configurable
   - Maintain backward compatibility

### Adding New Features

#### Example: Adding Confidence Scoring

```python
# In parse_copyright.py
def parse_with_confidence(text):
    data = {}
    confidence = {}

    # Extract field with confidence score
    match = re.search(pattern, text)
    if match:
        data['field'] = match.group(1)
        confidence['field'] = calculate_confidence(match)

    return data, confidence
```

#### Example: Adding New Certificate Type

1. Create new parsing module: `scripts/parse_trademark.py`
2. Update batch processor to detect certificate type
3. Add type-specific field mappings
4. Update documentation

### Testing Guidelines

#### Manual Testing
- Test with various certificate qualities (high/low resolution)
- Test with multi-page PDFs
- Test with different file formats
- Test batch processing with mixed formats

#### Test Cases to Cover
- Empty/corrupted files
- Files with no text
- Files with partial information
- Non-standard certificate formats
- Very large batch operations

### Documentation Style

- Use clear, concise language
- Include code examples
- Provide both Chinese and English when relevant
- Use markdown formatting consistently
- Add screenshots for visual features

### Skill-Specific Guidelines

When modifying skill.md:

1. **Keep trigger keywords updated**:
   - Add new relevant keywords
   - Test that Claude recognizes them
   - Document in marketplace.json

2. **Update workflow descriptions**:
   - Reflect any process changes
   - Keep diagrams current
   - Update error handling guidance

3. **Maintain examples**:
   - Ensure examples work with current code
   - Add examples for new features
   - Show both success and error cases

## Code of Conduct

### Our Standards
- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior
- Harassment or discriminatory language
- Trolling or insulting comments
- Publishing others' private information
- Other unprofessional conduct

## Questions?

- Open a GitHub Discussion for general questions
- Use Issues for bug reports and feature requests
- Check existing documentation first

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers this project.

---

Thank you for contributing to make this skill better! 🎉
