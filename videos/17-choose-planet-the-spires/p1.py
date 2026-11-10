"""THE AURORA: o céu brilha toda noite, a luz cantarola e todo mundo dorme. Ninguém acordou."""
from lib import *
from planets import *

SHOTS = {'p1a': 6.0, 'p1b': 3.75, 'p1c': 3.5, 'p1d': 4.0}
BAGS = ((0.42, 0.1, 0.07), (0.08, 0.16, 0.34), (0.36, 0.3, 0.08), (0.1, 0.24, 0.12), (0.3, 0.08, 0.2))


def build_p1a():
    def extra(p):
        aurora_shell(1.0).parent = p
    upd = orbit(planet_aurora, (0.3, 0.9, 0.7), (-1.0, -0.25, 0.25), extra=extra)
    return lambda t, u: upd(t, u, SHOTS['p1a'])


def frost(name, base, amount=0.55, scale=9.0):
    """cor base coberta de manchas de gelo"""
    m, nt = mat(name)
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=scale, Detail=8.0, Roughness=0.7); L(nt, tc, a.inputs['Vector'])
    k = ramp(nt, [(amount, (0, 0, 0)), (amount + 0.12, (1, 1, 1))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=0.4, Distance=0.004); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, mix(nt, k, base, (0.82, 0.88, 0.95)), 0.55, spec=0.6, normal=bp.outputs[0]).outputs[0])
    return m


def curtain_mat(z0, z1, phase):
    """cortina de aurora: raios verticais, verde embaixo e violeta em cima, que somam luz.
    O nó 'tclock' é o tempo, que faz os raios andarem."""
    m, nt = mat('curtain')
    vn = n(nt, 'ShaderNodeValue'); vn.name = 'tclock'
    val = vn.outputs[0]
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, pos, sp.inputs[0])
    h = math_(nt, 'DIVIDE', math_(nt, 'SUBTRACT', sp.outputs['Z'], z0), z1 - z0)
    fade = ramp(nt, [(0.0, (0, 0, 0)), (0.06, (1, 1, 1)), (0.35, (0.55, 0.55, 0.55)), (1.0, (0, 0, 0))], h).outputs[0]
    col = ramp(nt, [(0.05, (0.2, 1.0, 0.5)), (0.4, (0.15, 0.9, 0.6)), (0.85, (0.6, 0.2, 1.0))], h).outputs[0]
    cx = n(nt, 'ShaderNodeCombineXYZ')
    L(nt, math_(nt, 'ADD', math_(nt, 'MULTIPLY', sp.outputs['X'], 0.035), math_(nt, 'ADD', val, phase)), cx.inputs['X'])
    L(nt, math_(nt, 'MULTIPLY', val, 0.3), cx.inputs['Y'])
    rays = n(nt, 'ShaderNodeTexNoise', Scale=6.0, Detail=6.0, Roughness=0.65); L(nt, cx.outputs[0], rays.inputs['Vector'])
    r = ramp(nt, [(0.35, (0.05, 0.05, 0.05)), (0.7, (1, 1, 1))], rays.outputs['Fac']).outputs[0]
    bw1 = n(nt, 'ShaderNodeRGBToBW'); L(nt, fade, bw1.inputs[0])
    bw2 = n(nt, 'ShaderNodeRGBToBW'); L(nt, r, bw2.inputs[0])
    e = n(nt, 'ShaderNodeEmission'); L(nt, col, e.inputs['Color'])
    L(nt, math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', bw1.outputs[0], bw2.outputs[0]), 2.6), e.inputs['Strength'])
    add = n(nt, 'ShaderNodeAddShader')
    L(nt, n(nt, 'ShaderNodeBsdfTransparent').outputs[0], add.inputs[0]); L(nt, e.outputs[0], add.inputs[1])
    out(nt, add.outputs[0])
    return m


def curtain(y0, z0, z1, phase, amp=30.0):
    xs = np.linspace(-320, 320, 260)
    ys = y0 + amp * np.sin(xs * 0.011 + phase) + 0.4 * amp * np.sin(xs * 0.031 + 2 * phase)
    v = np.concatenate([np.stack([xs, ys, np.full_like(xs, z0)], 1), np.stack([xs, ys, np.full_like(xs, z1)], 1)])
    k = np.arange(len(xs) - 1); N = len(xs)
    t = np.concatenate([np.stack([k, k + 1, k + N + 1], 1), np.stack([k, k + N + 1, k + N], 1)])
    return fast_mesh('curtain', v, t, curtain_mat(z0, z1, phase))


def valley():
    """Vale de neve à noite, lago parado no meio e cortinas de aurora. Devolve o relógio da aurora."""
    reset(18)
    world_space((0.01, 0.03, 0.04), 0.7)
    def hfun(X, Y):
        base = 0.45 * fbm(X * 0.05, Y * 0.05, 4)
        walls = np.clip((np.abs(X) - 28) / 60, 0, None) ** 1.4 * 55 * (0.6 + 0.8 * fbm(X * 0.02, Y * 0.02, 4))
        far = np.clip((Y - 170) / 90, 0, None) * 45 * (0.5 + fbm(X * 0.015, 3.0, 3))
        return base + walls + far
    grid_mesh('snow', 520, 220, hfun, frost('snowm', (0.3, 0.35, 0.45), 0.45, 0.6), center=(0, 170))
    box('lake', (46, 70, 0.02), (0, 70, 0.5), simple('lakem', (0.004, 0.008, 0.012), 0.03))
    vals = []
    for y0, z0, z1, ph in ((210, 26, 110, 0.0), (260, 34, 140, 1.7), (170, 22, 80, 3.1)):
        c = curtain(y0, z0, z1, ph)
        vals.append(c.data.materials[0].node_tree.nodes['tclock'])
    sun(0.16, (0.2, 0.6, 1.0), (0.55, 0.95, 0.8))
    sun(0.07, (-0.4, 0.3, 1.0), (0.75, 0.55, 1.0))
    def tick(t):
        for v in vals:
            v.outputs[0].default_value = 0.25 * t
    return tick


def build_p1b():
    tick = valley()
    cam = camera((0, -14, 3.5), (0, 100, 15), 30)
    def update(t, u):
        tick(t)
        cam.location = (0.3 * u, -14 + 0.6 * t, 3.5)
        look(cam, (0, 100, 14 + 14 * ease(u)))       # sobe do lago para o céu
    return update


def bag(loc, color, face=False):
    """saco de dormir deitado ao longo de X, com a abertura do capuz em -X"""
    root = bpy.data.objects.new('bag', None); link(root); root.location = loc
    m = frost('bagm', color, 0.5, 6.0)
    b = sphere('bagbody', 1.0, (0.3, 0, 0.2), m, 48, 24); b.scale = (0.95, 0.38, 0.2); b.parent = root
    hood = sphere('hood', 1.0, (-0.9, 0, 0.2), m, 48, 24); hood.scale = (0.15, 0.25, 0.15); hood.parent = root    # capuz atrás da cabeça
    sk = frost('face', (0.58, 0.63, 0.68), 0.5, 22.0)
    hd = sphere('head', 0.1, (-0.72, 0, 0.27), sk, 48, 32); hd.scale = (1.15, 0.8, 0.95); hd.parent = root
    if face:
        dark = simple('lid', (0.16, 0.18, 0.24), 0.6)
        for s_ in (-1, 1):                                  # pálpebras fechadas, fundas
            e = ico('lid', 0.016, (-0.745, s_ * 0.034, 0.352), dark, 3); e.scale = (0.5, 1.2, 0.3); e.parent = root
        e = ico('nose', 0.016, (-0.71, 0, 0.365), sk, 3); e.scale = (1.4, 0.75, 0.8); e.parent = root
        e = box('lips', (0.008, 0.04, 0.004), (-0.66, 0, 0.352), simple('lipm', (0.2, 0.24, 0.32), 0.5)); e.parent = root
        for k in range(7):                                  # cristais de gelo nos cílios e no capuz
            a = k * 0.9
            e = ico('ice', 0.008, (-0.72 + 0.17 * math.cos(a), 0.17 * math.sin(a), 0.33), simple('icem', (0.9, 0.95, 1.0), 0.1), 1)
            e.parent = root
    return root


def build_p1c():
    tick = valley()
    for k in range(9):
        bag((4.0, 6 + k * 1.15, 0.45), BAGS[k % len(BAGS)])
    cam = camera((1.4, 2.5, 1.3), (4.0, 12, 1.0), 30)
    def update(t, u):
        tick(t)
        cam.location = (1.4 + 0.3 * u, 2.5 + 0.8 * ease(u), 1.3)
        look(cam, (4.0, 12, 1.3))
    return update


def build_p1d():
    tick = valley()
    bag((0, 0, 0.45), BAGS[1], face=True)
    for k in (1, 2):
        bag((0, k * 1.15, 0.45), BAGS[(k + 2) % len(BAGS)])
    point((-0.4, -0.6, 2.2), 25.0, (0.4, 1.0, 0.7), 0.8)
    point((-1.2, 0.5, 2.0), 12.0, (0.7, 0.4, 1.0), 0.8)
    cam = camera((-0.1, -1.1, 1.65), (-0.72, 0, 0.75), 35)
    def update(t, u):
        tick(t)
        cam.location = vlerp((-0.1, -1.1, 1.65), (-0.45, -0.6, 1.25), ease(u))
        look(cam, (-0.72, 0, 0.76))
    return update
