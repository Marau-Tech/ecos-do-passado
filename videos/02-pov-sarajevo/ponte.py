"""Regiao da Ponte Latina e desfecho do atentado de Sarajevo."""
from lib import *
from places import *
import timeline as TL

SHOTS = {'t9': 15.0, 't10': 15.0, 't11': 15.0}


# Geometria (metros). O rio Miljacka corre ao longo de x; a Ponte Latina o atravessa ao
# longo de y. O observador anda pela ponte, junto ao parapeito direito, rumo ao cais norte
# (Appel Quay), onde o carro para na boca da rua lateral, diante dele.
RIVER_S, RIVER_N = -2.0, 26.0      # muros do cais sul e norte
WATER_Z = -3.2                     # superfície da água
BRIDGE_HALF = 3.8                  # meia largura da ponte, por fora dos parapeitos
PARAPET_T, PARAPET_H = 0.40, 0.95  # espessura e altura do parapeito; capa por cima
COPING_W, COPING_H = 0.50, 0.12    # topo da capa: 1,07 m acima do piso
QUAY_N = 40.0                      # fachadas do cais norte
SIDE_STREET = 5.0                  # meia largura da rua lateral, ao norte da ponte
RAIL_X = 2.93                      # a borda da capa do parapeito direito fica a 0,42 m do centro do corpo


def _rotated(fn, yaw, loc):
    """Chama fn() e gira tudo o que ele criar em torno de z (para prédios voltados para y)."""
    before = set(bpy.data.objects)
    fn()
    root = bpy.data.objects.new('quay_block', None)
    link(root)
    root.rotation_euler.z, root.location = yaw, loc
    for o in set(bpy.data.objects) - before - {root}:
        if o.parent is None:
            o.parent = root
            o.matrix_parent_inverse = Matrix.Identity(4)


def bridge_scene():
    """Ponte Latina e cais norte, com o piso da ponte no nível da rua (z = 0)."""
    reset(24)
    summer_light()
    mats = materials()
    rs = np.random.RandomState(21)

    water = noisy('miljacka_water', (0.07, 0.13, 0.14), (0.12, 0.20, 0.21), 1.2, 0.12, 0.05)
    stone = noisy('bridge_stone', (0.36, 0.31, 0.24), (0.50, 0.44, 0.34), 4.0, 0.9, 0.2)
    rail = noisy('bridge_rail', (0.30, 0.27, 0.22), (0.42, 0.38, 0.31), 6.0, 0.85, 0.15)
    wall = noisy('quay_wall', (0.26, 0.23, 0.19), (0.40, 0.36, 0.29), 3.0, 0.9, 0.25)

    # rio e muros dos cais
    box('river', (160, RIVER_N - RIVER_S + 2, 0.2), (0, (RIVER_S + RIVER_N) / 2, WATER_Z - 0.1), water)
    for y, d in ((RIVER_S, -1), (RIVER_N, 1)):
        box('quay_wall', (160, 1.2, -WATER_Z + 0.5), (0, y + d * 0.6, (WATER_Z - 0.5) / 2), wall)

    # ponte: tabuleiro, pilares no rio, parapeitos com capa, pilastras nas cabeceiras
    y0, y1 = RIVER_S - 1.5, RIVER_N          # a cabeceira norte encosta no calçamento do cais
    box('bridge_deck', (2 * BRIDGE_HALF, y1 - y0, 0.9), (0, (y0 + y1) / 2, JOINT_Z - 0.45), stone)
    for py in (5.0, 12.0, 19.0):
        box('bridge_pier', (2 * BRIDGE_HALF + 0.4, 1.6, -WATER_Z), (0, py, WATER_Z / 2 - 0.2), stone)
    for side in (-1, 1):
        x = side * (BRIDGE_HALF - PARAPET_T / 2)
        py0, py1 = y0, y1 + 0.5                       # encontra a mureta do cais
        box('bridge_parapet', (PARAPET_T, py1 - py0, PARAPET_H), (x, (py0 + py1) / 2, PARAPET_H / 2), stone)
        box('bridge_rail_top', (COPING_W, py1 - py0, COPING_H),
            (side * (BRIDGE_HALF - COPING_W / 2 + 0.05), (py0 + py1) / 2, PARAPET_H + COPING_H / 2), rail)
        for y in (y0 + 0.3, y1 - 0.3):
            box('bridge_post', (0.6, 0.6, 1.35), (side * (BRIDGE_HALF - 0.25), y, 0.675), rail)
    inner = BRIDGE_HALF - PARAPET_T
    cobblestones(0, 2 * inner, 31, y0=y0, y1=y1)

    # cais norte (rua ao longo de x) e rua lateral rumo ao norte
    box('quay_base', (160, QUAY_N - RIVER_N, 0.25), (0, (RIVER_N + QUAY_N) / 2, JOINT_Z - 0.125), mats['ground'])
    q = cobblestones(60, QUAY_N - RIVER_N, 32, near=60.0)
    q.rotation_euler.z = -math.pi / 2
    q.location = (-32.0, (RIVER_N + QUAY_N) / 2, 0.0)
    for side in (-1, 1):                    # mureta do cais, interrompida na cabeceira da ponte
        box('quay_parapet', (60, 0.4, 0.95), (side * (BRIDGE_HALF + 30), RIVER_N + 0.3, 0.475), stone)
        box('quay_coping', (60, 0.5, 0.12), (side * (BRIDGE_HALF + 30), RIVER_N + 0.3, 1.01), rail)
    box('side_base', (2 * SIDE_STREET, 60, 0.25), (0, QUAY_N + 30, JOINT_Z - 0.125), mats['ground'])
    sstreet = cobblestones(40, 2 * SIDE_STREET, 33)
    sstreet.location.y = QUAY_N + 8.0

    # fachadas: cais norte voltado para o rio, rua lateral, margem sul ao longe
    def quay_row():
        for xs in (1, -1):
            y = SIDE_STREET + 0.5
            while y < 46:
                w, d, h = rs.uniform(10, 14), rs.uniform(8, 10), rs.uniform(11, 16)
                # coordenadas locais: x local = y do mundo, y local = -x do mundo
                building(QUAY_N + d / 2, -xs * (y + w / 2), w, d, h, 1, mats['cream'] if rs.rand() < 0.6 else mats['brick'])
                pitched_roof(QUAY_N + d / 2, -xs * (y + w / 2), d, w, h, mats['roof'])
                y += w + 0.4
    _rotated(quay_row, math.pi / 2, (0, 0, 0))
    y = QUAY_N + 0.5
    while y < 92:
        for side in (-1, 1):
            w, d, h = rs.uniform(9, 13), rs.uniform(7, 9), rs.uniform(10, 15)
            building(side * (SIDE_STREET + d / 2), y + w / 2, w, d, h, side,
                     mats['cream'] if rs.rand() < 0.6 else mats['brick'])
            pitched_roof(side * (SIDE_STREET + d / 2), y + w / 2, d, w, h, mats['roof'])
        y += rs.uniform(11, 14)
    box('south_quay', (160, 24, 0.25), (0, RIVER_S - 1.2 - 12, JOINT_Z - 0.125), mats['stone'])
    x = -70.0
    while x < 70:                            # margem sul: só volumes, fora de foco
        w, h = rs.uniform(9, 14), rs.uniform(9, 15)
        box('south_bank_house', (w, 9, h), (x + w / 2, RIVER_S - 8.0, h / 2),
            mats['cream'] if rs.rand() < 0.6 else mats['brick'])
        pitched_roof(x + w / 2, RIVER_S - 8.0, w, 9, h, mats['roof'])
        x += w + 0.3

    cam = camera((RAIL_X, 5.0, EYE), (RAIL_X, 25.0, 1.5), 35)
    return cam


CAR_DZ = -0.19        # rodas no calçamento do cais (antes apoiadas a 0,19 m do piso)


def add_car():
    """O carro parado no cais, na boca da rua lateral em que entrou por engano."""
    body = simple('final_car', (0.12, 0.09, 0.055), 0.5)
    metal = simple('final_metal', (0.22, 0.20, 0.16), 0.4, 0.5)
    box('final_car_body', (1.8, 3.0, 1.0), (0.0, 31.0, 1.15 + CAR_DZ), body)
    box('final_car_hood', (1.7, 1.0, 0.55), (0.0, 33.0, 1.4 + CAR_DZ), body)
    box('final_car_screen', (1.3, 0.08, 0.55), (0.0, 30.2, 1.9 + CAR_DZ), metal)
    for x in (-0.95, 0.95):
        for y in (29.9, 32.5):
            w = sphere('final_wheel', 0.36, (x, y, 0.55 + CAR_DZ),
                       simple('final_tire', (0.02, 0.02, 0.02), 0.9), 24, 12)
            w.scale = (0.35, 1.0, 1.0)


def build_t9():
    cam = bridge_scene()
    add_car()
    me = pov_body(cam)
    def update(t, u):
        # anda junto ao parapeito; apoia a mão na capa de pedra e olha o rio (1,6 a 6,8 s),
        # depois solta a mão e volta o olhar para o cais, onde o carro vira na rua errada
        walk_pov(cam, t, (RAIL_X, 5.0, EYE), speed=0.22, pitch=-2.0, seed=15.0,
                 gaze=[(2.0, 6.6, -40.0, 1.2, -45.0)])
        pov_pose(me, cam, t, speed=0.22, actions=[('rail', 1.6, 7.0, 0.9)])
        return None
    return update


def build_t10():
    cam = bridge_scene()
    add_car()
    princip = figure((-3.2, 30.0, 0), yaw=math.pi / 2, s=1.0,
                     color=(0.018, 0.014, 0.012))
    me = pov_body(cam)
    def update(t, u):
        walk_pov(cam, t, (RAIL_X - 0.25, 8.0, EYE), speed=0.0, pitch=-1.5, seed=16.0)
        pov_pose(me, cam, t)
        return None
    return update


def build_t11():
    cam = bridge_scene()
    add_car()
    for x, y in [(-3.0, 27.0), (3.0, 29.0), (-4.0, 34.0), (4.0, 35.0)]:
        figure((x, y, 0), yaw=math.pi, s=0.95,
               color=(0.035, 0.025, 0.02))
    flash_mat = emission('gun_flash', (1.0, 0.72, 0.25), 8.0)
    flash = sphere('shot_flash', 0.12, (-3.0, 30.0, 1.7), flash_mat, 16, 8)
    me = pov_body(cam)
    def update(t, u):
        walk_pov(cam, t, (RAIL_X - 0.45, 10.0, EYE), speed=0.0, pitch=-2.5, seed=17.0)
        # os disparos: proteção instintiva no começo do take
        pov_pose(me, cam, t, actions=[('shield', 0.25, 3.2, 0.3)])
        flash.hide_render = int(t * 4) % 2 == 0
        return None
    return update
