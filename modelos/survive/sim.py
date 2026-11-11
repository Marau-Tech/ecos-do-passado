"""Mecânica do survive: algo no centro com vida, um perigo que tira, aliados que trazem e o escuro que avança.

Não sabe o que é cada coisa: a skin diz (fogueira e chuva, lanterna e mariposas, planeta e meteoros).
Roda em sequência e guarda o estado de cada frame; o desenho e o som só leem. Coordenadas do quadro 4:3 (960x720).

Há dois geradores aleatórios: r decide o placar e rv só enfeita (a skin usa rv). Assim a busca de sementes,
que roda sem enfeite, dá o mesmo resultado do vídeo.

Busca de sementes: VIDEO=<video> PYTHONPATH=engine tools/venv/bin/python -m modelos.survive.sim [n] [survive|out]
"""
import math
import importlib
import numpy as np

W, H = 960, 720
FPS, SUB = 30, 2                 # 2 passos de física por frame
DT = 1 / (FPS * SUB)

# Ordem: DEFAULTS < SIM da skin < SIM do timeline. Os dicionários de dentro se juntam chave a chave.
DEFAULTS = dict(
    hp0=60.0,                    # vida inicial do centro, de 0 a 100
    burn=0.35,                   # vida por segundo que o centro perde sozinho
    until=36.0,                  # fim da contagem: quem chega aqui venceu
    core=dict(
        x=480, y=600,            # ponto de apoio do centro: a base, se anchor > 0, ou o meio, se anchor = 0
        w=(14, 70), h=(30, 210), exp=0.8,   # meia largura e altura: w0 + w1 * (hp/100) ** exp
        anchor=0.45,             # o meio da área de colisão fica a anchor * altura acima de y
        ry=0.55,                 # meia altura da área de colisão, em fração da altura
        aim=0.4,                 # altura, em fração, para onde os aliados vão
    ),
    threat=dict(
        mode='rain',             # rain: caem de cima com vento. aim: vêm das bordas em direção ao centro
        rate=[(0, 10), (30, 30)],           # (s, ameaças por segundo)
        wind=[(0, 0)],                      # (s, px/s), só no rain
        speed=(850, 1050),
        spread=0.25,             # desvio da mira em radianos, só no aim
        edges='tlr',             # bordas de onde vêm no aim: t (cima), b (baixo), l (esquerda), r (direita)
        dmg=2.0,                 # vida que cada ameaça tira do centro
        floor=600,               # no rain, a altura em que a ameaça bate no chão e some
    ),
    ally=dict(
        hp=3,                    # ameaças que destroem um aliado
        gap=[(0, 2.2)],          # (s, segundos entre aliados)
        first=1.2, stop=3.0,     # o primeiro sai em first; param stop segundos antes do until
        speed=(120, 160), wobble=(25, 55),
        y=(90, 330),             # faixa de altura em que nascem, nas bordas da esquerda e da direita
        gain0=4.0, gain1=2.5,    # vida que dá ao chegar: gain0 + gain1 por vida que sobrou nele
    ),
    dark=dict(r0=70, r1=4.6),    # raio do lugar seguro: r0 + r1 * hp. Os vigias param logo depois dele
    watch=dict(n=7, arrive=(3.0, 2.6), size=(150, 210)),   # vigias: quantos, quando chega o 1º e o intervalo
)


def skin_of(tl):
    """A skin do vídeo: SKIN no timeline. Procura em modelos/survive/skins/ e depois na pasta do vídeo."""
    name = getattr(tl, 'SKIN', 'campfire')
    try:
        return importlib.import_module(f'modelos.survive.skins.{name}')
    except ModuleNotFoundError:
        return importlib.import_module(name)


def merge(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def config(tl):
    c = merge(merge(DEFAULTS, getattr(skin_of(tl), 'SIM', {})), getattr(tl, 'SIM', {}))
    c['seed'] = tl.SEED
    c['total'] = tl.TOTAL
    return c


def curve(pts, t):
    xs, ys = zip(*pts)
    return float(np.interp(t, xs, ys))


class Sim:
    def __init__(self, c, visual=True, skin=None):
        self.c = c
        self.r = np.random.RandomState(c['seed'])
        self.rv = np.random.RandomState(c['seed'] + 99)
        self.visual = visual
        self.skin = skin if visual else None
        self.hp = c['hp0']
        self.t = 0.0
        self.threats = np.zeros((0, 4))     # x, y, vx, vy
        self.allies = []
        self.next_ally = c['ally']['first']
        self.side = self.r.randint(2)
        self.events = []                    # (t, tipo, x, y[, ganho]): spawn, hit, block, lost, feed, floor, out
        self.dead_at = None
        self.frames = []
        self.fx = {}                        # estado visual da skin
        self._dark = []
        rv, wc = self.rv, c['watch']
        a0, da = wc['arrive']
        self.watch = [dict(side=1 if i % 2 else -1, extra=rv.uniform(40, 220), size=rv.uniform(*wc['size']),
                           d=560.0, arrive=a0 + i * da + rv.uniform(0, 1.5), blink=rv.uniform(0, 10),
                           lean=rv.uniform(-0.08, 0.08)) for i in range(wc['n'])]

    # ---- leituras ----
    def rate(self, t):
        return curve(self.c['threat']['rate'], t)

    def wind(self, t):
        return curve(self.c['threat']['wind'], t)

    def size(self, hp=None):
        """Meia largura e altura do centro."""
        cc = self.c['core']
        k = max(self.hp if hp is None else hp, 0) / 100
        return cc['w'][0] + cc['w'][1] * k ** cc['exp'], cc['h'][0] + cc['h'][1] * k ** cc['exp']

    def safe(self, hp=None):
        d = self.c['dark']
        return d['r0'] + d['r1'] * (self.hp if hp is None else hp)

    # ---- física ----
    def spawn_threats(self, n):
        r, th, t = self.r, self.c['threat'], self.t
        if th['mode'] == 'rain':
            return np.column_stack([r.uniform(-60, W + 160, n), r.uniform(-40, 0, n),
                                    np.full(n, self.wind(t)) + r.uniform(-15, 15, n), r.uniform(*th['speed'], n)])
        # aim: de um ponto qualquer das bordas em th['edges'] (t, b, l, r), mirando o centro
        cc = self.c['core']
        _, h = self.size()
        cx, cy = cc['x'], cc['y'] - h * cc['anchor']
        edges = th.get('edges', 'tlr')
        lens = np.array([W if e in 'tb' else H * 0.8 for e in edges])
        u = r.uniform(0, lens.sum(), n)
        k = np.searchsorted(np.cumsum(lens), u, side='right')
        off = u - np.concatenate([[0], np.cumsum(lens)])[k]
        side = np.array(list(edges))[k]
        x = np.select([side == 't', side == 'b', side == 'l'], [off, off, -20], W + 20)
        y = np.select([side == 't', side == 'b'], [-20, H + 20], off + H * 0.1)
        ang = np.arctan2(cy - y, cx - x) + r.normal(0, th['spread'], n)
        sp = r.uniform(*th['speed'], n)
        return np.column_stack([x, y, np.cos(ang) * sp, np.sin(ang) * sp])

    def spawn_ally(self):
        r, a = self.r, self.c['ally']
        self.side = 1 - self.side if r.rand() < 0.75 else self.side
        x = -10 if self.side == 0 else W + 10
        y = r.uniform(*a['y'])
        self.allies.append(dict(x=x, y=y, hp=a['hp'], ph=r.uniform(0, 6.28), sp=r.uniform(*a['speed']),
                                wob=r.uniform(*a['wobble']), born=self.t))
        self.events.append((self.t, 'spawn', x, y))

    def step(self):
        r, t, c = self.r, self.t, self.c
        th, cc, al = c['threat'], c['core'], c['ally']
        n0 = len(self.events)
        n = r.poisson(self.rate(t) * DT)
        if n:
            self.threats = np.vstack([self.threats, self.spawn_threats(n)])
        d = self.threats
        px, py = d[:, 0].copy(), d[:, 1].copy()
        d[:, 0] += d[:, 2] * DT
        d[:, 1] += d[:, 3] * DT
        keep = np.ones(len(d), bool)

        # ameaça no centro
        w, h = self.size()
        if self.hp > 0:
            cy = cc['y'] - h * cc['anchor']
            inside = ((d[:, 0] - cc['x']) / w) ** 2 + ((d[:, 1] - cy) / (h * cc['ry'])) ** 2 < 1
            for i in np.nonzero(inside)[0]:
                keep[i] = False
                self.hp -= th['dmg']
                self.events.append((t, 'hit', d[i, 0], d[i, 1]))

        # ameaça no aliado
        for e in self.allies:
            rad = 5 + 2.5 * e['hp']
            if th['mode'] == 'rain':          # quase vertical: teste rápido pelo trecho que a gota andou
                hit = keep & (np.abs(d[:, 0] - e['x']) < rad) & (py - rad < e['y']) & (d[:, 1] + rad > e['y'])
            else:                             # distância do aliado ao trecho que a ameaça andou
                sx, sy = d[:, 0] - px, d[:, 1] - py
                k = np.clip(((e['x'] - px) * sx + (e['y'] - py) * sy) / np.maximum(sx * sx + sy * sy, 1e-6), 0, 1)
                hit = keep & ((px + k * sx - e['x']) ** 2 + (py + k * sy - e['y']) ** 2 < rad * rad)
            for i in np.nonzero(hit)[0]:
                keep[i] = False
                e['hp'] -= 1
                self.events.append((t, 'block', e['x'], e['y']))
                if e['hp'] <= 0:
                    break

        # fim do caminho da ameaça
        if th['mode'] == 'rain':
            g = keep & (d[:, 1] >= th['floor'] + r.uniform(-4, 18, len(d)))
            if self.visual:
                for i in np.nonzero(g)[0][:6]:
                    self.events.append((t, 'floor', d[i, 0], d[i, 1]))
            keep &= ~g
            keep &= d[:, 0] > -80
        else:
            keep &= (d[:, 0] > -60) & (d[:, 0] < W + 60) & (d[:, 1] > -60) & (d[:, 1] < H + 60)
        self.threats = d[keep]

        # aliados indo para o centro
        alive = []
        for e in self.allies:
            if e['hp'] <= 0:
                self.events.append((t, 'lost', e['x'], e['y']))
                continue
            tx, ty = cc['x'], cc['y'] - h * cc['aim']
            dx, dy = tx - e['x'], ty - e['y']
            dist = math.hypot(dx, dy)
            if dist < max(w * 0.7, 20):
                if self.hp > 0:
                    gain = al['gain0'] + al['gain1'] * e['hp']
                    self.hp = min(100, self.hp + gain)
                    self.events.append((t, 'feed', e['x'], e['y'], gain))
                else:
                    self.events.append((t, 'lost', e['x'], e['y']))
                continue
            ux, uy = dx / dist, dy / dist
            wob = math.sin((t - e['born']) * 3.1 + e['ph']) * e['wob']
            e['x'] += (ux * e['sp'] - uy * wob) * DT
            e['y'] += (uy * e['sp'] + ux * wob) * DT
            alive.append(e)
        self.allies = alive

        if t >= self.next_ally and t < c['until'] - al['stop'] and self.dead_at is None:
            self.spawn_ally()
            self.next_ally = t + curve(al['gap'], t) * r.uniform(0.75, 1.3)

        # sem vida, sem volta
        if self.hp <= 0 and self.dead_at is None:
            self.hp = 0
            self.dead_at = t
            self.events.append((t, 'out', cc['x'], cc['y']))
        if self.hp > 0:
            self.hp = max(self.hp - c['burn'] * DT, 0)

        if self.skin is not None and hasattr(self.skin, 'step'):
            self.skin.step(self, self.events[n0:])
        self.t += DT

    def _watchers(self):
        """Os vigias param logo depois do lugar seguro: avançam devagar e recuam rápido. Sem vida, eles vêm."""
        self._dark.append(self.safe())
        lr = np.mean(self._dark[-9:])
        w, _ = self.size()
        out = []
        for f in self.watch:
            if self.t < f['arrive']:
                tgt = 560
            elif self.dead_at is not None:
                tgt = 40 + f['extra'] * 0.3
            else:
                tgt = max(lr * 0.9 + f['extra'], 95 + w)
            f['d'] += np.clip(tgt - f['d'], -55 / FPS, 160 / FPS)
            out.append(f['d'])
        return out

    def snap(self):
        w, h = self.size()
        st = dict(t=self.t, hp=self.hp, w=w, h=h, dead=self.dead_at, watch=self._watchers(),
                  threats=self.threats.copy(), allies=[(e['x'], e['y'], e['hp'], e['ph']) for e in self.allies])
        if self.skin is not None and hasattr(self.skin, 'snap'):
            st.update(self.skin.snap(self))
        return st

    def run(self):
        for i in range(int(round(self.c['total'] * FPS))):
            for _ in range(SUB):
                self.step()
            self.frames.append(self.snap() if self.visual else self.hp)
        return self


def score(c):
    """Resumo de uma semente, para escolher o drama: menor vida, quando, viradas e resultado."""
    s = Sim(c, visual=False).run()
    hp = np.array(s.frames)
    t = np.arange(len(hp)) / FPS
    run = hp[t < c['until']]
    return dict(seed=c['seed'], at_end=round(float(run[-1]), 1), low=round(float(run.min()), 1),
                low_at=round(float(t[np.argmin(run)]), 1), out=None if s.dead_at is None else round(s.dead_at, 1),
                feeds=sum(1 for e in s.events if e[1] == 'feed'), lost=sum(1 for e in s.events if e[1] == 'lost'),
                swings=int(np.sum(np.abs(np.diff(np.sign(run - 40))) > 0)), early=round(float(hp[t < 12].min()), 1))


def _score(a):
    c, seed = a
    return score(dict(c, seed=seed))


def search(tl, n=300, end='survive'):
    """Ranking de sementes. survive: escapa por pouco no fim. out: perde tarde, depois de lutar."""
    from multiprocessing import Pool
    c = config(tl)
    with Pool() as p:
        res = p.map(_score, [(c, i) for i in range(n)])
    until = c['until']
    if end == 'out':
        pool = [r for r in res if r['out'] and r['early'] > 30]
        key = lambda r: r['out'] + r['swings'] * 0.5 + r['feeds'] * 0.2
    else:
        pool = [r for r in res if not r['out'] and r['early'] > 30]
        key = lambda r: (r['low'] > 2) * 100 - r['low'] + r['swings'] * 2 + (r['low_at'] > until - 10) * 30
    print(f'{n} sementes: {sum(1 for r in res if r["out"])} perdem, {sum(1 for r in res if not r["out"])} sobrevivem')
    print(f'{"semente":>7} {"no fim":>7} {"menor":>6} {"aos":>5} {"perde":>6} {"chegam":>7} {"perdidos":>9} {"viradas":>8}')
    for r in sorted(pool, key=key, reverse=True)[:10]:
        print(f'{r["seed"]:>7} {r["at_end"]:>6}% {r["low"]:>5}% {r["low_at"]:>4}s {str(r["out"] or "-"):>6} '
              f'{r["feeds"]:>7} {r["lost"]:>9} {r["swings"]:>8}')


if __name__ == '__main__':
    import sys
    import project                      # noqa: F401  (põe a pasta do vídeo no caminho)
    import timeline
    search(timeline, int(sys.argv[1]) if len(sys.argv) > 1 else 300, sys.argv[2] if len(sys.argv) > 2 else 'survive')
