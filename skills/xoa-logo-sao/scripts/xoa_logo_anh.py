"""Xoá logo ✦ ở góc dưới phải ảnh Gemini (bản tải "kích thước đầy đủ", 1376x768).
python xoa_logo_anh.py <ảnh vào> <ảnh ra>
In JSON; mã 0 = đã xoá hoặc không có logo (không có thì vẫn chép ảnh), 2 = còn logo / cỡ ảnh chưa đo (không ghi ảnh ra), 1 = lỗi đọc.
"""
import json, shutil, sys
from pathlib import Path
import cv2
sys.path.insert(0, str(Path(__file__).resolve().parent))
import logo_sao as L


def main():
    vao, ra = sys.argv[1], sys.argv[2]
    img = cv2.imread(vao, cv2.IMREAD_COLOR)
    if img is None:
        print(json.dumps({'loi': 'khong doc duoc anh'})); sys.exit(1)
    kq = L.do_logo([img])
    if kq.get('coLogo') is None or kq.get('conLogo'):
        print(json.dumps({**kq, 'conLogo': True})); sys.exit(2)
    if not kq['coLogo']:
        shutil.copyfile(vao, ra); print(json.dumps(kq)); sys.exit(0)
    img = L.khu(img, kq['x'], kq['y'], kq['co'], kq['k'])
    cv2.imwrite(ra, img, [cv2.IMWRITE_PNG_COMPRESSION, 3] if ra.lower().endswith('.png') else [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(json.dumps(kq)); sys.exit(0)


if __name__ == '__main__':
    main()
