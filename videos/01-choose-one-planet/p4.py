from lib import *
from planets import *

SHOTS = {'p4a': 4.0, 'p4b': 3.5, 'p4c': 3.75, 'p4d': 3.75}

def hemi(name, r, m, seg=64, rings=20):
    v = [(0, 0, r)]; f = []
    for i in range(1, rings + 1):
        a = i / rings * math.pi / 2
        for j in range(seg):
            b = j / seg * 2 * math.pi
            v.append((r * math.sin(a) * math.cos(b), r * math.sin(a) * math.sin(b), r * math.cos(a)))
    for j in range(seg):
        f.append((0, 1 + j, 1 + (j + 1) % seg))
    for i in range(rings - 1):
        for j in range(seg):
            a = 1 + i * seg + j; b = 1 + i * seg + (j + 1) % seg
            f.append((a, a + seg, b + seg, b))
    return mesh_from(name, v, f, m, True)

def build_p4a():
    s = reset(20)
    world_space((0.04, 0.004, 0.008), 1.0)
    sd = (-0.95, -0.55, 0.5)
    sun(4.0, sd, (1, 0.9, 0.85))
    p = planet_flesh(1.0); atmosphere(1.0, (1.0, 0.2, 0.15), sd, 1.09, power=5, strength=0.5)
    fm = flesh_material('lid', 1.8, 0.2)
    EP = Vector((0.08, -0.80, 0.14))
    ER = 0.44
    eye = sphere('eye', 1.0, EP, iris_material('iris4', (0.85, 0.55, 0.04), 0.06, 0.3, 3.4), 96, 48)
    eye.scale = (ER, ER, ER)
    up_l = hemi('lidU', ER * 1.05, fm); up_l.location = EP
    lo_l = hemi('lidL', ER * 1.05, fm); lo_l.location = EP
    bpy.ops.mesh.primitive_torus_add(major_radius=ER * 1.05, minor_radius=ER * 0.17, major_segments=96, minor_segments=24, location=EP, rotation=(math.pi / 2 - 0.05, 0, 0))
    tor = bpy.context.object; tor.data.materials.append(fm)
    tor.data.polygons.foreach_set('use_smooth', [True] * len(tor.data.polygons)); tor.data.update()
    cam = camera((0, -3.5, 0.3), (0, 0, 0), 38)
    def update(t, u):
        sc = 1 + 0.02 * math.sin(t * 2.6)
        p.scale = (sc, sc, sc)
        cam.location = vlerp((0.35, -3.9, 0.35), (0.12, -2.65, 0.2), ease(u))
        look(cam, (0.03, 0, 0.07))
        # abre devagar, com um tremor; depois encara
        o = ease((t - 0.9) / 1.3)
        a = lerp(0.0, 1.05, o) + 0.03 * math.sin(t * 19) * o
        up_l.rotation_euler = (-a, 0, 0); lo_l.rotation_euler = (math.pi + a * 0.8, 0, 0)
        tgt = vlerp(EP + Vector((1.2, -2, 0.4)), cam.location, ease((t - 1.9) / 0.5))
        eye.rotation_euler = (tgt - EP).to_track_quat('Y', 'Z').to_euler()
    return update

def fl_h(x, y):
    return (fbm(x * 0.03, y * 0.03, 4) - .5) * 14 + (fbm(x * 0.2 + 5, y * 0.2, 3) - .5) * 1.6

def bone_mat():
    m, nt = mat('bone')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.7, Detail=8.0); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.42, 0.32, 0.2)), (0.65, (0.82, 0.74, 0.56))], a.outputs['Fac']).outputs[0]
    out(nt, principled(nt, c, 0.35, spec=0.6).outputs[0])
    return m

def stage_flesh(samples=18, size=260, res=280):
    s = reset(samples)
    world_flat((0.14, 0.015, 0.012))
    sun(2.6, (-0.5, -0.5, 0.7), (1, 0.62, 0.5), 8)
    m = flesh_material('ground', 0.06, 0.55)
    g = grid_mesh('gr', size, res, fl_h, m, (0, 60))
    fog((0.20, 0.018, 0.012), 8, 150, 0.95, 'LINEAR')
    return s, g

def build_p4b():
    s, g = stage_flesh()
    bm = bone_mat()
    # costelas gigantes formando um túnel
    ribs = []
    for i in range(9):
        y = 16 + i * 11
        for sgn in (-1, 1):
            b = float(fl_h(np.array([sgn * 15.0]), np.array([y]))[0])
            o = tube('rib', [(sgn * 15, y, b - 2), (sgn * 18, y, b + 9), (sgn * 15, y + 1, b + 21), (sgn * 3.5, y + 2, b + 28)],
                     [1.5, 1.2, .8, .15], bm, res=6)
            ribs.append(o)
    z0 = float(fl_h(np.array([0.0]), np.array([0.0]))[0])
    cam = camera((0, 0, z0 + 1.7), (0, 30, z0 + 6), 26)
    base = np.array([v.co[:] for v in g.data.vertices], np.float32)
    co = base.copy()
    def update(t, u):
        # o chão respira: onda lenta subindo e descendo
        k = math.sin(t * 2.0)
        w = np.sin(base[:, 0] * 0.05 + base[:, 1] * 0.07 - t * 2.4) * 0.65
        co[:, 2] = base[:, 2] + w + 0.5 * k
        g.data.vertices.foreach_set('co', co.ravel()); g.data.update()
        p = vlerp((0, 0, z0 + 2.0), (0, 8, z0 + 2.2), u)
        cam.location = p + Vector((0, 0, 0.5 * k + 0.55 * math.sin(p.y * 0.05 - t * 2.4)))
        look(cam, p + Vector((0.6 * math.sin(t * .8), 30, 4.5 + .6 * math.sin(t * .6))), roll=0.022 * math.sin(t * 1.5))
    return update

def build_p4c():
    s, g = stage_flesh(18, 200, 220)
    fm = flesh_material('stalk', 0.25, 0.25)
    im = iris_material('iris5', (0.85, 0.55, 0.04), 0.07, 0.35, 3.4)
    z0 = float(fl_h(np.array([0.0]), np.array([0.0]))[0])
    rnd = random.Random(6)
    stalks = []
    for i in range(11):
        a = -1.0 + 2.0 * (i / 10) + rnd.uniform(-.06, .06)
        r = rnd.uniform(9, 26)
        x, y = r * math.sin(a), r * math.cos(a) + 2
        b = float(fl_h(np.array([x]), np.array([y]))[0])
        h = rnd.uniform(5, 13); rad = rnd.uniform(.9, 1.7)
        tb = tube('st', [(x, y, b - 1)] * 5, [1.3 * rad / 1.3] * 5, fm, res=6)
        e = sphere('eye', 1.0, (x, y, b), im, 40, 20); e.scale = (rad, rad, rad)
        stalks.append(dict(x=x, y=y, b=b, h=h, rad=rad, tb=tb, e=e, ph=rnd.uniform(0, 6.28), lag=rnd.uniform(0.0, 1.25)))
    cam = camera((0, 0, z0 + 1.7), (0, 20, z0 + 6), 30)
    def update(t, u):
        cam.location = Vector((0, -1.2, z0 + 1.8)) + shake(t, 0.018, 7)
        look(cam, (0.5 * math.sin(t * .7), 20, z0 + 5.8))
        for k in stalks:
            g_ = ease((t - k['lag']) / 1.25)
            h = k['h'] * g_ + 0.2
            sw = 0.55 * math.sin(t * 1.9 + k['ph'])
            x, y, b = k['x'], k['y'], k['b']
            top = Vector((x + sw, y - 1.1 * g_, b + h))
            pts = [(x, y, b - 1), (x - sw * .5, y + .3, b + h * .3), (x + sw * .8, y, b + h * .6), (x + sw * 1.1, y - .5, b + h * .85), top]
            r = k['rad'] * 0.5
            set_tube(k['tb'], pts, [r * 1.3, r, r * .8, r * .7, r * .7])
            k['e'].location = top + Vector((0, 0, k['rad'] * .55))
            look_at = vlerp(top + Vector((math.sin(k['ph']) * 8, 6, 3)), cam.location, ease((t - 1.7 - k['lag'] * 0.5) / 0.3))
            k['e'].rotation_euler = (look_at - k['e'].location).to_track_quat('Y', 'Z').to_euler()
    return update

def teeth_ring(R, z, count, length, rad, m, tilt=0.5):
    V = []; F = []
    seg = 12
    for i in range(count):
        a = i / count * 2 * math.pi
        p = Vector((R * math.cos(a), R * math.sin(a), z))
        d = Vector((-math.cos(a), -math.sin(a), -tilt)).normalized()
        u_ = d.cross(Vector((0, 0, 1))).normalized(); v_ = d.cross(u_)
        b = len(V)
        l = length * random.uniform(.8, 1.2)
        for k in range(seg):
            c = k / seg * 2 * math.pi
            V.append(tuple(p + u_ * rad * math.cos(c) + v_ * rad * math.sin(c)))
        V.append(tuple(p + d * l))
        for k in range(seg):
            F.append((b + k, b + (k + 1) % seg, b + seg))
    return mesh_from('teeth', V, F, m, True)

def build_p4d():
    s = reset(14)
    world_flat((0.0, 0.0, 0.0))
    random.seed(9)
    tm = bone_mat()
    # garganta: funil de carne fechando para o fundo
    n_r, n_a = 70, 96
    prof = lambda k: 34 * (1 - k) ** 1.15 + 1.5
    V, F = [], []
    for i in range(n_r):
        k = i / (n_r - 1)
        z = -k * 190
        R = prof(k) * (1 + 0.06 * math.sin(k * 40))
        for j in range(n_a):
            a = j / n_a * 2 * math.pi
            V.append((R * math.cos(a), R * math.sin(a), z))
    for i in range(n_r - 1):
        for j in range(n_a):
            a = i * n_a + j; b = i * n_a + (j + 1) % n_a
            F.append((a, b, b + n_a, a + n_a))
    fm = flesh_material('throat', 0.05, 0.22)
    mesh_from('throat', V, F, fm, True)
    rings = []
    for i in range(9):
        k = (i + 0.2) / 11
        z = -k * 190
        R = prof(k)
        rings.append(teeth_ring(R * 1.1, z, 20 - i, 6.0 + R * .3, 1.25 + R * .05, tm, 0.75))
    point((0, 0, -120), 3000, (1, 0.2, 0.12), 3)
    hl = point((0, 0, 40), 26000, (1, 0.88, 0.8), 2)
    s.cycles.diffuse_bounces = 1
    fog((0.0, 0.0, 0.0), 40, 200, 0.92, 'LINEAR')
    cam = camera((0, 0, 44), (0, 0, -100), 24)
    def update(t, u):
        z = lerp(40, -150, u ** 1.9)
        cam.location = Vector((0.0, 0.0, z)) + shake(t, 0.9, 11)
        hl.location = cam.location + Vector((6, 3, 4))
        look(cam, (2 * math.sin(t * 1.4), 2 * math.cos(t * 1.1), z - 60), roll=t * 0.5 + 0.9 * u * u)
        for i, r in enumerate(rings):
            r.rotation_euler.z = (t * 0.55 * (1 if i % 2 else -1))
    return update
