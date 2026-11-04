# (shot, duração, legendas [(início, fim, texto)])
FPS_SRC = 15
FPS_OUT = 30
SHOTS = [
 ('intro', 5.0,  [(0.3, 5.0, 'Choose one. You stay for 24 hours.')]),
 ('p1a', 3.75, [(0.5, 3.75, 'Every inch of this planet is edible.')]),
 ('p1b', 3.75, [(0.2, 3.75, 'The table is always set.')]),
 ('p1c', 3.5,  [(0.2, 3.5,  'The rivers run with warm honey.')]),
 ('p1d', 4.0,  [(0.1, 2.1,  'Take a bite. It grows back.'), (2.1, 4.0, 'There is no catch.')]),
 ('p2a', 3.5,  [(0.5, 3.5,  'Just trees, from pole to pole.')]),
 ('p2b', 4.0,  [(0.2, 4.0,  'No monsters. No trails either.')]),
 ('p2c', 3.5,  [(0.2, 3.5,  'Water is easy. Food is on you.')]),
 ('p2d', 4.0,  [(0.1, 2.1,  'The nights get cold.'), (2.1, 4.0, 'You will make it. Barely.')]),
 ('p3a', 3.75, [(0.5, 3.75, 'There is no land here.')]),
 ('p3b', 3.75, [(0.2, 3.75, 'You get one raft. Nothing else.')]),
 ('p3c', 3.5,  [(0.2, 3.5,  'That pale shape below is not the seabed.')]),
 ('p3d', 4.0,  [(0.1, 2.0,  'It is a hand.'), (2.0, 4.0, 'And it just felt you land.')]),
 ('p4a', 4.0,  [(0.5, 4.0,  'Those pale specks are not rocks.')]),
 ('p4b', 3.5,  [(0.2, 3.5,  'They are people. Billions of them.')]),
 ('p4c', 3.75, [(0.2, 3.75, 'All standing still. All facing away.')]),
 ('p4d', 3.75, [(0.1, 1.2,  'Then you breathe.'), (1.2, 3.05, 'They are practicing your face.')]),
]
PLANETS = [('PLANET 1', 'THE FEAST', 'p1a'), ('PLANET 2', 'THE WOODS', 'p2a'),
           ('PLANET 3', 'THE DEEP', 'p3a'), ('PLANET 4', 'THE CROWD', 'p4a')]
TOTAL = sum(s[1] for s in SHOTS)
START = {}
_t = 0.0
for s in SHOTS:
    START[s[0]] = _t; _t += s[1]
END_CARD = TOTAL - 0.7          # tela final "CHOOSE."

# eventos de glitch: (tempo global, força, duração)
EVENTS = []
for name, dur, _ in SHOTS[1:]:
    EVENTS.append((START[name], 0.45, 0.13))
for _, _, sh in PLANETS:
    EVENTS.append((START[sh], 1.0, 0.28))
EVENTS.append((START['p3c'] + 2.2, 0.5, 0.15))     # a forma aparece
EVENTS.append((START['p3d'] + 2.0, 0.9, 0.3))      # a mão fecha
EVENTS.append((START['p3d'] + 3.4, 0.8, 0.6))
EVENTS.append((START['p4d'], 1.0, 0.4))            # todos viram de uma vez
EVENTS.append((START['p4d'] + 2.5, 0.55, 0.3))     # investida
EVENTS.append((END_CARD - 0.25, 1.0, 0.33))
# quadros subliminares: (tempo global, shot, frame)
SUBLIM = [(START['p2d'] + 3.55, 'p4d', 40), (START['p3c'] + 2.9, 'p4d', 45)]
SUBLIM_GRADE = 'p4'

SECTION = 15.0                  # duração de cada trecho, usada no contador
END_TEXT = 'CHOOSE.'
INTRO_LABELS = [((88, 228), '1'), ((872, 212), '2'), ((96, 492), '3'), ((880, 482), '4')]

GRADE = {  # saturação, contraste, tint RGB, lift
 'intro': (0.85, 1.05, (1.0, 0.98, 1.0), 0.02),
 'p1': (1.02, 1.02, (1.05, 1.0, 0.90), 0.03),
 'p2': (0.78, 1.06, (0.97, 1.02, 0.94), 0.025),
 'p3': (0.74, 1.12, (0.90, 1.02, 1.04), 0.02),
 'p4': (0.42, 1.10, (1.02, 1.0, 0.96), 0.03),
}

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    return a
