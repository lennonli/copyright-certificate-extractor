# Copyright Certificate Extractor

这是一个专门用于从软件著作权登记证书（PDF 或图片格式）中提取结构化信息的工具技能。

## 核心功能

- **多格式支持**：支持 PDF、JPG、PNG、BMP 等多种格式的软著证书识别。
- **高精度 OCR**：内置图像预处理（对比度增强、灰度化），显著提升扫描件识别率。
- **智能解析**：自动提取序号、著作权人、软件名称、首次发表日期、权利取得方式、权利范围、登记号等关键字段。
- **自动修正**：当 OCR 识别效果不佳时，支持通过文件名自动补全（Filename Fallback）。
- **批量处理**：支持对整个目录进行扫描，并汇总生成 Excel 报表。
- **多页 PDF**：支持解析包含多个证书的单一 PDF 文件。

## 安装指南

### 系统依赖
- **Tesseract OCR**: 必须安装。
  - macOS: `brew install tesseract tesseract-lang` (需包含 `chi_sim` 语言包)
- **Poppler**: 用于处理 PDF。
  - macOS: `brew install poppler`

### Python 依赖
```bash
pip install pytesseract pdf2image Pillow openpyxl
```

## 使用方法

### 1. 批量提取并生成 Excel
这是最常用的命令，会自动扫描文件夹内的所有证书并汇总。
```bash
python scripts/batch_extract.py <证书目录路径> <输出Excel路径.xlsx>
```

### 2. 单个文件 OCR 识别
```bash
python scripts/extract_ocr.py <证书路径> > output.txt
```

### 3. 解析文本信息
```bash
python scripts/parse_copyright.py output.txt > data.json
```

### 4. 生成 Excel 文件
```bash
python scripts/generate_excel.py result.xlsx data.json
```

## 目录结构说明

- `scripts/extract_ocr.py`: 负责图像预处理和文字提取。
- `scripts/parse_copyright.py`: 核心解析逻辑，包含增强型正则表达式。
- `scripts/batch_extract.py`: 批量化工作流脚本。
- `scripts/generate_excel.py`: Excel 报表生成工具。
- `references/llm_prompt.md`: 针对极其复杂件的 LLM 辅助识别提示词。

## 注意事项

- 建议证书扫描分辨率不低于 300 DPI 以获得最佳识别效果。
- 对于多页 PDF 且文字极为模糊的情况，建议手动检查生成的 Excel 汇总表。
