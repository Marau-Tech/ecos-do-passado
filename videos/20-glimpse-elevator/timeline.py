# (take, duração, legendas): este modelo não tem legenda
from modelos import glimpse as MODELO
from modelos.glimpse import *
import numpy as np

LOOK = 'cctv'
SHOTS = [('a', 12.0, [])]
TOTAL, START, END_CARD = timing(SHOTS)

STAMP = '2009-11-21'
CLOCK = 2 * 3600 + 47 * 60 + 13
OPEN = (3.0, 3.8)               # ding: as portas abrem para o corredor escuro
CLOSE = (8.0, 9.2)              # as portas fecham, sem ninguém ter entrado
SEEN = (9.2, 11.45)             # a figura parada no reflexo das portas fechadas; some no glitch

EVENTS = [(11.35, 0.7, 0.3)]
SUBLIM = []
SUBLIM_GRADE = 'cam'

GRADE = {'cam': (0.0, 1.05, (1.0, 1.0, 1.0), 0.02)}

def frame_fx(a, shot, rt):
    return np.clip(a, 0, 1) ** 0.85
