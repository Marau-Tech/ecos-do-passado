"""Piscina coberta vazia de madrugada, vista por uma câmera de segurança fixa. Pegadas molhadas saem da água
em direção à câmera; no glitch elas somem e a água se agita, até voltar ao quadro do começo."""
from lib import *
import timeline as TL

SHOTS = {'a': 12.0}
HOLD_STATES = True


def annulus(name, m, n_=40):
    v = []; t = []
    for i in range(n_):
        a = 2 * math.pi * i / n_
        v += [(0.9 * math.cos(a), 0.9 * math.sin(a), 0.0), (1.0 * math.cos(a), 1.0 * math.sin(a), 0.0)]
    for i in range(n_):
        j = (i + 1) % n_
        t += [(2 * i, 2 * i + 1, 2 * j), (2 * i + 1, 2 * j + 1, 2 * j)]
    return fast_mesh(name, np.array(v, np.float32), np.array(t, np.int32), m)


def build_a():
    reset(48)
    world_flat((0.01, 0.012, 0.015), 0.3)
    tile = simple('tile', (0.62, 0.64, 0.64), 0.35)
    wall = simple('wall', (0.5, 0.52, 0.52), 0.8)
    box('deckF', (16, 8.5, 0.1), (0, -1.75, -0.05), tile); box('deckB', (16, 1.5, 0.1), (0, 15.25, -0.05), tile)
    box('deckL', (4, 12, 0.1), (-6, 8.5, -0.05), tile); box('deckR', (4, 12, 0.1), (6, 8.5, -0.05), tile)
    for x in (-4.0, 4.0):
        box('wallP', (0.1, 12, 1.0), (x, 8.5, -0.55), simple('poolwall', (0.3, 0.45, 0.5), 0.4))
    box('wallPF', (8, 0.1, 1.0), (0, 2.5, -0.55), simple('poolwall', (0.3, 0.45, 0.5), 0.4))
    box('wallPB', (8, 0.1, 1.0), (0, 14.5, -0.55), simple('poolwall', (0.3, 0.45, 0.5), 0.4))
    box('ceil', (16, 24, 0.1), (0, 5, 5.0), simple('ceilm', (0.35, 0.35, 0.35), 0.9))
    box('wallB', (16, 0.1, 5), (0, 16, 2.5), wall); box('wallF', (16, 0.1, 5), (0, -6, 2.5), wall)
    box('wallL', (0.1, 24, 5), (-8, 5, 2.5), wall); box('wallR', (0.1, 24, 5), (8, 5, 2.5), wall)
    box('basin', (8.4, 12, 0.05), (0, 8.5, -1.05), simple('bed', (0.08, 0.3, 0.36), 0.5))
    water = box('water', (8, 12, 0.04), (0, 8.5, -0.12), simple('water', (0.04, 0.16, 0.2), 0.04))
    box('edge', (8.8, 0.4, 0.06), (0, 2.3, 0.0), simple('coping', (0.8, 0.82, 0.82), 0.4))
    for x in (-3.0, -1.0, 1.0, 3.0):                  # faixas do fundo e boias das raias
        box('lane', (0.25, 11.5, 0.02), (x, 8.5, -1.0), simple('lane', (0.02, 0.05, 0.08), 0.5))
    bead_a = simple('beadA', (0.8, 0.1, 0.1), 0.5); bead_b = simple('beadB', (0.85, 0.85, 0.85), 0.5)
    for x in (-2.0, 0.0, 2.0):
        for i, y in enumerate(np.arange(3.0, 14.3, 0.6)):
            box('bead', (0.12, 0.3, 0.1), (x, y, -0.07), bead_a if i % 4 < 2 else bead_b)
    # cadeira do salva-vidas e escada
    steel = simple('steel', (0.55, 0.57, 0.6), 0.3, 0.8)
    for dx in (-0.35, 0.35):
        for dy in (-0.3, 0.3):
            box('leg', (0.08, 0.08, 1.9), (-5.0 + dx, 4.8 + dy, 0.95), simple('chairleg', (0.8, 0.8, 0.78), 0.6))
    box('seat', (0.9, 0.8, 0.1), (-5.0, 4.8, 1.9), simple('chairseat', (0.85, 0.85, 0.82), 0.6))
    box('back', (0.9, 0.08, 0.6), (-5.0, 5.15, 2.25), simple('chairback', (0.85, 0.85, 0.82), 0.6))
    for dx in (-0.2, 0.2):
        box('rail', (0.05, 0.05, 1.2), (4.2 + dx, 2.6, 0.6), steel)
    for z in (0.3, 0.6, 0.9):
        box('rung', (0.45, 0.04, 0.04), (4.2, 2.6, z), steel)
    # luz fluorescente fria
    lamp = emission('tube', (0.8, 0.9, 1.0), 3.0)
    for y in (-1.0, 4.0, 9.0):
        box('light', (6.0, 0.3, 0.06), (0, y, 4.9), lamp)
        point((0, y, 4.5), 180.0, (0.8, 0.9, 1.0), 0.5)
    # pegadas molhadas da água até a câmera, uma por vez, em ziguezague
    wet = simple('wet', (0.1, 0.11, 0.12), 0.05)
    prints = []
    for k in range(TL.STEPS):
        y = 1.8 - k * 0.42
        x = 0.7 + (0.16 if k % 2 else -0.16)
        p = ico('print', 1.0, (x, y, 0.004), wet, 2); p.scale = (0.085, 0.19, 0.004)
        p.rotation_euler.z = math.radians(-6 if k % 2 else 6)
        prints.append(p)
    rings = [annulus('ring', simple('ripple', (0.45, 0.6, 0.65), 0.1)) for _ in TL.RINGS]
    for r in rings:
        r.location = (0.0, 8.5, -0.095)
    camera((0.0, -4.5, 2.6), (0.0, 6.5, 0.2), 20)

    def upd(t, u):
        shown = 0 if t >= TL.RESET else int(min(TL.STEPS, max(0, (t - TL.STEP_T0) // TL.STEP_DT + 1)))
        for k, p in enumerate(prints):
            p.hide_render = k >= shown
        st = []
        for r, t0 in zip(rings, TL.RINGS):
            a = t - TL.RESET - t0
            on = 0 <= a < 1.9
            r.hide_render = not on
            if on:
                s = 0.4 + a * 2.2
                r.scale = (s, s, 1.0)
                st.append(round(a * 15))
            else:
                st.append(None)
        return (shown, tuple(st))
    return upd
