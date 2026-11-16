# Bộ skill Duy TTD

Các skill rời của Duy TTD Studio — mỗi thư mục trong `skills/` là một skill độc lập (theo chuẩn Agent Skills: `SKILL.md`
có `name` + `description`, kèm script), dùng được với Claude Code hoặc đọc tay. Cập nhật dần.

| Skill | Làm gì |
|---|---|
| [`xoa-logo-sao`](skills/xoa-logo-sao/SKILL.md) | Xoá logo ngôi sao ✦ trên ảnh Gemini và video Veo bằng trừ ngược alpha, dò lại tới khi không còn thấy. |
| [`ngu-anh`](skills/ngu-anh/SKILL.md) | Dùng trình duyệt nhẹ Ngư Ảnh (Rust + V8, CDP) cho Playwright/Puppeteer khi cần nhiều phiên web. |

## Cài vào Claude Code

```bash
git clone https://github.com/ttrdy19-svg/duy-ttd-skills
# chép skill cần dùng vào .claude/skills/ của dự án (hoặc ~/.claude/skills/)
cp -r duy-ttd-skills/skills/xoa-logo-sao .claude/skills/
```

## Giấy phép

Mã của bộ skill: MIT (`LICENSE`). Mặt nạ hình sao trong `skills/xoa-logo-sao/scripts/mat-na/` lấy từ
[py-gemini-watermark-remover](https://github.com/daniel-style/py-gemini-watermark-remover) (MIT, giấy phép đi kèm thư mục đó).
Ngư Ảnh là bản sửa đổi của Obscura (Apache-2.0), mã ở repo riêng.

---

**English.** Standalone agent skills from Duy TTD Studio: `xoa-logo-sao` removes the ✦ star watermark from Gemini images
and Veo videos by reverse alpha blending (measured position + opacity, re-checked until invisible); `ngu-anh` explains how to
drive the Ngư Ảnh lightweight headless browser (a patched Obscura fork) with Playwright. MIT licensed.
