"""A: o planeta lento. O sol parado no horizonte, a chuva parada no ar em volta do módulo de pouso."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'a1': 4.5, 'a2': 4.0}


def build_a1():
    """A borda do planeta com o sol nascendo atrás dela, sem sair do lugar. O zoom é de lente, para o sol não andar."""
    reset(20)
    world_space((0.015, 0.012, 0.02), 1.0)
    ang = math.radians(16.3)                                             # a borda fica a 16,1° do centro, vista da câmera
    far = Vector((math.sin(ang), math.cos(ang), 0.0)) * 60 + Vector((0, -3.6, 0))
    sd = tuple(far.normalized())
    sun(4.5, sd, (1.0, 0.8, 0.55))
    p = planet_slow(1.0); atmosphere(1.0, (1.0, 0.6, 0.3), sd, 1.03, power=4, strength=0.6)
    p.rotation_euler = (0.25, -0.15, 0)
    ico('sundisk', 1.6, tuple(far), emission('sundisk', (1.0, 0.7, 0.4), 20.0), 4)   # metade escondida atrás da borda
    aim = Vector((math.sin(math.radians(11)), math.cos(math.radians(11)), 0.0)) * 3.6 + Vector((0, -3.6, 0))
    cam = camera((0, -3.6, 0), tuple(aim), 40)
    def update(t, u):
        u = zoom_after(t, TL.NAME_HOLD, SHOTS['a1'])
        cam.data.lens = lerp(40, 62, ease(u))
        return round(u, 3)
    return update


def build_a2():
    """O módulo de pouso no amanhecer âmbar, com a chuva suspensa entre a câmera e ele. As gotas quase não descem."""
    reset(24)
    world_flat((0.75, 0.45, 0.22), 0.7)
    ground(((0.42, 0.24, 0.1), (0.62, 0.4, 0.2)))
    sun(3.5, (0.9, 0.2, 0.08), (1.0, 0.62, 0.32), 2.0)
    fog((0.75, 0.48, 0.26), 4.0, 40.0)
    lander((0, 0, 0), math.radians(20))
    rs = np.random.RandomState(5)
    k = 6000
    c = np.stack([rs.uniform(-7, 7, k), rs.uniform(-6, 7, k), rs.uniform(0.0, 4.5, k)], 1)
    c = c[np.hypot(c[:, 0] + 2.6, c[:, 1] + 7.0) > 1.6]                # nada colado na lente
    h, w = 0.11, 0.005
    base = np.array([(0, 0, h), (w, 0, 0), (0, w, 0), (-w, 0, 0), (0, -w, 0), (0, 0, -h)], np.float32)
    tri = np.array([(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (5, 2, 1), (5, 3, 2), (5, 4, 3), (5, 1, 4)])
    v = (c[:, None, :] + base[None]).reshape(-1, 3)
    t_ = (tri[None] + 6 * np.arange(len(c))[:, None, None]).reshape(-1, 3)
    drops = fast_mesh('drops', v, t_, simple('drop', (0.8, 0.78, 0.75), 0.05, emis=(1.0, 0.85, 0.65), emis_str=0.25))
    cam = camera((-2.6, -7.0, 1.6), (0.0, 0.0, 1.5), 32)
    def update(t, u):
        drops.location.z = -0.02 * t                                  # 8 cm em 4s
        cam.location = (-2.6 + 0.05 * u, -7.0 + 0.12 * u, 1.6)
        return None
    return update
