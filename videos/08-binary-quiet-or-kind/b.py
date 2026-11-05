"""B: o planeta simpático. Cidade de casas iguais em tons pastel, gente acenando nas janelas
e uma mesa comprida posta na rua, com um lugar vazio."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'b1': 4.5, 'b2': 4.0, 'b3': 5.2}
PASTEL = ((0.95, 0.75, 0.78), (0.70, 0.90, 0.82), (0.98, 0.90, 0.70), (0.78, 0.80, 0.98))


def flat_figure(name='sil', s=1.0):
    """Silhueta escura achatada, para ficar na frente da janela acesa."""
    v, t = lathe(FIG, 10)
    v = np.asarray(v, np.float32) * np.array([s, 0.08 * s, s], np.float32)
    return fast_mesh(name, v, t, simple('silm', (0.03, 0.025, 0.03), 0.9), True)


def street(n_=9):
    """Duas fileiras de casas iguais, de frente para a rua; devolve as silhuetas das janelas."""
    rs = np.random.RandomState(4)
    roof = simple('roof', (0.55, 0.35, 0.40), 0.8)
    lit = emission('lit', (1.0, 0.82, 0.55), 3.0)
    box('road', (6, 200, 0.05), (0, 60, 0.0), simple('road', (0.55, 0.52, 0.55), 0.9))
    box('grass', (200, 200, 0.05), (0, 60, -0.03), simple('grass', (0.55, 0.78, 0.55), 0.95))
    sil = []
    for side in (-1, 1):
        for k in range(n_):
            x, y = side * 8.0, 6 + k * 9.0
            wall = simple(f'w{side}{k}', PASTEL[(k + (side > 0)) % 4], 0.85)
            box('house', (5.5, 7, 4.5), (x, y, 2.25), wall)
            v = [(-3.0, -3.8, 4.5), (3.0, -3.8, 4.5), (3.0, 3.8, 4.5), (-3.0, 3.8, 4.5), (0, -3.8, 6.6), (0, 3.8, 6.6)]
            r = mesh_from('roof', v, [(0, 4, 5, 3), (1, 2, 5, 4), (0, 1, 4), (3, 5, 2)], roof); r.location = (x, y, 0)
            fx = x - side * 2.77                                       # fachada virada para a rua
            for wy in (-1.6, 1.6):
                box('win', (0.05, 1.3, 1.5), (fx, y + wy, 2.6), lit)
                f = flat_figure(); f.location = (fx - side * 0.06, y + wy, 1.85)
                f.rotation_euler.z = math.pi / 2
                sil.append((f, rs.rand() * 6.28))
    return sil


def build_b1():
    reset(20)
    world_space((0.02, 0.012, 0.02), 1.0)
    sd = (-1.0, -0.3, 0.3)
    sun(4.2, sd, (1, 0.96, 0.94))
    p = planet_kind(1.0); atmosphere(1.0, (1.0, 0.7, 0.8), sd, 1.03, power=4, strength=0.6)
    p.rotation_euler = (0.25, -0.15, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, TL.NAME_HOLD, SHOTS['b1'])
        p.rotation_euler.z = 2.0 - 0.1 * t
        cam.location = vlerp((0.1, -3.6, 0.1), (0.05, -2.3, 0.05), ease(u))
        look(cam, (-0.05 * u, 0, 0))
    return update


def build_b2():
    reset(24)
    pastel_sky()
    sil = street()
    sun(2.5, (-0.5, -0.4, 0.35), (1.0, 0.85, 0.8), 3.0)
    cam = camera((0, 0, 1.7), (0, 30, 2.2), 32)
    def update(t, u):
        y = 1.3 * t
        cam.location = (0.4, y, 1.7)
        look(cam, (-3.0, y + 22, 2.4))
        for f, ph in sil:
            f.rotation_euler.y = 0.22 * math.sin(2 * math.pi * 1.1 * t + ph)      # acenando
    return update


def build_b3():
    reset(24)
    pastel_sky()
    street(6)
    cloth = simple('cloth', (0.95, 0.94, 0.92), 0.8)
    wood = simple('chairw', (0.55, 0.40, 0.30), 0.7)
    plate = simple('plate', (0.98, 0.98, 0.98), 0.3)
    box('table', (1.4, 30, 0.08), (0, 25, 0.8), cloth)
    box('drape', (1.5, 30, 0.5), (0, 25, 0.55), cloth)
    pv, pt = lathe([(0.0, 0.0), (0.2, 0.0), (0.24, 0.03), (0.0, 0.03)], 20)
    fig = simple('guest', (0.03, 0.025, 0.03), 0.9)
    for k in range(14):
        y = 11.5 + k * 2.0
        for side in (-1, 1):
            fast_mesh('plate', pv, pt, plate).location = (side * 0.4, y, 0.85)
            box('chair', (0.5, 0.5, 0.06), (side * 1.1, y, 0.48), wood)
            box('chairback', (0.06, 0.5, 0.9), (side * 1.35, y, 0.9), wood)
            g = figure((side * 1.05, y, 0.0), math.pi / 2 * side, 1.0, (0.03, 0.025, 0.03))
            g.rotation_euler.z = -side * math.pi / 2 + side * 0.5                # sentados virados para a cabeceira vazia
    # a cabeceira vazia, de frente para a câmera
    fast_mesh('plate', pv, pt, plate).location = (0, 10.6, 0.85)
    box('seat', (0.55, 0.55, 0.06), (0, 9.8, 0.48), wood)
    box('seatback', (0.55, 0.06, 0.55), (0, 9.5, 0.75), wood)          # encosto baixo: a mesa aparece por cima
    sun(2.5, (-0.5, -0.4, 0.35), (1.0, 0.85, 0.8), 3.0)
    cam = camera((0, 4.0, 1.7), (0, 14, 0.9), 32)
    def update(t, u):
        y = 4.0 + 1.6 * ease(min(1.0, t / 4.5))
        cam.location = (0, y, 1.7 - 0.25 * ease(min(1.0, t / 4.5)))
        look(cam, (0, y + 10, 0.9))
    return update
