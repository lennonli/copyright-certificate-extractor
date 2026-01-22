#!/usr/bin/env python3
"""
Enhanced OCR extraction with improved error handling and logging.
"""

import sys
import os
from pathlib import Path
from typing import Optional, Union
import logging

try:
    import pytesseract
    from PIL import Image, ImageEnhance
    from pdf2image import convert_from_path
except ImportError as e:
    print(f"ERROR: Missing required dependency: {e}", file=sys.stderr)
    print("Install with: pip install pytesseract pdf2image Pillow", file=sys.stderr)
    sys.exit(1)

from logger import setup_logger, OCRError, DependencyError

# Setup logger
logger = setup_logger('extract_ocr', level=logging.INFO)


def check_dependencies():
    """
    Check if required system dependencies are installed.

    Raises:
        DependencyError: If required dependencies are missing
    """
    try:
        # Check Tesseract
        pytesseract.get_tesseract_version()
        logger.debug("Tesseract OCR found")
    except pytesseract.TesseractNotFoundError:
        raise DependencyError(
            "Tesseract OCR not found. Install with:\n"
            "  macOS: brew install tesseract tesseract-lang\n"
            "  Ubuntu: apt-get install tesseract-ocr tesseract-ocr-chi-sim"
        )

    # Check for Chinese language pack
    try:
        available_langs = pytesseract.get_languages()
        if 'chi_sim' not in available_langs:
            logger.warning("Chinese language pack 'chi_sim' not found")
            logger.warning("Install with: brew install tesseract-lang (macOS)")
    except Exception as e:
        logger.warning(f"Could not check available languages: {e}")


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Apply preprocessing to improve OCR quality.

    Args:
        image: PIL Image object

    Returns:
        Preprocessed PIL Image object
    """
    try:
        logger.debug(f"Preprocessing image: size={image.size}, mode={image.mode}")

        # Convert to grayscale
        gray = image.convert('L')

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(2.0)

        logger.debug("Image preprocessing completed")
        return enhanced

    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}, using original image")
        return image


def extract_text_from_image(image_path: Union[str, Path], lang: str = 'chi_sim') -> str:
    """
    Extract text from an image file using Tesseract OCR.

    Args:
        image_path: Path to image file
        lang: Tesseract language code (default: 'chi_sim')

    Returns:
        Extracted text string

    Raises:
        OCRError: If OCR extraction fails
    """
    image_path = Path(image_path)
    logger.info(f"Extracting text from image: {image_path.name}")

    try:
        # Open and validate image
        image = Image.open(image_path)
        logger.debug(f"Image loaded: {image.format}, {image.size}, {image.mode}")

        # Preprocess
        processed_image = preprocess_image(image)

        # Extract text
        text = pytesseract.image_to_string(processed_image, lang=lang)

        if not text.strip():
            logger.warning(f"No text extracted from {image_path.name}")
            return ""

        logger.info(f"Successfully extracted {len(text)} characters from {image_path.name}")
        return text

    except FileNotFoundError:
        raise OCRError(f"Image file not found: {image_path}")
    except Image.UnidentifiedImageError:
        raise OCRError(f"Cannot identify image file: {image_path}")
    except pytesseract.TesseractError as e:
        raise OCRError(f"Tesseract OCR failed for {image_path}: {e}")
    except Exception as e:
        raise OCRError(f"Unexpected error extracting text from {image_path}: {e}")


def extract_text_from_pdf(pdf_path: Union[str, Path], lang: str = 'chi_sim') -> str:
    """
    Extract text from a PDF file by converting pages to images first.

    Args:
        pdf_path: Path to PDF file
        lang: Tesseract language code (default: 'chi_sim')

    Returns:
        Extracted text from all pages

    Raises:
        OCRError: If PDF processing or OCR fails
    """
    pdf_path = Path(pdf_path)
    logger.info(f"Extracting text from PDF: {pdf_path.name}")

    try:
        # Convert PDF to images
        logger.debug(f"Converting PDF to images: {pdf_path}")
        images = convert_from_path(pdf_path)
        logger.info(f"PDF converted to {len(images)} page(s)")

        full_text = ""

        for i, image in enumerate(images, start=1):
            logger.debug(f"Processing page {i}/{len(images)}")

            # Preprocess
            processed_image = preprocess_image(image)

            # Extract text
            try:
                text = pytesseract.image_to_string(processed_image, lang=lang)
                full_text += f"--- Page {i} ---\n{text}\n"
                logger.debug(f"Page {i}: extracted {len(text)} characters")
            except pytesseract.TesseractError as e:
                logger.error(f"OCR failed on page {i}: {e}")
                full_text += f"--- Page {i} ---\n[OCR FAILED]\n"

        if not full_text.strip():
            logger.warning(f"No text extracted from any page of {pdf_path.name}")

        logger.info(f"Successfully processed {len(images)} pages from {pdf_path.name}")
        return full_text

    except Exception as e:
        raise OCRError(f"Error processing PDF {pdf_path}: {e}")


def extract_text(file_path: Union[str, Path], lang: str = 'chi_sim') -> Optional[str]:
    """
    Main extraction function that handles both PDF and image files.

    Args:
        file_path: Path to PDF or image file
        lang: Tesseract language code (default: 'chi_sim')

    Returns:
        Extracted text or None if extraction fails

    Raises:
        OCRError: If file format is unsupported or extraction fails
    """
    path = Path(file_path)

    if not path.exists():
        raise OCRError(f"File not found: {file_path}")

    if not path.is_file():
        raise OCRError(f"Not a file: {file_path}")

    suffix = path.suffix.lower()

    logger.info(f"Processing file: {path.name} (format: {suffix})")

    try:
        if suffix == '.pdf':
            return extract_text_from_pdf(path, lang)
        elif suffix in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']:
            return extract_text_from_image(path, lang)
        else:
            raise OCRError(f"Unsupported file format: {suffix}")
    except OCRError:
        raise
    except Exception as e:
        raise OCRError(f"Unexpected error processing {path.name}: {e}")


if __name__ == "__main__":
    # Enable debug logging when run directly
    logger.setLevel(logging.DEBUG)

    if len(sys.argv) < 2:
        print("Usage: python extract_ocr.py <file_path> [lang]")
        print("\nSupported formats: PDF, PNG, JPG, JPEG, BMP, TIFF")
        print("Default language: chi_sim (Chinese Simplified)")
        sys.exit(1)

    file_path = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else 'chi_sim'

    try:
        # Check dependencies
        check_dependencies()

        # Extract text
        text = extract_text(file_path, lang)

        if text:
            print(text)
        else:
            logger.error("No text extracted")
            sys.exit(1)

    except DependencyError as e:
        logger.error(f"Dependency error: {e}")
        sys.exit(2)
    except OCRError as e:
        logger.error(f"OCR error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
