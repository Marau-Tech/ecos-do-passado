# (take, duração, legendas [(início, fim, texto)])
from modelos import binary as MODELO
from modelos.binary import *

SHOTS = [
 ('intro', 4.0, [(0.3, 4.0, 'Pick one. You spend one night there.')]),
 ('a1', 4.5, [(NAME_HOLD + 0.6, 4.5, 'No sound exists on this planet.')]),
 ('a2', 4.0, [(0.2, 4.0, "You can't hear your own steps.")]),
 ('a3', 4.5, [(0.1, 2.2, 'You can only hear breathing.'), (2.2, 4.5, "It isn't yours.")]),
 ('b1', 4.5, [(NAME_HOLD + 0.6, 4.5, 'Everyone here is friendly.')]),
 ('b2', 4.0, [(0.2, 4.0, 'They wave from every window.')]),
 ('b3', 5.2, [(0.1, 2.2, 'They are so happy you came.'), (2.2, 4.5, 'Nobody else ever leaves.')]),
]
OPTIONS = [('OPTION A', 'THE QUIET PLANET', 'a1'), ('OPTION B', 'THE FRIENDLY PLANET', 'b1')]
STAKE_SECS = 8 * 3600           # uma noite
TOTAL, START, END_CARD = timing(SHOTS)

BREATH = 0.32                   # respirações por segundo no visor
FOG_FROM = 0.4                  # o visor começa a embaçar, em segundos dentro do a3

EVENTS = base_events(SHOTS, OPTIONS, START)
EVENTS += [(START['a3'] + 2.2, 0.5, 0.15),          # não é sua
           (START['b3'] + 2.2, 0.5, 0.15),
           (END_CARD - 0.25, 1.0, 0.33)]
SUBLIM = []
SUBLIM_GRADE = 'a'

VOICE = {
    'voice': 'bm_lewis', 'lang': 'en-gb', 'speed': 0.95,
    'name_at': 0.15,
    'names': {'a1': 'Option A. The quiet planet.', 'b1': 'Option B. The friendly planet.'},
}

GRADE = {  # saturação, contraste, tint RGB, lift
 'intro': (0.9, 1.05, (1.0, 0.98, 1.0), 0.02),
 'a': (0.25, 1.08, (0.98, 1.0, 1.02), 0.03),
 'b': (1.05, 1.02, (1.06, 0.98, 1.0), 0.03),
}

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    return a
