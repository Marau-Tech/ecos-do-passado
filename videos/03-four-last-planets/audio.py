from synth import *

def chord(fs, a=1.0):
    return sum(np.sin(2 * np.pi * f * T + i) for i, f in enumerate(fs)) * a / len(fs)
def bell(f, dur=1.4, decay=3.0):
    n = int(dur * SR); tv = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tv) + 0.4 * np.sin(2 * np.pi * f * 2.01 * tv) * np.exp(-tv * 4) + 0.15 * np.sin(2 * np.pi * f * 4.1 * tv) * np.exp(-tv * 9)) * np.exp(-tv * decay)
def knock(g=1.0):
    n = int(0.35 * SR); tv = np.arange(n) / SR
    body = np.sin(2 * np.pi * 140 * tv) * np.exp(-tv * 30) + 0.5 * np.sin(2 * np.pi * 260 * tv) * np.exp(-tv * 45)
    return (body + lp(rs.randn(n), 900) * np.exp(-tv * 70) * 0.8) * g

t1, t2, t3, t4 = (START[p[2]] for p in PLANETS)

# ---- intro: drone desafinado ----
e = seg(0, t1, 0.8)
add(sum(np.sin(2 * np.pi * f * T + p) * a for f, a, p in ((46, 1, 0), (46.5, .9, 1), (69.0, .55, 2), (92.4, .4, 3), (138.0, .2, 4))) * e * (0.8 + 0.2 * np.sin(T * 1.3)), 0.11)

# ---- P1 THE SALT: vidro soando, vento fino, passos de sal ----
e = seg(t1, t2, 0.6)
for k, f in enumerate((392.0, 587.33, 783.99)):
    add(np.sin(2 * np.pi * f * T + k) * (0.6 + 0.4 * np.sin(2 * np.pi * (0.13 + 0.05 * k) * T + k)) * e, 0.018, (k - 1) * 0.4)
add(bp(white, 900, 3600) * (0.5 + 0.5 * smooth_noise(0.5, 3)) * e, 0.012)
mel = [783.99, 987.77, 1174.66, 987.77, 880.0, 1046.5, 1318.5, 1046.5]
tt = t1 + 0.4; i = 0
while tt < START['p1d'] + 2.0:
    put(bell(mel[i % 8], 2.0, 2.2), tt, 0.04, 0.3 * np.sin(i)); tt += 0.9; i += 1
for i in range(5):                                    # passos de sal rachando
    n = int(0.14 * SR)
    put(bp(rs.randn(n), 1200, 7000) * np.exp(-np.arange(n) / n * 6), START['p1c'] + 0.2 + i * 0.66, 0.08, 0.2 if i % 2 else -0.2)
a = START['p1d'] + 2.1                                # ninguém volta: tudo some, fica um tom
cut = 1 - seg(a, t2, 0.15) * 0.9
mixL *= cut; mixR *= cut
put(bell(466.16, 3.0, 1.2), a + 0.1, 0.07)

# ---- P2 THE CUL-DE-SAC: grilos, zumbido de poste, caixinha de música distante ----
e = seg(t2, t3, 0.5)
add(np.sin(2 * np.pi * 120 * T) * (0.7 + 0.3 * np.sin(T * 0.7)) * e, 0.018)
add(np.sin(2 * np.pi * 60 * T) * e, 0.03)
cr = np.sign(np.sin(2 * np.pi * 4700 * T)) * (np.sin(2 * np.pi * 9 * T) > 0.4) * (np.sin(2 * np.pi * 0.8 * T) > -0.3)
add(hp(cr, 3500) * e, 0.01, 0.3)
box_notes = [523.25, 659.25, 783.99, 659.25, 698.46, 587.33, 523.25, 587.33]
tt = START['p2b']; i = 0
while tt < START['p2d'] + 2.0:
    put(lp(bell(box_notes[i % 8] * 2, 0.8, 5.0), 3200), tt, 0.03 + 0.04 * ((tt - START['p2b']) / 8), -0.3); tt += 0.43; i += 1
a = START['p2d'] + 0.2                                # a luz da varanda
n = int(0.12 * SR); put(np.sin(2 * np.pi * 90 * np.arange(n) / SR) * np.exp(-np.arange(n) / SR * 40), a, 0.1)
a = START['p2d'] + 2.0                                # a porta abre
n = int(1.4 * SR); tv = np.arange(n) / SR
put(np.tanh(sum(np.sin(2 * np.pi * np.cumsum(180 + 120 * (tv / 1.4)) / SR * k) / k for k in range(1, 5))) * np.sin(np.pi * tv / 1.4) * 0.5, a, 0.1, 0.3)
put(boom(2.0, 60, 22, 0.6, 0.5), a + 0.8)
add(chord([220.0, 261.6, 311.1], 1.0) * seg(a + 0.8, t3, 0.3), 0.06)

# ---- P3 THE WHITEOUT: vendaval, fogueira, batidas ----
e = seg(t3, t4, 0.4)
gust = np.clip(0.55 + 0.35 * smooth_noise(0.7, 9), 0.05, 1.5)
add(bp(white, 200, 1400) * gust ** 1.5 * e, 0.11, -0.1)
add(lp(white, 300) * gust * e, 0.07, 0.1)
add(bp(white, 1200, 4500) * (0.4 + 0.6 * smooth_noise(1.2, 2)) * e, 0.018)
for k in range(110):                                  # estalos da fogueira
    n = int(0.012 * SR); put(hp(rs.randn(n), 1500) * np.exp(-np.arange(n) / n * 5), START['p3b'] + rs.rand() * (t4 - START['p3b']), 0.10 * rs.rand(), rs.rand() * .6 - .3)
add(lp(white, 500) * seg(START['p3b'], t4, 0.3) * (0.6 + 0.4 * smooth_noise(5, 7)), 0.035)
for dt in (0.9, 2.3):
    put(knock(), START['p3c'] + dt, 0.4)
    put(knock(), START['p3c'] + dt + 0.22, 0.34)
for dt in (0.7, 0.95):
    put(knock(), START['p3d'] + dt, 0.5)
a = START['p3d'] + 1.9
put(boom(3.0, 60, 18, 1.0, 0.8), a)
n = int(2.1 * SR); tv = np.arange(n) / SR
put(np.tanh(sum(np.sin(2 * np.pi * np.cumsum(220 * (1 + 0.3 * tv / 2.1)) / SR * k) / k for k in range(1, 6)) * 1.5) * 0.12 * (tv / 2.1) ** 1.5, a, 1.0)
mute = 1 - seg(t4 - 0.02, t4 + 0.12, 0.004) * 0.92
mixL *= mute; mixR *= mute

# ---- P4 THE TWIN: drone que cresce, pulsação, o olho ----
end = END_CARD
e = seg(t4, end, 0.3)
add(lp(white, 280) * e, 0.012)
add(np.sin(2 * np.pi * 38 * T) * e, 0.035)
grow = np.clip((T - t4) / (end - t4), 0, 1)
add(sum(np.sin(2 * np.pi * f * T + i) for i, f in enumerate((233.1, 233.9, 349.2))) * e * grow ** 2, 0.03)
pulse = (0.5 + 0.5 * np.sin(2 * np.pi * (0.4 + 1.2 * grow) * (T - t4))) ** 3
add(lp(white, 160) * pulse * e * (0.2 + grow), 0.08)
a = START['p4c'] + 1.6                                # piscou
put(boom(1.2, 80, 30, 0.6, 0.4), a)
put(lp(rs.randn(int(0.5 * SR)), 1800) * np.exp(-np.arange(int(0.5 * SR)) / SR * 9), a, 0.1)
a = START['p4d'] + 2.0                                # abriu
n = int((end - a) * SR); tv = np.arange(n) / SR
u = tv / tv[-1]
sc = sum(np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.5 * u)) / SR) for f0 in (640, 756, 912, 1140, 1490))
put(np.tanh(sc * 1.4 + lp(rs.randn(n), 2600) * 5) * 0.24 * (0.3 + 0.7 * u), a)
put(boom(1.6, 70, 24, 1.0, 0.8), a)

finish()
