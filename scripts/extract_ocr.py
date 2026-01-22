#!/usr/bin/env python3
import sys
import os
import pytesseract
from PIL import Image, ImageEnhance
from pdf2image import convert_from_path
from pathlib import Path

def preprocess_image(image):
    """
    Apply preprocessing to improve OCR quality.
    """
    try:
        # Convert to grayscale
        gray = image.convert('L')
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(2.0)
        return enhanced
    except Exception as e:
        print(f"Warning: Image preprocessing failed: {e}", file=sys.stderr)
        return image

def extract_text_from_image(image_path, lang='chi_sim'):
    """
    Extract text from an image file using Tesseract OCR.
    """
    try:
        image = Image.open(image_path)
        processed_image = preprocess_image(image)
        text = pytesseract.image_to_string(processed_image, lang=lang)
        return text
    except Exception as e:
        print(f"Error extracting text from image {image_path}: {e}", file=sys.stderr)
        return ""

def extract_text_from_pdf(pdf_path, lang='chi_sim'):
    """
    Extract text from a PDF file by converting pages to images first.
    """
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        full_text = ""
        
        for i, image in enumerate(images):
            processed_image = preprocess_image(image)
            text = pytesseract.image_to_string(processed_image, lang=lang)
            full_text += f"--- Page {i+1} ---\n{text}\n"
            
        return full_text
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}", file=sys.stderr)
        return ""

def extract_text(file_path, lang='chi_sim'):
    """
    Main extraction function that handles both PDF and image files.
    """
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}", file=sys.stderr)
        return None
        
    suffix = path.suffix.lower()
    
    if suffix == '.pdf':
        return extract_text_from_pdf(file_path, lang)
    elif suffix in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']:
        return extract_text_from_image(file_path, lang)
    else:
        print(f"Unsupported file format: {suffix}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_ocr.py <file_path> [lang]")
        sys.exit(1)
        
    file_path = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else 'chi_sim'
    
    text = extract_text(file_path, lang)
    if text:
        print(text)