# (shot, duração, legendas): este modelo não tem legenda
from modelos import cctv as MODELO
from modelos.cctv import *

SHOTS = [
 ('a1', 6.0, []), ('a2', 10.0, []), ('a3', 8.0, []),
 ('c1', 10.0, []),
 ('a4', 10.0, []),
 ('c2', 10.0, []), ('c3', 8.0, []),
 ('a5', 8.0, []), ('a6', 6.0, []),
]
TOTAL, START, END_CARD = timing(SHOTS)
PREP = ['prep']                 # texturas das telas, antes dos takes

WIDE = ('CAM 04', 'FLOOR 3 - OPEN OFFICE')
CLOSE = ('CAM 02', 'FLOOR 3 - ROW B')
DESK = ('CAM 03', 'FLOOR 3 - DESK 14')
CAMS = {s[0]: (CLOSE if s[0][0] == 'c' else WIDE) for s in SHOTS}
CAMS['c3'] = DESK
CLOCK = 2 * 3600 + 47 * 60 + 13
DATE = 'NOV 05 2026'

FLICKERS = (0.6, 2.4, 4.6, 6.4, 8.2)        # luzes do teto, em segundos dentro do a4
TYPE_AT, TYPE_STEP = 2.0, 0.45              # texto da tela no c2
MESSAGE = "HE'S\nCOMING"

# glitch só nos acontecimentos: (tempo global, força, duração)
EVENTS = [(START['a1'] + 3.0, 0.25, 0.12), (START['a3'], 0.5, 0.2)]
EVENTS += [(START['a4'] + f, 0.4, 0.15) for f in FLICKERS]
EVENTS += [(START['c2'] + TYPE_AT + TYPE_STEP * len(MESSAGE), 0.5, 0.25),
           (START['c3'], 0.9, 0.35), (START['c3'] + 4.0, 0.6, 0.2),
           (END_CARD - 0.4, 1.0, 0.4)]
SUBLIM = []
SUBLIM_GRADE = 'cam'

GRADE = {'cam': (0.0, 1.12, (1.0, 1.0, 1.0), 0.0)}  # saturação, contraste, tint RGB, lift

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    return a ** 0.6             # ganho da câmera no escuro
