#!/usr/bin/env python3
"""
Multi-engine OCR support with PaddleOCR and Tesseract.
"""

import sys
import os
from pathlib import Path
from typing import Optional, Union, Literal
import logging
from enum import Enum

try:
    import pytesseract
    from PIL import Image, ImageEnhance
    from pdf2image import convert_from_path
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False

from logger import setup_logger, OCRError, DependencyError

# Setup logger
logger = setup_logger('ocr_engine', level=logging.INFO)


class OCREngine(str, Enum):
    """Available OCR engines."""
    TESSERACT = "tesseract"
    PADDLEOCR = "paddleocr"
    AUTO = "auto"


class MultiEngineOCR:
    """
    Multi-engine OCR class supporting both Tesseract and PaddleOCR.
    """

    def __init__(self, engine: OCREngine = OCREngine.AUTO, lang: str = 'chi_sim'):
        """
        Initialize OCR engine.

        Args:
            engine: OCR engine to use (tesseract, paddleocr, or auto)
            lang: Language code (for Tesseract) or language parameter

        Raises:
            DependencyError: If selected engine is not available
        """
        self.lang = lang
        self.engine = self._select_engine(engine)
        self._paddle_ocr = None

        logger.info(f"Initialized OCR with engine: {self.engine}")

    def _select_engine(self, preferred: OCREngine) -> OCREngine:
        """
        Select best available OCR engine.

        Args:
            preferred: Preferred engine

        Returns:
            Selected engine

        Raises:
            DependencyError: If no engine available
        """
        if preferred == OCREngine.AUTO:
            # Prefer PaddleOCR for Chinese text (better accuracy)
            if PADDLEOCR_AVAILABLE and 'chi' in self.lang.lower():
                logger.debug("Auto-selected PaddleOCR for Chinese text")
                return OCREngine.PADDLEOCR
            elif TESSERACT_AVAILABLE:
                logger.debug("Auto-selected Tesseract")
                return OCREngine.TESSERACT
            elif PADDLEOCR_AVAILABLE:
                logger.debug("Auto-selected PaddleOCR (fallback)")
                return OCREngine.PADDLEOCR
            else:
                raise DependencyError(
                    "No OCR engine available. Install one of:\n"
                    "  - Tesseract: brew install tesseract tesseract-lang\n"
                    "  - PaddleOCR: pip install paddleocr paddlepaddle"
                )

        elif preferred == OCREngine.TESSERACT:
            if not TESSERACT_AVAILABLE:
                raise DependencyError(
                    "Tesseract not available. Install with:\n"
                    "  macOS: brew install tesseract tesseract-lang\n"
                    "  Ubuntu: apt-get install tesseract-ocr tesseract-ocr-chi-sim"
                )
            return OCREngine.TESSERACT

        elif preferred == OCREngine.PADDLEOCR:
            if not PADDLEOCR_AVAILABLE:
                raise DependencyError(
                    "PaddleOCR not available. Install with:\n"
                    "  pip install paddleocr paddlepaddle"
                )
            return OCREngine.PADDLEOCR

        else:
            raise ValueError(f"Unknown OCR engine: {preferred}")

    def _get_paddle_ocr(self):
        """Lazy initialization of PaddleOCR."""
        if self._paddle_ocr is None:
            logger.debug("Initializing PaddleOCR...")
            # Determine language
            use_angle_cls = True
            lang = 'ch' if 'chi' in self.lang.lower() else 'en'

            self._paddle_ocr = PaddleOCR(
                use_angle_cls=use_angle_cls,
                lang=lang,
                show_log=False
            )
            logger.debug(f"PaddleOCR initialized with lang={lang}")

        return self._paddle_ocr

    def preprocess_image(self, image: Image.Image) -> Image.Image:
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

            # Enhance contrast (important for low-quality scans)
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(2.0)

            logger.debug("Image preprocessing completed")
            return enhanced

        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}, using original image")
            return image

    def extract_text_tesseract(self, image: Image.Image) -> str:
        """
        Extract text using Tesseract OCR.

        Args:
            image: PIL Image object

        Returns:
            Extracted text
        """
        try:
            processed = self.preprocess_image(image)
            text = pytesseract.image_to_string(processed, lang=self.lang)
            logger.debug(f"Tesseract extracted {len(text)} characters")
            return text
        except Exception as e:
            raise OCRError(f"Tesseract extraction failed: {e}")

    def extract_text_paddleocr(self, image: Image.Image) -> str:
        """
        Extract text using PaddleOCR.

        Args:
            image: PIL Image object

        Returns:
            Extracted text
        """
        try:
            ocr = self._get_paddle_ocr()

            # Convert PIL Image to numpy array
            import numpy as np
            img_array = np.array(image)

            # Run OCR
            result = ocr.ocr(img_array, cls=True)

            # Extract text from results
            if result and result[0]:
                lines = []
                for line in result[0]:
                    if line and len(line) >= 2:
                        text = line[1][0]  # [1] is the text tuple, [0] is the text content
                        lines.append(text)

                full_text = '\n'.join(lines)
                logger.debug(f"PaddleOCR extracted {len(full_text)} characters")
                return full_text
            else:
                logger.warning("PaddleOCR returned no results")
                return ""

        except Exception as e:
            raise OCRError(f"PaddleOCR extraction failed: {e}")

    def extract_text_from_image(self, image: Union[Image.Image, str, Path]) -> str:
        """
        Extract text from image using selected engine.

        Args:
            image: PIL Image or path to image file

        Returns:
            Extracted text
        """
        # Load image if path provided
        if isinstance(image, (str, Path)):
            image = Image.open(image)

        logger.debug(f"Extracting text using {self.engine}")

        if self.engine == OCREngine.TESSERACT:
            return self.extract_text_tesseract(image)
        elif self.engine == OCREngine.PADDLEOCR:
            return self.extract_text_paddleocr(image)
        else:
            raise ValueError(f"Invalid engine: {self.engine}")

    def extract_text_from_pdf(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract text from PDF by converting pages to images.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text from all pages
        """
        pdf_path = Path(pdf_path)
        logger.info(f"Extracting text from PDF: {pdf_path.name}")

        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            logger.info(f"PDF converted to {len(images)} page(s)")

            full_text = ""
            for i, image in enumerate(images, start=1):
                logger.debug(f"Processing page {i}/{len(images)}")

                try:
                    text = self.extract_text_from_image(image)
                    full_text += f"--- Page {i} ---\n{text}\n"
                    logger.debug(f"Page {i}: extracted {len(text)} characters")
                except OCRError as e:
                    logger.error(f"OCR failed on page {i}: {e}")
                    full_text += f"--- Page {i} ---\n[OCR FAILED]\n"

            logger.info(f"Successfully processed {len(images)} pages")
            return full_text

        except Exception as e:
            raise OCRError(f"Error processing PDF {pdf_path}: {e}")

    def extract_text(self, file_path: Union[str, Path]) -> str:
        """
        Main extraction function for any file type.

        Args:
            file_path: Path to PDF or image file

        Returns:
            Extracted text
        """
        path = Path(file_path)

        if not path.exists():
            raise OCRError(f"File not found: {file_path}")

        suffix = path.suffix.lower()
        logger.info(f"Processing file: {path.name} (format: {suffix})")

        if suffix == '.pdf':
            return self.extract_text_from_pdf(path)
        elif suffix in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']:
            return self.extract_text_from_image(path)
        else:
            raise OCRError(f"Unsupported file format: {suffix}")


def create_ocr_engine(
    engine: str = "auto",
    lang: str = "chi_sim"
) -> MultiEngineOCR:
    """
    Factory function to create OCR engine.

    Args:
        engine: Engine name (tesseract, paddleocr, auto)
        lang: Language code

    Returns:
        Configured OCR engine instance
    """
    engine_enum = OCREngine(engine.lower())
    return MultiEngineOCR(engine=engine_enum, lang=lang)


if __name__ == "__main__":
    # Demo usage
    logger.setLevel(logging.DEBUG)

    print("Available OCR Engines:")
    print(f"  - Tesseract: {'✓' if TESSERACT_AVAILABLE else '✗'}")
    print(f"  - PaddleOCR: {'✓' if PADDLEOCR_AVAILABLE else '✗'}")
    print()

    if len(sys.argv) < 2:
        print("Usage: python ocr_engine.py <file_path> [engine] [lang]")
        print("\nEngines: tesseract, paddleocr, auto (default)")
        print("Languages: chi_sim (default), eng, etc.")
        sys.exit(1)

    file_path = sys.argv[1]
    engine = sys.argv[2] if len(sys.argv) > 2 else "auto"
    lang = sys.argv[3] if len(sys.argv) > 3 else "chi_sim"

    try:
        ocr = create_ocr_engine(engine=engine, lang=lang)
        text = ocr.extract_text(file_path)
        print(text)
    except (OCRError, DependencyError) as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
