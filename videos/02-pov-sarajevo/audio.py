"""Paisagem sonora de Sarajevo, 28 de junho de 1914."""
from synth import *

i0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11 = (
    START[s] for s in (
        'intro', 't1', 't2', 't3', 't4', 't5',
        't6', 't7', 't8', 't9', 't10', 't11'
    )
)

# ---- Ambiente urbano: ar, vozes distantes e movimento da rua ----
air = bp(white, 180, 1400) * (0.65 + 0.35 * smooth_noise(0.25, 12))
add(air * seg(i0, END_CARD, 1.5), 0.035)

crowd = bp(white, 250, 2200) * (0.65 + 0.35 * smooth_noise(0.8, 15))
add(crowd * seg(t1, t4, 1.0), 0.045)
add(crowd * seg(t5, t8, 1.0), 0.025)
add(crowd * seg(t9, t11, 0.5), 0.055)

# Pequenas variações de vozes indistintas ao fundo.
for k, t0 in enumerate(np.arange(t1 + 0.5, t4, 1.8)):
    dur = rs.uniform(0.25, 0.65)
    n = int(dur * SR)
    tv = np.arange(n) / SR
    voice = bp(rs.randn(n), 350, 1800)
    env = np.sin(np.pi * tv / dur) ** 2
    put(voice * env, t0, rs.uniform(0.008, 0.018),
        pan=rs.uniform(-0.5, 0.5))

# ---- Passos sobre pedra ----
def stone_step(g=1.0):
    n = int(0.16 * SR)
    tv = np.arange(n) / SR
    noise = bp(rs.randn(n), 180, 2400)
    return noise * np.exp(-tv * 28) * g

for a, b, gap in (
    (i0 + 2, t1, 0.62),
    (t1, t2, 0.68),
    (t5, t6, 0.72),
    (t8, t9, 0.70),
):
    for k, t0 in enumerate(np.arange(a, b, gap)):
        put(stone_step(), t0, 0.055,
            pan=-0.18 if k % 2 else 0.18)

# ---- Cortejo: rodas, cavalos e motor do automóvel ----
def hoof(g=1.0):
    return click(g)

for k, t0 in enumerate(np.arange(t2, t5, 0.42)):
    put(hoof(), t0, 0.12, pan=-0.2 if k % 2 else 0.2)

# Ruído grave das rodas e dos motores, aumentando na aproximação.
engine = lp(white, 115) * (
    0.7 + 0.3 * np.sin(2 * np.pi * 2.2 * T)
)
add(engine * seg(t2, t4, 1.0), 0.045)
add(engine * seg(t6, t8, 1.0), 0.035)
add(engine * seg(t9, t11, 0.5), 0.055)

# ---- Primeiro atentado e reação da multidão ----
put(boom(2.4, 75, 28, 1.0, 0.75), t4 + 4.0, 0.28)
add(bp(white, 500, 3500) * seg(t4 + 4.0, t5 + 2.0, 0.2), 0.025)

# A multidão fica mais intensa logo após a explosão.
add(crowd * seg(t4 + 4.0, t6, 0.3), 0.09)

# ---- Prefeitura: ambiente mais fechado e discreto ----
room = lp(white, 650) * (0.7 + 0.3 * smooth_noise(0.35, 20))
add(room * seg(t6, t8, 0.8), 0.025)

# ---- Retorno e Ponte Latina ----
for k, t0 in enumerate(np.arange(t9, t10 + 1.0, 0.48)):
    put(hoof(0.7), t0, 0.10,
        pan=-0.15 if k % 2 else 0.15)

# Pequena pausa do automóvel antes dos disparos.
# Dois impactos secos, sem exagero cinematográfico.
put(click(1.0), t10 + 8.0, 0.75, pan=-0.12)
put(click(1.0), t10 + 8.35, 0.75, pan=0.12)

# Reação sonora da rua depois dos disparos.
add(bp(white, 350, 2600) * seg(t10 + 8.2, t11 + 4.0, 0.3), 0.07)

# ---- Encerramento ----
add(chord((110, 138.6, 164.8)) * seg(t11 + 8.0, END_CARD, 1.5), 0.018)

finish()
