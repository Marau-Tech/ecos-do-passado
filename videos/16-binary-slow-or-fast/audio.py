from synth import *
from timeline import TURN, DAY

ia, ib = START['a1'], START['b1']
a3, b3 = START['a3'], START['b3']

# ---- intro: drone ----
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((49, 1, 0), (49.4, .9, 1), (73.5, .5, 2), (98.2, .3, 3))) * seg(0, ia, 0.6), 0.1)

# ---- A: tudo esticado e grave ----
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((36.7, 1, 0), (37.0, .8, 1), (55.0, .4, 2))) * seg(ia, ib, 0.4), 0.09)
rain = lp(white, 380) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.15 * T))           # chuva lenta e grave
add(rain * seg(START['a2'], ib, 0.4), 0.06)
t0, gap = ia + 0.3, 0.5                                                      # tique-taque cada vez mais espaçado
while t0 < a3:
    put(click(0.6), t0, 0.05)
    t0 += gap; gap *= 1.35
t0 = a3 + 0.05                                                               # bipes do visor de data, até travar
while t0 < a3 + TURN:
    put(beep(1800, 0.025), t0, 0.012)
    t0 += 0.07
put(beep(900, 0.35), a3 + TURN, 0.03)

# ---- B: tudo acelerado ----
day_env = 0.5 + 0.5 * np.sin(2 * np.pi * T / DAY)                            # uma rajada de vento por dia
add(bp(white, 200, 1400) * day_env ** 2 * seg(ib, b3 + TURN, 0.2), 0.05)
k = 0
for t0 in np.arange(START['b2'], b3 + TURN, 0.11):                           # passarinhos acelerados
    if rs.rand() < 0.55:
        n = int(0.05 * SR); tv = np.arange(n) / SR
        f = 3000 + 2500 * rs.rand() + 9000 * tv
        put(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tv / 0.05), t0, 0.01, pan=rs.uniform(-0.6, 0.6))
t0 = b3 + 0.05                                                               # riscos na parede, cada vez mais rápidos
while t0 < b3 + TURN:
    n = int(0.04 * SR); tv = np.arange(n) / SR
    put(bp(rs.randn(n), 1500, 6000) * np.exp(-tv * 60), t0, 0.06, pan=rs.uniform(-0.3, 0.3))
    t0 += max(0.018, 0.14 * (1 - (t0 - b3) / TURN))
# depois de "Alone.": nada além da fita

finish()
