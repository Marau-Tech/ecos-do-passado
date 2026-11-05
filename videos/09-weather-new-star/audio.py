from synth import *

ident, map1, map2, sky1, map3, fc, sky2 = (START[s[0]] for s in SHOTS)

# ---- vinheta e música de previsão do tempo, até a virada ----
put(bell(880, 1.2, 3.5), ident + 0.2, 0.06); put(bell(1318.5, 1.2, 3.5), ident + 0.45, 0.05)
add(muzak(ident + 0.2, map3, 220.0, 2.4), 0.06)

# ---- estúdio: zumbido baixo da transmissão ----
add(np.sin(2 * np.pi * 60 * T) * seg(0, END_CARD), 0.006)

# ---- câmera do céu: vento ----
for a, b in ((sky1, map3), (sky2, END_CARD)):
    add(lp(white, 420) * (0.6 + 0.4 * smooth_noise(0.5, 4)) * seg(a, b, 0.2), 0.045)

# ---- a virada: a música corta e fica um grave ----
put(digital(0.3, 1.0), map3, 0.08)
add((np.sin(2 * np.pi * 43 * T) + 0.6 * np.sin(2 * np.pi * 43.8 * T)) * seg(map3, END_CARD, 1.0), 0.05)
put(boom(1.6, 60, 24, 0.5, 0.4), sky2 + 3.6)          # "Do not look up"

finish()
