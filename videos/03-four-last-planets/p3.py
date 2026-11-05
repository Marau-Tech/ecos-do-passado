from lib import *
from planets import *
from timeline import NAME_HOLD

SHOTS = {'p3a': 6.0, 'p3b': 3.75, 'p3c': 3.5, 'p3d': 4.0}
STORM = (0.30, 0.34, 0.42)

def snow_mat():
    m, nt = mat('snow')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.35, Detail=8.0, Roughness=0.6); L(nt, pos, a.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.8, Distance=0.3); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    col = ramp(nt, [(0.35, (0.70, 0.76, 0.86)), (0.65, (0.92, 0.95, 1.0))], a.outputs['Fac']).outputs[0]
    out(nt, principled(nt, col, 0.7, spec=0.3, normal=bp.outputs[0]).outputs[0])
    return m

def stage(storm=STORM):
    s = reset(18)
    world_flat(storm, 1.0)
    sun(0.35, (0.2, -0.3, 0.9), (0.7, 0.8, 1.0), 20.0)
    box('ground', (6000, 6000, 1), (0, 0, -0.5), snow_mat())
    return s

def flakes(cx, cy, count=30000, seed=2, reach=22.0):
    """neve: lascas minúsculas numa caixa ao redor da câmera; o objeto inteiro anda com o vento"""
    rs = np.random.RandomState(seed)
    x = cx + (rs.rand(count) * 2 - 1) * reach
    y = cy + (rs.rand(count) * 2 - 1) * reach
    z = rs.rand(count) * 9.0
    w = 0.011 * (0.6 + rs.rand(count) * 0.9)
    v = np.empty((count * 3, 3), np.float32)
    v[0::3] = np.stack([x - w, y, z - w], 1)
    v[1::3] = np.stack([x + w, y, z - w], 1)
    v[2::3] = np.stack([x, y, z + w], 1)
    t = np.arange(count * 3).reshape(-1, 3)
    o = fast_mesh('flakes', v, t, emission('flake', (0.9, 0.95, 1.0), 1.6))
    return o

def fire(loc=(0, 0, 0)):
    """fogueira: lenha, chamas emissivas e uma luz que pisca"""
    logs = simple('log', (0.07, 0.04, 0.025), 0.9)
    for i in range(5):
        a = i * 1.26
        tube('log', [(0.5 * math.cos(a) + loc[0], 0.5 * math.sin(a) + loc[1], 0.1), (0.1 * math.cos(a) + loc[0], 0.1 * math.sin(a) + loc[1], 0.28),
                     (-0.1 * math.cos(a) + loc[0], -0.1 * math.sin(a) + loc[1], 0.28)], [0.07, 0.07, 0.06], logs)
    fm = emission('flame', (1.0, 0.30, 0.05), 0.9)
    core = emission('flamecore', (1.0, 0.65, 0.22), 1.6)
    cones = []
    for i, (r, h, a) in enumerate(((0.28, 0.9, 0), (0.2, 0.75, 2.1), (0.2, 0.7, 4.2), (0.14, 0.5, 1.0))):
        v, t = lathe([(r, 0), (r * 0.8, h * 0.35), (r * 0.4, h * 0.75), (0.0, h)], 8)
        o = fast_mesh('flame', v, t, core if i == 3 else fm, True)
        o.location = (loc[0] + 0.1 * math.cos(a), loc[1] + 0.1 * math.sin(a), 0.25)
        cones.append(o)
    light = point((loc[0], loc[1], loc[2] + 0.7), 700, (1.0, 0.55, 0.2), 0.3)
    def flick(t):
        for i, o in enumerate(cones):
            k = 1 + 0.18 * math.sin(t * 13 + i * 2.1) + 0.1 * math.sin(t * 31 + i)
            o.scale = (1 + 0.1 * math.sin(t * 17 + i), 1 + 0.1 * math.cos(t * 15 + i), k)
        light.data.energy = 700 * (1 + 0.2 * math.sin(t * 19) + 0.12 * math.sin(t * 41))
    return flick

def build_p3a():
    s = reset(20)
    world_space((0.012, 0.014, 0.02), 1.0)
    sd = (-1.0, -0.5, 0.4)
    sun(4.0, sd, (0.95, 0.97, 1.0))
    p, c = planet_white(1.0); atmosphere(1.0, (0.75, 0.85, 1.0), sd, 1.04, power=4, strength=1.0)
    p.rotation_euler = c.rotation_euler = (0.3, -0.2, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, NAME_HOLD, SHOTS['p3a'])
        p.rotation_euler.z = 0.05 * t
        c.rotation_euler.z = 0.09 * t
        d = lerp(3.5, 1.32, ease(u))
        cam.location = (0.2 * (1 - u) - 0.25 * u, -d, 0.15 + 0.1 * u)
        look(cam, (-0.25 * u, 0, 0.1 * u))
    return update

def build_p3b():
    stage()
    flick = fire((0, 0, 0))
    fl = flakes(0, 0)
    fog(STORM, 1.0, 22, 0.98)
    cam = camera((0, -9, 3.0), (0, 0, 0.6), 30)
    def update(t, u):
        flick(t)
        fl.location = (-6.0 * t, 0, -1.0 * t)
        cam.location = (0.03 * math.sin(t * 2), -8.0 + 4.8 * ease(u), 3.0 - 1.4 * ease(u))
        look(cam, (0, 0, 0.7))
    return update

def build_p3c():
    stage()
    flick = fire((0, 0, 0))
    fl = flakes(0, 0)
    fig = figure((0, 11.0, 0), math.pi, 1.0)
    fog(STORM, 1.0, 22, 0.98)
    cam = camera((0.5, -2.6, 1.15), (0, 4, 1.3), 30)
    def update(t, u):
        flick(t)
        fl.location = (-6.0 * t, 0, 0)
        dist = 11.0 - 2.8 * ease((t - 0.9) / 0.25) - 2.8 * ease((t - 2.3) / 0.25)    # cada batida traz a figura mais perto
        fig.location = (0.3 * math.sin(t * 0.7), dist, 0)
        cam.location = (0.5 + 0.02 * math.sin(t * 2), -2.6, 1.15)
        look(cam, (0, 4, 1.3))
    return update

def build_p3d():
    stage()
    flick = fire((0, 0, 0))
    fl = flakes(0, 0)
    fig = figure((0, 5.0, 0), math.pi, 1.0, eyes=True)
    fog(STORM, 1.0, 22, 0.98)
    cam = camera((0.0, -2.6, 1.2), (0, 3, 1.3), 30)
    def update(t, u):
        flick(t)
        fl.location = (-6.0 * t, 0, 0)
        near = ease((t - 0.7) / 0.2)
        inside = 1.0 if t > 1.9 else 0.0
        y = lerp(5.4, 3.7, near)
        y = 0.0 if inside else y
        fig.location = (0, y + (0.35 if inside else 0), 0)
        sc = 1.0 + 0.25 * ease((t - 2.0) / 2.0) * inside
        fig.scale = (sc, sc, sc)
        cam.location = (0.0 + 0.02 * math.sin(t * 2), -2.6 + 0.2 * ease((t - 2.0) / 2.0), 1.2)
        look(cam, (0, 3, 1.3 + 0.2 * inside))
    return update
