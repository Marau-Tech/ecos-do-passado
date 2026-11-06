from synth import *
from timeline import KNOCKS, SLATE_COUNT

slate, r1 = START['slate'], START['r1']
r5a = START['r5a']

# ---- contagem do filme: um bipe por número e o projetor ----
for i in range(3):
    put(beep(1000, 0.12, 1.0), slate + i * SLATE_COUNT, 0.08)
proj = seg(slate, END_CARD, 0.1)
add(bp(white, 200, 1400) * (0.7 + 0.3 * np.sign(np.sin(2 * np.pi * 24 * T))) * proj, 0.012)

# ---- trilha institucional: acordes calmos que desafinam na virada ----
calm = [(261.6, 329.6, 392.0), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7)]
turn = r5a + 4.0
for i in range(int((turn - r1) / 2.6) + 1):
    a = r1 + i * 2.6
    add(chord(calm[i % 4]) * seg(a, min(turn, a + 2.8), 0.5), 0.035)
add(chord([233.1, 246.9, 349.2]) * seg(turn, END_CARD, 0.3) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.4 * T)), 0.045)

# ---- rádio: chiado de sintonia ----
r2a = START['r2a']
add(bp(white, 900, 3200) * (0.5 + 0.5 * smooth_noise(3, 6)) * seg(r2a, r2a + 5.0, 0.3), 0.02)

# ---- janela a mais: um clique ----
put(click(), START['r3a'] + 4.6, 0.25)

# ---- batidas na porta ----
r4a = START['r4a']
for t0 in KNOCKS:
    put(boom(0.35, 120, 70, 0.6, 0.8), r4a + t0)
    put(lp(click(), 900), r4a + t0, 0.6)

# ---- a virada e a regra 6 ----
put(boom(2.0, 60, 24, 0.7, 0.5), turn)
put(digital(0.25, 1.0), r5a + 7.5, 0.12)

finish()
