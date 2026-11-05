from lib import *
from planets import *
from nature import grass
from timeline import NAME_HOLD

SHOTS = {'p1a': 6.0, 'p1b': 3.75, 'p1c': 3.5, 'p1d': 4.0}
WHEAT = ((0.50, 0.30, 0.07), (0.86, 0.60, 0.16), (1.0, 0.80, 0.34))
PATH = 1.0

def evening_sky():
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    g = ramp(nt, [(0.0, (1.0, 0.66, 0.36)), (0.10, (1.0, 0.50, 0.38)), (0.35, (0.46, 0.30, 0.52)), (0.85, (0.12, 0.13, 0.34))], sp.outputs['Z']).outputs[0]
    b = n(nt, 'ShaderNodeBackground', Strength=0.6); L(nt, g, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])

def dirt_mat():
    m, nt = mat('dirt')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=1.4, Detail=8.0, Roughness=0.6); L(nt, pos, a.inputs['Vector'])
    col = ramp(nt, [(0.35, (0.80, 0.52, 0.28)), (0.65, (1.0, 0.72, 0.42))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=0.5, Distance=0.05); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.95, spec=0.1, normal=bp.outputs[0]).outputs[0])
    return m

def field(sd, path=True, fill=0.0):
    s = reset(18)
    evening_sky()
    sun(5.0, sd, (1.0, 0.80, 0.52), 0.8)
    if fill:
        sun(fill, (-0.35, -1, 0.3), (1.0, 0.76, 0.46), 6.0)    # contraluz sem escurecer o trigo
    box('ground', (6000, 6000, 1), (0, 0, -0.5), dirt_mat())
    flat = lambda x, y: np.zeros_like(x) - (3 * (np.abs(x) < PATH + 0.18 * np.sin(y * 0.5) + 0.08 * np.sin(y * 1.7 + 1)) if path else 0)
    grass(0, -3, math.pi / 2, 80, 420000, flat, 3, 0.62, 2.8, WHEAT)
    return s

def walker():
    """pessoa que a câmera não vê: só a sombra dela aparece"""
    root = bpy.data.objects.new('walker', None); link(root)
    m = simple('shade', (0.1, 0.1, 0.1), 0.9)
    parts = []
    v, t = lathe([(0.0, 0.86), (0.17, 0.92), (0.20, 1.2), (0.23, 1.44), (0.09, 1.54), (0.0, 1.56)], 12)
    parts.append(fast_mesh('torso', v, t, m, True))
    parts.append(ico('head', 0.115, (0, 0, 1.68), m, 3))
    swing = []
    for x, z, prof in ((-0.1, 0.92, [(0.0, -0.92), (0.085, -0.9), (0.07, 0.0), (0.0, 0.02)]), (0.1, 0.92, [(0.0, -0.92), (0.085, -0.9), (0.07, 0.0), (0.0, 0.02)]),
                       (-0.27, 1.44, [(0.0, -0.68), (0.05, -0.64), (0.055, 0.0), (0.0, 0.02)]), (0.27, 1.44, [(0.0, -0.68), (0.05, -0.64), (0.055, 0.0), (0.0, 0.02)])):
        v, t = lathe(prof, 8)
        o = fast_mesh('limb', v, t, m, True); o.location = (x, 0, z)
        parts.append(o); swing.append(o)
    for o in parts:
        o.parent = root; o.visible_camera = False
    def step(t):
        a = 0.5 * math.sin(2 * math.pi * 0.95 * t)
        for o, k in zip(swing, (1, -1, -1, 1)):
            o.rotation_euler.x = a * k
        root.location.z = 0.03 * abs(math.sin(2 * math.pi * 0.95 * t))
        root.rotation_euler.y = 0.03 * math.sin(2 * math.pi * 0.95 * t)
    return root, step

def build_p1a():
    s = reset(20)
    world_space((0.03, 0.016, 0.018), 1.0)
    sd = (-1.0, -0.22, 0.2)
    sun(4.6, sd, (1, 0.86, 0.66))
    p = planet_evening(1.0); atmosphere(1.0, (1.0, 0.66, 0.36), sd, 1.03, power=5, strength=0.55)
    p.rotation_euler = (0.3, -0.2, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, NAME_HOLD, SHOTS['p1a'])
        p.rotation_euler.z = 0.8 + 0.1 * t
        cam.location = vlerp((0.1, -3.6, 0.1), (0.05, -2.3, 0.05), ease(u))
        look(cam, (-0.05 * u, 0, 0))
    return update

def build_p1b():
    field((0.1, 1, 0.09), path=False, fill=3.5)
    disc = (200, 2000, 165)
    ico('sundisc', 52.0, disc, emission('sundisc', (1.0, 0.86, 0.60), 1.4), 3)
    halo(250.0, disc, (1.0, 0.62, 0.30), 1.2)
    cam = camera((0, 0, 1.15), (0, 30, 2.5), 30)
    def update(t, u):
        y = 1.2 * t
        cam.location = (0.03 * math.sin(t * 1.3), y, 1.15 + 0.02 * math.sin(t * 2.1))
        look(cam, (1.6, y + 30, 3.4))
    return update

def build_p1c():
    field((0.04, -1, 0.17))
    who, step = walker()
    cam = camera((0, 0, 1.6), (0, 9, 0.2), 30)
    def update(t, u):
        y = 1.1 * t
        who.location.x, who.location.y = 0, y
        step(t)
        cam.location = (0.015 * math.sin(t * 3.0), y, 1.6 + 0.02 * math.sin(t * 6.0))
        look(cam, (0, y + 9, 0.2))
    return update

def build_p1d():
    field((0.04, -1, 0.17))
    who, step = walker()
    cam = camera((0, 3.85, 1.6), (0, 12.85, 0.2), 30)
    def update(t, u):
        slow = 1 - ease(t / 0.8)
        y = 3.85 + 1.1 * 0.4 * (1 - slow)                 # a câmera freia e para
        who.location.x, who.location.y = 0, 3.85 + 1.25 * t
        step(t + 3.5)
        cam.location = (0, y, 1.6 + 0.02 * slow * math.sin(t * 6.0))
        look(cam, (0, y + 9, 0.2 + 0.5 * ease((t - 2.1) / 1.6)))
    return update
