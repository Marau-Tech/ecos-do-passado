"""Filtros de imagem. Cada look recebe a (float RGB 0..1, a tela inteira), o número do frame e a força do glitch."""
import numpy as np
from scipy.ndimage import uniform_filter1d, gaussian_filter1d


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

def cctv(a, n, g):
    """Câmera de segurança: monocromática, granulada e com compressão. Fora de glitch, a imagem fica estável."""
    n //= 2                                      # a câmera grava a 15 fps
    rs = np.random.RandomState(n * 7 + 1)
    Hh, Ww, _ = a.shape
    Y = a @ np.array([.299, .587, .114], np.float32)
    # compressão: detalhe vira bloco
    B = 8; hh, ww = Hh // B * B, Ww // B * B
    blk = Y[:hh, :ww].reshape(hh // B, B, ww // B, B).mean((1, 3))
    Y[:hh, :ww] = Y[:hh, :ww] * 0.7 + np.repeat(np.repeat(blk, B, 0), B, 1) * 0.3
    Y = uniform_filter1d(uniform_filter1d(Y, 3, axis=1), 2, axis=0)
    # ruído de sensor, mais forte no escuro
    nz = np.repeat(np.repeat(rs.randn(Hh // 2 + 1, Ww // 2 + 1).astype(np.float32), 2, 0), 2, 1)[:Hh, :Ww]
    Y = Y + nz * (0.018 + 0.036 * np.clip(1 - Y * 2.2, 0, 1))
    rows = np.arange(Hh)
    # interferência lenta do cabo
    by = (n * 2.3) % (Hh * 1.5) - Hh * 0.25
    Y = Y * (1 + 0.035 * np.exp(-((rows - by) / 70) ** 2))[:, None]
    if g > 0:
        for _ in range(int(3 + 16 * g)):         # faixas deslocadas
            y0 = rs.randint(Hh); h = rs.randint(6, 70)
            Y[y0:y0 + h] = np.roll(Y[y0:y0 + h], int(rs.randint(-260, 260) * g), 1)
        for _ in range(int(34 * g)):             # blocos corrompidos
            y0 = rs.randint(Hh // 16) * 16; x0 = rs.randint(Ww // 16) * 16
            h = 16 * rs.randint(1, 4); w = 16 * rs.randint(1, 10)
            ys = rs.randint(Hh // 16) * 16; xs = rs.randint(Ww // 16) * 16
            src = Y[ys:ys + h, xs:xs + w]
            Y[y0:y0 + src.shape[0], x0:x0 + src.shape[1]] = src[:Hh - y0, :Ww - x0]
        if g > 0.7:                              # perda de sinal
            k = min(1.0, (g - 0.7) * 3.0)
            snow = np.repeat(rs.rand(Hh // 4 + 1, Ww).astype(np.float32), 4, 0)[:Hh]
            Y = Y * (1 - k) + snow * k * 0.7
    # linhas e vinheta
    Y = Y * (1 - 0.05 * (rows % 2))[:, None]
    xx = np.linspace(-1, 1, Ww)[None, :]; yy = np.linspace(-1, 1, Hh)[:, None]
    Y = Y * (1 - 0.34 * (xx ** 2 * 0.8 + yy ** 2 * 0.8) ** 1.4)
    return np.clip(Y[..., None] * np.array([0.90, 1.0, 0.94], np.float32), 0, 1)


def _yiq(a):
    Y = a @ np.array([.299, .587, .114], np.float32)
    I = a @ np.array([.596, -.274, -.322], np.float32)
    Q = a @ np.array([.211, -.523, .312], np.float32)
    return Y, I, Q


def _rgb(Y, I, Q):
    r = Y + .956 * I + .621 * Q; g = Y - .272 * I - .647 * Q; b = Y - 1.106 * I + 1.703 * Q
    return np.clip(np.stack([r, g, b], -1), 0, 1)


def _vignette(Y, k):
    Hh, Ww = Y.shape
    xx = np.linspace(-1, 1, Ww)[None, :]; yy = np.linspace(-1, 1, Hh)[:, None]
    return Y * (1 - k * (xx ** 2 * 0.8 + yy ** 2 * 0.8) ** 1.4)


def broadcast(a, n, g):
    """TV pega pela antena: mais limpa que a fita, com fantasma, chuvisco fino e barra de zumbido.
    No glitch o sincronismo se perde: a imagem rasga, rola e vira chuvisco."""
    rs = np.random.RandomState(n * 7 + 3)
    Hh, Ww, _ = a.shape
    Y, I, Q = _yiq(a)
    Y = uniform_filter1d(Y, 2, axis=1)
    I = np.roll(uniform_filter1d(I, 9, axis=1), 2, axis=1)
    Q = np.roll(uniform_filter1d(Q, 11, axis=1), 3, axis=1)
    Y = Y + 0.10 * (np.roll(Y, 11, axis=1) - Y) + 0.05 * (np.roll(Y, 23, axis=1) - Y)     # fantasma de multipercurso
    rows = np.arange(Hh)
    off = rs.randn(Hh) * 0.25
    if g > 0:                                          # perda de sincronismo horizontal
        knots = rs.randn(Hh // 40 + 2)
        off += np.interp(rows, np.arange(len(knots)) * 40, knots) * 40 * g
        off += ((rows + n * 37) % 180 < 12) * rs.randn() * 120 * g
    idx = (np.arange(Ww)[None, :] + np.round(off).astype(int)[:, None]) % Ww
    Y = np.take_along_axis(Y, idx, 1); I = np.take_along_axis(I, idx, 1); Q = np.take_along_axis(Q, idx, 1)
    nz = rs.randn(Hh, Ww).astype(np.float32)
    Y = Y + uniform_filter1d(nz, 2, axis=1) * (0.028 + 0.10 * g)
    Y = Y * (1 + 0.045 * np.sin(2 * np.pi * (rows / Hh - n * 0.006)))[:, None]   # barra de zumbido de 60 Hz
    I *= 1 - 0.8 * g; Q *= 1 - 0.8 * g
    if g > 0.55:                                       # rolagem vertical
        sft = int((n * 47) % Hh * g)
        Y = np.roll(Y, sft, 0); I = np.roll(I, sft, 0); Q = np.roll(Q, sft, 0)
        Y[(rows + sft) % Hh < 18] *= 0.15              # barra preta do intervalo vertical
    if g > 0.75:
        k = min(1.0, (g - 0.75) * 3.2)
        Y = Y * (1 - k) + rs.rand(Hh, Ww).astype(np.float32) * k
    Y = Y * (1 - 0.05 * (rows % 2))[:, None]
    return _rgb(_vignette(Y, 0.22), I, Q)


def webcam(a, n, g):
    """Webcam dos anos 2000: pouca resolução, blocos de compressão, cor em degraus e exposição que respira.
    O post segura cada frame por 3 (10 fps). No glitch, blocos ficam para trás e se arrastam."""
    rs = np.random.RandomState(n * 5 + 11)
    Hh, Ww, _ = a.shape
    S = 3
    h, w = Hh // S, Ww // S
    s = a[:h * S, :w * S].reshape(h, S, w, S, 3).mean((1, 3))
    y = s.mean(-1, keepdims=True)
    s = y + (s - y) * 1.25                              # cor estourada
    s = s * (1 + 0.05 * np.sin(n * 0.21) + 0.03 * np.sin(n * 0.057))       # exposição automática
    s = s + rs.randn(h // 2 + 1, w // 2 + 1, 3).repeat(2, 0).repeat(2, 1)[:h, :w] * 0.022
    B = 8; hh, ww = h // B * B, w // B * B                # blocos de compressão
    blk = s[:hh, :ww].reshape(hh // B, B, ww // B, B, 3).mean((1, 3))
    s[:hh, :ww] = s[:hh, :ww] * 0.55 + np.repeat(np.repeat(blk, B, 0), B, 1) * 0.45
    if g > 0:                                          # blocos arrastados de outro lugar
        for _ in range(int(6 + 40 * g)):
            y0 = rs.randint(h // B) * B; x0 = rs.randint(w // B) * B
            bh = B * rs.randint(1, 4); bw = B * rs.randint(1, 8)
            dy, dx = rs.randint(-2, 3) * B, rs.randint(-4, 5) * B
            ys, xs = np.clip(y0 + dy, 0, h - bh), np.clip(x0 + dx, 0, w - bw)
            s[y0:y0 + bh, x0:x0 + bw] = s[ys:ys + bh, xs:xs + bw][:h - y0, :w - x0]
        if g > 0.7:
            k = min(1.0, (g - 0.7) * 3)
            s = s * (1 - k) + np.repeat(np.repeat(rs.rand(h // B + 1, w // B + 1, 3), B, 0), B, 1)[:h, :w] * k * 0.6
    s = np.round(np.clip(s, 0, 1) * 31) / 31          # cor em 5 bits
    out = np.zeros_like(a)
    big = np.repeat(np.repeat(s, S, 0), S, 1)
    out[:h * S, :w * S] = uniform_filter1d(uniform_filter1d(big, 2, axis=0), 2, axis=1)
    return np.clip(out, 0, 1)


def probe(a, n, g):
    """Imagem de sonda no monitor do controle de missão: 6 bits por canal, erros de bit soltos
    e um leve fósforo de CRT. No glitch, pacotes se perdem e viram linhas pretas, repetidas ou de lixo."""
    rs = np.random.RandomState(n * 3 + 17)
    Hh, Ww, _ = a.shape
    a = np.round(np.clip(a, 0, 1) * 63) / 63
    a = a.copy()
    k = int(160 + 2500 * g)                           # erros de bit
    ys, xs = rs.randint(Hh, size=k), rs.randint(Ww, size=k)
    a[ys, xs] = rs.rand(k, 1) > 0.5
    for _ in range(rs.poisson(0.6 + 8 * g)):          # rajadas curtas na mesma linha
        y = rs.randint(Hh); x = rs.randint(Ww); L = rs.randint(20, 220)
        a[y, x:x + L] = rs.rand(min(L, Ww - x), 1) > 0.5
    if g > 0:
        P = 12
        for _ in range(int(2 + 14 * g)):              # pacotes perdidos
            y0 = rs.randint(Hh // P) * P
            kind = rs.randint(3)
            if kind == 0: a[y0:y0 + P] = 0
            elif kind == 1: a[y0:y0 + P] = a[max(0, y0 - 1)]
            else: a[y0:y0 + P] = rs.rand(min(P, Hh - y0), Ww, 1) * 0.8
    rows = np.arange(Hh)
    a = a * (1 - 0.08 * (rows % 3 == 0))[:, None, None]
    a = a + 0.25 * (uniform_filter1d(a, 5, axis=1) - a) * -1   # nitidez de monitor
    xx = np.linspace(-1, 1, Ww)[None, :]; yy = np.linspace(-1, 1, Hh)[:, None]
    a = a * (1 - 0.18 * (xx ** 2 * 0.8 + yy ** 2 * 0.8) ** 1.4)[..., None]
    return np.clip(a, 0, 1)


LOOKS = {'vhs': vhs, 'cctv': cctv, 'broadcast': broadcast, 'webcam': webcam, 'probe': probe}
STEP = {'webcam': 3}            # frames de 30 fps que cada frame do look segura
