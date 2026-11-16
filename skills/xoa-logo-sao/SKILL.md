---
name: xoa-logo-sao
description: Xoá logo ngôi sao ✦ ở góc dưới phải ảnh Gemini và video Veo (Google Flow) bằng trừ ngược alpha — đo vị trí và độ đậm trên chính file, dò lại tới khi không còn thấy. Dùng khi cần ảnh/clip Gemini–Veo sạch logo cho MV, thumbnail.
---

# Xoá logo sao ✦ (Gemini ảnh · Veo video)

Logo của Gemini và Veo là cùng một hình sao trắng bán trong suốt dán ở góc dưới phải. Vì là lớp phủ bán trong suốt
(không phải vẽ đè đặc), có thể **trừ ngược** để lấy lại điểm ảnh gốc thay vì làm nhoè:

```
quan_sat = k·a·255 + (1 − k·a)·nen   →   nen = (quan_sat − k·a·255) / (1 − k·a)
```

`a` là hình sao (mặt nạ trong `scripts/mat-na/`, MIT), `k` là độ đậm đo trên chính file.

## Cách dùng

Cần Python 3.10+ với `opencv-python` và `numpy`; video cần thêm `ffmpeg`.

```bash
pip install opencv-python numpy
# ảnh Gemini (bản tải "kích thước đầy đủ" 1376×768 — bản xem trên trang chỉ 1024 px, logo bị thu nhỏ)
python scripts/xoa_logo_anh.py vao.png ra.png
# video Veo 720p (hoặc 16:9 cỡ khác — tự co giãn theo bề ngang)
python scripts/xoa_logo_video.py vao.mp4 ra.mp4 --ffmpeg /duong/dan/ffmpeg
python scripts/xoa_logo_video.py vao.mp4 bo-qua.mp4 --chi-do   # chỉ đo, không ghi
```

Kết quả in một dòng JSON: `coLogo`, `conLogo`, `logo` [x, y, cỡ], `k` (độ đậm), `diemTruoc` / `diemSau` (khớp hình sao),
`tqSau` (tương quan còn lại ngay chỗ sao, ≈ 0 là sạch). Mã thoát: `0` xong hoặc không có logo, `2` còn logo hoặc cỡ khung
chưa đo (không ghi file ra), `1` lỗi đọc.

## Cách làm (để sửa khi Google đổi logo)

1. **Tìm** quanh vị trí đã đo (`VI_TRI_ANH`, `VEO_GOC` trong `logo_sao.py`), cửa sổ ±14 px, cỡ 44–56 px.
   Đo 11/2026: ảnh Gemini 1376×768 → logo ~48 px cách mép phải/dưới ~97 px; Veo 1280×720 → 48 px, cách mép 96 px.
2. **Ước k** bằng vá nền (inpaint) + bình phương tối thiểu; nền vá lệch theo cảnh nên **chỉnh k** trong 0,6–1,6× tới khi
   tương quan còn lại với hình sao gần 0 nhất.
3. **Khử**, rồi **dò lại**: so điểm khớp với nhiễu nền ở nửa trên khung. "Còn logo" chỉ khi cả điểm dò vượt nhiễu nền
   *và* tương quan đúng chỗ > 0,15 (nền nhiều vân làm điểm dò chạm nhiễu dù sao đã hết).
4. Video: logo đứng yên → đo một lần trên 20 khung, khử từng khung qua đường ống ffmpeg, giữ fps và tiếng.

## Lưu ý

- **Xoá ở độ phân giải gốc, trước khi nâng nét.** Clip đã nâng (RelayVSR, Topaz…) có viền logo sắc hơn hình mẫu — trừ xong còn hằn viền.
- Cỡ ảnh lạ → báo `chua do vi tri logo`, không đoán. Đo vị trí mới rồi thêm vào bảng.
- Chỉ dùng cho nội dung bạn có quyền dùng; logo AI không phải dấu bản quyền, nhưng điều khoản dịch vụ từng nơi khác nhau.
