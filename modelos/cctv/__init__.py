"""Modelo câmera de segurança: sem narrador e sem legenda, com a história contada pela imagem.

Regras do roteiro em modelos/cctv/GUIA.md.
"""
from modelos.base import FPS_OUT, FPS_SRC, labels, opens_section, big_caption, timing as _timing

__all__ = ['FPS_SRC', 'FPS_OUT', 'END_SECS', 'END_TEXT', 'MIN_SECS', 'MAX_SECS', 'timing']

LOOK = 'cctv'
MIN_SECS, MAX_SECS = 40, 120
END_SECS = 2.0                  # tela final
END_TEXT = 'NO SIGNAL'


def timing(shots, end_card=None):
    """Como o timing da base, mas recusa vídeo fora da duração do modelo."""
    total, start, end = _timing(shots, END_SECS if end_card is None else end_card)
    if not MIN_SECS <= total <= MAX_SECS:
        raise ValueError(f'O vídeo tem {total}s, e o modelo cctv pede de {MIN_SECS} a {MAX_SECS}s')
    return total, start, end


def rec_label(tl, shot):
    return tl.CAMS[shot][0]


def counter(tl, t):
    s = int(tl.CLOCK + t)
    return f'{tl.DATE}  {s // 3600 % 24:02d}:{s % 3600 // 60:02d}:{s % 60:02d}'


def footer(tl, shot, t, frame):
    return None


def title(tl, shot):
    return tl.CAMS[shot]


def grade_key(tl, shot):
    return 'cam'


def scene_module(tl, shot):
    return 'scene'
