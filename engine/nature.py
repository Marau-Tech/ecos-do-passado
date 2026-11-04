"""Céu, grama, árvores e casas reaproveitáveis em cenas ao ar livre."""
from lib import *

def sky():
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    grad = ramp(nt, [(0.0, (0.85, 0.92, 0.95)), (0.2, (0.42, 0.68, 0.95)), (0.7, (0.10, 0.32, 0.78))], sp.outputs['Z']).outputs[0]
    # nuvens projetadas num plano alto
    z = math_(nt, 'MAXIMUM', sp.outputs['Z'], 0.04)
    cv = n(nt, 'ShaderNodeCombineXYZ')
    L(nt, math_(nt, 'DIVIDE', sp.outputs['X'], z), cv.inputs['X'])
    L(nt, math_(nt, 'DIVIDE', sp.outputs['Y'], z), cv.inputs['Y'])
    nz = n(nt, 'ShaderNodeTexNoise', Scale=0.55, Detail=9.0, Roughness=0.58)
    L(nt, cv.outputs[0], nz.inputs['Vector'])
    cl = ramp(nt, [(0.52, (0, 0, 0)), (0.68, (1, 1, 1))], nz.outputs['Fac']).outputs[0]
    up = math_(nt, 'GREATER_THAN', sp.outputs['Z'], 0.0)
    col = mix(nt, math_(nt, 'MULTIPLY', cl, up), grad, (1, 0.98, 0.94))
    b = n(nt, 'ShaderNodeBackground', Strength=1.0); L(nt, col, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])

def ground_mat():
    m, nt = mat('ground')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.5, Detail=8.0, Roughness=0.6); L(nt, pos, a.inputs['Vector'])
    col = ramp(nt, [(0.35, (0.10, 0.27, 0.03)), (0.65, (0.25, 0.46, 0.06))], a.outputs['Fac']).outputs[0]
    out(nt, principled(nt, col, 0.9).outputs[0])
    return m

GRASS = ((0.13, 0.36, 0.04), (0.28, 0.58, 0.07), (0.55, 0.72, 0.12))
def grass_mat(colors=GRASS):
    m, nt = mat('grass')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.5, Detail=6.0, Roughness=0.6); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.32, colors[0]), (0.55, colors[1]), (0.72, colors[2])], a.outputs['Fac']).outputs[0]
    d = n(nt, 'ShaderNodeBsdfDiffuse'); L(nt, c, d.inputs['Color'])
    tr = n(nt, 'ShaderNodeBsdfTranslucent'); L(nt, c, tr.inputs['Color'])
    ms = n(nt, 'ShaderNodeMixShader', Fac=0.4)
    L(nt, d.outputs[0], ms.inputs[1]); L(nt, tr.outputs[0], ms.inputs[2])
    out(nt, ms.outputs[0])
    return m

def grass(cx, cy, ang, reach, count, hfun, seed=1, blade=0.32, spread=1.5, colors=GRASS):
    """lâminas em leque à frente da câmera (densidade alta perto)"""
    rs = np.random.RandomState(seed)
    r = reach * rs.rand(count) ** 1.8 + 0.2
    th = ang + (rs.rand(count) - .5) * spread
    x = cx + r * np.cos(th); y = cy + r * np.sin(th)
    z = hfun(x, y)
    h = blade * (0.6 + 0.8 * rs.rand(count)) * (1 + r / reach * 1.8)
    w = 0.018 * (1 + r / reach * 7)
    d = rs.rand(count) * 6.283
    dx, dy = np.cos(d) * w, np.sin(d) * w
    lean = (rs.rand(count, 2) - .5) * h[:, None] * 0.7
    v = np.empty((count * 3, 3), np.float32)
    v[0::3] = np.stack([x - dx, y - dy, z], 1)
    v[1::3] = np.stack([x + dx, y + dy, z], 1)
    v[2::3] = np.stack([x + lean[:, 0], y + lean[:, 1], z + h], 1)
    t = np.arange(count * 3).reshape(-1, 3)
    return fast_mesh('grass', v, t, grass_mat(colors))

def cottage(loc, rot=0.0, s=1.0, wall=(0.92, 0.88, 0.78), roof=(0.62, 0.13, 0.08)):
    root = bpy.data.objects.new('house', None); link(root)
    wm = simple('w', wall, 0.8)
    rm = simple('r', roof, 0.65)
    b = box('b', (4, 3, 2.4), (0, 0, 1.2), wm); b.parent = root
    v = [(-2.3, -1.8, 2.3), (2.3, -1.8, 2.3), (2.3, 1.8, 2.3), (-2.3, 1.8, 2.3), (-2.3, 0, 3.9), (2.3, 0, 3.9)]
    f = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5)]
    r = mesh_from('roof', v, f, rm); r.parent = root
    gv = [(-2, -1.5, 2.4), (-2, 1.5, 2.4), (-2, 0, 3.7), (2, -1.5, 2.4), (2, 1.5, 2.4), (2, 0, 3.7)]
    g = mesh_from('gab', gv, [(0, 1, 2), (3, 5, 4)], wm); g.parent = root
    d = box('d', (0.9, 0.06, 1.7), (0, -1.52, 0.85), simple('door', (0.28, 0.14, 0.06), 0.6)); d.parent = root
    gl = simple('gl', (0.5, 0.75, 0.9), 0.15, emis=(1, 0.85, 0.5), emis_str=0.4)
    for x in (-1.3, 1.3):
        w = box('win', (0.75, 0.06, 0.75), (x, -1.52, 1.4), gl); w.parent = root
    c = box('ch', (0.45, 0.45, 1.3), (1.1, 0.7, 3.6), simple('ch', (0.4, 0.2, 0.14), 0.8)); c.parent = root
    root.location = loc; root.rotation_euler.z = rot; root.scale = (s, s, s)
    return root

_tex = {}
def blob_tex():
    if 'c' not in _tex:
        t = bpy.data.textures.new('leafc', 'CLOUDS'); t.noise_scale = 0.32; t.noise_depth = 3
        _tex['c'] = t
    return _tex['c']

def leaf_mat():
    m, nt = mat('leaf')
    tc = n(nt, 'ShaderNodeTexCoord')
    a = n(nt, 'ShaderNodeTexNoise', Scale=11.0, Detail=6.0, Roughness=0.65); L(nt, tc.outputs['Object'], a.inputs['Vector'])
    c = ramp(nt, [(0.35, (0.03, 0.17, 0.03)), (0.62, (0.16, 0.45, 0.07))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=1.0, Distance=0.25); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, 0.7, normal=bp.outputs[0]).outputs[0])
    return m

def tree(loc, s=1.0, seed=1):
    rnd = random.Random(seed)
    root = bpy.data.objects.new('tree', None); link(root); root.location = loc; root.scale = (s, s, s)
    bark = simple('bark', (0.20, 0.12, 0.06), 0.9)
    lm = leaf_mat()
    t = tube('trunk', [(0, 0, 0), (0.1, 0, 1.3), (-0.1, 0.1, 2.6), (0, 0, 3.8)], [.42, .3, .24, .15], bark, res=6)
    t.parent = root
    blobs = []
    for i in range(15):
        a = i * 2.4 + rnd.random()
        r = 0.3 + 2.0 * rnd.random()
        p = (r * math.cos(a), r * math.sin(a), 3.5 + 2.3 * rnd.random())
        rad = 0.85 + 0.6 * rnd.random()
        b = ico('leaf', rad, p, lm, 5); b.parent = root
        d = b.modifiers.new('d', 'DISPLACE'); d.texture = blob_tex(); d.strength = 0.38; d.mid_level = 0.5
        blobs.append((p, rad))
        if i < 5:
            br = tube('br', [(0, 0, 2.7), (p[0] * .5, p[1] * .5, 3.3), p], [.14, .09, .05], bark); br.parent = root
    return root, blobs
