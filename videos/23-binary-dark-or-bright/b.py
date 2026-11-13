"""B: o planeta claro. O sol parado em cima dele; na planície de sal, a sombra curta e as figuras no calor."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'b1': 4.5, 'b2': 4.0, 'b3': 5.2}


def build_b1():
    """O planeta branco com um sol enorme parado logo acima dele."""
    reset(20)
    world_space((0.02, 0.018, 0.012), 1.0, 0.6)
    sd = (0.45, -0.5, 0.75)                                             # luz do sol no canto de cima, à direita
    sun(4.0, sd, (1.0, 0.97, 0.9))
    p = planet_bright(1.0); p.rotation_euler = (0.25, -0.15, 0)
    atmosphere(1.0, (1.0, 0.96, 0.82), sd, 1.03, power=4, strength=1.0)
    # o sol no canto de cima à direita do quadro, longe da borda do planeta: nada de "boneco de neve"
    look_dir = Vector((0, 3.6, 0.9)).normalized()
    side = look_dir.cross(Vector((0, 0, 1))).normalized()
    up = side.cross(look_dir).normalized()
    sdir = (look_dir + side * math.tan(math.radians(17)) + up * math.tan(math.radians(11))).normalized()
    ico('sundisk', 1.4, tuple(Vector((0, -3.6, -0.35)) + sdir * 30), emission('sundisk', (1.0, 0.95, 0.82), 40.0), 4)
    cam = camera((0, -3.6, -0.35), (0, 0, 0.55), 40)
    def update(t, u):
        u = zoom_after(t, TL.NAME_HOLD, SHOTS['b1'])
        p.rotation_euler.z = 1.4 + 0.05 * t
        cam.location = vlerp((0.0, -3.6, -0.35), (0.0, -2.7, -0.15), ease(u))
        look(cam, (0, 0, 0.55 + 0.1 * u))
    return update


def plain(sun_dir=(0.06, -0.04, 1.0)):
    reset(24)
    world_flat((0.86, 0.88, 0.9), 1.0)
    box('ground', (400, 400, 0.1), (0, 0, -0.05), salt_mat())
    sun(3.2, sun_dir, (1.0, 0.97, 0.9), 1.5)
    fog((0.9, 0.9, 0.88), 6.0, 140.0, 0.9)


def build_b2():
    """O astronauta parado ao meio-dia que não acaba: a sombra é uma poça logo embaixo dos pés."""
    plain()
    astronaut((0, 0, 0), math.radians(-20))
    cam = camera((1.4, -4.2, 1.7), (0, 0, 0.75), 34)
    def update(t, u):
        cam.location = (1.4 - 0.15 * u, -4.2 + 0.4 * u, 1.7)
        look(cam, (0, 0, 0.75))
        return None
    return update


FIGS = [(-14.0, 62.0), (-5.0, 78.0), (4.0, 70.0), (11.0, 88.0), (19.0, 66.0)]
NEAR = 2                        # a figura que chega mais perto na chave
NEAR_AT = 28.0


def build_b3():
    """O horizonte branco com figuras paradas no calor. Na chave, uma delas está na metade da distância."""
    plain()
    figs = [figure((x, y, 0), 0.0, 1.0, (0.1, 0.1, 0.1)) for x, y in FIGS]
    cam = camera((0, 0, 1.7), (0, 100, 1.7), 50)
    x0, y0 = FIGS[NEAR]
    def update(t, u):
        near = t >= TL.TURN
        y = NEAR_AT if near else y0
        figs[NEAR].location = (x0 * y / y0, y, 0)                     # mesma coluna no quadro, só mais perto
        return near
    return update
