# (take, duração, legendas [(início, fim, texto)])
from modelos import binary as MODELO
from modelos.binary import *

SHOTS = [
 ('intro', 4.0, [(0.3, 4.0, 'Pick one. Each has its own clock.')]),
 ('a1', 4.5, [(NAME_HOLD + 0.6, 4.5, 'Time runs slow here.')]),
 ('a2', 4.0, [(0.2, 4.0, 'You stay for one day.')]),
 ('a3', 4.5, [(0.1, 2.2, 'At home, forty years pass.'), (2.2, 4.5, 'Someone else lives in your house.')]),
 ('b1', 4.5, [(NAME_HOLD + 0.6, 4.5, 'Time runs fast here.')]),
 ('b2', 4.0, [(0.2, 4.0, 'Your body only feels one day.')]),
 ('b3', 5.2, [(0.1, 2.2, 'Your mind lives forty years.'), (2.2, 4.5, 'Alone.')]),
]
OPTIONS = [('OPTION A', 'THE SLOW PLANET', 'a1'), ('OPTION B', 'THE FAST PLANET', 'b1')]
DRAWN = ['a3', 'b3']            # o visor de data e a parede riscada
TOTAL, START, END_CARD = timing(SHOTS)

TURN = 2.2                      # a chave no a3 e no b3: o ano trava, os riscos param
YEAR0, YEAR1 = 1996, 2036
DAY = 1.0                       # um dia do planeta rápido, em segundos de vídeo
SEASON = 2.0                    # as plantas nascem e secam nesse tempo
SPIN = 1.2                      # uma volta do planeta rápido na órbita

EVENTS = base_events(SHOTS, OPTIONS, START)
EVENTS += [(START['a3'] + TURN, 0.5, 0.15),
           (START['b3'] + TURN, 0.5, 0.15),
           (END_CARD - 0.25, 1.0, 0.33)]
SUBLIM = []
SUBLIM_GRADE = 'a'

VOICE = {
    'voice': 'bm_lewis', 'lang': 'en-gb', 'speed': 0.95,
    'name_at': 0.1,
    'names': {'a1': 'Option A. The slow planet.', 'b1': 'Option B. The fast planet.'},
}

GRADE = {  # saturação, contraste, tint RGB, lift
 'intro': (0.95, 1.05, (1.0, 0.98, 1.0), 0.02),
 'a': (0.85, 1.06, (1.06, 0.98, 0.9), 0.03),
 'b': (1.0, 1.04, (0.97, 1.0, 1.04), 0.03),
}

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    return a
