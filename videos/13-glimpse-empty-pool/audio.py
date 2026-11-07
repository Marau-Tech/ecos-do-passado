from synth import *
from timeline import STEP_T0, STEP_DT, STEPS, RESET

# ---- piscina coberta: filtragem, reverberação grave e zumbido da fluorescente ----
add(lp(white, 500) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * T)), 0.05)
add(np.sin(2 * np.pi * 100 * T) + 0.5 * np.sin(2 * np.pi * 200 * T) + 0.2 * np.sin(2 * np.pi * 300 * T), 0.004)
add(bp(white, 2000, 6000), 0.004)

# ---- pingos distantes ----
for t0 in (1.1, 5.4, 10.6):
    put(bell(1300, 0.6, 9.0), t0, 0.012)

# ---- passos molhados, um por pegada ----
for k in range(STEPS):
    n = int(0.18 * SR); tv = np.arange(n) / SR
    slap = lp(rs.randn(n), 900) * np.exp(-tv * 28)
    put(slap, STEP_T0 + k * STEP_DT, 0.06 + 0.012 * k, pan=-0.1)

# ---- a virada: o glitch e a água se agitando ----
put(digital(0.25, 1.0), RESET - 0.1, 0.06)
n = int(2.4 * SR); tv = np.arange(n) / SR
splash = bp(rs.randn(n), 300, 2500) * np.exp(-tv * 1.6) * (0.6 + 0.4 * np.sin(2 * np.pi * 3.0 * tv))
put(splash, RESET, 0.05)

finish()
