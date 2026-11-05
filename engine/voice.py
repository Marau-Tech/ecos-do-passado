"""Narração: lê as legendas e os nomes dos planetas com o Kokoro, que roda local na CPU."""
import numpy as np
from kokoro_onnx import Kokoro
from scipy.signal import butter, resample_poly, sosfilt
from project import ROOT
from timeline import END_CARD, SHOTS, START, VOICE

MODEL = f'{ROOT}/tools/kokoro'
MAX_SPEED = 1.25
GAP = 0.08          # respiro mínimo entre uma fala e a próxima
SILENCE = 0.01


def lines():
    """(início, texto) de cada fala, em ordem."""
    out = [(START[s] + VOICE['name_at'], name) for s, name in VOICE.get('names', {}).items()]
    out += [(START[name] + c0, text) for name, _, caps in SHOTS for c0, _, text in caps]
    return sorted(out)


def speak(k, text, speed):
    x, sr = k.create(text, voice=VOICE['voice'], speed=speed, lang=VOICE['lang'])
    i = np.flatnonzero(np.abs(x) > SILENCE)
    return x[i[0]:i[-1] + 1], sr


def fit(k, text, window):
    """Gera a fala e acelera só o necessário para caber na janela."""
    speed = VOICE['speed']
    x, sr = speak(k, text, speed)
    if len(x) / sr > window:
        speed = min(MAX_SPEED, speed * len(x) / sr / window)
        x, sr = speak(k, text, speed)
    return x, sr, speed


def tape_voice(x, sr, out_sr):
    """Faixa estreita, oscilação e saturação de fita velha."""
    x = resample_poly(x, out_sr, sr)
    n = np.arange(len(x))
    wow = out_sr * 0.0016 * np.sin(2 * np.pi * 0.7 * n / out_sr) + out_sr * 0.0004 * np.sin(2 * np.pi * 5.3 * n / out_sr)
    x = np.interp(n + wow, n, x)
    x = sosfilt(butter(2, [260, 3300], 'band', fs=out_sr, output='sos'), x)
    x = np.tanh(2.2 * x / np.abs(x).max())
    return x / np.abs(x).max()


def radio_voice(x, sr):
    """Voz saindo de um alto-falante pequeno, com zumbido e chiado."""
    x = sosfilt(butter(4, [550, 2300], 'band', fs=sr, output='sos'), x)
    n = np.arange(len(x))
    x = np.tanh(4.0 * x / np.abs(x).max()) * (0.8 + 0.2 * np.sign(np.sin(2 * np.pi * 60 * n / sr)))
    x = x + 0.06 * np.random.RandomState(3).randn(len(x))
    return x / np.abs(x).max()


def track(n, sr):
    """Devolve a faixa mono da voz e os trechos (início, fim) em que há fala."""
    k = Kokoro(f'{MODEL}/kokoro-v1.0.onnx', f'{MODEL}/voices-v1.0.bin')
    ls = lines()
    v = np.zeros(n)
    spans = []
    for (t0, text), nxt in zip(ls, [l[0] for l in ls[1:]] + [END_CARD]):
        window = nxt - t0 - GAP
        x, xsr, speed = fit(k, text, window)
        size = len(x) / xsr
        flag = '' if size <= window else '  PASSA DA JANELA'
        print(f'{t0:6.2f}s  {size:.2f}/{window:.2f}s  x{speed:.2f}  {text}{flag}')
        y = tape_voice(np.asarray(x, float), xsr, sr)
        if text in VOICE.get('radio', ()):
            y = radio_voice(y, sr)
        i = int(t0 * sr)
        j = min(n, i + len(y))
        v[i:j] += y[:j - i]
        spans.append((t0, t0 + size))
    return v, spans
