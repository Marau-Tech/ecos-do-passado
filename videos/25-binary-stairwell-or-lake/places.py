"""Peças da intro e dos trechos: a escada que só desce e a cabana no lago congelado."""
from lib import *

# ---------- escada ----------
FH = 3.0                        # altura de um andar
Q = FH / 4                      # cada lance desce um quarto de andar, em volta do vão
S = 2.0                         # meia largura do poço, até a face de dentro da parede
V = 0.6                         # meia largura do vão do meio
C = (S + V) / 2                 # centro de um patamar de canto
CORNERS = [(C, C), (-C, C), (-C, -C), (C, -C)]
DIRS = [(-1, 0), (0, -1), (1, 0), (0, 1)]       # lance k vai do canto k ao canto k+1, descendo
STEPS = 5


def concrete(name='concrete', col=(0.42, 0.44, 0.4)):
    m, nt = mat(name)
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=3.0, Detail=8.0, Roughness=0.6); L(nt, pos, a.inputs['Vector'])
    c = ramp(nt, [(0.3, tuple(x * 0.75 for x in col)), (0.7, col)], a.outputs['Fac']).outputs[0]
    out(nt, principled(nt, c, 0.85, spec=0.1).outputs[0])
    return m


def corner_z(q):
    return -q * Q


def lamp(name, loc, energy=30.0):
    """luminária de parede com a luz junto; devolve (emissão, luz) para ligar e desligar"""
    m, nt = mat(name)
    e = n(nt, 'ShaderNodeEmission', Strength=3.0); e.inputs['Color'].default_value = (0.85, 1.0, 0.85, 1)
    out(nt, e.outputs[0])
    box(name, (0.34, 0.34, 0.12), loc, m)
    lt = point((loc[0] * 0.78, loc[1] * 0.78, loc[2] - 0.2), energy, (0.85, 1.0, 0.85), 0.2)
    return e, lt, energy


def set_lamp(lp, k):
    e, lt, en = lp
    e.inputs['Strength'].default_value = 0.04 + 3.0 * k                # apagada, fica o vidro cinza
    lt.data.energy = en * k


def stairwell(quarters, lamp_at=(), walls=(0, 1, 2, 3), top=1.6, doors=True):
    """Poço quadrado com lances em volta do vão. lamp_at: quartos com luminária. Devolve (peças, {quarto: luminária})."""
    steel = simple('rail', (0.08, 0.2, 0.12), 0.45, 0.4)
    step_m = concrete('step', (0.5, 0.5, 0.47))
    wall_m = concrete('wall', (0.55, 0.6, 0.52))
    door_m = simple('door', (0.22, 0.26, 0.24), 0.5, 0.5)
    parts = []
    bottom = corner_z(quarters) - FH
    hgt = top - bottom
    zc = (top + bottom) / 2
    wall_boxes = [((2 * S + 0.4, 0.2, hgt), (0, S + 0.1, zc)), ((0.2, 2 * S + 0.4, hgt), (-S - 0.1, 0, zc)),
                  ((2 * S + 0.4, 0.2, hgt), (0, -S - 0.1, zc)), ((0.2, 2 * S + 0.4, hgt), (S + 0.1, 0, zc))]
    for w in walls:
        sz, loc = wall_boxes[w]
        parts.append(box('wall', sz, loc, wall_m))
    lamps = {}
    for q in range(quarters):
        k = q % 4
        cx, cy = CORNERS[k]
        z = corner_z(q)
        parts.append(box('landing', (S - V, S - V, 0.25), (cx, cy, z - 0.125), step_m))
        # corrimão do lado do vão, de quina a quina
        ix, iy = math.copysign(V, cx), math.copysign(V, cy)
        dx, dy = DIRS[k]
        parts.append(tube('rail', [(ix, iy, z + 0.95), (ix + dx * 2 * V, iy + dy * 2 * V, z - Q + 0.95)], [0.025, 0.025], steel, kind='POLY'))
        parts.append(tube('post', [(ix, iy, z), (ix, iy, z + 0.95)], [0.02, 0.02], steel, kind='POLY'))
        # degraus do lance que sai deste canto
        run = 2 * V / STEPS
        for j in range(STEPS):
            ztop = z - (j + 1) * Q / STEPS
            r = V - (j + 0.5) * run
            if dx:
                parts.append(box('step', (run + 0.01, S - V, 0.34), (-dx * r, cy, ztop - 0.17), step_m))
            else:
                parts.append(box('step', (S - V, run + 0.01, 0.34), (cx, -dy * r, ztop - 0.17), step_m))
        for j in (1, 3):                                   # balaústres do lance
            f = j / 4
            parts.append(tube('post', [(ix + dx * 2 * V * f, iy + dy * 2 * V * f, z - Q * f),
                                       (ix + dx * 2 * V * f, iy + dy * 2 * V * f, z - Q * f + 0.95)], [0.015, 0.015], steel, kind='POLY'))
        if q in lamp_at:
            ax, ay = DIRS[(k - 1) % 4]                     # na parede de frente para quem chega
            lx, ly = cx + ax * (S - C - 0.08), cy + ay * (S - C - 0.08)
            lamps[q] = lamp(f'lamp{q}', (lx, ly, z + 2.3))
        if doors and k == 0:                               # uma porta por andar, na parede x = +S
            parts.append(box('door', (0.06, 0.9, 2.0), (S - 0.02, C, z + 1.0), door_m))
            parts.append(box('frame', (0.04, 1.05, 2.1), (S - 0.005, C, z + 1.05), simple('frame', (0.1, 0.11, 0.1), 0.6)))
    return parts, lamps


def sign(text, loc, size=0.16):
    """placa branca com o andar, presa na parede x = +S, lida de quem olha para +x"""
    plate = box('plate', (0.02, size * 2.6, size * 1.1), loc, simple('plate', (0.75, 0.75, 0.7), 0.6))
    cu = bpy.data.curves.new('sign', 'FONT'); cu.body = text; cu.size = size
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = 0.003
    o = bpy.data.objects.new('sign', cu); link(o)
    o.location = (loc[0] - 0.015, loc[1], loc[2])
    o.rotation_euler = (math.radians(90), 0, math.radians(-90))
    cu.materials.append(simple('ink', (0.02, 0.02, 0.02), 0.6))
    return plate, o


# ---------- lago ----------
def ice_mat(name='ice'):
    m, nt = mat(name)
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.25, Detail=6.0, Roughness=0.6); L(nt, pos, a.inputs['Vector'])
    snow = ramp(nt, [(0.45, (0, 0, 0)), (0.6, (1, 1, 1))], a.outputs['Fac']).outputs[0]
    c = mix(nt, snow, (0.08, 0.13, 0.18), (0.75, 0.8, 0.86))
    r = mix(nt, snow, (0.15, 0.15, 0.15), (0.9, 0.9, 0.9))
    cr = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=0.6); L(nt, pos, cr.inputs['Vector'])
    crack = math_(nt, 'LESS_THAN', cr.outputs['Distance'], 0.015)
    c = mix(nt, math_(nt, 'MULTIPLY', crack, 0.6), c, (0.6, 0.7, 0.78))
    p = principled(nt, c, 0.3, spec=0.5)
    L(nt, r, p.inputs['Roughness'])
    out(nt, p.outputs[0])
    return m


def night_sky(top=(0.004, 0.006, 0.014), low=(0.03, 0.04, 0.06), strength=1.0):
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc.outputs['Generated'], sp.inputs[0])
    col = ramp(nt, [(0.0, low), (0.12, low), (0.4, top)], sp.outputs['Z']).outputs[0]
    b = n(nt, 'ShaderNodeBackground', Strength=strength); L(nt, col, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld'); L(nt, b.outputs[0], o.inputs['Surface'])


def wood(name='wood', col=(0.16, 0.1, 0.06), distort=6.0):
    m, nt = mat(name)
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    w = n(nt, 'ShaderNodeTexWave', Scale=1.5, Distortion=distort, Detail=4.0); L(nt, pos, w.inputs['Vector'])
    c = ramp(nt, [(0.2, tuple(x * 0.6 for x in col)), (0.8, col)], w.outputs['Fac']).outputs[0]
    out(nt, principled(nt, c, 0.8, spec=0.1).outputs[0])
    return m


def cabin(loc=(0, 0, 0), rot=0.0, window=8.0):
    """cabana de pesca: paredes de tábua, telhado com neve, uma janela acesa de frente (-y) e chaminé"""
    root = bpy.data.objects.new('cabin', None); link(root)
    wd = wood('cabin_wood', (0.2, 0.12, 0.07))
    snow = simple('snow', (0.85, 0.88, 0.92), 0.7)
    dark = simple('trim', (0.05, 0.04, 0.03), 0.7)
    parts = [box('walls', (3.0, 2.4, 2.0), (0, 0, 1.0), wd),
             box('roofL', (3.3, 1.5, 0.12), (0, -0.62, 2.3), wd, rot=(math.radians(-28), 0, 0)),
             box('roofR', (3.3, 1.5, 0.12), (0, 0.62, 2.3), wd, rot=(math.radians(28), 0, 0)),
             box('snowL', (3.3, 1.45, 0.08), (0, -0.6, 2.4), snow, rot=(math.radians(-28), 0, 0)),
             box('snowR', (3.3, 1.45, 0.08), (0, 0.6, 2.4), snow, rot=(math.radians(28), 0, 0)),
             box('gableF', (3.0, 0.1, 0.6), (0, -1.15, 2.1), wd), box('gableB', (3.0, 0.1, 0.6), (0, 1.15, 2.1), wd),
             box('chimney', (0.3, 0.3, 0.9), (0.9, 0.5, 2.7), dark),
             box('door', (0.8, 0.06, 1.7), (-0.8, -1.21, 0.85), dark),
             box('base', (3.4, 2.8, 0.12), (0, 0, 0.0), snow)]
    win = emission('window', (1.0, 0.62, 0.28), window)
    parts.append(box('window', (0.7, 0.05, 0.55), (0.6, -1.21, 1.25), win))
    parts.append(box('mullion', (0.04, 0.07, 0.55), (0.6, -1.23, 1.25), dark))
    for o in parts:
        o.parent = root
    glow = point((0.6, -1.9, 1.2), 25.0, (1.0, 0.6, 0.28), 0.3)
    glow.parent = root
    root.location = loc; root.rotation_euler.z = rot
    return root


def pines(n_, radius, seed=2, h=(4, 9), m=None, center=(0, 0), arc=None):
    """pinheiros escuros em volta da margem: cones empilhados numa malha só"""
    m = m or simple('pine', (0.01, 0.02, 0.015), 0.9)
    rs = np.random.RandomState(seed)
    v, t = lathe([(0.0, 0.0), (0.12, 0.0), (0.12, 0.2), (0.55, 0.2), (0.0, 0.55), (0.42, 0.45), (0.0, 0.8),
                  (0.3, 0.72), (0.0, 1.0)], 7)
    pos, sc = [], []
    for i in range(n_):
        a = rs.uniform(*(arc or (0, 2 * math.pi)))
        r = radius + rs.uniform(-0.08, 0.15) * radius
        hh = rs.uniform(*h)
        pos.append((center[0] + r * math.cos(a), center[1] + r * math.sin(a), 0))
        sc.append((hh * 0.5, hh * 0.5, hh))
    return scatter('pines', v, t, pos, rs.uniform(0, 6, n_), sc, m, smooth=False)


def snowfall(k, lo, hi, seed=5, size=0.02, bright=0.6):
    """flocos: pontinhos numa malha só; mover a malha faz a neve cair"""
    rs = np.random.RandomState(seed)
    c = np.stack([rs.uniform(lo[i], hi[i], k) for i in range(3)], 1)
    v, t = lathe([(0.0, -size), (size, 0.0), (0.0, size)], 4)
    return scatter('snow', v, t, c, None, None,
                   simple('flake', (0.9, 0.92, 0.95), 0.6, emis=(0.8, 0.85, 0.95), emis_str=bright), smooth=False)


def group(build, loc, s, rot=(0, 0, 0)):
    """monta uma miniatura: tudo que build() criar vira filho de um vazio, e as luzes encolhem junto"""
    before = set(bpy.data.objects)
    build()
    root = bpy.data.objects.new('mini', None); link(root)
    for o in set(bpy.data.objects) - before:
        if o is root or o.parent is not None:
            continue
        o.parent = root
        if o.type == 'LIGHT':
            o.data.energy *= s * s
            if o.data.type == 'POINT':
                o.data.shadow_soft_size *= s
    root.location = loc; root.scale = (s, s, s); root.rotation_euler = rot
    return root
