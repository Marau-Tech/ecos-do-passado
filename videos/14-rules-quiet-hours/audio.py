from synth import *
from timeline import SHAPE, CLOCK_STOP, FLICKER

slate, r1 = START['slate'], START['r1']
r5a, r6a = START['r5a'], START['r6a']

# ---- contagem do filme: um bipe por número e o projetor ----
for i in range(3):
    put(beep(1000, 0.12, 1.0), slate + i * SLATE_COUNT, 0.08)
proj = seg(slate, END_CARD, 0.1)
add(bp(white, 200, 1400) * (0.7 + 0.3 * np.sign(np.sin(2 * np.pi * 24 * T))) * proj, 0.012)

# ---- trilha institucional: acordes calmos que desafinam na virada ----
calm = [(261.6, 329.6, 392.0), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7)]
for i in range(int((r6a - r1) / 2.6) + 1):
    a = r1 + i * 2.6
    add(chord(calm[i % 4]) * seg(a, min(r6a, a + 2.8), 0.5), 0.035)
add(chord([233.1, 246.9, 349.2]) * seg(r6a, END_CARD, 0.3) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.4 * T)), 0.045)

# ---- relógio de parede: um tique por segundo, que para na virada ----
for k in range(int(CLOCK_STOP) + 1):
    if k > slate + 4.5:
        put(lp(click(), 3000), float(k), 0.05)

# ---- a luz do fundo pisca ----
put(digital(0.2, 1.0), r5a + FLICKER, 0.08)

# ---- a virada e a silhueta ----
put(boom(2.0, 60, 24, 0.7, 0.5), r6a + 0.1)
put(boom(1.2, 80, 30, 0.6, 0.4), r6a + SHAPE)
put(digital(0.25, 1.0), r6a + SHAPE, 0.12)

finish()
