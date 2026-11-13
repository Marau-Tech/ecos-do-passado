# (take, duração, legendas [(início, fim, texto)])
from modelos import binary as MODELO
from modelos.binary import *

SHOTS = [
 ('intro', 4.0, [(0.3, 4.0, 'Pick one. You stay for 24 hours.')]),
 ('a1', 4.5, [(NAME_HOLD + 0.7, 4.5, 'Gravity here is triple ours.')]),
 ('a2', 4.0, [(0.2, 4.0, "You can't stand up.")]),
 ('a3', 4.5, [(0.1, 2.2, 'You crawl to the shelter.'), (2.2, 4.5, "It's 24 hours away.")]),
 ('b1', 4.5, [(NAME_HOLD + 0.7, 4.5, 'Gravity here is almost zero.')]),
 ('b2', 4.0, [(0.2, 4.0, 'One jump, and you never land.')]),
 ('b3', 5.2, [(0.1, 2.2, 'A rope ties you to the ground.'), (2.2, 4.5, "It's fraying.")]),
]
OPTIONS = [('OPTION A', 'THE HEAVY PLANET', 'a1'), ('OPTION B', 'THE LIGHT PLANET', 'b1')]
TOTAL, START, END_CARD = timing(SHOTS)

TURN = 2.2                      # a chave no a3 e no b3: o outro rastro aparece, o fio da corda arrebenta
FLAT = 0.78                     # achatamento do planeta pesado nos polos
ORBIT = 6.0                     # uma volta das pedras em torno do planeta leve, em segundos

EVENTS = base_events(SHOTS, OPTIONS, START)
EVENTS += [(START['a3'] + TURN, 0.5, 0.15),
           (START['b3'] + TURN, 0.5, 0.15),
           (END_CARD - 0.25, 1.0, 0.33)]
SUBLIM = []
SUBLIM_GRADE = 'a'

VOICE = {
    'voice': 'bm_lewis', 'lang': 'en-gb', 'speed': 0.95,
    'name_at': 0.1,
    'names': {'a1': 'Option A. The heavy planet.', 'b1': 'Option B. The light planet.'},
}

GRADE = {  # saturação, contraste, tint RGB, lift
 'intro': (0.95, 1.05, (1.0, 0.98, 1.0), 0.02),
 'a': (0.9, 1.1, (1.07, 0.97, 0.88), 0.03),
 'b': (0.85, 1.04, (0.95, 1.0, 1.07), 0.03),
}

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    return a
