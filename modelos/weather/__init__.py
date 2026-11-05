"""Modelo previsão do tempo: o boletim local da TV, em que a previsão vai deixando de fazer sentido.

Regras do roteiro em modelos/weather/GUIA.md.
"""
from modelos.base import *
from modelos.base import drawn as _drawn, card as _card, paint as _paint

__all__ = ['FPS_SRC', 'FPS_OUT', 'END_SECS', 'END_TEXT', 'END_TONE', 'MIN_SECS', 'MAX_SECS', 'timing']

LOOK = 'broadcast'
REC_DOT = False
MIN_SECS, MAX_SECS = 35, 75
END_SECS = 1.2
END_TEXT = ''
END_TONE = False                # tela final sem o tom de alerta do EAS


def timing(shots, end_card=None):
    return bounded(shots, END_SECS if end_card is None else end_card, MIN_SECS, MAX_SECS, 'weather')


def rec_label(tl, shot):
    return tl.STATION


def counter(tl, t):
    s = int(tl.CLOCK + t)
    h = s // 3600 % 24
    return f'{(h - 1) % 12 + 1}:{s % 3600 // 60:02d}  {tl.TEMP}'


def footer(tl, shot, t, frame):
    return None


def title(tl, shot):
    return getattr(tl, 'TITLES', {}).get(shot, tl.TITLE)


def grade_key(tl, shot):
    return shot if shot in tl.GRADE else 'scene'


def scene_module(tl, shot):
    return 'scene'


def drawn(tl, shot):
    return shot == 'ident' or shot in getattr(tl, 'FORECASTS', {}) or _drawn(tl, shot)


def card(tl, shot, rt):
    from modelos.weather import draw
    if shot == 'ident':
        return draw.ident(tl, rt)
    if shot in getattr(tl, 'FORECASTS', {}):
        return draw.forecast(tl, tl.FORECASTS[shot], rt)
    return _card(tl, shot, rt)


def paint(tl, shot, rt, img):
    if shot in getattr(tl, 'MAPS', {}):
        from modelos.weather import draw
        img = draw.map_layer(img, tl.MAPS[shot], rt)
    return _paint(tl, shot, rt, img)
