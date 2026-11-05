"""Modelo transmissão de sonda: imagens chegando linha a linha, com telemetria, até a perda de sinal.

Regras do roteiro em modelos/probe_feed/GUIA.md.
"""
from modelos.base import *
from modelos.base import drawn as _drawn, card as _card, paint as _paint

__all__ = ['FPS_SRC', 'FPS_OUT', 'END_SECS', 'END_TEXT', 'END_TONE', 'MIN_SECS', 'MAX_SECS', 'REVEAL_AT', 'REVEAL_SECS',
           'timing', 'images']

LOOK = 'probe'
MIN_SECS, MAX_SECS = 30, 60
END_SECS = 2.0
END_TEXT = 'LOSS OF SIGNAL'
END_TONE = False                # a tela final fica só com o chiado, sem o tom de alerta
REVEAL_AT, REVEAL_SECS = 0.3, 3.5    # a imagem começa a chegar em REVEAL_AT e leva REVEAL_SECS


def timing(shots, end_card=None):
    return bounded(shots, END_SECS if end_card is None else end_card, MIN_SECS, MAX_SECS, 'probe_feed')


def images(shots):
    """Takes de imagem, em ordem: os que começam com i."""
    return [s[0] for s in shots if s[0][0] == 'i']


def reveal(tl, shot):
    """(início, duração) da chegada da imagem no take."""
    return getattr(tl, 'REVEAL', {}).get(shot, (tl.REVEAL_AT, tl.REVEAL_SECS))


def rec_label(tl, shot):
    return 'RX'


def counter(tl, t):
    ims = images(tl.SHOTS)
    shot = shot_of(tl, t)
    k = ims.index(shot) + 1 if shot in ims else sum(tl.START[s] <= t for s in ims)
    return f'IMG {k:02d}/{len(ims):02d}'


def footer(tl, shot, t, frame):
    a, b = tl.SIGNAL
    u = min(1.0, t / tl.END_CARD)
    sig = a + (b - a) * u ** 1.6 + (frame % 7 - 3) * 0.3
    ber = 10 ** (-6 + 4 * u ** 2)
    return f'{sig:5.1f} dBm  BER {ber:.0e}'


def title(tl, shot):
    if shot == 'head':
        return 'DOWNLINK', tl.PROBE
    ims = images(tl.SHOTS)
    if shot in ims:
        return f'IMAGE {ims.index(shot) + 1:02d}', getattr(tl, 'SUBTITLES', {}).get(shot, tl.TARGET)
    return getattr(tl, 'TITLES', {}).get(shot)


def opens_section(tl, shot):
    return shot in images(tl.SHOTS)


def grade_key(tl, shot):
    return shot if shot in tl.GRADE else 'img'


def scene_module(tl, shot):
    return 'scene'


def drawn(tl, shot):
    return shot == 'head' or _drawn(tl, shot)


def card(tl, shot, rt):
    if shot == 'head':
        from modelos.probe_feed import draw
        return draw.header(tl, rt)
    return _card(tl, shot, rt)


def paint(tl, shot, rt, img):
    if shot in images(tl.SHOTS):
        from modelos.probe_feed import draw
        at, secs = reveal(tl, shot)
        img = draw.reveal(img, (rt - at) / secs, rt)
    return _paint(tl, shot, rt, img)
