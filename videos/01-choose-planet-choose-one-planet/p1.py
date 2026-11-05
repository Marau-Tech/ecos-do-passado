from lib import *
from planets import *

SHOTS = {'p1a': 3.75, 'p1b': 3.75, 'p1c': 3.5, 'p1d': 4.0}
H = 2.7           # pé-direito
CELL = 4.0        # módulo da grade

def wallpaper():
    m, nt = mat('wall')
    tc = n(nt, 'ShaderNodeTexCoord')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    sep = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, pos, sep.inputs[0])
    h = math_(nt, 'ADD', sep.outputs['X'], sep.outputs['Y'])
    # listras + losangos discretos do papel de parede
    st = math_(nt, 'SINE', math_(nt, 'MULTIPLY', h, 21.0))
    st = math_(nt, 'GREATER_THAN', st, 0.2)
    dz = math_(nt, 'SINE', math_(nt, 'MULTIPLY', math_(nt, 'ADD', h, sep.outputs['Z']), 12.0))
    dz2 = math_(nt, 'SINE', math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', h, sep.outputs['Z']), 12.0))
    dm = math_(nt, 'GREATER_THAN', math_(nt, 'MULTIPLY', dz, dz2), 0.55)
    base = mix(nt, st, (0.80, 0.63, 0.14), (0.70, 0.54, 0.11))
    base = mix(nt, dm, base, (0.60, 0.45, 0.09))
    nz = n(nt, 'ShaderNodeTexNoise', Scale=0.9, Detail=9.0, Roughness=0.62)
    L(nt, pos, nz.inputs['Vector'])
    stain = ramp(nt, [(0.45, (1, 1, 1)), (0.68, (0.42, 0.33, 0.2))], nz.outputs['Fac']).outputs[0]
    # umidade subindo do rodapé
    damp = ramp(nt, [(0.0, (0.3, 0.24, 0.13)), (0.3, (1, 1, 1))], math_(nt, 'MULTIPLY', sep.outputs['Z'], math_(nt, 'ADD', 0.6, math_(nt, 'MULTIPLY', nz.outputs['Fac'], 0.8)))).outputs[0]
    col = mix(nt, 1.0, base, stain, 'MULTIPLY')
    col = mix(nt, 1.0, col, damp, 'MULTIPLY')
    out(nt, principled(nt, col, 0.72).outputs[0])
    return m

def carpet():
    m, nt = mat('carpet')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=90.0, Detail=4.0); L(nt, pos, a.inputs['Vector'])
    b = n(nt, 'ShaderNodeTexNoise', Scale=0.7, Detail=8.0, Roughness=0.6); L(nt, pos, b.inputs['Vector'])
    wet = ramp(nt, [(0.5, (1, 1, 1)), (0.62, (0.36, 0.3, 0.2))], b.outputs['Fac']).outputs[0]
    col = ramp(nt, [(0.3, (0.27, 0.2, 0.09)), (0.7, (0.47, 0.37, 0.18))], a.outputs['Fac']).outputs[0]
    col = mix(nt, 1.0, col, wet, 'MULTIPLY')
    bp = n(nt, 'ShaderNodeBump', Strength=0.6, Distance=0.02); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.92, normal=bp.outputs[0]).outputs[0])
    return m

def ceiling():
    m, nt = mat('ceil')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    sep = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, pos, sep.inputs[0])
    def grid(v):
        return math_(nt, 'LESS_THAN', math_(nt, 'ABSOLUTE', math_(nt, 'SUBTRACT', math_(nt, 'FRACT', math_(nt, 'DIVIDE', v, 1.0)), 0.5)), 0.015)
    g = math_(nt, 'MAXIMUM', grid(sep.outputs['X']), grid(sep.outputs['Y']))
    nz = n(nt, 'ShaderNodeTexNoise', Scale=1.2, Detail=8.0); L(nt, pos, nz.inputs['Vector'])
    sp = n(nt, 'ShaderNodeTexNoise', Scale=60.0, Detail=2.0); L(nt, pos, sp.inputs['Vector'])
    dirty = ramp(nt, [(0.45, (0.72, 0.68, 0.52)), (0.65, (0.42, 0.35, 0.2))], nz.outputs['Fac']).outputs[0]
    col = mix(nt, g, dirty, (0.3, 0.26, 0.17))
    bp = n(nt, 'ShaderNodeBump', Strength=0.5, Distance=0.01); L(nt, sp.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.9, normal=bp.outputs[0]).outputs[0])
    return m

def light_mats(k):
    """k grupos de lâmpadas, cada um com força própria"""
    res = []
    for i in range(k):
        m, nt = mat(f'lamp{i}')
        e = n(nt, 'ShaderNodeEmission', Strength=9.0)
        e.inputs['Color'].default_value = (1.0, 0.93, 0.70, 1)
        out(nt, e.outputs[0])
        res.append((m, e))
    return res

def build_level(grid, lamp_groups=1, group_fn=None, seed=2):
    """grid: lista de strings; '#' parede; '.' livre. retorna (mats lâmpadas)"""
    rows, cols = len(grid), len(grid[0])
    W, C, K = wallpaper(), carpet(), ceiling()
    wv, wf = [], []
    def quad(a, b, c, d):
        i = len(wv); wv.extend((a, b, c, d)); wf.append((i, i + 1, i + 2, i + 3))
    for y in range(rows):
        for x in range(cols):
            if grid[y][x] != '#': continue
            x0, x1, y0, y1 = x * CELL, (x + 1) * CELL, y * CELL, (y + 1) * CELL
            def free(ix, iy):
                return 0 <= iy < rows and 0 <= ix < cols and grid[iy][ix] != '#'
            if free(x, y - 1): quad((x1, y0, 0), (x0, y0, 0), (x0, y0, H), (x1, y0, H))
            if free(x, y + 1): quad((x0, y1, 0), (x1, y1, 0), (x1, y1, H), (x0, y1, H))
            if free(x - 1, y): quad((x0, y0, 0), (x0, y1, 0), (x0, y1, H), (x0, y0, H))
            if free(x + 1, y): quad((x1, y1, 0), (x1, y0, 0), (x1, y0, H), (x1, y1, H))
    mesh_from('walls', wv, wf, W)
    # rodapé
    bv, bf = [], []
    for f in wf:
        a, b = wv[f[0]], wv[f[1]]
        i = len(bv)
        d = Vector(b) - Vector(a); nrm = Vector((-d.y, d.x, 0)).normalized() * -0.02
        nrm = Vector((d.y, -d.x, 0)).normalized() * 0.02
        bv.extend(((a[0] + nrm.x, a[1] + nrm.y, 0), (b[0] + nrm.x, b[1] + nrm.y, 0),
                   (b[0] + nrm.x, b[1] + nrm.y, 0.12), (a[0] + nrm.x, a[1] + nrm.y, 0.12)))
        bf.append((i, i + 1, i + 2, i + 3))
    mesh_from('base', bv, bf, simple('rod', (0.24, 0.18, 0.09), 0.6))
    S = (cols * CELL, rows * CELL)
    mesh_from('floor', [(0, 0, 0), (S[0], 0, 0), (S[0], S[1], 0), (0, S[1], 0)], [(0, 1, 2, 3)], C)
    mesh_from('ceil', [(0, 0, H), (0, S[1], H), (S[0], S[1], H), (S[0], 0, H)], [(0, 1, 2, 3)], K)
    lm = light_mats(lamp_groups)
    verts = [[] for _ in range(lamp_groups)]; faces = [[] for _ in range(lamp_groups)]
    for y in range(rows):
        for x in range(cols):
            if grid[y][x] == '#': continue
            cx, cy = (x + .5) * CELL, (y + .5) * CELL
            g = group_fn(x, y) if group_fn else 0
            v = verts[g]; i = len(v)
            a, b = 0.3, 0.6
            if (x + y) % 2: a, b = b, a
            z = H - 0.005
            v.extend(((cx - a, cy - b, z), (cx - a, cy + b, z), (cx + a, cy + b, z), (cx + a, cy - b, z)))
            faces[g].append((i, i + 1, i + 2, i + 3))
    for g in range(lamp_groups):
        if verts[g]:
            mesh_from(f'lamps{g}', verts[g], faces[g], lm[g][0])
    return lm

def flicker(t, seed=0.0, base=9.0, depth=0.5):
    v = noise.noise(Vector((t * 13.0, seed, 1.0)))
    b = 1.0 - depth * max(0.0, v * 2.2)
    if noise.noise(Vector((t * 5.0, seed + 3, 8))) > 0.32:
        b *= 0.12
    return base * b

def figure(loc=(0, 0, 0), s=1.0, facing=0.0):
    """silhueta alta: braços até o chão, cabeça tombada"""
    bl = simple('fig', (0.006, 0.005, 0.005), 0.55)
    pts = []
    root = bpy.data.objects.new('fig', None); link(root); root.location = loc
    def T(name, p, r):
        o = tube(name, p, r, bl, res=6); o.parent = root; return o
    T('torso', [(0, 0, 1.1), (0, 0, 1.6), (0.03, 0, 2.2), (0.05, 0, 2.42)], [.12, .17, .2, .07])
    T('lLeg', [(-.09, 0, 1.1), (-.12, 0.02, .6), (-.14, 0, 0.02)], [.07, .05, .04])
    T('rLeg', [(.09, 0, 1.1), (.12, 0.02, .6), (.14, 0, 0.02)], [.07, .05, .04])
    T('lArm', [(-.2, 0, 2.28), (-.42, .05, 1.65), (-.36, -.05, .9), (-.5, -.12, .1)], [.05, .035, .03, .012])
    T('rArm', [(.2, 0, 2.28), (.44, .04, 1.6), (.38, -.04, .85), (.55, -.1, .1)], [.05, .035, .03, .012])
    h = ico('head', 0.14, (0.22, -0.02, 2.5), bl, 3); h.scale = (0.8, 0.85, 1.4); h.rotation_euler = (0, 1.05, 0); h.parent = root
    em = emission('smile', (1, 0.96, 0.85), 3.0)
    for dx, dz in ((-.05, .10), (.05, .03)):
        e = ico('eye', 0.018, (0.22 + dx, -0.135, 2.5 + dz), em, 2); e.parent = root
    # sorriso largo demais, acompanhando a cabeça tombada
    arc = []
    for k in range(9):
        a = (k / 8 - .5) * 2.4
        arc.append((0.22 + 0.095 * math.sin(a) + 0.03, -0.128 + 0.02 * abs(math.sin(a)), 2.46 - 0.07 * math.cos(a) - 0.05 * math.sin(a)))
    g = tube('grin', arc, [.006, .012, .016, .018, .018, .018, .016, .012, .006], em, res=4); g.parent = root
    root.rotation_euler.z = facing
    root.scale = (s, s, s)
    return root

# --- planeta em órbita, descendo até a superfície ---
def build_p1a():
    s = reset(20)
    world_space((0.02, 0.015, 0.01), 1.0)
    sd = (-1.0, -0.35, 0.45)
    sun(3.2, sd, (1, 0.95, 0.82))
    p = planet_maze(1.0); atmosphere(1.0, (1.0, 0.75, 0.3), sd, 1.02, power=5, strength=0.7)
    p.rotation_euler = (0.3, -0.2, 0)
    cam = camera((0, -3.6, 0.3), (0, 0, 0), 40)
    def update(t, u):
        p.rotation_euler.z = 1.1 + 0.11 * t
        e = ease(u) ** 1.7
        cam.location = vlerp((0.0, -3.8, 0.3), (-0.25, -1.13, 0.2), e)
        look(cam, vlerp((0, 0, 0), (-0.42, -0.6, 0.15), e))
    return update

# --- caminhando pelo corredor ---
G1 = [
"###############",
"#.............#",
"#.###.#.##.##.#",
"#.#...#.#.....#",
"#.#.###.#.###.#",
"#...........#.#",
"###.#.#.###.#.#",
"#.....#.#.....#",
"#.###.#...###.#",
"#...#...#.....#",
"###############"]
def build_p1b():
    s = reset(16)
    world_flat((0.0, 0.0, 0.0))
    lm = build_level(G1, 1)
    cam = camera((6, 6, 1.6), (6, 20, 1.6), 22)
    A = Vector((1.5 * CELL, 1.5 * CELL, 1.58)); B = Vector((10.5 * CELL, 1.5 * CELL, 1.58))
    def update(t, u):
        bob = math.sin(t * 7.4) * 0.016
        p = A.lerp(B, u * 0.42) + Vector((0, 0.08 * math.sin(t * 1.1), bob))
        cam.location = p
        look(cam, p + Vector((6, 0.25 * math.sin(t * 0.8 + 1), -0.03)), roll=0.008 * math.sin(t * 3.7))
        lm[0][1].inputs['Strength'].default_value = flicker(t, 2.0, 13.0, 0.28)
    return update

# --- salão vazio, infinito, com pilares ---
def build_p1c():
    s = reset(16)
    world_flat((0.0, 0.0, 0.0))
    rows, cols = 16, 22
    g = []
    rnd = random.Random(5)
    for y in range(rows):
        r = ''
        for x in range(cols):
            edge = x in (0, cols - 1) or y in (0, rows - 1)
            r += '#' if edge or (x % 3 == 1 and y % 3 == 1 and rnd.random() < 0.8) else '.'
        g.append(r)
    lm = build_level(g, 1)
    cam = camera((6, 6, 1.6), (40, 40, 1.4), 20)
    def update(t, u):
        p = vlerp((2.5 * CELL, 2.5 * CELL, 1.45), (4.0 * CELL, 2.8 * CELL, 1.45), u)
        cam.location = p
        look(cam, p + Vector((8, 3.2 - 1.5 * u, -0.1)))
        lm[0][1].inputs['Strength'].default_value = flicker(t, 9.0, 13.0, 0.2)
    return update

# --- a figura no fim do corredor ---
def build_p1d():
    s = reset(18)
    world_flat((0.0, 0.0, 0.0))
    g = ["#" * 16, "#" + "." * 14 + "#", "#" * 16]
    NG = 7
    lm = build_level(g, NG, lambda x, y: min(NG - 1, (x - 1) // 2))
    fig = figure((13.5 * CELL, 1.5 * CELL, 0), 0.92, -math.pi / 2)
    cam = camera((1.5 * CELL, 1.5 * CELL, 1.55), (15 * CELL, 1.5 * CELL, 1.4), 26)
    # cada apagão aproxima a figura
    steps = [(0.0, 13.5), (1.35, 10.2), (2.3, 6.8), (3.05, 3.9), (3.55, 2.35)]
    def update(t, u):
        pos = steps[0][1]
        for tt, x in steps:
            if t >= tt: pos = x
        fig.location.x = pos * CELL
        cam.location = Vector((1.5 * CELL, 1.5 * CELL, 1.55)) + shake(t, 0.006 + 0.012 * u)
        look(cam, (15 * CELL, 1.5 * CELL, 1.45))
        off = any(abs(t - tt) < 0.13 for tt, _ in steps[1:])
        for i, (m, e) in enumerate(lm):
            v = flicker(t, i * 3.1, 13.0, 0.35)
            if off: v = 0.0
            e.inputs['Strength'].default_value = v
    return update
