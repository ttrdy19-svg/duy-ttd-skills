---
name: ngu-anh
description: Dùng trình duyệt Ngư Ảnh (headless Rust + V8, nói CDP) thay Chrome headless cho Playwright/Puppeteer khi cần mở nhiều phiên web nhẹ RAM — tạo video trên web AI, đọc trang, tải file lên. Biết các chỗ đã vá (WebSocket thật, tải file, gõ contenteditable, blob:) và các trang còn phải để Chrome thật.
---

# Ngư Ảnh — trình duyệt nhẹ cho tự động hoá

Mã nguồn: https://github.com/ttrdy19-svg/ngu-anh (bản sửa đổi của Obscura, Apache-2.0).

## Khi nào dùng

- Cần chạy **nhiều phiên web cùng lúc** trên một máy (mỗi phiên Chrome ăn vài trăm MB RAM; Ngư Ảnh ít hơn nhiều).
- Trang dùng JS hiện đại bình thường: chat, tạo ảnh/video, tải file lên, đọc kết quả.

## Khi nào KHÔNG dùng (để Chrome / trình duyệt thật)

Đo 11/2026: trang dựng canvas/WebGL nặng, cần `DecompressionStream` / `CompressionStream`, Navigation API,
`ViewTransition`… còn thiếu → ví dụ ChatGPT vẽ ảnh, Muse, đếm tín dụng Dreamina vẫn chạy trên trình duyệt thật.
Đăng nhập Google mới (mật khẩu) cũng làm trên trình duyệt thật, rồi **chép cookie** sang Ngư Ảnh.

## Dựng và chạy

```bash
git clone https://github.com/ttrdy19-svg/ngu-anh && cd ngu-anh
cargo build --release -p obscura-cli --bins --features render
./target/release/obscura serve --port 9222        # xem README-OBSCURA.md cho đủ tham số
```

Nối Playwright:

```js
const { chromium } = require('playwright');
const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
const ctx = browser.contexts()[0] || await browser.newContext();
await ctx.addCookies(cookiesTuTrinhDuyetThat);   // phiên đăng nhập chép sang
const page = await ctx.newPage();
await page.goto('https://example.com');
```

## Chỗ đã vá so với Obscura (đừng viết lại vòng tránh)

- **WebSocket thật** — trang chat nhận được tin trả lời.
- **Tải file lên**: `input.files` gán được, `DataTransfer` có thật → `setInputFiles` / gán file qua JS chạy.
- **Gõ chữ** vào ô `contenteditable` (ProseMirror, Quill): `Input.insertText`, `document.execCommand('insertText')`.
- **blob:** giữ đúng byte, `fetch(blob:)` đọc được, `<img src=blob:>` hiện → tải ảnh/video kết quả về được.
- `Runtime.evaluate` + `awaitPromise` không bị cắt 30–60 s → chờ việc dài trong trang được.
- `importScripts` trong Worker, `MessagePort` xuyên khung (reCAPTCHA), `canPlayType` như Chrome.

## Mẹo

- Khung nhỏ (≈ 820 px ngang) cho vài trang (Google Flow) hiện đúng trình biên tập; khung rộng có thể treo.
- Mỗi tài khoản một context riêng; đóng trang xong thì đóng context để trả RAM.
- Lỗi lạ: thử cùng trang trên Chrome thật trước khi kết luận trang hỏng — thường là thiếu một API trình duyệt.
