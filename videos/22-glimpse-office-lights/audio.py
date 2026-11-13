from synth import *
from timeline import OFF, BACK

# ---- quantas faixas estão acesas a cada instante: 4 até o primeiro relé, 0 na última, 4 de novo no glitch ----
lit = np.full(N, 4.0)
for k, z in enumerate(OFF):
    lit -= seg(z, BACK, 0.03)
lit = lp(lit, 40)

# ---- zumbido das fluorescentes, mais fraco a cada faixa; a de perto pesa mais ----
hum = np.sin(2 * np.pi * 120 * T) + 0.45 * np.sin(2 * np.pi * 240 * T) + 0.25 * np.sin(2 * np.pi * 360 * T)
buzz = bp(white, 3500, 7000) * (0.7 + 0.3 * np.sin(2 * np.pi * 120 * T))
near = np.clip(lit - 3, 0, 1)                         # a faixa da câmera
far = np.clip(lit, 0, 3) / 3
add(hum * (0.4 * far + 0.6 * near), 0.012)
add(buzz * (0.3 * far + 0.7 * near), 0.004)

# ---- ar-condicionado e ventoinha do notebook, que não param ----
add(lp(white, 350) * (0.85 + 0.15 * smooth_noise(0.25, 3)), 0.035)
add(bp(white, 500, 1800) * (0.9 + 0.1 * np.sin(2 * np.pi * 0.4 * T)), 0.008)

# ---- tunc de cada relé: mais longe, mais abafado ----
for k, z in enumerate(OFF):
    n = int(0.35 * SR); tv = np.arange(n) / SR
    thud = (np.sin(2 * np.pi * 70 * tv) * np.exp(-tv * 18) + lp(rs.randn(n), 600) * np.exp(-tv * 30) * 0.8)
    thud = lp(thud, 500 + 600 * k)
    put(thud, z, 0.05 + 0.03 * k)

# ---- o glitch: as luzes voltam com o estalo dos reatores ----
put(digital(0.25, 1.0), BACK - 0.02, 0.05)
n = int(0.2 * SR); tv = np.arange(n) / SR
put(bp(rs.randn(n), 800, 5000) * np.exp(-tv * 25), BACK, 0.04)

finish()
