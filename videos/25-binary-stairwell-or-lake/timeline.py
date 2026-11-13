# (take, duração, legendas [(início, fim, texto)])
from modelos import binary as MODELO
from modelos.binary import *

SHOTS = [
 ('intro', 4.0, [(0.3, 4.0, 'Pick one. You spend one night there.')]),
 ('a1', 4.5, [(NAME_HOLD + 0.6, 4.5, 'The stairs only go down.')]),
 ('a2', 4.0, [(0.2, 4.0, 'The lights follow you.')]),
 ('a3', 4.5, [(0.1, 2.2, 'Stop walking, they go out.'), (2.2, 4.5, 'Dawn is eight hours away.')]),
 ('b1', 4.5, [(NAME_HOLD + 0.6, 4.5, 'A cabin on a frozen lake.')]),
 ('b2', 4.0, [(0.2, 4.0, 'The ice is a meter thick.')]),
 ('b3', 5.2, [(0.1, 2.2, 'Something knocks from below.'), (2.2, 4.5, 'Once every hour.')]),
]
OPTIONS = [('OPTION A', 'THE STAIRWELL', 'a1'), ('OPTION B', 'THE LAKE', 'b1')]
STAKE_SECS = 8 * 3600           # uma noite
TOTAL, START, END_CARD = timing(SHOTS)

TURN = 2.2                      # a chave no a3 e no b3: a luz morre, a tábua pula
LIGHT_ON, LIGHT_OFF = 1.5, 2.4  # a2: a luz de baixo acende quando você chega, a de cima apaga
FLOOR = 'B-212'                 # placa do patamar no a3

EVENTS = base_events(SHOTS, OPTIONS, START)
EVENTS += [(START['a3'] + TURN, 0.5, 0.15),
           (START['b3'] + TURN, 0.6, 0.18),
           (END_CARD - 0.25, 1.0, 0.33)]
SUBLIM = []
SUBLIM_GRADE = 'a'

VOICE = {
    'voice': 'bm_lewis', 'lang': 'en-gb', 'speed': 0.95,
    'name_at': 0.15,
    'names': {'a1': 'Option A. The stairwell.', 'b1': 'Option B. The lake.'},
}

GRADE = {  # saturação, contraste, tint RGB, lift
 'intro': (0.9, 1.05, (1.0, 0.98, 1.0), 0.02),
 'a': (0.7, 1.08, (0.96, 1.04, 0.92), 0.02),
 'b': (0.85, 1.05, (0.94, 0.98, 1.08), 0.03),
}

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    return a
