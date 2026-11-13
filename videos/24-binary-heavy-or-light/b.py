"""B: o planeta leve. As pedras soltas em volta dele, a poeira que sobe e não desce, e a corda presa na
cintura até uma estaca, que perde um fio na chave."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'b1': 4.5, 'b2': 4.0, 'b3': 5.2}
PALE = ((0.32, 0.31, 0.36), (0.58, 0.56, 0.62))


def build_b1():
    reset(20)
    world_space((0.015, 0.012, 0.02), 1.0)
    sd = (-1.0, -0.4, 0.4)
    sun(4.2, sd, (1, 0.98, 0.96))
    p = planet_light(1.0)
    p.rotation_euler = (0.25, -0.15, 0)
    rocks = orbit_rocks(36, 1.3, 1.9, (0, 0, 0), (0.025, 0.08), seed=7)
    cam = camera((0.1, -4.2, 0.35), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, TL.NAME_HOLD, SHOTS['b1'])
        p.rotation_euler.z = 0.1 * t
        move_rocks(rocks, t, tilt=0.3)
        cam.location = vlerp((0.1, -4.2, 0.35), (0.35, -3.0, 0.3), ease(u))
        look(cam, (0.2 * u, 0, 0))
    return update


def light_ground(r=40.0):
    m = ground(PALE, 'pumice', bump=0.5, scale=0.9)
    g = sphere('ground', r, (0, 0, -r), m, 256, 128)
    return g


def build_b2():
    """Olhando para o céu, com a curva do horizonte embaixo. A poeira sobe devagar e não cai."""
    reset(24)
    world_space((0.05, 0.035, 0.08), 1.2, 1.6)
    light_ground()
    sun(3.2, (-0.6, -0.5, 0.25), (1, 0.97, 0.92), 0.6)
    gas = planet_light(9.0, (-18, 70, 26))                           # um vizinho enorme no céu
    gas.rotation_euler = (0.4, 0.2, 0)
    rs = np.random.RandomState(11)
    k = 900
    c = np.stack([rs.uniform(-4, 4, k), rs.uniform(1.0, 9.0, k), rs.uniform(-0.2, 3.5, k)], 1)
    v, t_ = lathe([(0.0, -0.5), (1.0, 0.0), (0.0, 0.5)], 4)
    s = rs.uniform(0.004, 0.014, k)
    dust = scatter('dust', v, t_, c, rs.uniform(0, 6.28, k), s, simple('dustm', (0.7, 0.68, 0.72), 0.9))
    rp = np.stack([rs.uniform(-3, 3, 14), rs.uniform(2.5, 8, 14), rs.uniform(0.3, 2.5, 14)], 1)
    stones = pebbles('floaters', 14, (-3, 3, 2.5, 8), (0.05, 0.14), rock_mat('stone', (0.5, 0.48, 0.54)), 4, flat=0.8)
    cam = camera((0.0, 0.0, 1.7), (0.0, 10.0, 2.2), 24)
    def update(t, u):
        dust.location.z = 0.09 * t                                  # sobe 36 cm em 4s
        stones.location.z = 1.0 + 0.04 * t
        cam.location = Vector((0.0, 0.0, 1.7)) + shake(t, 0.004, 1.5)
        look(cam, (0.0, 10.0, 2.2 + 0.25 * u))
        return None
    return update


A, B = Vector((0.0, 0.15, 1.12)), Vector((0.32, 1.35, 0.14))       # cintura e topo da estaca
BREAK = 0.52                                                     # onde o fio arrebenta, na corda
TURNS = 11


def strand_pts(k, s0, s1, npts, curl=0.0, side=1):
    """pontos de um dos 3 fios trançados, de s0 a s1 ao longo da corda"""
    ax = (B - A).normalized()
    u_ = ax.cross(Vector((0, 0, 1))).normalized(); v_ = ax.cross(u_)
    out_ = []
    for s in np.linspace(s0, s1, npts):
        th = 2 * math.pi * TURNS * s + k * 2 * math.pi / 3
        r = 0.016
        p = A + (B - A) * s + (u_ * math.cos(th) + v_ * math.sin(th)) * r
        if curl:
            d = max(0.0, 1 - abs(s - BREAK) / 0.12)                   # a ponta solta se afasta da corda e enrola
            p = p + (u_ * side * 0.6 + v_ * 0.8).normalized() * curl * d ** 2
        out_.append(tuple(p))
    return out_


def build_b3():
    """Olhando para baixo: o peito do traje, as botas soltas no ar, a corda esticada da cintura até a estaca
    na rocha. Na chave, um fio arrebenta e o pedaço sai flutuando."""
    reset(28)
    world_space((0.02, 0.015, 0.03), 0.6)
    box('ground', (400, 400, 0.1), (0, 0, -0.05), ground(PALE, 'pumice', bump=0.5, scale=0.9))
    pebbles('rocks', 600, (-3, 3, -1.5, 4), (0.01, 0.08), rock_mat('rocks', (0.52, 0.5, 0.56)), 9)
    sun(3.5, (-0.5, 0.3, 1.0), (1, 0.97, 0.92), 1.0)
    point((0.0, 0.4, 2.2), 6.0, (0.9, 0.95, 1.0), 0.3)              # luz do capacete
    sm = suit_mat()
    tor = ico('torso', 0.2, (0, -0.12, 1.45), sm, 3); tor.scale = (1.15, 0.8, 1.4)
    box('belt', (0.4, 0.26, 0.07), (0, -0.04, 1.12), simple('belt', (0.15, 0.15, 0.16), 0.5, 0.4))
    for sx in (-1, 1):
        tube('leg', [(sx * 0.1, 0.0, 1.08), (sx * 0.14, 0.38, 0.72), (sx * 0.12, 0.42, 0.4)], [0.08, 0.07, 0.065], sm)
        b_ = ico('boot', 0.08, (sx * 0.12, 0.47, 0.33), simple('boot', (0.25, 0.25, 0.27), 0.6), 2); b_.scale = (1.0, 1.6, 0.8)
    steel = simple('steel', (0.55, 0.56, 0.6), 0.3, 0.9)
    tube('stake', [(B.x, B.y, -0.2), (B.x, B.y, 0.05), (B.x, B.y + 0.0, B.z)], [0.035, 0.035, 0.03], steel, kind='POLY')
    box('plate', (0.2, 0.2, 0.025), (B.x, B.y, 0.012), steel)
    ico('knob', 0.04, (B.x, B.y, B.z), steel, 2)
    for k in range(4):                                             # parafusos da placa
        a = k * math.pi / 2 + 0.78
        ico('bolt', 0.015, (B.x + 0.07 * math.cos(a), B.y + 0.07 * math.sin(a), 0.03), simple('boltm', (0.2, 0.2, 0.22), 0.4, 0.8), 1)
    rope = simple('rope', (0.8, 0.32, 0.06), 0.8)
    whole = [tube('strand', strand_pts(k, 0, 1, 90), [0.014] * 90, rope, res=2, bevel=2) for k in range(3)]
    lo = tube('strand_lo', strand_pts(2, 0, BREAK - 0.004, 50), [0.014] * 50, rope, res=2, bevel=2)
    hi = tube('strand_hi', strand_pts(2, BREAK + 0.04, 1, 50), [0.014] * 50, rope, res=2, bevel=2)
    bit_pts = strand_pts(2, BREAK - 0.004, BREAK + 0.04, 8)
    bit = tube('bit', [tuple(Vector(p) - Vector(bit_pts[4])) for p in bit_pts], [0.014] * 8, rope, res=2, bevel=2)
    bit.location = bit_pts[4]
    # fiapos soltos no ponto que vai arrebentar
    rs = np.random.RandomState(3)
    mid = A + (B - A) * BREAK
    for i in range(9):
        d = Vector(rs.uniform(-1, 1, 3)).normalized()
        o0 = mid + (B - A) * rs.uniform(-0.05, 0.05)
        tube('fiber', [tuple(o0), tuple(o0 + d * 0.025), tuple(o0 + d * 0.045 + Vector((0, 0, 0.01)))], [0.0025] * 3, rope, res=2, bevel=1)
    cam = camera((0.0, 0.12, 1.9), (0.2, 1.0, 0.0), 26)
    def update(t, u):
        broke = t >= TL.TURN
        a = max(0.0, t - TL.TURN)
        whole[2].hide_render = broke
        for o in (lo, hi, bit):
            o.hide_render = not broke
        if broke:
            c = 0.1 * (1 - math.exp(-a * 3)) + 0.01 * a
            set_tube(lo, strand_pts(2, 0, BREAK - 0.004, 50, c, 1), [0.014] * 50)
            set_tube(hi, strand_pts(2, BREAK + 0.04, 1, 50, c, -1), [0.014] * 50)
            bit.location = Vector(bit_pts[4]) + Vector((0.12, -0.04, 0.22)) * a
            bit.rotation_euler = (1.3 * a, 0.7 * a, 0.4 * a)
        cam.location = Vector((0.0, 0.12, 1.9)) + shake(t, 0.004, 1.2)
        look(cam, (0.2, 1.0, 0.0))
        return None
    return update
