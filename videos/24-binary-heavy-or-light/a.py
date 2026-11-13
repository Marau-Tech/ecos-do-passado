"""A: o planeta pesado. O planeta achatado, a luva colada no cascalho e a planície até a luz do abrigo,
com o rastro de outra pessoa que termina no meio do caminho."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'a1': 4.5, 'a2': 4.0, 'a3': 4.5}
RUST = ((0.2, 0.08, 0.04), (0.36, 0.17, 0.09))
SKY = (0.2, 0.09, 0.05)


def build_a1():
    """O planeta visto de lado, no plano do equador, para o achatamento ficar à vista."""
    reset(20)
    world_space((0.015, 0.012, 0.02), 1.0)
    sd = (-1.0, -0.45, 0.25)
    sun(4.5, sd, (1.0, 0.86, 0.72))
    p = planet_heavy(1.0)
    atmosphere(1.0, (0.9, 0.45, 0.25), sd, 1.025, power=4, strength=0.6).scale = (1, 1, TL.FLAT)
    cl = heavy_clouds(1.0)
    for o in (p, cl):
        o.rotation_euler = (0.0, math.radians(-4), 0)
    cam = camera((0.05, -3.6, 0.1), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, TL.NAME_HOLD, SHOTS['a1'])
        p.rotation_euler.z = 0.06 * t
        cl.rotation_euler.z = 0.09 * t
        cam.location = vlerp((0.05, -3.6, 0.1), (0.25, -2.6, 0.05), ease(u))
        look(cam, (0.1 * u, 0, 0))
    return update


def overcast(z, m_color):
    """teto de nuvem baixo e opaco, que brilha fraco de ferrugem"""
    m, nt = mat('deck')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    mp = n(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.08, 0.04, 1.0); L(nt, pos, mp.inputs['Vector'])
    a = n(nt, 'ShaderNodeTexNoise', Scale=1.0, Detail=6.0, Roughness=0.6); L(nt, mp.outputs[0], a.inputs['Vector'])
    col = ramp(nt, [(0.35, tuple(c * 0.4 for c in m_color)), (0.7, m_color)], a.outputs['Fac']).outputs[0]
    e = n(nt, 'ShaderNodeEmission', Strength=1.0); L(nt, col, e.inputs['Color'])
    out(nt, e.outputs[0])
    return box('deck', (3000, 3000, 0.1), (0, 0, z), m)


def heavy_ground(seed=2, area=(-4, 4, -0.5, 14), k=4000):
    m = ground(RUST, 'rust', bump=0.6, scale=0.8)
    box('ground', (3000, 3000, 0.1), (0, 0, -0.05), m)
    pebbles('gravel', k, area, (0.01, 0.06), rock_mat('gravel', (0.38, 0.2, 0.12)), seed)


def build_a2():
    """Rente ao chão: a luva espalmada no cascalho, o céu baixo e pesado. A luva se arrasta alguns centímetros."""
    reset(24)
    world_flat(SKY, 0.6)
    heavy_ground()
    overcast(3.5, (0.38, 0.17, 0.09))
    sun(2.2, (0.4, -0.3, 0.35), (1.0, 0.7, 0.5), 8.0)
    fog((0.24, 0.11, 0.06), 2.0, 40.0, 0.9)
    gr = glove((0.2, 0.8, 0.0), math.radians(38))
    gl = glove((-0.24, 0.66, 0.0), math.radians(-40))
    cam = camera((0.0, 0.0, 0.34), (0.0, 3.0, -0.15), 26)
    def update(t, u):
        gr.location.y = 0.78 + 0.06 * ease(u)                       # o braço puxa o corpo, quase nada
        cam.location = Vector((0.0, 0.015 * u, 0.34 - 0.006 * math.sin(math.pi * u))) + shake(t, 0.003, 3.0)
        look(cam, (0.0, 3.0, -0.15))
    return update


def trail_mesh(name, pts, half_w, m, z=0.004):
    """faixa no chão ao longo de uma linha"""
    pts = np.asarray(pts, np.float32)
    d = np.gradient(pts, axis=0); d /= np.linalg.norm(d, axis=1, keepdims=True)
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    hw = np.asarray(half_w, np.float32)[:, None] if np.ndim(half_w) else half_w
    L_ = pts + nrm * hw; R_ = pts - nrm * hw
    v = np.zeros((2 * len(pts), 3), np.float32)
    v[0::2, :2] = L_; v[1::2, :2] = R_; v[:, 2] = z
    t = []
    for i in range(len(pts) - 1):
        a = 2 * i
        t += [(a, a + 1, a + 2), (a + 1, a + 3, a + 2)]
    return fast_mesh(name, v, np.array(t, np.int32), m)


def build_a3():
    """Rente ao chão, a planície até o horizonte e a luz minúscula do abrigo. Na chave, ao lado, o rastro de
    arrasto de outra pessoa, que termina no meio do caminho."""
    reset(24)
    world_flat(SKY, 0.6)
    heavy_ground(5, (-5, 5, 0.5, 20), 5000)
    overcast(6.0, (0.36, 0.16, 0.08))
    sun(2.0, (-0.3, -0.5, 0.35), (1.0, 0.7, 0.5), 8.0)
    fog((0.26, 0.12, 0.07), 6.0, 260.0, 0.8)
    shelter = (9.0, 160.0, 0.6)
    ico('shelter', 0.5, shelter, emission('shelterl', (1.0, 0.85, 0.55), 60.0), 2)
    box('hut', (2.4, 1.6, 1.2), (shelter[0], shelter[1] + 1.2, 0.6), simple('hut', (0.05, 0.04, 0.04), 0.8))
    # o outro rastro: duas marcas de joelho e um arrasto no meio, do lado da câmera em direção ao abrigo
    s = np.linspace(0, 1, 120)
    path = np.stack([0.7 + 0.6 * s + 0.1 * np.sin(9 * s), 1.6 + 11 * s], 1)
    drag = simple('drag', (0.07, 0.03, 0.02), 1.0)
    groove = simple('groove', (0.035, 0.015, 0.01), 1.0)
    nrm = np.array([[1.0, 0.0]]) * 0.16
    marks = [trail_mesh('drag', path, 0.17, drag, 0.003),
             trail_mesh('knee', path - nrm, 0.05, groove, 0.005),
             trail_mesh('knee', path + nrm, 0.05, groove, 0.005)]
    end = path[-1]
    lump = ico('lump', 0.3, (end[0], end[1] + 0.35, 0.1), simple('lump', (0.5, 0.49, 0.46), 0.8), 2)
    lump.scale = (1.0, 1.7, 0.45)
    marks.append(lump)
    g = glove((-0.3, 1.25, 0.0), math.radians(-38), 1.0)
    cam = camera((0.0, 0.0, 0.42), (0.6, 50.0, -1.8), 30)
    def update(t, u):
        on = t >= TL.TURN
        for o in marks:
            o.hide_render = not on
        y = 0.12 * u
        g.location.y = 1.25 + y
        cam.location = Vector((0.0, y, 0.42 - 0.01 * math.sin(math.pi * u))) + shake(t, 0.003, 3.0)
        look(cam, (0.6, 50.0 + y, -1.8))
        return None
    return update
