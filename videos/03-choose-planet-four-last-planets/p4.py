from lib import *
from planets import *
from timeline import NAME_HOLD

SHOTS = {'p4a': 6.25, 'p4b': 3.5, 'p4c': 3.75, 'p4d': 3.75}
HORIZON = (0.36, 0.17, 0.42)

def dust_mat():
    m, nt = mat('twindust')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.5, Detail=9.0, Roughness=0.62); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.03, 0.02, 0.05)), (0.65, (0.12, 0.07, 0.15))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=0.6, Distance=0.1); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    cd = n(nt, 'ShaderNodeCameraData').outputs['View Distance']
    fade = math_(nt, 'DIVIDE', math_(nt, 'SUBTRACT', cd, 60.0), 500.0, clamp=True)
    c = mix(nt, fade, c, HORIZON)
    out(nt, principled(nt, c, 0.9, spec=0.2, normal=bp.outputs[0]).outputs[0])
    return m

def purple_sky():
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    g = ramp(nt, [(0.0, HORIZON), (0.12, (0.20, 0.09, 0.26)), (0.35, (0.06, 0.03, 0.12)), (0.8, (0.01, 0.005, 0.03))], sp.outputs['Z']).outputs[0]
    b = n(nt, 'ShaderNodeBackground', Strength=1.0); L(nt, g, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])

def eye_mat():
    """esfera que parece um sol; quando 'open' sobe, a pálpebra abre e mostra o olho"""
    m, nt = mat('twineye')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc, sp.inputs[0])
    x, z = sp.outputs[0], sp.outputs[2]
    op = n(nt, 'ShaderNodeValue')
    x2 = math_(nt, 'MULTIPLY', x, x)
    arch = math_(nt, 'SQRT', math_(nt, 'MAXIMUM', math_(nt, 'SUBTRACT', 1.0, math_(nt, 'MULTIPLY', x2, 1.35)), 0.0))
    h = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', arch, op.outputs[0]), 0.6)
    eyem = math_(nt, 'LESS_THAN', math_(nt, 'ABSOLUTE', z), h)
    r2 = math_(nt, 'ADD', x2, math_(nt, 'MULTIPLY', z, z))
    iris = math_(nt, 'LESS_THAN', r2, 0.17)
    pup = math_(nt, 'LESS_THAN', math_(nt, 'ADD', math_(nt, 'MULTIPLY', x2, 90.0), math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', z, z), 4.0)), 1.0)
    veins = n(nt, 'ShaderNodeTexNoise', Scale=14.0, Detail=6.0, Roughness=0.6); L(nt, tc, veins.inputs['Vector'])
    white = mix(nt, math_(nt, 'MULTIPLY', ramp(nt, [(0.45, (0, 0, 0)), (0.65, (1, 1, 1))], veins.outputs['Fac']).outputs[0], 0.0), (0.95, 0.9, 0.85), (0.8, 0.15, 0.12))
    ir = mix(nt, iris, white, (0.95, 0.75, 0.15))
    ey = mix(nt, pup, ir, (0.0, 0.0, 0.0))
    lid_n = n(nt, 'ShaderNodeTexNoise', Scale=5.0, Detail=7.0, Roughness=0.6); L(nt, tc, lid_n.inputs['Vector'])
    lid = ramp(nt, [(0.35, (0.55, 0.30, 0.85)), (0.65, (0.85, 0.70, 1.0))], lid_n.outputs['Fac']).outputs[0]
    col = mix(nt, eyem, lid, ey)
    e = n(nt, 'ShaderNodeEmission'); L(nt, col, e.inputs['Color'])
    L(nt, math_(nt, 'SUBTRACT', 1.15, math_(nt, 'MULTIPLY', eyem, 0.4)), e.inputs['Strength'])
    out(nt, e.outputs[0])
    return m, op

def sph(az, el, d):
    a, e = math.radians(az), math.radians(el)
    return Vector((d * math.sin(a) * math.cos(e), d * math.cos(a) * math.cos(e), d * math.sin(e)))

def face_cam(o, cam_loc):
    o.rotation_euler = (Vector(cam_loc) - o.location).to_track_quat('-Y', 'Z').to_euler()

def stage():
    s = reset(18)
    purple_sky()
    box('ground', (6000, 6000, 1), (0, 0, -0.5), dust_mat())
    rs = np.random.RandomState(5)
    rk = simple('rock', (0.05, 0.035, 0.07), 0.9)
    for i in range(60):
        r = 1.0 + rs.rand() * 3.0
        o = ico('rock', r, (rs.randn() * 60, 25 + rs.rand() * 380, 0), rk, 3); o.scale = (1, 1, 0.45)
    # o sol de verdade, à direita
    sd = sph(22, 30, 1.0)
    sun(3.0, sd, (1.0, 0.92, 0.80), 1.0)
    ico('sun', 15.0, sph(22, 30, 700), emission('sun', (1.0, 0.95, 0.85), 60.0), 3)
    return s

def eye(cam_loc, az, el, dist, diam):
    """o falso sol: diam é o diâmetro angular em graus"""
    r = dist * math.tan(math.radians(diam / 2))
    m, op = eye_mat()
    o = sphere('twin', 1.0, sph(az, el, dist), m, 96, 48)
    o.scale = (r, r, r)
    face_cam(o, cam_loc)
    light = point(sph(az, el, dist * 0.9), 1, (0.8, 0.5, 1.0), r * 0.2)
    return o, op, light

def build_p4a():
    s = reset(20)
    world_space((0.012, 0.008, 0.02), 1.0)
    sd = (-1.0, -0.5, 0.4)
    sun(3.5, sd, (1, 0.97, 0.9))
    p = planet_twin(1.0); atmosphere(1.0, (0.6, 0.3, 0.9), sd, 1.03, power=4, strength=1.0)
    sm = emission('twinsun', (0.85, 0.6, 1.0), 10.0)
    twin = sphere('twin_sun', 0.22, (2.3, 1.2, 0.9), sm, 64, 32)
    point((2.0, 1.0, 0.8), 40, (0.7, 0.45, 1.0), 0.1)
    p.rotation_euler = (0.3, -0.2, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, NAME_HOLD, SHOTS['p4a'])
        p.rotation_euler.z = 0.06 * t
        twin.location = (2.3 - 0.3 * u, 1.2, 0.9)
        d = lerp(3.5, 1.32, ease(u))
        cam.location = (0.2 * (1 - u) - 0.25 * u, -d, 0.15 + 0.1 * u)
        look(cam, (-0.25 * u, 0, 0.1 * u))
    return update

def build_p4b():
    stage()
    cl = Vector((0, 0, 1.7))
    o, op, light = eye(cl, -18, 28, 650, 9.0)
    cam = camera(cl, sph(-2, 14, 100), 30)
    def update(t, u):
        r = 650 * math.tan(math.radians(lerp(9.0, 12.0, u) / 2))
        o.scale = (r, r, r)
        light.data.energy = r * r * 4
        cam.location = (0.02 * math.sin(t * 3.0), 0.0, 1.7)
        look(cam, sph(-2, 14, 100))
    return update

def build_p4c():
    stage()
    cl = Vector((0, 0, 1.7))
    o, op, light = eye(cl, -6, 24, 480, 24.0)
    cam = camera(cl, sph(-4, 15, 100), 30)
    def update(t, u):
        blink = max(0.0, 1.0 - abs(t - 1.7) / 0.3) * 0.0 + (ease((t - 1.45) / 0.15) - ease((t - 1.85) / 0.2))
        op.outputs[0].default_value = max(0.0, blink)
        r = 480 * math.tan(math.radians(lerp(24.0, 27.0, u) / 2))
        o.scale = (r, r, r)
        light.data.energy = r * r * 4
        look(cam, sph(-4, 15, 100))
    return update

def build_p4d():
    stage()
    cl = Vector((0, 0, 1.7))
    o, op, light = eye(cl, 0, 22, 300, 34.0)
    cam = camera(cl, sph(0, 12, 100), 30)
    def update(t, u):
        sink = ease(t / 1.9)
        el = lerp(24, 12, sink)
        ang = lerp(34, 56, ease(t / 3.4))
        o.location = sph(0, el, 300)
        r = 300 * math.tan(math.radians(ang / 2))
        o.scale = (r, r, r)
        face_cam(o, cl)
        op.outputs[0].default_value = ease((t - 2.0) / 0.5)
        light.data.energy = r * r * 4
        cam.location = Vector((0, 0, 1.7)) + shake(t, 0.004 + 0.03 * ease((t - 2.0) / 0.5), 11.0)
        look(cam, sph(0, 12, 100))
    return update
