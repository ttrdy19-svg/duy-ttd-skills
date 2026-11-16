"""Xoá logo ngôi sao ✦ (Gemini ảnh / Veo video) bằng trừ ngược alpha.

Logo là hình sao trắng bán trong suốt dán lên ảnh:  quan_sat = k*a*255 + (1 - k*a) * nen
  a  = hình sao (mặt nạ 0..1, lấy từ py-gemini-watermark-remover, MIT — xem mat-na/LICENSE-*)
  k  = độ đậm của logo (đo trên chính ảnh/clip)
=> nen = (quan_sat - k*a*255) / (1 - k*a)

Các bước: TÌM logo quanh vị trí đã đo -> ƯỚC k (vá nền + bình phương tối thiểu) -> CHỈNH k tới khi tương quan còn lại với
hình sao ≈ 0 -> KHỬ -> DÒ LẠI (so với nhiễu nền ở chỗ khác). Còn thấy thì báo, không trả kết quả.
"""
from pathlib import Path
import cv2
import numpy as np

MAT_NA = Path(__file__).resolve().parent / 'mat-na'

# Vị trí đo trên file thật (11/2026): cỡ khung -> (cỡ logo px, cách mép phải/dưới px).
#  - Ảnh Gemini web 1376x768: logo ~44–48 px, cách mép ~97 px; ảnh Google Flow (Nano Banana, bản 1K) cùng cỡ nhưng cách mép ~76 px.
#  - Video Veo 1280x720: logo ~48 px, cách mép 96 px (tâm 1160,600). Khung 16:9 cỡ khác: co giãn theo bề ngang.
VI_TRI_ANH = {(1376, 768): [(48, 97), (46, 76)]}
VEO_GOC = (48, 96, 1280)


def mat_na(co):
    """Alpha (0..1) hình sao cỡ co px, chuẩn hoá đỉnh = 1."""
    goc = cv2.imread(str(MAT_NA / ('bg_96.png' if co > 60 else 'bg_48.png')), cv2.IMREAD_COLOR).astype(np.float32)
    a = cv2.resize(goc.max(axis=2) / 255.0, (co, co), interpolation=cv2.INTER_AREA)
    return a / max(float(a.max()), 1e-6)


def sang_hon_nen(img):
    xam = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    return xam - cv2.GaussianBlur(xam, (0, 0), 6)


def vi_tri_mac_dinh(W, H, video=False):
    """Danh sách (x0, y0, co0, ti_le) các vị trí đã đo cho cỡ khung này; rỗng nếu chưa đo."""
    if not video:
        return [(W - le - co0, H - le - co0, co0, 1.0) for co0, le in VI_TRI_ANH.get((W, H), [])]
    if abs(W / H - 16 / 9) > 0.03:
        return []
    s = W / VEO_GOC[2]
    co0, le = round(VEO_GOC[0] * s), round(VEO_GOC[1] * s)
    return [(W - le - co0, H - le - co0, co0, s)]


def tim(img, x0, y0, co0, s=1.0):
    """Khớp hình sao trong cửa sổ ±14 px (×s), cỡ 44–56 (×s). Trả (điểm, x, y, cỡ)."""
    hp = sang_hon_nen(img)
    bien, tot = round(14 * s), (-1.0, x0, y0, co0)
    for co in sorted({round(c * s) for c in range(44, 57, 2)}):
        ya, xa = max(0, y0 - bien), max(0, x0 - bien)
        o = hp[ya:y0 + co0 + bien, xa:x0 + co0 + bien]
        if o.shape[0] <= co or o.shape[1] <= co:
            continue
        _, m, _, p = cv2.minMaxLoc(cv2.matchTemplate(o, mat_na(co), cv2.TM_CCOEFF_NORMED))
        if m > tot[0]:
            tot = (float(m), xa + p[0], ya + p[1], co)
    return tot


def nguong_nen(imgs, co):
    """Mức nhiễu nền: điểm khớp hình sao cao nhất (phân vị 99,5) ở nửa trên khung — nơi không có logo."""
    v = [float(np.percentile(cv2.matchTemplate(sang_hon_nen(i)[: i.shape[0] // 2], mat_na(co), cv2.TM_CCOEFF_NORMED), 99.5)) for i in imgs]
    return max(float(np.median(v)), 0.3)


def tuong_quan(img, x, y, co):
    """Tương quan CÓ DẤU giữa phần nét của ô logo và hình sao, đúng chỗ. >0 còn sao, ≈0 sạch, <0 trừ lố."""
    pad = 24
    y1, x1 = max(0, y - pad), max(0, x - pad)
    hp = sang_hon_nen(img[y1:y + co + pad, x1:x + co + pad])[y - y1:y - y1 + co, x - x1:x - x1 + co]
    m = mat_na(co)
    a, b = hp - hp.mean(), m - m.mean()
    return float((a * b).sum() / max(np.sqrt((a * a).sum() * (b * b).sum()), 1e-6))


def khu(img, x, y, co, k):
    ak = np.clip(k * mat_na(co), 0, 0.95)[..., None]
    vung = img[y:y + co, x:x + co].astype(np.float32)
    img[y:y + co, x:x + co] = np.clip((vung - ak * 255.0) / (1.0 - ak), 0, 255).astype(np.uint8)
    return img


def uoc_k(imgs, x, y, co):
    """k ban đầu: vá (inpaint) vùng logo làm nền, bình phương tối thiểu gộp mọi ảnh mẫu."""
    a = mat_na(co)[..., None]
    chon = np.repeat(a[..., 0].ravel() > 0.05, 3)
    m = (a[..., 0] > 0.05).astype(np.uint8) * 255
    tu = mau = 0.0
    for img in imgs:
        pad = round(co / 4)
        y1, x1 = max(0, y - pad), max(0, x - pad)
        lon = img[y1:y + co + pad, x1:x + co + pad]
        ml = np.zeros(lon.shape[:2], np.uint8); ml[y - y1:y - y1 + co, x - x1:x - x1 + co] = m
        nen = cv2.inpaint(lon, cv2.dilate(ml, np.ones((3, 3), np.uint8)), 5, cv2.INPAINT_TELEA).astype(np.float32)[y - y1:y - y1 + co, x - x1:x - x1 + co]
        A = (a * (255.0 - nen)).ravel()[chon]; B = (img[y:y + co, x:x + co].astype(np.float32) - nen).ravel()[chon]
        tu += float((A * B).sum()); mau += float((A * A).sum())
    return float(np.clip(tu / max(mau, 1e-6), 0.0, 0.95))


def chinh_k(imgs, x, y, co, k0):
    """Nền vá lệch theo cảnh -> chọn k (0,6–1,6 × k0) để tương quan còn lại với hình sao gần 0 nhất."""
    ks = np.linspace(max(0.05, 0.6 * k0), min(0.95, 1.6 * k0), 41)
    d = [abs(float(np.median([tuong_quan(khu(i.copy(), x, y, co, k), x, y, co) for i in imgs]))) for k in ks]
    return float(ks[int(np.argmin(d))])


def do_logo(imgs, video=False):
    """Đo trên 1 ảnh hoặc nhiều khung mẫu cùng cỡ. Trả dict: coLogo, conLogo (sau khử thử), x, y, co, k, điểm."""
    H, W = imgs[0].shape[:2]
    ds = vi_tri_mac_dinh(W, H, video)
    if not ds:
        return {'loi': f'co {W}x{H} chua do vi tri logo', 'coLogo': None}
    # nhiều vị trí đã đo (Gemini / Flow cùng cỡ) -> lấy vị trí khớp tốt nhất trên ảnh đầu
    x0, y0, co0, s = max(ds, key=lambda v: tim(imgs[0], *v)[0])
    kq = [tim(i, x0, y0, co0, s) for i in imgs]
    truoc, x, y, co = float(np.median([r[0] for r in kq])), *max(kq, key=lambda r: r[0])[1:]
    ng = nguong_nen(imgs, co)
    out = {'kichThuoc': f'{W}x{H}', 'logo': [int(x), int(y), int(co)], 'diemTruoc': round(truoc, 3), 'nguong': round(ng, 3)}
    if truoc <= ng:
        return {**out, 'coLogo': False, 'conLogo': False}
    k = chinh_k(imgs, x, y, co, uoc_k(imgs, x, y, co))
    sach = [khu(i.copy(), x, y, co, k) for i in imgs]
    sau = float(np.median([tim(i, x0, y0, co0, s)[0] for i in sach]))
    tq = float(np.median([tuong_quan(i, x, y, co) for i in sach]))
    con = sau > ng and tq > 0.15   # nền nhiều vân: điểm dò chạm nhiễu nền dù sao đã hết -> cần cả hai cùng báo
    return {**out, 'coLogo': True, 'conLogo': bool(con), 'k': round(k, 3), 'x': int(x), 'y': int(y), 'co': int(co),
            'diemSau': round(sau, 3), 'tqSau': round(tq, 3)}
