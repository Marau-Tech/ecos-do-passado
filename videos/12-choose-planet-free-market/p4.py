"""THE MARKET: um supermercado do tamanho do planeta. Tudo de graça. Quando as luzes piscarem, não se mexa."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'p4a': 6.25, 'p4b': 3.5, 'p4c': 3.75, 'p4d': 3.75}
HOLD_STATES = True              # p4c e p4d têm câmera parada: só renderiza quando a luz ou a figura mudam
FIG_AT = {'p4c': (None, 60.0, 45.0), 'p4d': (40.0, 28.0, 16.0)}   # distância da figura depois de cada piscada


def build_p4a():
    upd = orbit(planet_market, (0.9, 0.85, 0.6), (-1.0, -0.25, 0.3))
    return lambda t, u: upd(t, u, SHOTS['p4a'])


def aisle():
    """Corredor com prateleiras cheias dos dois lados, frutas na entrada e tubos fluorescentes.
    Devolve o controle da luz (valor da emissão e as lâmpadas)."""
    reset(18)
    world_flat((0, 0, 0), 0.0)
    box('floor', (14, 400, 0.1), (0, 190, -0.05), simple('tile', (0.75, 0.75, 0.72), 0.15))
    box('ceil', (14, 400, 0.1), (0, 190, 4.6), simple('ceilm', (0.55, 0.55, 0.53), 0.9))
    lm, nt = mat('tube')
    val = n(nt, 'ShaderNodeValue'); val.outputs[0].default_value = 1.0
    e = n(nt, 'ShaderNodeEmission'); e.inputs['Color'].default_value = (0.92, 1.0, 0.95, 1)
    L(nt, math_(nt, 'MULTIPLY', val.outputs[0], 6.0), e.inputs['Strength']); out(nt, e.outputs[0])
    v, t = cube_vt(0.18, 2.4, 0.06)
    scatter('tubes', v, t, [(x, y, 4.45) for x in (-1.2, 1.2) for y in range(-2, 380, 4)], m=lm)
    lamps = [point((0, y, 4.2), 120.0, (0.92, 1.0, 0.95), 1.0) for y in range(0, 120, 10)]
    shelf = simple('shelf', (0.85, 0.85, 0.82), 0.5, metal=0.3)
    for side in (-1, 1):
        box('back', (0.6, 380, 2.4), (side * 3.4, 190, 1.2), shelf)
        v, t = cube_vt(0.7, 380, 0.04)
        scatter('boards', v, t, [(side * 3.05, 190, z) for z in (0.3, 0.8, 1.3, 1.8)], m=shelf)
    rs = np.random.RandomState(5)
    cols = ((0.9, 0.2, 0.2), (0.95, 0.6, 0.1), (0.2, 0.5, 0.9), (0.95, 0.9, 0.3), (0.3, 0.75, 0.35), (0.95, 0.95, 0.95))
    v, t = cube_vt(0.22, 0.16, 0.3)
    groups = [[] for _ in cols]
    for side in (-1, 1):
        for z in (0.34, 0.84, 1.34, 1.84):
            for y in np.arange(4, 200, 0.24):
                groups[rs.randint(len(cols))].append((side * 2.9, y, z))
    for i, (c, g) in enumerate(zip(cols, groups)):
        scatter(f'prod{i}', v, t, g, m=simple(f'pm{i}', c, 0.35))
    fv, ft = lathe([(0.0, 0.0), (0.08, 0.02), (0.1, 0.08), (0.07, 0.15), (0.0, 0.16)], 10)
    for i, c in enumerate(((0.85, 0.1, 0.1), (1.0, 0.55, 0.05), (0.35, 0.75, 0.1), (0.95, 0.85, 0.2))):
        pos = [(sx * 1.6 + rs.uniform(-0.45, 0.45), rs.uniform(0.5, 2.5), 0.85 + rs.uniform(0, 0.12)) for sx in (-1, 1) for _ in range(40)]
        scatter(f'fruit{i}', fv, ft, pos, m=simple(f'fm{i}', c, 0.4), smooth=True)
    for sx in (-1, 1):
        box('stand', (1.1, 2.2, 0.85), (sx * 1.6, 1.5, 0.42), simple('wood', (0.45, 0.3, 0.18), 0.7))
    fog((0.6, 0.62, 0.6), 10.0, 160.0, 0.7)
    return val, lamps


def lights(val, lamps, on):
    val.outputs[0].default_value = 1.0 if on else 0.04
    for l in lamps:
        l.data.energy = 120.0 if on else 2.0


def build_p4b():
    val, lamps = aisle()
    cam = camera((0.6, -3, 1.6), (0.3, 40, 1.4), 32)
    def update(t, u):
        y = -3 + 1.6 * t
        cam.location = (0.6, y, 1.6 + 0.015 * math.sin(t * 5))
        look(cam, (0.3, y + 40, 1.4))
    return update


def flicker_scene(shot):
    val, lamps = aisle()
    fig = pale_figure((0, 60, 0))
    fig.scale = (1.15, 1.15, 1.15)
    cam = camera((0.2, 4, 1.6), (0, 60, 1.5), 34)
    times, dists = TL.FLICKERS[shot], FIG_AT[shot]
    def update(t, u):
        k = sum(t >= x for x in times)                 # quantas piscadas já passaram
        dark = any(x <= t < x + 0.25 for x in times) or (shot == 'p4d' and t >= TL.BLACKOUT)
        lights(val, lamps, not dark)
        d = dists[min(k, len(dists) - 1)]
        for o in [fig] + list(fig.children_recursive):
            o.hide_render = d is None
        if d is not None:
            fig.location = (0.1, 4 + d, 0)
        return (k, dark)
    return update


def build_p4c():
    return flicker_scene('p4c')


def build_p4d():
    return flicker_scene('p4d')
