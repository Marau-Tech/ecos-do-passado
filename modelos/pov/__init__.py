"""Modelo POV histórico do Ecos do Passado: relato em primeira pessoa num lugar e data reais, em português.

Regras do roteiro em modelos/pov/GUIA.md.
"""
from modelos.base import *

__all__ = ['FPS_SRC', 'FPS_OUT', 'END_SECS', 'END_TEXT', 'END_TONE', 'MIN_SECS', 'MAX_SECS', 'timing', 'base_events']

MIN_SECS, MAX_SECS = 30, 60
END_SECS = 1.5
END_TEXT = 'ECOS DO PASSADO'
END_TONE = False                # tela final em silêncio, sem o tom de alerta do EAS


def timing(shots, end_card=None, min_secs=None, max_secs=None):
    """Faixa padrão de 30 a 60s; um episódio longo passa a sua (Sarajevo usa 175 a 180s)."""
    lo = MIN_SECS if min_secs is None else min_secs
    hi = MAX_SECS if max_secs is None else max_secs
    return bounded(shots, END_SECS if end_card is None else end_card, lo, hi, 'pov')


def base_events(shots, start):
    """Glitches de todo vídeo: um leve em cada corte."""
    return [(start[name], 0.45, 0.13) for name, _, _ in shots[1:]]


def counter(tl, t):
    """Data e hora do relato no OSD; cada take pode ter seu horário em CLOCK, que anda com o tempo."""
    shot = shot_of(tl, t)
    s = int(tl.CLOCK[shot] + (t - tl.START[shot]))
    return f'{tl.STAMP} {s // 3600 % 24:02d}:{s % 3600 // 60:02d}'


def title(tl, shot):
    """Lugar e data na barra de cima, só no take que abre o vídeo."""
    return (tl.PLACE, tl.DATE) if shot == tl.SHOTS[0][0] else None


def opens_section(tl, shot):
    return shot == tl.SHOTS[0][0]


def scene_module(tl, shot):
    """Arquivo de videos/<video>/ com build_<take>(); o timeline diz em SCENE_OF."""
    return tl.SCENE_OF[shot]
