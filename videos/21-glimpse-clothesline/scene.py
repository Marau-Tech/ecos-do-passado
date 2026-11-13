"""Quintal à noite, filmado de dentro da cozinha pela janela. Três lençóis no varal; o holofote de movimento
acende, o vento sacode os dois dos lados e o do meio fica reto, com dois pés descalços embaixo da barra."""
from lib import *
from nature import grass, tree
import timeline as TL

SHOTS = {'a': 12.0}
HOLD_STATES = True

LINE_Z = 2.02                   # altura da corda do varal
SHEET_W, SHEET_H = 1.75, 1.57   # a barra fica a 45 cm do chão
SHEET_Y = 6.0
NX, NZ = 36, 30


def night_sky():
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    col = ramp(nt, [(0.0, (0.05, 0.06, 0.1)), (0.15, (0.03, 0.04, 0.08)), (0.6, (0.01, 0.012, 0.03))], sp.outputs['Z']).outputs[0]
    b = n(nt, 'ShaderNodeBackground', Strength=1.0); L(nt, col, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])


def sheet_grid(cx):
    xs = np.linspace(-SHEET_W / 2, SHEET_W / 2, NX)
    zs = np.linspace(0, -SHEET_H, NZ)
    X, Z = np.meshgrid(xs, zs)
    i = np.arange(NX - 1); j = np.arange(NZ - 1)
    a = (j[:, None] * NX + i[None, :]).ravel()
    tris = np.concatenate([np.stack([a, a + 1, a + NX + 1], 1), np.stack([a, a + NX + 1, a + NX], 1)])
    return X, Z, tris


def sheet_pose(X, Z, t, side):
    """deslocamento do lençol em y (para longe e para perto da câmera); a barra mexe mais que o topo"""
    g = TL.gust(t)
    amp = (-Z / SHEET_H) ** 1.3
    ph = side * 1.3
    w = (0.32 * math.sin(2 * math.pi * t / 2.4 + ph) * np.ones_like(X)
         + 0.16 * np.sin(2 * math.pi * t / (12 / 7) + X * 3.1 + Z * 1.6 + ph)
         + 0.08 * np.sin(2 * math.pi * t / 1.5 + X * 5.3 - Z * 2.2 + ph))
    folds = 0.06 * np.sin(X * 11.0 + side) * (0.4 + 0.6 * amp)            # vincos de pano pendurado
    y = folds + amp * g * w * 1.6
    x = X + amp * g * 0.05 * np.sin(2 * math.pi * t / 3.0 + ph)
    z = Z + amp * g * 0.06 * np.abs(np.sin(2 * math.pi * t / 2.4 + ph))   # a barra sobe quando o lençol infla
    return np.stack([x, y, z], -1).reshape(-1, 3).astype(np.float32)


def feet(m):
    parts = []
    for s_ in (-1, 1):
        x = s_ * 0.11
        f = ico('foot', 1.0, (x, SHEET_Y - 0.03, 0.04), m, 3); f.scale = (0.052, 0.13, 0.04)
        f.rotation_euler.z = math.radians(-6 * s_)
        parts.append(f)
        for k, dx in enumerate((-0.03, -0.015, 0.0, 0.015, 0.03)):                 # dedos
            r = 0.014 if k else 0.017
            parts.append(ico('toe', r, (x + dx, SHEET_Y - 0.155, 0.02), m, 2))
        parts.append(tube('shin', [(x, SHEET_Y + 0.04, 0.05), (x, SHEET_Y + 0.05, 0.13), (x, SHEET_Y + 0.07, 0.32),
                                   (x, SHEET_Y + 0.08, 0.8)], [0.042, 0.032, 0.048, 0.055], m))
    return parts


def build_a():
    reset(48)
    night_sky()
    # ---- cozinha: parede escura com a janela, peitoril e uma caneca ----
    wall = simple('wall', (0.3, 0.29, 0.27), 0.9)
    x0, x1, z0, z1 = -0.04, 1.86, 1.08, 2.36
    box('wallL', (3.0, 0.12, 3.0), (x0 - 1.5, 0, 1.5), wall); box('wallR', (3.0, 0.12, 3.0), (x1 + 1.5, 0, 1.5), wall)
    box('wallD', (x1 - x0, 0.12, z0), ((x0 + x1) / 2, 0, z0 / 2), wall); box('wallU', (x1 - x0, 0.12, 0.7), ((x0 + x1) / 2, 0, z1 + 0.35), wall)
    trim = simple('trim', (0.55, 0.5, 0.42), 0.6)
    box('sill', (2.1, 0.3, 0.04), (0.96, -0.12, z0 - 0.02), trim)
    box('frameL', (0.05, 0.08, z1 - z0), (x0 + 0.025, -0.02, (z0 + z1) / 2), trim)
    box('frameB', (x1 - x0, 0.08, 0.05), ((x0 + x1) / 2, -0.02, z0 + 0.025), trim)
    v, t_ = lathe([(0.0, 0.0), (0.034, 0.0), (0.036, 0.085), (0.0, 0.085)], 16)
    mug = fast_mesh('mug', v, t_, simple('mug', (0.5, 0.18, 0.12), 0.5), True); mug.location = (0.07, -0.13, z0)
    gm, gnt = mat('glass')
    tr = n(gnt, 'ShaderNodeBsdfTransparent'); gl = n(gnt, 'ShaderNodeBsdfGlossy', Roughness=0.05)
    ms = n(gnt, 'ShaderNodeMixShader', Fac=0.1); L(gnt, tr.outputs[0], ms.inputs[1]); L(gnt, gl.outputs[0], ms.inputs[2])
    out(gnt, ms.outputs[0])
    box('glass', (x1 - x0, 0.005, z1 - z0), ((x0 + x1) / 2, 0.02, (z0 + z1) / 2), gm)
    box('clock', (0.12, 0.02, 0.04), (1.2, -2.3, 0.5), emission('clockled', (0.2, 1.0, 0.4), 0.9))   # relógio do micro-ondas, só no reflexo
    # ---- quintal ----
    box('lawn', (60, 60, 0.1), (0, 20, -0.05), simple('lawn', (0.03, 0.07, 0.02), 0.95))
    grass(0.4, 0.3, math.pi / 2, 12, 60000, lambda x, y: 0 * x, seed=3, blade=0.016, spread=1.5,
          colors=((0.03, 0.08, 0.02), (0.06, 0.13, 0.03), (0.1, 0.17, 0.04)))
    wood = simple('post', (0.42, 0.4, 0.38), 0.8)
    for x in (-3.0, 3.0):
        box('post', (0.08, 0.08, 2.15), (x, SHEET_Y, 1.075), wood)
        box('arm', (0.06, 0.6, 0.06), (x, SHEET_Y, 2.1), wood)
    tube('line', [(-3.0, SHEET_Y, LINE_Z + 0.05), (0, SHEET_Y, LINE_Z - 0.02), (3.0, SHEET_Y, LINE_Z + 0.05)], [0.006] * 3,
         simple('rope', (0.6, 0.6, 0.58), 0.7), kind='POLY')
    cloth = simple('cloth', (0.86, 0.86, 0.83), 0.92)
    sheets = []
    for k, cx in enumerate((-1.95, 0.0, 1.95)):
        X, Z, tris = sheet_grid(cx)
        side = (-1, 0, 1)[k]
        v0 = sheet_pose(X, Z, 0.0, side) if side else np.stack([X, np.zeros_like(X), Z], -1).reshape(-1, 3).astype(np.float32)
        o = fast_mesh('sheet', v0, tris, cloth, True)
        o.location = (cx, SHEET_Y, LINE_Z)
        sheets.append((o, X, Z, side))
        for px in (-0.75, 0.0, 0.75):
            box('pin', (0.025, 0.03, 0.08), (cx + px, SHEET_Y - 0.015, LINE_Z - 0.01), simple('pinm', (0.5, 0.4, 0.3), 0.7))
    foot_parts = feet(simple('skin', (0.48, 0.38, 0.33), 0.6))
    # cerca de tábuas e árvores escuras atrás
    fence = simple('fence', (0.3, 0.24, 0.18), 0.9)
    for x in np.arange(-14, 14.1, 0.16):
        box('board', (0.14, 0.03, 1.7), (x, 11.0, 0.85), fence)
    box('rail', (28, 0.06, 0.1), (0, 10.95, 1.3), fence)
    for i, (x, y, s) in enumerate([(-11, 22, 1.4), (-4, 24, 1.6), (3, 22.5, 1.5), (10, 23, 1.7), (16, 25, 1.5)]):
        tree((x, y, 0), s, seed=i + 11)
    # lua fraca vinda de trás da casa e o holofote acima da janela
    sun(0.12, (0.25, -1.0, 0.9), (0.55, 0.65, 1.0), 2.0)
    fl = bpy.data.lights.new('flood', 'SPOT'); fl.color = (1.0, 0.86, 0.62); fl.shadow_soft_size = 0.08
    fl.spot_size = math.radians(95); fl.spot_blend = 0.5
    flood = bpy.data.objects.new('flood', fl); link(flood); flood.location = (1.0, 0.25, 3.0)
    look(flood, (0.0, 6.0, 0.4))
    camera((0.35, -0.55, 1.4), (0.2, 6.0, 1.05), 28)

    def upd(t, u):
        on = TL.LIGHT_ON <= t < TL.LIGHT_OFF
        fl.energy = 0.0 if not on else (450.0 if t < TL.LIGHT_ON + 1 / 15 else 900.0)   # a lâmpada pega no primeiro frame
        for o in foot_parts:
            o.hide_render = not on
        for o, X, Z, side in sheets:
            if side:
                o.data.vertices.foreach_set('co', sheet_pose(X, Z, t, side).ravel())
                o.data.update()
        return (on, round(t, 3))
    return upd
