"""Modelo vislumbre: de 6 a 15s, sem texto e sem voz, que termina onde começa para rodar em loop.

Regras do roteiro em modelos/glimpse/GUIA.md.
"""
from modelos.base import *

__all__ = ['FPS_SRC', 'FPS_OUT', 'END_SECS', 'END_TEXT', 'END_TONE', 'LOOP', 'MIN_SECS', 'MAX_SECS', 'timing']

LOOK = 'webcam'
REC_DOT = False
MIN_SECS, MAX_SECS = 6, 15
END_SECS = 0.0                  # sem tela final: o vídeo emenda no começo
END_TEXT = ''
END_TONE = False
LOOP = True


def timing(shots, end_card=None):
    if any(caps for _, _, caps in shots):
        raise ValueError('O modelo glimpse não tem legenda')
    return bounded(shots, 0.0, MIN_SECS, MAX_SECS, 'glimpse')


def rec_label(tl, shot):
    return None


def footer(tl, shot, t, frame):
    """Carimbo de data da câmera. Sem STAMP no timeline, nada."""
    if not getattr(tl, 'STAMP', None):
        return None
    s = int(tl.CLOCK + t)
    return f'{tl.STAMP} {s // 3600 % 24:02d}:{s % 3600 // 60:02d}:{s % 60:02d}'


def grade_key(tl, shot):
    return 'cam'


def scene_module(tl, shot):
    return 'scene'
