# (take, duração, legendas [(início, fim, texto)])
from modelos import binary as MODELO
from modelos.binary import *
import numpy as np

SHOTS = [
 ('intro', 4.0, [(0.3, 4.0, 'Pick one. You stay for 24 hours.')]),
 ('a1', 4.5, [(NAME_HOLD + 0.6, 4.5, 'The sun never rises here.')]),
 ('a2', 4.0, [(0.2, 4.0, 'You get one flashlight.')]),
 ('a3', 4.5, [(0.1, 2.2, 'It only moves in the dark.'), (2.2, 4.5, 'Your battery is old.')]),
 ('b1', 4.5, [(NAME_HOLD + 0.6, 4.5, 'The sun never sets here.')]),
 ('b2', 4.0, [(0.2, 4.0, 'You cannot sleep here.')]),
 ('b3', 5.2, [(0.1, 2.2, 'By hour twenty, you see things.'), (2.2, 4.5, "You can't tell what's real.")]),
]
OPTIONS = [('OPTION A', 'THE DARK PLANET', 'a1'), ('OPTION B', 'THE BRIGHT PLANET', 'b1')]
TOTAL, START, END_CARD = timing(SHOTS)

TURN = 2.2                      # a chave no a3 e no b3: a lanterna morre; uma figura do calor está mais perto
# a3: apagões da lanterna antes da chave; a cada um, a forma volta mais perto, no limite da luz
BLINKS = [(0.75, 0.95), (1.45, 1.65)]
FORM_DIST = [6.2, 5.0, 3.9]     # distância da forma antes, entre e depois dos apagões
SPUTTER = (3.2, 3.45)           # depois da chave, a lanterna volta um instante: a forma a 3 m
SPUTTER_DIST = 2.3

EVENTS = base_events(SHOTS, OPTIONS, START)
EVENTS += [(START['a3'] + TURN, 0.5, 0.15),
           (START['b3'] + TURN, 0.5, 0.15),
           (END_CARD - 0.25, 1.0, 0.33)]
SUBLIM = []
SUBLIM_GRADE = 'a'

VOICE = {
    'voice': 'bm_lewis', 'lang': 'en-gb', 'speed': 0.95,
    'name_at': 0.1,
    'names': {'a1': 'Option A. The dark planet.', 'b1': 'Option B. The bright planet.'},
}

GRADE = {  # saturação, contraste, tint RGB, lift
 'intro': (0.95, 1.05, (1.0, 0.98, 1.0), 0.02),
 'a': (0.6, 1.08, (0.95, 0.98, 1.05), 0.02),
 'b': (0.8, 0.95, (1.03, 1.01, 0.96), 0.0),
}

# ---- calor da planície branca: as linhas perto do horizonte tremem ----
W_, H_ = 960, 720
_Y = np.arange(H_)[:, None]
_X = np.arange(W_)[None, :]
HORIZON = {'b2': 250, 'b3': 330}    # linha do horizonte no quadro de 960x720
STILL_X = (505, 585)                # coluna da figura que parou de tremer, no b3 depois da chave


def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1. Tremor de calor só no b2 e no b3."""
    if shot not in HORIZON:
        return a
    hy = HORIZON[shot]
    band = np.exp(-((_Y - hy) / 70.0) ** 2)                               # forte no horizonte
    amp = 4.5 * band * (1.0 if shot == 'b3' else 0.6)
    dx = amp * np.sin(_Y * 0.21 + rt * 9.0) + 0.6 * amp * np.sin(_Y * 0.53 - rt * 13.0)
    dx = np.broadcast_to(dx, (H_, W_)).copy()
    if shot == 'b3' and rt >= TURN:
        m = np.clip(np.minimum(_X - STILL_X[0], STILL_X[1] - _X) / 12.0, 0, 1)
        dx = dx * (1 - m)
    xs = np.clip(np.round(_X + dx).astype(int), 0, W_ - 1)
    return a[_Y, xs]
