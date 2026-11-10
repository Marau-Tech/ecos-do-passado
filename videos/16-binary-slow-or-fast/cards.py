"""Takes desenhados: o visor de data da Terra (a3) e a parede riscada de dias (b3)."""
import numpy as np
from gfx import W, H, canvas, font, text
import timeline as TL

MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
AMBER, DIM = (255, 170, 60), (70, 40, 14)


def earth_year(rt):
    """o ano corre cada vez mais rápido até a chave, e trava"""
    u = min(1.0, rt / TL.TURN) ** 1.6
    return TL.YEAR0 + (TL.YEAR1 - TL.YEAR0) * u


def draw_a3(rt):
    img, d = canvas((22, 20, 18))
    d.rectangle((110, 110, 850, 590), fill=(48, 46, 42), outline=(15, 14, 12), width=6)
    for x, y in ((135, 135), (825, 135), (135, 565), (825, 565)):
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(80, 78, 72))
    text(d, (W // 2, 180), 'EARTH DATE', font(38, 'mono'), (200, 195, 180))
    d.rectangle((170, 230, 790, 400), fill=(12, 8, 4), outline=(5, 3, 2), width=4)
    yr = earth_year(rt)
    frac = yr % 1.0
    day = 1 + int(frac * 365) % 28
    mon = MONTHS[int(frac * 12) % 12]
    s = f'{mon} {day:02d} {int(yr)}'
    text(d, (W // 2, 318), '888 88 8888', font(82, 'mono'), DIM)         # segmentos apagados atrás
    text(d, (W // 2, 318), s, font(82, 'mono'), AMBER)
    text(d, (W // 2, 470), 'LOCAL: DAY 1', font(34, 'mono'), (200, 195, 180))
    lit = (rt * 20) % 1 < 0.5 if rt < TL.TURN else True
    d.ellipse((700, 455, 730, 485), fill=(255, 60, 40) if lit else (70, 20, 15))
    return img


# riscos de contagem: grupos de 5 (4 em pé e 1 cortando), em linhas, do canto de cima à esquerda
GW, GH, X0, Y0, COLS, ROWS = 30, 34, 90, 86, 26, 15
_rs = np.random.RandomState(3)
_JIT = _rs.uniform(-2.5, 2.5, (COLS * ROWS, 5, 4))
_TONE = _rs.uniform(0.0, 1.0, COLS * ROWS)
_WALL = None


def wall():
    global _WALL
    if _WALL is None:
        from PIL import Image
        rs = np.random.RandomState(1)
        g = rs.randn(H // 4, W // 4)
        from scipy.ndimage import gaussian_filter, zoom
        g = zoom(gaussian_filter(g, 2.0), 4, order=1)[:H, :W]
        base = 120 + 14 * g[..., None] + rs.randn(H, W, 1) * 4
        a = np.clip(base * np.array([1.0, 1.0, 0.96]), 0, 255).astype(np.uint8)
        _WALL = Image.fromarray(a)
    return _WALL.copy()


def draw_b3(rt):
    from PIL import ImageDraw
    img = wall(); d = ImageDraw.Draw(img)
    total = COLS * ROWS * 5
    u = min(1.0, rt / TL.TURN)
    count = int(total * u ** 1.5)
    for i in range(count):
        g, k = divmod(i, 5)
        r, c = divmod(g, COLS)
        x, y = X0 + c * GW, Y0 + r * GH
        j = _JIT[g, k]
        tone = int(40 + 50 * _TONE[g])
        col = (tone, tone, tone - 4)
        if k < 4:
            d.line((x + 4 + k * 5 + j[0], y + 2 + j[1], x + 4 + k * 5 + j[2], y + 28 + j[3]), fill=col, width=2)
        else:
            d.line((x + j[0], y + 22 + j[1], x + 26 + j[2], y + 6 + j[3]), fill=col, width=2)
    return img
