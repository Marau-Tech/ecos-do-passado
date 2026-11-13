from synth import *
from timeline import LIGHT_ON, LIGHT_OFF, LOOP_T, gust

# ---- noite de verão: ar, grilos e o motor da câmera ----
g = np.array([gust(t) for t in np.arange(0, TOTAL + 0.1, 0.05)])
genv = np.interp(T, np.arange(len(g)) * 0.05, g)
add(lp(white, 300) * (0.7 + 0.3 * genv), 0.04)
add(bp(white, 250, 1600) * genv ** 2, 0.03)                                    # rajadas de vento
add(np.sin(2 * np.pi * 47 * T) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.5 * T)), 0.003)

# grilos: trilos em ritmo fixo, que fecha em 12s
for f, rate, ph, pan in [(4300, 1.5, 0.1, -0.5), (4700, 2.0, 0.37, 0.6), (3900, 1.0, 0.8, 0.1), (5100, 0.75, 0.55, -0.2)]:
    gate = (np.sin(2 * np.pi * rate * T + ph * 6.28) > 0.3) * (np.sin(2 * np.pi * 30 * T) > 0)
    add(np.sin(2 * np.pi * f * T) * lp(gate.astype(float), 400), 0.004, pan)

# ---- o holofote: clique do relé, zumbido enquanto acende ----
put(click(1.0), LIGHT_ON, 0.08, pan=0.2)
put(click(0.8), LIGHT_OFF, 0.08, pan=0.2)
hum = (np.sin(2 * np.pi * 120 * T) + 0.4 * np.sin(2 * np.pi * 240 * T) + 0.2 * np.sign(np.sin(2 * np.pi * 120 * T)))
add(lp(hum, 900) * seg(LIGHT_ON, LIGHT_OFF, 0.02), 0.006, 0.2)

# ---- só dois lençóis batendo: um estalo de pano em cada virada do vento ----
for side, pan in ((-1, -0.55), (1, 0.55)):
    ph = side * 1.3
    for k in range(10):                                            # extremos da oscilação de 2,4s
        t0 = ((0.5 + k) * 1.2 - ph / (2 * np.pi) * 2.4) % LOOP_T
        n = int(0.22 * SR); tv = np.arange(n) / SR
        flap = bp(rs.randn(n), 180, 2400) * np.exp(-tv * 18) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 41 * tv)))
        put(flap, t0, 0.045 * gust(t0) ** 2, pan)

finish()
