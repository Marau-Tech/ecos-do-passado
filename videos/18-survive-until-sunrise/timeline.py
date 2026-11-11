# (take, duração, legendas): este modelo não tem legenda; o texto fica no título e no placar
from modelos import survive as MODELO
from modelos.survive import *

SKIN = 'campfire'                       # fogueira, chuva e brasas: modelos/survive/skins/campfire.py
SEED = 118                              # cai abaixo de 10% aos 30s e chega ao nascer do sol com 2,8%
SHOTS = [('night', 36.0, []), ('dawn', 4.0, [])]
TOTAL, START, END_CARD = timing(SHOTS)

TITLE = ('KEEP THE FIRE ALIVE', 'UNTIL SUNRISE')
TITLES = {'dawn': ('SUNRISE.', '')}

# o fim deste vídeo: o dia nasce, as figuras vão embora, e uma fica do lado do fogo
SKIN_CFG = dict(stand=[dict(at=38.6, dx=108, h=205, lean=-0.05)])

EVENTS = [(24.3, 0.35, 0.12), (28.9, 0.35, 0.12), (31.6, 0.35, 0.12)]     # o relâmpago estoura a fita
SUBLIM = []
SUBLIM_GRADE = None
GRADE = {}


def frame_fx(a, shot, rt):
    return a
