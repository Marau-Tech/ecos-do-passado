from synth import *
from timeline import TURN

ia, ib = START['a1'], START['b1']
a3, b3 = START['a3'], START['b3']

# ---- intro: drone ----
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((49, 1, 0), (49.4, .9, 1), (73.5, .5, 2), (98.2, .3, 3))) * seg(0, ia, 0.6), 0.1)

# ---- A: tudo pesado e grave ----
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((31.0, 1, 0), (31.3, .8, 1), (46.5, .4, 2))) * seg(ia, ib, 0.4), 0.1)
add(lp(white, 160) * seg(ia, ib, 0.4), 0.08)                                 # pressão: um ronco abafado
def thump(f=48, dur=0.16):
    n = int(dur * SR); tv = np.arange(n) / SR
    return np.sin(2 * np.pi * f * tv * (1 - 0.3 * tv / dur)) * np.exp(-tv * 22)
t0 = START['a2']                                                             # o coração trabalhando dobrado
while t0 < ib - 0.2:
    put(thump(52), t0, 0.12); put(thump(44), t0 + 0.2, 0.09)
    t0 += 0.62
for t0 in (START['a2'] + 0.5, START['a2'] + 2.6, a3 + 0.6, a3 + 3.2):       # a luva arrastando no cascalho
    n = int(0.7 * SR); tv = np.arange(n) / SR
    put(bp(rs.randn(n), 700, 4000) * (rs.rand(n) > 0.7) * np.sin(np.pi * tv / 0.7), t0, 0.05, pan=0.2)
put(boom(1.6, 50, 26, 1.0, 0.3), a3 + TURN, 0.25)

# ---- B: quase nada, respiração e a corda ----
add(np.sin(2 * np.pi * 2200 * T) * seg(ib, END_CARD, 0.5), 0.003)            # zumbido fino do traje
breath = (0.5 - 0.5 * np.cos(2 * np.pi * 0.35 * np.clip(T - ib, 0, None))) ** 2
add(bp(white, 400, 2400) * breath * seg(ib, b3 + TURN, 0.3), 0.05)
fast = (0.5 - 0.5 * np.cos(2 * np.pi * 0.9 * np.clip(T - b3 - TURN, 0, None))) ** 2
add(bp(white, 400, 2400) * fast * seg(b3 + TURN, END_CARD, 0.1), 0.07)       # depois do fio, a respiração acelera
for t0 in (b3 + 0.3, b3 + 1.4):                                              # a corda rangendo esticada
    n = int(0.5 * SR); tv = np.arange(n) / SR
    f = 380 * (1 + 0.05 * np.sin(2 * np.pi * 6 * tv))
    x = bp(((np.cumsum(f) / SR) % 1.0) * 2 - 1, 300, 2000) * (np.abs(np.sin(2 * np.pi * 30 * tv)) ** 3)
    put(x * np.sin(np.pi * tv / 0.5), t0, 0.04)
put(click(1.0), b3 + TURN, 0.12)                                             # o fio arrebenta
n = int(1.2 * SR); tv = np.arange(n) / SR
put(np.sin(2 * np.pi * 170 * tv) * np.exp(-tv * 4) * (1 + 0.3 * np.sin(2 * np.pi * 9 * tv)), b3 + TURN, 0.05)

finish()
