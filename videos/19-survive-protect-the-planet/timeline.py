# (take, duração, legendas): este modelo não tem legenda; o texto fica no título e no placar
from modelos import survive as MODELO
from modelos.survive import *

SKIN = 'planet'                         # planeta com escudo, meteoros e esferas: modelos/survive/skins/planet.py
SEED = 284                              # cai a 2,3% aos 32,37s, uma esfera salva no frame seguinte, termina com 4,5%
SHOTS = [('storm', 36.0, []), ('calm', 5.5, []), ('twist', 4.5, [])]
TOTAL, START, END_CARD = timing(SHOTS)

TITLE = ('PROTECT THE PLANET', 'UNTIL THE STORM ENDS')
TITLES = {'calm': ('IT SURVIVED.', ''), 'twist': ('THE METEORS WERE', 'TRYING TO STOP IT.')}

# a virada: o planeta racha e abre um olho. glimpse: o olho aparece num frame só, no pior momento
SKIN_CFG = dict(hatch=dict(at=37.5, open=39.5), glimpse=[32.33])

EVENTS = [(32.3, 0.5, 0.12), (39.5, 0.4, 0.2)]      # a fita falha no frame do olho e quando ele abre
SUBLIM = []
SUBLIM_GRADE = None
GRADE = {}


def frame_fx(a, shot, rt):
    return a
