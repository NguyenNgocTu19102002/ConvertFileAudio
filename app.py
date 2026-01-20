#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web server để serve audio và generate QR code
"""

import os
import uuid
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, request, send_file, jsonify, render_template_string
from werkzeug.utils import secure_filename
import qrcode
from io import BytesIO
import base64
from txt_to_audio import convert_txt_to_audio

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['DATA_FILE'] = 'qr_data.json'

# Tạo thư mục uploads và temp nếu chưa có
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path('temp').mkdir(exist_ok=True)

# Load/Save QR data
def load_qr_data():
    """Load danh sách QR codes từ file JSON"""
    if Path(app.config['DATA_FILE']).exists():
        try:
            with open(app.config['DATA_FILE'], 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_qr_data(data):
    """Lưu danh sách QR codes vào file JSON"""
    with open(app.config['DATA_FILE'], 'w', encoding='utf-8') as f:
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

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Code Audio Generator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .upload-area:hover {
            background: #f0f0ff;
            border-color: #764ba2;
        }
        .upload-area.dragover {
            background: #e0e0ff;
            border-color: #764ba2;
        }
        input[type="file"] {
            display: none;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 5px;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: scale(1.05);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .qr-container {
            text-align: center;
            margin-top: 30px;
            display: none;
        }
        .qr-container.active {
            display: block;
        }
        .qr-code {
            background: white;
            padding: 20px;
            border-radius: 10px;
            display: inline-block;
            margin: 20px 0;
        }
        .qr-code img {
            max-width: 300px;
            height: auto;
        }
        .audio-link {
            margin-top: 20px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 10px;
            word-break: break-all;
        }
        .audio-link a {
            color: #667eea;
            text-decoration: none;
        }
        .audio-link a:hover {
            text-decoration: underline;
        }
        .status {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            display: none;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            display: block;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            display: block;
        }
        .audio-preview {
            margin: 20px 0;
            text-align: center;
        }
        audio {
            width: 100%;
            max-width: 400px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 QR Code Audio Generator</h1>
        
        <div class="status" id="status"></div>
        
        <div style="margin-bottom: 20px; text-align: center;">
            <a href="/manage" class="btn" style="background: #28a745; text-decoration: none; margin-right: 10px;">📋 Quản Lý QR Codes</a>
            <button class="btn" onclick="switchMode('audio')" id="btnAudio" style="background: #667eea;">Upload Audio</button>
            <button class="btn" onclick="switchMode('txt')" id="btnTxt" style="background: #ccc;">Upload TXT</button>
        </div>
        
        <div style="margin-bottom: 15px; text-align: center;">
            <label style="display: inline-block; margin: 0 10px;">
                <input type="checkbox" id="multipleFiles" onchange="toggleMultiple()"> Upload nhiều file
            </label>
        </div>
        
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="upload-area" id="uploadArea">
                <p style="font-size: 18px; margin-bottom: 10px;" id="uploadText">📁 Kéo thả file audio vào đây</p>
                <p style="color: #666;">hoặc click để chọn file</p>
                <input type="file" id="audioFile" name="audio" accept="audio/*">
                <input type="file" id="audioFiles" name="audio_files" accept="audio/*" multiple style="display: none;">
                <input type="file" id="txtFile" name="txt_file" accept=".txt" style="display: none;">
                <input type="file" id="txtFiles" name="txt_files" accept=".txt" multiple style="display: none;">
            </div>
            <div style="text-align: center;">
                <button type="submit" class="btn" id="submitBtn">Tạo QR Code</button>
            </div>
        </form>
        
        <div class="qr-container" id="qrContainer">
            <h2 style="margin-bottom: 20px;">QR Code của bạn:</h2>
            <div class="qr-code" id="qrCode"></div>
            <div class="audio-link" id="audioLink"></div>
            <div class="audio-preview" id="audioPreview"></div>
            <button class="btn" onclick="downloadQR()">Tải QR Code</button>
        </div>
    </div>

    <script>
        let currentMode = 'audio';
        const uploadArea = document.getElementById('uploadArea');
        const audioInput = document.getElementById('audioFile');
        const txtInput = document.getElementById('txtFile');
        const form = document.getElementById('uploadForm');
        const status = document.getElementById('status');
        const qrContainer = document.getElementById('qrContainer');
        const submitBtn = document.getElementById('submitBtn');
        const uploadText = document.getElementById('uploadText');

        let multipleMode = false;
        
        function toggleMultiple() {
            multipleMode = document.getElementById('multipleFiles').checked;
            updateFileInputs();
        }
        
        function updateFileInputs() {
            if (currentMode === 'audio') {
                if (multipleMode) {
                    audioInput.style.display = 'none';
                    document.getElementById('audioFiles').style.display = 'block';
                    audioInput.required = false;
                    document.getElementById('audioFiles').required = true;
                } else {
                    audioInput.style.display = 'block';
                    document.getElementById('audioFiles').style.display = 'none';
                    audioInput.required = true;
                    document.getElementById('audioFiles').required = false;
                }
            } else {
                if (multipleMode) {
                    txtInput.style.display = 'none';
                    document.getElementById('txtFiles').style.display = 'block';
                    txtInput.required = false;
                    document.getElementById('txtFiles').required = true;
                } else {
                    txtInput.style.display = 'block';
                    document.getElementById('txtFiles').style.display = 'none';
                    txtInput.required = true;
                    document.getElementById('txtFiles').required = false;
                }
            }
        }
        
        function switchMode(mode) {
            currentMode = mode;
            if (mode === 'audio') {
                document.getElementById('btnAudio').style.background = '#667eea';
                document.getElementById('btnTxt').style.background = '#ccc';
                uploadText.textContent = '📁 Kéo thả file audio vào đây';
            } else {
                document.getElementById('btnAudio').style.background = '#ccc';
                document.getElementById('btnTxt').style.background = '#667eea';
                uploadText.textContent = '📄 Kéo thả file TXT vào đây';
            }
            updateFileInputs();
        }

        uploadArea.addEventListener('click', () => {
            if (currentMode === 'audio') {
                if (multipleMode) {
                    document.getElementById('audioFiles').click();
                } else {
                    audioInput.click();
                }
            } else {
                if (multipleMode) {
                    document.getElementById('txtFiles').click();
                } else {
                    txtInput.click();
                }
            }
        });
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                if (currentMode === 'audio') {
                    if (multipleMode) {
                        document.getElementById('audioFiles').files = files;
                    } else {
                        audioInput.files = files;
                    }
                } else {
                    if (multipleMode) {
                        document.getElementById('txtFiles').files = files;
                    } else {
                        txtInput.files = files;
                    }
                }
                const fileCount = files.length;
                showStatus(`Đã chọn ${fileCount} file${fileCount > 1 ? 's' : ''}: ${files[0].name}${fileCount > 1 ? '...' : ''}`, 'success');
            }
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Đang xử lý...';
            showStatus('Đang tạo QR code...', 'success');

            try {
                let endpoint, response, data;
                
                if (multipleMode) {
                    endpoint = '/api/batch-upload';
                    response = await fetch(endpoint, {
                        method: 'POST',
                        body: formData
                    });
                    data = await response.json();
                    
                    if (response.ok) {
                        const count = data.count || 0;
                        showStatus(`Đã tạo thành công ${count} QR code${count > 1 ? 's' : ''}!`, 'success');
                        setTimeout(() => {
                            window.location.href = '/manage';
                        }, 2000);
                    } else {
                        showStatus('Lỗi: ' + (data.error || 'Unknown error'), 'error');
                    }
                } else {
                    endpoint = currentMode === 'audio' ? '/upload' : '/txt-to-qr';
                    response = await fetch(endpoint, {
                        method: 'POST',
                        body: formData
                    });
                    data = await response.json();
                    
                    if (response.ok) {
                        showStatus('Tạo QR code thành công!', 'success');
                        displayQR(data.qr_code, data.audio_url, data.audio_path);
                    } else {
                        showStatus('Lỗi: ' + data.error, 'error');
                    }
                }
            } catch (error) {
                showStatus('Lỗi: ' + error.message, 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Tạo QR Code';
            }
        });

        function showStatus(message, type) {
            status.textContent = message;
            status.className = 'status ' + type;
        }

        function displayQR(qrBase64, audioUrl, audioPath) {
            qrContainer.classList.add('active');
            document.getElementById('qrCode').innerHTML = 
                '<img src="data:image/png;base64,' + qrBase64 + '" alt="QR Code">';
            
            const fullUrl = window.location.origin + audioUrl;
            document.getElementById('audioLink').innerHTML = 
                '<strong>Link audio:</strong><br><a href="' + fullUrl + '" target="_blank">' + fullUrl + '</a>';
            
            document.getElementById('audioPreview').innerHTML = 
                '<audio controls><source src="' + audioUrl + '" type="audio/mpeg">Trình duyệt không hỗ trợ audio.</audio>';
            
            window.qrImageBase64 = qrBase64;
        }

        function downloadQR() {
            if (window.qrImageBase64) {
                const link = document.createElement('a');
                link.href = 'data:image/png;base64,' + window.qrImageBase64;
                link.download = 'qrcode.png';
                link.click();
            }
        }
    </script>
</body>
</html>
"""


# HTML template cho trang quản lý
MANAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quản Lý QR Codes</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }
        .header-actions {
            text-align: center;
            margin-bottom: 30px;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
            text-decoration: none;
            display: inline-block;
        }
        .qr-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .qr-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .qr-card h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
        }
        .qr-card img {
            max-width: 200px;
            height: auto;
            margin: 10px 0;
        }
        .qr-card audio {
            width: 100%;
            margin: 10px 0;
        }
        .qr-card .actions {
            margin-top: 15px;
        }
        .btn-small {
            padding: 8px 15px;
            font-size: 14px;
            margin: 5px;
        }
        .btn-danger {
            background: #dc3545;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Quản Lý QR Codes</h1>
        <div class="header-actions">
            <a href="/" class="btn">➕ Tạo QR Code Mới</a>
            <button class="btn" onclick="location.reload()">🔄 Làm Mới</button>
        </div>
        <div class="qr-grid" id="qrGrid">
            <div class="empty-state">
                <p>Chưa có QR code nào. <a href="/">Tạo QR code mới</a></p>
            </div>
        </div>
    </div>
    <script>
        async function loadQRList() {
            const response = await fetch('/api/qr-list');
            const data = await response.json();
            const grid = document.getElementById('qrGrid');
            
            if (data.length === 0) {
                grid.innerHTML = '<div class="empty-state"><p>Chưa có QR code nào. <a href="/">Tạo QR code mới</a></p></div>';
                return;
            }
            
            grid.innerHTML = data.map(item => `
                <div class="qr-card">
                    <h3>${escapeHtml(item.title)}</h3>
                    <img src="data:image/png;base64,${item.qr_base64}" alt="QR Code">
                    <audio controls><source src="${item.audio_url}" type="audio/mpeg"></audio>
                    <div class="actions">
                        <a href="${item.audio_url}" target="_blank" class="btn btn-small">🔗 Link</a>
                        <a href="/qr-download/${item.id}" class="btn btn-small" download>⬇️ Tải QR (Chất lượng cao)</a>
                        <button class="btn btn-small" onclick="downloadQR('${item.qr_base64}', '${escapeHtml(item.title)}')">⬇️ Tải QR (Nhanh)</button>
                        <button class="btn btn-small btn-danger" onclick="deleteQR('${item.id}')">🗑️ Xóa</button>
                    </div>
                </div>
            `).join('');
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function downloadQR(base64, title) {
            const link = document.createElement('a');
            link.href = 'data:image/png;base64,' + base64;
            link.download = title.replace(/[^a-z0-9]/gi, '_') + '.png';
            link.click();
        }
        
        async function deleteQR(id) {
            if (!confirm('Bạn có chắc muốn xóa QR code này?')) return;
            
            const response = await fetch(`/api/qr-delete/${id}`, { method: 'DELETE' });
            if (response.ok) {
                loadQRList();
            } else {
                alert('Lỗi khi xóa');
            }
        }
        
        loadQRList();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Trang chủ"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/manage')
def manage():
    """Trang quản lý QR codes"""
    return render_template_string(MANAGE_TEMPLATE)


@app.route('/upload', methods=['POST'])
def upload_audio():
    """Upload audio file và generate QR code"""
    if 'audio' not in request.files:
        return jsonify({'error': 'Khong co file audio'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'Khong co file duoc chon'}), 400
    
    if file:
        # Lưu file với tên unique
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_ext = Path(filename).suffix
        saved_filename = f"{file_id}{file_ext}"
        file_path = Path(app.config['UPLOAD_FOLDER']) / saved_filename
        
        file.save(file_path)
        
        # Tạo URL cho audio
        audio_url = f'/audio/{saved_filename}'
        full_url = request.url_root.rstrip('/') + audio_url
        
        # Generate QR code với chất lượng cao để in (High error correction)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction cho in
            box_size=10,
            border=4,
        )
        qr.add_data(full_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR code to base64 (chất lượng cao)
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG', optimize=False)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Lưu vào database
        title = request.form.get('title', filename)
        add_qr_record(saved_filename, audio_url, full_url, img_str, title)
        
        return jsonify({
            'qr_code': img_str,
            'audio_url': audio_url,
            'audio_path': saved_filename,
            'full_url': full_url
        })


@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve audio file từ uploads hoặc audio_stories"""
    # Thử tìm trong uploads folder trước
    file_path = Path(app.config['UPLOAD_FOLDER']) / filename
    if not file_path.exists():
        # Thử tìm trong audio_stories folder
        file_path = Path('audio_stories') / filename
    
    if not file_path.exists():
        return jsonify({'error': 'File khong ton tai'}), 404
    
    return send_file(file_path, mimetype='audio/mpeg')


@app.route('/txt-to-qr', methods=['POST'])
def txt_to_qr():
    """
    Upload TXT file -> Convert to Audio -> Generate QR Code
    """
    if 'txt_file' not in request.files:
        return jsonify({'error': 'Khong co file TXT'}), 400
    
    file = request.files['txt_file']
    if file.filename == '':
        return jsonify({'error': 'Khong co file duoc chon'}), 400
    
    # Lấy tham số
    voice = request.form.get('voice', 'vi-VN-HoaiMyNeural')
    format_type = request.form.get('format', 'mp3')
    
    try:
        # Lưu file TXT tạm
        filename = secure_filename(file.filename)
        temp_dir = Path('temp')
        temp_dir.mkdir(exist_ok=True)
        
        file_id = str(uuid.uuid4())
        temp_txt = temp_dir / f"{file_id}.txt"
        file.save(temp_txt)
        
        # Convert TXT to Audio
        audio_path = convert_txt_to_audio(
            str(temp_txt),
            output_path=None,
            voice=voice,
            format=format_type
        )
        
        # Di chuyển audio file vào uploads folder
        audio_filename = Path(audio_path).name
        final_audio_path = Path(app.config['UPLOAD_FOLDER']) / audio_filename
        Path(audio_path).rename(final_audio_path)
        
        # Tạo URL cho audio
        audio_url = f'/audio/{audio_filename}'
        full_url = request.url_root.rstrip('/') + audio_url
        
        # Generate QR code với chất lượng cao để in (High error correction)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction cho in
            box_size=10,
            border=4,
        )
        qr.add_data(full_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR code to base64 (chất lượng cao)
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG', optimize=False)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Lưu vào database
        title = request.form.get('title', filename)
        add_qr_record(audio_filename, audio_url, full_url, img_str, title)
        
        # Xóa file TXT tạm
        temp_txt.unlink()
        
        return jsonify({
            'qr_code': img_str,
            'audio_url': audio_url,
            'audio_path': audio_filename,
            'full_url': full_url,
            'message': 'Convert thanh cong'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/qr-list')
def qr_list():
    """API: Lấy danh sách tất cả QR codes"""
    data = load_qr_data()
    # Sắp xếp theo thời gian tạo mới nhất
    data.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(data)

@app.route('/api/qr-delete/<qr_id>', methods=['DELETE'])
def qr_delete(qr_id):
    """API: Xóa QR code"""
    data = load_qr_data()
    data = [item for item in data if item['id'] != qr_id]
    save_qr_data(data)
    return jsonify({'status': 'ok'})

@app.route('/qr-download/<qr_id>')
def qr_download(qr_id):
    """Download QR code với chất lượng cao để in"""
    data = load_qr_data()
    qr_item = next((item for item in data if item['id'] == qr_id), None)
    
    if not qr_item:
        return jsonify({'error': 'QR code khong ton tai'}), 404
    
    # Tạo QR code với kích thước lớn hơn để in
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,  # Kích thước lớn hơn để in
        border=4,
    )
    qr.add_data(qr_item['full_url'])
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG', optimize=False)
    img_buffer.seek(0)
    
    filename = secure_filename(qr_item['title']) + '_qrcode.png'
    return send_file(img_buffer, mimetype='image/png', as_attachment=True, download_name=filename)

@app.route('/api/batch-upload', methods=['POST'])
def batch_upload():
    """API: Upload nhiều file cùng lúc"""
    results = []
    
    # Xử lý upload audio
    if 'audio_files' in request.files:
        files = request.files.getlist('audio_files')
        for file in files:
            if file.filename:
                try:
                    filename = secure_filename(file.filename)
                    file_id = str(uuid.uuid4())
                    file_ext = Path(filename).suffix
                    saved_filename = f"{file_id}{file_ext}"
                    file_path = Path(app.config['UPLOAD_FOLDER']) / saved_filename
                    file.save(file_path)
                    
                    audio_url = f'/audio/{saved_filename}'
                    full_url = request.url_root.rstrip('/') + audio_url
                    
                    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
                    qr.add_data(full_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    img_buffer = BytesIO()
                    img.save(img_buffer, format='PNG', optimize=False)
                    img_str = base64.b64encode(img_buffer.getvalue()).decode()
                    
                    title = request.form.get('title', filename)
                    record = add_qr_record(saved_filename, audio_url, full_url, img_str, title)
                    results.append(record)
                except Exception as e:
                    results.append({'error': str(e), 'filename': file.filename})
    
    # Xử lý upload TXT
    if 'txt_files' in request.files:
        files = request.files.getlist('txt_files')
        voice = request.form.get('voice', 'vi-VN-HoaiMyNeural')
        format_type = request.form.get('format', 'mp3')
        
        for file in files:
            if file.filename:
                try:
                    filename = secure_filename(file.filename)
                    temp_dir = Path('temp')
                    file_id = str(uuid.uuid4())
                    temp_txt = temp_dir / f"{file_id}.txt"
                    file.save(temp_txt)
                    
                    audio_path = convert_txt_to_audio(str(temp_txt), output_path=None, voice=voice, format=format_type)
                    audio_filename = Path(audio_path).name
                    final_audio_path = Path(app.config['UPLOAD_FOLDER']) / audio_filename
                    Path(audio_path).rename(final_audio_path)
                    
                    audio_url = f'/audio/{audio_filename}'
                    full_url = request.url_root.rstrip('/') + audio_url
                    
                    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
                    qr.add_data(full_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    img_buffer = BytesIO()
                    img.save(img_buffer, format='PNG', optimize=False)
                    img_str = base64.b64encode(img_buffer.getvalue()).decode()
                    
                    title = request.form.get('title', filename)
                    record = add_qr_record(audio_filename, audio_url, full_url, img_str, title)
                    results.append(record)
                    
                    temp_txt.unlink()
                except Exception as e:
                    results.append({'error': str(e), 'filename': file.filename})
    
    return jsonify({'results': results, 'count': len(results)})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    # Lấy port từ environment variable hoặc dùng 5000
    port = int(os.environ.get('PORT', 5000))
    # Chạy trên tất cả interfaces để có thể access từ network
    app.run(host='0.0.0.0', port=port, debug=False)

