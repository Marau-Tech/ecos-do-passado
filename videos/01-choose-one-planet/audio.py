from synth import *

# ---- intro: drone desafinado ----
e = seg(0, 5.0, 0.8)
dr = sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((55, 1, 0), (55.5, .9, 1), (82.7, .55, 2), (110.9, .4, 3), (164.2, .2, 4)))
add(dr * e * (0.8 + 0.2 * np.sin(T * 1.3)), 0.11)

# ---- P1: reator fluorescente ----
t1 = START['p1a']; t2 = START['p2a']
buzz = sum(np.sin(2 * np.pi * 120 * k * T) / k for k in range(1, 15))
buzz = buzz * (1 + 0.5 * np.sign(np.sin(2 * np.pi * 120 * T)) * 0.2)
fl = np.clip(0.8 + 0.5 * smooth_noise(13, 3), 0.15, 1.1)
e = seg(t1 + 1.5, t2, 0.6)
# corta nos apagões
for tt in (1.35, 2.3, 3.05, 3.55):
    a = START['p1d'] + tt - 0.08
    e = e * (1 - seg(a, a + 0.19, 0.005))
add(lp(buzz, 3500) * fl * e, 0.022)
add(bp(white, 4200, 7000) * fl * e, 0.018)
add(np.sin(2 * np.pi * 73 * T) * seg(t1, t2, 1.0), 0.05)
# passos no carpete
for i in range(7):
    b = boom(0.28, 90, 50, 0.22, 0.6)
    put(lp(b, 300), START['p1b'] + 0.1 + i * 0.52, 1.0, 0.25 if i % 2 else -0.25)
# cada apagão fica mais alto
for i, tt in enumerate((1.35, 2.3, 3.05, 3.55)):
    a = START['p1d'] + tt
    put(boom(1.1, 75, 35, 0.3 + i * 0.13, 0.5), a)
    n = int(0.9 * SR); tv = np.arange(n) / SR
    st = sum(np.sin(2 * np.pi * f * tv) for f in (830, 880, 931, 1244)) * np.exp(-tv * 5)
    put(st, a, 0.015 + i * 0.012)
# ---- P2: caixinha de música que desafina ----
t3 = START['p3a']
notes = [523.25, 659.25, 783.99, 880.0, 783.99, 659.25, 698.46, 880.0, 1046.5, 880.0, 698.46, 587.33,
         587.33, 783.99, 987.77, 1174.66, 987.77, 783.99, 523.25, 659.25, 783.99, 1046.5, 783.99, 659.25]
dt = 0.31
i = 0
tt = t2 + 0.25
while tt < t3 - 0.1:
    rel = (tt - t2) / 15
    bend = 1 - 0.09 * max(0, rel - 0.72) / 0.28 * (1 + rs.rand() * 0.8)
    f = notes[i % len(notes)] * bend * (1 + 0.003 * rs.randn())
    n = int(1.3 * SR); tv = np.arange(n) / SR
    v = (np.sin(2 * np.pi * f * tv) + 0.45 * np.sin(2 * np.pi * f * 2.01 * tv) * np.exp(-tv * 4) + 0.2 * np.sin(2 * np.pi * f * 4.1 * tv) * np.exp(-tv * 9)) * np.exp(-tv * 3.3)
    put(v, tt, 0.075, 0.3 * np.sin(i))
    tt += dt * (1 + 0.5 * max(0, rel - 0.75) / 0.25); i += 1
add(lp(white, 700) * (0.6 + 0.4 * smooth_noise(0.7, 8)) * seg(t2, t3, 0.5), 0.022)
for k in range(16):                                   # pássaros
    a = t2 + rs.rand() * 11.5
    n = int(0.16 * SR); tv = np.arange(n) / SR
    f = 3100 + 1500 * np.sin(tv * 42 + rs.rand() * 6)
    v = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tv / tv[-1]) ** 2
    put(v, a, 0.012, rs.rand() - .5)
# acorde grave entra na última legenda do planeta 2
e = seg(START['p2d'] + 2.1, t3, 0.6)
add(sum(np.sin(2 * np.pi * f * T) for f in (46.2, 61.7, 65.4)) * e, 0.07)

# ---- P3: vento, infrassom, chifre ----
t4 = START['p4a']
e = seg(t3, t4, 0.4)
wind = bp(white, 180, 900) * (0.55 + 0.45 * smooth_noise(0.9, 5))
add(wind * e, 0.07, 0.2)
add(np.sin(2 * np.pi * 33 * T) * e, 0.09)
add(np.sin(2 * np.pi * 41.5 * T) * e, 0.05)
def horn(dur, f0, f1, g):
    n = int(dur * SR); tv = np.arange(n) / SR
    f = np.linspace(f0, f1, n) * (1 + 0.012 * np.sin(tv * 31))
    ph = 2 * np.pi * np.cumsum(f) / SR
    v = sum(np.sin(ph * k) / k for k in range(1, 18))
    env = np.sin(np.pi * np.clip(tv / dur, 0, 1)) ** 0.7
    return lp(np.tanh(v * 1.6), 700) * env * g
put(horn(3.0, 62, 47, 0.14), t3 + 0.7)
put(boom(4.2, 58, 19, 1.0, 0.9), START['p3b'] + 2.1)
put(boom(2.8, 45, 16, 0.5, 0.7), START['p3c'] + 2.1)
put(horn(3.2, 52, 74, 0.13), START['p3c'] + 0.3)
# aglomerado agudo subindo até o ataque
a = START['p3d']; n = int(4.0 * SR); tv = np.arange(n) / SR
v = sum(np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.5 * (tv / 4) ** 2)) / SR) for f0 in (610, 647, 702, 811, 934, 1021))
put(v * (tv / 4) ** 2.6, a, 0.05)
n = int(0.75 * SR); tv = np.arange(n) / SR
roar = np.tanh(lp(rs.randn(n), 900) * 6) * 0.26 + horn(0.75, 90, 38, 0.3)
put(roar, a + 3.25)
# corte seco no fim do planeta 3 + silêncio
mute3 = 1 - seg(t4 - 0.02, t4 + 0.12, 0.004) * 0.92
mixL *= mute3; mixR *= mute3

# ---- P4: coração, respiração, carne ----
end = END_CARD
e = seg(t4, end, 0.3)
add(np.sin(2 * np.pi * 37 * T) * e, 0.06)
breath = 0.5 + 0.5 * np.sin(T * 2.0)
add(bp(white, 200, 1100) * (breath ** 2) * e, 0.05)
hb = t4 + 0.3
rate = 1.0
while hb < end - 0.1:
    put(boom(0.34, 74, 44, 0.42, 0.25), hb)
    put(boom(0.28, 62, 40, 0.30, 0.2), hb + 0.27)
    rate = max(0.42, rate * 0.955)
    hb += rate
def squelch(g):
    n = int((0.09 + 0.3 * rs.rand()) * SR)
    x = bp(rs.randn(n), 280 + 500 * rs.rand(), 1600 + 1200 * rs.rand())
    return x * np.sin(np.pi * np.arange(n) / n) ** 2 * g * (0.5 + 0.5 * np.sign(np.sin(np.arange(n) / SR * 2 * np.pi * (28 + rs.rand() * 45))))
for k in range(46):
    put(squelch(0.12), t4 + rs.rand() * 13, 1.0, rs.rand() * 1.4 - .7)
# pálpebra abrindo: estalos cada vez mais rápidos
a = t4 + 0.9; tt = 0.0; gap = 0.13
while tt < 1.3:
    n = int(0.018 * SR); put(bp(rs.randn(n), 500, 3500) * np.exp(-np.arange(n) / n * 4), a + tt, 0.14)
    tt += gap; gap = max(0.018, gap * 0.92)
put(boom(1.6, 80, 28, 0.42, 0.35), t4 + 1.9)
# rugido final
a = START['p4d']; n = int((end - a) * SR); tv = np.arange(n) / SR
u = tv / tv[-1]
f = 46 - 22 * u
saw = sum(np.sin(2 * np.pi * np.cumsum(f * k) / SR) / k for k in range(1, 22))
rr = np.tanh(saw * 2.2) * 0.2 + (lambda z: np.tanh((lp(z, 650) * (1 - u) + lp(z, 1150) * u) * 5) * 0.2)(rs.randn(n))
sc = sum(np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.8 * u ** 2)) / SR) for f0 in (517, 603, 788, 1130)) * u ** 3 * 0.035
put((rr * (0.15 + 0.85 * u ** 1.4) + sc), a)

finish()
