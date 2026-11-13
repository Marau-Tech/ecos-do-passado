# (take, duração, legendas): este modelo não tem legenda
from modelos import glimpse as MODELO
from modelos.glimpse import *
import numpy as np

SHOTS = [('a', 12.0, [])]
TOTAL, START, END_CARD = timing(SHOTS)

STAMP = '2006-01-09'
CLOCK = 21 * 3600 + 58 * 60 + 30
OFF = (2.0, 4.5, 7.0, 9.5)      # as faixas de luz apagam do fundo (4) para a frente (1)
SPOT = (18.0, 12.5, 7.5)        # onde a silhueta está parada depois de cada faixa apagar, em y
BACK = 9.7                      # glitch: todas as luzes voltam e o andar fica vazio

EVENTS = [(BACK - 0.02, 0.75, 0.3)]
SUBLIM = []
SUBLIM_GRADE = 'cam'

GRADE = {'cam': (0.8, 1.04, (0.95, 1.02, 0.98), 0.0)}

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1. Ganho leve da webcam."""
    return np.clip(a, 0, 1) ** 0.85
