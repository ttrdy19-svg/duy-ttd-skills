"""Xoá logo ✦ ở góc dưới phải ảnh Gemini (bản tải "kích thước đầy đủ", 1376x768).
python xoa_logo_anh.py <ảnh vào> <ảnh ra>
In JSON; mã 0 = đã xoá hoặc không có logo (không có thì vẫn chép ảnh), 2 = còn logo / cỡ ảnh chưa đo (không ghi ảnh ra), 1 = lỗi đọc.
"""
import json, shutil, sys
from pathlib import Path
import cv2
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import logo_sao as L


# cv2.imread/imwrite trên Windows không mở được đường dẫn có dấu (vd thư mục "Ảnh mẫu") -> đọc/ghi qua numpy.
def doc_anh(f):
    try:
        return cv2.imdecode(np.fromfile(f, np.uint8), cv2.IMREAD_COLOR)
    except OSError:
        return None


def ghi_anh(f, img):
    duoi = '.png' if f.lower().endswith('.png') else '.jpg'
    ok, buf = cv2.imencode(duoi, img, [cv2.IMWRITE_PNG_COMPRESSION, 3] if duoi == '.png' else [cv2.IMWRITE_JPEG_QUALITY, 95])
    if ok:
        buf.tofile(f)
    return ok


def main():
    vao, ra = sys.argv[1], sys.argv[2]
    img = doc_anh(vao)
    if img is None:
        print(json.dumps({'loi': 'khong doc duoc anh'})); sys.exit(1)
    kq = L.do_logo([img])
    if kq.get('coLogo') is None or kq.get('conLogo'):
        print(json.dumps({**kq, 'conLogo': True})); sys.exit(2)
    if not kq['coLogo']:
        shutil.copyfile(vao, ra); print(json.dumps(kq)); sys.exit(0)
    img = L.khu(img, kq['x'], kq['y'], kq['co'], kq['k'])
    if not ghi_anh(ra, img):
        print(json.dumps({'loi': 'khong ghi duoc anh'})); sys.exit(1)
    print(json.dumps(kq)); sys.exit(0)


if __name__ == '__main__':
    main()
