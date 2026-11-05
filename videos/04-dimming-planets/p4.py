from lib import *
from planets import *
from timeline import NAME_HOLD, LIGHTS_OUT

SHOTS = {'p4a': 6.25, 'p4b': 3.5, 'p4c': 3.75, 'p4d': 3.75}
STAR_AZ, STAR_EL = 24, 11

def sph(az, el, d=1.0):
    a, e = math.radians(az), math.radians(el)
    return (d * math.cos(e) * math.sin(a), d * math.cos(e) * math.cos(a), d * math.sin(e))

def stone_mat():
    m, nt = mat('stone')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.6, Detail=9.0, Roughness=0.62); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.16, 0.14, 0.15)), (0.65, (0.42, 0.38, 0.38))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=0.8, Distance=0.12); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, 0.85, spec=0.2, normal=bp.outputs[0]).outputs[0])
    return m

def stage():
    s = reset(18)
    world_flat((0.002, 0.0, 0.002), 1.0)
    light = sun(7.0, sph(STAR_AZ, STAR_EL), (1.0, 0.16, 0.08), 3.0)
    rm = stone_mat()
    box('ground', (6000, 6000, 1), (0, 0, -0.5), rm)
    rs = np.random.RandomState(6)
    for i in range(50):
        r = 0.4 + rs.rand() ** 2 * 2.4
        o = ico('rock', r, ((rs.rand() * 2 - 1) * 90, 8 + rs.rand() * 200, 0), rm, 3); o.scale = (1, 1, 0.5)
    sm = emission('redstar', (0.9, 0.03, 0.01), 0.58)
    ico('redstar', 78.0, sph(STAR_AZ, STAR_EL, 900), sm, 4)
    glow, gm = halo(190.0, sph(STAR_AZ, STAR_EL, 901), (0.9, 0.03, 0.01), 0.55)
    return light, sm, glow

def stars(count):
    """estrelas soltas, ordenadas da mais longe para a mais perto da estrela vermelha"""
    rs = np.random.RandomState(12)
    m = emission('star', (0.86, 0.9, 1.0), 12.0)
    az = rs.rand(count) * 100 - 30
    el = 14 + rs.rand(count) ** 0.8 * 50
    d = np.hypot(az - STAR_AZ, el - STAR_EL)
    order = np.argsort(-d)
    return [ico('star', 3.0 + 2.2 * rs.rand(), sph(az[i], el[i], 800), m, 1) for i in order]

def show(objs, first):
    for i, o in enumerate(objs):
        o.hide_render = i < first

def build_p4a():
    s = reset(20)
    world_flat((0, 0, 0), 1.0)
    sd = (0.85, -0.3, 0.35)
    sun(4.0, sd, (1.0, 0.2, 0.12))
    p = planet_dimming(1.0); atmosphere(1.0, (1.0, 0.25, 0.2), sd, 1.03, power=4, strength=0.8)
    ico('redstar', 0.3, (2.2, 2.5, 1.1), emission('redstar', (0.9, 0.03, 0.01), 0.58), 4)
    halo(0.72, (2.2, 2.51, 1.1), (0.9, 0.03, 0.01), 0.55)
    p.rotation_euler = (0.3, -0.2, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, NAME_HOLD, SHOTS['p4a'])
        p.rotation_euler.z = 0.1 * t
        cam.location = vlerp((0, -3.6, 0.05), (0.2, -2.9, 0.1), ease(u))
        look(cam, (0.25 * ease(u), 0, 0.15 * ease(u)))
    return update

def build_p4b():
    stage()
    sky = stars(26)
    cam = camera((0, 0, 1.6), (0, 30, 1.6), 30)
    def update(t, u):
        cam.location = (0, 0.4 * t, 1.6)
        e = 7 + 22 * ease(u)
        look(cam, sph(STAR_AZ - 10, e, 100))
    return update

def build_p4c():
    stage()
    sky = stars(26)
    cam = camera((0, 0, 1.6), sph(STAR_AZ - 8, 29, 100), 30)
    def update(t, u):
        show(sky, int(26 * min(1.0, t / 3.3)))
        look(cam, sph(STAR_AZ - 8 + 8 * ease(u), 29 - 13 * ease(u), 100))
    return update

def build_p4d():
    light, sm, glow = stage()
    cam = camera((0, 0, 1.6), sph(STAR_AZ, STAR_EL + 3, 100), 34)
    base = light.data.energy
    def update(t, u):
        k = 1.0
        if t >= LIGHTS_OUT:
            k = 0.0
        elif t >= 2.1:                                         # falha antes de apagar
            k = 0.55 + 0.45 * math.sin(t * 47)
        sm.node_tree.nodes['Emission'].inputs['Strength'].default_value = 0.58 * k
        glow.hide_render = k == 0.0
        light.data.energy = base * k
        look(cam, sph(STAR_AZ, STAR_EL + 3 - 0.8 * u, 100))
    return update
