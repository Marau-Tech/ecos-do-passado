from synth import *
from timeline import BOARDING_AT, RESTOCK_AT, FLICKERS, BLACKOUT

t1, t2, t3, t4 = (START[p[2]] for p in PLANETS)

# ---- intro: drone ----
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((46, 1, 0), (46.4, .9, 1), (69.0, .5, 2), (92.3, .35, 3))) * seg(0, t1, 0.8), 0.1)

# ---- P1 THE TERMINAL: ar-condicionado, esteira e o aviso de embarque ----
e = seg(t1 + 2.0, t2, 0.4)
add(lp(white, 500) * (0.8 + 0.2 * smooth_noise(0.4, 2)) * e, 0.04)
add((np.sin(2 * np.pi * 50 * T) + 0.3 * np.sin(2 * np.pi * 100 * T)) * seg(START['p1b'], START['p1c'], 0.3), 0.02)   # motor da esteira
add(chord([174.6, 220.0, 261.6]) * e, 0.02)
a = START['p1d'] + BOARDING_AT
put(bell(784.0, 1.4, 2.5), a, 0.12); put(bell(622.3, 1.6, 2.2), a + 0.45, 0.12)          # ding-dong
put(boom(1.4, 60, 26, 0.4, 0.3), START['p1d'] + 2.0)

# ---- P2 THE NEON: chuva, zumbido do neon e o motor da máquina ----
e = seg(t2 + 2.0, t3, 0.4)
add(bp(white, 1500, 8000) * (0.7 + 0.3 * smooth_noise(2.0, 5)) * e, 0.03)       # chuva
add((np.sin(2 * np.pi * 120 * T) + 0.4 * np.sin(2 * np.pi * 360 * T)) * e, 0.012)
prog = [(220.0, 277.2, 329.6), (196.0, 246.9, 293.7), (174.6, 220.0, 261.6), (196.0, 246.9, 329.6)]
for i in range(int((t3 - t2) / 2.0) + 1):
    a = t2 + 2.0 + i * 2.0
    add(chord(prog[i % 4]) * seg(a, min(t3, a + 2.1), 0.4) * e, 0.035)
add(np.sin(2 * np.pi * 58 * T) * seg(START['p2c'], t3, 0.2), 0.02)               # compressor da máquina
a = START['p2d'] + RESTOCK_AT
put(click(), a, 0.4); put(lp(click(), 800), a + 0.08, 0.3)                        # algo cai na prateleira
cut = 1 - seg(a, t3, 0.15) * 0.6
mixL *= cut; mixR *= cut

# ---- P3 THE NOON: quase nada, um chiado agudo de calor que sobe ----
e = seg(t3 + 2.0, t4, 0.3)
k = np.clip((T - t3) / (t4 - t3), 0, 1)
add(np.sin(2 * np.pi * (7200 + 2400 * k) * T) * e * (0.2 + 0.8 * k), 0.006)
add(hp(white, 6000) * e * k, 0.012)
add(lp(white, 150) * e, 0.02)

# ---- P4 THE MARKET: zumbido das lâmpadas e música de mercado, que cortam a cada piscada ----
e = seg(t4 + 2.0, END_CARD, 0.4)
hum = (np.sin(2 * np.pi * 120 * T) + 0.5 * np.sign(np.sin(2 * np.pi * 120 * T)) * 0.3)
gate = np.ones(N)
for shot, times in FLICKERS.items():
    for tt in times:
        a = START[shot] + tt
        gate *= 1 - seg(a, a + 0.25, 0.01)
        put(click(), a, 0.35); put(click(), a + 0.25, 0.25)
b = START['p4d'] + BLACKOUT
gate *= 1 - seg(b, END_CARD, 0.01)
add(hum * e * gate, 0.02)
add(muzak(t4 + 2.0, b, 261.6, 2.2) * gate, 0.04)
put(boom(2.0, 62, 22, 0.8, 0.5), b)
put(digital(0.4, 1.0), b, 0.14)

finish()
