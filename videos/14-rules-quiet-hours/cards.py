"""Takes desenhados: a ficha de empréstimo e a capa do livro."""
from gfx import W, H, canvas, font, text, typed, blink

DATES = ['MAR 14 1986', 'APR 09 1986', 'JUN 21 1987', 'SEP 30 1987', 'NOV 06 1988']


def draw_r2a(rt):
    img, d = canvas((38, 26, 18))
    d.rectangle((130, 90, 830, 600), fill=(228, 218, 180), outline=(90, 70, 50), width=4)
    text(d, (W // 2, 140), 'DATE DUE', font(40, 'serif'), (50, 40, 30))
    d.line((130, 175, 830, 175), fill=(90, 70, 50), width=3)
    for i, s in enumerate(DATES):
        y = 225 + i * 50
        d.line((160, y + 22, 800, y + 22), fill=(170, 160, 130), width=2)
        if rt >= 0.5 + i * 0.5:
            text(d, (330 + (i % 2) * 14, y), s, font(32, 'mono'), (80, 40, 110))
    if rt >= 3.6:
        d.line((160, 497, 800, 497), fill=(170, 160, 130), width=2)
        text(d, (400, 475), 'TONIGHT', font(34, 'mono'), (150, 30, 30))
    return img


def draw_r4a(rt):
    img, d = canvas((20, 24, 20))
    d.rectangle((240, 90, 720, 610), fill=(30, 62, 44), outline=(12, 30, 20), width=6)
    d.rectangle((262, 112, 698, 588), outline=(205, 170, 80), width=3)
    text(d, (480, 190), 'A BIOGRAPHY', font(34, 'serif'), (205, 170, 80))
    text(d, (480, 260), 'OF', font(30, 'serif'), (205, 170, 80))
    d.rectangle((330, 320, 630, 400), outline=(205, 170, 80), width=2, fill=(226, 214, 176))
    name = typed('YOU', rt, 0.8, 4)
    text(d, (480, 360), name + ('_' if blink(rt) else ' '), font(46, 'mono'), (40, 30, 30))
    text(d, (480, 500), 'VOL. 1 OF 1', font(26, 'serif'), (205, 170, 80))
    return img
