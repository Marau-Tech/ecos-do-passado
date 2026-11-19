"""Elementos urbanos de Sarajevo em junho de 1914."""
from lib import *

EYE = 1.65

# Materiais com pequenas variações naturais de cor e relevo.
def noisy(name, a, b, scale=2.0, rough=0.85, bump=0.12):
    m, nt = mat(name)
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    nz = n(nt, 'ShaderNodeTexNoise', Scale=scale, Detail=5.0, Roughness=0.65)
    L(nt, pos, nz.inputs['Vector'])
    c = ramp(nt, [(0.35, a), (0.65, b)], nz.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=bump, Distance=0.025)
    L(nt, nz.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, c, rough, spec=0.3, normal=bp.outputs[0]).outputs[0])
    return m


def materials():
    return {
        'stone': noisy('sarajevo_stone', (0.22, 0.21, 0.19), (0.38, 0.36, 0.32), 3.0),
        'plaster': noisy('sarajevo_plaster', (0.48, 0.39, 0.28), (0.72, 0.61, 0.45), 2.0),
        'cream': simple('facade_cream', (0.72, 0.63, 0.49), 0.9),
        'brick': simple('facade_ochre', (0.48, 0.25, 0.14), 0.9),
        'roof': simple('roof_tile', (0.19, 0.12, 0.09), 0.85),
        'wood': simple('dark_wood', (0.12, 0.075, 0.045), 0.8),
        'metal': simple('dark_metal', (0.10, 0.11, 0.10), 0.35, 0.65),
        'glass': simple('window_glass', (0.055, 0.075, 0.085), 0.25),
        'ground': noisy('cobblestone_ground', (0.06, 0.055, 0.045), (0.12, 0.105, 0.085), 14.0, 0.95, 0.3),
    }


def summer_light():
    """Luz natural de uma manhã de verão."""
    world_flat((0.48, 0.55, 0.62), 0.8)
    sun(2.0, (-0.35, -0.55, 0.8), (1.0, 0.88, 0.72), 8)


# Paralelepípedos assentados em fiadas: cada pedra tem contorno chanfrado, bisel e topo
# levemente abaulado, e fica cravada no leito de areia (as juntas ficam 1 a 2 cm abaixo).
# Tudo vira uma malha só; longe da câmera, as pedras usam um contorno mais simples.
_OCT = np.array([(1, 1, 0, -1), (1, 1, -1, 0), (-1, 1, 1, 0), (-1, 1, 0, -1),
                 (-1, -1, 0, 1), (-1, -1, 1, 0), (1, -1, -1, 0), (1, -1, 0, 1)], np.float32)
_QUAD = np.array([(1, 1, 0, 0), (-1, 1, 0, 0), (-1, -1, 0, 0), (1, -1, 0, 0)], np.float32)
JOINT_Z = -0.012          # topo do leito (fundo das juntas)


def _stone_faces(k):
    """Triângulos de uma pedra com contorno de k pontos: base, bisel, topo, centro."""
    B, O, T, C = 0, k, 2 * k, 3 * k
    f = []
    for i in range(k):
        j = (i + 1) % k
        f += [(B + i, B + j, O + j), (B + i, O + j, O + i),
              (O + i, O + j, T + j), (O + i, T + j, T + i),
              (T + i, T + j, C)]
    return np.array(f, np.int32)


def _stones(cx, cy, hx, hy, yaw, rs, outline):
    """Vértices (N, 3k+1, 3), atributos de variação e de borda, para N pedras."""
    N, k = len(cx), len(outline)
    corner = np.arange(k) // (2 if k == 8 else 1)        # os dois pontos de um canto chanfrado
    nc = corner.max() + 1
    per = lambda lo, hi: rs.uniform(lo, hi, (N, nc))[:, corner]
    ch = np.minimum(hx, hy)[:, None] * per(0.12, 0.24)             # chanfro irregular
    px = outline[None, :, 0] * hx[:, None] + outline[None, :, 2] * ch + per(-0.008, 0.008)
    py = outline[None, :, 1] * hy[:, None] + outline[None, :, 3] * ch + per(-0.008, 0.008)
    top = rs.uniform(-0.003, 0.007, (N, 1))
    tilt = rs.uniform(-0.035, 0.035, (N, 2))
    bev = rs.uniform(0.010, 0.016, (N, 1))
    ins = per(0.010, 0.022)
    r = np.hypot(px, py)
    shrink = np.clip(1 - ins / np.maximum(r, 1e-3), 0.5, 1)
    ring = lambda sx, z: np.stack([px * sx, py * sx, np.broadcast_to(z, px.shape)], -1)
    V = np.concatenate([ring(0.96, -0.04), ring(1.0, top - bev), ring(shrink, top),
                        np.stack([np.zeros((N, 1)), np.zeros((N, 1)),
                                  top + rs.uniform(0.003, 0.009, (N, 1))], -1)], 1)
    V[..., 2] += (V[..., 0] * tilt[:, :1] + V[..., 1] * tilt[:, 1:]) * (V[..., 2] > -0.03)
    c, s = np.cos(yaw)[:, None], np.sin(yaw)[:, None]
    X = V[..., 0] * c - V[..., 1] * s + cx[:, None]
    Y = V[..., 0] * s + V[..., 1] * c + cy[:, None]
    V = np.stack([X, Y, V[..., 2]], -1)
    var = np.repeat(rs.rand(N, 1), V.shape[1], 1)
    edge = np.concatenate([np.full((N, k), 1.0), np.full((N, k), 0.55),
                           np.zeros((N, k)), np.zeros((N, 1))], 1)
    return V, var, edge


def _courses(x0, x1, y0, y1, rs):
    """Fiadas transversais: profundidade e comprimento variados, juntas desencontradas."""
    cx, cy, hx, hy = [], [], [], []
    y = y0
    while y < y1:
        d = rs.uniform(0.105, 0.145)
        x = x0 - rs.uniform(0, 0.2)
        while x < x1:
            ln = rs.uniform(0.14, 0.24)
            a, b = max(x, x0), min(x + ln, x1)
            if b - a > 0.06:
                dd = d * rs.uniform(0.9, 1.0)
                cx.append((a + b) / 2); cy.append(y + d / 2 + rs.uniform(-0.004, 0.004))
                hx.append((b - a) / 2); hy.append(dd / 2)
            x += ln + rs.uniform(0.010, 0.018)
        y += d + rs.uniform(0.010, 0.017)
    return [np.array(v, np.float32) for v in (cx, cy, hx, hy)]


def cobble_material():
    m, nt = mat('cobble_sett')
    var = n(nt, 'ShaderNodeAttribute', {'attribute_name': 'cobble_var'}).outputs['Fac']
    edge = n(nt, 'ShaderNodeAttribute', {'attribute_name': 'cobble_edge'}).outputs['Fac']
    # calcário e arenito gastos: cinzas quentes e frios, algumas pedras mais escuras
    tone = ramp(nt, [(0.0, (0.085, 0.08, 0.072)), (0.18, (0.13, 0.12, 0.105)),
                     (0.45, (0.17, 0.16, 0.14)), (0.7, (0.15, 0.15, 0.145)),
                     (0.88, (0.21, 0.19, 0.16)), (1.0, (0.24, 0.215, 0.18))], var).outputs[0]
    co = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    grain = n(nt, 'ShaderNodeTexNoise', Scale=22.0, Detail=8.0, Roughness=0.6)
    L(nt, co, grain.inputs['Vector'])
    g = n(nt, 'ShaderNodeMapRange', From_Min=0.3, From_Max=0.7, To_Min=0.72, To_Max=1.18)
    L(nt, grain.outputs['Fac'], g.inputs['Value'])
    mul = n(nt, 'ShaderNodeMix', {'data_type': 'RGBA', 'blend_type': 'MULTIPLY'}, Factor=1.0)
    L(nt, tone, mul.inputs['A'])
    L(nt, g.outputs[0], mul.inputs['B'])
    wear = n(nt, 'ShaderNodeTexNoise', Scale=0.35, Detail=3.0, Roughness=0.5)   # manchas largas da rua
    L(nt, co, wear.inputs['Vector'])
    wr = n(nt, 'ShaderNodeMapRange', From_Min=0.35, From_Max=0.65, To_Min=0.8, To_Max=1.1)
    L(nt, wear.outputs['Fac'], wr.inputs['Value'])
    mul2 = n(nt, 'ShaderNodeMix', {'data_type': 'RGBA', 'blend_type': 'MULTIPLY'}, Factor=1.0)
    L(nt, mul.outputs['Result'], mul2.inputs['A'])
    L(nt, wr.outputs[0], mul2.inputs['B'])
    mul = mul2
    dirt = n(nt, 'ShaderNodeMix', {'data_type': 'RGBA'})
    dirt.inputs['B'].default_value = (0.085, 0.075, 0.06, 1)
    de = n(nt, 'ShaderNodeMath', {'operation': 'MULTIPLY'})
    de.inputs[1].default_value = 0.6
    L(nt, edge, de.inputs[0])
    L(nt, de.outputs[0], dirt.inputs['Factor'])
    L(nt, mul.outputs['Result'], dirt.inputs['A'])
    rough = n(nt, 'ShaderNodeMapRange', To_Min=0.72, To_Max=0.95)
    L(nt, edge, rough.inputs['Value'])
    fine = n(nt, 'ShaderNodeTexNoise', Scale=90.0, Detail=6.0, Roughness=0.7)
    L(nt, co, fine.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.22, Distance=0.004)
    L(nt, fine.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, dirt.outputs['Result'], rough.outputs[0], spec=0.35,
                       normal=bp.outputs[0]).outputs[0])
    return m


def cobblestones(length=100, width=12, seed=4, near=45.0, y0=-8.0, y1=None):
    """Calçamento de paralelepípedos de 1914: fiadas transversais e duas linhas de sarjeta
    junto ao meio-fio. Até `near` metros as pedras têm contorno chanfrado; depois, simples."""
    rs = np.random.RandomState(seed)
    y1 = length + 12 if y1 is None else y1
    gut = 0.36
    groups = []
    for a, b, outline in ((y0, min(near, y1), _OCT), (min(near, y1), y1, _QUAD)):
        if b <= a:
            continue
        cx, cy, hx, hy = _courses(-width / 2 + gut, width / 2 - gut, a, b, rs)
        groups.append((cx, cy, hx, hy, rs.uniform(-0.05, 0.05, len(cx)), outline))
        for side in (-1, 1):                       # sarjeta: pedras no sentido da rua
            for col in range(2):
                # uma fiada só, gerada ao longo de y e depois girada para o sentido da rua
                gy, gx, gl, gw = _courses(a, b, -0.06, -0.05, rs)
                xc = side * (width / 2 - 0.09 - col * 0.175)
                groups.append((xc + gx * 0.3, gy, np.minimum(gw, 0.075), gl,
                               rs.uniform(-0.02, 0.02, len(gx)), outline))
    Vs, Fs, Var, Edge, off = [], [], [], [], 0
    for cx, cy, hx, hy, yaw, outline in groups:
        if len(cx) == 0:
            continue
        V, var, edge = _stones(cx, cy, hx, hy, yaw, rs, outline)
        nv = V.shape[1]
        F = _stone_faces(len(outline))
        Fs.append((F[None] + (np.arange(len(cx)) * nv + off)[:, None, None]).reshape(-1, 3))
        Vs.append(V.reshape(-1, 3)); Var.append(var.ravel()); Edge.append(edge.ravel())
        off += len(cx) * nv
    ob = fast_mesh('cobblestones', np.concatenate(Vs), np.concatenate(Fs), cobble_material(), smooth=True)
    for name, vals in (('cobble_var', Var), ('cobble_edge', Edge)):
        at = ob.data.attributes.new(name, 'FLOAT', 'POINT')
        at.data.foreach_set('value', np.concatenate(vals).astype(np.float32))
    return ob


# Cubo com origem na base, útil para fachadas e elementos urbanos.
CUBE_V = [
    (-.5, -.5, 0), (.5, -.5, 0), (.5, .5, 0), (-.5, .5, 0),
    (-.5, -.5, 1), (.5, -.5, 1), (.5, .5, 1), (-.5, .5, 1)
]
CUBE_T = [
    (0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
    (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
    (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)
]


def pitched_roof(x, y, depth, width, height, material):
    """Telhado de duas aguas, com beiral e cumeeira elevada."""
    half = depth / 2 + 0.45
    ridge = height + 1.35
    eave = height + 0.18
    y0 = y - width / 2 - 0.35
    y1 = y + width / 2 + 0.35

    verts = [
        (x - half, y0, eave),
        (x,        y0, ridge),
        (x + half, y0, eave),
        (x - half, y1, eave),
        (x,        y1, ridge),
        (x + half, y1, eave),
    ]
    faces = [
        (0, 1, 4, 3),
        (1, 2, 5, 4),
        (0, 2, 1),
        (3, 4, 5),
    ]
    return mesh_from("pitched_roof", verts, faces, material)


def building(x, y, width, depth, height, side, material):
    """Edificio historico com fachada em relevo e janelas detalhadas."""
    box('facade', (depth, width, height),
        (x, y, height / 2), material)

    inner = x - side * depth / 2
    front = inner - side * 0.10

    stone = simple('facade_stone_detail', (0.48, 0.42, 0.33), 0.88)
    dark = simple('window_shadow', (0.025, 0.035, 0.04), 0.95)
    trim = simple('window_frame', (0.24, 0.16, 0.09), 0.82)
    metal = simple('balcony_iron', (0.075, 0.085, 0.08), 0.38, 0.65)

    # Base de pedra e cornija superior.
    box('building_plinth', (0.30, width + 0.25, 0.65),
        (front, y, 0.42), stone)
    box('upper_cornice', (0.42, width + 0.55, 0.30),
        (front, y, height - 0.25), stone)
    box('lower_cornice', (0.22, width + 0.25, 0.18),
        (front, y, 3.35), stone)

    # Pilastras verticais nas extremidades da fachada.
    for offset in (-width / 2 + 0.25, width / 2 - 0.25):
        box('facade_pilaster', (0.25, 0.30, height - 1.0),
            (front - side * 0.04, y + offset, height / 2), stone)

    rows = max(1, int((height - 2.2) // 2.8))
    cols = max(1, int(width // 2.8))

    for row in range(rows):
        for col in range(cols):
            wy = y - width / 2 + 1.4 + col * 2.8
            wz = 2.0 + row * 2.8

            # Recuo escuro da janela.
            box('window_recess', (0.09, 1.05, 1.50),
                (front, wy, wz), dark)

            # Molduras laterais.
            for offset in (-0.55, 0.55):
                box('window_jamb', (0.16, 0.12, 1.68),
                    (front - side * 0.09, wy + offset, wz), trim)

            # Peitoril e verga.
            box('window_sill', (0.24, 1.30, 0.16),
                (front - side * 0.12, wy, wz - 0.82), stone)
            box('window_lintel', (0.20, 1.28, 0.16),
                (front - side * 0.10, wy, wz + 0.82), stone)

            # Divisoes da esquadria.
            box('window_mullion', (0.10, 0.07, 1.35),
                (front - side * 0.14, wy, wz), trim)
            box('window_crossbar', (0.10, 0.92, 0.07),
                (front - side * 0.14, wy, wz + 0.10), trim)

            # Pequena sacada de ferro em algumas janelas.
            if row == 0 and col % 2 == 0:
                balcony_y = wy
                balcony_x = front - side * 0.35
                box('balcony_slab', (0.65, 1.35, 0.12),
                    (balcony_x, balcony_y, wz - 0.58), stone)

                rail_x = balcony_x - side * 0.28
                box('balcony_top_rail', (0.08, 1.35, 0.07),
                    (rail_x, balcony_y, wz - 0.05), metal)
                for j in range(5):
                    by = balcony_y - 0.55 + j * 0.275
                    box('balcony_spindle', (0.07, 0.055, 0.50),
                        (rail_x, by, wz - 0.32), metal)


def city_street(length=100, width=12, seed=3):
    """Rua urbana de Sarajevo, com calçamento e edifícios preservados."""
    rs = np.random.RandomState(seed)
    mats = materials()

    box('street_base', (width, length + 20, 0.25),
        (0, length / 2, JOINT_Z - 0.125), mats['ground'])

    # Calçadas laterais.
    for side in (-1, 1):
        box('sidewalk', (2.2, length + 20, 0.28),
            (side * (width / 2 + 1.1), length / 2, 0.02),
            mats['stone'])

    cobblestones(length, width, seed + 10)

    y = -8.0
    while y < length + 12:
        for side in (-1, 1):
            depth = rs.uniform(7.0, 10.0)
            w = rs.uniform(9.0, 14.0)
            h = rs.uniform(9.0, 17.0)
            x = side * (width / 2 + depth / 2)
            material = mats['cream'] if rs.rand() < 0.65 else mats['brick']

            building(x, y + w / 2, w, depth, h, side, material)

            # Telhado historico de duas aguas.
            pitched_roof(x, y + w / 2, depth, w, h, mats['roof'])

        y += rs.uniform(12.0, 17.0)


def look_dir(t, pitch, gaze=()):
    """Pitch e giro da cabeça (graus) no tempo t.
    gaze: [(início, fim, pitch[, rampa[, giro]])]; giro negativo vira a cabeça para a direita."""
    p, y = pitch, 0.0
    for item in gaze:
        a, b, deg = item[:3]
        r = item[3] if len(item) > 3 else 0.9
        yaw = item[4] if len(item) > 4 else 0.0
        w = min(1.0, max(0.0, (t - a) / r), max(0.0, (b - t) / r))
        w = w * w * (3 - 2 * w)
        p += (deg - p) * w
        y += (yaw - y) * w
    return p, y


def walk_pov(cam, t, start, speed=0.7, pitch=-2.0, seed=2.0, gaze=()):
    """Movimento de câmera em primeira pessoa, independente de Stalingrado.

    gaze dirige olhares (relógio, chão): a cabeça gira em torno do pescoço, então o olho
    desce e avança um pouco, e o corpo do personagem POV fica no lugar. Sem gaze, a câmera
    é a mesma de antes."""
    step = math.sin(math.pi * 1.8 * t)
    p = Vector(start) + Vector((0, 1, 0)) * speed * t

    if speed > 0:
        p.z += 0.035 * abs(step) - 0.035 / 2
        p += Vector((1, 0, 0)) * 0.021 * step
    else:
        p.z += 0.01 * math.sin(2 * math.pi * 0.25 * t)

    aim = Vector((0, 10, 10 * math.tan(math.radians(pitch))))
    if gaze:
        from pov.motion import head_eye
        pt, yw = look_dir(t, pitch, gaze)
        if pt != pitch or yw != 0.0:
            d = (head_eye((0, 0, 0), math.radians(pt), math.radians(yw), 0.0)
                 - head_eye((0, 0, 0), math.radians(pitch)))
            p += Vector(tuple(d))
            r = math.radians(yw)
            aim = Vector((-10 * math.sin(r), 10 * math.cos(r), 10 * math.tan(math.radians(pt))))

    j = shake(t, 0.012, 1.6, seed)
    target = p + aim + j * 10

    cam.location = p
    look(cam, target, roll=0.012 * step + j.x * 0.5)


def pov_body(cam, ground=0.0):
    """Corpo do civil de 1914 preso à câmera (engine/pov). POV_BODY=0 desliga, para comparar."""
    if os.environ.get('POV_BODY', '1') == '0':
        return None
    from pov import create_character
    return create_character(cam, 'sarajevo_civilian_1914', ground=ground)


def pov_pose(me, cam, t, speed=0.0, actions=()):
    """Pose do corpo no tempo t, depois do walk_pov do mesmo frame. Rumo fixo em +Y."""
    if me is not None:
        me.update(t, cam, speed=speed, heading=0.0, actions=actions)
