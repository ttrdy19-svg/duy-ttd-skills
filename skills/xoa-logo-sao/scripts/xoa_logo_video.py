"""Xoá logo ✦ ở góc dưới phải clip Veo (Flow). Logo đứng yên -> đo một lần trên 20 khung, rồi khử từng khung qua ffmpeg.
python xoa_logo_video.py <clip vào> <clip ra> [--ffmpeg <đường dẫn ffmpeg>] [--chi-do]
Mẹo: xoá ở độ phân giải GỐC (720p) TRƯỚC khi nâng nét — sau khi nâng (RelayVSR…) viền logo sắc hơn hình mẫu, trừ xong còn hằn viền.
In JSON; mã 0 = đã xoá hoặc không có logo, 2 = còn logo / khung không phải 16:9, 1 = lỗi.
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import logo_sao as L


def thong_so(ff, vao):
    e = subprocess.run([ff, '-hide_banner', '-i', vao], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    m = re.search(r'Video:.*?, (\d{2,5})x(\d{2,5})', e)
    if not m:
        return None
    f = re.search(r'(\d+(?:\.\d+)?) fps', e)
    d = re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)', e)
    giay = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3)) if d else 0
    return int(m.group(1)), int(m.group(2)), float(f.group(1)) if f else 30.0, giay, ' Audio:' in e


def khung(ff, vao, t, W, H):
    r = subprocess.run([ff, '-v', 'error', '-ss', f'{t:.3f}', '-i', vao, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'bgr24', 'pipe:1'], capture_output=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(H, W, 3).copy() if len(r.stdout) == W * H * 3 else None


def main():
    a = sys.argv[1:]
    ff = a[a.index('--ffmpeg') + 1] if '--ffmpeg' in a else 'ffmpeg'
    vao, ra = [x for i, x in enumerate(a) if not x.startswith('--') and (i == 0 or a[i - 1] != '--ffmpeg')][:2]
    ts = thong_so(ff, vao)
    if not ts:
        print(json.dumps({'loi': 'khong doc duoc clip'})); sys.exit(1)
    W, H, fps, giay, tieng = ts
    mau = [k for k in (khung(ff, vao, giay * (i + 0.5) / 20, W, H) for i in range(20)) if k is not None]
    if len(mau) < 3:
        print(json.dumps({'loi': 'khong lay duoc khung mau'})); sys.exit(1)
    kq = L.do_logo(mau, video=True)
    if kq.get('coLogo') is None or kq.get('conLogo'):
        print(json.dumps({**kq, 'conLogo': True})); sys.exit(2)
    if not kq['coLogo'] or '--chi-do' in a:
        print(json.dumps(kq)); sys.exit(0)
    doc = subprocess.Popen([ff, '-v', 'error', '-i', vao, '-f', 'rawvideo', '-pix_fmt', 'bgr24', 'pipe:1'], stdout=subprocess.PIPE)
    ghi = subprocess.Popen([ff, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', f'{fps:g}', '-i', 'pipe:0', '-i', vao,
                            '-map', '0:v', *(['-map', '1:a', '-c:a', 'copy'] if tieng else []), '-c:v', 'libx264', '-preset', 'medium', '-crf', '14',
                            '-pix_fmt', 'yuv420p', '-shortest', ra], stdin=subprocess.PIPE)
    n, kc = 0, W * H * 3
    while True:
        b = doc.stdout.read(kc)
        if len(b) < kc:
            break
        ghi.stdin.write(L.khu(np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(), kq['x'], kq['y'], kq['co'], kq['k']).tobytes()); n += 1
    ghi.stdin.close(); doc.wait(); ghi.wait()
    if ghi.returncode != 0 or n == 0:
        print(json.dumps({**kq, 'loi': 'ghi clip loi'})); sys.exit(1)
    print(json.dumps({**kq, 'khung': n})); sys.exit(0)


if __name__ == '__main__':
    main()
