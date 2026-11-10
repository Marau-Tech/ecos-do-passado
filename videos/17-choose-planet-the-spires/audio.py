from synth import *
from timeline import EXTRA_AT, STONE_AT, ALIGN_AT

t1, t2, t3, t4 = (START[p[2]] for p in PLANETS)


def creak(dur=0.9, f=90.0):
    """rangido de madeira: serra grave com o tom tremendo"""
    n = int(dur * SR); tv = np.arange(n) / SR
    fr = f * (1 + 0.25 * np.sin(2 * np.pi * 3.3 * tv) + 0.1 * rs.randn(n).cumsum() / np.sqrt(n))
    x = 2 * ((np.cumsum(fr) / SR) % 1) - 1
    return bp(x, 300, 2400) * np.sin(np.pi * tv / dur) ** 2


def choir(fs, vib=5.0):
    """coro sem palavras: serras com vibrato, filtradas como um 'aah'"""
    x = np.zeros(N)
    for i, f in enumerate(fs):
        ph = np.cumsum(f * (1 + 0.006 * np.sin(2 * np.pi * (vib + 0.3 * i) * T + i))) / SR
        x += 2 * (ph % 1) - 1
    return (bp(x, 600, 1100) + 0.5 * bp(x, 250, 400)) / len(fs)


# ---- intro: drone ----
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((46, 1, 0), (46.4, .9, 1), (69.0, .5, 2), (92.3, .35, 3))) * seg(0, t1, 0.8), 0.1)

# ---- P1 THE AURORA: a melodia macia da luz, vento fraco; no fim, ela desafina e some ----
e = seg(t1, t2, 0.6)
mel = [440.0, 554.4, 659.3, 554.4, 493.9, 659.3, 587.3, 554.4]
for i in range(int((t2 - t1 - 2.0) / 0.9)):
    a = t1 + 2.0 + i * 0.9
    put(bell(mel[i % len(mel)], 1.6, 2.0), a, 0.05)
prog = [(220.0, 277.2, 329.6), (196.0, 246.9, 329.6), (185.0, 277.2, 329.6), (207.7, 246.9, 329.6)]
for i in range(int((t2 - t1) / 2.4) + 1):
    a = t1 + i * 2.4
    add(chord(prog[i % 4]) * seg(a, a + 2.5, 0.6) * e, 0.04)
add(lp(white, 600) * (0.5 + 0.5 * smooth_noise(0.3, 2)) * e, 0.02)
a = START['p1d'] + 2.35
fall = np.clip((T - a) / 1.5, 0, 1)
add(np.sin(2 * np.pi * np.cumsum(330 * (1 - 0.3 * fall)) / SR) * seg(a, t2, 0.1) * (1 - fall), 0.03)     # a nota que desafina
cut = 1 - seg(a, t2, 0.3) * 0.85
mixL *= cut; mixR *= cut
put(boom(1.6, 55, 24, 0.4, 0.3), a)

# ---- P2 THE FIELD: vento no milho, madeira rangendo ----
e = seg(t2 + 2.0, t3, 0.5)
add(bp(white, 400, 4000) * (0.35 + 0.65 * np.clip(smooth_noise(0.8, 5), 0, None)) * e, 0.04, 0.2)
add(lp(white, 200) * e, 0.02)
for k, tt in enumerate((START['p2b'] + 1.2, START['p2c'] + 0.8, START['p2c'] + 2.6, START['p2d'] + 0.6)):
    put(creak(0.9, 80 + 15 * k), tt, 0.06, 0.4 if k % 2 else -0.4)
a = START['p2d'] + EXTRA_AT
cut = 1 - seg(a, t3, 0.05) * 0.9                       # o vento para de uma vez
mixL *= cut; mixR *= cut
put(boom(1.8, 60, 24, 0.6, 0.4), a)
put(creak(1.4, 60), a + 0.3, 0.08)

# ---- P3 THE WELL: vento seco que vai sumindo até o silêncio, e a pedra voltando ----
e = seg(t3 + 2.0, t4, 0.4)
fade = 1 - np.clip((T - START['p3c']) / (START['p3d'] + 0.5 - START['p3c']), 0, 1)
add(bp(white, 150, 1200) * (0.6 + 0.4 * smooth_noise(0.5, 7)) * e * fade, 0.035)
add(hp(white, 5000) * e * fade, 0.006)
a = START['p3d'] + STONE_AT
pre = seg(a - 0.35, a, 0.02)                           # o ar subindo do poço
add(bp(white, 200, 3000) * pre * np.clip((T - a + 0.35) / 0.35, 0, 1) ** 2, 0.25)
put(boom(1.6, 80, 26, 1.0, 0.8), a)
put(click(2.5), a + 0.3, 0.8)
put(digital(0.4, 1.0), a, 0.2)
add(lp(white, 120) * seg(a, t4, 0.1), 0.05)

# ---- P4 THE SPIRES: drone grave e lento, coro distante que sobe até as estrelas se alinharem ----
e = seg(t4, END_CARD, 0.8)
add(sum(np.sin(2 * np.pi * f * T + i) for i, f in enumerate((32.7, 33.1, 49.0, 65.4))) * e * (0.75 + 0.25 * np.sin(2 * np.pi * T / 1.8)), 0.06)
a = START['p4d'] + ALIGN_AT
rise = np.clip((T - t4 - 2.0) / (a - t4 - 2.0), 0, 1) ** 2
add(lp(choir((110.0, 130.8, 155.6, 185.0, 220.0)), 2500) * seg(t4 + 2.0, END_CARD, 1.0) * (0.25 + 0.75 * rise), 0.09)
add(lp(white, 300) * (0.5 + 0.5 * smooth_noise(0.4, 11)) * seg(START['p4b'], END_CARD, 0.5), 0.025)     # o mar
put(boom(2.5, 50, 20, 1.0, 0.8), a)
grind = lp(white, 500) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * T))) * seg(a, END_CARD, 0.1)
add(grind, 0.08)                                        # a porta de pedra arrastando
add(choir((98.0, 103.8, 146.8, 155.6, 207.7), 7.0) * seg(a, END_CARD, 0.05), 0.12)

finish()
