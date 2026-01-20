# Hướng Dẫn Sử Dụng QR Code

## ✅ Có thể in QR code và dùng ở nhiều nơi

**Câu trả lời: CÓ!** Khi bạn deploy lên server, mỗi QR code sẽ có một **URL duy nhất** trỏ đến file audio trên server. 

### Cách hoạt động:

1. **Tạo QR code** → Hệ thống tạo URL duy nhất (ví dụ: `https://your-server.com/audio/abc123.mp3`)
2. **In QR code** → In QR code ra giấy, poster, banner, v.v.
3. **Quét QR code** → Bất kỳ ai quét QR code đó ở bất kỳ đâu (có internet) đều có thể:
   - Tự động mở trình duyệt
   - Truy cập URL audio
   - Nghe audio ngay lập tức

### Lưu ý quan trọng:

✅ **QR code hoạt động ở mọi nơi** - Chỉ cần có internet và camera để quét
✅ **URL không thay đổi** - Một khi tạo, URL sẽ luôn trỏ đến file audio đó
✅ **Có thể in nhiều bản** - In nhiều QR code giống nhau, tất cả đều hoạt động
✅ **Chất lượng cao** - QR code được tạo với error correction cao, quét được ngay cả khi in mờ

### Cách in QR code:

1. **Tải QR code chất lượng cao:**
   - Vào trang **Quản Lý QR Codes** (`/manage`)
   - Click **"Tải QR (Chất lượng cao)"** cho từng QR code
   - File PNG sẽ được tải về với kích thước lớn, phù hợp để in

2. **In QR code:**
   - Mở file PNG đã tải
   - In với kích thước tối thiểu **5x5 cm** (hoặc lớn hơn)
   - Đảm bảo độ phân giải in đủ cao (300 DPI trở lên)

3. **Test trước khi in:**
   - Quét QR code trên màn hình để đảm bảo hoạt động
   - Kiểm tra URL có đúng không

### Ví dụ sử dụng:

- 📄 **In trên tài liệu** - Thêm QR code vào sách, tài liệu
- 🎨 **Poster/Banner** - In QR code trên poster quảng cáo
- 🏷️ **Nhãn sản phẩm** - Dán QR code lên sản phẩm
- 📱 **Business card** - In QR code trên danh thiếp
- 🎓 **Giáo dục** - In QR code trên bài giảng, sách giáo khoa

### Yêu cầu kỹ thuật:

- **Server phải online 24/7** - Để QR code luôn hoạt động
- **Domain/IP cố định** - URL không được thay đổi
- **SSL/HTTPS** - Nên dùng HTTPS để an toàn hơn
- **Backup files** - Đảm bảo file audio không bị mất

### Troubleshooting:

❌ **QR code không quét được:**
- Kiểm tra kích thước in (phải đủ lớn)
- Kiểm tra độ tương phản (đen trắng rõ ràng)
- Thử quét với app khác

❌ **Quét được nhưng không mở được:**
- Kiểm tra server có online không
- Kiểm tra URL có đúng không
- Kiểm tra file audio có còn tồn tại không

