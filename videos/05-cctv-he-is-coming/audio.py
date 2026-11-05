from synth import *
from timeline import FLICKERS, MESSAGE, TYPE_AT, TYPE_STEP

a1, a2, a3, c1, a4, c2, c3, a5, a6 = (START[s[0]] for s in SHOTS)

# ---- sala: ar-condicionado e zumbido ----
room = seg(0, END_CARD, 0.5)
add(lp(white, 320) * (0.75 + 0.25 * smooth_noise(0.3, 3)) * room, 0.05)
add(np.sin(2 * np.pi * 60 * T) * room, 0.02)

# ---- monitores ligando ----
def power_on(t0, g=1.0):
    put(click(), t0, 0.5 * g)
    n = int(0.5 * SR); tv = np.arange(n) / SR
    put(np.sin(2 * np.pi * (15000 - 600 * tv) * tv) * np.exp(-tv * 3), t0 + 0.03, 0.012 * g)
power_on(a1 + 3.0)
for x in (1.5, 4.5, 7.5):
    power_on(a2 + x)
for i in range(8):
    power_on(a3 + rs.rand() * 0.12, 0.7)
put(digital(0.35, 1.0), a3, 0.1)
add(sum(np.sin(2 * np.pi * f * T + i) for i, f in enumerate((120.0, 121.0, 240.0))) * seg(a3, c3, 0.3), 0.012)     # telas acesas

# ---- a figura: quase silêncio e um bipe por segundo ----
for i in range(9):
    n = int(0.06 * SR); put(np.sin(2 * np.pi * 980 * np.arange(n) / SR) * np.hanning(n), c1 + 0.5 + i, 0.02)

# ---- luzes piscando ----
for f in FLICKERS:
    n = int(0.3 * SR); tv = np.arange(n) / SR
    put(np.sign(np.sin(2 * np.pi * 120 * tv)) * np.exp(-tv * 6), a4 + f, 0.05)
    put(click(), a4 + f, 0.35); put(click(), a4 + f + 0.25, 0.25)
    put(digital(0.28, 1.0), a4 + f, 0.07, rs.rand() - .5)

# ---- a mensagem ----
for i in range(len(MESSAGE)):
    n = int(0.05 * SR); put(np.sign(np.sin(2 * np.pi * 1400 * np.arange(n) / SR)) * np.exp(-np.arange(n) / n * 3), c2 + TYPE_AT + i * TYPE_STEP, 0.03)
a = c2 + TYPE_AT + len(MESSAGE) * TYPE_STEP
put(digital(0.4, 1.0), a, 0.1)
put(boom(1.6, 60, 24, 0.5, 0.4), a)

# ---- as telas mostram esta sala: o zumbido corta ----
cut = 1 - seg(c3, END_CARD, 0.01) * 0.85
mixL *= cut; mixR *= cut
put(digital(0.6, 1.0), c3, 0.16)
put(boom(2.2, 64, 22, 0.8, 0.5), c3)
put(digital(0.3, 1.0), c3 + 4.0, 0.1)
put(boom(1.2, 56, 24, 0.4, 0.3), c3 + 4.0)

# ---- as telas apagam ----
for i in range(12):
    put(click(), a5 + 1.0 + i * 0.5, 0.3)

# ---- a câmera perde o sinal ----
put(digital(0.4, 1.0), END_CARD - 0.4, 0.2)

finish()
