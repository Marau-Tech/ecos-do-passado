"""THE SPIRES: uma cidade de pedra verde num mar preto. Os ângulos estão errados. Embaixo dela, algo dorme e sonha você."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'p4a': 6.25, 'p4b': 3.25, 'p4c': 3.25, 'p4d': 4.5}
AJAR, OPEN = 0.15, 0.85         # ângulo da porta: entreaberta e aberta
HINGE = (-6.0, 84.0, 0.0)


def build_p4a():
    upd = orbit(planet_spires, (0.25, 0.8, 0.5), (-1.0, -0.25, 0.3))
    return lambda t, u: upd(t, u, SHOTS['p4a'])


def green_stone():
    """pedra verde-preta, com entalhes que brilham fraco"""
    m, nt = mat('gstone')
    tc = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.4, Detail=8.0, Roughness=0.65); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.35, (0.012, 0.03, 0.022)), (0.65, (0.05, 0.1, 0.07))], a.outputs['Fac']).outputs[0]
    w = n(nt, 'ShaderNodeTexWave', {'wave_type': 'BANDS', 'bands_direction': 'Z'}, Scale=0.11, Distortion=7.0, Detail=4.0); L(nt, tc, w.inputs['Vector'])
    carve = math_(nt, 'GREATER_THAN', w.outputs['Fac'], 0.992)
    bp = n(nt, 'ShaderNodeBump', Strength=0.7, Distance=0.2); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.55, spec=0.5, normal=bp.outputs[0], emis=mix(nt, carve, (0, 0, 0), (0.25, 1.0, 0.5)), emis_str=0.35).outputs[0])
    return m


def monolith(m, loc, w, d, h, shear, twist, spire, tilt, yaw):
    """bloco alto com o topo deslocado e torcido, às vezes em ponta; cada um inclinado para um lado"""
    c, s = math.cos(twist), math.sin(twist)
    base = [(-w, -d), (w, -d), (w, d), (-w, d)]
    v = [(x, y, -6.0) for x, y in base]
    v += [(x * c * 0.7 - y * s * 0.7 + shear[0], x * s * 0.7 + y * c * 0.7 + shear[1], h) for x, y in base]
    f = [(0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    if spire:
        v.append((shear[0] * 1.3, shear[1] * 1.3, h + 0.6 * h * spire))
        f += [(4, 5, 8), (5, 6, 8), (6, 7, 8), (7, 4, 8)]
    else:
        f.append((4, 5, 6, 7))
    o = mesh_from('monolith', v, f, m)
    o.location = loc; o.rotation_euler = (tilt[0], tilt[1], yaw)
    return o


def city():
    """Mar preto, céu roxo-escuro, torres tortas e a muralha com a porta. Devolve a dobradiça, a massa e a luz de dentro."""
    reset(18)
    world_space((0.035, 0.008, 0.05), 0.9, star=1.4)
    sm, nt = mat('sea')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.35, Detail=6.0); L(nt, pos, a.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.25, Distance=0.3); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, (0.002, 0.005, 0.005), 0.1, spec=0.8, normal=bp.outputs[0]).outputs[0])
    grid_mesh('sea', 1400, 360, lambda X, Y: 0.06 * np.sin(X * 0.21 + Y * 0.13) + 0.2 * (fbm(X * 0.03, Y * 0.03, 3) - 0.5), sm, center=(0, 500))
    gs = green_stone()
    rs = np.random.RandomState(13)
    for k in range(46):
        r = 25 + 110 * rs.rand() ** 0.8; a_ = rs.uniform(-1.3, 1.3)
        x, y = r * math.sin(a_), 150 + r * math.cos(a_) * 0.7
        h = 45 + 120 * rs.rand() * (1.2 - r / 160)
        monolith(gs, (x, y, 0), 2.5 + 6 * rs.rand(), 2.5 + 6 * rs.rand(), h,
                 (rs.uniform(-0.25, 0.25) * h, rs.uniform(-0.15, 0.15) * h), rs.uniform(-0.6, 0.6),
                 rs.rand() if rs.rand() < 0.6 else 0, (rs.uniform(-0.18, 0.18), rs.uniform(-0.18, 0.18)), rs.uniform(0, 3.1))
    # muralha com a porta: nenhum lado é reto com o outro
    box('wallL', (20, 12, 48), (-16, 90, 18), gs, rot=(0.0, 0.03, 0.0))
    box('wallR', (20, 12, 52), (16.5, 90, 20), gs, rot=(0.0, -0.05, 0.02))
    box('lintel', (30, 13, 12), (0.5, 90, 37), gs, rot=(0.0, 0.06, -0.02))
    hinge = bpy.data.objects.new('hinge', None); link(hinge); hinge.location = HINGE
    door = box('door', (12, 1.6, 31), (6, 0, 15.5), gs); door.parent = hinge
    box('back', (48, 1, 44), (0, 128, 20), simple('voidm', (0, 0, 0), 1.0))
    # a coisa que dorme, atrás da porta
    mm, nt = mat('mass')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    pv = n(nt, 'ShaderNodeValue'); pv.name = 'pulse'
    vn = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=0.5); L(nt, tc, vn.inputs['Vector'])
    veins = math_(nt, 'MULTIPLY', math_(nt, 'LESS_THAN', vn.outputs['Distance'], 0.05), pv.outputs[0])
    out(nt, principled(nt, (0.01, 0.018, 0.014), 0.25, spec=0.8, emis=mix(nt, veins, (0, 0, 0), (0.3, 1.0, 0.45)), emis_str=3.0).outputs[0])
    mass = ico('mass', 11, (0, 112, 12), mm, 5)
    tex = bpy.data.textures.new('massc', 'CLOUDS'); tex.noise_scale = 3.5; tex.noise_depth = 3
    dm = mass.modifiers.new('d', 'DISPLACE'); dm.texture = tex; dm.strength = 3.0; dm.mid_level = 0.5
    rs = np.random.RandomState(4)
    for k in range(9):                                    # tentáculos saindo da massa na direção da porta
        a0 = rs.uniform(-1.2, 1.2); z0 = rs.uniform(2, 24)
        pts = [(9 * math.sin(a0), 104, z0), (5 * math.sin(a0) + rs.uniform(-3, 3), 99, z0 + rs.uniform(-4, 4)),
               (rs.uniform(-4, 4), 95, z0 + rs.uniform(-6, 6)), (rs.uniform(-6, 6), 90.5, rs.uniform(1, 28))]
        tube('tentacle', pts, [1.4, 1.0, 0.6, 0.15], mm).parent = mass
    inner = point((0, 98, 14), 900.0, (0.3, 1.0, 0.5), 3.0)
    sun(0.25, (0.3, -0.5, 0.6), (0.5, 0.8, 0.65))
    fog((0.01, 0.03, 0.025), 30.0, 420.0, 0.6)
    return hinge, mass, inner


def build_p4b():
    hinge, mass, inner = city()
    hinge.rotation_euler.z = 0.0
    cam = camera((4, -30, 2.4), (0, 150, 30), 30)
    def update(t, u):
        cam.location = (4 - 1.5 * u, -30 + 2.5 * t, 2.4 + 0.2 * math.sin(t * 0.9))     # boiando
        look(cam, (0, 150, 30 + 4 * u), roll=0.02 * math.sin(t * 0.7))
    return update


def build_p4c():
    hinge, mass, inner = city()
    hinge.rotation_euler.z = AJAR
    pulse = mass.data.materials[0].node_tree.nodes['pulse']
    cam = camera((9, 38, 2.6), (0, 86, 16), 30)
    def update(t, u):
        b = 0.5 + 0.5 * math.sin(2 * math.pi * t / 1.8)    # respira devagar
        mass.scale = (1 + 0.05 * b,) * 3
        pulse.outputs[0].default_value = 0.3 + 0.7 * b
        inner.data.energy = 600 + 600 * b
        cam.location = (9 - 2.5 * u, 38 + 9 * ease(u), 2.6 + 0.2 * math.sin(t * 0.9))
        look(cam, (0, 86, 16), roll=0.02 * math.sin(t * 0.7))
    return update


def build_p4d():
    hinge, mass, inner = city()
    pulse = mass.data.materials[0].node_tree.nodes['pulse']
    rs = np.random.RandomState(21)
    sm = emission('star', (0.85, 1.0, 0.9), 40.0)
    stars = []
    for k in range(9):
        a = (rs.uniform(-210, 210), 320, rs.uniform(170, 400))
        b = (0.0, 320, 225 + k * 15)                      # em fila, bem em cima da porta
        s = ico('star', 1.6, a, sm, 2)
        g = glow(6.0, (0, 0, 0), (0.6, 1.0, 0.75), 2.0); g.parent = s
        stars.append((s, a, b))
    cam = camera((0, 8, 3.0), (0, 90, 58), 24)
    def update(t, u):
        k = ease(min(1.0, t / TL.ALIGN_AT))
        for s, a, b in stars:
            s.location = vlerp(a, b, k)
        o = ease(min(1.0, max(0.0, (t - TL.ALIGN_AT) / 1.0)))     # acorda: a porta abre
        hinge.rotation_euler.z = AJAR + (OPEN - AJAR) * o
        rate = 1.8 - 1.2 * o
        b_ = 0.5 + 0.5 * math.sin(2 * math.pi * t / rate)
        mass.scale = (1 + 0.05 * b_ + 0.25 * o,) * 3
        pulse.outputs[0].default_value = 0.3 + 0.7 * b_ + 2.0 * o
        inner.data.energy = 600 + 600 * b_ + 6000 * o
        cam.location = Vector((0, 8 + 0.8 * t, 3.0)) + shake(t, 0.25 * o, 10)
        look(cam, (0, 90, 58), roll=0.02 * math.sin(t * 0.7) + 0.05 * o)
    return update
