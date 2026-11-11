"""Skin campfire: uma fogueira numa clareira à noite, a chuva apagando e brasas vindo dos cantos.
Os vigias são silhuetas altas no limite da luz, e o relâmpago mostra uma multidão entre as árvores.

Fim: depois do until o dia nasce e os vigias vão embora; se o fogo apaga, sobe fumaça e os vigias vêm.
CFG no timeline (SKIN_CFG): lightning, crowd e stand (figuras de pé que o vídeo põe, como a que fica no fim).
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from modelos.survive import kit
from modelos.survive.kit import W, H
from modelos.survive.sim import DT

GROUND, FX = 600, 480

SIM = dict(
    hp0=60.0, burn=0.35, until=36.0,
    core=dict(x=FX, y=GROUND, w=(14, 70), h=(30, 210), exp=0.8, anchor=0.45, ry=0.55, aim=0.4),
    threat=dict(mode='rain', dmg=2.2, floor=GROUND, speed=(850, 1050),
                rate=[(0, 7), (8, 10), (12, 20), (21, 24), (24, 38), (31, 40), (33, 18), (36, 8), (38, 0)],
                wind=[(0, -70), (22, -70), (26, -160), (33, -160), (34, -70)]),
    ally=dict(hp=3, gap=[(0, 2.4), (20, 1.9), (36, 1.6)], first=1.2, stop=3.0),
)
CFG = dict(lightning=[24.3, 28.9, 31.6], crowd=22, stand=[])
HUD = dict(name='FIRE', clock='SUNRISE IN')
WARM = np.array([1.0, 0.56, 0.26], np.float32)
G = {}


# ---------------- cenário ----------------
def pine(d, x, base, h, w, col):
    for i in range(5):
        y0 = base - h * i / 5
        ww = w * (1 - i / 5 * 0.75)
        d.polygon([(x - ww, y0), (x + ww, y0), (x, y0 - h / 5 * 1.9)], fill=col)
    d.rectangle([x - w * 0.08, base, x + w * 0.08, base + 12], fill=col)


def prepare(sim, cfg):
    """Cenário fixo: céu, duas fileiras de pinheiros, a multidão entre as árvores, chão, pedras e lenha."""
    r = np.random.RandomState(sim.c['seed'] + 1000)
    img = Image.new('RGB', (W, H)); d = ImageDraw.Draw(img)
    for y in range(H):
        k = min(1, y / (GROUND - 40))
        d.line([(0, y), (W, y)], fill=(int(5 + 9 * k), int(7 + 9 * k), int(13 + 10 * k)))
    sky = Image.new('L', (W, H), 255); ds = ImageDraw.Draw(sky)
    crowd = []
    for layer, (base, hmin, hmax, col) in enumerate([(575, 150, 260, (11, 13, 17)), (590, 220, 360, (7, 8, 11))]):
        for x in np.sort(r.uniform(-40, W + 40, 34 if layer == 0 else 16)):
            if layer == 1 and abs(x - FX) < 170: continue
            h = r.uniform(hmin, hmax); w = h * r.uniform(0.2, 0.28); b = base + r.uniform(-6, 6)
            pine(d, x, b, h, w, col); pine(ds, x, b, h, w, 0)
        if layer == 0:
            for x in r.uniform(30, W - 30, cfg['crowd']):
                f = (x, 578 + r.uniform(-3, 4), r.uniform(85, 125), r.uniform(-0.06, 0.06))
                kit.figure(d, *f[:3], lean=f[3], col=(9, 10, 13)); kit.figure(ds, *f[:3], lean=f[3], col=0)
                crowd.append(f)
    ds.rectangle([0, GROUND - 26, W, H], fill=0)
    for y in range(GROUND - 26, H):
        k = (y - GROUND + 26) / (H - GROUND + 26)
        d.line([(0, y), (W, y)], fill=(int(17 + 6 * k), int(14 + 4 * k), int(11 + 2 * k)))
    for a in np.linspace(0, 2 * np.pi, 9, endpoint=False):
        x = FX + math.cos(a) * 62; y = GROUND + 6 + math.sin(a) * 8
        d.ellipse([x - 13, y - 8, x + 13, y + 7], fill=(40, 38, 36))
    for ang in (0.35, -0.35, 0.0):
        L = 70
        d.line([(FX - L * math.cos(ang), GROUND + 2 - L * math.sin(ang) * 0.3),
                (FX + L * math.cos(ang), GROUND + 2 + L * math.sin(ang) * 0.3)], fill=(52, 34, 20), width=13)
    G['base'] = np.asarray(img, np.float32) / 255
    G['sky'] = np.asarray(sky, np.float32) / 255
    G['crowd'] = crowd
    rr = np.random.RandomState(7)
    G['bg'] = np.column_stack([rr.uniform(0, W + 300, 420), rr.uniform(0, H, 420), rr.uniform(700, 900, 420)])


# ---------------- partículas: chama, vapor e respingo ----------------
def step(sim, new):
    fx, rv = sim.fx, sim.rv
    fl = fx.setdefault('flames', np.zeros((0, 6)))     # x, y, vx, vy, idade, vida
    puffs = fx.setdefault('puffs', [])                 # x, y, t0, tamanho
    splash = fx.setdefault('splash', [])               # x, y, t0
    t = sim.t
    for e in new:
        if e[1] == 'hit' and rv.rand() < 0.5: puffs.append([e[2], e[3], t, rv.uniform(6, 14)])
        elif e[1] == 'lost': puffs.append([e[2], e[3], t, 14])
        elif e[1] == 'floor': splash.append([e[2], GROUND + rv.uniform(-2, 16), t])
    w, h = sim.size()
    if sim.hp > 0:
        k = rv.poisson(3 + sim.hp / 9)
        if k:
            life = rv.uniform(0.35, 0.75, k) * (0.5 + h / 240)
            nf = np.column_stack([FX + rv.normal(0, w * 0.38, k), GROUND - rv.uniform(0, 10, k),
                                  rv.normal(0, 18, k) + sim.wind(t) * 0.15,
                                  -rv.uniform(0.9, 1.3, k) * h / life * 0.8, np.zeros(k), life])
            fl = np.vstack([fl, nf])
    if len(fl):
        fl[:, 4] += DT
        fl[:, 2] += (FX - fl[:, 0]) * 3.0 * DT        # puxa para o centro conforme sobe: chama em ponta
        fl[:, 0] += fl[:, 2] * DT
        fl[:, 1] += fl[:, 3] * DT
        fl = fl[fl[:, 4] < fl[:, 5]]
    fx['flames'] = fl
    fx['puffs'] = [p for p in puffs if t - p[2] < 1.2]
    fx['splash'] = [s for s in splash if t - s[2] < 0.18]


def snap(sim):
    fx = sim.fx
    return dict(flames=fx.get('flames', np.zeros((0, 6))).copy(), puffs=[list(p) for p in fx.get('puffs', [])],
                splash=[list(s) for s in fx.get('splash', [])])


def flash_at(t, cfg):
    f = 0.0
    for tl in cfg['lightning']:
        u = t - tl
        if u >= 0:
            f += np.exp(-u * 9) + 0.7 * np.exp(-max(0, u - 0.13) * 14) * (u > 0.13)
    return min(f, 1.4)


# ---------------- frame ----------------
def world(t, fr, sim, cfg):
    base, sky, crowd = G['base'], G['sky'], G['crowd']
    hp, dead, until = fr['hp'], fr['dead'], sim.c['until']
    won = dead is None or dead > until
    dawn = np.clip((t - until) / 3, 0, 1) if won else 0.0
    leave = 1 - np.clip((t - until) / 1.2, 0, 1) if won else 1.0

    # figuras: os vigias e as que o vídeo põe de pé
    fig, df = kit.layer()
    heads = []
    if leave > 0:
        for w, dd in zip(sim.watch, fr['watch']):
            x = FX + w['side'] * dd
            if -60 < x < W + 60:
                feet = GROUND + 8 + (w['size'] - 150) * 0.12
                hx, hy = kit.figure(df, x, feet, w['size'], w['lean'], col=int(255 * leave))
                heads.append((hx, hy, w['size'], w['blink'], leave))
    for s in cfg['stand']:
        if s['at'] <= t < s.get('until', 1e9):
            hx, hy = kit.figure(df, FX + s['dx'], GROUND + 14, s['h'], s.get('lean', 0), col=255)
            if s.get('eyes'): heads.append((hx, hy, s['h'], 0, 1))
    fm = kit.arr(fig)
    img = base * (1 - fm) + np.array([0.012, 0.012, 0.016], np.float32) * fm
    skym = sky[..., None] * (1 - fm)

    # luz do fogo e das brasas
    lr = sim.safe(hp) * kit.flicker(t)
    lit = kit.light(FX, GROUND - fr['h'] * 0.35, lr, 1.5) * (hp > 0) * (0.4 + hp / 100 * 1.1) * 2.0
    if dead is not None:                          # brasa no fundo da lenha, morrendo
        lit = lit + 0.5 * math.exp(-(t - dead) / 1.8) * kit.light(FX, GROUND, 90, 2)
    for ex, ey, ehp, ph in fr['allies']:
        lit = lit + 0.55 * kit.light(ex, ey, 70)
    img = img * (0.55 + dawn * 3.5 + lit[..., None] * WARM * 3.0)
    if dawn > 0:
        img += skym * np.array([0.16, 0.17, 0.21]) * dawn
    fla = flash_at(t, cfg)
    if fla > 0:                                   # relâmpago: céu branco, tudo vira recorte
        img += (skym * np.array([0.62, 0.66, 0.8]) + (1 - skym) * 0.05) * fla

    # chuva de fundo, só enfeite
    bgl, db = kit.layer()
    bg = G['bg']
    nshow = int(len(bg) * min(1, sim.rate(min(t, until + 2)) / 40))
    wd = sim.wind(t)
    for x0, y0, v in bg[:nshow]:
        y = (y0 + v * t) % (H + 40) - 20
        x = (x0 + wd * (v / 950) * t) % (W + 300) - 150
        db.line([(x, y), (x + wd * 0.018, y + 16)], fill=45, width=1)
    img += kit.arr(bgl) * np.array([0.3, 0.34, 0.42]) * (0.25 + lit[..., None] * 0.8 + fla)

    # fogo e brasas
    heat = kit.Heat()
    f = fr['flames']
    if len(f):
        heat.add(f[:, 0], f[:, 1], (1 - f[:, 4] / f[:, 5]) ** 0.6)
    for ex, ey, ehp, ph in fr['allies']:
        k = (0.9 + 0.3 * math.sin(t * 22 + ph)) * (0.5 + ehp / 3)
        for j in range(6):                        # chama pequena que sobe da brasa
            heat.add(ex + round(math.sin(t * 9 + ph + j) * j * 0.4) * 2, ey - j * 2, k * (1 - j / 6) * 0.8, small=True)
    if dead is not None and t - dead < 6:          # lenha em brasa depois de apagar
        k = math.exp(-(t - dead) / 1.5)
        for dx in range(-30, 31, 6):
            heat.add(FX + dx, GROUND - 2, 0.25 * k * (1 + 0.5 * math.sin(t * 7 + dx)), small=True)
    img += heat.rgb()

    # gotas que contam e respingos
    lay, dl = kit.layer()
    for x, y, vx, vy in fr['threats']:
        dl.line([(x - vx * 0.03, y - vy * 0.03), (x, y)], fill=255, width=3)
        dl.ellipse([x - 3, y - 4, x + 3, y + 3], fill=255)
    for x, y, t0 in fr['splash']:
        dl.line([(x - 6, y - 5), (x, y), (x + 6, y - 5)], fill=150, width=1)
    da = kit.arr(lay)
    da = da + kit.arr(lay, 3) * 0.8
    img += da * np.array([0.55, 0.72, 0.95]) * (0.7 + lit[..., None] * 0.9 + fla * 0.5)

    # vapor, e a fumaça quando apaga
    puf, dp = kit.layer()
    for x, y, t0, sz in fr['puffs']:
        a = t - t0; rr = sz * (1 + a * 2.2)
        dp.ellipse([x - rr, y - a * 40 - rr, x + rr, y - a * 40 + rr], fill=int(110 * (1 - a / 1.2) ** 1.5))
    if dead is not None:
        rs = np.random.RandomState(5)
        for j in range(40):
            a = t - dead - j * 0.12
            x0 = rs.uniform(-25, 25)
            if 0 <= a < 3.5:
                x = FX + x0 + a * 18 * math.sin(j); y = GROUND - 10 - a * 70; rr = 10 + a * 16
                dp.ellipse([x - rr, y - rr, x + rr, y + rr], fill=int(90 * (1 - a / 3.5) ** 1.3))
    img += kit.arr(puf, 7) * 0.8 * np.array([0.5, 0.5, 0.52]) * (0.3 + lit[..., None])

    # olhos: os vigias, e a multidão quando o fogo está baixo
    low = np.clip((28 - hp) / 18, 0, 1) * (1 - dawn)
    if low > 0:
        for j, (x, feet, h, lean) in enumerate(crowd[:9]):
            heads.append((x + lean * h, feet - h + h * 0.07, h, j * 1.7, low * 0.8))
    img += kit.eyes(heads, lit, t)
    return kit.done(img)


# ---------------- som ----------------
def sound(s, cfg, A, hp):
    """Chuva, fogo, chiado na gota, brasa apagando e chegando, fogo apagando e trovão."""
    SR, N, T = A.SR, A.N, A.T
    noise = A.rs.randn

    def env(n, decay, attack=0.0):
        tv = np.arange(n) / SR
        e = np.exp(-tv * decay)
        return e * np.minimum(tv / attack, 1) if attack else e

    grid = np.arange(0, A.TOTAL + 0.05, 0.05)
    rain = np.interp(T, grid, [s.rate(t) for t in grid]) / 40
    w = noise(N)
    A.add(A.bp(w, 600, 7000) * 0.09 * rain, 1.0, -0.3)
    A.add(A.bp(np.roll(w, 9999), 600, 7000) * 0.09 * rain, 1.0, 0.3)

    A.add(A.lp(noise(N), 350) * 0.5 * (hp / 100) ** 0.7)       # o fogo
    t = 0.0
    while t < A.TOTAL:                                          # estalos da lenha
        h = np.interp(t, T[::441], hp[::441])
        t += A.rs.exponential(1 / (2 + h / 7))
        if h <= 0: continue
        n = int(A.rs.uniform(0.004, 0.02) * SR)
        A.put(A.hp(noise(n), 1200) * np.exp(-np.arange(n) / (n / 4)), t, A.rs.uniform(0.05, 0.25) * (0.3 + h / 100),
              A.rs.uniform(-0.4, 0.4))

    for ev in s.events:
        t0, kind, x = ev[0], ev[1], ev[2]
        pan = (x - FX) / FX
        if kind == 'hit':
            n = int(0.16 * SR); A.put(A.hp(noise(n), 3500) * env(n, 22), t0, 0.22, pan * 0.3)
        elif kind == 'block':
            n = int(0.07 * SR); A.put(A.hp(noise(n), 2500) * env(n, 50), t0, 0.18, pan)
        elif kind == 'lost':
            n = int(0.5 * SR); A.put(A.hp(noise(n), 1800) * env(n, 7), t0, 0.32, pan)
        elif kind == 'feed':
            n = int(0.6 * SR); tv = np.arange(n) / SR
            x = A.lp(noise(n), 400) * 2.2 + np.sin(2 * np.pi * np.cumsum(90 - 40 * tv / 0.6) / SR) * 0.6
            A.put(x * env(n, 5, 0.04), t0, 0.55, pan * 0.5)
        elif kind == 'spawn':
            n = int(0.25 * SR); A.put(A.bp(noise(n), 300, 1500) * env(n, 9, 0.08), t0, 0.15, pan)
        elif kind == 'out':
            n = int(2.8 * SR); tv = np.arange(n) / SR
            A.put(A.hp(noise(n), 1500) * env(n, 1.6, 0.03), t0, 0.55)
            A.put(np.sin(2 * np.pi * np.cumsum(70 - 35 * tv / 2.8) / SR) * env(n, 1.2, 0.05), t0, 0.5)

    for tl0 in cfg['lightning']:
        n = int(4 * SR); tv = np.arange(n) / SR
        crack = A.hp(noise(n), 900) * np.exp(-tv * 14) * 0.5
        rum = A.lp(noise(n), 140, 4) * 6 * np.minimum(tv / 0.2, 1) * np.exp(-tv * 0.9)
        A.put(crack + rum, tl0 + 0.05, 0.6)
