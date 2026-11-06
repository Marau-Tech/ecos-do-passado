# (shot, duração, legendas [(início, fim, texto)])
import numpy as np

from modelos import choose_planet as MODELO
from modelos.choose_planet import *
SHOTS = [
 ('intro', 5.0,  [(0.3, 5.0, 'Choose one. You stay for 24 hours.')]),
 ('p1a', 6.0, [(NAME_HOLD + 0.5, 6.0, 'The whole planet is one airport.')]),
 ('p1b', 3.75, [(0.2, 3.75, 'Every gate. Every hallway. Empty.')]),
 ('p1c', 3.5,  [(0.2, 3.5,  'Every flight is delayed.')]),
 ('p1d', 4.0,  [(0.1, 2.0,  'One just started boarding.'), (2.0, 4.0, 'Your name is on it.')]),
 ('p2a', 6.0, [(NAME_HOLD + 0.5, 6.0, 'A city built by a species long extinct.')]),
 ('p2b', 3.75, [(0.2, 3.75, 'Everything still runs. Nobody is left.')]),
 ('p2c', 3.5,  [(0.2, 3.5,  'The machines are full of food and water.')]),
 ('p2d', 4.0,  [(0.1, 1.8,  'You will not go hungry.'), (1.8, 4.0, 'Someone restocks them every night.')]),
 ('p3a', 6.0, [(NAME_HOLD + 0.5, 6.0, 'No sand. No rocks. Nothing.')]),
 ('p3b', 3.75, [(0.2, 3.75, 'There is no shade anywhere.')]),
 ('p3c', 3.5,  [(0.2, 3.5,  'The sun stays right above you.')]),
 ('p3d', 4.0,  [(0.1, 2.25, 'Walk for miles. It does not move.'), (2.25, 4.0, 'It is following you.')]),
 ('p4a', 6.25, [(NAME_HOLD + 0.5, 6.25, 'One supermarket. Fresh food. All free.')]),
 ('p4b', 3.5,  [(0.2, 3.5,  'Aisle one to aisle nine thousand.')]),
 ('p4c', 3.75, [(0.2, 3.75, 'When the lights flicker, do not move.')]),
 ('p4d', 3.75, [(0.1, 2.0,  'It only takes what moves.'), (2.0, 3.05, 'You just blinked.')]),
]
PLANETS = [('PLANET 1', 'THE TERMINAL', 'p1a'), ('PLANET 2', 'THE NEON', 'p2a'),
           ('PLANET 3', 'THE NOON', 'p3a'), ('PLANET 4', 'THE MARKET', 'p4a')]
TOTAL, START, END_CARD = timing(SHOTS, END_SECS)

BOARDING_AT = 1.6               # no p1d, uma linha do painel vira NOW BOARDING
RESTOCK_AT = 2.0                # no p2d, o espaço vazio da máquina aparece cheio
# piscadas das luzes do mercado, em segundos dentro do take; a figura fica mais perto a cada uma
FLICKERS = {'p4c': (1.6, 2.6), 'p4d': (0.5, 1.2, 1.9)}
BLACKOUT = 2.4                  # no p4d, tudo apaga

# eventos de glitch: (tempo global, força, duração)
EVENTS = base_events(SHOTS, PLANETS, START)
EVENTS.append((START['p1d'] + BOARDING_AT, 0.5, 0.15))
EVENTS.append((START['p2d'] + RESTOCK_AT, 0.45, 0.12))
EVENTS.append((START['p3d'] + 2.0, 0.5, 0.15))
for shot, times in FLICKERS.items():
    for tt in times:
        EVENTS.append((START[shot] + tt, 0.35, 0.1))
EVENTS.append((START['p4d'] + BLACKOUT, 1.0, 0.35))
EVENTS.append((END_CARD - 0.25, 1.0, 0.33))
# quadros subliminares: (tempo global, shot, frame)
SUBLIM = [(START['p3c'] + 3.2, 'p4d', 28)]
SUBLIM_GRADE = 'p4'

VOICE = {
    'voice': 'bm_lewis', 'lang': 'en-gb', 'speed': 0.95,
    'name_at': 0.35,
    'names': {'p1a': 'Planet one. The Terminal.', 'p2a': 'Planet two. The Neon.',
              'p3a': 'Planet three. The Noon.', 'p4a': 'Planet four. The Market.'},
}

GRADE = {  # saturação, contraste, tint RGB, lift
 'intro': (0.9, 1.05, (1.0, 0.98, 1.0), 0.02),
 'p1': (0.75, 1.02, (1.02, 1.0, 0.94), 0.03),
 'p2': (1.15, 1.08, (1.0, 0.96, 1.06), 0.01),
 'p3': (0.6, 0.95, (1.04, 1.02, 0.96), 0.04),
 'p4': (0.85, 1.04, (0.98, 1.02, 0.96), 0.02),
}

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    if shot in ('p3b', 'p3c', 'p3d'):                 # calor: as linhas tremem e o branco estoura
        rows = np.arange(a.shape[0])
        off = np.round(2.5 * np.sin(rows * 0.09 + rt * 9.0)).astype(int)
        idx = (np.arange(a.shape[1])[None, :] + off[:, None]) % a.shape[1]
        a = np.take_along_axis(a, idx[..., None].repeat(3, 2), 1)
        return np.clip(a * (1.0 + 0.04 * rt), 0, 1)
    return a
