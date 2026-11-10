# (shot, duração, legendas [(início, fim, texto)])
import numpy as np

from modelos import choose_planet as MODELO
from modelos.choose_planet import *
SHOTS = [
 ('intro', 5.0,  [(0.3, 5.0, 'Choose one. You stay for 24 hours.')]),
 ('p1a', 6.0, [(NAME_HOLD + 0.5, 6.0, 'The sky glows every single night.')]),
 ('p1b', 3.75, [(0.2, 3.75, 'The lights hum a soft melody.')]),
 ('p1c', 3.5,  [(0.2, 3.5,  'You will sleep better than ever.')]),
 ('p1d', 4.0,  [(0.1, 2.35, 'Everyone who came is still here.'), (2.35, 4.0, 'Nobody has woken up.')]),
 ('p2a', 6.0, [(NAME_HOLD + 0.5, 6.0, 'Corn from pole to pole.')]),
 ('p2b', 3.75, [(0.2, 3.75, 'A scarecrow every hundred steps.')]),
 ('p2c', 3.5,  [(0.2, 3.5,  'They all face the path.')]),
 ('p2d', 4.0,  [(0.1, 2.0,  'Count them again.'), (2.0, 4.0, 'There is one more.')]),
 ('p3a', 6.0, [(NAME_HOLD + 0.5, 6.0, 'A dry plain. One stone well.')]),
 ('p3b', 3.75, [(0.2, 3.75, 'Drop a stone. It never lands.')]),
 ('p3c', 3.5,  [(0.2, 3.5,  'Lean over. Listen closely.')]),
 ('p3d', 4.0,  [(0.1, 1.9,  'Nothing. Not a sound.'), (1.9, 4.0, 'It throws it back.')]),
 ('p4a', 6.25, [(NAME_HOLD + 0.5, 6.25, 'A black sea. One city of green stone.')]),
 ('p4b', 3.25, [(0.2, 3.25, 'Its angles are wrong.')]),
 ('p4c', 3.25, [(0.2, 3.25, 'Something sleeps beneath it. It dreams.')]),
 ('p4d', 4.5,  [(0.1, 1.65, 'You are part of its dream.'), (1.65, 3.8,  'At hour 24, it wakes.')]),
]
PLANETS = [('PLANET 1', 'THE AURORA', 'p1a'), ('PLANET 2', 'THE FIELD', 'p2a'),
           ('PLANET 3', 'THE WELL', 'p3a'), ('PLANET 4', 'THE SPIRES', 'p4a')]
TOTAL, START, END_CARD = timing(SHOTS, END_SECS)

EXTRA_AT = 2.0                  # no p2d, aparece um espantalho a mais no meio da trilha
STONE_AT = 1.9                  # no p3d, a pedra volta do fundo do poço
ALIGN_AT = 2.8                  # no p4d, as estrelas terminam de se alinhar e a porta abre

# eventos de glitch: (tempo global, força, duração)
EVENTS = base_events(SHOTS, PLANETS, START)
EVENTS.append((START['p1d'] + 2.35, 0.45, 0.12))
EVENTS.append((START['p2d'] + EXTRA_AT, 0.6, 0.15))
EVENTS.append((START['p3d'] + STONE_AT, 1.0, 0.35))
EVENTS.append((START['p4d'] + ALIGN_AT, 0.8, 0.25))
EVENTS.append((END_CARD - 0.25, 1.0, 0.33))
# quadros subliminares: (tempo global, shot, frame)
SUBLIM = [(START['p1d'] + 3.55, 'p3d', 34), (START['p2c'] + 2.9, 'p4c', 45)]
SUBLIM_GRADE = 'p4'

VOICE = {
    'voice': 'bm_lewis', 'lang': 'en-gb', 'speed': 0.95,
    'name_at': 0.35,
    'names': {'p1a': 'Planet one. The Aurora.', 'p2a': 'Planet two. The Field.',
              'p3a': 'Planet three. The Well.', 'p4a': 'Planet four. The Spires.'},
}

GRADE = {  # saturação, contraste, tint RGB, lift
 'intro': (0.9, 1.05, (1.0, 0.98, 1.0), 0.02),
 'p1': (1.15, 1.04, (0.94, 1.02, 1.06), 0.02),
 'p2': (0.6, 1.02, (1.05, 1.0, 0.86), 0.03),
 'p3': (0.45, 1.2, (1.08, 0.98, 0.84), 0.02),
 'p4': (0.85, 1.1, (0.9, 1.06, 0.98), 0.0),
}

WARP = {'p4b': (0.3, 0.6), 'p4c': (0.6, 1.0), 'p4d': (1.0, 1.4)}    # força da distorção no começo e no fim do take


def warp(a, k, rt):
    """ângulos errados: linhas e colunas escorregam devagar, com ondas longas"""
    h, w = a.shape[:2]
    rows = np.arange(h)
    off = np.round(k * (6 * np.sin(rows * 0.011 + rt * 1.1) + 3 * np.sin(rows * 0.031 - rt * 0.7))).astype(int)
    idx = (np.arange(w)[None, :] + off[:, None]) % w
    a = np.take_along_axis(a, idx[..., None].repeat(3, 2), 1)
    cols = np.arange(w)
    off = np.round(k * 4 * np.sin(cols * 0.008 - rt * 0.9)).astype(int)
    idx = np.clip(np.arange(h)[:, None] + off[None, :], 0, h - 1)
    return np.take_along_axis(a, idx[..., None].repeat(3, 2), 0)


def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    if shot in WARP:
        k0, k1 = WARP[shot]
        dur = dict((s[0], s[1]) for s in SHOTS)[shot]
        k = k0 + (k1 - k0) * min(1.0, rt / dur)
        if shot == 'p4d' and rt > ALIGN_AT:
            k += 3.0 * min(1.0, (rt - ALIGN_AT) / 0.8)
        return warp(a, k, rt)
    return a
