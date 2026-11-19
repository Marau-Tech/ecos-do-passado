"""Geometria procedural do personagem POV, em malhas-gaiola para Subdivision Surface.

Cada peça é uma Cage: vértices na pose de repouso (espaço do corpo), faces em quads,
UV em metros (u em volta, v ao longo) e, por vértice, os pesos de cada osso. O personagem
deforma a gaiola por skinning linear a cada frame; o Subdivision suaviza o resultado.

Só usa numpy: dá para gerar e conferir a geometria fora do Blender.
"""
import math
import numpy as np
from . import skeleton as S

TAU = 2 * math.pi


def spow(x, p):
    return math.copysign(abs(x) ** p, x)


def chain_w(d, bones, joints):
    """Pesos ao longo de uma cadeia: joints = [(posição, meia-largura da transição), ...]."""
    w = {bones[0]: 1.0}
    for i, (J, half) in enumerate(joints):
        u = S.smooth((d - (J - half)) / (2 * half)) if half > 0 else float(d >= J)
        if u <= 0:
            break
        a, b = bones[i], bones[i + 1]
        moved = w.get(a, 0.0) * u
        w[a] = w.get(a, 0.0) - moved
        w[b] = w.get(b, 0.0) + moved
    return {k: v for k, v in w.items() if v > 1e-4}


def resample(stations, step):
    """Interpola estações (d, a, b, ...) a cada `step`, mantendo as originais."""
    st = sorted(stations)
    ds = sorted(set([s[0] for s in st] + list(np.arange(st[0][0], st[-1][0], step))))
    arr = np.array(st, float)
    return [tuple([d] + [float(np.interp(d, arr[:, 0], arr[:, j])) for j in range(1, arr.shape[1])]) for d in ds]


class Cage:
    def __init__(self, name):
        self.name = name
        self.V, self.F, self.FUV, self.W = [], [], [], []

    def tube(self, rings, sides=8, cap0=True, cap1=True, circ=None):
        """Tubo de anéis. Cada anel: c (centro), t (direção do tubo), z (para onde aponta o
        eixo 'rz'), rx, rz, w (pesos) ou wfn(p) -> pesos, exp (superelipse), wob (irregularidade),
        seed, rfn(a) -> fator do raio no ângulo a (a = pi/2 aponta para 'z'), post(p) -> p. O frame de cada anel tem ax x az = t, para as normais saírem para fora."""
        base, n = len(self.V), sides
        if circ is None:
            circ = TAU * float(np.mean([(r['rx'] + r['rz']) / 2 for r in rings]))
        self.circ = circ
        vs, cum, prev = [], 0.0, None
        for r in rings:
            c = np.asarray(r['c'], float)
            t = S.unit(r['t'])
            zh = np.asarray(r.get('z', (0, 0, 1)), float)
            az = S.unit(zh - np.dot(zh, t) * t)
            ax = np.cross(az, t)
            if prev is not None:
                cum += float(np.linalg.norm(c - prev))
            prev = c
            vs.append(cum)
            e = 2.0 / r.get('exp', 2.0)
            wob, seed = r.get('wob', 0.0), r.get('seed', 0.0)
            rfn = r.get('rfn')
            for k in range(n):
                a = TAU * k / n
                rad = 1 + wob * (0.6 * math.sin(3 * a + seed) + 0.4 * math.sin(5 * a + 2.3 * seed))
                if rfn is not None:                  # dobras: dependem do ângulo em volta do eixo
                    rad *= rfn(a)
                p = c + ax * r['rx'] * spow(math.cos(a), e) * rad + az * r['rz'] * spow(math.sin(a), e) * rad
                if 'post' in r:
                    p = r['post'](p)
                self.V.append(p)
                self.W.append(r['wfn'](p) if 'wfn' in r else r['w'])
        for i in range(len(rings) - 1):
            for k in range(n):
                k1 = (k + 1) % n
                self.F.append((base + i * n + k, base + i * n + k1, base + (i + 1) * n + k1, base + (i + 1) * n + k))
                u0, u1 = k / n * circ, (k + 1) / n * circ
                self.FUV.append(((u0, vs[i]), (u1, vs[i]), (u1, vs[i + 1]), (u0, vs[i + 1])))
        cap_uv = lambda k, v: (0.5 * circ + 0.01 * math.cos(TAU * k / n), v + 0.01 * math.sin(TAU * k / n))
        if cap0:
            self.F.append(tuple(base + k for k in reversed(range(n))))
            self.FUV.append(tuple(cap_uv(k, vs[0]) for k in reversed(range(n))))
        if cap1:
            last = base + (len(rings) - 1) * n
            self.F.append(tuple(last + k for k in range(n)))
            self.FUV.append(tuple(cap_uv(k, vs[-1]) for k in range(n)))
        return self

    def merge(self, other):
        """Acrescenta as faces de outra gaiola (ex.: antebraço na mão, para fundir o punho)."""
        base = len(self.V)
        self.V += other.V
        self.W += other.W
        self.F += [tuple(i + base for i in f) for f in other.F]
        self.FUV += other.FUV
        return self

    def arrays(self):
        bones = sorted({b for w in self.W for b in w})
        Wm = np.zeros((len(self.V), len(bones)))
        for i, w in enumerate(self.W):
            tot = sum(w.values())
            for b, x in w.items():
                Wm[i, bones.index(b)] = x / tot
        return np.array(self.V, float), bones, Wm


def _local(R, h):
    return lambda p: R @ np.asarray(p, float) + h


# ---------- mãos ----------
PALM = [  # (y, meia-largura, meia-espessura, centro z)
    (-0.014, 0.025, 0.016, 0.000), (0.000, 0.029, 0.0175, 0.000), (0.020, 0.0345, 0.0172, -0.001),
    (0.045, 0.0395, 0.0163, -0.001), (0.066, 0.0420, 0.0152, 0.000), (0.080, 0.0432, 0.0140, 0.000),
    (0.091, 0.0420, 0.0118, -0.001), (0.101, 0.0385, 0.0080, -0.0045), (0.107, 0.0320, 0.0048, -0.0055),
]   # as duas últimas formam a membrana entre os dedos, do lado da palma


def hand(side, s, rest, glove=0.0):
    """Mão com palma, quatro dedos de três falanges e polegar com eminência tenar.
    Devolve (pele ou luva, unhas). glove engrossa tudo e dispensa as unhas."""
    Rh, W0 = rest[f'{side}_hand']
    to = _local(Rh, W0)
    hb = f'{side}_hand'
    cage = Cage(f'pov_{side}_hand')

    def slant(p):                    # nós dos dedos em arco: o lado do mínimo fica mais curto
        if p[1] > 0.06:
            q = p.copy()
            q[1] -= 0.22 * max(0.0, s * p[0]) * min(1.0, (p[1] - 0.06) / 0.02) + 0.06 * max(0.0, -s * p[0] - 0.02)
            return to(q)
        return to(p)

    cage.tube([{'c': (0, y, cz), 't': (0, 1, 0), 'z': (0, 0, 1), 'rx': rx + glove, 'rz': rz + glove,
                'exp': 2.5, 'w': {hb: 1.0}, 'post': slant} for y, rx, rz, cz in PALM], sides=12)

    nails = Cage(f'pov_{side}_nails')
    for name, x, y, z, lens, r0, spread in S.FINGERS:
        R0, h0 = rest[f'{side}_{name}_0']
        bones = [hb] + [f'{side}_{name}_{j}' for j in range(3)]
        j1, j2 = lens[0], lens[0] + lens[1]
        L = sum(lens)
        prof = [(-0.016, 1.10), (-0.004, 1.14), (0.004, 1.10), (lens[0] * 0.55, 0.95), (j1, 0.95),
                (j1 + lens[1] * 0.5, 0.84), (j2, 0.84), (j2 + lens[2] * 0.45, 0.80), (j2 + lens[2] * 0.78, 0.73),
                (L - 0.004, 0.58), (L - 0.0008, 0.28)]
        rings = []
        for d, f in prof:
            r = r0 * f + glove
            rings.append({'c': h0 + R0[:, 1] * d + R0[:, 2] * (-0.0008 if d > j2 else 0.0), 't': R0[:, 1], 'z': R0[:, 2],
                          'rx': r, 'rz': r * 0.86, 'w': chain_w(d, bones, [(-0.006, 0.008), (j1, 0.006), (j2, 0.005)])})
        cage.tube(rings, sides=8)
        if not glove:
            Rd, hd = rest[f'{side}_{name}_2']
            rd = r0 * 0.85
            zc = rd * 0.86 * 0.80          # unha rente: a pele fundida encolhe uns décimos de mm

            def curve(p, Rd=Rd, hd=hd, zc=zc):
                q = p.copy()
                q[2] -= 3.0 * q[0] * q[0]
                return Rd @ q + hd
            nails.tube([{'c': (0, lens[2] * f, zc + dz), 't': (0, 1, 0), 'z': (0, 0, 1), 'rx': rd * k,
                         'rz': 0.0009, 'w': {f'{side}_{name}_2': 1.0}, 'post': curve}
                        for f, k, dz in ((0.42, 0.40, -0.0006), (0.54, 0.54, 0.0), (0.78, 0.55, 0.0), (0.88, 0.44, -0.0008))],
                       sides=8)

    # polegar: metacarpo carnudo (tenar) que sai de dentro da palma, falange proximal e distal
    R0, h0 = rest[f'{side}_thumb_0']
    bones = [hb, f'{side}_thumb_0', f'{side}_thumb_1', f'{side}_thumb_2']
    m, p1 = S.THUMB_LEN[0], S.THUMB_LEN[0] + S.THUMB_LEN[1]
    L = sum(S.THUMB_LEN)
    prof = [(-0.012, 0.0150, 0.0125), (0.004, 0.0168, 0.0140), (0.024, 0.0150, 0.0128), (m, 0.0118, 0.0105),
            (m + 0.015, 0.0110, 0.0096), (p1, 0.0108, 0.0092), (p1 + 0.011, 0.0104, 0.0089),
            (p1 + 0.020, 0.0093, 0.0078), (L - 0.004, 0.0072, 0.0060), (L - 0.0008, 0.0034, 0.0028)]
    cage.tube([{'c': h0 + R0[:, 1] * d, 't': R0[:, 1], 'z': R0[:, 2], 'rx': rx + glove, 'rz': rz + glove,
                'w': chain_w(d, bones, [(0.010, 0.012), (m, 0.006), (p1, 0.005)])} for d, rx, rz in prof], sides=8)
    if not glove:
        Rd, hd = rest[f'{side}_thumb_2']

        def curve_t(p):
            q = p.copy()
            q[2] -= 2.5 * q[0] * q[0]
            return Rd @ q + hd
        nails.tube([{'c': (0, S.THUMB_LEN[2] * f, 0.0072 + dz), 't': (0, 1, 0), 'z': (0, 0, 1), 'rx': 0.0093 * k,
                     'rz': 0.0010, 'w': {f'{side}_thumb_2': 1.0}, 'post': curve_t}
                    for f, k, dz in ((0.40, 0.42, -0.0006), (0.52, 0.58, 0.0), (0.78, 0.58, 0.0), (0.88, 0.45, -0.0008))],
                   sides=8)
    return cage, (nails if not glove else None)


def forearm_skin(side, rest, glove=0.0):
    """Pele do antebraço até o punho: só aparece no vão entre a manga e a mão."""
    Rf, E = rest[f'{side}_fore']
    c = Cage(f'pov_{side}_wrist')
    st = [(0.14, 0.031, 0.026), (0.20, 0.029, 0.022), (0.245, 0.0275, 0.0195), (S.FORE + 0.004, 0.027, 0.0185)]
    c.tube([{'c': E + Rf[:, 1] * d, 't': Rf[:, 1], 'z': Rf[:, 2], 'rx': a + glove, 'rz': b + glove,
             'w': chain_w(d, [f'{side}_fore', f'{side}_hand'], [(S.FORE - 0.004, 0.01)])} for d, a, b in st], sides=10)
    return c


# ---------- roupa ----------
def _arm_point(rest, side, d):
    Ru, Sh = rest[f'{side}_upper']
    Rf, E = rest[f'{side}_fore']
    return (Sh + Ru[:, 1] * d, Ru) if d <= S.UPPER else (E + Rf[:, 1] * (d - S.UPPER), Rf)


def _sleeve_folds(d, end, s):
    """Dobras da manga no ponto d (m a partir do ombro). Lado de dentro do cotovelo (a = pi/2):
    vincos curvos de compressão; antebraço: tecido acumulado em hélice; braço: caimento sob a axila."""
    elbow = S.smooth((d - 0.2) / 0.06) * (1 - S.smooth((d - 0.38) / 0.05))
    fore = S.smooth((d - 0.36) / 0.05) * (1 - S.smooth((d - (end - 0.035)) / 0.025))
    upper = S.smooth((d - 0.05) / 0.05) * (1 - S.smooth((d - 0.2) / 0.05))

    def rfn(a):
        inner = max(0.0, math.sin(a)) ** 1.5
        f = 1.0
        f += 0.07 * elbow * inner * math.sin(TAU * d / 0.034 + 1.4 * math.cos(a))
        f += 0.012 * elbow * math.sin(TAU * d / 0.05 + 2 * a)
        f += 0.04 * fore * math.sin(TAU * d / 0.048 + 2 * a + 0.8 * s) * (0.6 + 0.4 * inner)
        f += 0.018 * upper * math.sin(3 * a + TAU * d / 0.09) * max(0.0, -math.cos(a) * s + 0.3)
        return f
    return rfn


def sleeve(side, s, rest, spec, name='sleeve'):
    """Manga com volume que afina até o punho, dobras discretas e borda com espessura de tecido."""
    st = resample(spec['stations'], 0.03)
    end = st[-1][0]
    bones = ['chest', f'{side}_upper', f'{side}_fore']
    joints = [(0.02, 0.05), (S.UPPER, 0.07)]
    turn = spec.get('turnback')
    st = resample(spec['stations'], 0.015)            # anéis mais próximos: dobras com forma
    end = st[-1][0]
    rings = []
    for i, (d, rx, rz) in enumerate(st):
        extra = 0.008 if (turn and d > end - 0.115) else 0.0
        c, R = _arm_point(rest, side, d)
        rings.append({'c': c, 't': R[:, 1], 'z': R[:, 2], 'rx': rx + extra, 'rz': rz + extra,
                      'wob': 0.02, 'seed': 1.7 * i + s, 'rfn': _sleeve_folds(d, end, s),
                      'w': chain_w(d, bones, joints)})
        if turn and i + 1 < len(st) and d < end - 0.115 < st[i + 1][0]:
            for dd, ex in ((end - 0.117, 0.0), (end - 0.115, 0.008)):   # degrau do punho virado
                c, R = _arm_point(rest, side, dd)
                rr = float(np.interp(dd, [x[0] for x in st], [x[1] for x in st]))
                rz2 = float(np.interp(dd, [x[0] for x in st], [x[2] for x in st]))
                rings.append({'c': c, 't': R[:, 1], 'z': R[:, 2], 'rx': rr + ex, 'rz': rz2 + ex,
                              'w': chain_w(dd, bones, joints)})
    # borda: o tecido dobra para dentro, com 4 mm de espessura
    rx, rz = rings[-1]['rx'], rings[-1]['rz']
    for dd, k in ((end + 0.002, -0.0025), (end - 0.001, -0.005), (end - 0.03, -0.006)):
        c, R = _arm_point(rest, side, dd)
        # o frame não inverte: só a progressão volta, e as normais da parte de dentro olham para dentro
        rings.append({'c': c, 't': R[:, 1], 'z': R[:, 2], 'rx': rx + k, 'rz': rz + k,
                      'w': chain_w(dd, bones, joints)})
    cage = Cage(f'pov_{side}_{name}').tube(rings, sides=12, cap1=False)
    return cage, end


def shirt_cuff(side, rest, end):
    """Punho da camisa, aparecendo 1 cm além da manga do paletó."""
    rings = []
    for d, r in ((end - 0.07, 0.0335), (end + 0.004, 0.0335), (end + 0.012, 0.033), (end + 0.0135, 0.031), (end + 0.010, 0.0295)):
        c, R = _arm_point(rest, side, d)
        rings.append({'c': c, 't': R[:, 1], 'z': R[:, 2], 'rx': r, 'rz': r * 0.88, 'w': {f'{side}_fore': 1.0}})
    return Cage(f'pov_{side}_cuff').tube(rings, sides=12, cap0=False, cap1=False)


def sleeve_buttons(side, s, rest, end, count, cage):
    """Botões decorativos no lado de fora do punho do paletó."""
    for i in range(count):
        d = end - 0.028 - i * 0.017
        c, R = _arm_point(rest, side, d)
        nrm = S.unit(R[:, 0] * s * 0.75 - R[:, 2] * 0.66)
        _button(cage, c + nrm * 0.040, nrm, 0.0065, {f'{side}_fore': 1.0})


def _button(cage, p, nrm, r, w):
    t = S.unit(nrm)
    zh = np.array([0, 0, 1.0]) if abs(t[2]) < 0.9 else np.array([0, 1.0, 0])
    cage.tube([{'c': p + t * dz, 't': t, 'z': zh, 'rx': r * f, 'rz': r * f, 'w': w}
               for dz, f in ((-0.002, 0.95), (0.0015, 1.0), (0.003, 0.82))], sides=8)


def torso_ring(stations, z):
    arr = np.array(sorted(stations), float)
    return [float(np.interp(z, arr[:, 0], arr[:, j])) for j in (1, 2, 3)]


def _torso_w(z):
    return chain_w(z, ['pelvis', 'chest'], [(1.06, 0.07)])


def _torso_folds(z, hem):
    """Caimento do tronco (a = pi/2 é a frente): quedas verticais abaixo da cintura, vincos
    horizontais leves nas costas, na altura da cintura, e um pouco de tecido sob as axilas."""
    skirt = S.smooth((1.0 - z) / 0.18) * (1 - S.smooth((hem + 0.02 - z) / 0.02))
    waist = S.smooth((z - 0.93) / 0.04) * (1 - S.smooth((z - 1.09) / 0.04))
    arm = S.smooth((z - 1.18) / 0.05) * (1 - S.smooth((z - 1.34) / 0.04))

    def rfn(a):
        back = max(0.0, -math.sin(a))
        sides = abs(math.cos(a)) ** 3
        f = 1.0
        f += 0.02 * skirt * math.sin(7 * a + 1.3) + 0.01 * skirt * math.sin(11 * a + 0.4)
        f += 0.012 * waist * back * math.sin(TAU * z / 0.045)
        f += 0.014 * arm * sides * math.sin(TAU * z / 0.05 + 2 * a)
        return f
    return rfn


def torso(spec):
    """Tronco da peça de cima, aberto na barra (com espessura) e fechado no pescoço.
    Abaixo de 0,86 m a barra acompanha um pouco as coxas, para as pernas não atravessarem."""
    st = resample(spec['stations'], 0.05)
    hem = st[0][0]
    thigh_k = 0.65 if hem < 0.5 else 0.3

    def wfn_for(z):
        def wfn(p):
            w = _torso_w(z)
            if z < 0.86:
                k = thigh_k * min(1.0, (0.86 - z) / (0.86 - hem + 1e-6))
                x = p[0]
                share = {'R_thigh': S.smooth((x + 0.03) / 0.06), 'L_thigh': 1 - S.smooth((x + 0.03) / 0.06)}
                w = {b: v * (1 - k) for b, v in w.items()}
                for b, f in share.items():
                    if f * k > 1e-4:
                        w[b] = w.get(b, 0.0) + f * k
            return w
        return wfn

    rings = []
    rx, ry, cy = st[0][1:]
    for z, k in ((hem + 0.03, -0.007), (hem - 0.001, -0.0035)):          # lado de dentro da barra
        rings.append({'c': (0, cy, z), 't': (0, 0, 1), 'z': (0, 1, 0), 'rx': rx + k, 'rz': ry + k,
                      'exp': 2.2, 'wfn': wfn_for(z)})
    st = resample(spec['stations'], 0.03)
    for i, (z, rx, ry, cy) in enumerate(st):
        rings.append({'c': (0, cy, z), 't': (0, 0, 1), 'z': (0, 1, 0), 'rx': rx, 'rz': ry, 'exp': 2.2,
                      'wob': 0.008, 'seed': i * 0.9, 'rfn': _torso_folds(z, hem), 'wfn': wfn_for(z)})
    cage = Cage('pov_torso').tube(rings, sides=24, cap0=False, cap1=True)
    return cage


def torso_buttons(spec, cage):
    for z, x in spec['buttons']:
        rx, ry, cy = torso_ring(spec['stations'], z)
        u = max(-0.95, min(0.95, x / rx))
        y = cy + ry * math.sqrt(1 - u * u)
        nrm = S.unit((x / (rx * rx), (y - cy) / (ry * ry), 0.0))
        _button(cage, np.array([x, y, z]) + nrm * 0.004, nrm, 0.0085 if abs(x) > 0 else 0.0078, _torso_w(z))


def belt(spec_torso, belt_spec):
    z = belt_spec['z']
    rx, ry, cy = torso_ring(spec_torso['stations'], z)
    c = Cage('pov_belt')
    c.tube([{'c': (0, cy, z + dz), 't': (0, 0, 1), 'z': (0, 1, 0), 'rx': rx + k, 'rz': ry + k, 'exp': 2.2,
             'w': _torso_w(z)} for dz, k in ((-0.024, 0.001), (-0.022, 0.007), (0.022, 0.007), (0.024, 0.001))],
           sides=24, cap0=False, cap1=False)
    buckle = Cage('pov_buckle')
    yf = cy + ry + 0.006
    buckle.tube([{'c': (0, yf + dy, z), 't': (0, 1, 0), 'z': (0, 0, 1), 'rx': 0.032 * f, 'rz': 0.026 * f, 'exp': 6,
                  'w': _torso_w(z)} for dy, f in ((-0.004, 0.95), (0.002, 1.0), (0.005, 0.93))], sides=12)
    return c, buckle


def _trouser_folds(d, end, tucked):
    """Vincos atrás do joelho (lado da dobra, a = pi/2) e a quebra da barra sobre o sapato
    (ou o tecido franzido que entra no cano da bota)."""
    knee = S.smooth((d - (S.THIGH - 0.08)) / 0.04) * (1 - S.smooth((d - (S.THIGH + 0.07)) / 0.04))
    low = S.smooth((d - (end - 0.12)) / 0.05)

    def rfn(a):
        inner = max(0.0, math.sin(a)) ** 1.5
        f = 1.0 + 0.045 * knee * inner * math.sin(TAU * d / 0.03 + 1.2 * math.cos(a))
        f += (0.035 if tucked else 0.022) * low * math.sin(TAU * d / 0.045 + 2 * a) * (0.5 + 0.5 * max(0.0, -math.sin(a)))
        return f
    return rfn


def trousers(side, s, rest, spec):
    Rt, H = rest[f'{side}_thigh']
    Rs, K = rest[f'{side}_shin']
    bones = ['pelvis', f'{side}_thigh', f'{side}_shin']
    joints = [(0.06, 0.08), (S.THIGH, 0.06)]
    st = resample([(H[2] - z, r) for z, r in spec['stations']], 0.025)
    rings = []
    for i, (d, r) in enumerate(st):
        c = H + Rt[:, 1] * d if d <= S.THIGH else K + Rs[:, 1] * (d - S.THIGH)
        R = Rt if d <= S.THIGH else Rs
        rings.append({'c': c + np.array([-s * 0.008 * max(0.0, 0.2 - d) / 0.2, 0, 0]), 't': R[:, 1], 'z': R[:, 2],
                      'rx': r, 'rz': r * 0.96, 'wob': 0.02, 'seed': i * 1.3 + s,
                      'rfn': _trouser_folds(d, st[-1][0], bool(spec.get('tucked'))),
                      'w': chain_w(d, bones, joints)})
    tucked = spec.get('tucked')
    if not tucked:                    # barra com espessura
        d, r = st[-1]
        for dd, k in ((d + 0.002, -0.002), (d - 0.025, -0.005)):
            rings.append({'c': K + Rs[:, 1] * (dd - S.THIGH), 't': Rs[:, 1],
                          'z': Rs[:, 2], 'rx': r + k, 'rz': r * 0.96 + k, 'w': {f'{side}_shin': 1.0}})
    return Cage(f'pov_{side}_trousers').tube(rings, sides=12, cap0=True, cap1=bool(tucked))


FOOTWEAR = {
    # (dy a partir do tornozelo, meia-largura, altura do cabedal acima do chão)
    'ankle_boot': {'upper': [(-0.062, 0.022, 0.06), (-0.055, 0.031, 0.09), (-0.035, 0.035, 0.12), (0.0, 0.036, 0.13),
                             (0.045, 0.040, 0.098), (0.095, 0.045, 0.075), (0.145, 0.047, 0.060), (0.18, 0.043, 0.052),
                             (0.200, 0.034, 0.045), (0.213, 0.019, 0.037)],
                   'shaft': [(0.09, 0.046), (0.13, 0.045), (0.165, 0.046)], 'heel': 0.026, 'sole': 0.011},
    'jackboot': {'upper': [(-0.064, 0.024, 0.06), (-0.057, 0.034, 0.10), (-0.035, 0.038, 0.14), (0.0, 0.039, 0.15),
                           (0.045, 0.043, 0.105), (0.095, 0.048, 0.080), (0.145, 0.050, 0.065), (0.18, 0.047, 0.058),
                           (0.202, 0.039, 0.051), (0.216, 0.024, 0.043)],
                 'shaft': [(0.10, 0.050), (0.16, 0.048), (0.24, 0.052), (0.33, 0.058), (0.395, 0.062)],
                 'heel': 0.032, 'sole': 0.015},
    'kirza_boot': {'upper': [(-0.064, 0.024, 0.06), (-0.057, 0.034, 0.10), (-0.035, 0.038, 0.14), (0.0, 0.040, 0.15),
                             (0.045, 0.044, 0.106), (0.095, 0.049, 0.082), (0.145, 0.051, 0.066), (0.18, 0.048, 0.059),
                             (0.202, 0.040, 0.052), (0.216, 0.025, 0.044)],
                   'shaft': [(0.10, 0.051), (0.16, 0.050), (0.24, 0.054), (0.32, 0.060), (0.38, 0.064)],
                   'heel': 0.030, 'sole': 0.014},
}


def footwear(side, s, rest, kind):
    """Calçado: cabedal, sola com salto e cano. Devolve (couro, sola)."""
    spec = FOOTWEAR[kind]
    _, A = rest[f'{side}_foot']
    fb = [f'{side}_foot', f'{side}_toe']
    ball = float(S.FOOT_VEC[1])

    def sole_top(dy):
        return spec['heel'] if dy < 0.0 else float(np.interp(dy, [0.0, 0.05, 0.11], [spec['heel'], spec['sole'] + 0.004, spec['sole']]))

    def w_of(dy):
        return chain_w(dy, fb, [(ball, 0.02)])

    up = Cage(f'pov_{side}_shoe')
    rings = []
    for i, (dy, hw, top) in enumerate(spec['upper']):
        st = sole_top(dy) - 0.003
        rz = (top - st) / 2
        xm = -s * 0.009 * max(0.0, dy - 0.10) / 0.11            # dedão para dentro
        rings.append({'c': (A[0] + xm, A[1] + dy, st + rz), 't': (0, 1, 0), 'z': (0, 0, 1), 'rx': hw, 'rz': rz,
                      'exp': 2.4, 'wob': 0.01, 'seed': i, 'w': w_of(dy)})
    up.tube(rings, sides=12)
    # cano: do tornozelo para cima, acompanhando a perna
    Rs, K = rest[f'{side}_shin']
    sh = []
    for z, r in spec['shaft']:
        d = K[2] - z
        w = chain_w(-z, [f'{side}_shin', f'{side}_foot'], [(-0.12, 0.03)])
        sh.append({'c': K + Rs[:, 1] * d + np.array([0, 0.004, 0]), 't': Rs[:, 1], 'z': Rs[:, 2],
                   'rx': r, 'rz': r * 1.05, 'wob': 0.02, 'seed': z * 40, 'w': w})
    top_d = K[2] - spec['shaft'][-1][0]
    r = spec['shaft'][-1][1]
    for dd, k in ((top_d - 0.002, -0.002), (top_d + 0.02, -0.005)):     # borda do cano
        sh.append({'c': K + Rs[:, 1] * dd + np.array([0, 0.004, 0]), 't': Rs[:, 1],
                   'z': Rs[:, 2], 'rx': r + k, 'rz': r * 1.05 + k, 'w': {f'{side}_shin': 1.0}})
    sh = sh[::-1]
    for ring in sh:
        ring['t'] = Rs[:, 1]
    up.tube(sh, sides=12, cap0=False, cap1=True)

    sole = Cage(f'pov_{side}_sole')
    rings = []
    for dy, hw, _ in spec['upper']:
        top = sole_top(dy)
        xm = -s * 0.009 * max(0.0, dy - 0.10) / 0.11
        rings.append({'c': (A[0] + xm, A[1] + dy + (0.002 if dy > 0.2 else 0), top / 2), 't': (0, 1, 0), 'z': (0, 0, 1),
                      'rx': hw + 0.0035, 'rz': top / 2, 'exp': 5.0, 'w': w_of(dy)})
    sole.tube(rings, sides=12)
    laces = None
    if kind == 'ankle_boot':          # lingueta e cadarço cruzado no peito do pé
        laces = Cage(f'pov_{side}_laces')
        ups = np.array(spec['upper'])
        top = lambda dy: float(np.interp(dy, ups[:, 0], ups[:, 2]))
        laces.tube([{'c': (A[0], A[1] + dy, top(dy) + 0.0005), 't': (0, 1, 0), 'z': (0, 0, 1), 'rx': 0.0115, 'rz': 0.0028,
                     'exp': 3.0, 'w': w_of(dy)} for dy in (-0.012, 0.01, 0.04, 0.07, 0.092)], sides=8)
        for i, dy in enumerate((0.0, 0.018, 0.036, 0.054, 0.072)):
            z = top(dy) + 0.0032
            for sgn in (-1, 1):             # duas pernas do X, de um ilhós ao outro
                p0 = np.array([A[0] - 0.012, A[1] + dy, z])
                p1 = np.array([A[0] + 0.012, A[1] + dy + sgn * 0.009, z])
                laces.tube([{'c': p0 + (p1 - p0) * u, 't': p1 - p0, 'z': (0, 0, 1), 'rx': 0.0016, 'rz': 0.0013,
                             'w': w_of(dy)} for u in (0.0, 0.5, 1.0)], sides=6)
    return up, sole, laces


# ---------- cabeça (só sombra) ----------
def head_proxy(hat):
    """Pescoço, cabeça e chapéu, presos ao osso 'head' (pivô na base do pescoço).
    Não aparecem na câmera; existem para a sombra do corpo no chão ter cabeça."""
    w = {'head': 1.0}
    P = S.HEAD_PIVOT
    c = Cage('pov_head_shadow')
    c.tube([{'c': P + np.array([0, 0.0, dz]), 't': (0, 0, 1), 'z': (0, 1, 0), 'rx': r, 'rz': r * 1.05, 'w': w}
            for dz, r in ((-0.03, 0.06), (0.06, 0.055), (0.12, 0.058))], sides=10)
    skull = [(0.10, 0.03), (0.13, 0.075), (0.18, 0.090), (0.24, 0.092), (0.29, 0.080), (0.32, 0.055), (0.335, 0.02)]
    c.tube([{'c': P + np.array([0, 0.035, dz]), 't': (0, 0, 1), 'z': (0, 1, 0), 'rx': r * 0.82, 'rz': r, 'w': w}
            for dz, r in skull], sides=12)
    if hat == 'homburg':        # copa e aba
        c.tube([{'c': P + np.array([0, 0.03, dz]), 't': (0, 0, 1), 'z': (0, 1, 0), 'rx': r * 0.9, 'rz': r, 'w': w}
                for dz, r in ((0.24, 0.150), (0.255, 0.150), (0.26, 0.095), (0.36, 0.088), (0.37, 0.06))], sides=16)
    elif hat == 'stahlhelm':    # casco com a saia aberta atrás e dos lados
        c.tube([{'c': P + np.array([0, 0.02, dz]), 't': (0, 0, 1), 'z': (0, 1, 0), 'rx': r * 0.92, 'rz': r, 'w': w}
                for dz, r in ((0.17, 0.155), (0.20, 0.135), (0.26, 0.128), (0.32, 0.11), (0.355, 0.06))], sides=16)
    elif hat == 'ushanka':      # gorro de pele com abas
        c.tube([{'c': P + np.array([0, 0.03, dz]), 't': (0, 0, 1), 'z': (0, 1, 0), 'rx': r * 0.95, 'rz': r, 'w': w}
                for dz, r in ((0.14, 0.11), (0.22, 0.125), (0.31, 0.12), (0.36, 0.09), (0.375, 0.04))], sides=16)
    return c


# ---------- objetos ----------
def pocket_watch(rest):
    """Relógio de bolso (caixa aberta, ~50 mm) na palma da mão esquerda, mostrador para cima.
    Devolve (caixa com coroa e alça, mostrador esmaltado, marcas e ponteiros, vidro)."""
    Rh, W0 = rest['L_hand']
    to = _local(Rh, W0)
    w = {'L_hand': 1.0}
    c0 = S.PALM_POINT + np.array([0.0, 0.004, -0.004])
    t = np.array([0, 0, -1.0])                  # normal do mostrador (para fora da palma)
    up = np.array([0, 1.0, 0])                   # 12 horas: para os dedos
    side = np.cross(up, t)                       # 3 horas, visto de frente (sentido horário)
    R = 0.024
    ring = lambda dz, f: {'c': to(c0 + t * dz), 't': Rh @ t, 'z': Rh @ up, 'rx': R * f, 'rz': R * f, 'w': w}
    case = Cage('pov_watch_case')
    # fundo abaulado, carrure, bisel que sobe acima do vidro e encaixa o mostrador
    case.tube([ring(dz, f) for dz, f in ((-0.0025, 0.55), (-0.0012, 0.82), (0.0004, 0.96), (0.0025, 1.0),
                                          (0.0072, 1.0), (0.0086, 0.985), (0.0101, 0.95), (0.0104, 0.90),
                                          (0.0098, 0.87))], sides=32, cap0=True, cap1=False)
    # pendente, coroa serrilhada e alça (argola) às 12 horas
    stem = lambda d: to(c0 + up * d + t * 0.0045)
    case.tube([{'c': stem(d), 't': Rh @ up, 'z': Rh @ t, 'rx': r, 'rz': r, 'w': w}
               for d, r in ((0.0225, 0.0042), (0.0262, 0.0036), (0.0272, 0.0022))], sides=12)
    case.tube([{'c': stem(d), 't': Rh @ up, 'z': Rh @ t, 'rx': r, 'rz': r, 'w': w, 'wob': wob, 'seed': 0.0}
               for d, r, wob in ((0.0270, 0.0040, 0.0), (0.0274, 0.0047, 0.06), (0.0302, 0.0047, 0.06), (0.0306, 0.0040, 0.0))],
              sides=24)
    bow = []
    for k in range(17):                          # argola: meia volta do pendente por cima
        a = math.pi * k / 16
        p = up * (0.0285 + 0.0085 * math.sin(a)) + side * (0.0095 * math.cos(a))
        tg = up * math.cos(a) - side * math.sin(a)
        bow.append({'c': to(c0 + p + t * 0.0045), 't': Rh @ tg, 'z': Rh @ t, 'rx': 0.0011, 'rz': 0.0011, 'w': w})
    case.tube(bow, sides=8)

    face = Cage('pov_watch_face')
    face.tube([ring(dz, f) for dz, f in ((0.0080, 0.94), (0.0084, 0.93))], sides=32, cap0=False, cap1=True)
    sub = up * -0.0105                           # mostrador dos segundos, às 6 horas
    face.tube([{'c': to(c0 + sub + t * dz), 't': Rh @ t, 'z': Rh @ up, 'rx': r, 'rz': r, 'w': w}
               for dz, r in ((0.00835, 0.0062), (0.0084, 0.0058))], sides=20, cap0=False, cap1=True)

    marks = Cage('pov_watch_hands')
    surf = 0.00845
    for h in range(12):                          # marcas das horas
        a = TAU * h / 12
        d = up * math.cos(a) + side * math.sin(a)
        if h == 6:
            continue
        ln = 0.0034 if h % 3 == 0 else 0.0022
        marks.tube([{'c': to(c0 + d * r + t * surf), 't': Rh @ d, 'z': Rh @ t, 'rx': 0.0006, 'rz': 0.00012, 'w': w}
                    for r in (0.0205 - ln, 0.0205)], sides=4)
    track = []                                   # trilha dos minutos
    for k in range(49):
        a = TAU * k / 48
        d = up * math.cos(a) + side * math.sin(a)
        track.append({'c': to(c0 + d * 0.0211 + t * surf), 't': Rh @ (side * math.cos(a) - up * math.sin(a)),
                      'z': Rh @ t, 'rx': 0.00022, 'rz': 0.0001, 'w': w})
    marks.tube(track, sides=4)

    def spade(ang, ln, wd, z, origin=np.zeros(3)):   # ponteiro em pá, com cubo central
        d = up * math.cos(ang) + side * math.sin(ang)
        marks.tube([{'c': to(c0 + origin + d * ln * f + t * z), 't': Rh @ d, 'z': Rh @ t, 'rx': wd * k, 'rz': 0.00018, 'w': w}
                    for f, k in ((-0.18, 0.5), (0.0, 0.9), (0.55, 0.45), (0.72, 1.4), (0.86, 1.0), (1.0, 0.15))], sides=6)
    spade(TAU * (9 + 55 / 60) / 12, 0.0125, 0.0010, surf + 0.0004)   # 9h55: a hora do intro (timeline.CLOCK)
    spade(TAU * 55 / 60, 0.0175, 0.0008, surf + 0.0007)
    spade(TAU * 0.6, 0.0050, 0.0004, surf + 0.0003, sub)
    marks.tube([{'c': to(c0 + t * dz), 't': Rh @ t, 'z': Rh @ up, 'rx': 0.0011, 'rz': 0.0011, 'w': w}
                for dz in (surf, surf + 0.0011)], sides=10)

    glass = Cage('pov_watch_glass')              # vidro abaulado
    glass.tube([ring(dz, f) for dz, f in ((0.0090, 0.90), (0.0102, 0.84), (0.0110, 0.62), (0.0113, 0.3))],
               sides=32, cap0=False, cap1=True)
    return case, face, marks, glass


RIFLES = {
    'kar98k': {
        'stock': [(-0.330, 0.0205, 0.064, -0.050), (-0.318, 0.0215, 0.065, -0.050), (-0.20, 0.0205, 0.052, -0.037),
                  (-0.10, 0.018, 0.038, -0.027), (-0.035, 0.0155, 0.023, -0.019), (0.02, 0.0185, 0.026, -0.016),
                  (0.10, 0.0225, 0.024, -0.012), (0.20, 0.021, 0.020, -0.012), (0.40, 0.0185, 0.017, -0.012),
                  (0.60, 0.0165, 0.0155, -0.011), (0.64, 0.0145, 0.013, -0.010)],
        'barrel_end': 0.78, 'receiver': (0.03, 0.24), 'bands': (0.40, 0.62), 'bolt': 'bent',
        'magazine': None,
    },
    'mosin': {
        'stock': [(-0.335, 0.020, 0.060, -0.047), (-0.322, 0.021, 0.061, -0.047), (-0.20, 0.0195, 0.049, -0.034),
                  (-0.10, 0.0175, 0.034, -0.024), (-0.035, 0.016, 0.022, -0.016), (0.03, 0.019, 0.024, -0.014),
                  (0.11, 0.0215, 0.022, -0.012), (0.22, 0.020, 0.019, -0.012), (0.45, 0.018, 0.016, -0.011),
                  (0.69, 0.0160, 0.0150, -0.010), (0.72, 0.0140, 0.0125, -0.009)],
        'barrel_end': 0.89, 'receiver': (0.03, 0.25), 'bands': (0.47, 0.70), 'bolt': 'straight',
        'magazine': (0.06, 0.15),
    },
}


def rifle(kind):
    """Fuzil no espaço dele: Y é o cano, Z a mira, origem no punho da coronha. Devolve (madeira, aço)."""
    spec = RIFLES[kind]
    w = {'rifle': 1.0}
    wood = Cage('pov_rifle_wood').tube(
        [{'c': (0, y, cz), 't': (0, 1, 0), 'z': (0, 0, 1), 'rx': hw, 'rz': hh, 'exp': 2.6, 'w': w}
         for y, hw, hh, cz in spec['stock']], sides=12)
    steel = Cage('pov_rifle_steel')
    tube = lambda pts, sides=8: steel.tube([{'c': c, 't': t, 'z': z, 'rx': rx, 'rz': rz, 'w': w, 'exp': e}
                                            for c, t, z, rx, rz, e in pts], sides=sides)
    y0, y1 = spec['receiver']
    tube([((0, y, 0.011), (0, 1, 0), (0, 0, 1), r, r, 2.0) for y, r in ((y0 - 0.006, 0.0095), (y0, 0.0135), (y1, 0.0135), (y1 + 0.01, 0.0115))])
    yb = spec['barrel_end']
    tube([((0, y, 0.009), (0, 1, 0), (0, 0, 1), r, r, 2.0) for y, r in ((y1, 0.0110), (y1 + 0.06, 0.0095), (yb - 0.01, 0.0076), (yb, 0.0072))])
    for yb_ in spec['bands']:
        tube([((0, yb_ + dy, -0.003), (0, 1, 0), (0, 0, 1), 0.0205, 0.023, 3.0) for dy in (-0.008, 0.008)])
    tube([((0, yb - 0.01 + dy, 0.020), (0, 1, 0), (0, 0, 1), 0.0045, 0.006, 3.0) for dy in (-0.008, 0.008)])   # massa de mira
    tube([((0, y1 + 0.03 + dy, 0.022), (0, 1, 0), (0, 0, 1), 0.009, 0.0045, 4.0) for dy in (-0.03, 0.03)])     # alça de mira
    tube([((0, spec['stock'][0][0] - 0.001 + dy, spec['stock'][0][3]), (0, 1, 0), (0, 0, 1),
           spec['stock'][0][1] + 0.001, spec['stock'][0][2] + 0.001, 2.6) for dy in (-0.004, 0.003)], sides=12)   # chapa da soleira
    # guarda-mato
    pts = [(0, -0.005 + 0.06 * u, -0.032 - 0.018 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 6)]
    tube([(p, (0, 1, 0), (0, 0, 1), 0.003, 0.0022, 2.0) for p in pts], sides=6)
    if spec['magazine']:
        m0, m1 = spec['magazine']
        tube([((0, y, -0.040), (0, 1, 0), (0, 0, 1), 0.016, 0.022, 5.0) for y in (m0, m1)], sides=10)
    if spec['bolt'] == 'bent':          # alavanca dobrada para baixo, com bola
        path = [(0.010, 0.075, 0.017), (0.030, 0.072, 0.012), (0.042, 0.064, -0.002)]
        knob = (0.046, 0.060, -0.010)
    else:                               # Mosin: alavanca reta para o lado
        path = [(0.010, 0.085, 0.016), (0.035, 0.085, 0.015), (0.052, 0.085, 0.013)]
        knob = (0.058, 0.085, 0.012)
    tube([(p, S.unit(np.subtract(path[-1], path[0])), (0, 0, 1), 0.0035, 0.0035, 2.0) for p in path], sides=6)
    tube([(np.add(knob, (0, 0, dz)), (0, 0, 1), (0, 1, 0), 0.0075 * f, 0.0075 * f, 2.0)
          for dz, f in ((-0.0075, 0.3), (-0.004, 0.9), (0.0, 1.0), (0.004, 0.9), (0.0075, 0.3))], sides=8)
    return wood, steel
