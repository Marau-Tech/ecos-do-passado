from lib import *

def maze_image(cells=64, px=4, seed=3):
    """labirinto real (DFS) em tile contínuo"""
    rnd = random.Random(seed)
    W = cells * px
    img = np.zeros((W, W), np.float32)          # 1 = corredor
    seen = np.zeros((cells, cells), bool)
    st = [(0, 0)]; seen[0, 0] = True
    wall = max(1, px // 4)
    def carve(x, y, dx, dy):
        x0, y0 = x * px + wall, y * px + wall
        img[y0:y0 + px - wall, x0:x0 + px - wall] = 1
        if dx == 1:
            for k in range(px):
                img[y0:y0 + px - wall, (x0 + k) % W] = 1
        if dx == -1:
            for k in range(px):
                img[y0:y0 + px - wall, (x0 - k) % W] = 1
        if dy == 1:
            for k in range(px):
                img[(y0 + k) % W, x0:x0 + px - wall] = 1
        if dy == -1:
            for k in range(px):
                img[(y0 - k) % W, x0:x0 + px - wall] = 1
    while st:
        x, y = st[-1]
        nb = [(dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if not seen[(y + dy) % cells, (x + dx) % cells]]
        if not nb:
            st.pop(); continue
        dx, dy = rnd.choice(nb)
        carve(x, y, dx, dy)
        x2, y2 = (x + dx) % cells, (y + dy) % cells
        carve(x2, y2, 0, 0)
        seen[y2, x2] = True
        st.append((x2, y2))
    rgba = np.ones((W, W, 4), np.float32)
    rgba[..., 0] = rgba[..., 1] = rgba[..., 2] = img
    path = f'{RENDER}/_maze.png'
    if not os.path.exists(path):
        im = bpy.data.images.new('maze0', W, W, alpha=False)
        im.pixels.foreach_set(rgba.ravel()); im.update()
        im.filepath_raw = path; im.file_format = 'PNG'; im.save()
    im = bpy.data.images.load(path)
    im.colorspace_settings.name = 'Non-Color'
    return im

def planet_maze(r=1.0, loc=(0, 0, 0)):
    m, nt = mat('maze')
    im = maze_image(96, 8)
    tc = n(nt, 'ShaderNodeTexCoord')
    def layer(scale):
        mp = n(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale,) * 3
        L(nt, tc.outputs['Object'], mp.inputs['Vector'])
        t = n(nt, 'ShaderNodeTexImage', {'image': im, 'projection': 'BOX', 'projection_blend': 0.15,
                                         'extension': 'REPEAT', 'interpolation': 'Closest'})
        L(nt, mp.outputs[0], t.inputs['Vector'])
        return t.outputs[0]
    big = layer(0.085); fine = layer(0.7)
    cor = math_(nt, 'MULTIPLY', big, math_(nt, 'ADD', math_(nt, 'MULTIPLY', fine, 0.45), 0.55))
    dirt = n(nt, 'ShaderNodeTexNoise', Scale=3.0, Detail=9.0, Roughness=0.62)
    L(nt, tc.outputs['Object'], dirt.inputs['Vector'])
    dr = ramp(nt, [(0.38, (0.42, 0.26, 0.03)), (0.62, (0.95, 0.68, 0.08))], dirt.outputs['Fac'])
    col = mix(nt, cor, (0.05, 0.035, 0.012), dr.outputs[0])
    bp = n(nt, 'ShaderNodeBump', Strength=0.9, Distance=0.05)
    L(nt, math_(nt, 'SUBTRACT', 1.0, cor), bp.inputs['Height'])
    # luz fluorescente vazando dos corredores no lado escuro
    em = math_(nt, 'MULTIPLY', cor, 1.0)
    p = principled(nt, col, 0.8, normal=bp.outputs[0], emis=(1.0, 0.86, 0.45), emis_str=0.0)
    L(nt, math_(nt, 'MULTIPLY', em, 0.05), p.inputs['Emission Strength'])
    out(nt, p.outputs[0])
    return sphere('p_maze', r, loc, m, 192, 96)

def planet_green(r=1.0, loc=(0, 0, 0)):
    m, nt = mat('green')
    tc = n(nt, 'ShaderNodeTexCoord')
    nz = n(nt, 'ShaderNodeTexNoise', Scale=1.5, Detail=12.0, Roughness=0.58)
    L(nt, tc.outputs['Object'], nz.inputs['Vector'])
    h = nz.outputs['Fac']
    land = ramp(nt, [(0.505, (0.02, 0.33, 0.06)), (0.60, (0.16, 0.55, 0.11)),
                     (0.68, (0.55, 0.50, 0.22)), (0.76, (0.92, 0.92, 0.9))], h).outputs[0]
    sea = ramp(nt, [(0.30, (0.01, 0.06, 0.28)), (0.5, (0.04, 0.34, 0.62))], h).outputs[0]
    isl = math_(nt, 'GREATER_THAN', h, 0.5)
    col = mix(nt, isl, sea, land)
    sep = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Object'], sep.inputs[0])
    z = math_(nt, 'ABSOLUTE', sep.outputs['Z'])
    ice = math_(nt, 'GREATER_THAN', math_(nt, 'ADD', z, math_(nt, 'MULTIPLY', h, 0.25)), 1.0)
    col = mix(nt, ice, col, (0.95, 0.97, 1.0))
    rough = math_(nt, 'ADD', math_(nt, 'MULTIPLY', isl, 0.6), 0.25)
    bp = n(nt, 'ShaderNodeBump', Strength=0.4, Distance=0.05)
    L(nt, math_(nt, 'MULTIPLY', h, isl), bp.inputs['Height'])
    out(nt, principled(nt, col, rough, normal=bp.outputs[0]).outputs[0])
    o = sphere('p_green', r, loc, m, 192, 96)
    # nuvens
    cm, cn = mat('clouds')
    t2 = n(cn, 'ShaderNodeTexCoord')
    mp = n(cn, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 1, 2.2)
    L(cn, t2.outputs['Object'], mp.inputs['Vector'])
    nc = n(cn, 'ShaderNodeTexNoise', Scale=2.6, Detail=13.0, Roughness=0.62, Distortion=0.5)
    L(cn, mp.outputs[0], nc.inputs['Vector'])
    a = ramp(cn, [(0.5, (0, 0, 0)), (0.66, (1, 1, 1))], nc.outputs['Fac']).outputs[0]
    d = n(cn, 'ShaderNodeBsdfDiffuse'); d.inputs['Color'].default_value = (1, 1, 1, 1)
    tr = n(cn, 'ShaderNodeBsdfTransparent')
    ms = n(cn, 'ShaderNodeMixShader')
    L(cn, a, ms.inputs[0]); L(cn, tr.outputs[0], ms.inputs[1]); L(cn, d.outputs[0], ms.inputs[2])
    out(cn, ms.outputs[0])
    c = sphere('clouds', r * 1.012, loc, cm, 128, 64)
    return o, c

def planet_night(r=1.0, loc=(0, 0, 0)):
    m, nt = mat('night')
    tc = n(nt, 'ShaderNodeTexCoord')
    nz = n(nt, 'ShaderNodeTexNoise', Scale=4.0, Detail=12.0, Roughness=0.62)
    L(nt, tc.outputs['Object'], nz.inputs['Vector'])
    col = ramp(nt, [(0.3, (0.012, 0.014, 0.022)), (0.6, (0.10, 0.11, 0.15)), (0.8, (0.2, 0.2, 0.25))], nz.outputs['Fac']).outputs[0]
    warp = n(nt, 'ShaderNodeVectorMath', {'operation': 'ADD'})
    L(nt, tc.outputs['Object'], warp.inputs[0])
    nv = n(nt, 'ShaderNodeTexNoise', Scale=3.0, Detail=4.0)
    L(nt, tc.outputs['Object'], nv.inputs['Vector'])
    sc = n(nt, 'ShaderNodeVectorMath', {'operation': 'SCALE'}); sc.inputs['Scale'].default_value = 0.35
    L(nt, nv.outputs['Color'], sc.inputs[0]); L(nt, sc.outputs[0], warp.inputs[1])
    v = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=3.2)
    L(nt, warp.outputs[0], v.inputs['Vector'])
    crack = math_(nt, 'LESS_THAN', v.outputs['Distance'], 0.007)
    bp = n(nt, 'ShaderNodeBump', Strength=1.0, Distance=0.1)
    L(nt, nz.outputs['Fac'], bp.inputs['Height'])
    p = principled(nt, col, 0.9, normal=bp.outputs[0], emis=(1.0, 0.06, 0.02), emis_str=0)
    L(nt, math_(nt, 'MULTIPLY', crack, 0.3), p.inputs['Emission Strength'])
    out(nt, p.outputs[0])
    return sphere('p_night', r, loc, m, 192, 96)

def flesh_material(name='flesh', scale=1.0, emis=0.35):
    m, nt = mat(name)
    tc = n(nt, 'ShaderNodeTexCoord')
    mp = n(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale,) * 3
    L(nt, tc.outputs['Object'], mp.inputs['Vector'])
    co = mp.outputs[0]
    nw = n(nt, 'ShaderNodeTexNoise', Scale=3.0, Detail=5.0)
    L(nt, co, nw.inputs['Vector'])
    sc = n(nt, 'ShaderNodeVectorMath', {'operation': 'SCALE'}); sc.inputs['Scale'].default_value = 0.55
    L(nt, nw.outputs['Color'], sc.inputs[0])
    wp = n(nt, 'ShaderNodeVectorMath', {'operation': 'ADD'})
    L(nt, co, wp.inputs[0]); L(nt, sc.outputs[0], wp.inputs[1])
    v1 = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=2.2)
    L(nt, wp.outputs[0], v1.inputs['Vector'])
    v2 = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=7.0)
    L(nt, wp.outputs[0], v2.inputs['Vector'])
    vein1 = ramp(nt, [(0.0, (1, 1, 1)), (0.05, (0, 0, 0))], v1.outputs['Distance']).outputs[0]
    vein2 = ramp(nt, [(0.0, (0.6, 0.6, 0.6)), (0.03, (0, 0, 0))], v2.outputs['Distance']).outputs[0]
    vein = math_(nt, 'MAXIMUM', vein1, vein2)
    nz = n(nt, 'ShaderNodeTexNoise', Scale=6.0, Detail=10.0, Roughness=0.6)
    L(nt, wp.outputs[0], nz.inputs['Vector'])
    base = ramp(nt, [(0.32, (0.13, 0.008, 0.015)), (0.5, (0.50, 0.06, 0.07)),
                     (0.68, (0.82, 0.32, 0.30))], nz.outputs['Fac']).outputs[0]
    col = mix(nt, vein, base, (0.05, 0.0, 0.05))
    bp = n(nt, 'ShaderNodeBump', Strength=1.0, Distance=0.12)
    L(nt, math_(nt, 'ADD', nz.outputs['Fac'], math_(nt, 'MULTIPLY', vein, 0.7)), bp.inputs['Height'])
    p = principled(nt, col, 0.32, spec=0.7, normal=bp.outputs[0], emis=(0.9, 0.05, 0.03), emis_str=0)
    L(nt, math_(nt, 'MULTIPLY', vein, emis), p.inputs['Emission Strength'])
    out(nt, p.outputs[0])
    return m

def planet_flesh(r=1.0, loc=(0, 0, 0)):
    m = flesh_material('flesh_planet', 1.0, 0.45)
    o = sphere('p_flesh', r, loc, m, 320, 160)
    t = bpy.data.textures.new('cl', 'CLOUDS'); t.noise_scale = 0.42; t.noise_depth = 2
    d = o.modifiers.new('d', 'DISPLACE'); d.texture = t; d.strength = 0.16 * r; d.mid_level = 0.5
    d.texture_coords = 'LOCAL'
    return o

def iris_material(name='iris', color=(0.9, 0.75, 0.1), pupil=0.13, glow=0.6, slit=1.0):
    """olho apontado para +Y local; íris por distância radial no plano XZ"""
    m, nt = mat(name)
    tc = n(nt, 'ShaderNodeTexCoord')
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Object'], sp.inputs[0])
    def radial(k):
        xs = math_(nt, 'MULTIPLY', sp.outputs['X'], k)
        return math_(nt, 'SQRT', math_(nt, 'ADD', math_(nt, 'MULTIPLY', xs, xs),
                                       math_(nt, 'MULTIPLY', sp.outputs['Z'], sp.outputs['Z'])))
    rad = radial(1.0); radp = radial(slit)
    front = math_(nt, 'GREATER_THAN', sp.outputs['Y'], 0.0)
    ang = math_(nt, 'ARCTAN2', sp.outputs['Z'], sp.outputs['X'])
    fib = n(nt, 'ShaderNodeTexNoise', Scale=7.0, Detail=5.0)
    cv = n(nt, 'ShaderNodeCombineXYZ'); L(nt, ang, cv.inputs['X'])
    L(nt, math_(nt, 'MULTIPLY', rad, 0.6), cv.inputs['Y'])
    L(nt, cv.outputs[0], fib.inputs['Vector'])
    icol = ramp(nt, [(0.3, tuple(c * 0.25 for c in color)), (0.65, color)], fib.outputs['Fac']).outputs[0]
    # esclera com vasos
    nv = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=3.0)
    nw2 = n(nt, 'ShaderNodeTexNoise', Scale=2.5, Detail=4.0)
    L(nt, tc.outputs['Object'], nw2.inputs['Vector'])
    L(nt, nw2.outputs['Color'], nv.inputs['Vector'])
    vv = ramp(nt, [(0.0, (0.8, 0.8, 0.8)), (0.014, (0, 0, 0))], nv.outputs['Distance']).outputs[0]
    scl = mix(nt, vv, (0.74, 0.64, 0.46), (0.55, 0.03, 0.03))
    is_iris = math_(nt, 'MULTIPLY', math_(nt, 'LESS_THAN', rad, 0.46), front)
    is_pup = math_(nt, 'MULTIPLY', math_(nt, 'LESS_THAN', radp, pupil * 3), front)
    col = mix(nt, is_iris, scl, icol)
    col = mix(nt, is_pup, col, (0.0, 0.0, 0.0))
    p = principled(nt, col, 0.12, spec=0.8, emis=(1, 1, 1), emis_str=0)
    em = math_(nt, 'MULTIPLY', is_iris, math_(nt, 'SUBTRACT', 1.0, is_pup))
    L(nt, icol, p.inputs['Emission Color'])
    L(nt, math_(nt, 'MULTIPLY', em, glow), p.inputs['Emission Strength'])
    out(nt, p.outputs[0])
    return m
