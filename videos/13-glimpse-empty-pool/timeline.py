# (take, duração, legendas): este modelo não tem legenda
from modelos import glimpse as MODELO
from modelos.glimpse import *
import numpy as np

LOOK = 'cctv'
SHOTS = [('a', 12.0, [])]
TOTAL, START, END_CARD = timing(SHOTS)

STAMP = '2011-08-02'
CLOCK = 3 * 3600 + 7 * 60 + 41
STEP_T0, STEP_DT, STEPS = 2.0, 1.0, 7     # uma pegada molhada por segundo, da água até a câmera
RESET = 9.3                               # glitch: as pegadas somem e a água se agita
RINGS = (0.0, 0.5, 1.0)                   # ondas saem do meio da piscina, depois de RESET

EVENTS = [(RESET - 0.1, 0.7, 0.25)]
SUBLIM = []
SUBLIM_GRADE = 'cam'

GRADE = {'cam': (0.0, 1.05, (0.95, 1.0, 1.02), 0.02)}

def frame_fx(a, shot, rt):
    return np.clip(a, 0, 1) ** 0.85
