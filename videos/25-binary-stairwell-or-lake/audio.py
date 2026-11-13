from synth import *
from timeline import TURN, LIGHT_ON, LIGHT_OFF

ia, ib = START['a1'], START['b1']
a2, a3 = START['a2'], START['a3']
b2, b3 = START['b2'], START['b3']

# ---- intro: drone ----
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((49, 1, 0), (49.4, .9, 1), (73.5, .5, 2), (98.2, .3, 3))) * seg(0, ia, 0.6), 0.1)

# ---- A: o poço de concreto. Zumbido da luz, passos com eco, relés ----
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((41.2, 1, 0), (41.5, .8, 1), (61.7, .4, 2))) * seg(ia, ib, 0.4), 0.07)
hum = np.sin(2 * np.pi * 120 * T) + 0.5 * np.sin(2 * np.pi * 240 * T) + 0.3 * np.sin(2 * np.pi * 360 * T)
add(hum * seg(ia, a3 + TURN, 0.3) * np.clip(1 - np.clip(T - a3, 0, None) / TURN * 0.7, 0, 1), 0.006)


def step(g=1.0):
    """passo em degrau de concreto, com eco do poço"""
    n = int(0.9 * SR); tv = np.arange(n) / SR
    hit = lp(rs.randn(n), 1400) * np.exp(-tv * 40)
    tail = sum(np.roll(hit, int(d * SR)) * a for d, a in ((0.11, 0.45), (0.23, 0.3), (0.37, 0.18), (0.55, 0.1)))
    return (hit + lp(tail, 800)) * g


for k, t0 in enumerate(np.arange(a2 + 0.1, a3 - 0.1, 0.5)):              # descendo, dois passos por segundo
    put(step(), t0, 0.07, pan=-0.2 if k % 2 else 0.2)
for t0 in (a2 + LIGHT_ON, a2 + LIGHT_OFF):                                 # relé da luz que acende e da que apaga
    put(click(0.8), t0, 0.06)
    put(lp(rs.randn(int(0.2 * SR)), 300) * np.exp(-np.arange(int(0.2 * SR)) / SR * 20), t0, 0.05)
# a3: parado. Depois da chave, o zumbido engasga com a lâmpada
fl = (rs.rand(int(TOTAL * 15) + 2) > 0.45).astype(float)
gate = lp(np.repeat(fl, SR // 15 + 1)[:N], 200)
buzz = bp(np.sign(np.sin(2 * np.pi * 120 * T)), 100, 2000)
add(buzz * gate * seg(a3 + TURN, ib, 0.05), 0.012)

# ---- B: vento no gelo, o gelo cantando, e a batida ----
wind = bp(white, 150, 900) * (0.6 + 0.4 * smooth_noise(0.4, 3))
add(wind * seg(ib, b3, 0.4), 0.05)
add(lp(white, 250) * seg(b3, END_CARD, 0.2), 0.03)                          # dentro da cabana, abafado


def sing(dur=0.7, f0=2600, f1=180):
    """o gelo do lago estala e 'canta': um assobio que desce rápido"""
    n = int(dur * SR); tv = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tv * 9)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tv * 5)


for t0, g, p in ((ib + 0.8, 0.04, -0.5), (ib + 3.1, 0.03, 0.6), (b2 + 1.0, 0.05, 0.2), (b2 + 2.8, 0.035, -0.4)):
    put(sing(), t0, g, pan=p)
# lampião chiando dentro da cabana
add(bp(white, 2500, 7000) * (0.8 + 0.2 * smooth_noise(6, 5)) * seg(b3, END_CARD, 0.2), 0.008)
# a batida, de baixo da tábua
put(boom(1.4, 70, 30, 1.0, 0.9), b3 + TURN, 0.5)
put(lp(rs.randn(int(0.12 * SR)), 2500) * np.exp(-np.arange(int(0.12 * SR)) / SR * 30), b3 + TURN, 0.12)
put(click(1.0), b3 + TURN + 0.17, 0.05)                                      # a tábua cai de volta, torta
# depois de "Once every hour.": nada além do lampião

finish()
