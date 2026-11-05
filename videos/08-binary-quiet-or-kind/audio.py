from synth import *

ia, ib = START['a1'], START['b1']

# ---- intro: drone ----
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((49, 1, 0), (49.4, .9, 1), (73.5, .5, 2), (98.2, .3, 3))) * seg(0, ia, 0.6), 0.1)

# ---- A: quase silêncio, depois uma respiração que não é sua ----
from timeline import BREATH, FOG_FROM
add(lp(white, 300) * seg(ia, ib, 0.3), 0.01)
a3 = START['a3']
s = np.clip(T - (a3 + FOG_FROM), 0, None)
breath = (0.5 - 0.5 * np.cos(2 * np.pi * BREATH * s)) ** 2 * seg(a3 + FOG_FROM, ib, 0.3)
add(bp(white, 300, 2200) * breath, 0.09)
add(bp(white, 120, 600) * breath, 0.05)

# ---- B: caixinha de música alegre, que desafina no fim ----
notes = [523.3, 659.3, 784.0, 659.3, 587.3, 698.5, 880.0, 698.5]
k = 0
t0 = ib + 0.2
while t0 < END_CARD - 0.2:
    detune = 1.0 + 0.03 * max(0.0, t0 - (START['b3'] + 2.2))
    put(bell(notes[k % 8] * detune, 1.0, 4.5), t0, 0.05)
    k += 1; t0 += 0.38
add(chord([261.6, 329.6, 392.0]) * seg(ib, START['b3'] + 2.2, 0.5), 0.025)
add(chord([246.9, 261.6, 370.0]) * seg(START['b3'] + 2.2, END_CARD, 0.2), 0.03)

finish()
