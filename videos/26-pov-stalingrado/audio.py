from synth import *
from timeline import FLASHES, BOOM_DELAY

i0, t1, t2, t3, t4, t5 = (START[s] for s in ('intro', 't1', 't2', 't3', 't4', 't5'))

# ---- rua: vento frio, que some dentro do porão ----
wind = bp(white, 120, 1100) * (0.55 + 0.45 * smooth_noise(0.35, 3))
add(wind * (seg(i0, t3 + 1.5, 0.5) + 0.6 * seg(t5, END_CARD, 0.8)), 0.06)
add(lp(white, 180) * seg(i0, t3, 0.5), 0.02)                               # ronco grave da cidade

# drone baixo e tenso por baixo de tudo
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((41.2, 1, 0), (41.6, .8, 1), (61.8, .35, 2))) * seg(i0, END_CARD, 1.0), 0.05)


def crunch(g=1.0):
    """passo na neve: chiado curto e abafado"""
    n = int(0.22 * SR); tv = np.arange(n) / SR
    x = bp(rs.randn(n), 400, 3500) * np.exp(-tv * 18) * (0.6 + 0.4 * (rs.rand(n) > 0.6))
    return x * g


for a, b, gap in ((t1 + 0.1, t2, 0.56), (t2 + 0.1, t3, 0.7), (t5 + 0.2, END_CARD - 0.3, 0.72)):
    for k, t0 in enumerate(np.arange(a, b, gap)):
        put(crunch(), t0, 0.09, pan=-0.15 if k % 2 else 0.15)

# ---- artilharia: um estrondo distante na intro e um para cada clarão do t2 ----
put(boom(2.8, 55, 22, 1.0, 0.8), i0 + 2.2, 0.35, pan=0.3)
for f in FLASHES:
    put(boom(3.0, 50, 20, 1.0, 0.9), t2 + f + BOOM_DELAY, 0.42, pan=-0.2)

# ---- porão: degraus de pedra, depois só a respiração e a vela ----
for k in range(8):
    put(lp(rs.randn(int(0.3 * SR)), 900) * np.exp(-np.arange(int(0.3 * SR)) / SR * 25), t3 + 0.4 + k * 0.62, 0.08)
breath = bp(white, 300, 1800) * np.clip(np.sin(2 * np.pi * 0.27 * (T - t3)), 0, None) ** 2
add(breath * seg(t3 + 3.4, t5, 0.6), 0.05)                                 # alguém respira no escuro
add(bp(white, 2500, 6500) * (0.8 + 0.2 * smooth_noise(7, 5)) * seg(t4, t5, 0.3), 0.006)   # chiado da vela
put(boom(2.0, 45, 20, 1.0, 0.6), t4 + 5.5, 0.18)                           # abafado, lá em cima

# ---- amanhecer: o vento baixo e um acorde frio que fica ----
add(chord((110, 130.8, 164.8)) * seg(t5 + 0.5, END_CARD, 1.5), 0.03)

finish()
