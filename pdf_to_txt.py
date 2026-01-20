#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool convert PDF sang TXT
Sử dụng pdfplumber để extract text từ PDF
"""

import sys
import os
import argparse
from pathlib import Path


def convert_pdf_to_txt(pdf_path: str, output_path: str = None) -> str:
    """
    Convert file PDF sang TXT
    
    Args:
        pdf_path: Đường dẫn file PDF
        output_path: Đường dẫn file TXT output (nếu None thì tự động tạo)
    
    Returns:
        Đường dẫn file TXT đã tạo
    """
    try:
        import pdfplumber
    except ImportError:
        print("Can cai dat pdfplumber: pip install pdfplumber")
        sys.exit(1)
    
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {pdf_path}")
    
    if not pdf_file.suffix.lower() == '.pdf':
        raise ValueError(f"File phải có extension .pdf: {pdf_path}")
    
    # Tạo output path nếu chưa có
    if output_path is None:
        output_path = pdf_file.with_suffix('.txt')
    else:
        output_path = Path(output_path)
    
    # Extract text từ PDF
    text_content = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Dang xu ly {len(pdf.pages)} trang...")
            
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append(f"--- Trang {i} ---\n{text}\n")
                print(f"Da xu ly trang {i}/{len(pdf.pages)}")
    
    except Exception as e:
        raise Exception(f"Lỗi khi đọc PDF: {str(e)}")
    
    # Ghi file TXT
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_content))
        print(f"Da tao file: {output_path}")
        return str(output_path)
    
    except Exception as e:
        raise Exception(f"Lỗi khi ghi file TXT: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='Tool convert PDF sang TXT',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python pdf_to_txt.py input.pdf
  python pdf_to_txt.py input.pdf -o output.txt
  python pdf_to_txt.py input.pdf --output output.txt
        """
    )
    
    parser.add_argument(
        'pdf_file',
        help='Đường dẫn file PDF cần convert'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output',
        help='Đường dẫn file TXT output (mặc định: cùng tên với file PDF)'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = convert_pdf_to_txt(args.pdf_file, args.output)
        print(f"\nHoan thanh! File da duoc luu tai: {output_file}")

    except Exception as e:
        print(f"\nLoi: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

