# QR Audio Generator

Web application để convert PDF/TXT sang Audio và tạo QR Code.

## Tính năng

- ✅ Convert PDF → TXT → Audio
- ✅ Upload Audio trực tiếp
- ✅ Tạo QR Code cho audio
- ✅ Upload nhiều file cùng lúc
- ✅ Quản lý danh sách QR Codes
- ✅ Download QR Code chất lượng cao để in
- ✅ Hỗ trợ tiếng Việt (TTS)

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
python app.py
```

Truy cập: http://localhost:5000

## Cấu trúc Project

```
├── app.py                 # Web server chính (Flask)
├── txt_to_audio.py       # Module convert TXT → Audio
├── pdf_to_txt.py         # Tool CLI convert PDF → TXT (optional)
├── requirements.txt       # Dependencies
├── Dockerfile            # Docker configuration
├── DEPLOY.md             # Hướng dẫn deploy
└── README_QR.md          # Hướng dẫn sử dụng QR Code
```

## API Endpoints

- `GET /` - Trang chủ (upload file)
- `GET /manage` - Trang quản lý QR codes
- `POST /upload` - Upload audio file
- `POST /txt-to-qr` - Upload TXT, convert sang audio và tạo QR
- `POST /api/batch-upload` - Upload nhiều file cùng lúc
- `GET /api/qr-list` - Lấy danh sách QR codes
- `GET /qr-download/<id>` - Download QR code chất lượng cao
- `DELETE /api/qr-delete/<id>` - Xóa QR code
- `GET /audio/<filename>` - Serve audio file
- `GET /health` - Health check

## Deploy

Xem file `DEPLOY.md` để biết cách deploy lên server.

## Sử dụng QR Code

Xem file `README_QR.md` để biết cách in và sử dụng QR code.
