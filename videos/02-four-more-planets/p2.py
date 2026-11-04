from lib import *
from planets import *
from nature import grass
from timeline import NAME_HOLD

SHOTS = {'p2a': 5.75, 'p2b': 4.0, 'p2c': 3.5, 'p2d': 4.0}
FERN = ((0.07, 0.20, 0.05), (0.12, 0.32, 0.08), (0.24, 0.40, 0.10))

def soil(x, y):
    return (fbm(x * 0.03 + 9, y * 0.03, 4) - 0.5) * 7 + (fbm(x * 0.3, y * 0.3, 3) - 0.5) * 0.5

def soil_mat():
    m, nt = mat('soil')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.8, Detail=8.0, Roughness=0.62); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.13, 0.09, 0.05)), (0.52, (0.20, 0.16, 0.07)), (0.68, (0.15, 0.27, 0.07))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=1.0, Distance=0.3); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, 0.9, spec=0.2, normal=bp.outputs[0]).outputs[0])
    return m

def bark_mat():
    m, nt = mat('bark2')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    mp = n(nt, 'ShaderNodeMapping'); L(nt, pos, mp.inputs['Vector']); mp.inputs['Scale'].default_value = (5, 5, 0.5)
    a = n(nt, 'ShaderNodeTexNoise', Scale=1.5, Detail=8.0, Roughness=0.65); L(nt, mp.outputs[0], a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.07, 0.05, 0.035)), (0.65, (0.30, 0.21, 0.13))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=1.0, Distance=0.12); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, 0.85, spec=0.2, normal=bp.outputs[0]).outputs[0])
    return m

def needle_mat():
    m, nt = mat('needle')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=1.4, Detail=6.0, Roughness=0.7); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.02, 0.08, 0.035)), (0.65, (0.07, 0.19, 0.06))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=1.0, Distance=0.3); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, 0.8, spec=0.2, normal=bp.outputs[0]).outputs[0])
    return m

def pines(count, cx, cy, spread, keep, hfun, seed=2, branch_from=0.42):
    """troncos e copas em duas malhas. keep(x, y) -> máscara de onde pode ter árvore"""
    rs = np.random.RandomState(seed)
    x = cx + (rs.rand(count) - .5) * spread; y = cy + (rs.rand(count) - .5) * spread
    ok = keep(x, y); x, y = x[ok], y[ok]
    z = hfun(x, y) - 0.2
    N = len(x)
    h = 24 + 16 * rs.rand(N); r = 0.32 + 0.5 * rs.rand(N)
    v, t = lathe([(1.25, 0), (1.0, 0.03), (0.8, 0.3), (0.5, 0.7), (0.05, 1)], 12)
    pos = np.stack([x, y, z], 1)
    scatter('trunks', v, t, pos, rs.rand(N) * 6.28, np.stack([r, r, h], 1), bark_mat())
    # copa: 12 saias pontudas, mais estreitas no topo
    vs, ts, off = [], [], 0
    for i in range(12):
        k = i / 11
        zc = branch_from + (1 - branch_from) * k
        rad = 0.13 * (1 - k) ** 0.85 + 0.012
        a, b = lathe([(rad, zc - 0.035), (rad * 0.5, zc + 0.015), (0.002, zc + 0.075)], 14)
        a = a.copy()
        sp = 1 - 0.42 * (np.arange(len(a)) % 2)      # pontas alternadas
        a[:, :2] *= sp[:, None]
        vs.append(a); ts.append(b + off); off += len(a)
    v = np.vstack(vs); t = np.vstack(ts)
    scatter('crowns', v, t, pos, rs.rand(N) * 6.28, np.stack([h, h, h], 1), needle_mat(), smooth=False)
    return x, y

def rocks(pts, sizes, m, seed=3):
    rnd = random.Random(seed)
    t = bpy.data.textures.new('rock', 'CLOUDS'); t.noise_scale = 0.5; t.noise_depth = 2
    for i, (p, s) in enumerate(zip(pts, sizes)):
        o = ico('rock', s, p, m, 4); o.scale = (1, rnd.uniform(.7, 1), rnd.uniform(.45, .7))
        o.rotation_euler.z = rnd.uniform(0, 6.28)
        d = o.modifiers.new('d', 'DISPLACE'); d.texture = t; d.strength = 0.5 * s

def rock_mat():
    m, nt = mat('rockm')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=1.8, Detail=7.0, Roughness=0.62); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.4, (0.13, 0.13, 0.12)), (0.56, (0.2, 0.2, 0.18)), (0.66, (0.06, 0.13, 0.04))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=1.0, Distance=0.1); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, 0.75, normal=bp.outputs[0]).outputs[0])
    return m

def overcast():
    world_flat((0.74, 0.80, 0.76), 1.5)

def build_p2a():
    s = reset(20)
    world_space((0.006, 0.014, 0.012), 1.0)
    sd = (-1.0, -0.6, 0.45)
    sun(4.5, sd, (1, 0.98, 0.94))
    p, c = planet_woods(1.0); atmosphere(1.0, (0.5, 0.75, 0.6), sd, 1.03)
    p.rotation_euler = c.rotation_euler = (0.35, -0.2, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, NAME_HOLD, SHOTS['p2a'])
        p.rotation_euler.z = 1.2 + 0.1 * t
        c.rotation_euler.z = 1.2 + 0.14 * t
        cam.location = vlerp((-0.3, -3.6, 0.15), (-0.12, -2.6, 0.05), ease(u))
        look(cam, (0, 0, 0))
    return update

def build_p2b():
    s = reset(18)
    overcast()
    sun(2.4, (-0.4, -0.3, 0.8), (1, 0.97, 0.88), 8.0)
    grid_mesh('terrain', 340, 300, soil, soil_mat(), (0, 90))
    path = lambda y: 1.8 * np.sin(y * 0.09)
    keep = lambda x, y: np.abs(x - path(y)) > 1.5
    pines(1500, 0, 90, 330, keep, soil)
    grass(0, 0, math.pi / 2, 60, 260000, soil, 3, 0.5, 2.2, FERN)
    pts = [(-3, 9, float(soil(np.array([-3.]), np.array([9.]))[0])), (4, 14, float(soil(np.array([4.]), np.array([14.]))[0])), (-5, 21, float(soil(np.array([-5.]), np.array([21.]))[0]))]
    rocks(pts, (0.9, 1.3, 1.1), rock_mat())
    fog((0.60, 0.68, 0.62), 5, 80, 0.85, 'LINEAR')
    cam = camera((0, 0, 2), (0, 20, 2), 28)
    def update(t, u):
        y = lerp(0, 5.5, u)
        x = float(path(np.array([y]))[0])
        z = float(soil(np.array([x]), np.array([y]))[0]) + 1.6 + 0.035 * math.sin(t * 7.2)
        cam.location = Vector((x, y, z)) + shake(t, 0.03, 1.4)
        tx = float(path(np.array([y + 12]))[0])
        look(cam, (tx + 0.4 * math.sin(t * 0.7), y + 12, z + 0.6), 0.012 * math.sin(t * 1.3))
    return update

def creek_x(y):
    return 3.5 * np.sin(y * 0.11) + 1.5 * np.sin(y * 0.27 + 2)

def creek(x, y):
    d = np.abs(x - creek_x(y))
    return -0.6 + np.clip((d - 1.0) / 2.0, 0, 1) * 1.0 + np.clip((d - 3) / 12, 0, 1) * 3 + soil(x, y) * np.clip((d - 3) / 10, 0, 1) * 0.6 + (fbm(x * 0.8, y * 0.8, 2) - 0.5) * 0.14

def water_mat():
    m, nt = mat('creekw')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    mp = n(nt, 'ShaderNodeMapping'); L(nt, pos, mp.inputs['Vector']); mp.inputs['Scale'].default_value = (2.5, 0.8, 1)
    a = n(nt, 'ShaderNodeTexNoise', Scale=1.6, Detail=4.0, Roughness=0.5); L(nt, mp.outputs[0], a.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.5, Distance=0.12); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, (0.03, 0.06, 0.055), 0.06, spec=0.8, normal=bp.outputs[0]).outputs[0])
    return m, mp

def build_p2c():
    s = reset(18)
    overcast()
    sun(2.6, (-0.5, 0.2, 0.7), (1, 0.97, 0.88), 8.0)
    grid_mesh('terrain', 240, 340, creek, soil_mat(), (0, 60))
    wm, mp = water_mat()
    box('water', (240, 240, 0.1), (0, 60, -0.34), wm)
    keep = lambda x, y: np.abs(x - creek_x(y)) > 5
    pines(900, 0, 60, 230, keep, creek, 5)
    rs = np.random.RandomState(4)
    ys = rs.rand(34) * 34 + 1
    xs = creek_x(ys) + (rs.rand(34) - .5) * 4.4
    pts = [(float(a), float(b), float(creek(np.array([a]), np.array([b]))[0]) + 0.1) for a, b in zip(xs, ys)]
    rocks(pts, list(0.2 + 0.5 * rs.rand(34)), rock_mat())
    grass(0, 0, math.pi / 2, 46, 180000, lambda x, y: creek(x, y) - 3 * (np.abs(x - creek_x(y)) < 2.3), 7, 0.5, 2.4, FERN)
    fog((0.60, 0.68, 0.62), 6, 80, 0.85, 'LINEAR')
    cam = camera((0, 0, 1), (0, 10, 0), 30)
    def update(t, u):
        mp.inputs['Location'].default_value = (0, t * 2.2, 0)
        y = lerp(-1, 3.5, u)
        x = float(creek_x(np.array([y]))[0]) + 0.4
        cam.location = Vector((x, y, 0.72)) + shake(t, 0.012, 1.2)
        tx = float(creek_x(np.array([y + 9]))[0])
        look(cam, (tx, y + 9, 0.35))
    return update

def build_p2d():
    s = reset(20)
    world_flat((0.006, 0.010, 0.02), 1.0)
    flat = lambda x, y: soil(x, y) * np.clip((np.hypot(x, y - 6) - 4) / 10, 0, 1)
    grid_mesh('terrain', 200, 240, flat, soil_mat(), (0, 40))
    keep = lambda x, y: np.hypot(x, y - 6) > 4.5
    pines(900, 0, 40, 190, keep, flat, 8)
    grass(0, -1, math.pi / 2, 30, 90000, lambda x, y: flat(x, y) - 3 * (np.hypot(x, y - 6) < 3.2) - 3 * (np.hypot(x, y - 1) < 2.0), 11, 0.4, 2.8, FERN)
    bark = bark_mat()
    c = (0, 6, 0.0)
    for a in (0.2, 1.3, 2.4):
        dx, dy = math.cos(a) * 0.65, math.sin(a) * 0.65
        tube('log', [(c[0] - dx, c[1] - dy, 0.08), (c[0], c[1], 0.18), (c[0] + dx, c[1] + dy, 0.08)], [.085, .08, .07], bark)
    rm = rock_mat()
    rocks([(0.9 * math.cos(a), 6 + 0.9 * math.sin(a), 0.03) for a in np.linspace(0, 6.28, 12, endpoint=False)], [0.15] * 12, rm)
    # galhos encostados: abrigo improvisado
    for i in range(9):
        x = -2.5 + i * 0.25
        tube('lean', [(x, 7.5, 0.0), (x + 0.03, 8.4, 1.0), (x, 9.0, 1.7)], [.04, .035, .03], bark)
    flame = emission('flame2', (1.0, 0.22, 0.02), 2.2)
    mid = emission('mid', (1.0, 0.45, 0.05), 3.2)
    core = emission('core', (1.0, 0.78, 0.28), 5)
    drop = [(0.0, 0.0), (0.7, 0.08), (1.0, 0.22), (0.72, 0.5), (0.3, 0.8), (0.0, 1.0)]
    fl = []
    rnd = random.Random(6)
    tongues = [(0, 0, 1.15, .24, flame), (.05, .02, .8, .17, mid), (-.04, 0, .5, .11, core)]
    for i in range(10):
        a_ = i * 2.4; rr = rnd.uniform(.1, .34)
        tongues.append((rr * math.cos(a_), rr * math.sin(a_), rnd.uniform(.4, 1.0) * (1 - rr), rnd.uniform(.07, .13), flame if i % 3 else mid))
    for i, (dx, dy, h, r, m_) in enumerate(tongues):
        v, t = lathe(drop, 16)
        o = fast_mesh('fl', v, t, m_, True); o.location = (dx, 6 + dy, 0.12); o.scale = (r, r, h)
        fl.append((o, i * 1.7, r, h))
    lt = point((0, 6, 0.95), 260, (1, 0.48, 0.14), 0.25)
    fog((0.012, 0.016, 0.028), 6, 40, 0.9, 'LINEAR')
    cam = camera((0, 0, 1.3), (0, 6, 0.6), 30)
    def update(t, u):
        f = 0.75 + 0.25 * math.sin(t * 13) * math.sin(t * 7.3 + 1)
        lt.data.energy = 260 * f
        for o, ph, r, h in fl:
            k = 1 + 0.22 * math.sin(t * 15 + ph)
            w = r * (1 - 0.12 * math.sin(t * 11 + ph))
            o.scale = (w, w, h * k)
        cam.location = vlerp((0.6, 2.7, 1.15), (0.15, 1.3, 1.35), ease(u))
        look(cam, (0, 6, 0.7))
    return update
