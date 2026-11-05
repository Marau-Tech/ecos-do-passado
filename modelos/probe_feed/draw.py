"""Desenho 2D do modelo probe_feed: tela do terminal de recepção e a imagem chegando linha a linha."""
import numpy as np
from PIL import Image
from gfx import W, H, SAFE, canvas, font, typed, blink

GREEN = (120, 255, 150)
DIM = (50, 120, 70)


def header(tl, rt):
    """Terminal da estação: linhas de HEADER digitadas uma após a outra, com cursor."""
    img, d = canvas((2, 8, 4))
    f = font(30)
    y, at = 120, 0.15
    for i, ln in enumerate(tl.HEADER):
        s = typed(ln, rt, at, 40)
        d.text((SAFE, y), s, font=f, fill=GREEN if i else (200, 255, 210))
        if 0 < len(s) < len(ln) or (s == ln and i == len(tl.HEADER) - 1):
            if blink(rt, 2.5):
                d.rectangle((SAFE + d.textlength(s, font=f) + 4, y + 2, SAFE + d.textlength(s, font=f) + 22, y + 32), fill=GREEN)
        at += len(ln) / 40 + 0.25
        y += 52
    for x in range(SAFE, W - SAFE, 24):                     # régua de dados
        d.line((x, H - 150, x, H - 140 - (hash((x, int(rt * 6))) % 30)), fill=DIM, width=3)
    return img


def reveal(img, u, rt):
    """Mostra a imagem só até a linha que já chegou. A linha que está chegando brilha;
    abaixo dela fica escuro, com um pouco de ruído de portadora."""
    a = np.asarray(img, np.float32) / 255
    rows = np.arange(H)[:, None, None]
    line = int(np.clip(u, 0, 1) * H)
    rs = np.random.RandomState(int(rt * 30) + 5)
    below = rs.rand(H, W, 1).astype(np.float32) * 0.05
    out = np.where(rows < line, a, below)
    if 0 <= u < 1:
        out[max(0, line - 2):line + 2] = 0.9
        out[max(0, line - 14):line] = out[max(0, line - 14):line] * 0.6 + 0.4 * out[max(0, line - 14):line].mean(-1, keepdims=True)
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
