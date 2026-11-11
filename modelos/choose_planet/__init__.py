"""Modelo "Choose one": intro com 4 planetas, um trecho por planeta e tela final.

Regras do roteiro em modelos/choose_planet/GUIA.md.
"""
from modelos.base import FPS_OUT, FPS_SRC, LOOK, REC_DOT, footer, labels as _labels, rec_label, timing, drawn, card, paint, prepare, hud

__all__ = ['FPS_SRC', 'FPS_OUT', 'NAME_HOLD', 'SECTION', 'END_SECS', 'END_TEXT', 'INTRO_LABELS',
           'timing', 'base_events']

NAME_HOLD = 2.25                # planeta girando enquanto o narrador diz o nome, antes do zoom
SECTION = 15.0 + NAME_HOLD      # duração de cada trecho, usada no contador
END_SECS = 0.7                  # tela final
END_TEXT = 'CHOOSE.'
INTRO_LABELS = [((88, 228), '1'), ((872, 212), '2'), ((96, 492), '3'), ((880, 482), '4')]


def base_events(shots, planets, start):
    """Glitches de todo vídeo: um leve em cada corte e um forte na abertura de cada planeta."""
    ev = [(start[name], 0.45, 0.13) for name, _, _ in shots[1:]]
    return ev + [(start[sh], 1.0, 0.28) for _, _, sh in planets]


def counter(tl, t):
    first, last = tl.PLANETS[0][2], tl.PLANETS[-1][2]
    if t < tl.START[first]:
        cd = 24 * 3600
    else:
        k = min(1.0, ((t - tl.START[first]) % tl.SECTION) / tl.SECTION)
        if t >= tl.START[last]:
            k = min(1.0, (t - tl.START[last]) / (tl.END_CARD - tl.START[last]))
        cd = int(24 * 3600 * (1 - k))
    return f'T-{cd // 3600:02d}:{cd % 3600 // 60:02d}:{cd % 60:02d}'


def title(tl, shot):
    if shot == 'intro':
        return None
    a, b, _ = tl.PLANETS[int(shot[1]) - 1]
    return a, b


def opens_section(tl, shot):
    return any(shot == sh for _, _, sh in tl.PLANETS)


def big_caption(tl, shot):
    return shot == 'intro'


def labels(tl, shot):
    return tl.INTRO_LABELS if shot == 'intro' else _labels(tl, shot)


def grade_key(tl, shot):
    return 'intro' if shot == 'intro' else shot[:2]


def scene_module(tl, shot):
    return 'intro' if shot == 'intro' else shot[:2]
