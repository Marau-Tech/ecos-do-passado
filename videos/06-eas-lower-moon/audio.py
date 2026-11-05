from synth import *
from timeline import WINDOWS_OFF, EOM_AT

pgm, tone, m1, m2, v1, m3, m4, v2, m5 = (START[s[0]] for s in SHOTS)

# ---- fim da programação: tom de teste ----
put(beep(1000, tone - 0.15, 1.0), 0.0, 0.08)

# ---- alerta: cabeçalho SAME e tom de atenção ----
t = same_header(tone + 0.2, 0.3, burst=0.5)
put(attention(tone + 5.4 - t), t, 0.32)

# ---- portadora: zumbido e chiado sob as mensagens ----
air = seg(m1, END_CARD, 0.2)
add((np.sin(2 * np.pi * 60 * T) + 0.4 * np.sin(2 * np.pi * 180 * T)) * air, 0.012)
add(bp(white, 2000, 7000) * air, 0.010)

# ---- câmeras: vento e um grave que cresce ----
for a, b, gr in ((v1, m3, 0.5), (v2, m5, 1.0)):
    e = seg(a, b, 0.15)
    add(lp(white, 380) * (0.6 + 0.4 * smooth_noise(0.5, 4)) * e, 0.05)
    add((np.sin(2 * np.pi * 41 * T) + 0.6 * np.sin(2 * np.pi * 41.7 * T)) * e, 0.05 * gr)
add(chord([55.0, 58.3, 82.4]) * seg(m3, v2, 0.8), 0.03)      # o grave não some nas instruções

# ---- as janelas apagam: um clique distante cada ----
for t0 in WINDOWS_OFF:
    put(lp(click(), 1800), v2 + t0, 0.5, rs.rand() - 0.5)

# ---- a emissora retoma: o grave para, rajada curta e fim de mensagem ----
cut = 1 - seg(m5, END_CARD, 0.02) * 0.9
mixL *= cut; mixR *= cut
put(digital(0.45, 1.0), m5, 0.16)
put(afsk(rs.rand(int(0.3 * 520.83)) > 0.5), m5 + 0.05, 0.3)
bits = rs.rand(int(0.25 * 520.83)) > 0.5
for i in range(3):
    put(afsk(bits), m5 + EOM_AT + i * 0.5, 0.3)

finish()
