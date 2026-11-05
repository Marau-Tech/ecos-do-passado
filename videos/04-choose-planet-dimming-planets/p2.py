from lib import *
from planets import *
from timeline import NAME_HOLD

SHOTS = {'p2a': 5.75, 'p2b': 4.0, 'p2c': 3.5, 'p2d': 4.0}
FACE_Y = 1.86          # frente do rádio
DIAL_Z = 1.03

def rust_mat():
    m, nt = mat('rust')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.2, Detail=9.0, Roughness=0.62); L(nt, pos, a.inputs['Vector'])
    col = ramp(nt, [(0.35, (0.10, 0.06, 0.04)), (0.55, (0.26, 0.13, 0.07)), (0.70, (0.34, 0.30, 0.24))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=0.6, Distance=0.02); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.75, metal=0.3, normal=bp.outputs[0]).outputs[0])
    return m

def glow(m, v):
    m.node_tree.nodes['Emission'].inputs['Strength'].default_value = v

def radio():
    """rádio de mesa; devolve o ponteiro, o material do mostrador e a luz dele"""
    body = simple('radiobody', (0.05, 0.05, 0.045), 0.45, metal=0.5)
    dark = simple('radiodark', (0.006, 0.006, 0.006), 0.7)
    box('radio', (0.64, 0.3, 0.36), (0, 2.01, 0.95), body)
    dm = emission('dial', (0.22, 0.95, 0.38), 0.85)
    box('dial', (0.46, 0.012, 0.09), (0, FACE_Y - 0.006, DIAL_Z), dm)
    for i in range(13):
        x = -0.21 + i * 0.035
        box('tick', (0.003, 0.004, 0.03 if i % 3 == 0 else 0.018), (x, FACE_Y - 0.014, DIAL_Z + 0.025), dark)
    needle = box('needle', (0.006, 0.006, 0.085), (0, FACE_Y - 0.018, DIAL_Z), emission('needle', (1.0, 0.08, 0.04), 1.0))
    for i in range(11):                                      # grade do alto-falante
        box('grill', (0.34, 0.008, 0.008), (-0.1, FACE_Y - 0.004, 0.82 + i * 0.013), dark)
    for x in (0.16, 0.24):
        o = ico('knob', 0.032, (x, FACE_Y - 0.012, 0.88), simple('knob', (0.3, 0.28, 0.24), 0.35, metal=0.8), 2); o.scale = (1, 0.6, 1)
    tube('antenna', [(0.25, 2.1, 1.12), (0.3, 2.12, 1.4), (0.38, 2.14, 1.75)], [0.006, 0.005, 0.003], simple('ant', (0.5, 0.5, 0.5), 0.3, metal=1.0))
    light = point((0, FACE_Y - 0.3, DIAL_Z), 2.0, (0.4, 1.0, 0.5), 0.08)
    return needle, dm, light

def cabin():
    s = reset(18)
    world_flat((0.01, 0.006, 0.004), 1.0)
    w = rust_mat()
    box('floor', (4.2, 5.2, 0.1), (0, 0, -0.05), w)
    box('ceil', (4.2, 5.2, 0.1), (0, 0, 2.45), w)
    box('wallN', (4.2, 0.1, 2.5), (0, 2.55, 1.2), w)
    box('wallS', (4.2, 0.1, 2.5), (0, -2.55, 1.2), w)
    box('wallE', (0.1, 5.2, 2.5), (2.05, 0, 1.2), w)
    box('wallW', (0.1, 5.2, 2.5), (-2.05, 0, 1.2), w)
    box('window', (0.03, 1.0, 0.6), (-1.99, 0.3, 1.5), emission('dusk', (0.85, 0.34, 0.14), 1.3))
    for z in (1.34, 1.56):                                   # tábuas na janela
        box('plank', (0.04, 1.2, 0.09), (-1.97, 0.3, z), simple('plank', (0.05, 0.03, 0.02), 0.9), (0.08, 0, 0))
    point((-1.2, 0.3, 1.5), 14, (0.9, 0.42, 0.2), 0.5)
    point((0.4, 0.4, 2.2), 7, (1.0, 0.72, 0.5), 0.3)
    table = simple('table', (0.11, 0.075, 0.05), 0.7)
    box('desk', (1.7, 0.85, 0.05), (0, 2.05, 0.745), table)
    for x in (-0.78, 0.78):
        box('leg', (0.06, 0.7, 0.72), (x, 2.05, 0.36), table)
    paper = simple('paper', (0.55, 0.5, 0.4), 0.9)
    box('paper', (0.2, 0.28, 0.003), (-0.55, 1.95, 0.772), paper, (0, 0, 0.2))
    box('paper', (0.2, 0.28, 0.003), (-0.5, 1.9, 0.775), paper, (0, 0, -0.15))
    box('seat', (0.42, 0.42, 0.04), (0.25, 1.2, 0.46), table, (0, 0, 0.5))
    for dx, dy in ((-0.17, -0.17), (0.17, -0.17), (-0.17, 0.17), (0.17, 0.17)):
        box('chairleg', (0.03, 0.03, 0.45), (0.25 + dx, 1.2 + dy, 0.22), table)
    rs = np.random.RandomState(3)                            # poeira no ar
    pos = np.stack([rs.rand(70) * 3.6 - 1.8, rs.rand(70) * 4.4 - 1.6, rs.rand(70) * 2.2 + 0.1], 1)
    v, t = lathe([(0.0, -0.003), (0.003, 0.0), (0.0, 0.003)], 4)
    scatter('dust', v, t, pos, m=emission('dust', (1.0, 0.8, 0.6), 0.25), smooth=False)
    return s

def needle_at(o, x):
    o.location.x = max(-0.21, min(0.21, x))

def build_p2a():
    s = reset(20)
    world_space((0.022, 0.012, 0.008), 1.0)
    sd = (-1.0, -0.4, 0.35)
    sun(3.4, sd, (1, 0.9, 0.78))
    p = planet_broadcast(1.0); atmosphere(1.0, (0.9, 0.45, 0.25), sd, 1.02, power=5, strength=0.6)
    d = Vector((0.34, -0.93, 0.06)).normalized() * 1.008
    dot = ico('beacon', 0.014, tuple(d), emission('beacon', (1.0, 0.06, 0.03), 60.0), 2)
    dot.parent = p
    p.rotation_euler = (0.3, -0.2, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, NAME_HOLD, SHOTS['p2a'])
        p.rotation_euler.z = 0.05 * (t - 2.5)
        dot.hide_render = (t % 1.1) > 0.75
        cam.location = vlerp((0, -3.6, 0.1), (0.3, -1.75, 0.1), ease(u))
        look(cam, (0.28 * ease(u), 0, 0.08 * ease(u)))
    return update

def build_p2b():
    cabin()
    needle, dm, light = radio()
    cam = camera((0.5, -1.9, 1.4), (0, 2, 1.0), 28)
    def update(t, u):
        cam.location = vlerp((0.5, -1.9, 1.4), (0.2, 0.35, 1.22), ease(u))
        look(cam, (0, 2, 1.0))
        needle_at(needle, 0.05 + 0.02 * math.sin(t * 1.7))
    return update

def build_p2c():
    cabin()
    needle, dm, light = radio()
    cam = camera((0.03, 1.1, 1.06), (0, 2, 0.98), 35)
    def update(t, u):
        cam.location = vlerp((0.04, 1.1, 1.07), (0.0, 1.38, 1.04), ease(u))
        look(cam, (0, 2, 0.98))
        talk = 1.0 if 0.2 < t < 1.9 else 0.15
        needle_at(needle, 0.05 + talk * (0.07 * math.sin(t * 23) + 0.05 * math.sin(t * 37 + 1)))
    return update

def build_p2d():
    cabin()
    needle, dm, light = radio()
    cam = camera((0, 1.42, 1.05), (0, 2, DIAL_Z), 35)
    def update(t, u):
        cam.location = vlerp((0.0, 1.42, 1.05), (0.0, 1.55, DIAL_Z), ease(u))
        look(cam, (0, 2, DIAL_Z))
        talk = 1.0 if 0.1 < t < 1.7 else 0.1
        x = 0.05 + talk * (0.07 * math.sin(t * 23) + 0.05 * math.sin(t * 37 + 1))
        hit = t >= 2.0                                        # o ponteiro bate no fim da escala
        needle_at(needle, 0.125 + 0.006 * math.sin(t * 41) if hit else x)
        k = 1.25 + 0.2 * math.sin(t * 29) if hit else 0.85
        glow(dm, k)
        light.data.energy = 2.0 * k / 0.85
    return update
