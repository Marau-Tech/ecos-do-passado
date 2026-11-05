"""Desenho 2D para takes desenhados: textos, cartelas, barras de cor, ícones e letreiros.

Tudo desenha em 960x720, o tamanho do quadro 4:3 do post. Usa PIL, então não roda no Blender.
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 960, 720
WHITE, BLACK = (245, 245, 235), (0, 0, 0)
_DIR = '/usr/share/fonts/truetype/dejavu'
FONTS = {'mono': 'DejaVuSansMono-Bold', 'mono-r': 'DejaVuSansMono', 'sans': 'DejaVuSans-Bold',
         'sans-r': 'DejaVuSans', 'cond': 'DejaVuSansCondensed-Bold', 'serif': 'DejaVuSerif-Bold'}
SAFE = 70           # margem lateral; o OSD ocupa y < 70 e y > H - 110


@lru_cache(None)
def font(size, kind='mono'):
    return ImageFont.truetype(f'{_DIR}/{FONTS[kind]}.ttf', size)


def canvas(color=BLACK):
    img = Image.new('RGB', (W, H), color)
    return img, ImageDraw.Draw(img)


def typed(s, rt, at=0.0, cps=45):
    """Parte do texto já digitada no instante rt, começando em at, com cps letras por segundo."""
    return s[:max(0, int((rt - at) * cps) + 1)] if rt >= at else ''


def blink(rt, hz=1.5, duty=0.6):
    return (rt * hz) % 1 < duty


def wrap(d, s, f, maxw):
    lines = []
    for par in s.split('\n'):
        cur = ''
        for w in par.split():
            c = (cur + ' ' + w).strip()
            if d.textlength(c, font=f) <= maxw: cur = c
            else: lines.append(cur); cur = w
        lines.append(cur)
    return lines


def text(d, xy, s, f, fill=WHITE, anchor='mm', stroke=0, stroke_fill=BLACK):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)


def block(d, s, f, y, fill=WHITE, maxw=W - 2 * SAFE, step=None, align='center', x=None, shown=None):
    """Parágrafo quebrado em linhas a partir de y (topo). shown corta o total de letras, para digitar.
    Devolve o y depois da última linha."""
    lines = wrap(d, s, f, maxw)
    step = step or int(f.size * 1.3)
    left = SAFE if x is None else x
    for ln in lines:
        part = ln if shown is None else ln[:max(0, shown)]
        if shown is not None:
            shown -= len(ln)
        if part:
            if align == 'center':
                d.text((W // 2 - d.textlength(ln, font=f) / 2, y), part, font=f, fill=fill, anchor='la')
            else:
                d.text((left, y), part, font=f, fill=fill, anchor='la')
        y += step
    return y


def crawl(d, s, y, rt, f, speed=170, fill=WHITE, band=None, h=None):
    """Letreiro que corre da direita para a esquerda, repetindo. band pinta a faixa atrás."""
    h = h or int(f.size * 1.6)
    if band:
        d.rectangle((0, y - h // 2, W, y + h // 2), fill=band)
    s = s + '   ' * 4
    L = d.textlength(s, font=f)
    x = W - (rt * speed) % L
    while x > -L:
        x -= L
    while x < W:
        d.text((x, y), s, font=f, fill=fill, anchor='lm')
        x += L


def color_bars(img=None):
    """Barras de cor SMPTE, a tela de teste da TV."""
    img = img or Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    top = [(192, 192, 192), (192, 192, 0), (0, 192, 192), (0, 192, 0), (192, 0, 192), (192, 0, 0), (0, 0, 192)]
    mid = [(0, 0, 192), (19, 19, 19), (192, 0, 192), (19, 19, 19), (0, 192, 192), (19, 19, 19), (192, 192, 192)]
    bw = W / 7
    for i, c in enumerate(top):
        d.rectangle((i * bw, 0, (i + 1) * bw, H * 0.67), fill=c)
    for i, c in enumerate(mid):
        d.rectangle((i * bw, H * 0.67, (i + 1) * bw, H * 0.75), fill=c)
    low = [((0, 33, 76), 1.25), ((255, 255, 255), 1.25), ((50, 0, 106), 1.25), ((19, 19, 19), 1.25),
           ((9, 9, 9), 1 / 3), ((19, 19, 19), 1 / 3), ((29, 29, 29), 1 / 3), ((19, 19, 19), 1)]
    x = 0
    for c, k in low:
        d.rectangle((x, H * 0.75, x + bw * k, H), fill=c); x += bw * k
    return img


def static(img, amount=1.0, seed=0):
    """Mistura chuvisco na imagem."""
    rs = np.random.RandomState(seed)
    a = np.asarray(img, np.float32) / 255
    nz = rs.rand(H // 2 + 1, W).astype(np.float32).repeat(2, 0)[:H, :, None]
    return Image.fromarray((np.clip(a * (1 - amount) + nz * amount, 0, 1) * 255).astype(np.uint8))


def leader(d, rt, number, fg=(30, 30, 30), bg=(170, 170, 160)):
    """Contagem de filme: círculo, cruz, setor girando e o número."""
    d.rectangle((0, 0, W, H), fill=bg)
    cx, cy, r = W // 2, H // 2, 250
    ang = (rt % 1) * 360 - 90
    d.pieslice((cx - r * 2, cy - r * 2, cx + r * 2, cy + r * 2), -90, ang, fill=(120, 120, 112))
    d.line((0, cy, W, cy), fill=fg, width=4); d.line((cx, 0, cx, H), fill=fg, width=4)
    for rr in (r, r - 30):
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=fg, width=6)
    text(d, (cx, cy + 10), str(number), font(330, 'sans'), fg)


# ---- ícones de previsão do tempo ----
def icon(d, kind, cx, cy, s=60, fill=WHITE, accent=(255, 205, 60), bg=BLACK):
    """Ícone simples: sun, moon, cloud, rain, storm, snow, fog, eye, none. bg é a cor do fundo, para a lua."""
    def cloud(dx=0, dy=0, c=fill):
        for ox, oy, rr in ((-0.45, 0.1, 0.38), (0.0, -0.15, 0.5), (0.45, 0.1, 0.38)):
            x, y, r = cx + dx + ox * s, cy + dy + oy * s, rr * s
            d.ellipse((x - r, y - r, x + r, y + r), fill=c)
        d.rectangle((cx + dx - 0.8 * s, cy + dy + 0.1 * s, cx + dx + 0.8 * s, cy + dy + 0.48 * s), fill=c)
    if kind == 'sun':
        r = 0.45 * s
        for i in range(8):
            a = i * math.pi / 4
            d.line((cx + math.cos(a) * r * 1.3, cy + math.sin(a) * r * 1.3, cx + math.cos(a) * r * 1.9, cy + math.sin(a) * r * 1.9), fill=accent, width=max(3, s // 12))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=accent)
    elif kind == 'moon':
        r = 0.55 * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(235, 235, 210))
        d.ellipse((cx - r + 0.4 * s, cy - r - 0.15 * s, cx + r + 0.4 * s, cy + r - 0.15 * s), fill=bg)
    elif kind in ('cloud', 'rain', 'storm', 'snow'):
        cloud(dy=-0.2 * s)
        if kind == 'rain':
            for i in range(4):
                x = cx - 0.5 * s + i * 0.33 * s
                d.line((x, cy + 0.45 * s, x - 0.12 * s, cy + 0.8 * s), fill=(120, 170, 255), width=max(3, s // 14))
        if kind == 'storm':
            p = [(0.05, 0.3), (-0.15, 0.62), (0.05, 0.62), (-0.1, 0.95), (0.25, 0.52), (0.05, 0.52), (0.18, 0.3)]
            d.polygon([(cx + x * s, cy + y * s) for x, y in p], fill=accent)
        if kind == 'snow':
            for i in range(3):
                x = cx - 0.4 * s + i * 0.4 * s
                text(d, (x, cy + 0.68 * s), '*', font(int(0.5 * s), 'sans'), (230, 240, 255))
    elif kind == 'fog':
        for i in range(4):
            y = cy - 0.4 * s + i * 0.27 * s
            d.rounded_rectangle((cx - 0.8 * s + (i % 2) * 0.15 * s, y, cx + 0.8 * s - (i % 2) * 0.15 * s, y + 0.12 * s), 0.06 * s, fill=(200, 200, 200))
    elif kind == 'eye':
        d.ellipse((cx - 0.85 * s, cy - 0.42 * s, cx + 0.85 * s, cy + 0.42 * s), fill=(240, 240, 230))
        d.ellipse((cx - 0.34 * s, cy - 0.34 * s, cx + 0.34 * s, cy + 0.34 * s), fill=(150, 20, 20))
        d.ellipse((cx - 0.14 * s, cy - 0.14 * s, cx + 0.14 * s, cy + 0.14 * s), fill=(0, 0, 0))
    else:                                          # none: o quadro fica vazio
        text(d, (cx, cy), '?', font(int(0.9 * s), 'sans'), (120, 120, 120))
