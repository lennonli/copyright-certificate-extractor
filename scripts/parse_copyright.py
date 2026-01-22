#!/usr/bin/env python3
"""
Enhanced parsing with improved error handling and validation.
"""

import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from logger import setup_logger, ParsingError, ValidationError

# Setup logger
logger = setup_logger('parse_copyright', level=logging.INFO)


def validate_field(field_name: str, value: str) -> bool:
    """
    Validate extracted field values.

    Args:
        field_name: Name of the field
        value: Extracted value

    Returns:
        True if valid, False otherwise
    """
    if not value or not value.strip():
        return False

    # Field-specific validation
    validators = {
        '登记号': lambda v: bool(re.match(r'^\d{4}SR\d+$', v)),
        '序号': lambda v: v.isdigit() and len(v) >= 6,
        '首次发表日期': lambda v: bool(re.match(r'^\d{4}年\d{1,2}月\d{1,2}日$', v)) or v == '未发表',
    }

    if field_name in validators:
        is_valid = validators[field_name](value)
        if not is_valid:
            logger.warning(f"Field '{field_name}' failed validation: {value}")
        return is_valid

    # Default validation: non-empty and not too short
    return len(value.strip()) >= 2


def _parse_single_block(text: str) -> Dict[str, str]:
    """
    Parse structured information from a single certificate text block.

    Args:
        text: OCR extracted text from certificate

    Returns:
        Dictionary with extracted fields
    """
    logger.debug("Parsing single certificate block")

    data = {
        "序号": "",
        "著作权人": "",
        "软件名称": "",
        "首次发表日期": "",
        "权利取得方式": "",
        "权利范围": "",
        "登记号": ""
    }

    try:
        # Clean text: remove extra whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        logger.debug(f"Cleaned text length: {len(cleaned_text)} chars")

        # Registration Number (e.g., 2021SR0123456)
        reg_match = re.search(r'登\s*记\s*号\s*[:：;]?\s*([0-9]{4}SR[0-9]+)', cleaned_text)
        if reg_match:
            data["登记号"] = reg_match.group(1)
            logger.debug(f"Found 登记号: {data['登记号']}")

        # Serial Number (No. 0000000)
        serial_match = re.search(r'No\.\s*(\d{6,})', cleaned_text)
        if serial_match:
            data["序号"] = serial_match.group(1)
            logger.debug(f"Found 序号: {data['序号']}")

        # Copyright Owner
        owner_match = re.search(r'著\s*作\s*权\s*人\s*[:：;,]?\s*([^\n]+)', cleaned_text)
        if owner_match:
            raw_owner = owner_match.group(1).strip()
            data["著作权人"] = re.sub(r'^[:：,，.\-]\s*', '', raw_owner)
            logger.debug(f"Found 著作权人: {data['著作权人']}")

        # Software Name (complex multi-line matching)
        name_match = re.search(
            r'软\s*件\s*名\s*称\s*[:：;,]?\s*([^\n]+)(?:\n\s*[:：]?\s*([^\n]+))?',
            cleaned_text
        )
        if name_match:
            part1 = name_match.group(1).strip()
            part2 = name_match.group(2)

            full_name = part1
            if part2:
                part2 = part2.strip()
                # Check if part2 is continuation (not a new field)
                if not re.match(r'(著作权人|版本号|V\d|首次发表|权利|开发完成)', part2):
                    part2 = re.sub(r'^[:：]\s*', '', part2)
                    full_name += " " + part2

            data["软件名称"] = full_name
            logger.debug(f"Found 软件名称: {data['软件名称']}")

        # First Publication Date
        date_match = re.search(
            r'首次发表日期\s*[:：;,]?\s*(\d{4}年\d{1,2}月\d{1,2}日|未发表)',
            cleaned_text
        )
        if date_match:
            data["首次发表日期"] = date_match.group(1)
            logger.debug(f"Found 首次发表日期: {data['首次发表日期']}")

        # Acquisition Method
        method_match = re.search(r'权利取得方式\s*[:：;,]?\s*([^\n]+)', cleaned_text)
        if method_match:
            data["权利取得方式"] = method_match.group(1).strip()
            logger.debug(f"Found 权利取得方式: {data['权利取得方式']}")

        # Rights Scope
        scope_match = re.search(r'权\s*利\s*范\s*围\s*[:：;,]?\s*([^\n]+)', cleaned_text)
        if scope_match:
            data["权利范围"] = scope_match.group(1).strip()
            logger.debug(f"Found 权利范围: {data['权利范围']}")

        # Validate extracted data
        valid_fields = sum(1 for k, v in data.items() if validate_field(k, v))
        logger.info(f"Extracted {valid_fields}/7 valid fields")

        return data

    except Exception as e:
        logger.error(f"Error parsing text block: {e}", exc_info=True)
        raise ParsingError(f"Failed to parse certificate text: {e}")


def parse_copyright_text(text: str) -> List[Dict[str, str]]:
    """
    Parse structured information from copyright certificate text.
    Handles multiple pages separated by '--- Page X ---'.

    Args:
        text: OCR extracted text (may contain multiple pages)

    Returns:
        List of dictionaries with extracted information

    Raises:
        ParsingError: If parsing fails critically
        ValidationError: If no valid data found
    """
    if not text or not text.strip():
        raise ValidationError("Empty text provided for parsing")

    logger.info("Starting copyright text parsing")

    try:
        # Split by page delimiter
        pages = re.split(r'--- Page \d+ ---', text)
        logger.info(f"Found {len(pages)} page(s) to process")

        results = []
        for i, page in enumerate(pages, start=1):
            if not page.strip():
                logger.debug(f"Skipping empty page {i}")
                continue

            logger.debug(f"Processing page {i}")

            # Parse each page block
            try:
                data = _parse_single_block(page)

                # Only add if we found at least one key field
                key_fields = [data["序号"], data["登记号"], data["软件名称"], data["著作权人"]]
                if any(key_fields):
                    results.append(data)
                    logger.info(f"Page {i}: Successfully extracted certificate data")
                else:
                    logger.warning(f"Page {i}: No key fields found")

            except ParsingError as e:
                logger.error(f"Page {i}: Parsing failed - {e}")
                continue

        # Fallback: if no pages found, parse as single block
        if not results and text.strip():
            logger.info("No page delimiters found, parsing as single block")
            data = _parse_single_block(text)
            key_fields = [data["序号"], data["登记号"], data["软件名称"], data["著作权人"]]
            if any(key_fields):
                results.append(data)

        if not results:
            raise ValidationError("No valid certificate data extracted from text")

        logger.info(f"Successfully parsed {len(results)} certificate(s)")
        return results

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during parsing: {e}", exc_info=True)
        raise ParsingError(f"Failed to parse copyright text: {e}")


if __name__ == "__main__":
    # Enable debug logging when run directly
    logger.setLevel(logging.DEBUG)

    if len(sys.argv) < 2:
        print("Usage: python parse_copyright.py <text_file_path>")
        print("\nInput: Text file containing OCR extracted text")
        print("Output: JSON array of extracted certificate data")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        # Read input file
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        logger.info(f"Read {len(text)} characters from {file_path}")

        # Parse text
        data_list = parse_copyright_text(text)

        # Output JSON
        output = json.dumps(data_list, ensure_ascii=False, indent=2)
        print(output)

        logger.info(f"Output {len(data_list)} certificate(s) as JSON")

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except ParsingError as e:
        logger.error(f"Parsing error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
