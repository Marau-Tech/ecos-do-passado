from synth import *
from timeline import HEADER, REVEAL

air = seg(0, END_CARD, 0.1)
add(bp(white, 400, 3200) * (0.8 + 0.2 * smooth_noise(0.7, 2)) * air, 0.012)     # portadora

# ---- terminal: um bipe a cada linha digitada ----
at = 0.15
for ln in HEADER:
    at += len(ln) / 40
    put(beep(1500, 0.05, 1.0, True), at, 0.02)
    at += 0.25

# ---- cada imagem: dados chegando e um bipe quando termina ----
for s in [s[0] for s in SHOTS if s[0][0] == 'i']:
    a, secs = REVEAL.get(s, (REVEAL_AT, REVEAL_SECS))
    put(downlink(secs), START[s] + a, 0.11)
    put(beep(1800, 0.1), START[s] + a + secs + 0.05, 0.06)

# ---- a última: um grave enquanto chega devagar ----
i6 = START['i6']
add((np.sin(2 * np.pi * 37 * T) + 0.6 * np.sin(2 * np.pi * 37.6 * T)) * seg(i6, END_CARD, 2.5), 0.07)
put(boom(1.8, 58, 24, 0.5, 0.4), i6 + 6.4)            # o log da imagem 6

# ---- perda de sinal ----
put(digital(0.6, 1.0), i6 + 9.0, 0.16)
put(digital(0.3, 1.0), START['i5'] + REVEAL_AT + REVEAL_SECS + 0.05, 0.08)

finish()
