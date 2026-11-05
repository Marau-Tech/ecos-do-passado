# (take, duração, legendas): este modelo não tem legenda
from modelos import glimpse as MODELO
from modelos.glimpse import *
import numpy as np

SHOTS = [('a', 10.0, [])]
TOTAL, START, END_CARD = timing(SHOTS)

STAMP = '2004-03-17'
CLOCK = 3 * 3600 + 14 * 60 + 7
GONE = 6.5                      # o rosto some da fresta da porta; no loop ele volta

EVENTS = [(GONE - 0.1, 0.7, 0.25)]
SUBLIM = []
SUBLIM_GRADE = 'cam'

GRADE = {'cam': (0.9, 1.0, (0.92, 0.97, 1.08), 0.0)}

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1. Ganho da webcam no escuro."""
    return np.clip(a, 0, 1) ** 0.6
