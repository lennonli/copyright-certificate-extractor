# Copyright Certificate Extraction Prompt

Please extract the following information from the OCR text of a Software Copyright Registration Certificate.

## Input Text

[PASTE OCR TEXT HERE]

## Desired Output Fields

Please extract the exact values for these fields. If a field is not found, return null or an empty string.

- **序号** (Serial Number): Usually starting with "No." followed by digits.
- **著作权人** (Copyright Owner): The name of the entity or individual owning the copyright.
- **软件名称** (Software Name): The full name of the software, including version if present.
- **首次发表日期** (First Publication Date): Date in YYYY年MM月DD日 format, or "未发表" (Unpublished).
- **权利取得方式** (Acquisition Method): e.g., "原始取得" (Original acquisition).
- **权利范围** (Rights Scope): e.g., "全部权利" (All rights).
- **登记号** (Registration Number): Usually in the format YYYYSRxxxxxx.

## Output Format

Return the result as a valid JSON object:

```json
{
  "序号": "...",
  "著作权人": "...",
  "软件名称": "...",
  "首次发表日期": "...",
  "权利取得方式": "...",
  "权利范围": "...",
  "登记号": "..."
}
```
