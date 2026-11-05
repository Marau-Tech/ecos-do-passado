"""Desenho 2D do modelo weather: vinheta da emissora, previsão de vários dias e camadas do mapa."""
import math
from PIL import Image, ImageDraw
from gfx import W, H, SAFE, WHITE, canvas, font, text, icon

NAVY, BLUE, SKY = (12, 28, 80), (30, 70, 170), (90, 150, 230)
GOLD = (255, 205, 60)


def _grad(top, bottom):
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        u = y / (H - 1)
        d.line((0, y, W, y), fill=tuple(int(a + (b - a) * u) for a, b in zip(top, bottom)))
    return img, d


def ident(tl, rt):
    """Vinheta: nome da emissora e do quadro entrando, com uma faixa que passa."""
    img, d = _grad(NAVY, BLUE)
    u = min(1.0, rt / 0.6)
    x = int(-W + (W + W // 2) * (1 - (1 - u) ** 3))
    d.polygon([(x - 300, 250), (x + 400, 250), (x + 340, 470), (x - 360, 470)], fill=(20, 50, 130))
    if rt > 0.25:
        text(d, (W // 2, 300), tl.STATION, font(110, 'sans'), WHITE, stroke=4, stroke_fill=NAVY)
        text(d, (W // 2, 420), tl.SHOW, font(54, 'sans'), GOLD, stroke=3, stroke_fill=NAVY)
    return img


def forecast(tl, days, rt):
    """Previsão: uma coluna por dia (nome, ícone, máxima e mínima), entrando um dia por vez."""
    img, d = _grad((20, 40, 110), (60, 110, 200))
    head = getattr(tl, 'FORECAST_HEAD', 'EXTENDED FORECAST')
    d.rectangle((0, 84, W, 160), fill=NAVY)
    text(d, (W // 2, 122), head, font(46, 'sans'), WHITE)
    n = len(days)
    cw = (W - 2 * 40) / n
    for i, day in enumerate(days):
        name, kind, hi, lo = day[:4]
        if rt < 0.15 + i * 0.25:
            continue
        cx = 40 + cw * (i + 0.5)
        d.rounded_rectangle((cx - cw / 2 + 8, 190, cx + cw / 2 - 8, 600), 14, fill=(15, 32, 92), outline=SKY, width=3)
        text(d, (cx, 235), name, font(38, 'sans'), GOLD)
        icon(d, kind, cx, 345, int(min(70, cw * 0.38)), bg=(15, 32, 92))
        text(d, (cx, 470), hi, font(58, 'sans'), WHITE)
        text(d, (cx, 545), lo, font(40, 'sans'), (170, 200, 255))
    return img


def map_layer(img, spec, rt):
    """Camadas por cima do mapa renderizado: eco de radar com varredura, cidades e temperaturas.
    spec: radar=[(x, y, raio, força)], sweep=True, roads=[((x, y), (x, y))], cities=[((x, y), nome, temp)], banner='texto'."""
    img = img.copy()
    if spec.get('radar'):
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        for x, y, r, k in spec['radar']:
            for j, (c, f) in enumerate((((40, 200, 60), 1.0), ((250, 220, 40), 0.66), ((230, 40, 30), 0.36))):
                if k >= j / 3:
                    rr = r * f
                    ld.ellipse((x - rr, y - rr * 0.8, x + rr, y + rr * 0.8), fill=c + (150,))
        img = Image.alpha_composite(img.convert('RGBA'), lay).convert('RGB')
    d = ImageDraw.Draw(img)
    for a, b in spec.get('roads', ()):              # estradas por baixo das cidades
        d.line((*a, *b), fill=(40, 40, 40), width=7)
        d.line((*a, *b), fill=(225, 215, 190), width=3)
    if spec.get('sweep'):
        cx, cy = spec.get('center', (W // 2, H // 2))
        a = rt * 2.2
        d.line((cx, cy, cx + math.cos(a) * 900, cy + math.sin(a) * 900), fill=(140, 255, 140), width=3)
    for (x, y), name, temp in spec.get('cities', ()):
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=WHITE, outline=(0, 0, 0), width=2)
        text(d, (x + 14, y - 4), name, font(28, 'sans'), WHITE, 'lm', 3)
        if temp:
            text(d, (x + 14, y + 30), temp, font(36, 'sans'), GOLD, 'lm', 3)
    if spec.get('banner'):
        d.rectangle((0, H - 210, W, H - 140), fill=(180, 20, 20))
        text(d, (W // 2, H - 175), spec['banner'], font(38, 'sans'), WHITE)
    return img
