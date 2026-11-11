"""Som do survive: a skin faz os sons do mundo a partir dos eventos da física, e aqui fica a tensão,
que é igual em toda skin: zumbido grave quando a vida cai, e o coração no fim dela.

Uso no audio.py do vídeo, depois de `from synth import *`:
    from modelos.survive import sound
    sound.night()        # a skin e a tensão
    ...                  # sons só do vídeo, como o do fim
    sound.master()       # comprime para o volume do TikTok; logo antes do finish()
    finish()
"""
import numpy as np
import synth as A
import timeline as tl
from modelos.survive import sim as S


def night():
    skin = S.skin_of(tl)
    c = S.config(tl)
    cfg = dict(getattr(skin, 'CFG', {})); cfg.update(getattr(tl, 'SKIN_CFG', {}))
    s = S.Sim(c, visual=False).run()
    T, SR = A.T, A.SR
    hp = np.interp(T, np.arange(len(s.frames)) / S.FPS, s.frames)
    if hasattr(skin, 'sound'):
        skin.sound(s, cfg, A, hp)

    until = c['until']
    won = s.dead_at is None or s.dead_at > until
    end = until + 0.5 if won else A.TOTAL
    tens = np.clip(1 - hp / 55, 0, 1) ** 2 * (T < end)
    drone = np.sin(2 * np.pi * 49 * T) + np.sin(2 * np.pi * 51.7 * T) + 0.4 * np.sin(2 * np.pi * 98.3 * T)
    A.add(drone * 0.12 * tens)
    tb = 0.0
    while tb < min(until, A.TOTAL):
        h = np.interp(tb, T[::441], hp[::441])
        if 0 < h < 25:
            for k, g in ((0, 1), (0.22, 0.7)):
                n = int(0.18 * SR); tv = np.arange(n) / SR
                A.put(np.sin(2 * np.pi * 52 * tv) * np.exp(-tv * 22), tb + k, (0.9 * (1 - h / 25) + 0.3) * g)
            tb += 60 / (70 + (25 - h) * 3)
        else:
            tb += 0.1
    return s


def master(drive=2.2):
    """Compressor lento e saturação: tira os picos (trovão, impacto) para o resto subir."""
    for ch in (A.mixL, A.mixR):
        env = A.lp(np.abs(ch), 8)
        ref = np.percentile(env, 95)
        ch *= 1 / np.maximum(1, env / ref) ** 0.6
        pk = np.abs(ch).max()
        ch[:] = np.tanh(ch / pk * drive) / np.tanh(drive)
