"""B: o planeta rápido. Ele gira na órbita, e na superfície o sol cruza o céu a cada segundo e as plantas
nascem e secam em volta do módulo de pouso."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'b1': 4.5, 'b2': 4.0}


def build_b1():
    reset(20)
    world_space((0.015, 0.012, 0.02), 1.0)
    sd = (-1.0, -0.3, 0.3)
    sun(4.2, sd, (1, 0.98, 0.96))
    p = planet_fast(1.0); atmosphere(1.0, (0.45, 0.65, 1.0), sd, 1.03, power=4, strength=0.7)
    cl = clouds(1.0)
    for o in (p, cl):
        o.rotation_euler = (0.25, -0.15, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, TL.NAME_HOLD, SHOTS['b1'])
        p.rotation_euler.z = 2 * math.pi * t / TL.SPIN
        cl.rotation_euler.z = 2 * math.pi * t / (TL.SPIN * 0.7)
        cam.location = vlerp((0.1, -3.6, 0.1), (0.05, -2.3, 0.05), ease(u))
        look(cam, (-0.05 * u, 0, 0))
    return update


def build_b2():
    reset(24)
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    day = n(nt, 'ShaderNodeValue'); day.outputs[0].default_value = 1.0
    col = mix(nt, day.outputs[0], (0.01, 0.015, 0.035), (0.45, 0.65, 0.95))
    bg = n(nt, 'ShaderNodeBackground', Strength=0.8); L(nt, col, bg.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, bg.outputs[0], o.inputs['Surface'])
    ground(((0.12, 0.2, 0.08), (0.22, 0.3, 0.12)), 'soil')
    sn = sun(4.0, (0, 0.3, 1), (1, 0.96, 0.9), 2.0)
    lander((0, 0, 0), math.radians(20))
    # plantas em volta: cones finos que crescem e secam juntos
    pm, pnt = mat('plant')
    age = n(pnt, 'ShaderNodeValue'); age.outputs[0].default_value = 0.0
    pc = ramp(pnt, [(0.0, (0.08, 0.35, 0.06)), (0.6, (0.25, 0.4, 0.08)), (1.0, (0.35, 0.22, 0.08))], age.outputs[0]).outputs[0]
    out(pnt, principled(pnt, pc, 0.8).outputs[0])
    rs = np.random.RandomState(9)
    v, t_ = lathe([(0.05, 0), (0.04, 0.3), (0.0, 0.7)], 6)
    plants = []
    for i in range(70):
        x, y = rs.uniform(-6, 6), rs.uniform(-5, 6)
        if abs(x) < 2.0 and abs(y) < 2.0:
            continue
        pl = fast_mesh('plant', v, t_, pm); pl.location = (x, y, 0)
        pl.rotation_euler = (rs.uniform(-0.2, 0.2), rs.uniform(-0.2, 0.2), 0)
        plants.append((pl, rs.uniform(0.7, 1.4)))
    cam = camera((-2.6, -7.0, 1.6), (0.0, 0.0, 1.5), 32)
    def update(t, u):
        ph = 2 * math.pi * t / TL.DAY - math.pi / 2                    # começa no nascer do sol
        el = math.sin(ph)
        d = Vector((math.cos(ph), 0.35, max(el, 0.02)))
        sn.rotation_euler = d.normalized().to_track_quat('Z', 'Y').to_euler()
        sn.data.energy = 4.5 * max(0.0, el) ** 0.6
        day.outputs[0].default_value = 0.06 + 0.94 * max(0.0, min(1.0, el * 2.5 + 0.3))
        g = (t / TL.SEASON) % 1.0
        age.outputs[0].default_value = g
        for pl, s in plants:
            sz = s * (0.15 + 0.85 * math.sin(math.pi * min(1.0, g * 1.4)) if g < 0.72 else s * 0.55)
            pl.scale = (s, s, max(0.05, sz))
        cam.location = (-2.6 + 0.05 * u, -7.0 + 0.12 * u, 1.6)
        return None
    return update
