"""Desenho do survive: roda a física uma vez, entrega cada frame para a skin e desenha o placar das barras.

Só roda no post (usa PIL). O que aparece na imagem é da skin; aqui fica só o que é igual em toda skin.
"""
import math
import numpy as np
from PIL import ImageDraw
from gfx import font
from modelos.survive import sim as S
from modelos.survive.sim import W, FPS

G = {}
WHITE = (245, 245, 235)


def prepare(tl):
    if 'sim' in G: return
    skin = S.skin_of(tl)
    c = S.config(tl)
    cfg = dict(getattr(skin, 'CFG', {}))
    cfg.update(getattr(tl, 'SKIN_CFG', {}))
    G.update(skin=skin, c=c, cfg=cfg, hud=dict(getattr(skin, 'HUD', {})))
    G['sim'] = S.Sim(c, skin=skin).run()
    if hasattr(skin, 'prepare'):
        skin.prepare(G['sim'], cfg)


def frame_at(t):
    fr = G['sim'].frames
    return fr[min(int(round(t * FPS)), len(fr) - 1)]


def world(t):
    """Imagem 960x720 do mundo no tempo global t."""
    return G['skin'].world(t, frame_at(t), G['sim'], G['cfg'])


def hud(tl, img, t, y0):
    """Barra de vida e contagem até o until, na barra de baixo (y0 = topo dela).
    Os textos vêm de HUD_NAME e HUD_CLOCK no timeline, ou do HUD da skin."""
    d = ImageDraw.Draw(img)
    fr = frame_at(t)
    hp, dead = fr['hp'], fr['dead']
    name = getattr(tl, 'HUD_NAME', G['hud'].get('name', 'LIFE'))
    clock = getattr(tl, 'HUD_CLOCK', G['hud'].get('clock', 'SURVIVE'))
    x0, bw, bh, y = 110, 740, 44, y0 + 95
    d.rectangle([x0, y, x0 + bw, y + bh], outline=WHITE, width=3)
    k = np.clip(hp / 100, 0, 1)
    blink = (t * 4) % 1 < 0.6
    if hp <= 20:                                   # perigo: vermelho piscando, em toda skin
        col = (230, 40, 30) if blink else (120, 20, 15)
    else:                                          # HUD['color'] da skin: cor da barra, de vazia a cheia
        c0, c1 = G['hud'].get('color', ((255, 70, 30), (255, 220, 70)))
        col = tuple(int(a + (b - a) * k) for a, b in zip(c0, c1))
    if k > 0:
        d.rectangle([x0 + 6, y + 6, x0 + 6 + (bw - 12) * k, y + bh - 6], fill=col)
    f = font(32)
    d.text((x0, y - 30), name, font=f, fill=WHITE, anchor='lm')
    d.text((x0 + bw, y - 30), f'{int(math.ceil(hp))}%', font=f, fill=WHITE, anchor='rm')
    stop = min(t, dead) if dead is not None else t
    left = int(math.ceil(max(0, G['c']['until'] - stop) - 1e-6))
    if dead is None or blink:
        d.text((W // 2, y + bh + 105), f'{clock}  {left // 60:02d}:{left % 60:02d}', font=font(44),
               fill=WHITE if dead is None else (230, 40, 30), anchor='mm')
