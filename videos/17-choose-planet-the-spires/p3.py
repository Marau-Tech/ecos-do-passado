"""THE WELL: planície seca e um poço de pedra. A pedra nunca bate no fundo. Alguma coisa joga de volta."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'p3a': 6.0, 'p3b': 3.75, 'p3c': 3.5, 'p3d': 4.0}


def build_p3a():
    upd = orbit(planet_well, (0.9, 0.7, 0.45), (-1.0, -0.25, 0.3))
    return lambda t, u: upd(t, u, SHOTS['p3a'])


def stone_mat():
    """pedra do poço; por dentro escurece com a profundidade até o preto"""
    m, nt = mat('stone')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    mp = n(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 1.0, 1.8); L(nt, tc, mp.inputs['Vector'])
    v = n(nt, 'ShaderNodeTexVoronoi', Scale=6.0); L(nt, mp.outputs[0], v.inputs['Vector'])
    e = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=6.0); L(nt, mp.outputs[0], e.inputs['Vector'])
    bw = n(nt, 'ShaderNodeRGBToBW'); L(nt, v.outputs['Color'], bw.inputs[0])
    c = ramp(nt, [(0.0, (0.36, 0.32, 0.27)), (1.0, (0.55, 0.5, 0.42))], bw.outputs[0]).outputs[0]
    mortar = math_(nt, 'LESS_THAN', e.outputs['Distance'], 0.06)
    col = mix(nt, mortar, c, (0.12, 0.1, 0.08))
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc, sp.inputs[0])
    deep = ramp(nt, [(0.0, (0, 0, 0)), (1.0, (1, 1, 1))], math_(nt, 'DIVIDE', math_(nt, 'ADD', sp.outputs['Z'], 2.2), 2.6, clamp=True)).outputs[0]
    col = mix(nt, 1.0, col, deep, 'MULTIPLY')
    bp = n(nt, 'ShaderNodeBump', Strength=0.8, Distance=0.05); L(nt, e.outputs['Distance'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.9, spec=0.2, normal=bp.outputs[0]).outputs[0])
    return m


def plain():
    """Terra rachada até o horizonte, céu pálido de calor, sol duro, e o poço com a armação de madeira no meio."""
    reset(16)
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    g = ramp(nt, [(0.0, (0.9, 0.82, 0.66)), (0.25, (0.72, 0.7, 0.66)), (1.0, (0.5, 0.58, 0.68))], sp.outputs['Z']).outputs[0]
    b = n(nt, 'ShaderNodeBackground', Strength=1.0); L(nt, g, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])
    m, nt = mat('earth')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.2, Detail=6.0); L(nt, pos, a.inputs['Vector'])
    base = ramp(nt, [(0.4, (0.42, 0.32, 0.2)), (0.6, (0.55, 0.43, 0.29))], a.outputs['Fac']).outputs[0]
    v = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=0.9); L(nt, pos, v.inputs['Vector'])
    crack = math_(nt, 'LESS_THAN', v.outputs['Distance'], 0.035)
    bp = n(nt, 'ShaderNodeBump', Strength=0.6, Distance=0.03); L(nt, crack, bp.inputs['Height']); bp.invert = True
    out(nt, principled(nt, mix(nt, crack, base, (0.12, 0.08, 0.05)), 0.95, spec=0.1, normal=bp.outputs[0]).outputs[0])
    # o chão tem um furo do tamanho do poço: dois anéis de caixas não fecham um círculo, então o chão é uma malha
    R = 0.8; k = 48; a_ = np.arange(k) * 2 * np.pi / k
    inner = np.stack([R * np.cos(a_), R * np.sin(a_), np.zeros(k)], 1)
    outer = np.stack([3000 * np.cos(a_), 3000 * np.sin(a_), np.zeros(k)], 1)
    i = np.arange(k); j = (i + 1) % k
    tris = np.concatenate([np.stack([i, j, j + k], 1), np.stack([i, j + k, i + k], 1)])
    fast_mesh('ground', np.vstack([inner, outer]), tris, m)
    v, t = lathe([(0.78, -40.0), (0.78, 0.85), (1.05, 0.85), (1.05, -0.1)], 28)
    fast_mesh('well', v, t[:-28], stone_mat())             # sem a tampa de cima: o buraco fica aberto
    wood = simple('wood', (0.25, 0.17, 0.1), 0.9)
    for x in (-1.25, 1.25):
        box('postw', (0.14, 0.14, 2.3), (x, 0, 1.15), wood)
    box('beam', (2.7, 0.14, 0.14), (0, 0, 2.25), wood)
    tube('rope', [(0, 0, 2.2), (0, 0.01, 0.5), (0.01, 0, -6), (0, 0, -18)], [0.018] * 4, simple('ropem', (0.4, 0.33, 0.2), 0.95))
    sun(4.0, (-0.45, -0.55, 0.75), (1.0, 0.94, 0.82), 1.0)


def build_p3b():
    plain()
    cam = camera((-2.2, -11, 1.7), (0, 0, 0.9), 32)
    def update(t, u):
        cam.location = (-2.2 + 0.4 * u, -11 + 1.6 * ease(u), 1.7)
        look(cam, (0, 0, 0.9))
    return update


def build_p3c():
    plain()
    cam = camera((0.35, -1.05, 2.5), (0, 0, -3), 30)
    def update(t, u):
        cam.location = vlerp((0.35, -1.05, 2.5), (0.2, -0.55, 1.85), ease(u))     # inclina por cima da borda
        look(cam, (0.02, 0.05, -3))
    return update


def hand():
    """mão pálida de dedos compridos, com a palma para cima, no fundo do poço"""
    root = bpy.data.objects.new('hand', None); link(root)
    sk = skin_mat()
    parts = [ico('palm', 0.1, (0, 0, 0), sk, 3), tube('arm', [(0, 0, -0.05), (0.02, 0.03, -0.6), (0.0, 0.05, -1.6)], [0.07, 0.065, 0.06], sk)]
    parts[0].scale = (1.0, 0.45, 1.15)
    for k, (dx, ln) in enumerate(((-0.075, 0.2), (-0.03, 0.27), (0.015, 0.29), (0.06, 0.25))):
        parts.append(tube('finger', [(dx, 0, 0.08), (dx * 1.1, -0.03, 0.08 + ln * 0.5), (dx * 1.2, -0.09, 0.08 + ln)],
                          [0.018, 0.015, 0.01], sk))
    parts.append(tube('thumb', [(0.08, 0, 0.0), (0.16, -0.03, 0.08), (0.2, -0.07, 0.15)], [0.02, 0.016, 0.011], sk))
    for o in parts:
        o.parent = root
    return root


def build_p3d():
    plain()
    hd = hand(); hd.location = (0.05, 0.05, -2.6); hd.scale = (2.6, 2.6, 2.6); hd.rotation_euler = (0.9, 0.0, 0.4)     # de lado, para os dedos aparecerem
    lamp = point((0.1, -0.2, -1.4), 0.0, (0.8, 0.86, 0.9), 0.3)
    stone = ico('rock', 0.14, (0, 0, -3), simple('rockm', (0.2, 0.18, 0.16), 0.9), 1)
    cam = camera((0.2, -0.55, 1.85), (0.02, 0.05, -3), 30)
    def update(t, u):
        s = t - TL.STONE_AT
        if s < 0:
            cam.location = vlerp((0.2, -0.55, 1.85), (0.12, -0.38, 1.6), ease(t / TL.STONE_AT))
        else:
            k = ease(min(1.0, s / 0.5))                   # você pula para trás
            cam.location = vlerp((0.12, -0.38, 1.6), (0.2, -0.6, 1.95), k) + shake(t, 0.05 * (1 - 0.5 * k), 14)
        look(cam, (0.02, 0.05, -3))
        on = s >= 0
        for o in [hd] + list(hd.children_recursive):
            o.hide_render = not on
        lamp.data.energy = 6.0 if on else 0.0
        q = min(1.0, max(0.0, s / 0.33))                  # a pedra sobe até a lente
        stone.hide_render = not (0 <= s < 0.33)
        stone.location = vlerp((0.05, 0.05, -1.9), (0.13, -0.33, 1.45), q * q)
    return update
