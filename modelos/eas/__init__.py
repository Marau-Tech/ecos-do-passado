"""Modelo alerta de emergência: a programação é cortada por um alerta do EAS cujas instruções ficam específicas demais.

Regras do roteiro em modelos/eas/GUIA.md.
"""
from modelos.base import *
from modelos.base import drawn as _drawn, card as _card

__all__ = ['FPS_SRC', 'FPS_OUT', 'END_SECS', 'END_TEXT', 'MIN_SECS', 'MAX_SECS', 'ALERT_STYLE', 'timing']

LOOK = 'broadcast'
REC_DOT = False
MIN_SECS, MAX_SECS = 25, 75
END_SECS = 1.5
END_TEXT = 'END OF MESSAGE'
ALERT_STYLE = {                 # padrão de cada tela de alerta; ALERTS[take] sobrescreve
    'style': 'red',             # red, blue, black ou bars
    'head': 'EMERGENCY ALERT SYSTEM',
    'lines': (),
    'crawl': '',
}


def timing(shots, end_card=None):
    return bounded(shots, END_SECS if end_card is None else end_card, MIN_SECS, MAX_SECS, 'eas')


def rec_label(tl, shot):
    return tl.STATION


def counter(tl, t):
    s = int(tl.CLOCK + t)
    h = s // 3600 % 24
    return f'{(h - 1) % 12 + 1}:{s % 3600 // 60:02d} {"AM" if h < 12 else "PM"}'


def footer(tl, shot, t, frame):
    return None


def title(tl, shot):
    """HEADLINE nas telas de alerta, menos nas barras de cor. TITLES[take] muda um take, e None tira o título."""
    alert = shot in tl.ALERTS and tl.ALERTS[shot].get('style', tl.ALERT_STYLE['style']) != 'bars'
    return getattr(tl, 'TITLES', {}).get(shot, tl.HEADLINE if alert else None)


def grade_key(tl, shot):
    return shot if shot in tl.GRADE else 'scene'


def scene_module(tl, shot):
    return 'scene'


def drawn(tl, shot):
    return shot in tl.ALERTS or _drawn(tl, shot)


def card(tl, shot, rt):
    if shot in tl.ALERTS:
        from modelos.eas import draw
        return draw.alert({**tl.ALERT_STYLE, **tl.ALERTS[shot]}, rt)
    return _card(tl, shot, rt)
