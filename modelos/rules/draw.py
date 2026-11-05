"""Desenho 2D do modelo rules: contagem do filme, cartela de abertura e cartela de cada regra."""
from gfx import W, H, SAFE, WHITE, canvas, font, text, block, leader, icon

PALETTE = [((22, 92, 98), (240, 200, 90)), ((150, 60, 30), (250, 230, 190)), ((40, 50, 110), (250, 210, 120)),
           ((70, 100, 40), (245, 235, 200)), ((110, 30, 50), (250, 220, 170))]


def slate(tl, rt):
    """Contagem 3, 2, 1 do filme e depois a cartela: quem apresenta, número e título."""
    n = int(rt / tl.SLATE_COUNT)
    if n < 3:
        img, d = canvas()
        leader(d, rt / tl.SLATE_COUNT, 3 - n)
        return img
    img, d = canvas((18, 22, 26))
    org, film, name = tl.FILM
    d.rectangle((50, 80, W - 50, H - 120), outline=(200, 190, 160), width=4)
    text(d, (W // 2, 160), org, font(30, 'serif'), (200, 190, 160))
    text(d, (W // 2, 205), 'PRESENTS', font(24, 'serif'), (160, 150, 130))
    text(d, (W // 2, 300), film, font(36, 'serif'), (230, 220, 190))
    block(d, name, font(58, 'serif'), 360, (250, 240, 210), maxw=W - 200, step=70)
    return img


def rule_card(tl, k, rt):
    """Cartela da regra k: número grande, texto da regra e ícone opcional (RULES[k-1][1])."""
    rule = tl.RULES[k - 1]
    bg, fg = PALETTE[(k - 1) % len(PALETTE)]
    img, d = canvas(bg)
    d.rectangle((36, 76, W - 36, H - 116), outline=fg, width=6)       # fora do OSD
    d.rectangle((50, 90, W - 50, H - 130), outline=fg, width=2)
    text(d, (W // 2, 180), f'RULE {k}', font(110, 'sans'), fg)
    y = block(d, rule[0], font(48, 'sans'), 280, WHITE, maxw=W - 220, step=60)
    if len(rule) > 1 and rule[1]:
        icon(d, rule[1], W // 2, min(H - 200, y + 80), 60, bg=bg)
    return img
