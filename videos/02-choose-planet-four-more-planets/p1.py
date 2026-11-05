from lib import *
from planets import *
from nature import tree
from timeline import NAME_HOLD

SHOTS = {'p1a': 6.0, 'p1b': 3.75, 'p1c': 3.5, 'p1d': 4.0}

def sky_gold():
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    g = ramp(nt, [(0.0, (1.0, 0.72, 0.42)), (0.12, (1.0, 0.62, 0.45)), (0.45, (0.62, 0.48, 0.72)), (0.9, (0.28, 0.32, 0.62))], sp.outputs['Z']).outputs[0]
    b = n(nt, 'ShaderNodeBackground', Strength=1.0); L(nt, g, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])

def tasty(name, color, rough=0.35, bump=0.3, scale=18.0, color2=None):
    m, nt = mat(name)
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=scale, Detail=6.0, Roughness=0.6); L(nt, tc, a.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=bump, Distance=0.04); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    c = ramp(nt, [(0.35, color), (0.65, color2 or color)], a.outputs['Fac']).outputs[0]
    out(nt, principled(nt, c, rough, normal=bp.outputs[0]).outputs[0])
    return m

def lathe_obj(name, prof, m, sides=32, loc=(0, 0, 0)):
    v, t = lathe(prof, sides)
    o = fast_mesh(name, v, t, m, True); o.location = loc
    return o

def food_kit():
    """pratos protótipo: cada um é uma lista de objetos para clone()"""
    plate_m = simple('plate', (0.92, 0.90, 0.85), 0.2)
    gold = simple('goldm', (0.9, 0.62, 0.2), 0.3, metal=0.9)
    frost = tasty('frost', (0.95, 0.55, 0.62), 0.3, 0.2, 9.0, (0.98, 0.72, 0.76))
    choco = tasty('choco', (0.09, 0.035, 0.015), 0.25, 0.2, 9.0)
    crust = tasty('crust', (0.72, 0.40, 0.12), 0.5, 0.8, 14.0, (0.42, 0.18, 0.05))
    roast = tasty('roast', (0.42, 0.17, 0.04), 0.28, 0.7, 7.0, (0.70, 0.36, 0.09))
    bread = tasty('bread', (0.80, 0.52, 0.22), 0.65, 0.9, 11.0, (0.55, 0.28, 0.08))
    red = simple('apple', (0.65, 0.03, 0.04), 0.22)
    grape = simple('grape', (0.18, 0.04, 0.28), 0.18)
    plate_p = [(0.0, 0.0), (0.26, 0.0), (0.30, 0.03), (0.0, 0.03)]
    plate = lambda: lathe_obj('plate', [(0, 0.03), (0.2, 0.03), (0.32, 0.055), (0.33, 0.045), (0.2, 0.0), (0, 0.0)], plate_m)
    kit = []
    # bolo
    a = plate()
    b = lathe_obj('cake', [(0, 0.05), (0.22, 0.05), (0.23, 0.3), (0.2, 0.33), (0, 0.33)], frost)
    c = ico('cherry', 0.045, (0, 0, 0.37), red, 2)
    kit.append([a, b, c])
    # torta
    a = plate()
    b = lathe_obj('pie', [(0, 0.05), (0.27, 0.05), (0.29, 0.11), (0.25, 0.14), (0, 0.13)], crust)
    kit.append([a, b])
    # assado
    a = plate()
    b = ico('roast', 0.2, (0, 0, 0.2), roast, 3); b.scale = (1.25, 0.95, 0.8)
    l1 = tube('leg', [(0.2, 0.1, 0.17), (0.32, 0.17, 0.2), (0.42, 0.2, 0.26)], [.07, .05, .02], roast)
    l2 = tube('leg', [(0.2, -0.1, 0.17), (0.32, -0.17, 0.2), (0.42, -0.2, 0.26)], [.07, .05, .02], roast)
    kit.append([a, b, l1, l2])
    # pão
    a = plate()
    b = ico('bread', 0.17, (0, 0, 0.16), bread, 3); b.scale = (1.55, 0.9, 0.72)
    c = ico('bread2', 0.11, (-0.1, 0.17, 0.12), bread, 3); c.scale = (1.3, 0.9, 0.8)
    kit.append([a, b, c])
    # frutas
    a = lathe_obj('bowl', [(0, 0.02), (0.14, 0.02), (0.26, 0.15), (0.28, 0.15), (0.16, 0.0), (0, 0.0)], gold)
    fr = [a]
    for i, (x, y, z) in enumerate(((0, 0, .24), (.11, .05, .17), (-.1, .07, .17), (.02, -.12, .17), (-.08, -.07, .19), (.1, -.08, .19))):
        fr.append(ico('f', 0.075, (x, y, z), red if i % 2 else grape, 2))
    kit.append(fr)
    # calda de chocolate
    a = plate()
    b = lathe_obj('tower', [(0, 0.05), (0.2, 0.05), (0.2, 0.15), (0.14, 0.17), (0.14, 0.27), (0.08, 0.29), (0.08, 0.38), (0, 0.4)], choco)
    kit.append([a, b])
    # taça
    a = lathe_obj('goblet', [(0, 0), (0.07, 0), (0.02, 0.03), (0.018, 0.16), (0.08, 0.2), (0.085, 0.31), (0.075, 0.31), (0.07, 0.22), (0, 0.2)], gold, 16)
    kit.append([a])
    # vela
    wax = simple('wax', (0.95, 0.9, 0.8), 0.4)
    fl = emission('flame', (1.0, 0.65, 0.2), 16)
    a = lathe_obj('candle', [(0, 0), (0.025, 0), (0.025, 0.34), (0, 0.34)], wax, 10)
    b = ico('fl', 0.024, (0, 0, 0.385), fl, 2); b.scale = (0.7, 0.7, 1.7)
    kit.append([a, b])
    all_o = [o for g in kit for o in g]
    hide(all_o)
    return kit

def table(length=340, y0=-6, width=2.2, height=0.9, chairs=True, seed=2, clear=None):
    cloth = tasty('cloth', (0.93, 0.90, 0.84), 0.75, 0.2, 40.0)
    box('table', (width, length, height), (0, y0 + length / 2, height / 2), cloth)
    box('runner', (0.8, length, 0.008), (0, y0 + length / 2, height + 0.004), simple('run', (0.55, 0.05, 0.08), 0.6))
    kit = food_kit()
    rnd = random.Random(seed)
    y = y0 + 0.2
    while y < y0 + length:
        near = y < 26
        for x in (-0.68, 0.0, 0.68):
            if not near and rnd.random() < 0.3: continue
            if clear and clear[0] < y < clear[1]: continue
            g = kit[rnd.randrange(6)] if x == 0 or rnd.random() < 0.72 else kit[rnd.choice((6, 7))]
            clone(g, (x + rnd.uniform(-.06, .06), y + rnd.uniform(-.12, .12), height + 0.01), rnd.uniform(0, 6.28), rnd.uniform(0.95, 1.2))
        y += 0.8 if near else 1.25
    if chairs:
        wood = tasty('wood', (0.28, 0.12, 0.05), 0.4, 0.3, 24.0)
        v1, t1 = lathe([(0.3, 0.45), (0.3, 0.5)], 4)
        back = box('bk', (0.5, 0.06, 0.8), (0, 0.27, 0.9), wood)
        seat = box('st', (0.5, 0.5, 0.06), (0, 0, 0.5), wood)
        legs = [box('lg', (0.05, 0.05, 0.5), (x, y, 0.25), wood) for x in (-.21, .21) for y in (-.21, .21)]
        proto = [back, seat] + legs
        hide(proto)
        y = y0 + 1.0
        while y < min(y0 + length, 120):
            clone(proto, (-width / 2 - 0.42, y, 0), -math.pi / 2)
            clone(proto, (width / 2 + 0.42, y, 0), math.pi / 2)
            y += 1.6

def dunes(x, y):
    return (fbm(x * 0.02 + 4, y * 0.02, 4) - 0.5) * 10 + (fbm(x * 0.2, y * 0.2, 3) - 0.5) * 0.25

def frosting_ground():
    m, nt = mat('fground')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.12, Detail=6.0, Roughness=0.55); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.38, (0.96, 0.72, 0.48)), (0.55, (0.92, 0.50, 0.46)), (0.68, (0.82, 0.46, 0.16))], a.outputs['Fac']).outputs[0]
    w = n(nt, 'ShaderNodeTexWave', {'wave_type': 'BANDS'}, Scale=0.6, Distortion=6.0, Detail=3.0); L(nt, pos, w.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.5, Distance=0.3); L(nt, w.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, 0.34, spec=0.6, normal=bp.outputs[0]).outputs[0])
    return m

def honey_mat():
    m, nt = mat('honey')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    mp = n(nt, 'ShaderNodeMapping'); L(nt, pos, mp.inputs['Vector']); mp.inputs['Scale'].default_value = (1, 0.35, 1)
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.45, Detail=5.0, Roughness=0.5); L(nt, mp.outputs[0], a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.75, 0.30, 0.02)), (0.65, (1.0, 0.62, 0.08))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=0.5, Distance=0.25); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, 0.12, spec=0.7, normal=bp.outputs[0], emis=(1.0, 0.45, 0.05), emis_str=0.25).outputs[0])
    return m, mp

def build_p1a():
    s = reset(20)
    world_space((0.03, 0.015, 0.02), 1.0)
    sd = (-1.0, -0.7, 0.4)
    sun(4.2, sd, (1, 0.96, 0.9))
    p = planet_feast(1.0); atmosphere(1.0, (1.0, 0.7, 0.55), sd, 1.04, power=4, strength=1.0)
    p.rotation_euler = (0.35, -0.2, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, NAME_HOLD, SHOTS['p1a'])
        p.rotation_euler.z = 0.8 + 0.12 * t
        cam.location = vlerp((0.3, -3.6, 0.2), (0.12, -2.5, 0.05), ease(u))
        look(cam, (0.05, 0, 0))
    return update

def build_p1b():
    s = reset(18)
    sky_gold()
    sun(3.2, (-0.5, -0.7, 0.32), (1, 0.82, 0.6), 3.0)
    grid_mesh('terrain', 900, 240, lambda x, y: dunes(x, y) * np.clip(np.abs(x) / 30, 0, 1) - 0.02, frosting_ground(), (0, 150))
    table()
    fog((1.0, 0.70, 0.48), 25, 300, 0.6, 'LINEAR')
    cam = camera((0, -3.5, 1.55), (0, 30, 0.9), 30)
    def update(t, u):
        cam.location = vlerp((0.0, -4.2, 1.72), (0.0, 1.6, 1.42), ease(u)) + shake(t, 0.006, 2.0)
        look(cam, (0, 40, 0.75))
    return update

def river_x(y):
    return 7 * np.sin(y * 0.035) + 3 * np.sin(y * 0.09 + 1)

def valley(x, y):
    d = np.abs(x - river_x(y))
    bank = np.clip((d - 5) / 18, 0, 1)
    return -0.8 + np.clip((d - 2.5) / 2.5, 0, 1) * 1.1 + bank * bank * 16 + dunes(x, y) * bank * 0.7

def build_p1c():
    s = reset(18)
    sky_gold()
    sun(3.4, (-0.6, 0.4, 0.42), (1, 0.84, 0.62), 3.0)
    grid_mesh('terrain', 420, 300, valley, frosting_ground(), (0, 130))
    hm, mp = honey_mat()
    box('honey', (420, 420, 0.1), (0, 130, -0.1), hm)
    bun = tasty('bun', (0.9, 0.6, 0.2), 0.3, 0.6, 16.0, (0.62, 0.32, 0.08))
    rnd = random.Random(4)
    for i, (dx, y) in enumerate(((-12, 26), (13, 38), (-15, 60), (17, 76), (-20, 104))):
        x = float(river_x(np.array([y]))[0]) + dx
        z = float(valley(np.array([x]), np.array([float(y)]))[0])
        root, blobs = tree((x, y, z - 0.2), 1.7, i + 3)
        for (bx, by, bz), r in blobs[::2]:
            for k in range(3):
                a = rnd.uniform(0, 6.28)
                f = ico('bun', 0.16, (bx + r * math.cos(a), by + r * math.sin(a), bz - 0.3 * r), bun, 2); f.parent = root
    fog((1.0, 0.70, 0.48), 30, 240, 0.55, 'LINEAR')
    cam = camera((0, 0, 2.5), (0, 30, 0), 30)
    def update(t, u):
        mp.inputs['Location'].default_value = (0, -t * 0.8, 0)
        y = lerp(4, 17, u)
        x = float(river_x(np.array([y]))[0])
        cam.location = (x, y, 1.9 + 0.2 * math.sin(t * 0.8))
        xa = float(river_x(np.array([y + 34]))[0])
        look(cam, (xa, y + 34, 1.2))
    return update

def sector(R, H, a0, a1, seg=48, top=True, side=True, cut=True, z0=0.0):
    """fatia de cilindro entre os ângulos a0 e a1, com origem no eixo"""
    a = np.linspace(a0, a1, seg + 1)
    ring = lambda r, z: np.stack([r * np.cos(a), r * np.sin(a), np.full_like(a, z)], 1)
    v = [ring(R, z0), ring(R, H)]
    n0 = seg + 1
    c0 = 2 * n0; c1 = c0 + 1
    verts = np.vstack(v + [[[0, 0, z0], [0, 0, H]]])
    t = []
    for i in range(seg):
        if side: t += [(i, i + 1, n0 + i + 1), (i, n0 + i + 1, n0 + i)]
        if top: t += [(n0 + i, n0 + i + 1, c1)]
    if cut:
        t += [(c0, 0, n0), (c0, n0, c1), (seg, c0, c1), (seg, c1, n0 + seg)]
    return verts, np.array(t)

def layered():
    m, nt = mat('sponge')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc, sp.inputs[0])
    bands = ramp(nt, [(0.0, (0.86, 0.60, 0.26)), (0.30, (0.86, 0.60, 0.26)), (0.31, (0.98, 0.92, 0.82)), (0.40, (0.98, 0.92, 0.82)),
                      (0.41, (0.70, 0.08, 0.12)), (0.47, (0.70, 0.08, 0.12)), (0.48, (0.86, 0.60, 0.26)), (0.74, (0.86, 0.60, 0.26)),
                      (0.75, (0.98, 0.92, 0.82)), (0.85, (0.98, 0.92, 0.82)), (0.86, (0.86, 0.60, 0.26))],
                 math_(nt, 'DIVIDE', sp.outputs['Z'], 0.72))
    a = n(nt, 'ShaderNodeTexNoise', Scale=60.0, Detail=5.0, Roughness=0.7); L(nt, tc, a.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.8, Distance=0.02); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, bands.outputs[0], 0.7, normal=bp.outputs[0]).outputs[0])
    return m

def build_p1d():
    s = reset(20)
    sky_gold()
    sun(1.4, (-0.5, -0.7, 0.45), (1, 0.84, 0.64), 4.0)
    grid_mesh('terrain', 900, 120, lambda x, y: dunes(x, y) * np.clip(np.abs(x) / 30, 0, 1) - 0.02, frosting_ground(), (0, 150))
    table(y0=-4, seed=5, clear=(-5, 2.1))
    H0 = 0.91
    sponge = layered()
    ice = tasty('ice', (0.90, 0.42, 0.50), 0.26, 0.2, 12.0, (0.92, 0.48, 0.56))
    plate = lathe_obj('bigplate', [(0, 0.03), (0.62, 0.03), (0.8, 0.07), (0.81, 0.06), (0.6, 0.0), (0, 0.0)], simple('pl', (0.92, 0.90, 0.85), 0.2), 64, (0, 0.55, H0 + 0.02))
    R, H = 0.55, 0.72
    w0, w1 = -2.05, -0.95          # fatia voltada para a câmera
    base = H0 + 0.05
    v, t = sector(R, H, w1, w0 + 2 * math.pi, 96)
    body = fast_mesh('cake', v, t, sponge); body.location = (0, 0.55, base)
    v, t = sector(R + 0.018, H + 0.018, w1, w0 + 2 * math.pi, 96, cut=False)
    shell = fast_mesh('shell', v, t, ice, True); shell.location = (0, 0.55, base)
    wd = bpy.data.objects.new('wedge', None); link(wd); wd.location = (0, 0.55, base)
    v, t = sector(R, H, w0, w1, 24)
    a = fast_mesh('w', v, t, sponge); a.parent = wd
    v, t = sector(R + 0.018, H + 0.018, w0, w1, 24, cut=False)
    b = fast_mesh('ws', v, t, ice, True); b.parent = wd
    red = simple('cherry', (0.65, 0.02, 0.05), 0.18)
    for i in range(10):
        an = i * 2 * math.pi / 10 + 0.3
        p = ico('ch', 0.055, (0.42 * math.cos(an), 0.42 * math.sin(an), H + 0.06), red, 3)
        if w0 < (an + math.pi) % (2 * math.pi) - math.pi < w1:
            p.parent = wd
        else:
            p.parent = body
    fog((1.0, 0.70, 0.48), 8, 120, 0.6, 'LINEAR')
    point((1.0, -1.0, 2.4), 8, (1, 0.8, 0.55), 0.6)
    cam = camera((0, -1.9, 1.9), (0, 0.5, 1.3), 38)
    def update(t, u):
        k = ease(min(1, t / 2.0))
        sc = 0.03 + 0.97 * k
        wd.scale = (sc, sc, 1)
        cam.location = vlerp((0.3, -2.1, 1.95), (0.12, -1.55, 1.78), ease(u))
        look(cam, (0, 0.5, 1.26))
    return update
