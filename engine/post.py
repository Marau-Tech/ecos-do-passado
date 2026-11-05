import sys, os, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import uniform_filter1d, gaussian_filter1d
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from project import ROOT, FRAMES, OUT, PREVIEW
from timeline import *
W, H = 960, 720
VERT = os.environ.get('VERT', '1') == '1'     # 9:16: quadro 4:3 no centro, textos nas faixas; VERT=0 gera 4:3
CH = 1706
Y0 = (CH - H) // 2
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
F_CAP = ImageFont.truetype(FB, 30)
F_INTRO = ImageFont.truetype(FB, 38)
F_OSD = ImageFont.truetype(FB, 26)
F_BIG = ImageFont.truetype(FB, 46)
F_SUB = ImageFont.truetype(FB, 30)
F_END = ImageFont.truetype(FB, 84)
F_NUM = ImageFont.truetype(FB, 44)
F_VCAP = ImageFont.truetype(FB, 46)
F_VTIT = ImageFont.truetype(FB, 72)
F_VSUB = ImageFont.truetype(FB, 46)
F_VINT = ImageFont.truetype(FB, 62)

def shot_at(t):
    for name, dur, caps in SHOTS:
        if START[name] <= t < START[name] + dur:
            return name, t - START[name], dur, caps
    n, d, c = SHOTS[-1]
    return n, d - 1e-3, d, c

def load(name, idx):
    p = f'{FRAMES}/{name}/{idx:04d}.png'
    while idx > 0 and not os.path.exists(p):
        idx -= 1; p = f'{FRAMES}/{name}/{idx:04d}.png'
    if not os.path.exists(p):
        return Image.new('RGB', (640, 480))
    return Image.open(p).convert('RGB')

def glitch_at(t):
    g = 0.0
    for tt, s, d in EVENTS:
        if tt <= t < tt + d:
            g = max(g, s * (1 - (t - tt) / d * 0.6))
    return g

def grade(a, key):
    sat, con, tint, lift = GRADE[key]
    y = a @ np.array([.299, .587, .114], np.float32)
    a = y[..., None] + (a - y[..., None]) * sat
    a = (a - 0.5) * con + 0.5
    a = a * np.array(tint, np.float32)
    return a * (1 - lift) + lift

def text_box(d, xy, s, font, pad=10, anchor='mm', fill=(245, 245, 235), bg=(0, 0, 0)):
    x0, y0, x1, y1 = d.textbbox(xy, s, font=font, anchor=anchor)
    d.rectangle((x0 - pad * 1.4, y0 - pad, x1 + pad * 1.4, y1 + pad), fill=bg)
    d.text(xy, s, font=font, fill=fill, anchor=anchor)

def wrap(s, font, maxw, d):
    words = s.split(); lines = []; cur = ''
    for w in words:
        c = (cur + ' ' + w).strip()
        if d.textlength(c, font=font) <= maxw: cur = c
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def overlay(img, t, shot, rt, caps, frame):
    d = ImageDraw.Draw(img)
    # OSD
    if frame % 30 < 20:
        d.ellipse((40, 35, 64, 59), fill=(0, 0, 0)); d.ellipse((43, 38, 61, 56), fill=(225, 25, 20))
    d.text((72, 32), 'REC', font=F_OSD, fill=(240, 240, 230), stroke_width=3, stroke_fill=(0, 0, 0))
    first, last = PLANETS[0][2], PLANETS[-1][2]
    if t < START[first]:
        cd = 24 * 3600
    else:
        k = min(1.0, ((t - START[first]) % SECTION) / SECTION)
        if t >= START[last]:
            k = min(1.0, (t - START[last]) / (END_CARD - START[last]))
        cd = int(24 * 3600 * (1 - k))
    d.text((W - 42, 32), f'T-{cd // 3600:02d}:{cd % 3600 // 60:02d}:{cd % 60:02d}', font=F_OSD, fill=(240, 240, 230), anchor='ra', stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((42, H - 96), f'SP  {int(t) // 60}:{int(t) % 60:02d}:{frame % 30:02d}', font=F_OSD, fill=(240, 240, 230), stroke_width=3, stroke_fill=(0, 0, 0))
    # título do planeta
    for a, b, sh in PLANETS:
        if not VERT and shot == sh and 0.25 < rt < 2.6:
            text_box(d, (W // 2, 118), a, F_BIG, 8)
            text_box(d, (W // 2, 176), b, F_SUB, 7, fill=(255, 238, 180))
    # legendas
    for a, b, s in caps:
        if not VERT and a <= rt < b:
            n = int((rt - a) * 45) + 1
            font = F_INTRO if shot == 'intro' else F_CAP
            lines = wrap(s, font, W - 150, d)
            shown = n
            y = H - 130 - (len(lines) - 1) * 44
            if shot == 'intro': y = H // 2
            for ln in lines:
                part = ln[:max(0, shown)]; shown -= len(ln)
                if part:
                    x = W // 2 - d.textlength(ln, font=font) / 2
                    text_box(d, (x, y), part, font, 9, 'lm')
                y += 46
    if shot == 'intro':
        for (x, y), s in INTRO_LABELS:
            text_box(d, (x, y), s, F_NUM, 8, fill=(255, 215, 90))
    return img

def bars(img, shot, rt, caps):
    d = ImageDraw.Draw(img)
    white, gold = (245, 245, 235), (255, 225, 140)
    def typed(lines, font, y, step, shown):
        for ln in lines:
            part = ln[:max(0, shown)]; shown -= len(ln)
            if part:
                d.text((W // 2 - d.textlength(ln, font=font) / 2, y), part, font=font, fill=white, anchor='lm')
            y += step
    if shot != 'intro':
        a, b, _ = PLANETS[int(shot[1]) - 1]
        d.text((W // 2, 290), a, font=F_VTIT, fill=white, anchor='mm')
        d.text((W // 2, 376), b, font=F_VSUB, fill=gold, anchor='mm')
    for a, b, s in caps:
        if a <= rt < b:
            n = int((rt - a) * 45) + 1
            if shot == 'intro':
                typed(wrap(s, F_VINT, W - 200, d), F_VINT, 290, 84, n)
            else:
                typed(wrap(s, F_VCAP, W - 230, d), F_VCAP, Y0 + H + 80, 62, n)

def vhs(a, n, g):
    rs = np.random.RandomState(n * 7 + 1)
    Hh, Ww, _ = a.shape
    Y = a @ np.array([.299, .587, .114], np.float32)
    I = a @ np.array([.596, -.274, -.322], np.float32)
    Q = a @ np.array([.211, -.523, .312], np.float32)
    # banda limitada: luma macia + anel de nitidez, croma muito borrado e deslocado
    Yb = uniform_filter1d(Y, 3, axis=1)
    Y = Yb + 0.75 * (Yb - gaussian_filter1d(Yb, 3.2, axis=1))
    I = np.roll(uniform_filter1d(I, 19, axis=1), 5, axis=1)
    Q = np.roll(uniform_filter1d(Q, 25, axis=1), 6, axis=1)
    I = np.repeat(I[::2], 2, 0)[:Hh]; Q = np.repeat(Q[::2], 2, 0)[:Hh]
    rows = np.arange(Hh)
    # jitter de linha
    knots = rs.randn(Hh // 24 + 2)
    off = np.interp(rows, np.arange(len(knots)) * 24, knots) * (0.8 + 2.5 * g)
    off += rs.randn(Hh) * 0.35
    # faixa de tracking que desce devagar
    by = (n * 3.1) % (Hh * 1.8) - Hh * 0.4
    bw = 26 + 90 * g
    band = np.exp(-((rows - by) / bw) ** 2)
    off += band * rs.randn(Hh) * (2.5 + 30 * g)
    # head switching no rodapé
    hs = np.clip((rows - (Hh - 16)) / 16, 0, 1)
    off += hs ** 2 * (18 + 8 * rs.randn())
    if g > 0.3:
        off += np.sin(rows * 0.035 + n * 1.7) * 26 * g
    idx = (np.arange(Ww)[None, :] + np.round(off).astype(int)[:, None]) % Ww
    Y = np.take_along_axis(Y, idx, 1); I = np.take_along_axis(I, idx, 1); Q = np.take_along_axis(Q, idx, 1)
    # ruído
    nz = gaussian_filter1d(rs.randn(Hh, Ww).astype(np.float32), 1.1, axis=1)
    Y = Y + nz * (0.040 + 0.05 * g + 0.10 * band[:, None] + 0.25 * hs[:, None])
    cn = rs.randn(Hh // 8 + 1, Ww // 16 + 1).astype(np.float32)
    cn = np.repeat(np.repeat(cn, 8, 0), 16, 1)[:Hh, :Ww]
    I = I + uniform_filter1d(cn, 21, axis=1) * 0.018
    Q = Q + uniform_filter1d(cn[::-1], 21, axis=1) * 0.018
    # dropouts
    for _ in range(rs.poisson(0.5 + 6 * g)):
        y = rs.randint(Hh); x = rs.randint(Ww); L = rs.randint(30, 260)
        Y[y:y + rs.randint(1, 3), x:x + L] = 0.92 + rs.rand() * 0.08
    # neve em glitch forte
    if g > 0.75:
        k = min(1.0, (g - 0.75) * 3.2)
        snow = np.repeat(rs.rand(Hh // 2 + 1, Ww).astype(np.float32), 2, 0)[:Hh]
        Y = Y * (1 - k) + snow * k; I *= 1 - k; Q *= 1 - k
    if g > 0.55:                       # rolagem vertical
        sft = int(rs.randint(-140, 140) * g)
        Y = np.roll(Y, sft, 0); I = np.roll(I, sft, 0); Q = np.roll(Q, sft, 0)
    # linhas e vinheta
    Y = Y * (1 - 0.07 * (rows % 2))[:, None]
    xx = np.linspace(-1, 1, Ww)[None, :]; yy = np.linspace(-1, 1, Hh)[:, None]
    Y = Y * (1 - 0.30 * (xx ** 2 * 0.8 + yy ** 2 * 0.8) ** 1.4)
    r = Y + .956 * I + .621 * Q; gg = Y - .272 * I - .647 * Q; b = Y - 1.106 * I + 1.703 * Q
    return np.clip(np.stack([r, gg, b], -1), 0, 1)

def make_frame(n):
    t = n / FPS_OUT
    shot, rt, dur, caps = shot_at(t)
    g = glitch_at(t)
    key = shot[:2] if shot != 'intro' else 'intro'
    if t >= END_CARD:
        img = Image.new('RGB', (W, CH if VERT else H), (4, 4, 6))
        d = ImageDraw.Draw(img)
        d.text((W // 2, (CH if VERT else H) // 2), END_TEXT, font=F_END, fill=(240, 235, 225), anchor='mm')
        a = np.asarray(img, np.float32) / 255
    else:
        sub = [s for s in SUBLIM if s[0] <= t < s[0] + 1.5 / FPS_OUT]
        if sub:
            src = load(sub[0][1], sub[0][2]); gk = SUBLIM_GRADE
        else:
            idx = min(int(rt * FPS_SRC), int(round(dur * FPS_SRC)) - 1)
            src = load(shot, idx); gk = key
        im = src.resize((W, H), Image.BICUBIC)
        a = grade(np.asarray(im, np.float32) / 255, gk)
        a = frame_fx(a, shot, rt)
        im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
        im = overlay(im, t, shot, rt, caps, n)
        if VERT:
            c = Image.new('RGB', (W, CH), (4, 4, 6))
            c.paste(im, (0, Y0)); bars(c, shot, rt, caps); im = c
        a = np.asarray(im, np.float32) / 255
    a = vhs(a.astype(np.float32), n, g)
    return (a * 255).astype(np.uint8)

def still(n, path):
    Image.fromarray(make_frame(n)).save(path)

def main():
    step = 2 if PREVIEW else 1            # preview a 15 fps e encode rápido; o final segue em 30 fps e preset slow
    fps = FPS_OUT // step
    total = int(TOTAL * FPS_OUT)
    outp = f'{OUT}/video_mudo.mp4'
    size = f'{W}x{CH}' if VERT else f'{W}x{H}'
    scale = '1080:1920' if VERT else '1440:1080'
    ff = subprocess.Popen([f'{ROOT}/tools/ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                           '-s', size, '-r', str(fps), '-i', '-',
                           '-vf', f'scale={scale}:flags=bicubic', '-c:v', 'libx264', '-crf', '25', '-preset', 'veryfast' if PREVIEW else 'slow',
                           '-pix_fmt', 'yuv420p', outp], stdin=subprocess.PIPE)
    with Pool(int(os.environ.get('JOBS', '10'))) as p:
        for i, fr in enumerate(p.imap(make_frame, range(0, total, step), chunksize=4)):
            ff.stdin.write(fr.tobytes())
            if i % 150 == 0: print(i * step, '/', total, flush=True)
    ff.stdin.close(); ff.wait()
    print('ok', outp)

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'still':
        STILLS = os.environ.get('STILLS', f'{OUT}/stills'); os.makedirs(STILLS, exist_ok=True)
        for s in sys.argv[2:]:
            sec = float(s); still(int(sec * FPS_OUT), f'{STILLS}/s_{s}.png')
    else:
        main()
