"""Desenho 2D do modelo eas: telas de alerta, barras de cor e letreiro."""
from PIL import ImageDraw
from gfx import W, H, SAFE, WHITE, canvas, font, text, block, crawl, blink, color_bars

STYLES = {                      # fundo, faixa do cabeçalho, cor do cabeçalho, cor do texto
    'red':   ((10, 10, 14), (190, 18, 18), WHITE, WHITE),
    'blue':  ((18, 40, 150), (18, 40, 150), (255, 230, 90), WHITE),
    'black': ((0, 0, 0), (0, 0, 0), (230, 40, 40), (230, 230, 230)),
}


def alert(a, rt):
    """Tela de alerta. a: style, head, lines (parágrafos), crawl, e opcionais type (digita as linhas)
    e blink (cabeçalho piscando)."""
    if a['style'] == 'bars':
        img = color_bars()
        if a.get('lines'):
            d = ImageDraw.Draw(img)
            d.rectangle((0, H // 2 - 70, W, H // 2 + 70), fill=(0, 0, 0))
            text(d, (W // 2, H // 2), a['lines'][0], font(44), WHITE)
        return img
    bg, band, hc, tc = STYLES[a['style']]
    img, d = canvas(bg)
    if a.get('crawl'):
        crawl(d, a['crawl'], 112, rt, font(34), 190, WHITE, band=(150, 10, 10) if a['style'] != 'blue' else (10, 20, 90))
    d.rectangle((0, 160, W, 250), fill=band)
    if not a.get('blink') or blink(rt, 1.2, 0.7):
        text(d, (W // 2, 205), a['head'], font(50, 'sans'), hc)
    y = 290
    shown = int(rt * 30) if a.get('type') else None
    for ln in a['lines']:
        y = block(d, ln, font(40), y, tc, step=52, shown=shown) + 18
        if shown is not None:
            shown -= len(ln)
    return img
