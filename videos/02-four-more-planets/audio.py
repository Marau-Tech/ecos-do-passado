from synth import *

def chord(fs, a=1.0):
    return sum(np.sin(2 * np.pi * f * T + i) for i, f in enumerate(fs)) * a / len(fs)
def bell(f, dur=1.4, decay=3.0):
    n = int(dur * SR); tv = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tv) + 0.4 * np.sin(2 * np.pi * f * 2.01 * tv) * np.exp(-tv * 4) + 0.15 * np.sin(2 * np.pi * f * 4.1 * tv) * np.exp(-tv * 9)) * np.exp(-tv * decay)

t1, t2, t3, t4 = (START[p[2]] for p in PLANETS)

# ---- intro: drone desafinado ----
e = seg(0, t1, 0.8)
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((49, 1, 0), (49.4, .9, 1), (73.6, .55, 2), (98.6, .4, 3), (147.2, .2, 4))) * e * (0.8 + 0.2 * np.sin(T * 1.3)), 0.11)

# ---- P1 THE FEAST: órgão morno, caixinha afinada, talheres ----
e = seg(t1, t2, 0.6)
prog = [(261.6, 329.6, 392.0), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7)]
for i in range(8):
    a = t1 + i * 1.875
    ch = prog[i % 4]
    add(chord(ch) * seg(a, a + 1.95, 0.25) * e, 0.055)
    add(chord([f / 2 for f in ch]) * seg(a, a + 1.95, 0.25) * e, 0.05)
melody = [523.25, 659.25, 783.99, 659.25, 880.0, 783.99, 659.25, 523.25, 587.33, 698.46, 880.0, 698.46, 783.99, 987.77, 783.99, 587.33]
tt = t1 + 0.3; i = 0
while tt < t2 - 0.4:
    put(bell(melody[i % 16]), tt, 0.06, 0.25 * np.sin(i)); tt += 0.47; i += 1
for k in range(14):                                   # talheres e taças ao longe
    put(bell(2400 + 1400 * rs.rand(), 0.25, 18), START['p1b'] + rs.rand() * 3.6, 0.012, rs.rand() - .5)
add(bp(white, 150, 600) * (0.6 + 0.4 * smooth_noise(0.8, 2)) * seg(START['p1c'], START['p1d'], 0.5), 0.022)   # mel correndo
# na frase final a música para e sobra uma nota só
a = START['p1d'] + 2.1
mix_cut = 1 - seg(a, t2, 0.2) * 0.85
mixL *= mix_cut; mixR *= mix_cut
put(bell(523.25, 2.2, 1.6), a + 0.15, 0.07)

# ---- P2 THE WOODS: vento nas copas, riacho, grilos e fogueira ----
e = seg(t2, t3, 0.4)
add(bp(white, 250, 1400) * (0.5 + 0.5 * smooth_noise(0.6, 5)) * e, 0.05, -0.1)
add(np.sin(2 * np.pi * 58 * T) * e, 0.035)
add(bp(white, 900, 3800) * (0.75 + 0.25 * smooth_noise(6, 6)) * seg(START['p2c'], START['p2d'], 0.3), 0.03, 0.2)
for k in range(9):                                    # pássaros esparsos
    a = t2 + rs.rand() * 10.5
    n = int(0.22 * SR); tv = np.arange(n) / SR
    f = 2100 + 700 * np.sin(tv * 30 + rs.rand() * 6)
    put(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tv / tv[-1]) ** 2, a, 0.012, rs.rand() - .5)
for i in range(7):                                    # passos em folhas
    n = int(0.16 * SR)
    put(bp(rs.randn(n), 500, 3200) * np.exp(-np.arange(n) / n * 5), START['p2b'] + 0.25 + i * 0.52, 0.07, 0.25 if i % 2 else -0.25)
e = seg(START['p2d'], t3, 0.3)
add(lp(white, 400) * e * (0.6 + 0.4 * smooth_noise(4, 7)), 0.03)
for k in range(46):                                   # estalos da fogueira
    n = int(0.012 * SR); put(hp(rs.randn(n), 1500) * np.exp(-np.arange(n) / n * 5), START['p2d'] + rs.rand() * 3.8, 0.10 * rs.rand(), rs.rand() * .6 - .3)
cr = np.sign(np.sin(2 * np.pi * 4300 * T)) * (np.sin(2 * np.pi * 15 * T) > 0.2) * (np.sin(2 * np.pi * 1.1 * T) > -0.2)
add(hp(cr, 3000) * e, 0.006, 0.4)

# ---- P3 THE DEEP: mar, gemido grave, batida ----
e = seg(t3, t4, 0.4)
swell = 0.55 + 0.45 * np.sin(T * 0.8)
add(lp(white, 500) * swell * e, 0.09)
add(bp(white, 500, 2200) * swell ** 3 * e, 0.018, -0.2)
add(np.sin(2 * np.pi * 29 * T) * e, 0.08)
def groan(dur, f0, f1, g):
    n = int(dur * SR); tv = np.arange(n) / SR
    f = np.linspace(f0, f1, n) * (1 + 0.02 * np.sin(tv * 3.1))
    v = sum(np.sin(2 * np.pi * np.cumsum(f * k) / SR) / k for k in range(1, 9))
    return lp(np.tanh(v * 1.4), 520) * np.sin(np.pi * np.clip(tv / dur, 0, 1)) ** 0.8 * g
put(groan(2.8, 88, 64, 0.12), START['p3b'] + 0.6)
put(groan(3.2, 70, 118, 0.15), START['p3c'] + 0.2)
put(boom(3.0, 55, 18, 0.9, 0.8), START['p3c'] + 2.2)
a = START['p3d']
put(boom(2.6, 60, 20, 0.7, 0.7), a + 0.1)
put(boom(3.4, 52, 17, 1.0, 1.0), a + 2.0)
n = int(4.0 * SR); tv = np.arange(n) / SR
put(lp(rs.randn(n), 900) * (tv / 4) ** 2, a, 0.34)    # água caindo dos dedos
put(sum(np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.4 * (tv / 4) ** 2)) / SR) for f0 in (310, 347, 402, 511, 634)) * (tv / 4) ** 2.6, a, 0.05)
mute = 1 - seg(t4 - 0.02, t4 + 0.12, 0.004) * 0.92
mixL *= mute; mixR *= mute

# ---- P4 THE CROWD: quase silêncio, depois todos respiram ----
end = END_CARD
e = seg(t4, end, 0.3)
add(lp(white, 300) * e, 0.012)
add(np.sin(2 * np.pi * 41 * T) * e, 0.03)
a = START['p4b']
add(bp(white, 300, 1400) * (0.5 + 0.5 * smooth_noise(2, 12)) * seg(a, START['p4d'], 0.6), 0.016)     # multidão muda
for i in range(6):                                    # passos no pó
    put(lp(boom(0.2, 100, 60, 0.12, 0.5), 400), START['p4c'] + 0.2 + i * 0.6, 1.0, 0.2 if i % 2 else -0.2)
# virada: um estalo de bilhões de pescoços
a = START['p4d']
for k in range(420):
    n = int(0.008 * SR)
    put(bp(rs.randn(n), 800, 5000) * np.exp(-np.arange(n) / n * 4), a + rs.rand() ** 2 * 0.3, 0.05, rs.rand() * 1.6 - .8)
put(boom(1.4, 70, 28, 0.5, 0.4), a)
# respiração coletiva
b = seg(a + 0.3, END_CARD, 0.2)
breath = (0.5 + 0.5 * np.sin(2 * np.pi * 0.55 * (T - a))) ** 2
add(bp(white, 260, 1500) * breath * b, 0.12)
# aglomerado subindo até a investida
n = int(2.5 * SR); tv = np.arange(n) / SR
put(sum(np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.5 * (tv / 2.5) ** 2)) / SR) for f0 in (517, 603, 702, 788, 934)) * (tv / 2.5) ** 2.4, a, 0.05)
# grito final
a = START['p4d'] + 2.5; n = int((end - a) * SR); tv = np.arange(n) / SR
u = tv / tv[-1]
sc = sum(np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.5 * u)) / SR) for f0 in (640, 756, 912, 1140, 1490))
put(np.tanh(sc * 1.4 + lp(rs.randn(n), 2600) * 5) * 0.26 * (0.4 + 0.6 * u), a)
put(boom(1.0, 90, 32, 0.8, 0.8), a)

finish()
