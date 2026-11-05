from lib import *
from planets import *

SHOTS = {'p3a': 3.75, 'p3b': 3.75, 'p3c': 3.5, 'p3d': 4.0}

def hide_mat():
    m, nt = mat('hide')
    tc = n(nt, 'ShaderNodeTexCoord')
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.0, Detail=9.0, Roughness=0.65); L(nt, tc.outputs['Object'], a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.006, 0.006, 0.008)), (0.7, (0.05, 0.043, 0.05))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=1.0, Distance=0.6); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, 0.4, spec=0.6, normal=bp.outputs[0]).outputs[0])
    return m

class Walker:
    """corpo pequeno sobre 6 pernas absurdamente longas; escala livre"""
    def __init__(self, s, nlegs=6, eyes=True):
        self.s = s; self.m = hide_mat(); self.legs = []
        for i in range(nlegs):
            self.legs.append(tube(f'leg{i}', [(0, 0, i)] * 5, [1] * 5, self.m, res=6, bevel=2))
        self.body = ico('body', 0.16 * s, (0, 0, 0), self.m, 4)
        self.body.scale = (1.15, 0.9, 0.8)
        t = bpy.data.textures.new('bd', 'CLOUDS'); t.noise_scale = 0.05 * s
        d = self.body.modifiers.new('d', 'DISPLACE'); d.texture = t; d.strength = 0.05 * s
        self.eye = []
        if eyes:
            em = emission('reye', (1.0, 0.008, 0.0), 5.0)
            rnd = random.Random(1)
            for i in range(9):
                o = ico('re', 0.016 * s, (0, 0, 0), em, 2)
                self.eye.append((o, Vector((rnd.uniform(-.11, .11), -0.105, rnd.uniform(-.16, -.05))) * s))
    def pose(self, C, feet, up, r0=0.012, knee_h=0.3):
        C = Vector(C); up = Vector(up).normalized()
        self.body.location = C
        for o, off in self.eye:
            o.location = C + off
        s = self.s
        for leg, F in zip(self.legs, feet):
            F = Vector(F)
            d = F - C
            out_ = (d - d.project(up)).normalized()
            hip = C + out_ * 0.05 * s
            knee = C.lerp(F, 0.32) + up * knee_h * s + out_ * 0.14 * s
            mid = knee.lerp(F, 0.5) + out_ * 0.03 * s
            pts = [hip, C.lerp(knee, 0.65), knee, mid, F]
            set_tube(leg, pts, [r0 * s * 1.5, r0 * s * 1.25, r0 * s * 1.0, r0 * s * 0.65, r0 * s * 0.28])

def build_p3a():
    s = reset(20)
    world_space((0.05, 0.006, 0.012), 1.5)
    sd = (0.9, 0.55, 0.32)
    sun(5.0, sd, (0.72, 0.82, 1.0))
    p = planet_night(1.0); atmosphere(1.0, (0.32, 0.45, 0.8), sd, 1.018, power=3, strength=1.4)
    W = Walker(1.9)
    cam = camera((-0.5, -3.3, 0.2), (0.15, 0, 0.3), 30)
    up = Vector((0.58, 0.05, 0.80)).normalized()
    tang = up.cross(Vector((0, 1, 0))).normalized()
    side = up.cross(tang).normalized()
    def on_sphere(a, b):
        return (up + tang * a + side * b).normalized() * 1.0
    base = [(0.62, -0.4), (0.75, 0.25), (0.15, 0.7), (-0.6, 0.5), (-0.72, -0.2), (-0.1, -0.7)]
    def update(t, u):
        p.rotation_euler = (0.2, 0.1, 0.05 * t)
        step = t * 0.09
        feet = []
        for i, (a, b) in enumerate(base):
            ph = (t * 0.35 + i / 6) % 1
            k = ease(min(1, ph * 3)) if ph < 0.34 else 1
            feet.append(on_sphere(a + 0.12 * k - 0.06 + step, b) * (1 + 0.05 * math.sin(min(1, ph * 3) * math.pi) * (ph < .34)))
        C = (up + tang * step).normalized() * 2.2
        W.pose(C, feet, C, 0.015, 0.22)
        cam.location = vlerp((-0.7, -4.5, 0.5), (-0.5, -3.7, 0.7), ease(u))
        look(cam, vlerp((0.3, 0, 0.75), (0.62, 0, 1.15), ease(u)))
    return update

def ash_mat():
    m, nt = mat('ash')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.25, Detail=10.0, Roughness=0.62); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.02, 0.022, 0.03)), (0.7, (0.10, 0.11, 0.14))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=1.0, Distance=0.4); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, 0.95, normal=bp.outputs[0]).outputs[0])
    return m

def ash(x, y):
    return (fbm(x * 0.01, y * 0.01, 5) - .5) * 14

def spires(n_=70, spread=280, seed=2):
    rnd = random.Random(seed)
    m = simple('spire', (0.014, 0.014, 0.018), 0.8)
    for i in range(n_):
        x = rnd.uniform(-spread, spread); y = rnd.uniform(20, spread * 1.6)
        z = float(ash(np.array([x]), np.array([y]))[0])
        h = rnd.uniform(5, 18)
        lx, ly = rnd.uniform(-2, 2), rnd.uniform(-2, 2)
        tube('sp', [(x, y, z - 1), (x + lx * .3, y + ly * .3, z + h * .4), (x + lx, y + ly, z + h * .8), (x + lx * 2, y + ly * 1.5, z + h)],
             [h * .05, h * .03, h * .016, h * .002], m, res=3, bevel=1)

def stage_surface():
    s = reset(18)
    world_flat((0.024, 0.03, 0.05))
    sd = (0.5, 0.7, 0.45)
    sun(1.1, sd, (0.55, 0.65, 1.0), 12)
    grid_mesh('ash', 1800, 300, ash, ash_mat(), (0, 300))
    spires()
    return s

def build_p3b():
    stage_surface()
    W = Walker(1500.0, 4, eyes=False)
    W.body.hide_render = True
    fog((0.022, 0.028, 0.045), 30, 620, 0.96, 'LINEAR')
    dm, dn = mat('dust')
    nz = n(dn, 'ShaderNodeTexNoise', Scale=0.035, Detail=7.0, Roughness=0.6)
    L(dn, n(dn, 'ShaderNodeNewGeometry').outputs['Position'], nz.inputs['Vector'])
    al = ramp(dn, [(0.38, (0, 0, 0)), (0.62, (1, 1, 1))], nz.outputs['Fac']).outputs[0]
    fade = n(dn, 'ShaderNodeValue'); fade.outputs[0].default_value = 0.0
    dd = n(dn, 'ShaderNodeBsdfDiffuse'); dd.inputs['Color'].default_value = (0.11, 0.115, 0.135, 1)
    tr = n(dn, 'ShaderNodeBsdfTransparent')
    ms = n(dn, 'ShaderNodeMixShader')
    lw = n(dn, 'ShaderNodeLayerWeight', Blend=0.5)
    soft = math_(dn, 'POWER', math_(dn, 'SUBTRACT', 1.0, lw.outputs['Facing']), 2.5)
    L(dn, math_(dn, 'MULTIPLY', math_(dn, 'MULTIPLY', al, soft), math_(dn, 'MULTIPLY', fade.outputs[0], 0.55)), ms.inputs[0]); L(dn, tr.outputs[0], ms.inputs[1]); L(dn, dd.outputs[0], ms.inputs[2])
    out(dn, ms.outputs[0])
    rd = random.Random(4); dust = []
    for i in range(30):
        a = rd.uniform(0, 6.28); dist = rd.uniform(0.35, 1.0); hh = rd.uniform(0.05, 0.5)
        o = ico('dust', 1.0, (-10, 150, -4), dm, 3)
        dust.append((o, a, dist, hh, rd.uniform(0.6, 1.2)))
    z0 = float(ash(np.array([0.0]), np.array([0.0]))[0])
    cam = camera((0, 0, z0 + 1.7), (0, 100, z0 + 40), 26)
    C = Vector((-120, 420, 1300))
    def foot_z(t):
        tt = (t - 1.1) / 1.0
        return 260 * (1 - ease(tt)) ** 1.6 if tt < 1 else 0.0
    def update(t, u):
        zf = foot_z(t)
        F = [Vector((-10, 150, ash(np.array([-10.0]), np.array([150.0]))[0] - 1 + zf)),
             Vector((-190, 330, -4)), Vector((170, 440, -4)), Vector((-420, 520, -4))]
        W.pose(C, F, (0, 0, 1), 0.0115, 0.0)
        g = max(0.0, t - 2.1)
        fade.outputs[0].default_value = min(1.0, g * 5) * max(0.0, 1 - g * 0.15)
        grow = 1 - math.exp(-g * 2.0)
        for o, a, dist, hh, sz in dust:
            rr = 8 + 75 * grow * dist
            o.location = (-10 + rr * math.cos(a), 150 + rr * math.sin(a), -4 + 30 * grow * hh * sz)
            q = (1 + 30 * grow) * sz
            o.scale = (q, q, q * 0.7)
        hit = max(0.0, 1 - abs(t - 2.1) * 1.3) if t >= 2.1 else 0
        cam.location = Vector((0, 0, z0 + 1.7)) + shake(t, 0.02 + 0.42 * hit, 18)
        look(cam, Vector((-4, 100, z0 + 26)) + shake(t, 0.5 + 3.2 * hit, 14, 4))
    return update

def build_p3c():
    s = reset(18)
    world_flat((0.012, 0.016, 0.03))
    sd = (0.2, -0.8, 0.55)
    sun(1.0, sd, (0.5, 0.6, 1.0), 10)
    grid_mesh('ash', 1800, 220, ash, ash_mat(), (0, 300))
    spires(40)
    W = Walker(1500.0, 4)
    C = Vector((-30, 300, 680))
    z0 = float(ash(np.array([0.0]), np.array([0.0]))[0])
    F = [(70, 95, -4), (-290, 240, -4), (260, 330, -4), (20, 560, -4)]
    W.pose(C, F, (0, 0, 1), 0.0115, 0.0)
    fog((0.016, 0.022, 0.036), 80, 1300, 0.55, 'LINEAR')
    cam = camera((6, 0, z0 + 1.7), (-10, 90, z0), 22)
    def update(t, u):
        e = ease(u)
        look_to = vlerp((58, 95, z0 + 24), C + Vector((-30, 0, -40)), e ** 1.35)
        cam.location = Vector((6, 0, z0 + 1.7)) + shake(t, 0.02, 10)
        look(cam, look_to)
        # os olhos piscam em ondas
        for i, (o, off) in enumerate(W.eye):
            v = 1.0 if u > 0.55 + 0.03 * i else 0.0
            o.scale = (v, v, v)
    return update

def build_p3d():
    s = reset(20)
    world_flat((0.01, 0.012, 0.022))
    sun(0.9, (0.3, -0.8, 0.5), (0.5, 0.6, 1.0), 10)
    point((-22, -38, -16), 9000, (1, 0.14, 0.06), 6)
    point((26, -30, 22), 7000, (0.45, 0.55, 1.0), 6)
    hm = hide_mat()
    root = bpy.data.objects.new('head', None); link(root)
    head = ico('h', 14, (0, 0, 0), hm, 5); head.parent = root; head.scale = (1, 0.9, 1.45)
    t = bpy.data.textures.new('hd', 'CLOUDS'); t.noise_scale = 4; t.noise_depth = 3
    d = head.modifiers.new('d', 'DISPLACE'); d.texture = t; d.strength = 3.5
    neck = tube('neck', [(0, 6, 8), (0, 12, 30), (3, 24, 70), (8, 40, 140)], [6, 6, 7, 9], hm, res=6); neck.parent = root
    # boca vertical
    mouth_m = emission('mth', (0.03, 0.0, 0.0), 1.0)
    mouth = ico('m', 1.0, (0, -12.4, -8.0), mouth_m, 3); mouth.scale = (2.3, 0.5, 7.0); mouth.parent = root
    tm = simple('tooth', (0.8, 0.74, 0.58), 0.3)
    for i in range(14):
        for sgn in (-1, 1):
            z = -14 + i * 0.95
            w = 2.4 * math.sqrt(max(0.0, 1 - ((z + 8) / 7.2) ** 2))
            bpy.ops.mesh.primitive_cone_add(vertices=7, radius1=0.42, depth=1.9, location=(sgn * (w + .15), -12.9, z), rotation=(0, -sgn * 1.45, 0))
            o = bpy.context.object; o.data.materials.append(tm); o.parent = root
    # olhos
    im = iris_material('iris3', (0.95, 0.12, 0.03), 0.075, 1.3, 3.2)
    rnd = random.Random(3); eyes = []
    pts = [(0, 2.0, 2.9)]
    while len(pts) < 21:
        x, z, r = rnd.uniform(-10, 10), rnd.uniform(-2.5, 13), rnd.uniform(0.7, 2.0)
        if all((x - a) ** 2 + (z - b) ** 2 > (r + c + .25) ** 2 for a, b, c in pts) and (x / 12) ** 2 + (z / 17) ** 2 < 1:
            pts.append((x, z, r))
    for x, z, r in pts:
        yy = -12.2 * math.sqrt(max(0.05, 1 - (x / 14) ** 2 - (z / 20) ** 2))
        e = sphere('eye', 1.0, (x, yy, z), im, 32, 16); e.scale = (r, r, r); e.parent = root
        eyes.append(e)
    cam = camera((0, -70, 0), (0, 0, 0), 34)
    def update(t, u):
        # cabeça desce das nuvens, para, e avança de uma vez no final
        z = lerp(28, 2.0, ease(min(1, t / 2.3)))
        y = 0.0
        if t > 3.25:
            y = -min(1, (t - 3.25) / 0.5) ** 2 * 30
        root.location = Vector((0, y, z)) + shake(t, 0.5, 3)
        root.rotation_euler = (0.04 * math.sin(t * 1.3), 0, 0.09 * math.sin(t * 0.9) + 0.09)
        bpy.context.view_layer.update()
        cam.location = Vector((0, -47, 0)) + shake(t, 0.25 + 0.6 * u, 12)
        look(cam, (0, 0, 2.0))
        for i, e in enumerate(eyes):
            late = rnd_lag[i]
            k = ease((t - late) / 0.5)
            src = e.matrix_world.translation
            aim = vlerp(src + Vector((rnd_dir[i][0], -40, rnd_dir[i][1])), cam.location, k)
            q = (aim - src).to_track_quat('Y', 'Z')
            # rotação local = inversa do pai
            e.rotation_euler = (root.matrix_world.to_quaternion().inverted() @ q).to_euler()
    rr = random.Random(8)
    rnd_lag = [0.6 + rr.random() * 1.9 for _ in eyes]; rnd_dir = [(rr.uniform(-40, 40), rr.uniform(-30, 30)) for _ in eyes]
    return update
