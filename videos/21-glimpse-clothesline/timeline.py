# (take, duração, legendas): este modelo não tem legenda
from modelos import glimpse as MODELO
from modelos.glimpse import *
import math
import numpy as np

LOOK = 'vhs'
SHOTS = [('a', 12.0, [])]
TOTAL, START, END_CARD = timing(SHOTS)

STAMP = '1998-06-12'
CLOCK = 23 * 3600 + 41 * 60 + 5
LIGHT_ON, LIGHT_OFF = 3.5, 9.0  # o holofote de movimento acende e apaga; os pés só aparecem com a luz
LOOP_T = 12.0                   # período do vento e dos lençóis: o fim emenda no começo


def gust(t):
    """força do vento, 0..1, com período de 12s; mais forte no meio, quando a luz está acesa"""
    return 0.4 + 0.6 * (0.5 - 0.5 * math.cos(2 * math.pi * (t - 0.25) / LOOP_T))


EVENTS = [(LIGHT_OFF - 0.1, 0.7, 0.25)]
SUBLIM = []
SUBLIM_GRADE = 'cam'

GRADE = {'cam': (0.8, 1.05, (0.95, 0.98, 1.06), 0.02)}

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1. Ganho automático da câmera no escuro."""
    return np.clip(a, 0, 1) ** 0.8
