"""Modelo "Pick one": duas opções ruins, um trecho curto para cada e a tela final "PICK.".

Regras do roteiro em modelos/binary/GUIA.md.
"""
from modelos.base import *
from modelos.base import labels as _labels

__all__ = ['FPS_SRC', 'FPS_OUT', 'NAME_HOLD', 'END_SECS', 'END_TEXT', 'INTRO_LABELS', 'STAKE_SECS',
           'MIN_SECS', 'MAX_SECS', 'timing', 'base_events']

NAME_HOLD = 1.5                 # opção parada enquanto o narrador diz o nome, antes do zoom
END_SECS = 0.7                  # tela final
END_TEXT = 'PICK.'
STAKE_SECS = 24 * 3600          # tempo do contador; o timeline pode trocar (uma noite = 8 * 3600)
MIN_SECS, MAX_SECS = 20, 35
INTRO_LABELS = [((150, 330), 'A'), ((810, 330), 'B')]


def timing(shots, end_card=None):
    return bounded(shots, END_SECS if end_card is None else end_card, MIN_SECS, MAX_SECS, 'binary')


def base_events(shots, options, start):
    """Glitches de todo vídeo: um leve em cada corte e um forte na abertura de cada opção."""
    ev = [(start[name], 0.45, 0.13) for name, _, _ in shots[1:]]
    return ev + [(start[sh], 1.0, 0.28) for _, _, sh in options]


def _option(tl, shot):
    for i, (_, _, first) in enumerate(tl.OPTIONS):
        if shot[0] == first[0]:
            return i
    return None


def counter(tl, t):
    firsts = [tl.START[sh] for _, _, sh in tl.OPTIONS] + [tl.END_CARD]
    cd = tl.STAKE_SECS
    for a, b in zip(firsts, firsts[1:]):
        if a <= t < b:
            cd = int(tl.STAKE_SECS * (1 - (t - a) / (b - a)))
    if t >= tl.END_CARD:
        cd = 0
    return f'T-{cd // 3600:02d}:{cd % 3600 // 60:02d}:{cd % 60:02d}'


def title(tl, shot):
    i = None if shot == 'intro' else _option(tl, shot)
    return None if i is None else tl.OPTIONS[i][:2]


def opens_section(tl, shot):
    return any(shot == sh for _, _, sh in tl.OPTIONS)


def big_caption(tl, shot):
    return shot == 'intro'


def labels(tl, shot):
    return tl.INTRO_LABELS if shot == 'intro' else _labels(tl, shot)


def grade_key(tl, shot):
    return 'intro' if shot == 'intro' else shot[0]


def scene_module(tl, shot):
    return 'intro' if shot == 'intro' else shot[0]
