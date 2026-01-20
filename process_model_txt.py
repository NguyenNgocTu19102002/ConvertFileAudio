#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script xử lý tất cả file TXT trong model_txt:
- Convert TXT sang Audio
- Lưu audio vào uploads
- Tạo QR code và lưu vào qr_data.json
"""

import os
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path
from io import BytesIO
import base64
import qrcode
from werkzeug.utils import secure_filename
from txt_to_audio import convert_txt_to_audio

# Fix encoding cho Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Config
MODEL_TXT_DIR = Path('model_txt')
UPLOAD_FOLDER = Path('uploads')
QR_DATA_FILE = 'qr_data.json'
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
VOICE = 'vi-VN-HoaiMyNeural'
AUDIO_FORMAT = 'mp3'

# Tạo thư mục uploads nếu chưa có
UPLOAD_FOLDER.mkdir(exist_ok=True)


def load_qr_data():
    """Load danh sách QR codes từ file JSON"""
    if Path(QR_DATA_FILE).exists():
        try:
            with open(QR_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_qr_data(data):
    """Lưu danh sách QR codes vào file JSON"""
    with open(QR_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_qr_record(audio_filename, audio_url, full_url, qr_base64, title=None):
    """Thêm record QR code vào database"""
    data = load_qr_data()
    record = {
        'id': str(uuid.uuid4()),
        'title': title or audio_filename,
        'audio_filename': audio_filename,
        'audio_url': audio_url,
        'full_url': full_url,
        'qr_base64': qr_base64,
        'created_at': datetime.now().isoformat()
    }
    data.append(record)
    save_qr_data(data)
    return record


def generate_qr_code(url):
    """Tạo QR code từ URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG', optimize=False)
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    
    return img_str


def process_txt_file(txt_path: Path):
    """Xử lý một file TXT: convert sang audio, tạo QR code"""
    try:
        print(f"\n{'='*60}")
        print(f"Đang xử lý: {txt_path}")
        
        # Đặt tên file audio giống tên file txt (chỉ đổi extension)
        audio_filename = secure_filename(txt_path.stem + f'.{AUDIO_FORMAT}')
        output_audio_path = UPLOAD_FOLDER / audio_filename
        
        # Kiểm tra nếu file audio đã tồn tại
        if output_audio_path.exists():
            print(f"  ⚠ File audio đã tồn tại: {audio_filename}")
            # Kiểm tra xem đã có trong qr_data.json chưa
            data = load_qr_data()
            existing = next((item for item in data if item.get('audio_filename') == audio_filename), None)
            if existing:
                print(f"  ✓ Đã có trong qr_data.json, bỏ qua")
                return existing
            else:
                # File audio có nhưng chưa có trong qr_data, tạo QR code
                print(f"  → File audio có nhưng chưa có QR, tạo QR code...")
        else:
            # Convert TXT to Audio
            print(f"  → Đang convert sang audio...")
            temp_audio_path = convert_txt_to_audio(
                str(txt_path),
                output_path=str(output_audio_path),
                voice=VOICE,
                format=AUDIO_FORMAT
            )
            
            # Đảm bảo file đã được tạo
            if not Path(temp_audio_path).exists():
                raise Exception(f"Không tạo được file audio: {temp_audio_path}")
        
        # Tạo URL cho audio
        audio_url = f'/audio/{audio_filename}'
        full_url = BASE_URL.rstrip('/') + audio_url
        
        # Generate QR code
        print(f"  → Đang tạo QR code...")
        qr_base64 = generate_qr_code(full_url)
        
        # Tạo title từ tên file (bỏ extension)
        title = txt_path.stem
        
        # Lưu vào qr_data.json
        print(f"  → Đang lưu vào qr_data.json...")
        record = add_qr_record(audio_filename, audio_url, full_url, qr_base64, title)
        
        print(f"  ✓ Hoàn thành: {title}")
        print(f"    Audio: {audio_filename}")
        print(f"    URL: {full_url}")
        
        return record
        
    except Exception as e:
        print(f"  ✗ Lỗi: {str(e)}")
        return None


def main():
    """Xử lý tất cả file TXT trong model_txt"""
    if not MODEL_TXT_DIR.exists():
        print(f"Không tìm thấy thư mục: {MODEL_TXT_DIR}")
        return
    
    # Tìm tất cả file .txt
    txt_files = list(MODEL_TXT_DIR.rglob('*.txt'))
    
    if not txt_files:
        print(f"Không tìm thấy file .txt nào trong {MODEL_TXT_DIR}")
        return
    
    print(f"Tìm thấy {len(txt_files)} file .txt")
    print(f"BASE_URL: {BASE_URL}")
    print(f"Voice: {VOICE}")
    print(f"Format: {AUDIO_FORMAT}")
    
    # Xử lý từng file
    success_count = 0
    error_count = 0
    
    for i, txt_file in enumerate(txt_files, 1):
        print(f"\n[{i}/{len(txt_files)}]")
        result = process_txt_file(txt_file)
        if result:
            success_count += 1
        else:
            error_count += 1
    
    # Tổng kết
    print(f"\n{'='*60}")
    print(f"Tổng kết:")
    print(f"  ✓ Thành công: {success_count}")
    print(f"  ✗ Lỗi: {error_count}")
    print(f"  Tổng: {len(txt_files)}")
    print(f"\nDữ liệu QR code đã được lưu vào: {QR_DATA_FILE}")


if __name__ == '__main__':
    main()

