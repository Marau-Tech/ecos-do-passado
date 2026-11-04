from lib import *
from planets import *

SHOTS = {'p3a': 3.75, 'p3b': 3.75, 'p3c': 3.5, 'p3d': 4.0}

def waves(X, Y, t, a=1.0):
    z = np.zeros_like(X)
    for amp, kx, ky, w, ph in ((.42, .05, .09, .7, 0), (.26, -.08, .12, 1.0, 1), (.14, .19, .06, 1.5, 2), (.08, -.14, -.3, 2.2, 3), (.05, .42, .3, 3.1, 4)):
        z += amp * np.sin(X * kx + Y * ky + t * w + ph)
    return z * a

def sea_mat():
    m, nt = mat('sea')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.9, Detail=6.0, Roughness=0.55); L(nt, pos, a.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.4, Distance=0.2); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, (0.003, 0.016, 0.02), 0.1, spec=0.8, normal=bp.outputs[0]).outputs[0])
    return m

class Sea:
    def __init__(self, size=340, res=380, center=(0, 60), amp=1.0):
        self.amp = amp
        m = sea_mat()
        self.o = grid_mesh('sea', size, res, lambda x, y: waves(x, y, 0, amp), m, center)
        co = np.empty(len(self.o.data.vertices) * 3, np.float32)
        self.o.data.vertices.foreach_get('co', co)
        self.co = co.reshape(-1, 3)
        box('far', (9000, 9000, 0.1), (0, 0, -1.8), m)
    def update(self, t, amp=None):
        c = self.co
        c[:, 2] = waves(c[:, 0].astype(np.float64), c[:, 1].astype(np.float64), t, amp or self.amp)
        me = self.o.data
        me.vertices.foreach_set('co', c.ravel()); me.update()

def storm_sky():
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    g = ramp(nt, [(0.0, (0.22, 0.30, 0.28)), (0.1, (0.10, 0.15, 0.15)), (0.5, (0.03, 0.05, 0.06))], sp.outputs['Z']).outputs[0]
    z = math_(nt, 'MAXIMUM', sp.outputs['Z'], 0.05)
    cv = n(nt, 'ShaderNodeCombineXYZ')
    L(nt, math_(nt, 'DIVIDE', sp.outputs['X'], z), cv.inputs['X']); L(nt, math_(nt, 'DIVIDE', sp.outputs['Y'], z), cv.inputs['Y'])
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.7, Detail=8.0, Roughness=0.6); L(nt, cv.outputs[0], a.inputs['Vector'])
    cl = ramp(nt, [(0.45, (0, 0, 0)), (0.7, (0.7, 0.7, 0.7))], a.outputs['Fac']).outputs[0]
    col = mix(nt, cl, g, (0.26, 0.31, 0.30))
    b = n(nt, 'ShaderNodeBackground', Strength=1.0); L(nt, col, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])

def raft():
    root = bpy.data.objects.new('raft', None); link(root)
    wood = simple('rw', (0.16, 0.10, 0.06), 0.8)
    rope = simple('rp', (0.5, 0.42, 0.28), 0.9)
    for i in range(7):
        x = (i - 3) * 0.3
        o = tube('lg', [(x, -1.5 + 0.1 * (i % 2), 0.12), (x, 0, 0.12), (x, 1.5 - 0.1 * (i % 3), 0.12)], [.15, .15, .15], wood); o.parent = root
    for y in (-1.0, 1.0):
        o = tube('cr', [(-1.15, y, 0.27), (0, y, 0.28), (1.15, y, 0.27)], [.07, .07, .07], wood); o.parent = root
        for x in (-.9, .9):
            r = tube('rope', [(x, y - .12, .3), (x, y, .36), (x, y + .12, .3)], [.03, .03, .03], rope); r.parent = root
    return root

def skin_mat(rough=0.42):
    m, nt = mat('skin')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.05, Detail=7.0, Roughness=0.6); L(nt, tc, a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.60, 0.64, 0.60)), (0.65, (0.82, 0.80, 0.72))], a.outputs['Fac']).outputs[0]
    w = n(nt, 'ShaderNodeTexWave', {'wave_type': 'BANDS', 'bands_direction': 'Z'}, Scale=0.09, Distortion=5.0, Detail=4.0); L(nt, tc, w.inputs['Vector'])
    f = n(nt, 'ShaderNodeTexNoise', Scale=0.6, Detail=8.0, Roughness=0.65); L(nt, tc, f.inputs['Vector'])
    h = math_(nt, 'ADD', math_(nt, 'MULTIPLY', w.outputs['Fac'], 0.7), math_(nt, 'MULTIPLY', f.outputs['Fac'], 0.3))
    bp = n(nt, 'ShaderNodeBump', Strength=0.3, Distance=0.35); L(nt, h, bp.inputs['Height'])
    out(nt, principled(nt, c, rough, spec=0.5, normal=bp.outputs[0]).outputs[0])
    return m

def finger(base, height, curl, target, r=6.0):
    """pontos e raios de um dedo que sobe de base e curva para target"""
    b = Vector(base); tg = Vector(target)
    side = (tg - b); side.z = 0; side.normalize()
    segs = [0.0, 0.34, 0.62, 0.84, 1.0]
    pts = []; p = b.copy(); a = 0.0
    L_ = height
    for i, s_ in enumerate(segs):
        if i:
            step = L_ * (s_ - segs[i - 1])
            a += curl * (0.25 + 0.3 * i)
            p = p + (Vector((0, 0, 1)) * math.cos(a) + side * math.sin(a)) * step
        pts.append(p.copy())
    # 3 pontos por falange, com o nó engrossado em cada junta
    base_r = [r * 1.15, r, r * 0.95, r * 0.78, r * 0.42]
    out_p, out_r = [], []
    for i in range(4):
        for k in range(3):
            w = k / 3
            out_p.append(tuple(pts[i].lerp(pts[i + 1], w)))
            out_r.append(lerp(base_r[i], base_r[i + 1], w) * (1.16 if k == 0 and i else 0.94))
    out_p.append(tuple(pts[4])); out_r.append(base_r[4])
    return out_p, out_r

def nail_mat():
    return simple('nail', (0.62, 0.56, 0.38), 0.25)

def build_p3a():
    s = reset(20)
    world_space((0.004, 0.012, 0.014), 1.0)
    sd = (-1.0, -0.45, 0.5)
    sun(4.8, sd, (0.9, 0.96, 1.0))
    p, c = planet_deep(1.0); atmosphere(1.0, (0.2, 0.5, 0.55), sd, 1.03, power=4, strength=0.9)
    p.rotation_euler = c.rotation_euler = (0.3, -0.2, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        p.rotation_euler.z = 0.1 * t
        c.rotation_euler.z = 0.16 * t
        cam.location = vlerp((0.25, -3.6, 0.3), (0.1, -2.55, 0.1), ease(u))
        look(cam, (0, 0, 0))
    return update

def build_p3b():
    s = reset(20)
    storm_sky()
    sun(1.4, (-0.5, 0.7, 0.3), (0.72, 0.88, 0.86), 5.0)
    sea = Sea(size=300, res=360, center=(0, 40))
    r = raft()
    fog((0.11, 0.16, 0.16), 40, 330, 0.95, 'LINEAR')
    cam = camera((6, -10, 5), (0, 0, 0), 32)
    def update(t, u):
        sea.update(t)
        z = float(waves(np.array([0.]), np.array([0.]), t)[0])
        dz = float(waves(np.array([0.]), np.array([1.5]), t)[0]) - float(waves(np.array([0.]), np.array([-1.5]), t)[0])
        dx = float(waves(np.array([1.]), np.array([0.]), t)[0]) - float(waves(np.array([-1.]), np.array([0.]), t)[0])
        r.location = (0, 0, z - 0.02)
        r.rotation_euler = (math.atan2(dz, 3.0), -math.atan2(dx, 2.0), 0.15 * math.sin(t * 0.3))
        a = -0.9 + 0.35 * u
        d = lerp(7, 26, ease(u))
        cam.location = Vector((d * math.sin(a), -d * math.cos(a), lerp(2.6, 9, ease(u))))
        look(cam, (0, 0, 0))
    return update

def palm_hand(m, S=1.0, z=-120.0):
    """mão aberta com a palma para cima, gigante, no fundo"""
    root = bpy.data.objects.new('hand', None); link(root)
    palm = ico('palm', 60, (0, 0, 0), m, 5); palm.scale = (1.1, 1.25, 0.34); palm.parent = root
    wrist = tube('wr', [(0, -60, -6), (0, -110, -30), (0, -210, -80)], [40, 36, 36], m); wrist.parent = root
    for i, (x, y, a, l) in enumerate(((-58, 44, -0.32, 125), (-22, 66, -0.1, 150), (16, 68, 0.07, 160), (52, 52, 0.25, 140))):
        d = (math.sin(a), math.cos(a))
        pts = [(x, y, 2), (x + d[0] * l * .4, y + d[1] * l * .4, 10), (x + d[0] * l * .75, y + d[1] * l * .75, 18), (x + d[0] * l, y + d[1] * l, 30), (x + d[0] * l * 1.1, y + d[1] * l * 1.1, 33)]
        f = tube('fg', pts, [21, 19, 17, 12, 2], m, res=8); f.parent = root
    f = tube('th', [(56, -30, 0), (104, 10, 8), (130, 40, 18), (142, 62, 28), (150, 74, 32)], [34, 22, 18, 12, 2], m, res=8); f.parent = root
    root.location = (0, 0, z); root.scale = (S, S, S); root.rotation_euler.z = 0.25
    return root

def shaft_mat():
    m, nt = mat('shaft')
    g = n(nt, 'ShaderNodeNewGeometry')
    lw = n(nt, 'ShaderNodeLayerWeight', Blend=0.3)
    fac = math_(nt, 'POWER', lw.outputs['Facing'], 3.0)
    inv = math_(nt, 'SUBTRACT', 1.0, fac)
    e = n(nt, 'ShaderNodeEmission'); e.inputs['Color'].default_value = (0.35, 0.72, 0.68, 1)
    L(nt, math_(nt, 'MULTIPLY', inv, 0.035), e.inputs['Strength'])
    tr = n(nt, 'ShaderNodeBsdfTransparent')
    ad = n(nt, 'ShaderNodeAddShader'); L(nt, tr.outputs[0], ad.inputs[0]); L(nt, e.outputs[0], ad.inputs[1])
    out(nt, ad.outputs[0])
    return m

def build_p3c():
    s = reset(20)
    world_flat((0.004, 0.035, 0.04), 1.0)
    sun(1.1, (0.15, 0.1, 1), (0.55, 0.85, 0.8), 18.0)
    palm_hand(skin_mat(0.6), 0.5, -165)
    sm = shaft_mat()
    rnd = random.Random(3)
    for i in range(9):
        x, y = rnd.uniform(-34, 34), rnd.uniform(-34, 34)
        v, t = lathe([(1.2 + rnd.random() * 2, 30), (9 + rnd.random() * 6, -420)], 12)
        o = fast_mesh('sh', v, t, sm, True); o.location = (x, y, 0)
    bub = simple('bub', (0.6, 0.85, 0.85), 0.1, emis=(0.4, 0.7, 0.7), emis_str=0.5)
    rs = np.random.RandomState(4)
    bpos = rs.rand(70, 3) * (20, 20, 40) - (10, 10, 30)
    v, t = lathe([(0, -1), (.7, -.7), (1, 0), (.7, .7), (0, 1)], 8)
    bm = scatter('bubbles', v, t, bpos, None, 0.03 + 0.09 * rs.rand(70), bub)
    fog((0.005, 0.045, 0.05), 60, 97, 1.0, 'LINEAR')
    cam = camera((0, 0, -4), (0, 0, -100), 36)
    def update(t, u):
        k = ease(u)
        z = lerp(-6, -24, k)
        bm.location = (0, 0, t * 2.2)
        cam.location = Vector((math.sin(t * 0.5) * 0.4, -lerp(14, 2, k), z))
        look(cam, (0, 6, -165), 0.03 * math.sin(t * 0.6))
    return update

def claw_mesh(m):
    v, t = lathe([(1.0, 0), (0.75, 0.7), (0.3, 1.5), (0.0, 2.2)], 12)
    return fast_mesh('claw', v, t, m, True)

def build_p3d():
    s = reset(20)
    storm_sky()
    sun(2.4, (-0.35, -0.8, 0.42), (0.78, 0.92, 0.88), 5.0)
    sea = Sea(size=300, res=360, center=(0, 0), amp=1.5)
    r = raft()
    m = skin_mat(0.4)
    nm = nail_mat()
    ang = (-74, -34, 4, 42, 118)
    base = [(106 * math.sin(math.radians(a)), 106 * math.cos(math.radians(a))) for a in ang]
    fingers = []
    for i, (x, y) in enumerate(base):
        pts, rad = finger((x, y, -40), 10, 0, (0, 0, 0), 9.5)
        f = tube('finger', pts, rad, m, res=10, bevel=5)
        fingers.append((f, claw_mesh(nm), (x, y), 120 + 10 * (i % 3), i * 0.09))
    fog((0.11, 0.16, 0.16), 60, 320, 0.8, 'LINEAR')
    cam = camera((0, -3, 1.8), (0, 30, 20), 20)
    def update(t, u):
        amp = 1.5 + 2.0 * u
        sea.update(t, amp)
        z = float(waves(np.array([0.]), np.array([0.]), t, amp)[0])
        r.location = (0, 0, z - 0.02)
        r.rotation_euler = (0.08 * math.sin(t * 1.5) * (1 + 3 * u), 0.06 * math.sin(t * 1.1), 0)
        for f, claw, (x, y), h, d in fingers:
            k = ease((t - d) / 3.5)
            pts, rad = finger((x, y, -40), 45 + h * k, 0.47 * k ** 1.5, (0, 0, 0), 9.5)
            set_tube(f, pts, rad)
            tip = Vector(pts[-1]); prev = Vector(pts[-2])
            dirv = (tip - prev).normalized()
            claw.location = tip - dirv * 1.5
            claw.rotation_euler = dirv.to_track_quat('Z', 'Y').to_euler()
            sc = rad[-1] * 0.95
            claw.scale = (sc, sc, sc)
        zc = float(waves(np.array([0.]), np.array([-3.2]), t, amp)[0])
        cam.location = Vector((0, -3.2, max(z, zc) + 2.2)) + shake(t, 0.05 + 0.3 * u ** 3, 7.0)
        look(cam, (0, 30, lerp(5, 34, ease(u))), 0.1 * math.sin(t * 1.0) * u)
    return update
