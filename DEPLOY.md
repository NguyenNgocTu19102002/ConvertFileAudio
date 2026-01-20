# Hướng Dẫn Deploy

## Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

## Chạy Local

```bash
python app.py
```

Truy cập: http://localhost:5000

## Deploy lên Server

### 1. Sử dụng Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 2. Sử dụng Waitress (Windows)

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

### 3. Deploy lên Heroku

Tạo file `Procfile`:
```
web: gunicorn app:app
```

Tạo file `.env` (nếu cần):
```
PORT=5000
```

Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### 4. Deploy lên VPS/Cloud

#### Sử dụng systemd (Linux)

Tạo file `/etc/systemd/system/qr-audio.service`:

```ini
[Unit]
Description=QR Audio Generator
After=network.target

[Service]
User=your-user
WorkingDirectory=/path/to/ConvertFileText
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

Khởi động:
```bash
sudo systemctl enable qr-audio
sudo systemctl start qr-audio
```

#### Sử dụng Nginx reverse proxy

Cấu hình Nginx `/etc/nginx/sites-available/qr-audio`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. Sử dụng Docker

Tạo file `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build và run:
```bash
docker build -t qr-audio .
docker run -p 5000:5000 qr-audio
```

## Cấu hình

- Port mặc định: 5000
- Có thể thay đổi qua biến môi trường: `PORT=8080`
- Max file size: 50MB (có thể chỉnh trong `app.py`)

## Tính năng

1. **Upload Audio**: Upload file audio và tạo QR code
2. **Upload TXT**: Upload file TXT, tự động convert sang audio rồi tạo QR code
3. **QR Code**: Quét QR code để nghe audio trực tiếp
4. **Download QR**: Tải QR code về máy

## API Endpoints

- `GET /` - Trang chủ
- `POST /upload` - Upload audio file
- `POST /txt-to-qr` - Upload TXT file, convert sang audio và tạo QR
- `GET /audio/<filename>` - Serve audio file
- `GET /health` - Health check

