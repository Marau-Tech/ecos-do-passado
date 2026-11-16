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
        'ground': noisy('cobblestone_ground', (0.20, 0.19, 0.17), (0.34, 0.32, 0.28), 5.0),
    }


def summer_light():
    """Luz natural de uma manhã de verão."""
    world_flat((0.48, 0.55, 0.62), 0.8)
    sun(2.0, (-0.35, -0.55, 0.8), (1.0, 0.88, 0.72), 8)


def cobblestones(length=100, width=12, seed=4):
    """Calçamento irregular de pedras, sem aparência de asfalto moderno."""
    rs = np.random.RandomState(seed)
    count = int(length * width * 1.5)
    x = rs.uniform(-width / 2, width / 2, count)
    y = rs.uniform(-5, length, count)
    z = rs.uniform(0.005, 0.025, count)
    pos = np.stack([x, y, z], 1)
    size = rs.uniform(0.12, 0.24, count)
    scale = np.stack([size * rs.uniform(0.8, 1.3, count),
                      size * rs.uniform(0.6, 1.0, count),
                      np.full(count, 0.035)], 1)
    return scatter('cobblestones', CUBE_V, CUBE_T, pos,
                   rs.uniform(0, 0.12, count), scale,
                   simple('cobble_piece', (0.29, 0.27, 0.23), 0.95),
                   smooth=False)


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
        (0, length / 2, -0.14), mats['ground'])

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


def walk_pov(cam, t, start, speed=0.7, pitch=-2.0, seed=2.0):
    """Movimento de câmera em primeira pessoa, independente de Stalingrado."""
    step = math.sin(math.pi * 1.8 * t)
    p = Vector(start) + Vector((0, 1, 0)) * speed * t

    if speed > 0:
        p.z += 0.035 * abs(step) - 0.035 / 2
        p += Vector((1, 0, 0)) * 0.021 * step
    else:
        p.z += 0.01 * math.sin(2 * math.pi * 0.25 * t)

    j = shake(t, 0.012, 1.6, seed)
    target = p + Vector((0, 10, 10 * math.tan(math.radians(pitch)))) + j * 10

    cam.location = p
    look(cam, target, roll=0.012 * step + j.x * 0.5)
