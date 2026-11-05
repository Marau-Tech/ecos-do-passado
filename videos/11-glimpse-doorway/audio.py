from synth import *
from timeline import GONE

# ---- quarto: ventoinha do notebook e zumbido ----
add(lp(white, 600) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.31 * T)), 0.04)
add(np.sin(2 * np.pi * 120 * T) + 0.5 * np.sin(2 * np.pi * 240 * T), 0.004)
add(bp(white, 3000, 9000), 0.006)                     # chiado do microfone embutido

# ---- o rosto some: um rangido baixo e o glitch ----
n = int(0.9 * SR); tv = np.arange(n) / SR
creak = bp(np.sign(np.sin(2 * np.pi * (180 + 40 * np.sin(tv * 9)) * tv)) * (rs.rand(n) > 0.6), 150, 900) * np.sin(np.pi * tv / 0.9)
put(creak, GONE - 0.5, 0.05)
put(digital(0.25, 1.0), GONE - 0.1, 0.06)

finish()
