"""Peças de desenho que qualquer skin do survive pode usar: silhueta, olhos, campo de calor, luz e camadas.

Só roda no post (usa PIL e scipy). Tudo em 960x720, com imagem em float de 0 a 1.
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, zoom

W, H = 960, 720
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def layer():
    """Camada em tons de cinza para desenhar com PIL; converta com arr()."""
    im = Image.new('L', (W, H))
    return im, ImageDraw.Draw(im)


def arr(im, blur=0.0):
    a = np.asarray(im, np.float32) / 255
    return (gaussian_filter(a, blur) if blur else a)[..., None]


def light(x, y, radius, squash=1.0):
    """Luz que cai com a distância de (x, y). squash > 1 achata na vertical."""
    return np.exp(-((XX - x) ** 2 + ((YY - y) * squash) ** 2) / (radius * radius))


def figure(d, x, feet, h, lean=0.0, col=255):
    """Silhueta alta, magra, de braços compridos demais. Devolve a posição da cabeça, para os olhos."""
    hr, sh, top, lx = h * 0.06, h * 0.11, feet - h, lean * h
    d.ellipse([x + lx - hr, top, x + lx + hr, top + hr * 2.3], fill=col)
    neck = top + hr * 2.1
    d.polygon([(x + lx * 0.8 - sh, neck + h * 0.05), (x + lx * 0.8 + sh, neck + h * 0.05),
               (x + h * 0.06, feet - h * 0.42), (x - h * 0.06, feet - h * 0.42)], fill=col)
    d.polygon([(x + lx - hr * 0.5, neck - 2), (x + lx + hr * 0.5, neck - 2),
               (x + lx * 0.8 + sh * 0.6, neck + h * 0.07), (x + lx * 0.8 - sh * 0.6, neck + h * 0.07)], fill=col)
    for s in (-1, 1):
        d.line([(x + lx * 0.8 + s * sh * 0.95, neck + h * 0.06), (x + s * sh * 1.25, feet - h * 0.22)],
               fill=col, width=max(2, int(h * 0.025)))
        d.line([(x + s * h * 0.04, feet - h * 0.43), (x + s * h * 0.055, feet)], fill=col, width=max(2, int(h * 0.035)))
    return x + lx, top + h * 0.07


def eyes(heads, lit, t, color=(0.95, 0.92, 0.75)):
    """Pares de olhos que brilham só no escuro. heads: [(x, y, tamanho, fase da piscada, força)].
    lit é o mapa de luz: onde está claro, o olho some."""
    im, d = layer()
    for hx, hy, hh, blink, k in heads:
        if (t + blink) % 5.3 < 0.16: continue
        lv = lit[int(np.clip(hy, 0, H - 1)), int(np.clip(hx, 0, W - 1))]
        b = np.clip(1 - lv * 0.9, 0, 1) * k
        sep, rx, ry = max(hh * 0.03, 3), max(hh * 0.011, 1.5), max(hh * 0.009, 1.2)
        for s in (-1, 1):
            d.ellipse([hx + s * sep - rx, hy - ry, hx + s * sep + rx, hy + ry], fill=int(255 * b))
    a = np.asarray(im, np.float32)
    return ((gaussian_filter(a, 2.5) * 2.5 + a)[..., None] / 255) * np.array(color, np.float32)


class Heat:
    """Campo de calor em meia resolução: fogo, brasas, chamas de vela. add() põe pontos, rgb() devolve a cor."""

    def __init__(self):
        self.core = np.zeros((H // 2, W // 2), np.float32)
        self.small = np.zeros_like(self.core)

    def add(self, x, y, k, small=False):
        xi = np.clip((np.asarray(x) / 2).astype(int), 0, W // 2 - 1)
        yi = np.clip((np.asarray(y) / 2).astype(int), 0, H // 2 - 1)
        np.add.at(self.small if small else self.core, (yi, xi), k)

    def rgb(self, glow_color=(0.9, 0.32, 0.08)):
        c = gaussian_filter(self.core, 3.2) * 55 + gaussian_filter(self.small, 3.4) * 48
        heat = 1 - np.exp(-c)
        glow = gaussian_filter(self.core + self.small * 5, 16) * 60
        col = np.stack([np.clip(heat * 2.1, 0, 1), np.clip(heat * 2.1 - 0.65, 0, 1) * 0.9,
                        np.clip(heat * 3 - 2.1, 0, 1) * 0.85], -1)
        col += glow[..., None] * np.array(glow_color)
        return zoom(col, (2, 2, 1), order=1)


def flicker(t, seed=0):
    r = np.random.RandomState(int(t * 1000) + seed)
    return 1 + 0.07 * math.sin(t * 13.1) + 0.05 * math.sin(t * 29.7 + 1) + r.uniform(-0.04, 0.04)


def done(img):
    return Image.fromarray((np.clip(img, 0, 1) ** (1 / 1.1) * 255).astype(np.uint8))
