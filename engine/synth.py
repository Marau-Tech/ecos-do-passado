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

def chord(fs, a=1.0):
    return sum(np.sin(2 * np.pi * f * T + i) for i, f in enumerate(fs)) * a / len(fs)
def bell(f, dur=1.4, decay=3.0):
    n = int(dur * SR); tv = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tv) + 0.4 * np.sin(2 * np.pi * f * 2.01 * tv) * np.exp(-tv * 4) + 0.15 * np.sin(2 * np.pi * f * 4.1 * tv) * np.exp(-tv * 9)) * np.exp(-tv * decay)

def digital(dur=0.4, g=1.0):
    """chiado digital: tons quadrados que saltam, com poucos bits"""
    n = int(dur * SR); tv = np.arange(n) / SR
    k = int(dur / 0.028) + 2
    f = np.repeat(300 + 3600 * rs.rand(k), int(0.028 * SR) + 1)[:n]
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.6 + rs.randn(n) * 0.5
    x = np.round(x * 3) / 3
    x = x * (np.repeat(rs.rand(k) > 0.25, int(0.028 * SR) + 1)[:n])
    return hp(x, 500) * np.minimum(1, (dur - tv) * 30) * g

def click(g=1.0):
    n = int(0.05 * SR); tv = np.arange(n) / SR
    return (hp(rs.randn(n), 1200) * np.exp(-tv * 160) + np.sin(2 * np.pi * 180 * tv) * np.exp(-tv * 90) * 0.6) * g

def beep(f=1000, dur=0.12, g=1.0, square=False):
    """bipe curto, de contagem de filme ou de teste"""
    n = int(dur * SR); tv = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * tv)
    if square: x = np.sign(x)
    return x * np.minimum(1, np.minimum(tv * 400, (dur - tv) * 400)) * g

def attention(dur=8.0, g=1.0):
    """tom de atenção do EAS: 853 e 960 Hz juntos"""
    n = int(dur * SR); tv = np.arange(n) / SR
    return (np.sin(2 * np.pi * 853 * tv) + np.sin(2 * np.pi * 960 * tv)) * 0.5 * np.minimum(1, np.minimum(tv * 200, (dur - tv) * 60)) * g

def afsk(bits, g=1.0):
    """bits em AFSK a 520,83 baud, como o cabeçalho SAME do EAS (marca 2083,3 Hz, espaço 1562,5 Hz)"""
    per = SR / 520.83
    f = np.repeat(np.where(np.asarray(bits) > 0, 2083.3, 1562.5), int(per) + 1)[:int(len(bits) * per)]
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * g

def same_header(t0, g=0.35, burst=0.9):
    """três rajadas do cabeçalho SAME com 1s de pausa; devolve quando acabam"""
    bits = (rs.rand(int(burst * 520.83)) > 0.5)
    for i in range(3):
        put(afsk(bits, g), t0 + i * (burst + 1.0))
    return t0 + 3 * burst + 2.0

def eom(t0, g=0.35):
    """fim de mensagem: três rajadas curtas"""
    bits = (rs.rand(int(0.25 * 520.83)) > 0.5)
    for i in range(3):
        put(afsk(bits, g), t0 + i * 1.0)
    return t0 + 2.25

def downlink(dur, g=1.0):
    """dados de telemetria chegando: FSK rápido abafado, com chiado de portadora"""
    n = int(dur * SR); tv = np.arange(n) / SR
    k = int(dur * 1200) + 2
    f = np.repeat(np.where(rs.rand(k) > 0.5, 2400.0, 1200.0), int(SR / 1200) + 1)[:n]
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 + bp(rs.randn(n), 800, 3000) * 0.5
    x = bp(x, 500, 3200) * (0.75 + 0.25 * np.sin(2 * np.pi * 3.1 * tv))
    return x * np.minimum(1, np.minimum(tv * 40, (dur - tv) * 40)) * g

def muzak(a, b, root=220.0, beat=2.4, g=1.0):
    """música de previsão do tempo: acordes com sétima, macios, com trêmolo; devolve a faixa inteira"""
    prog = [(0, 4, 7, 11), (-3, 0, 4, 7), (2, 5, 9, 12), (-5, -1, 2, 5)]      # Imaj7 vi7 ii7 V7, em semitons
    x = np.zeros(N)
    for i in range(int((b - a) / beat) + 1):
        t0 = a + i * beat
        fs = [root * 2 ** (st / 12) for st in prog[i % 4]]
        x += chord(fs) * seg(t0, min(b, t0 + beat + 0.3), 0.25)
        x += np.sin(2 * np.pi * fs[0] / 2 * T) * seg(t0, min(b, t0 + beat * 0.6), 0.05) * 0.5
    return lp(x, 2600) * (0.85 + 0.15 * np.sin(2 * np.pi * 5 * T)) * seg(a, b, 0.4) * g

def narrate(L, R):
    """abaixa a trilha enquanto o narrador fala e soma a voz depois da fita"""
    import voice
    v, spans = voice.track(N, SR)
    duck = np.clip(sum(seg(a - 0.1, b + 0.15, 0.1) for a, b in spans), 0, 1)
    bed = 1 - 0.55 * duck
    L, R = L * bed + v * 0.6, R * bed + v * 0.6
    return np.stack([L, R]) / max(1.0, max(np.abs(L).max(), np.abs(R).max()) / 0.95)

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
    if END_CARD < TOTAL:
        cut = int(END_CARD * SR)
        mixL[cut:] = 0; mixR[cut:] = 0
        if globals().get('END_TONE', True):
            put(attention((N - cut) / SR - 0.04), END_CARD + 0.03, 0.12)
        add(hp(white, 2500) * 0.016 * seg(END_CARD, TOTAL, 0.01))

    L, R = tape(mixL), tape(mixR)
    pk = max(np.abs(L).max(), np.abs(R).max()); L, R = L / pk * 0.89, R / pk * 0.89
    if 'VOICE' in globals():
        L, R = narrate(L, R)
    if globals().get('LOOP'):        # vídeo em loop: emenda sem estalo
        k = int(0.03 * SR); ramp_ = np.linspace(0, 1, k)
        for ch in (L, R):
            ch[:k] *= ramp_; ch[-k:] *= ramp_[::-1]
    wavfile.write(f'{OUT}/audio.wav', SR, (np.stack([L, R], 1) * 32767).astype(np.int16))
    print('ok', TOTAL, 's  pico', pk, ' rms', np.sqrt((L ** 2).mean()))
    for name, dur, _ in SHOTS:
        i, j = int(START[name] * SR), int((START[name] + dur) * SR)
        print(f'{name:6s} rms {np.sqrt((L[i:j] ** 2).mean()):.3f} pico {np.abs(L[i:j]).max():.2f}')
