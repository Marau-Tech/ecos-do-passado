from synth import *
from timeline import TURN, BLINKS, SPUTTER

ia, ib = START['a1'], START['b1']
a3, b3 = START['a3'], START['b3']

# ---- intro: drone ----
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((49, 1, 0), (49.4, .9, 1), (73.5, .5, 2), (98.2, .3, 3))) * seg(0, ia, 0.6), 0.1)

# ---- A: vazio grave, um vento que quase não existe, a lanterna zumbindo ----
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((32.7, 1, 0), (33.0, .8, 1), (49.0, .3, 2))) * seg(ia, ib, 0.4), 0.09)
add(lp(white, 220) * (0.6 + 0.4 * smooth_noise(0.4, 3)) * seg(START['a2'], ib, 0.4), 0.05)
torch_on = seg(START['a2'], a3 + TURN + 0.1, 0.05)
for a, b in BLINKS:
    torch_on *= 1 - seg(a3 + a, a3 + b, 0.005)
torch_on += seg(a3 + SPUTTER[0], a3 + SPUTTER[1], 0.005)
add(bp(np.sin(2 * np.pi * 120 * T) * (1 + 0.3 * rs.randn(N)), 100, 1200) * torch_on, 0.006)   # filamento
for a, b in BLINKS:
    put(click(0.7), a3 + a, 0.04); put(click(0.5), a3 + b, 0.03)
n = int(0.5 * SR); tv = np.arange(n) / SR                                # passos no cascalho, cada vez mais perto
for k, (a, b) in enumerate(BLINKS):
    crunch = bp(rs.randn(n), 400, 3000) * (rs.rand(n) > 0.85) * np.exp(-tv * 7)
    put(crunch, a3 + a + 0.05, 0.03 + 0.03 * k, pan=0.4)
put(click(0.8), a3 + TURN, 0.05); put(click(0.6), a3 + TURN + 0.25, 0.04); put(click(0.5), a3 + TURN + 0.42, 0.04)
crunch = bp(rs.randn(n), 300, 2500) * (rs.rand(n) > 0.8) * np.exp(-tv * 5)
put(crunch, a3 + SPUTTER[0] - 0.05, 0.09, pan=0.15)                     # bem perto
put(boom(1.4, 50, 28, 1.0, 0.3), a3 + SPUTTER[0], 0.06)

# ---- B: zumbido claro e agudo, o calor, e o zumbido no ouvido que cresce ----
add(chord([220.0, 330.0, 440.0]) * seg(ib, END_CARD, 0.4), 0.02)
add(bp(white, 1500, 5000) * (0.7 + 0.3 * smooth_noise(2.0, 5)) * seg(START['b2'], END_CARD, 0.3), 0.012)  # chiado de calor
ring = np.clip((T - START['b2']) / (b3 + TURN - START['b2']), 0, 1) ** 2
add(np.sin(2 * np.pi * 6200 * T) * ring * seg(START['b2'], END_CARD, 0.1), 0.012)                       # zumbido no ouvido
put(beep(6200, 0.9), b3 + TURN, 0.02)
add(np.sin(2 * np.pi * 58 * T) * seg(b3 + TURN, END_CARD, 0.2), 0.04)

finish()
