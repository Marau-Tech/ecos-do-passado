from synth import *
from timeline import LIGHTS_OUT

def step(g=1.0):
    n = int(0.16 * SR)
    return bp(rs.randn(n), 180, 1600) * np.exp(-np.arange(n) / n * 6) * g
def shutter(g=1.0):
    n = int(0.09 * SR); tv = np.arange(n) / SR
    click = hp(rs.randn(n), 2200) * np.exp(-tv * 90)
    return (click + 0.6 * np.roll(click, int(0.035 * SR))) * g
def whine(dur=1.1):
    n = int(dur * SR); tv = np.arange(n) / SR
    f = 1400 + 3800 * (tv / dur) ** 0.6
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (tv / dur) ** 1.5 * (1 - tv / dur) ** 0.3

t1, t2, t3, t4 = (START[p[2]] for p in PLANETS)

# ---- intro: drone desafinado ----
e = seg(0, t1, 0.8)
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((44, 1, 0), (44.4, .9, 1), (66.0, .55, 2), (88.3, .4, 3), (132.0, .2, 4))) * e * (0.8 + 0.2 * np.sin(T * 1.3)), 0.11)

# ---- P1 THE EVENING: acordes mornos, vento no trigo, passos ----
e = seg(t1, t2, 0.6)
prog = [(196.0, 246.9, 293.7), (174.6, 220.0, 261.6), (146.8, 220.0, 293.7), (164.8, 196.0, 246.9)]
for i in range(int((t2 - t1) / 2.2) + 1):
    a = t1 + i * 2.2
    add(chord(prog[i % 4]) * seg(a, a + 2.3, 0.5) * e, 0.05)
    add(chord([f / 2 for f in prog[i % 4]]) * seg(a, a + 2.3, 0.5) * e, 0.04)
add(bp(white, 500, 2600) * (0.45 + 0.55 * smooth_noise(0.6, 3)) * e, 0.028, 0.1)
cr = np.sign(np.sin(2 * np.pi * 4100 * T)) * (np.sin(2 * np.pi * 7 * T) > 0.4) * (np.sin(2 * np.pi * 0.7 * T) > -0.2)
add(hp(cr, 3000) * e, 0.004, -0.4)
a = START['p1c']
for i in range(8):                                    # seus passos, até parar
    put(step(), a + 0.2 + i * 0.53, 0.12, 0.15 if i % 2 else -0.15)
a = START['p1d'] + 0.65                               # os passos que continuam sem você
for i in range(7):
    put(step(), a + i * 0.53, 0.11 * (1 - i / 9), 0.15 if i % 2 else -0.15)
a = START['p1d'] + 2.1                                # a música para
cut = 1 - seg(a, t2, 0.2) * 0.88
mixL *= cut; mixR *= cut

# ---- P2 THE BROADCAST: zumbido elétrico, estática, sintonia ----
e = seg(t2, t3, 0.4)
add((np.sin(2 * np.pi * 60 * T) + 0.5 * np.sin(2 * np.pi * 120 * T)) * e, 0.03)
add(bp(white, 1200, 5200) * (0.5 + 0.5 * smooth_noise(3, 6)) * seg(START['p2b'], t3, 0.5), 0.022)
tv = np.arange(int(2.6 * SR)) / SR                    # sintonia procurando
put(np.sin(2 * np.pi * np.cumsum(1600 + 900 * np.sin(tv * 1.9)) / SR) * np.sin(np.pi * tv / 2.6), START['p2b'] + 0.8, 0.012, 0.2)
for i in range(12):                                   # bipes de vigília do transmissor
    n = int(0.09 * SR)
    put(np.sin(2 * np.pi * 760 * np.arange(n) / SR) * np.hanning(n), t2 + 0.2 + i * 1.1, 0.012)
add(chord([73.4, 77.8, 110.0]) * seg(START['p2c'], START['p2d'] + 2.0, 0.6), 0.06)
a = START['p2d'] + 2.0                                # só a voz fica
put(boom(1.5, 70, 26, 0.5, 0.4), a)
cut = 1 - seg(a + 0.1, t3, 0.1) * 0.9
mixL *= cut; mixR *= cut
add(bp(white, 900, 3000) * seg(a + 0.1, t3 - 0.1, 0.05), 0.014)

# ---- P3 THE SHUTTER: quase nada, obturador e carga do flash ----
e = seg(t3, t4, 0.3)
add(lp(white, 200) * e, 0.012)
add(np.sin(2 * np.pi * 33 * T) * e, 0.04)
for shot, times in FLASHES.items():
    for dt in times:
        put(shutter(), START[shot] + dt, 0.3)
        if shot != 'p3d' or dt < 1:
            put(whine(), START[shot] + dt + 0.12, 0.012)
a = START['p3c'] + 2.7
put(boom(1.2, 60, 26, 0.35, 0.3), a)
a = START['p3d'] + 0.2
put(boom(1.6, 64, 24, 0.6, 0.4), a)
a = START['p3d'] + 3.4                                # o susto
n = int((t4 - a) * SR); tv = np.arange(n) / SR
u = tv / tv[-1]
sc = sum(np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.6 * u)) / SR) for f0 in (620, 742, 930, 1180, 1510))
put(np.tanh(sc * 1.5 + lp(rs.randn(n), 3000) * 6) * 0.3, a)
put(boom(1.4, 90, 28, 1.0, 0.9), a)
mute = 1 - seg(t4 - 0.02, t4 + 0.12, 0.004) * 0.92
mixL *= mute; mixR *= mute

# ---- P4 THE DIMMING: drone grave, relés apagando estrelas, o interruptor ----
end = END_CARD
out_at = START['p4d'] + LIGHTS_OUT
e = seg(t4, out_at, 0.3)
grow = np.clip((T - t4) / (out_at - t4), 0, 1)
add(np.sin(2 * np.pi * 36 * T) * e, 0.05)
add(lp(white, 240) * e * (0.5 + grow), 0.016)
add(sum(np.sin(2 * np.pi * f * T + i) for i, f in enumerate((110.0, 110.6, 164.8, 174.6))) * e * grow ** 2, 0.03)
for i in range(26):                                   # uma estrela por clique
    n = int(0.02 * SR)
    put(hp(rs.randn(n), 1800) * np.exp(-np.arange(n) / n * 7), START['p4c'] + (i + 0.5) * 3.3 / 26, 0.09, rs.rand() - .5)
a = START['p4d'] + 2.1                                # a estrela falha
add(bp(white, 700, 3400) * (np.sin(2 * np.pi * 7.5 * T) > 0) * seg(a, out_at, 0.02), 0.03)
cut = 1 - seg(out_at, end + 0.1, 0.004)               # o interruptor e o silêncio
mixL *= cut; mixR *= cut
n = int(0.14 * SR); tv = np.arange(n) / SR
put(lp(rs.randn(n), 1400) * np.exp(-tv * 45) + np.sin(2 * np.pi * 95 * tv) * np.exp(-tv * 30), out_at, 0.8)

finish()
