# (shot, duração, legendas [(início, fim, texto)])
from modelos import choose_planet as MODELO
from modelos.choose_planet import *
SHOTS = [
 ('intro', 5.0,  [(0.3, 5.0, 'Choose one to spend 24 hours on')]),
 ('p1a', 3.75, [(0.5, 3.75, 'The entire planet is a single building.')]),
 ('p1b', 3.75, [(0.2, 3.75, 'Endless hallways. Not a single window.')]),
 ('p1c', 3.5,  [(0.2, 3.5,  'The hum of the lights never stops.')]),
 ('p1d', 4.0,  [(0.1, 4.0,  'It only moves when the lights flicker.')]),
 ('p2a', 3.5,  [(0.5, 3.5,  'Clean air. 24 °C all year round.')]),
 ('p2b', 4.0,  [(0.2, 4.0,  'A home, ready and waiting. Just for you.')]),
 ('p2c', 3.5,  [(0.2, 3.5,  'The golden fruit cures any disease.')]),
 ('p2d', 4.0,  [(0.1, 2.1,  'All this gold is yours.'), (2.1, 4.0, 'No visitor ever wanted to go back.')]),
 ('p3a', 3.75, [(0.5, 3.75, 'The sun never rises. And something walks here.')]),
 ('p3b', 3.75, [(0.2, 3.75, 'Every step shakes the entire planet.')]),
 ('p3c', 3.5,  [(0.2, 3.5,  'The Walker is taller than the sky.')]),
 ('p3d', 4.0,  [(0.1, 2.0,  '21 eyes. None of them blink.'), (2.0, 4.0, 'It already heard you.')]),
 ('p4a', 4.0,  [(0.5, 4.0,  'This is not a planet.')]),
 ('p4b', 3.5,  [(0.2, 3.5,  'The ground breathes. You walk on its ribs.')]),
 ('p4c', 3.75, [(0.2, 3.75, 'It knows exactly where you landed.')]),
 ('p4d', 3.75, [(0.1, 3.05, 'At hour 24, it swallows.')]),
]
PLANETS = [('PLANET 1', 'THE BUILDING', 'p1a'), ('PLANET 2', 'VERDANT', 'p2a'),
           ('PLANET 3', 'ETERNAL NIGHT', 'p3a'), ('PLANET 4', 'THE HOST', 'p4a')]
TOTAL, START, END_CARD = timing(SHOTS, END_SECS)

# eventos de glitch: (tempo global, força, duração)
EVENTS = base_events(SHOTS, PLANETS, START)
for tt in (1.35, 2.3, 3.05, 3.55):                 # apagões do corredor
    EVENTS.append((START['p1d'] + tt - 0.08, 0.7, 0.18))
EVENTS.append((START['p2d'] + 2.05, 0.5, 0.1))
EVENTS.append((START['p3b'] + 2.1, 0.9, 0.5))      # pisada
EVENTS.append((START['p3d'] + 3.25, 0.8, 0.75))    # investida
EVENTS.append((START['p4a'] + 1.9, 0.5, 0.2))      # olho encara
EVENTS.append((END_CARD - 0.25, 1.0, 0.33))
# quadros subliminares: (tempo global, shot, frame)
SUBLIM = [(START['p2d'] + 3.55, 'p4a', 45), (START['p2c'] + 2.9, 'p3d', 30)]
SUBLIM_GRADE = 'p4'

SECTION = 15.0                  # duração de cada trecho, usada no contador

GRADE = {  # saturação, contraste, tint RGB, lift
 'intro': (0.82, 1.05, (1.0, 0.98, 1.0), 0.02),
 'p1': (0.86, 1.08, (1.03, 1.0, 0.86), 0.025),
 'p2': (0.90, 1.0, (1.03, 1.0, 0.94), 0.03),
 'p3': (0.72, 1.12, (0.92, 0.97, 1.08), 0.022),
 'p4': (0.88, 1.08, (1.04, 0.95, 0.93), 0.02),
}

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    if shot == 'p2d':                                  # o paraíso desbota no fim
        k = max(0.0, (rt - 2.1) / 1.9)
        y = a.mean(-1, keepdims=True)
        a = a * (1 - 0.45 * k) + y * 0.45 * k
    return a
