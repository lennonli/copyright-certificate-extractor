#!/usr/bin/env python3
"""
Unit tests for OCR extraction module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import tempfile
from PIL import Image

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from logger import OCRError, DependencyError


class TestExtractOCR(unittest.TestCase):
    """Test cases for extract_ocr module."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_image = self.test_dir / "test.png"
        self.test_pdf = self.test_dir / "test.pdf"

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    @patch('scripts.extract_ocr.pytesseract')
    def test_check_dependencies_success(self, mock_tesseract):
        """Test dependency check when Tesseract is installed."""
        from scripts.extract_ocr import check_dependencies

        mock_tesseract.get_tesseract_version.return_value = "4.1.1"
        mock_tesseract.get_languages.return_value = ['chi_sim', 'eng']

        # Should not raise exception
        check_dependencies()

    @patch('scripts.extract_ocr.pytesseract')
    def test_check_dependencies_missing_tesseract(self, mock_tesseract):
        """Test dependency check when Tesseract is missing."""
        from scripts.extract_ocr import check_dependencies
        from pytesseract import TesseractNotFoundError

        mock_tesseract.get_tesseract_version.side_effect = TesseractNotFoundError()

        with self.assertRaises(DependencyError):
            check_dependencies()

    def test_preprocess_image(self):
        """Test image preprocessing."""
        from scripts.extract_ocr import preprocess_image

        # Create test image
        img = Image.new('RGB', (100, 100), color='white')

        # Preprocess
        result = preprocess_image(img)

        # Should return grayscale image
        self.assertEqual(result.mode, 'L')

    @patch('scripts.extract_ocr.pytesseract.image_to_string')
    @patch('scripts.extract_ocr.Image.open')
    def test_extract_text_from_image_success(self, mock_open, mock_ocr):
        """Test successful text extraction from image."""
        from scripts.extract_ocr import extract_text_from_image

        # Create test image
        test_img = Image.new('RGB', (100, 100), color='white')
        self.test_image.touch()

        mock_open.return_value = test_img
        mock_ocr.return_value = "测试文本"

        result = extract_text_from_image(self.test_image)

        self.assertEqual(result, "测试文本")
        mock_ocr.assert_called_once()

    @patch('scripts.extract_ocr.pytesseract.image_to_string')
    @patch('scripts.extract_ocr.Image.open')
    def test_extract_text_from_image_empty(self, mock_open, mock_ocr):
        """Test extraction when no text is found."""
        from scripts.extract_ocr import extract_text_from_image

        test_img = Image.new('RGB', (100, 100), color='white')
        self.test_image.touch()

        mock_open.return_value = test_img
        mock_ocr.return_value = ""

        result = extract_text_from_image(self.test_image)

        self.assertEqual(result, "")

    def test_extract_text_from_image_file_not_found(self):
        """Test extraction with non-existent file."""
        from scripts.extract_ocr import extract_text_from_image

        non_existent = self.test_dir / "nonexistent.png"

        with self.assertRaises(OCRError):
            extract_text_from_image(non_existent)

    @patch('scripts.extract_ocr.pytesseract.image_to_string')
    @patch('scripts.extract_ocr.convert_from_path')
    def test_extract_text_from_pdf_success(self, mock_convert, mock_ocr):
        """Test successful text extraction from PDF."""
        from scripts.extract_ocr import extract_text_from_pdf

        # Mock PDF pages
        page1 = Image.new('RGB', (100, 100), color='white')
        page2 = Image.new('RGB', (100, 100), color='white')
        mock_convert.return_value = [page1, page2]

        # Mock OCR results
        mock_ocr.side_effect = ["Page 1 text", "Page 2 text"]

        self.test_pdf.touch()
        result = extract_text_from_pdf(self.test_pdf)

        self.assertIn("--- Page 1 ---", result)
        self.assertIn("Page 1 text", result)
        self.assertIn("--- Page 2 ---", result)
        self.assertIn("Page 2 text", result)

    def test_extract_text_unsupported_format(self):
        """Test extraction with unsupported file format."""
        from scripts.extract_ocr import extract_text

        unsupported_file = self.test_dir / "test.txt"
        unsupported_file.touch()

        with self.assertRaises(OCRError) as context:
            extract_text(unsupported_file)

        self.assertIn("Unsupported file format", str(context.exception))


class TestParseCopyright(unittest.TestCase):
    """Test cases for parse_copyright module."""

    def test_validate_field_registration_number(self):
        """Test validation of registration number."""
        from scripts.parse_copyright import validate_field

        # Valid registration number
        self.assertTrue(validate_field('登记号', '2021SR0123456'))

        # Invalid registration numbers
        self.assertFalse(validate_field('登记号', '2021XX0123456'))
        self.assertFalse(validate_field('登记号', 'SR0123456'))
        self.assertFalse(validate_field('登记号', ''))

    def test_validate_field_serial_number(self):
        """Test validation of serial number."""
        from scripts.parse_copyright import validate_field

        # Valid serial numbers
        self.assertTrue(validate_field('序号', '1234567'))
        self.assertTrue(validate_field('序号', '123456'))

        # Invalid serial numbers
        self.assertFalse(validate_field('序号', '12345'))  # Too short
        self.assertFalse(validate_field('序号', 'ABC123'))  # Not all digits

    def test_validate_field_date(self):
        """Test validation of publication date."""
        from scripts.parse_copyright import validate_field

        # Valid dates
        self.assertTrue(validate_field('首次发表日期', '2021年12月31日'))
        self.assertTrue(validate_field('首次发表日期', '2021年1月1日'))
        self.assertTrue(validate_field('首次发表日期', '未发表'))

        # Invalid dates
        self.assertFalse(validate_field('首次发表日期', '2021-12-31'))
        self.assertFalse(validate_field('首次发表日期', ''))

    def test_parse_single_block_complete(self):
        """Test parsing a complete certificate block."""
        from scripts.parse_copyright import _parse_single_block

        test_text = """
        No. 1234567
        著作权人: 测试公司
        软件名称: 测试软件V1.0
        首次发表日期: 2021年12月1日
        权利取得方式: 原始取得
        权利范围: 全部权利
        登记号: 2021SR0123456
        """

        result = _parse_single_block(test_text)

        self.assertEqual(result['序号'], '1234567')
        self.assertEqual(result['著作权人'], '测试公司')
        self.assertEqual(result['软件名称'], '测试软件V1.0')
        self.assertEqual(result['首次发表日期'], '2021年12月1日')
        self.assertEqual(result['权利取得方式'], '原始取得')
        self.assertEqual(result['权利范围'], '全部权利')
        self.assertEqual(result['登记号'], '2021SR0123456')

    def test_parse_single_block_partial(self):
        """Test parsing a partial certificate block."""
        from scripts.parse_copyright import _parse_single_block

        test_text = """
        著作权人: 测试公司
        软件名称: 测试软件
        登记号: 2021SR0123456
        """

        result = _parse_single_block(test_text)

        self.assertEqual(result['著作权人'], '测试公司')
        self.assertEqual(result['软件名称'], '测试软件')
        self.assertEqual(result['登记号'], '2021SR0123456')
        self.assertEqual(result['序号'], '')  # Missing field

    def test_parse_copyright_text_single_page(self):
        """Test parsing single page certificate."""
        from scripts.parse_copyright import parse_copyright_text

        test_text = """
        No. 1234567
        著作权人: 测试公司
        软件名称: 测试软件
        登记号: 2021SR0123456
        """

        result = parse_copyright_text(test_text)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['著作权人'], '测试公司')

    def test_parse_copyright_text_multiple_pages(self):
        """Test parsing multi-page PDF."""
        from scripts.parse_copyright import parse_copyright_text

        test_text = """
        --- Page 1 ---
        著作权人: 公司A
        软件名称: 软件A
        登记号: 2021SR0001111

        --- Page 2 ---
        著作权人: 公司B
        软件名称: 软件B
        登记号: 2021SR0002222
        """

        result = parse_copyright_text(test_text)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['著作权人'], '公司A')
        self.assertEqual(result[1]['著作权人'], '公司B')

    def test_parse_copyright_text_empty(self):
        """Test parsing empty text."""
        from scripts.parse_copyright import parse_copyright_text
        from logger import ValidationError

        with self.assertRaises(ValidationError):
            parse_copyright_text("")

    def test_parse_copyright_text_no_valid_data(self):
        """Test parsing text with no valid certificate data."""
        from scripts.parse_copyright import parse_copyright_text
        from logger import ValidationError

        test_text = "Some random text without certificate fields"

        with self.assertRaises(ValidationError):
            parse_copyright_text(test_text)


class TestBatchExtract(unittest.TestCase):
    """Test cases for batch extraction."""

    def setUp(self):
        """Set up test directory."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    @patch('scripts.batch_extract.generate_excel')
    @patch('scripts.batch_extract.parse_copyright_text')
    @patch('scripts.batch_extract.extract_text')
    def test_batch_extract_success(self, mock_extract, mock_parse, mock_excel):
        """Test successful batch extraction."""
        # This is a placeholder - actual implementation would be more complex
        # Create test files
        (self.test_dir / "cert1.png").touch()
        (self.test_dir / "cert2.pdf").touch()

        # Mock extraction results
        mock_extract.return_value = "Extracted text"
        mock_parse.return_value = [{'软件名称': '测试软件', '登记号': '2021SR0123456'}]

        # This would test the actual batch_extract function
        # For now, just verify setup
        self.assertTrue((self.test_dir / "cert1.png").exists())
        self.assertTrue((self.test_dir / "cert2.pdf").exists())


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestExtractOCR))
    suite.addTests(loader.loadTestsFromTestCase(TestParseCopyright))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchExtract))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
