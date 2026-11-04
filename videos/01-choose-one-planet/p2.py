from lib import *
from planets import *
from nature import *

SHOTS = {'p2a': 3.5, 'p2b': 4.0, 'p2c': 3.5, 'p2d': 4.0}

def hills(x, y):
    return (fbm(x * 0.012 + 3, y * 0.012, 4) - 0.5) * 16 + (fbm(x * 0.08, y * 0.08, 3) - 0.5) * 0.9

def gold_fruit_mat():
    m, nt = mat('fruit')
    lw = n(nt, 'ShaderNodeLayerWeight', Blend=0.4)
    p = principled(nt, (1.0, 0.68, 0.10), 0.22, metal=0.85, emis=(1.0, 0.62, 0.08), emis_str=0)
    L(nt, math_(nt, 'ADD', math_(nt, 'MULTIPLY', lw.outputs['Facing'], 1.4), 0.25), p.inputs['Emission Strength'])
    out(nt, p.outputs[0])
    return m

def villager(loc, s=1.0):
    root = bpy.data.objects.new('v', None); link(root); root.location = loc; root.scale = (s, s, s)
    cl = simple('cl', (0.92, 0.91, 0.87), 0.7)
    sk = simple('sk', (0.86, 0.68, 0.56), 0.45)
    bk = simple('bk', (0.01, 0.01, 0.01), 0.5)
    b = tube('body', [(0, 0, 0.03), (0, 0, 0.7), (0, 0, 1.35), (0, 0, 1.52)], [.3, .26, .2, .07], cl, res=6); b.parent = root
    h = ico('head', 0.17, (0, 0, 1.72), sk, 3); h.scale = (1, 1, 1.15); h.parent = root
    for dx in (-.065, .065):
        e = ico('e', 0.024, (dx, -0.155, 1.76), bk, 2); e.parent = root
    arc = [(0.1 * math.sin(a), -0.158 + 0.03 * abs(math.sin(a)), 1.67 - 0.035 * math.cos(a)) for a in np.linspace(-1.2, 1.2, 7)]
    g = tube('sm', arc, [.008] * 7, bk, res=3); g.parent = root
    arm = tube('arm', [(.22, 0, 1.38), (.4, 0, 1.6), (.46, 0, 1.9)], [.05, .045, .04], cl); arm.parent = root
    a2 = tube('arm2', [(-.22, 0, 1.38), (-.3, 0, 1.0), (-.3, 0, .68)], [.05, .045, .04], cl); a2.parent = root
    return root, arm

def build_p2a():
    s = reset(20)
    world_space((0.006, 0.012, 0.03), 1.0)
    sd = (-1.0, -0.7, 0.4)
    sun(4.5, sd, (1, 0.98, 0.94))
    p, c = planet_green(1.0); atmosphere(1.0, (0.35, 0.65, 1.0), sd, 1.04)
    p.rotation_euler = c.rotation_euler = (0.35, -0.2, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        p.rotation_euler.z = 2.2 + 0.1 * t
        c.rotation_euler.z = 2.2 + 0.14 * t
        cam.location = vlerp((0.3, -3.7, 0.2), (0.15, -2.75, 0.1), ease(u))
        look(cam, (0.05, 0, 0))
    return update

def build_p2b():
    s = reset(18)
    sky()
    sd = (-0.7, -0.6, 0.62)
    sun(3.6, sd, (1, 0.95, 0.85), 2.0)
    grid_mesh('terrain', 520, 260, hills, ground_mat())
    cpos = (0, 0)
    z0 = float(hills(np.array([0.0]), np.array([0.0]))[0])
    grass(0, 0, math.pi / 2, 70, 420000, hills, 3)
    def place(x, y):
        return (x, y, float(hills(np.array([x]), np.array([y]))[0]) - 0.1)
    cottage(place(-3, 30), 0.25, 1.15)
    cottage(place(11, 40), -0.4, 1.0, (0.9, 0.85, 0.7), (0.2, 0.32, 0.5))
    cottage(place(-20, 46), 0.5, 1.0, (0.95, 0.9, 0.86), (0.55, 0.3, 0.1))
    tree(place(-12, 27), 1.5, 2); tree(place(14, 25), 1.3, 3); tree(place(26, 60), 2.0, 4); tree(place(-34, 62), 2.2, 5); tree(place(4, 72), 2.0, 7)
    fog((0.72, 0.85, 0.95), 40, 420, 0.75, 'LINEAR')
    cam = camera((0, 0, z0 + 1.2), (0, 30, z0 + 2), 30)
    def update(t, u):
        p = vlerp((0, 0, z0 + 1.15), (0.5, 4.5, z0 + 1.3), ease(u))
        cam.location = p + Vector((0, 0, 0.012 * math.sin(t * 5)))
        look(cam, (-1.5 + 1.5 * u, 30, z0 + 3.0))
    return update

def build_p2c():
    s = reset(20)
    sky()
    sd = (-0.8, -0.5, 0.45)
    sun(3.4, sd, (1, 0.9, 0.72), 2.0)
    flat = lambda x, y: hills(x, y) * 0.12
    grid_mesh('terrain', 300, 180, flat, ground_mat())
    z0 = float(flat(np.array([0.0]), np.array([6.0]))[0])
    grass(0, -9, math.pi / 2, 40, 380000, flat, 5, spread=2.2)
    tr, blobs = tree((0, 6, z0 - .1), 1.25, 11)
    fm = gold_fruit_mat(); stem = simple('st', (0.2, 0.12, 0.05), 0.8)
    rnd = random.Random(4)
    fruits = []
    for i in range(40):
        p, rad = rnd.choice(blobs)
        th = rnd.uniform(3.3, 6.1); ph = rnd.uniform(1.1, 2.6)
        q = Vector(p) + Vector((math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th) - 0.3, math.cos(ph))) * (rad + 0.02)
        w = tr.matrix_world @ q
        wl = Vector((0, 6, z0 - .1)) + q * 1.25
        o = ico('fruit', 0.3, wl, fm, 3); o.scale = (1, 1, 1.15)
        fruits.append((o, wl.copy(), rnd.uniform(0, 6.28)))
    fog((0.75, 0.82, 0.86), 25, 300, 0.7, 'LINEAR')
    cam = camera((0, -3, z0 + 1.4), (0, 6, z0 + 4.4), 28)
    def update(t, u):
        cam.location = vlerp((-3.2, -7.2, z0 + 1.3), (1.6, -4.6, z0 + 1.7), ease(u))
        look(cam, (0, 6, z0 + 4.3))
        for o, base, ph in fruits:
            o.location = base + Vector((0.035 * math.sin(t * 2.2 + ph), 0, 0.015 * math.sin(t * 3.1 + ph)))
    return update

def build_p2d():
    s = reset(20)
    sky()
    sd = (-0.9, -0.55, 0.32)
    sun(3.6, sd, (1, 0.85, 0.62), 2.0)
    flat = lambda x, y: hills(x, y) * 0.25
    grid_mesh('terrain', 320, 200, flat, ground_mat())
    grass(0, -6, math.pi / 2, 45, 420000, flat, 8, spread=2.6)
    z0 = float(flat(np.array([0.0]), np.array([0.0]))[0])
    # monte de moedas de ouro
    rs = np.random.RandomState(2)
    N = 5200
    r = 1.9 * np.sqrt(rs.rand(N)); a = rs.rand(N) * 6.283
    x = r * np.cos(a); y = r * np.sin(a)
    z = z0 + 1.15 * np.exp(-(r / 1.05) ** 2) * (0.75 + 0.5 * rs.rand(N)) + 0.03
    seg = 10
    ang = np.arange(seg) / seg * 6.283
    ring = np.stack([np.cos(ang), np.sin(ang), np.zeros(seg)], 1) * 0.062
    V = []; F = []
    rots = rs.randn(N, 3); rots /= np.linalg.norm(rots, axis=1, keepdims=True)
    rots[:, 2] = np.abs(rots[:, 2]) + 0.8; rots /= np.linalg.norm(rots, axis=1, keepdims=True)
    for i in range(N):
        nz_ = rots[i]
        u_ = np.cross(nz_, [0.3, 0.5, 0.8]); u_ /= np.linalg.norm(u_); v_ = np.cross(nz_, u_)
        pts = (np.array([x[i], y[i], z[i]]) + ring[:, :1] * u_ + ring[:, 1:2] * v_).astype(np.float32)
        base = i * (seg + 1)
        V.append(pts); V.append(np.array([[x[i], y[i], z[i]]], np.float32))
        for k in range(seg):
            F.append((base + seg, base + k, base + (k + 1) % seg))
    gm, gn = mat('gold')
    pos = n(gn, 'ShaderNodeNewGeometry').outputs['Position']
    nz = n(gn, 'ShaderNodeTexNoise', Scale=22.0, Detail=2.0); L(gn, pos, nz.inputs['Vector'])
    c = ramp(gn, [(0.35, (1.0, 0.58, 0.08)), (0.65, (1.0, 0.80, 0.22))], nz.outputs['Fac']).outputs[0]
    pp = principled(gn, c, 0.28, metal=1.0, emis=(1.0, 0.6, 0.1), emis_str=0.12)
    out(gn, pp.outputs[0])
    fast_mesh('coins', np.concatenate(V), F, gm)
    # moradores acenando em sincronia
    people = []
    for i, xx in enumerate(np.linspace(-7.5, 7.5, 7)):
        yy = 9.5 + 0.5 * math.sin(i * 1.7)
        zz = float(flat(np.array([xx]), np.array([yy]))[0])
        people.append(villager((xx, yy, zz - .04), 1.3))
    cottage((-20, 30, z0 - .1), 0.3, 1.1); cottage((16, 33, z0 - .1), -0.3, 1.1, (0.9, 0.85, 0.7), (0.2, 0.32, 0.5))
    fog((0.86, 0.78, 0.62), 25, 300, 0.75, 'LINEAR')
    cam = camera((0, -5, z0 + 1.3), (0, 0, z0 + 0.6), 32)
    def update(t, u):
        p = vlerp((-1.4, -5.2, z0 + 1.7), (0.1, -3.9, z0 + 1.9), ease(u))
        cam.location = p
        look(cam, (0, 6, z0 + 1.15))
        for root, arm in people:
            w = math.sin(t * 5.2)
            set_tube(arm, [(.22, 0, 1.38), (.42 + .09 * w, 0, 1.6), (.5 + .3 * w, 0, 1.92)], [.05, .045, .04])
    return update
