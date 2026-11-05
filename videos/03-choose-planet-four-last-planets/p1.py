from lib import *
from planets import *
from nature import sky
from timeline import NAME_HOLD

SHOTS = {'p1a': 6.0, 'p1b': 3.75, 'p1c': 3.5, 'p1d': 4.0}
HAZE = (0.78, 0.86, 0.94)

def salt_mat():
    m, nt = mat('saltground')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    vo = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=0.3); L(nt, pos, vo.inputs['Vector'])
    line = math_(nt, 'LESS_THAN', vo.outputs['Distance'], 0.012)
    bp = n(nt, 'ShaderNodeBump', Strength=0.25, Distance=0.01); L(nt, vo.outputs['Distance'], bp.inputs['Height'])
    nz = n(nt, 'ShaderNodeTexNoise', Scale=0.08, Detail=4.0, Roughness=0.5); L(nt, pos, nz.inputs['Vector'])
    tone = ramp(nt, [(0.35, (0.90, 0.92, 0.95)), (0.65, (0.98, 0.98, 0.97))], nz.outputs['Fac']).outputs[0]
    col = mix(nt, line, tone, (0.72, 0.76, 0.82))
    cd = n(nt, 'ShaderNodeCameraData').outputs['View Distance']
    fade = math_(nt, 'DIVIDE', math_(nt, 'SUBTRACT', cd, 80.0), 900.0, clamp=True)
    col = mix(nt, fade, col, HAZE)
    rough = math_(nt, 'ADD', math_(nt, 'MULTIPLY', line, 0.5), 0.02)
    out(nt, principled(nt, col, rough, spec=0.9, normal=bp.outputs[0]).outputs[0])
    return m

def stage():
    s = reset(18)
    sky()
    sun(2.2, (-0.4, -0.3, 0.8), (1, 0.98, 0.94), 3.0)
    box('ground', (6000, 6000, 1), (0, 0, -0.5), salt_mat())
    return s

def prints(y0, count, step=0.78, x=0.13):
    """pegadas alternadas ao longo de +Y; devolve a lista de posições"""
    pos = np.array([[(-x if i % 2 else x), y0 + i * step, 0.004] for i in range(count)], np.float32)
    v, t = lathe([(0.0, 0.0), (0.12, 0.0), (0.11, 0.012), (0.0, 0.012)], 12)
    sc = np.tile(np.array([1.0, 2.4, 1.0], np.float32), (count, 1))
    yaw = np.array([(0.06 if i % 2 else -0.06) for i in range(count)], np.float32)
    return scatter('prints', v, t, pos, yaw, sc, simple('print', (0.16, 0.19, 0.27), 0.85), False)

def build_p1a():
    s = reset(20)
    world_space((0.012, 0.014, 0.03), 1.0)
    sd = (-1.0, -0.5, 0.4)
    sun(4.0, sd, (1, 0.98, 0.95))
    p = planet_salt(1.0); atmosphere(1.0, (0.7, 0.85, 1.0), sd, 1.04, power=4, strength=1.0)
    p.rotation_euler = (0.3, -0.2, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, NAME_HOLD, SHOTS['p1a'])
        p.rotation_euler.z = 0.06 * t
        d = lerp(3.5, 1.32, ease(u))
        cam.location = (0.2 * (1 - u) - 0.25 * u, -d, 0.15 + 0.1 * u)
        look(cam, (-0.25 * u, 0, 0.1 * u))
    return update

def build_p1b():
    stage()
    cam = camera((0, 0, 1.0), (0, 30, 4.0), 28)
    def update(t, u):
        y = 1.3 * t
        cam.location = (0.02 * math.sin(t * 3.4), y, 1.0 + 0.02 * math.sin(t * 6.8))
        look(cam, (0, y + 30, 8.0 + 4.0 * u))
    return update

def build_p1c():
    stage()
    prints(1.6, 120)
    cam = camera((0, 0, 1.6), (0, 10, 0.8), 30)
    def update(t, u):
        y = 1.5 * t
        cam.location = (0.02 * math.sin(t * 3.4), y, 1.6 + 0.025 * math.sin(t * 6.8))
        look(cam, (0, y + 9, 0.9), 0.01 * math.sin(t * 2))
    return update

def build_p1d():
    stage()
    prints(1.6, 120)
    cam = camera((0, 0, 1.6), (0, 10, 1.0), 30)
    def update(t, u):
        turn = ease((t - 2.0) / 1.7) * math.pi        # vira para trás: nenhuma pegada vem de lá
        cam.location = (0.01 * math.sin(t * 3.0), 0, 1.6 + 0.012 * math.sin(t * 6.0))
        look(cam, (20 * math.sin(turn), 20 * math.cos(turn), 1.2 + 0.4 * math.sin(turn)))
    return update
