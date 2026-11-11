"""Skin planet: um planeta no meio do espaço, com escudo. Meteoros vêm de todas as bordas, e esferas de energia
saem dos lados para recarregar o escudo. O escudo é a vida.

O planeta é pálido, gira devagar e pulsa como um coração; cada esfera que chega faz as rachaduras crescerem
e o pulso acelerar. Com hatch no SKIN_CFG, o planeta racha inteiro no fim e se abre um olho.
Venceu: os meteoros param e o escudo fica. Perdeu: o escudo estilhaça e os meteoros acertam a superfície.

CFG no timeline (SKIN_CFG): hatch=dict(at, open), glimpse (segundos em que o olho aparece num frame só).
"""
import math
import bisect
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
from modelos.survive import kit
from modelos.survive.kit import W, H, XX, YY
from modelos.survive.sim import DT

CX, CY, R = 480, 365, 108
SIM = dict(
    hp0=60.0, burn=0.25, until=36.0,
    core=dict(x=CX, y=CY, w=(R + 14, 58), h=(2 * R + 28, 116), exp=1.0, anchor=0.0, ry=0.5, aim=0.0),
    threat=dict(mode='aim', edges='tblr', speed=(230, 330), spread=0.5, dmg=1.9,
                rate=[(0, 3), (8, 4), (12, 6.5), (21, 7.5), (24, 11), (31, 12), (33, 5), (35.5, 0)]),
    ally=dict(hp=2, gap=[(0, 2.2), (20, 1.8), (36, 1.6)], first=1.0, stop=3.0, speed=(110, 150),
              wobble=(20, 45), y=(80, 650), gain0=5.0, gain1=3.5),
    watch=dict(n=0),
)
CFG = dict(hatch=None, glimpse=[])
HUD = dict(name='SHIELD', clock='STORM ENDS IN', color=((40, 140, 230), (120, 230, 255)))
G = {}

# recorte em volta do planeta, onde fica toda a conta pesada
B = 220
X0, Y0 = CX - B, CY - B
cyy, cxx = np.mgrid[0:2 * B, 0:2 * B].astype(np.float32)
DX, DY = cxx + X0 - CX, cyy + Y0 - CY
DIST = np.hypot(DX, DY)


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


# ---------------- coisas fixas ----------------
def _texture(r):
    """Superfície em equirretangular 512x256: pálida, cor de osso, com manchas."""
    n = sum(gaussian_filter(r.randn(256, 512), s, mode='wrap') * s for s in (2, 6, 16))
    n = (n - n.min()) / (n.max() - n.min())
    lo, hi = np.array([0.42, 0.38, 0.33]), np.array([0.78, 0.73, 0.64])
    tex = lo + (hi - lo) * n[..., None]
    for _ in range(14):                                       # crateras rasas
        u, v, s = r.uniform(0, 512), r.uniform(40, 216), r.uniform(4, 14)
        d = np.hypot((np.arange(512)[None] - u + 256) % 512 - 256, np.arange(256)[:, None] - v)
        tex *= (1 - 0.18 * np.exp(-(d / s) ** 2))[..., None]
    return tex.astype(np.float32)


def _cracks(r):
    """Rachaduras: cada pixel guarda quando aparece (0 a 1). Crescem a partir de 6 pontos."""
    im = Image.new('L', (512, 256)); d = ImageDraw.Draw(im)
    segs = []
    def grow(x, y, ang, order, depth):
        for k in range(r.randint(10, 20)):
            nx, ny = x + math.cos(ang) * r.uniform(5, 10), y + math.sin(ang) * r.uniform(5, 10)
            segs.append((x, y, nx, ny, order, depth))
            x, y, order = nx, ny, order + 0.035
            ang += r.normal(0, 0.45)
            if depth < 3 and r.rand() < 0.16:
                grow(x, y, ang + r.choice([-1, 1]) * r.uniform(0.6, 1.2), order, depth + 1)
    for i in range(6):
        grow(r.uniform(0, 512), r.uniform(70, 186), r.uniform(0, 6.28), i * 0.04, 0)
    top = max(s[4] for s in segs)
    for x, y, nx, ny, o, depth in sorted(segs, key=lambda s: -s[4]):
        x, nx = x % 512, nx % 512
        if abs(nx - x) > 100: continue            # cruza a emenda da textura
        d.line([(x, y), (nx, ny)], fill=1 + int(o / top * 253), width=2 if depth == 0 else 1)
    return np.asarray(im, np.float32) / 255


def _eye(r):
    """Olho no tamanho do planeta, em coordenadas do disco: esclera escura com veias e íris âmbar."""
    rr = np.hypot(DX, DY) / R
    sc = np.stack([0.32 - 0.12 * rr, 0.06 + 0.02 * rr, 0.05 + 0.0 * rr], -1)
    veins = Image.new('L', (2 * B, 2 * B)); dv = ImageDraw.Draw(veins)
    for _ in range(60):
        a = r.uniform(0, 6.28); x, y = B + math.cos(a) * R, B + math.sin(a) * R
        for k in range(12):
            a2 = a + math.pi + r.normal(0, 0.5)
            nx, ny = x + math.cos(a2) * 6, y + math.sin(a2) * 6
            dv.line([(x, y), (nx, ny)], fill=180, width=1); x, y = nx, ny
    v = gaussian_filter(np.asarray(veins, np.float32) / 255, 0.6)
    sc = sc + v[..., None] * np.array([0.35, 0.03, 0.02])
    G['sclera'] = np.clip(sc, 0, 1).astype(np.float32)
    ang = np.arctan2(DY, DX)
    G['striae'] = (0.75 + 0.25 * np.sin(ang * 37 + r.uniform(0, 6)) * np.sin(ang * 11)).astype(np.float32)


def _stars(r):
    im = np.zeros((H, W), np.float32)
    n = 420
    xs, ys, b = r.randint(0, W, n), r.randint(0, H, n), r.uniform(0.15, 1, n) ** 2.5
    im[ys, xs] = b
    stars = gaussian_filter(im, 0.7) * 5 + im * 0.6
    neb = gaussian_filter(r.randn(H // 4, W // 4), 9)
    neb = np.kron(np.clip(neb * 6, 0, 1), np.ones((4, 4)))[:H, :W]
    G['stars'] = stars[..., None] * np.array([0.9, 0.92, 1.0], np.float32)
    G['twinkle'] = r.uniform(0, 6.28, (H, W)).astype(np.float32)
    G['neb'] = neb[..., None] * np.array([0.05, 0.02, 0.07], np.float32)


def prepare(sim, cfg):
    r = np.random.RandomState(sim.c['seed'] + 1000)
    G['tex'] = _texture(r)
    G['crk'] = _cracks(r)
    _eye(r)
    _stars(r)
    # o disco: para cada pixel, onde ele cai na textura e quanta luz recebe
    nx, ny = DX / R, DY / R
    inside = nx * nx + ny * ny < 1
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    lat = np.arcsin(np.clip(-ny, -1, 1)); lon = np.arctan2(nx, nz)
    G['u0'] = (lon / (2 * np.pi) + 0.5) * 512
    G['v'] = np.clip((0.5 - lat / np.pi) * 256, 0, 255).astype(int)
    L = np.array([-0.55, -0.45, 0.7]); L /= np.linalg.norm(L)
    G['shade'] = (np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1) * 0.95 + 0.06) * inside
    G['disk'] = inside.astype(np.float32)
    G['edge'] = np.clip((R - DIST) / 1.5, 0, 1).astype(np.float32)
    feeds = [e[0] for e in sim.events if e[1] == 'feed']
    G['feeds'] = feeds
    G['beats'] = beats(feeds, sim.c['total'], cfg)


def feeds_until(t):
    return bisect.bisect_right(G['feeds'], t)


def beats(feeds, total, cfg):
    """Batidas do planeta: lentas no começo, mais rápidas a cada esfera que chega e no fim."""
    out, t = [], 0.6
    hatch = cfg.get('hatch')
    while t < total:
        out.append(t)
        bpm = 34 + 2.4 * bisect.bisect_right(feeds, t)
        if hatch and t > hatch['at']:
            bpm += 60 * smooth((t - hatch['at']) / 2)
        t += 60 / bpm
    return out


def pulse_at(t):
    b = G['beats']
    i = bisect.bisect_right(b, t) - 1
    if i < 0: return 0.0
    u = t - b[i]
    return math.exp(-u * 7) + 0.6 * math.exp(-max(0, u - 0.24) * 8) * (u > 0.24)


def crack_level(t, cfg):
    c = min(0.04 + 0.03 * feeds_until(t), 0.6)
    hatch = cfg.get('hatch')
    if hatch:
        c += (1 - c) * smooth((t - hatch['at']) / 1.6)
    return c


# ---------------- partículas ----------------
def step(sim, new):
    fx, rv, t = sim.fx, sim.rv, sim.t
    sp = fx.setdefault('sparks', np.zeros((0, 7)))       # x, y, vx, vy, idade, vida, tipo (0 fogo, 1 energia)
    hits = fx.setdefault('hits', [])                      # x, y, t0
    add = []
    for e in new:
        k, x, y = e[1], e[2], e[3]
        if k == 'hit':
            hits.append([x, y, t])
            a = math.atan2(y - CY, x - CX)
            n = 14
            ang = a + rv.normal(0, 0.7, n); v = rv.uniform(60, 260, n)
            add.append(np.column_stack([np.full(n, x), np.full(n, y), np.cos(ang) * v, np.sin(ang) * v,
                                        np.zeros(n), rv.uniform(0.25, 0.6, n), rv.rand(n) < 0.4]))
        elif k in ('block', 'lost', 'out'):
            n = {'block': 7, 'lost': 18, 'out': 60}[k]
            ang = rv.uniform(0, 6.28, n); v = rv.uniform(40, 200 if k != 'out' else 320, n)
            add.append(np.column_stack([np.full(n, x if k != 'out' else CX), np.full(n, y if k != 'out' else CY),
                                        np.cos(ang) * v, np.sin(ang) * v, np.zeros(n),
                                        rv.uniform(0.3, 0.8 if k != 'out' else 1.6, n), np.ones(n)]))
    if add:
        sp = np.vstack([sp] + add)
    if len(sp):
        sp[:, 4] += DT
        sp[:, 0] += sp[:, 2] * DT; sp[:, 1] += sp[:, 3] * DT
        sp[:, 2:4] *= 0.985
        sp = sp[sp[:, 4] < sp[:, 5]]
    fx['sparks'] = sp
    fx['hits'] = [h for h in hits if t - h[2] < 0.5]


def snap(sim):
    fx = sim.fx
    return dict(sparks=fx.get('sparks', np.zeros((0, 7))).copy(), hits=[list(h) for h in fx.get('hits', [])])


# ---------------- frame ----------------
def world(t, fr, sim, cfg):
    hp, dead, until = fr['hp'], fr['dead'], sim.c['until']
    hatch = cfg.get('hatch')
    img = G['neb'] + G['stars'] * (0.75 + 0.25 * np.sin(G['twinkle'] + t * 2.3))[..., None]
    img = img.copy()
    img += kit.light(-60, -80, 520) [..., None] * np.array([0.10, 0.08, 0.05])      # a estrela longe, fora do quadro

    # tremor do planeta no fim
    sx = sy = 0
    if hatch and t > hatch['at']:
        k = smooth((t - hatch['at']) / 2) * (1 - smooth((t - hatch['open'] - 1.2) / 0.6))
        rs = np.random.RandomState(int(t * 30))
        sx, sy = rs.uniform(-1, 1) * 4 * k, rs.uniform(-1, 1) * 3 * k
    x0, y0 = X0 + int(sx), Y0 + int(sy)

    # o planeta: textura girando, luz, rachaduras que brilham com o pulso
    crop = np.zeros((2 * B, 2 * B, 3), np.float32)
    u = ((G['u0'] + t * 6.0) % 512).astype(int)
    v = G['v']
    surf = G['tex'][v, u] * G['shade'][..., None]
    c = crack_level(t, cfg)
    cr = G['crk'][v, u]
    vis = ((cr > 0) & (cr <= c)).astype(np.float32) * G['disk']
    p = pulse_at(t)
    glow = p * 0.35 * c                               # antes do fim: só um brilho fraco na batida
    if hatch:
        glow += (0.6 + 0.4 * p) * 1.6 * smooth((t - hatch['at']) / 1.6)
    cg = gaussian_filter(vis, 2.2) * 2.2 + vis
    surf = surf * (1 - vis[..., None] * 0.7) + (cg * glow)[..., None] * np.array([1.0, 0.32, 0.08])
    surf += (G['disk'] * p * 0.03 * (0.4 + c))[..., None] * np.array([0.9, 0.3, 0.2])

    # o olho, entre as duas metades da casca
    if hatch or cfg['glimpse']:
        a = 0.0
        if hatch: a = smooth((t - hatch['open']) / 1.4)
        if any(g <= t < g + 1 / 30 + 1e-6 for g in cfg['glimpse']): a = 1.0
        if a > 0:
            yy = (DY - sy) / R; xx = (DX - sx) / R
            lid = a * 0.62 * np.clip(1 - xx ** 2 / 0.92, 0, 1)
            m = np.clip((lid - np.abs(yy)) * R / 2, 0, 1) * G['disk']
            look = 1 - smooth((t - hatch['open'] - 1.1) / 0.35) if hatch else 0.0     # olha de lado, depois para nós
            gx, gy = -0.38 * look, 0.05 * look
            ir = np.hypot(xx - gx, yy - gy)
            iris = np.clip((0.36 - ir) * R / 1.5, 0, 1)
            col = G['sclera'] * (1 - iris[..., None])
            amber = np.array([0.95, 0.62, 0.12]) * (1.1 - ir / 0.36 * 0.6)[..., None] * G['striae'][..., None]
            col += amber * iris[..., None]
            dil = 1 + 0.8 * smooth((t - hatch['open'] - 1.5) / 0.4) if hatch else 1.0
            pup = np.clip((1 - ((xx - gx) / (0.055 * dil)) ** 2 - ((yy - gy) / 0.3) ** 2) * 4, 0, 1)
            col *= (1 - pup * 0.96)[..., None]
            spec = np.exp(-(((xx - gx + 0.12) ** 2 + (yy - gy + 0.12) ** 2) / 0.0015))
            col += spec[..., None] * 0.8
            rim = np.clip(1 - np.abs(lid - np.abs(yy)) * R / 3, 0, 1) * G['disk'] * (a > 0.02)
            surf = surf * (1 - m[..., None]) + col * m[..., None]
            surf += rim[..., None] * np.array([1.0, 0.45, 0.12]) * 1.5
    crop += surf * G['edge'][..., None]

    # escudo: bolha com a borda acesa, que vira vermelha quando está fraca
    if dead is None:
        w = fr['w']
        k = np.clip(hp / 100, 0, 1)
        cool, warm = np.array([0.35, 0.8, 1.0]), np.array([1.0, 0.25, 0.2])
        col = cool if hp > 25 else warm * (0.6 + 0.4 * ((t * 4) % 1 < 0.6))
        if hatch:
            col = col + (warm - col) * smooth((t - hatch['open'] - 1.5) / 0.4)
        fl = 0.85 + 0.15 * math.sin(t * 17) * math.sin(t * 5.3)
        shell = np.exp(-((DIST - w) / 3.5) ** 2) * 0.9 + (DIST < w) * 0.07 * (DIST / w) ** 4
        shell = shell * (0.45 + 0.55 * k) * fl
        for hx, hy, h0 in fr['hits']:
            age = t - h0
            d2 = (DX + CX - hx) ** 2 + (DY + CY - hy) ** 2
            shell = shell + np.exp(-d2 / (26 + age * 900)) * np.exp(-age * 7) * 1.6 * (np.abs(DIST - w) < 14 + age * 60)
        crop += shell[..., None] * col

    # cola o recorte no quadro
    ys, xs = slice(max(0, y0), min(H, y0 + 2 * B)), slice(max(0, x0), min(W, x0 + 2 * B))
    img[ys, xs] += crop[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]

    # meteoros, esferas e faíscas
    met, dm = kit.layer()
    for x, y, vx, vy in fr['threats']:
        sp = math.hypot(vx, vy) or 1
        ux, uy = vx / sp, vy / sp
        for j in range(7):
            dm.line([(x - ux * j * 9, y - uy * j * 9), (x - ux * (j + 1) * 9, y - uy * (j + 1) * 9)],
                    fill=int(255 * (1 - j / 7) ** 1.5), width=max(1, 5 - j))
        dm.ellipse([x - 4, y - 4, x + 4, y + 4], fill=255)
        if dead is not None and math.hypot(x - CX, y - CY) < R:       # sem escudo, acerta o chão
            dm.ellipse([x - 14, y - 14, x + 14, y + 14], fill=255)
    a = kit.arr(met)
    img += a * np.array([1.0, 0.88, 0.7]) + kit.arr(met, 5) * 1.4 * np.array([1.0, 0.42, 0.12])

    orb, do = kit.layer()
    for ex, ey, ehp, ph in fr['allies']:
        rr = 4 + ehp * 2.2 + math.sin(t * 9 + ph) * 0.8
        do.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], fill=255)
        dx, dy = ex - CX, ey - CY; dd = math.hypot(dx, dy) or 1
        for j in range(1, 6):                         # rastro, do lado oposto ao planeta
            q = rr * (1 - j / 7)
            x, y = ex + dx / dd * j * 7, ey + dy / dd * j * 7
            do.ellipse([x - q, y - q, x + q, y + q], fill=int(150 * (1 - j / 6)))
    sk, ds = kit.layer(); fire, df = kit.layer()
    for x, y, vx, vy, age, life, kind in fr['sparks']:
        b = int(255 * (1 - age / life))
        (ds if kind else df).point((x, y), fill=b)
        (ds if kind else df).point((x + 1, y), fill=b)
    img += kit.arr(orb) * np.array([0.8, 0.97, 1.0]) + kit.arr(orb, 8) * 3.0 * np.array([0.3, 0.75, 1.0])
    img += kit.arr(sk, 1) * 2.5 * np.array([0.5, 0.9, 1.0]) + kit.arr(fire, 1) * 2.5 * np.array([1.0, 0.6, 0.2])
    return kit.done(img)


# ---------------- som ----------------
def sound(s, cfg, A, hp):
    SR, N, T = A.SR, A.N, A.T
    noise = A.rs.randn

    def env(n, decay, attack=0.0):
        tv = np.arange(n) / SR
        e = np.exp(-tv * decay)
        return e * np.minimum(tv / attack, 1) if attack else e

    def tone(fs, dur, decay):
        n = int(dur * SR); tv = np.arange(n) / SR
        return sum(np.sin(2 * np.pi * f * tv + i) for i, f in enumerate(fs)) / len(fs) * np.exp(-tv * decay)

    A.add(A.lp(noise(N), 90, 4) * 1.6 + np.sin(2 * np.pi * 38 * T) * 0.05, 1.0)     # o vazio: ronco grave
    for ev in s.events:
        t0, kind, x = ev[0], ev[1], ev[2]
        pan = (x - CX) / CX
        if kind == 'hit':
            n = int(0.5 * SR); tv = np.arange(n) / SR
            zap = np.sin(2 * np.pi * np.cumsum(900 * np.exp(-tv * 9) + 120) / SR) * env(n, 10)
            A.put(A.lp(noise(n), 220) * 3 * env(n, 7) + zap * 0.5 + A.bp(noise(n), 2000, 7000) * env(n, 30) * 0.6,
                  t0, 0.38, pan * 0.6)
        elif kind == 'block':
            n = int(0.18 * SR); A.put(A.bp(noise(n), 1500, 6000) * env(n, 30) + tone([1400], 0.18, 25)[:n] * 0.4,
                                      t0, 0.2, pan)
        elif kind == 'lost':
            A.put(tone([2200, 3150, 4700], 0.7, 6) + np.concatenate([A.hp(noise(int(0.1 * SR)), 3000) * 0.4,
                                                                       np.zeros(int(0.6 * SR))])[:int(0.7 * SR)],
                  t0, 0.3, pan)
        elif kind == 'feed':
            n = int(0.9 * SR)
            A.put(tone([880, 1320, 1760], 0.9, 4) * np.minimum(np.arange(n) / SR / 0.05, 1), t0, 0.28, pan * 0.4)
        elif kind == 'spawn':
            A.put(tone([1500], 0.15, 30), t0, 0.06, pan)
        elif kind == 'out':
            A.put(tone([1800, 2600, 3900, 5200], 1.5, 3) + np.concatenate([A.lp(noise(int(1.5 * SR)), 150) * 4]) *
                  env(int(1.5 * SR), 2.5), t0, 0.6)

    # o coração do planeta: quase inaudível no começo, cada vez mais alto
    feeds = [e[0] for e in s.events if e[1] == 'feed']
    for b in beats(feeds, A.TOTAL, cfg):
        k = 0.12 + 0.035 * bisect.bisect_right(feeds, b)
        hatch = cfg.get('hatch')
        if hatch: k += 0.8 * smooth((b - hatch['at']) / 2)
        for dt, g in ((0, 1.0), (0.24, 0.6)):
            n = int(0.22 * SR); tv = np.arange(n) / SR
            A.put(np.sin(2 * np.pi * 44 * tv) * np.exp(-tv * 16) + A.lp(noise(n), 120) * np.exp(-tv * 25),
                  b + dt, min(k, 1.0) * g)

    hatch = cfg.get('hatch')
    if hatch:
        a, o = hatch['at'], hatch['open']
        t = a
        while t < o + 0.6:                         # a casca estalando
            t += A.rs.exponential(0.06 if t > a + 0.8 else 0.15)
            n = int(A.rs.uniform(0.01, 0.05) * SR)
            A.put(A.bp(noise(n), 300, 2500) * env(n, 60), t, A.rs.uniform(0.2, 0.6), A.rs.uniform(-0.5, 0.5))
        n = int((o - a + 2) * SR); tv = np.arange(n) / SR
        saw = ((np.cumsum(28 + 18 * tv / tv[-1]) / SR) % 1) * 2 - 1
        A.put(A.lp(saw, 200) * np.minimum(tv / 1.0, 1) * np.exp(-np.maximum(0, tv - (o - a)) * 2), a, 0.5)
        n = int(5 * SR); tv = np.arange(n) / SR
        A.put(A.lp(noise(n), 70, 4) * 10 * np.exp(-tv * 0.9) + np.sin(2 * np.pi * 33 * tv) * np.exp(-tv * 0.6), o, 0.8)
        A.put(np.sin(2 * np.pi * 1975 * tv) * 0.15 * np.minimum(tv / 2, 1) * np.exp(-tv * 0.3), o + 1.5, 0.5)
