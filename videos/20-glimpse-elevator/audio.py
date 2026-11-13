from synth import *
from timeline import OPEN, CLOSE, EVENTS

# ---- cabine: zumbido da fluorescente e ventilação ----
add(np.sin(2 * np.pi * 120 * T) + 0.5 * np.sin(2 * np.pi * 240 * T) + 0.25 * np.sin(2 * np.pi * 360 * T), 0.005)
add(lp(white, 450) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * T)), 0.04)
add(bp(white, 2500, 7000), 0.003)

# ---- ding e portas ----
put(bell(1046.5, 1.6, 2.6) + 0.7 * bell(830.6, 1.6, 2.6), OPEN[0] - 0.25, 0.05)
for a, b in (OPEN, CLOSE):
    n = int((b - a) * SR); tv = np.arange(n) / SR
    motor = (np.sin(2 * np.pi * 95 * tv) * 0.5 + bp(rs.randn(n), 200, 1500)) * np.sin(np.pi * tv / (b - a)) ** 0.5
    put(motor, a, 0.03)
put(boom(0.6, 90, 50, 1.0, 0.8), CLOSE[1] - 0.02, 0.05)          # as portas batem

# ---- corredor aberto: ar mais grave e vazio ----
add(lp(white, 140) * seg(OPEN[0], CLOSE[1], 0.5), 0.07)

# ---- o cabo estala quando a cabine sente um peso ----
n = int(0.5 * SR); tv = np.arange(n) / SR
creak = bp(np.sign(np.sin(2 * np.pi * (120 + 30 * np.sin(tv * 11)) * tv)) * (rs.rand(n) > 0.55), 120, 800) * np.sin(np.pi * tv / 0.5)
put(creak, CLOSE[1] + 0.35, 0.05)

# ---- glitch ----
put(digital(0.3, 1.0), EVENTS[0][0], 0.06)

finish()
