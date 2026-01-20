#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool convert file TXT sang Audio (MP3/WAV)
Sử dụng edge-tts để hỗ trợ tiếng Việt
"""

import sys
import argparse
from pathlib import Path


def convert_txt_to_audio(txt_path: str, output_path: str = None, voice: str = "vi-VN-HoaiMyNeural", format: str = "mp3") -> str:
    """
    Convert file TXT sang Audio
    
    Args:
        txt_path: Đường dẫn file TXT
        output_path: Đường dẫn file audio output (nếu None thì tự động tạo)
        voice: Giọng đọc (mặc định: vi-VN-HoaiMyNeural - nữ)
        format: Định dạng audio (mp3 hoặc wav)
    
    Returns:
        Đường dẫn file audio đã tạo
    """
    try:
        import edge_tts
        import asyncio
    except ImportError:
        print("Can cai dat edge-tts: pip install edge-tts")
        sys.exit(1)
    
    txt_file = Path(txt_path)
    if not txt_file.exists():
        raise FileNotFoundError(f"Khong tim thay file: {txt_path}")
    
    if not txt_file.suffix.lower() == '.txt':
        raise ValueError(f"File phai co extension .txt: {txt_path}")
    
    # Đọc nội dung file TXT
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text_content = f.read().strip()
        
        if not text_content:
            raise ValueError("File TXT rong")
    
    except Exception as e:
        raise Exception(f"Loi khi doc file TXT: {str(e)}")
    
    # Không xử lý gì thêm, chỉ convert trực tiếp sang audio
    
    # Tạo output path nếu chưa có
    if output_path is None:
        output_path = txt_file.with_suffix(f'.{format}')
    else:
        output_path = Path(output_path)
    
    # Convert text to speech
    async def generate_speech():
        communicate = edge_tts.Communicate(text_content, voice)
        await communicate.save(str(output_path))
    
    try:
        print(f"Dang tao audio voi giong: {voice}...")
        print(f"Kich thuoc text: {len(text_content)} ky tu")
        
        asyncio.run(generate_speech())
        
        print(f"Da tao file audio: {output_path}")
        return str(output_path)
    
    except Exception as e:
        raise Exception(f"Loi khi tao audio: {str(e)}")


def list_voices(language: str = "vi-VN"):
    """
    Liệt kê các giọng đọc có sẵn cho ngôn ngữ
    
    Args:
        language: Mã ngôn ngữ (vi-VN, en-US, ...)
    """
    try:
        import edge_tts
        import asyncio
        
        async def get_voices():
            voices = await edge_tts.list_voices()
            filtered = [v for v in voices if language in v["Locale"]]
            return filtered
        
        voices = asyncio.run(get_voices())
        
        print(f"\nCac giong doc cho {language}:")
        print("-" * 60)
        for voice in voices:
            gender = voice["Gender"]
            name = voice["ShortName"]
            friendly = voice["FriendlyName"]
            print(f"  {name:30} ({gender:6}) - {friendly}")
        
        return voices
    
    except ImportError:
        print("Can cai dat edge-tts: pip install edge-tts")
        return []


def main():
    parser = argparse.ArgumentParser(
        description='Tool convert TXT sang Audio',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Vi du:
  python txt_to_audio.py sample.txt
  python txt_to_audio.py sample.txt -o output.mp3
  python txt_to_audio.py sample.txt --voice vi-VN-NamMinhNeural
  python txt_to_audio.py sample.txt --list-voices
        """
    )
    
    parser.add_argument(
        'txt_file',
        nargs='?',
        help='Duong dan file TXT can convert'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output',
        help='Duong dan file audio output (mac dinh: cung ten voi file TXT)'
    )
    
    parser.add_argument(
        '-v', '--voice',
        dest='voice',
        default='vi-VN-HoaiMyNeural',
        help='Giong doc (mac dinh: vi-VN-HoaiMyNeural)'
    )
    
    parser.add_argument(
        '-f', '--format',
        dest='format',
        choices=['mp3', 'wav'],
        default='mp3',
        help='Dinh dang audio (mp3 hoac wav, mac dinh: mp3)'
    )
    
    parser.add_argument(
        '--list-voices',
        action='store_true',
        help='Hien thi danh sach giong doc co san'
    )
    
    args = parser.parse_args()
    
    # List voices
    if args.list_voices:
        list_voices()
        return
    
    # Convert file
    if not args.txt_file:
        parser.print_help()
        print("\nHoac su dung --list-voices de xem danh sach giong doc")
        sys.exit(1)
    
    try:
        output_file = convert_txt_to_audio(
            args.txt_file, 
            args.output, 
            args.voice,
            args.format
        )
        print(f"\nHoan thanh! File da duoc luu tai: {output_file}")
    
    except Exception as e:
        print(f"\nLoi: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

