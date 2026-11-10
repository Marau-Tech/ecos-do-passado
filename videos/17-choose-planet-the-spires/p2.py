"""THE FIELD: milho de polo a polo, um espantalho a cada cem passos, todos virados para a trilha. Conte de novo."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'p2a': 6.0, 'p2b': 3.75, 'p2c': 3.5, 'p2d': 4.0}
POSTS = [(-2.3 if k % 2 else 2.3, 14 + k * 11) for k in range(14)]     # espantalhos dos dois lados da trilha
EXTRA = (0.0, 19.0)             # o espantalho a mais, no meio da trilha


def build_p2a():
    upd = orbit(planet_field, (0.9, 0.8, 0.5), (-1.0, -0.25, 0.3))
    return lambda t, u: upd(t, u, SHOTS['p2a'])


def stalk_vt():
    """pé de milho: duas faixas cruzadas que afinam e quatro folhas para fora"""
    v, t = [], []
    def quad(a, b, c, d):
        i = len(v); v.extend([a, b, c, d]); t.extend([(i, i + 1, i + 2), (i, i + 2, i + 3)])
    w = 0.035
    quad((-w, 0, 0), (w, 0, 0), (w * 0.4, 0, 2.5), (-w * 0.4, 0, 2.5))
    quad((0, -w, 0), (0, w, 0), (0, w * 0.4, 2.5), (0, -w * 0.4, 2.5))
    for k, (z, a) in enumerate(((0.5, 0.3), (0.8, 2.4), (1.1, 4.4), (1.4, 0.9), (1.7, 3.3), (2.0, 5.4))):
        ca, sa = math.cos(a), math.sin(a); px, py = -sa * 0.05, ca * 0.05     # folha larga que sobe e cai na ponta
        quad((px, py, z), (-px, -py, z), (0.4 * ca - px * 1.4, 0.4 * sa - py * 1.4, z + 0.35), (0.4 * ca + px * 1.4, 0.4 * sa + py * 1.4, z + 0.35))
        quad((0.4 * ca + px * 1.4, 0.4 * sa + py * 1.4, z + 0.35), (0.4 * ca - px * 1.4, 0.4 * sa - py * 1.4, z + 0.35),
             (0.8 * ca, 0.8 * sa, z + 0.15), (0.8 * ca, 0.8 * sa, z + 0.15))
    return v, t


def corn_mat():
    m, nt = mat('corn')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.6, Detail=5.0); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.36, 0.3, 0.1)), (0.55, (0.52, 0.44, 0.18)), (0.72, (0.4, 0.38, 0.14))], a.outputs['Fac']).outputs[0]
    d = n(nt, 'ShaderNodeBsdfDiffuse'); L(nt, c, d.inputs['Color'])
    tr = n(nt, 'ShaderNodeBsdfTranslucent'); L(nt, c, tr.inputs['Color'])
    ms = n(nt, 'ShaderNodeMixShader', Fac=0.35)
    L(nt, d.outputs[0], ms.inputs[1]); L(nt, tr.outputs[0], ms.inputs[2])
    out(nt, ms.outputs[0])
    return m


def burlap(name, color):
    m, nt = mat(name)
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    w = n(nt, 'ShaderNodeTexWave', {'wave_type': 'BANDS'}, Scale=60.0, Distortion=2.0); L(nt, tc, w.inputs['Vector'])
    a = n(nt, 'ShaderNodeTexNoise', Scale=12.0, Detail=6.0); L(nt, tc, a.inputs['Vector'])
    k = mix(nt, 0.5, w.outputs['Fac'], a.outputs['Fac'])
    c = mix(nt, k, color, tuple(x * 0.6 for x in color))
    bp = n(nt, 'ShaderNodeBump', Strength=0.6, Distance=0.01); L(nt, k, bp.inputs['Height'])
    out(nt, principled(nt, c, 0.95, spec=0.1, normal=bp.outputs[0]).outputs[0])
    return m


def scarecrow(loc, yaw):
    """estaca, travessa, camisa de saco, cabeça de saco com olhos costurados e chapéu; o rosto olha para -Y"""
    root = bpy.data.objects.new('scarecrow', None); link(root)
    root.location = loc; root.rotation_euler.z = yaw
    wood = simple('wood', (0.22, 0.16, 0.1), 0.9)
    sack = burlap('sack', (0.55, 0.45, 0.3))
    shirt = burlap('shirt', (0.3, 0.26, 0.22))
    stitch = simple('stitch', (0.02, 0.015, 0.01), 0.9)
    parts = [box('post', (0.09, 0.09, 2.7), (0, 0.05, 1.35), wood),
             box('bar', (1.7, 0.07, 0.07), (0, 0.05, 1.95), wood)]
    v, t = lathe([(0.0, 1.05), (0.24, 1.1), (0.27, 1.5), (0.3, 1.9), (0.12, 2.0), (0.0, 2.02)], 10)
    parts.append(fast_mesh('torso', v, t, shirt, True))
    for s_ in (-1, 1):
        parts.append(tube('sleeve', [(s_ * 0.2, 0, 1.95), (s_ * 0.5, 0, 1.94), (s_ * 0.8, 0, 1.9)], [0.1, 0.09, 0.08], shirt))
        parts.append(tube('straw', [(s_ * 0.82, 0, 1.9), (s_ * 0.88, 0, 1.78), (s_ * 0.9, -0.02, 1.68)], [0.05, 0.03, 0.005],
                          simple('strawm', (0.6, 0.5, 0.22), 0.9)))
    hd = sphere('head', 0.17, (0, 0, 2.2), sack, 32, 24); hd.scale = (0.95, 0.9, 1.1); parts.append(hd)
    for s_ in (-1, 1):                                    # olhos de X costurados
        for r in (0.6, -0.6):
            parts.append(box('st', (0.07, 0.012, 0.012), (s_ * 0.06, -0.152, 2.24), stitch, rot=(0, r, 0)))
    parts.append(box('mouth', (0.14, 0.012, 0.01), (0, -0.155, 2.12), stitch))
    v, t = lathe([(0.0, 2.3), (0.36, 2.3), (0.36, 2.32), (0.15, 2.34), (0.13, 2.52), (0.0, 2.55)], 16)
    parts.append(fast_mesh('hat', v, t, simple('hatm', (0.16, 0.13, 0.1), 0.95), True))
    for o in parts:
        o.parent = root
    return root


def field(posts=POSTS):
    """Trilha de terra entre paredes de milho, céu nublado amarelado e os espantalhos virados para a trilha."""
    reset(18)
    world_flat((0.55, 0.52, 0.42), 1.0)
    box('path', (3.4, 400, 0.1), (0, 180, -0.05), simple('dirt', (0.26, 0.2, 0.13), 0.95))
    box('soil', (400, 400, 0.1), (0, 180, -0.07), simple('soilm', (0.16, 0.13, 0.08), 0.95))
    rs = np.random.RandomState(3)
    pos, yaw, sc = [], [], []
    for side in (-1, 1):
        x = side * (1.9 + 40 * rs.rand(26000) ** 1.6)
        y = -20 + 240 * rs.rand(26000)
        pos += [(a, b, 0) for a, b in zip(x, y)]
        yaw += list(rs.rand(26000) * 6.28)
        sc += list(0.85 + 0.35 * rs.rand(26000))
    P = np.array(pos); keep = np.ones(len(P), bool)
    for x, y in posts + [EXTRA]:                          # abre espaço em volta de cada estaca
        keep &= (P[:, 0] - x) ** 2 + (P[:, 1] - y) ** 2 > 0.8 ** 2
    pos = P[keep]; yaw = np.array(yaw)[keep]; sc = np.array(sc)[keep]
    v, t = stalk_vt()
    scatter('corn', v, t, pos, yaw, sc, corn_mat(), smooth=False)
    for x, y in posts:
        scarecrow((x, y, 0), -math.pi / 2 if x > 0 else math.pi / 2)    # o rosto vira para a trilha
    sun(1.2, (0.3, -0.4, 1.0), (1.0, 0.95, 0.82), 25.0)
    fog((0.5, 0.48, 0.38), 10.0, 120.0, 0.85)


def build_p2b():
    field([(1.4, 62.0)])
    cam = camera((0.2, 0, 1.7), (0.6, 60, 1.9), 34)
    def update(t, u):
        cam.location = (0.2, 0.5 * t, 1.7 + 0.02 * math.sin(t * 5))
        look(cam, (0.7, 60, 1.9))
    return update


def build_p2c():
    field()
    cam = camera((0, 0, 1.7), (0, 40, 1.8), 30)
    def update(t, u):
        y = 1.3 * t
        cam.location = (0.15 * math.sin(t * 1.6), y, 1.7 + 0.04 * abs(math.sin(t * 4.5)))
        look(cam, (0, y + 40, 1.8))
    return update


def build_p2d():
    field()
    extra = scarecrow((*EXTRA, 0), 0.0)                   # no meio da trilha, olhando para você
    cam = camera((0, 4.55, 1.7), (0, 44, 1.8), 30)
    def update(t, u):
        k = ease(min(1.0, t / 1.6))                       # para de andar
        cam.location = (0, 4.55 + 0.9 * k, 1.7 + 0.04 * abs(math.sin(min(t, 1.6) * 4.5)) * (1 - k))
        look(cam, (0, 44, 1.85))
        for o in [extra] + list(extra.children_recursive):
            o.hide_render = t < TL.EXTRA_AT
    return update
