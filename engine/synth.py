"""Núcleo do áudio: mix, filtros, efeitos comuns e passagem pela fita."""
import os, sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from project import OUT
from timeline import *

SR = 44100
N = int(TOTAL * SR)
T = np.arange(N) / SR
rs = np.random.RandomState(4)
mixL = np.zeros(N); mixR = np.zeros(N)

def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)
def seg(a, b, fade=0.05):
    e = np.zeros(N); i, j = int(a * SR), min(N, int(b * SR)); e[i:j] = 1
    k = int(fade * SR)
    if k and j - i > 2 * k:
        e[i:i + k] = np.linspace(0, 1, k); e[j - k:j] = np.linspace(1, 0, k)
    return e
def add(x, g=1.0, pan=0.0):
    global mixL, mixR
    mixL += x * g * (1 - pan * 0.5); mixR += x * g * (1 + pan * 0.5)
def put(buf, t0, g=1.0, pan=0.0):
    i = int(t0 * SR); j = min(N, i + len(buf))
    if j <= i: return
    mixL[i:j] += buf[:j - i] * g * (1 - pan * 0.5); mixR[i:j] += buf[:j - i] * g * (1 + pan * 0.5)
def smooth_noise(rate, seed=0):
    r = np.random.RandomState(seed); k = int(TOTAL * rate) + 2
    return np.interp(T, np.arange(k) / rate, r.randn(k))
def boom(dur=2.5, f0=62, f1=24, g=1.0, noisy=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    nz = lp(rs.randn(n), 220) * np.exp(-t * 3.0) * noisy * 2
    return (s + nz) * g

white = rs.randn(N)
# ---- camada de fita ----
add(hp(white, 2500) * 0.016)
add(lp(white, 900) * 0.010)
add(np.sin(2 * np.pi * 60 * T) * 0.010 + np.sin(2 * np.pi * 180 * T) * 0.004)

def tape(x):
    wow = 0.0016 * np.sin(2 * np.pi * 0.7 * T) + 0.0005 * np.sin(2 * np.pi * 6.1 * T) + 0.0009 * smooth_noise(2.3, 9)
    pos = np.clip(np.arange(N) + np.cumsum(wow), 0, N - 1)
    y = np.interp(pos, np.arange(N), x)
    y = lp(hp(y, 28), 8200)
    return np.tanh(y * 1.25)

def finish():
    """bipes de legenda, estática, tom final, fita e gravação"""
    # ---- bipes de legenda e estática dos glitches ----
    for name, dur, caps in SHOTS:
        for c0, c1, s in caps:
            n = int(0.075 * SR); tv = np.arange(n) / SR
            put(np.sign(np.sin(2 * np.pi * 980 * tv)) * np.exp(-tv * 45), START[name] + c0, 0.018)
    for tt, s, d in EVENTS:
        n = int(d * SR)
        x = hp(rs.randn(n), 900) * (0.5 + 0.5 * np.sign(np.sin(np.arange(n) / SR * 2 * np.pi * 59)))
        put(x, tt, 0.13 * s)

    # ---- tela final: silêncio e tom de alerta ----
    cut = int(END_CARD * SR)
    mixL[cut:] = 0; mixR[cut:] = 0
    n = N - cut - int(0.04 * SR); tv = np.arange(n) / SR
    v = (np.sin(2 * np.pi * 853 * tv) + np.sin(2 * np.pi * 960 * tv)) * 0.5 * np.minimum(1, np.minimum(tv * 200, (tv[-1] - tv) * 60))
    put(v, END_CARD + 0.03, 0.12)
    add(hp(white, 2500) * 0.016 * seg(END_CARD, TOTAL, 0.01))

    L, R = tape(mixL), tape(mixR)
    pk = max(np.abs(L).max(), np.abs(R).max()); L, R = L / pk * 0.89, R / pk * 0.89
    wavfile.write(f'{OUT}/audio.wav', SR, (np.stack([L, R], 1) * 32767).astype(np.int16))
    print('ok', TOTAL, 's  pico', pk, ' rms', np.sqrt((L ** 2).mean()))
    for name, dur, _ in SHOTS:
        i, j = int(START[name] * SR), int((START[name] + dur) * SR)
        print(f'{name:6s} rms {np.sqrt((L[i:j] ** 2).mean()):.3f} pico {np.abs(L[i:j]).max():.2f}')
