# (shot, duração, legendas [(início, fim, texto)])
from modelos import choose_planet as MODELO
from modelos.choose_planet import *
SHOTS = [
 ('intro', 5.0,  [(0.3, 5.0, 'Choose one. You stay for 24 hours.')]),
 ('p1a', 6.0, [(NAME_HOLD + 0.5, 6.0, 'A white desert under a mirror sky.')]),
 ('p1b', 3.75, [(0.2, 3.75, 'The ground is a perfect reflection.')]),
 ('p1c', 3.5,  [(0.2, 3.5,  'Your footprints are already there. Ahead of you.')]),
 ('p1d', 4.0,  [(0.1, 2.1,  'They walk to the horizon.'), (2.1, 4.0, 'None of them walk back.')]),
 ('p2a', 5.75, [(NAME_HOLD + 0.5, 5.75, 'One street. Forty identical houses.')]),
 ('p2b', 4.0,  [(0.2, 4.0,  'Every window is lit. Every table is set.')]),
 ('p2c', 3.5,  [(0.2, 3.5,  'One mailbox has your name on it.')]),
 ('p2d', 4.0,  [(0.1, 2.0,  'The porch light turns on.'), (2.0, 4.0, 'Someone was expecting you.')]),
 ('p3a', 6.0, [(NAME_HOLD + 0.5, 6.0, 'A blizzard. Zero visibility.')]),
 ('p3b', 3.75, [(0.2, 3.75, 'You build a fire. It is the only light.')]),
 ('p3c', 3.5,  [(0.2, 3.5,  'Something knocks. From inside the snow.')]),
 ('p3d', 4.0,  [(0.1, 1.9,  'It knocks again.'), (1.9, 4.0, 'Now from inside the fire.')]),
 ('p4a', 6.25, [(NAME_HOLD + 0.5, 6.25, 'Two suns. One of them is not a sun.')]),
 ('p4b', 3.5,  [(0.2, 3.5,  'It has been getting closer since you landed.')]),
 ('p4c', 3.75, [(0.2, 3.75, 'It blinks.')]),
 ('p4d', 3.75, [(0.1, 2.0,  'At hour 24, it lands.'), (2.0, 3.05, 'And opens.')]),
]
PLANETS = [('PLANET 1', 'THE SALT', 'p1a'), ('PLANET 2', 'THE CUL-DE-SAC', 'p2a'),
           ('PLANET 3', 'THE WHITEOUT', 'p3a'), ('PLANET 4', 'THE TWIN', 'p4a')]
TOTAL, START, END_CARD = timing(SHOTS, END_SECS)

# eventos de glitch: (tempo global, força, duração)
EVENTS = base_events(SHOTS, PLANETS, START)
EVENTS.append((START['p1d'] + 2.1, 0.5, 0.15))     # ninguém volta
EVENTS.append((START['p2d'] + 2.0, 0.8, 0.3))      # a porta abre
EVENTS.append((START['p3c'] + 0.9, 0.6, 0.18))     # primeira batida
EVENTS.append((START['p3c'] + 2.3, 0.6, 0.18))
EVENTS.append((START['p3d'] + 0.7, 0.8, 0.2))      # segunda batida
EVENTS.append((START['p3d'] + 1.9, 1.0, 0.4))      # dentro do fogo
EVENTS.append((START['p4c'] + 1.6, 0.6, 0.2))      # piscou
EVENTS.append((START['p4d'] + 2.0, 1.0, 0.4))      # abre
EVENTS.append((START['p4d'] + 2.6, 0.7, 0.3))
EVENTS.append((END_CARD - 0.25, 1.0, 0.33))
# quadros subliminares: (tempo global, shot, frame)
SUBLIM = [(START['p2d'] + 3.55, 'p4d', 40), (START['p3b'] + 2.9, 'p4d', 45)]
SUBLIM_GRADE = 'p4'


VOICE = {
    'voice': 'bm_lewis', 'lang': 'en-gb', 'speed': 0.95,
    'name_at': 0.35,            # quando o nome começa, dentro do take do planeta
    'names': {'p1a': 'Planet one. The Salt.', 'p2a': 'Planet two. The Cul-de-sac.',
              'p3a': 'Planet three. The Whiteout.', 'p4a': 'Planet four. The Twin.'},
}

GRADE = {  # saturação, contraste, tint RGB, lift
 'intro': (0.85, 1.05, (1.0, 0.98, 1.0), 0.02),
 'p1': (0.60, 1.04, (0.96, 1.0, 1.06), 0.04),
 'p2': (0.85, 1.08, (1.04, 0.98, 0.90), 0.02),
 'p3': (0.55, 1.10, (0.92, 1.0, 1.08), 0.03),
 'p4': (0.80, 1.12, (1.0, 0.92, 1.06), 0.02),
}

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    return a
