# (take, duração, legendas): este modelo não tem legenda
from modelos import glimpse as MODELO
from modelos.glimpse import *
import numpy as np

LOOK = 'vhs'
SHOTS = [('a', 12.0, [])]
TOTAL, START, END_CARD = timing(SHOTS)

STAMP = '1996-10-04'
CLOCK = 17 * 3600 + 52 * 60 + 9
PERIOD = 3.0                    # balanço do meio: 4 idas e voltas em 12s, o loop emenda no mesmo ponto do arco
SWING = 24.0                    # amplitude em graus
SEEN = (7.85, 8.05)             # a criança aparece só nesses frames, dentro do glitch

EVENTS = [(7.8, 0.6, 0.3)]
SUBLIM = []
SUBLIM_GRADE = 'cam'

GRADE = {'cam': (0.85, 1.05, (1.04, 0.98, 0.9), 0.02)}

def frame_fx(a, shot, rt):
    return np.clip(a, 0, 1) ** 0.95
