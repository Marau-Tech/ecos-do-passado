"""Modelo survive: algo no centro com vida, um perigo que tira, aliados que vêm das bordas para trazer,
e no escuro, fora do lugar seguro, alguma coisa que chega mais perto quando a vida cai. Parece um jogo, e o espectador torce.

A mecânica fica em sim.py e não sabe o que cada coisa é. A skin diz (skins/campfire.py: fogueira, chuva e brasas).
Todo take é desenhado em 2D, sem Blender. O fim muda de vídeo para vídeo. Regras em modelos/survive/GUIA.md.
"""
from modelos.base import *

__all__ = ['FPS_SRC', 'FPS_OUT', 'END_TEXT', 'END_TONE', 'MIN_SECS', 'MAX_SECS', 'timing']

LOOK = 'vhs'
REC_DOT = False
MIN_SECS, MAX_SECS = 25, 60
END_TEXT = ''
END_TONE = False


def timing(shots, end_card=0.0):
    if any(caps for _, _, caps in shots):
        raise ValueError('O modelo survive não tem legenda: o texto fica no título e no placar')
    return bounded(shots, end_card, MIN_SECS, MAX_SECS, 'survive')


def rec_label(tl, shot):
    return None


def footer(tl, shot, t, frame):
    return None


def title(tl, shot):
    """TITLE do timeline, ou TITLES[take] quando o take troca o título, como no fim."""
    return getattr(tl, 'TITLES', {}).get(shot, tl.TITLE)


def drawn(tl, shot):
    return True


def prepare(tl):
    from modelos.survive import draw
    draw.prepare(tl)


def card(tl, shot, rt):
    from modelos.survive import draw
    return draw.world(tl.START[shot] + rt)


def hud(tl, img, t, y0):
    from modelos.survive import draw
    draw.hud(tl, img, t, y0)
