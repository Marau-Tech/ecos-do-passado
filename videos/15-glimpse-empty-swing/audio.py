from synth import *
from timeline import PERIOD, EVENTS

# ---- fim de tarde: ar parado, trânsito longe, motor da câmera ----
add(lp(white, 300) * (0.8 + 0.2 * smooth_noise(0.3, 2)), 0.05)
add(np.sin(2 * np.pi * 47 * T) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.5 * T)), 0.004)

# ---- grilos: trilos curtos em ritmo fixo, que fecha em 12s ----
for k, (f, rate, ph, pan) in enumerate([(4300, 1.5, 0.1, -0.5), (4700, 2.0, 0.37, 0.6), (3900, 1.0, 0.8, 0.1)]):
    gate = (np.sin(2 * np.pi * rate * T + ph * 6.28) > 0.3) * (np.sin(2 * np.pi * 30 * T) > 0)
    add(np.sin(2 * np.pi * f * T) * lp(gate.astype(float), 400), 0.004, pan)

# ---- rangido da corrente nos dois extremos de cada balançada ----
def creak(f, dur=0.38):
    n = int(dur * SR); tv = np.arange(n) / SR
    fi = f * (1 + 0.06 * np.sin(2 * np.pi * 7 * tv) + 0.03 * rs.randn(n).cumsum() / np.sqrt(n))
    x = ((np.cumsum(fi) / SR) % 1.0) * 2 - 1
    x = bp(x, f * 0.8, f * 4) * (np.abs(np.sin(2 * np.pi * 38 * tv)) ** 3)
    return x * np.sin(np.pi * tv / dur) ** 0.6

c_fwd, c_back = creak(760), creak(640)
t0 = PERIOD / 4
while t0 < TOTAL:
    k = round((t0 - PERIOD / 4) / (PERIOD / 2))
    put(c_fwd if k % 2 == 0 else c_back, t0 - 0.15, 0.035, pan=-0.15)
    t0 += PERIOD / 2

# ---- o glitch: a fita estica e o som cai de tom ----
tt, s, d = EVENTS[0]
n = int(0.45 * SR); tv = np.arange(n) / SR
wob = np.sin(2 * np.pi * np.cumsum(220 * (1 - 0.6 * tv / 0.45)) / SR) * np.exp(-tv * 4)
put(lp(wob, 1200), tt, 0.05)

finish()
