"""Rua em ruínas com neve, entulho, prédios destruídos, figuras sentadas e a câmera POV que anda."""
from lib import *

CUBE_V = [(-.5, -.5, 0), (.5, -.5, 0), (.5, .5, 0), (-.5, .5, 0), (-.5, -.5, 1), (.5, -.5, 1), (.5, .5, 1), (-.5, .5, 1)]
CUBE_T = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
          (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
EYE = 1.65


def noisy(name, a, b, scale=2.0, rough=0.9, bump=0.3):
    """material com manchas entre duas cores e um relevo leve"""
    m, nt = mat(name)
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    nz = n(nt, 'ShaderNodeTexNoise', Scale=scale, Detail=8.0, Roughness=0.65); L(nt, pos, nz.inputs['Vector'])
    c = ramp(nt, [(0.35, a), (0.65, b)], nz.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=bump, Distance=0.05); L(nt, nz.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, rough, spec=0.3, normal=bp.outputs[0]).outputs[0])
    return m


def snow_mat():
    return noisy('snow', (0.42, 0.42, 0.42), (0.80, 0.82, 0.86), 0.9, 0.85, 0.15)


def brick_mat(k=0):
    cols = [((0.20, 0.16, 0.13), (0.38, 0.30, 0.24)), ((0.25, 0.24, 0.22), (0.45, 0.43, 0.40)),
            ((0.17, 0.15, 0.14), (0.32, 0.28, 0.25))]
    a, b = cols[k % 3]
    return noisy(f'wall{k}', a, b, 3.0, 0.95, 0.4)


def soot_mat():
    return noisy('soot', (0.02, 0.02, 0.02), (0.08, 0.07, 0.06), 4.0, 0.95, 0.2)


def snowfall(k, lo, hi, seed=5, size=0.02, bright=0.5):
    """flocos: pontinhos numa malha só; mover a malha faz a neve cair"""
    rs = np.random.RandomState(seed)
    c = np.stack([rs.uniform(lo[i], hi[i], k) for i in range(3)], 1)
    v, t = lathe([(0.0, -size), (size, 0.0), (0.0, size)], 4)
    return scatter('snowfall', v, t, c, None, None,
                   simple('flake', (0.9, 0.92, 0.95), 0.6, emis=(0.8, 0.85, 0.95), emis_str=bright), smooth=False)


def rubble(count, xr, yr, seed=1, size=(0.15, 0.9), m=None):
    """entulho: blocos tortos numa malha só"""
    rs = np.random.RandomState(seed)
    pos = np.stack([rs.uniform(*xr, count), rs.uniform(*yr, count), rs.uniform(-0.15, 0.05, count)], 1)
    s = rs.uniform(*size, count)
    sc = np.stack([s * rs.uniform(0.6, 1.6, count), s * rs.uniform(0.6, 1.6, count), s * rs.uniform(0.3, 0.8, count)], 1)
    return scatter('rubble', CUBE_V, CUBE_T, pos, rs.uniform(0, 6.3, count), sc, m or brick_mat(0), smooth=False)


def mounds(count, xr, yr, seed=2):
    """montes de neve sobre o entulho"""
    rs = np.random.RandomState(seed)
    v, t = lathe([(1.0, 0.0), (0.8, 0.25), (0.45, 0.42), (0.0, 0.5)], 12)
    pos = np.stack([rs.uniform(*xr, count), rs.uniform(*yr, count), np.zeros(count)], 1)
    s = rs.uniform(0.4, 1.4, count)
    return scatter('mounds', v, t, pos, rs.uniform(0, 6.3, count), np.stack([s * 1.6, s, s * 0.7], 1), snow_mat())


def building(x, y, w, d, h, side, k, rs, broken=True):
    """bloco de alvenaria na beira da rua; janelas escuras na face da rua; topo quebrado"""
    m = brick_mat(k)
    dark = simple('hole', (0.008, 0.008, 0.009), 0.95)
    box('bld', (d, w, h), (x, y, h / 2), m)
    face = x - side * d / 2
    for row in range(int((h - 1.5) // 3.0)):
        for col in range(max(1, int(w // 2.4))):
            if rs.rand() < 0.15:
                continue
            wy = y - w / 2 + 1.2 + col * 2.4
            box('win', (0.08, 1.0, 1.5), (face - side * 0.02, wy, 2.2 + row * 3.0), dark)
    if broken:
        for _ in range(rs.randint(1, 4)):  # pedaços de parede que sobraram no topo
            ph = rs.uniform(1.0, 4.0)
            box('frag', (d * rs.uniform(0.15, 0.4), w * rs.uniform(0.15, 0.4), ph),
                (x + rs.uniform(-d / 3, d / 3), y + rs.uniform(-w / 3, w / 3), h + ph / 2), m,
                (rs.uniform(-0.08, 0.08), rs.uniform(-0.08, 0.08), 0))
        box('snowtop', (d * 0.98, w * 0.98, 0.15), (x, y, h + 0.05), snow_mat())


def street(length, seed=3, width=10.0, ruined=True):
    """rua ao longo de +y: chão de neve, prédios dos dois lados, entulho e montes"""
    rs = np.random.RandomState(seed)
    box('ground', (400, 400, 0.2), (0, length / 2, -0.1), snow_mat())
    y = -15.0
    while y < length + 120:
        for side in (-1, 1):
            if rs.rand() < 0.12:
                continue
            w, d = rs.uniform(7, 13), rs.uniform(8, 12)
            h = rs.uniform(5, 16) * (rs.uniform(0.35, 0.9) if ruined else 1.0)
            building(side * (width / 2 + d / 2), y + w / 2, w, d, h, side, rs.randint(3), rs, ruined)
        y += rs.uniform(9, 14)
    if ruined:
        rubble(500, (-width / 2, width / 2), (-5, length + 60), seed + 1)
        rubble(120, (-width / 2, -1.6), (-5, length + 60), seed + 2, (0.6, 1.8))
        rubble(120, (1.6, width / 2), (-5, length + 60), seed + 3, (0.6, 1.8))
        mounds(90, (-width / 2, width / 2), (-5, length + 60), seed + 4)
        burnt = soot_mat()
        for _ in range(14):  # vigas queimadas caídas
            x0, y0 = rs.uniform(-width / 2, width / 2), rs.uniform(0, length + 50)
            a = rs.uniform(0, 6.3)
            tube('beam', [(x0, y0, 0.1), (x0 + 3 * math.cos(a), y0 + 3 * math.sin(a), rs.uniform(0.2, 1.5))],
                 [0.12, 0.1], burnt, kind='POLY')


def overcast(col=(0.26, 0.27, 0.29), strength=1.0, mist=(0.33, 0.34, 0.36), start=6, depth=70):
    world_flat(col, strength)
    sun(0.6, (0.3, -0.6, 0.6), (0.85, 0.88, 0.95), 25)
    fog(mist, start, depth, 0.85)


def walk(cam, t, start, speed=1.1, yaw=0.0, pitch=-4.0, step_hz=1.8, bob=0.035, shake_amp=0.025, seed=1.0, pan=0.0):
    """câmera na mão de quem anda: passo, balanço lateral e tremor leve. yaw 0 olha para +y; pan gira com o tempo (rad/s)"""
    go = Vector((math.sin(yaw), math.cos(yaw), 0))            # direção do passo
    yaw = yaw + pan * t
    d = Vector((math.sin(yaw), math.cos(yaw), 0))             # direção do olhar
    step = math.sin(math.pi * step_hz * t)
    p = Vector(start) + go * speed * t
    if speed > 0:
        p.z += bob * abs(step) - bob / 2
        p += Vector((d.y, -d.x, 0)) * bob * 0.6 * step
    else:
        p.z += 0.01 * math.sin(2 * math.pi * 0.25 * t)       # respiração
    cam.location = p
    j = shake(t, shake_amp, 1.6, seed)
    target = p + d * 10 + Vector((0, 0, 10 * math.tan(math.radians(pitch)))) + j * 10
    look(cam, target, roll=0.012 * step + j.x * 0.5)


COAT = ((0.05, 0.055, 0.045), (0.11, 0.11, 0.09))


def seated(loc, yaw, seed=0):
    """soldado sentado encostado na parede, joelhos dobrados, capacete; só silhueta escura com pouca luz"""
    rs = np.random.RandomState(seed)
    root = bpy.data.objects.new('seated', None); link(root)
    root.location = loc; root.rotation_euler.z = yaw
    coat = noisy(f'coat{seed}', *COAT, 6.0, 0.95, 0.2)
    v, t = lathe([(0.0, 0.0), (0.24, 0.02), (0.22, 0.35), (0.2, 0.62), (0.08, 0.7), (0.0, 0.72)], 12)
    body = fast_mesh('torso', v, t, coat, True); body.parent = root
    body.rotation_euler.x = math.radians(-rs.uniform(8, 18))
    head = sphere('head', 0.11, (0, 0.06, 0.82), simple('face', (0.12, 0.09, 0.07), 0.8), 24, 16); head.parent = root
    v, t = lathe([(0.15, 0.0), (0.14, 0.06), (0.1, 0.12), (0.0, 0.14)], 16)
    helmet = fast_mesh('helmet', v, t, simple('helm', (0.07, 0.08, 0.06), 0.6, 0.2), True); helmet.parent = root
    helmet.location = (0, 0.06, 0.86)
    for s_ in (-1, 1):  # pernas dobradas: coxa para a frente, canela para baixo
        tube('leg', [(s_ * 0.1, 0.0, 0.05), (s_ * 0.12, -0.42, 0.38), (s_ * 0.12, -0.6, 0.0)], [0.08, 0.07, 0.06], coat,
             kind='POLY').parent = root
        tube('arm', [(s_ * 0.22, 0.0, 0.6), (s_ * 0.2, -0.25, 0.42), (s_ * 0.05, -0.38, 0.4)], [0.06, 0.05, 0.045], coat,
             kind='POLY').parent = root
    return root
