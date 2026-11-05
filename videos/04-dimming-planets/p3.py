from lib import *
from planets import *
from timeline import NAME_HOLD

SHOTS = {'p3a': 6.0, 'p3b': 3.75, 'p3c': 3.5, 'p3d': 4.0}

def rock_mat():
    """pedra que some no preto com a distância, como o alcance de um flash"""
    m, nt = mat('flashrock')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.9, Detail=9.0, Roughness=0.62); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.10, 0.10, 0.10)), (0.65, (0.34, 0.34, 0.33))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=0.9, Distance=0.12); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    cd = n(nt, 'ShaderNodeCameraData').outputs['View Distance']
    fade = math_(nt, 'DIVIDE', math_(nt, 'SUBTRACT', cd, 5.0), 26.0, clamp=True)
    c = mix(nt, fade, c, (0, 0, 0))
    out(nt, principled(nt, c, 0.85, spec=0.15, normal=bp.outputs[0]).outputs[0])
    return m

def stage():
    s = reset(18)
    world_flat((0, 0, 0), 1.0)
    flash = sun(3.0, (0.08, -1, 0.16), (0.95, 0.97, 1.0), 1.5)   # o flash, que sai da câmera
    rm = rock_mat()
    box('ground', (6000, 6000, 1), (0, 0, -0.5), rm)
    rs = np.random.RandomState(9)
    for i in range(70):
        r = 0.12 + rs.rand() ** 2 * 0.7
        x = (rs.rand() * 2 - 1) * 18
        if abs(x) < 1.4: x += 2.8 * np.sign(x or 1)
        o = ico('rock', r, (x, 2 + rs.rand() * 34, 0), rm, 2); o.scale = (1, 0.8 + rs.rand() * 0.5, 0.5 + rs.rand() * 0.4)
    return flash

def build_p3a():
    s = reset(20)
    world_flat((0, 0, 0), 1.0)
    sd = (0.92, 0.42, 0.16)
    sun(2.4, sd, (0.85, 0.9, 1.0))
    p = planet_shutter(1.0); atmosphere(1.0, (0.6, 0.65, 0.72), sd, 1.012, power=6, strength=0.35)
    p.rotation_euler = (0.3, -0.2, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, NAME_HOLD, SHOTS['p3a'])
        p.rotation_euler.z = 0.1 * t
        cam.location = vlerp((-0.1, -3.6, 0.05), (0.5, -2.5, 0.05), ease(u))
        look(cam, (0.3 * ease(u), 0, 0))
    return update

def build_p3b():
    stage()
    cam = camera((0, 0, 1.5), (0, 12, 1.2), 30)
    def update(t, u):
        cam.location = (0.006 * math.sin(t * 2.0), 0, 1.5 + 0.006 * math.sin(t * 3.1))
    return update

def build_p3c():
    stage()
    who = pale_figure((0.5, 26, 0))
    cam = camera((0, 0, 1.5), (0, 12, 1.3), 30)
    def update(t, u):
        who.location.y = 15 if t >= 2.5 else 26
        cam.location = (0.006 * math.sin(t * 2.0), 0, 1.5 + 0.006 * math.sin(t * 3.1))
    return update

def build_p3d():
    flash = stage()
    who = pale_figure((0.2, 5.5, 0))
    cam = camera((0, 0, 1.5), (0, 12, 1.4), 30)
    far = flash.rotation_euler.copy()
    low = Vector((0.12, -1, 0.02)).to_track_quat('Z', 'Y').to_euler()   # de perto, o flash vem de frente
    def update(t, u):
        near = t >= 2.5                                       # entre os dois flashes, ele chega
        who.location = (0.0, 0.27, 0) if near else (0.2, 5.5, 0)
        flash.rotation_euler = low if near else far
        z = HEAD_Z - 0.02 if near else 1.5
        cam.location = (0.006 * math.sin(t * 2.0), 0, z)
        look(cam, (0, 12, z) if near else (0, 12, 1.4), 0.09 if near else 0.0)
    return update
