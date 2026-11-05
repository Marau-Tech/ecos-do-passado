# (shot, duração, legendas [(início, fim, texto)])
import numpy as np

from modelos import choose_planet as MODELO
from modelos.choose_planet import *
SHOTS = [
 ('intro', 5.0,  [(0.3, 5.0, 'Choose one. You stay for 24 hours.')]),
 ('p1a', 6.0, [(NAME_HOLD + 0.5, 6.0, 'The sun never sets on this planet.')]),
 ('p1b', 3.75, [(0.2, 3.75, 'It is always a warm evening here.')]),
 ('p1c', 3.5,  [(0.2, 3.5,  'Your shadow stretches out ahead of you.')]),
 ('p1d', 4.0,  [(0.1, 2.1,  'You stop walking.'), (2.1, 4.0, 'Your shadow does not.')]),
 ('p2a', 5.75, [(NAME_HOLD + 0.5, 5.75, 'One radio tower. Nobody left to run it.')]),
 ('p2b', 4.0,  [(0.2, 4.0,  'The radio inside is still on.')]),
 ('p2c', 3.5,  [(0.2, 3.5,  'It only has one voice.')]),
 ('p2d', 4.0,  [(0.1, 2.0,  'It never stops talking.'), (2.0, 4.0, 'You are hearing it now.')]),
 ('p3a', 6.0, [(NAME_HOLD + 0.5, 6.0, 'No sun. No stars. Total dark.')]),
 ('p3b', 3.75, [(0.2, 3.75, 'All you have is a camera flash.')]),
 ('p3c', 3.5,  [(0.2, 3.5,  'Flash. A figure, far away.')]),
 ('p3d', 4.0,  [(0.1, 1.9,  'Flash. Closer.'), (1.9, 4.0, 'You are not pressing it.')]),
 ('p4a', 6.25, [(NAME_HOLD + 0.5, 6.25, 'One red star. The only one in the sky.')]),
 ('p4b', 3.5,  [(0.2, 3.5,  'Every other star is already gone.')]),
 ('p4c', 3.75, [(0.2, 3.75, 'Something is switching them off.')]),
 ('p4d', 3.75, [(0.1, 2.1,  'It gets here at hour 24.'), (2.1, 3.05, 'Lights out.')]),
]
PLANETS = [('PLANET 1', 'THE EVENING', 'p1a'), ('PLANET 2', 'THE BROADCAST', 'p2a'),
           ('PLANET 3', 'THE SHUTTER', 'p3a'), ('PLANET 4', 'THE DIMMING', 'p4a')]
TOTAL, START, END_CARD = timing(SHOTS, END_SECS)

# flashes da câmera, em segundos dentro do take; fora deles a imagem fica preta
FLASHES = {'p3b': (1.95,), 'p3c': (0.3, 2.7), 'p3d': (0.2, 3.4)}
LIGHTS_OUT = 2.6                # a estrela apaga, em segundos dentro do p4d

# eventos de glitch: (tempo global, força, duração)
EVENTS = base_events(SHOTS, PLANETS, START)
EVENTS.append((START['p1d'] + 2.1, 0.5, 0.15))     # a sombra segue
EVENTS.append((START['p2d'] + 2.0, 0.9, 0.3))      # a voz é o rádio
for shot, times in FLASHES.items():
    for tt in times:
        EVENTS.append((START[shot] + tt, 0.5, 0.1))
EVENTS.append((START['p3d'] + 3.4, 1.0, 0.45))     # rosto colado na câmera
EVENTS.append((START['p4d'] + LIGHTS_OUT, 1.0, 0.2))
EVENTS.append((END_CARD - 0.25, 1.0, 0.33))
# quadros subliminares: (tempo global, shot, frame)
SUBLIM = [(START['p1d'] + 3.55, 'p3d', 55), (START['p2c'] + 2.9, 'p3d', 55)]
SUBLIM_GRADE = 'p3'


VOICE = {
    'voice': 'bm_lewis', 'lang': 'en-gb', 'speed': 0.95,
    'name_at': 0.35,            # quando o nome começa, dentro do take do planeta
    'names': {'p1a': 'Planet one. The Evening.', 'p2a': 'Planet two. The Broadcast.',
              'p3a': 'Planet three. The Shutter.', 'p4a': 'Planet four. The Dimming.'},
    'radio': ('You are hearing it now.',),      # o narrador passa a sair pelo rádio
}

GRADE = {  # saturação, contraste, tint RGB, lift
 'intro': (0.85, 1.05, (1.0, 0.98, 1.0), 0.02),
 'p1': (1.05, 1.03, (1.06, 0.99, 0.88), 0.03),
 'p2': (0.80, 1.08, (1.04, 0.98, 0.88), 0.02),
 'p3': (0.08, 1.18, (0.96, 1.0, 1.04), 0.0),
 'p4': (0.95, 1.12, (1.08, 0.92, 0.96), 0.01),
}

def flash_level(rt, times):
    k = 0.0
    for t0 in times:
        d = rt - t0
        if d >= 0:
            k = max(k, 1.5 if d < 0.07 else 1.1 * float(np.exp(-(d - 0.07) * 9)))
    return k

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    if shot in FLASHES:
        return a * flash_level(rt, FLASHES[shot])
    return a
