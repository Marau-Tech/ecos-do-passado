from lib import *
from planets import *

SHOTS = {'p4a': 4.0, 'p4b': 3.5, 'p4c': 3.75, 'p4d': 3.75}

ROBE = [(0.30, 0), (0.27, 0.45), (0.24, 0.9), (0.25, 1.35), (0.13, 1.46), (0.055, 1.5), (0.055, 1.56),
        (0.11, 1.6), (0.125, 1.7), (0.115, 1.8), (0.07, 1.87), (0.0, 1.89)]
ROBE_LOW = [(0.30, 0), (0.24, 1.0), (0.24, 1.35), (0.06, 1.5), (0.12, 1.6), (0.11, 1.8), (0.0, 1.89)]

def cloth_mat():
    m, nt = mat('robe')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=3.0, Detail=5.0, Roughness=0.6); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.55, 0.54, 0.50)), (0.65, (0.78, 0.76, 0.70))], a.outputs['Fac']).outputs[0]
    out(nt, principled(nt, c, 0.8, spec=0.2).outputs[0])
    return m

def dust_mat():
    m, nt = mat('dust')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.7, Detail=9.0, Roughness=0.62); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.26, 0.255, 0.24)), (0.65, (0.40, 0.39, 0.36))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=0.7, Distance=0.1); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, 0.95, spec=0.15, normal=bp.outputs[0]).outputs[0])
    return m

def field(cx, cy, half, step=1.5, gap=0.0, seed=1):
    rs = np.random.RandomState(seed)
    k = int(half * 2 / step)
    gx, gy = np.meshgrid(np.arange(k), np.arange(k))
    x = cx - half + gx.ravel() * step + (rs.rand(k * k) - .5) * step * 0.55
    y = cy - half + gy.ravel() * step + (rs.rand(k * k) - .5) * step * 0.55
    if gap: 
        ok = np.abs(x) > gap
        x, y = x[ok], y[ok]
    return np.stack([x, y, np.zeros_like(x)], 1)

def crowd(pos, cam_xy, turned, near=30.0, face_target=None, seed=1):
    """figuras em 2 níveis de detalhe. turned=True olha para a câmera"""
    rs = np.random.RandomState(seed)
    N = len(pos)
    dist = np.hypot(pos[:, 0] - cam_xy[0], pos[:, 1] - cam_xy[1])
    if turned:
        yaw = facing(pos, cam_xy) + (rs.rand(N) - .5) * 0.1
    else:
        yaw = np.pi + (rs.rand(N) - .5) * 0.5
    sc = (0.92 + 0.2 * rs.rand(N))
    cm = cloth_mat()
    a = dist < near
    v, t = lathe(ROBE, 14)
    objs = []
    if a.any():
        objs.append(scatter('crowd_hi', v, t, pos[a], yaw[a], sc[a], cm))
    v, t = lathe(ROBE_LOW, 6)
    objs.append(scatter('crowd_lo', v, t, pos[~a], yaw[~a], sc[~a], cm))
    if turned:
        black = simple('hole', (0.004, 0.004, 0.004), 0.5)
        v, t = lathe([(0, -1), (.7, -.7), (1, 0), (.7, .7), (0, 1)], 6)
        b = dist < 70
        for dx, dz, sz in ((-0.05, 1.73, 0.024), (0.05, 1.75, 0.024), (0.0, 1.645, 0.03)):
            yy = yaw[b]
            off = np.stack([dx * np.cos(yy) + 0.112 * np.sin(yy), dx * np.sin(yy) - 0.112 * np.cos(yy), np.full(len(yy), dz)], 1) * sc[b, None]
            objs.append(scatter('faces', v, t, pos[b] + off, yy, np.stack([np.full(len(yy), sz)] * 3, 1), black))
    return objs

def pale_sky():
    world_flat((0.70, 0.70, 0.67), 1.0)

def stage(field_half, step=1.5, gap=0.0):
    s = reset(18)
    pale_sky()
    sun(1.2, (-0.3, -0.25, 0.9), (1, 0.98, 0.94), 12.0)
    box('ground', (6000, 6000, 1), (0, 0, -0.5), dust_mat())
    return s

def build_p4a():
    s = reset(20)
    world_space((0.012, 0.012, 0.012), 1.0)
    sd = (-1.0, -0.5, 0.4)
    sun(4.0, sd, (1, 0.98, 0.95))
    p = planet_crowd(1.0); atmosphere(1.0, (0.8, 0.8, 0.75), sd, 1.02, power=5, strength=0.5)
    p.rotation_euler = (0.3, -0.2, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        p.rotation_euler.z = 0.06 * t
        d = lerp(3.5, 1.32, ease(u))
        cam.location = (0.2 * (1 - u) - 0.25 * u, -d, 0.15 + 0.1 * u)
        look(cam, (-0.25 * u, 0, 0.1 * u))
    return update

def build_p4b():
    stage(0)
    pos = field(0, 120, 190, 1.7)
    crowd(pos, (0, -40), False, near=0.0)
    fog((0.70, 0.70, 0.67), 30, 260, 0.97, 'LINEAR')
    cam = camera((0, -20, 34), (0, 60, 0), 30)
    def update(t, u):
        cam.location = vlerp((0, -24, 34), (0, -2, 11), ease(u))
        look(cam, (0, lerp(60, 44, u), 1.0))
    return update

def build_p4c():
    stage(0)
    pos = field(0, 60, 80, 1.45, 0.85, 3)
    crowd(pos, (0, 2), False, near=28.0, seed=3)
    fog((0.70, 0.70, 0.67), 4, 62, 0.97, 'LINEAR')
    cam = camera((0, 0, 1.62), (0, 20, 1.6), 30)
    def update(t, u):
        y = lerp(0, 3.6, u)
        cam.location = (0.03 * math.sin(t * 3.6), y, 1.62 + 0.02 * math.sin(t * 7.2))
        look(cam, (0, y + 12, 1.55), 0.01 * math.sin(t * 2))
    return update

def face(loc):
    """o rosto ainda errado: olhos desalinhados, boca que abre para baixo"""
    root = bpy.data.objects.new('face', None); link(root); root.location = loc
    skin = tuple((0.70, 0.66, 0.58))
    sm, nt = mat('skin4')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    nz = n(nt, 'ShaderNodeTexNoise', Scale=22.0, Detail=7.0, Roughness=0.6); L(nt, tc, nz.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.58, 0.52, 0.45)), (0.65, (0.76, 0.71, 0.62))], nz.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=0.5, Distance=0.006); L(nt, nz.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, 0.42, normal=bp.outputs[0]).outputs[0])
    cl = cloth_mat()
    black = simple('void', (0.002, 0.002, 0.002), 0.45)
    head = ico('head', 0.135, (0, 0, 0), sm, 5); head.scale = (0.84, 1.0, 1.42); head.parent = root
    d = head.modifiers.new('d', 'DISPLACE')
    tx = bpy.data.textures.new('fc', 'CLOUDS'); tx.noise_scale = 0.07; tx.noise_depth = 2
    d.texture = tx; d.strength = 0.014
    v, t = lathe(ROBE[:6], 28)
    body = fast_mesh('body', v, t, cl, True); body.parent = root; body.location = (0, 0, -1.72)
    # olhos pequenos e desalinhados, nariz errado
    for dx, dz, r in ((-0.047, 0.05, 0.0125), (0.05, 0.03, 0.0155)):
        e = ico('eye', r, (dx, -0.114, dz), black, 3); e.scale = (1.25, 0.6, 0.9); e.parent = root
        lid = ico('lid', r * 1.7, (dx, -0.104, dz + r * 0.4), sm, 3); lid.scale = (1.3, 0.7, 0.6); lid.parent = root
    nose = ico('nose', 0.013, (0.006, -0.128, -0.01), sm, 3); nose.scale = (0.8, 1.1, 1.8); nose.parent = root
    # boca: fenda fina, larga demais, que ainda não sabe abrir
    mouth = ico('mouth', 0.03, (0.006, -0.109, -0.085), black, 4); mouth.scale = (1.9, 0.5, 0.09); mouth.parent = root
    return root, mouth

def build_p4d():
    stage(0)
    cam_xy = (0, 0)
    pos = field(0, 56, 76, 1.45, 0.85, 3)
    crowd(pos, cam_xy, True, near=30.0, seed=3)
    root, mouth = face((0, 2.7, 1.72))
    fog((0.70, 0.70, 0.67), 4, 60, 0.97, 'LINEAR')
    cam = camera((0, 0, 1.62), (0, 3.4, 1.7), 34)
    def update(t, u):
        lunge = ease((t - 2.5) / 0.3)
        y = lerp(2.7, 1.55, ease(t / 2.5))
        root.location = (0, lerp(y, 0.34, lunge), 1.72 + 0.006 * math.sin(t * 3))
        root.rotation_euler.y = 0.05 * math.sin(t * 1.3) + 0.22 * ease((t - 1.2) / 1.3)
        mz = 0.09 + 0.1 * ease((t - 1.4) / 1.1) + 0.62 * lunge
        mouth.scale = (1.9 + 0.35 * ease((t - 1.4) / 1.1), 0.5, mz)
        mouth.location.z = -0.085 - 0.03 * lunge
        cam.location = Vector((0, 0, 1.62)) + shake(t, 0.004 + 0.03 * lunge, 11.0)
        look(cam, (0, 3, 1.72))
    return update
