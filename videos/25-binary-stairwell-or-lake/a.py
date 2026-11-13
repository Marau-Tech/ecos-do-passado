"""A: a escada. O vão visto de cima sumindo no escuro, a descida com as luzes que seguem você e o patamar B-212."""
from lib import *
from places import *
import timeline as TL

SHOTS = {'a1': 4.5, 'a2': 4.0, 'a3': 4.5}


def build_a1():
    """De cima, olhando reto para baixo pelo vão: só os três primeiros andares acesos. O zoom é de lente."""
    reset(20)
    world_flat((0, 0, 0), 0.0)
    _, lamps = stairwell(48, lamp_at=(0, 4, 8), top=6.0, doors=False)
    for q, lp in lamps.items():
        set_lamp(lp, 1.0 - 0.25 * q / 4)
    cam = camera((0.25, -0.2, 4.2), (0.0, 0.05, -40.0), 20)
    cam.rotation_euler = (math.radians(-2.5), math.radians(2.0), math.radians(6))
    def update(t, u):
        u = zoom_after(t, TL.NAME_HOLD, SHOTS['a1'])
        cam.data.lens = lerp(20, 46, ease(u))
        return round(u, 3)
    return update


def build_a2():
    """Descendo um lance: a luz de baixo acende quando você chega, e a de cima, atrás, apaga."""
    reset(24)
    world_flat((0, 0, 0), 0.0)
    _, lamps = stairwell(12, lamp_at=range(12), top=1.6)
    z0 = corner_z(4)
    for q, lp in lamps.items():
        set_lamp(lp, 0.0)
    cam = camera((1.2, 1.35, z0 + 1.6), (-2.0, 1.2, z0 + 0.9), 26)
    def update(t, u):
        set_lamp(lamps[4], 1.0 if t < TL.LIGHT_OFF else 0.0)
        set_lamp(lamps[5], 1.0 if t >= TL.LIGHT_ON else 0.0)
        x = lerp(1.2, -0.9, u)
        z = z0 + 1.6 - Q * min(1.0, max(0.0, (V - x) / (2 * V))) if x < V else z0 + 1.6
        bob = 0.03 * abs(math.sin(math.pi * 1.8 * t))
        cam.location = (x, 1.35, z + bob)
        look(cam, (x - 1.7, -0.2, z - 1.5))
        return None
    return update


def build_a3():
    """Parado no patamar, de frente para a porta: a luz enfraquece e, na chave, sobra só ela piscando."""
    reset(24)
    world_flat((0, 0, 0), 0.0)
    _, lamps = stairwell(12, lamp_at=(7, 8, 9), top=1.6)
    z = corner_z(8)
    sign(TL.FLOOR, (S - 0.02, 0.3, z + 1.55), 0.2)
    cam = camera((0.1, 1.1, z + 1.45), (S, 0.95, z + 1.2), 24)
    rs = np.random.RandomState(7)
    flick = rs.rand(200)
    def update(t, u):
        if t < TL.TURN:
            k = 1.0 - 0.6 * (t / TL.TURN) ** 1.5
            set_lamp(lamps[7], max(0.0, 0.5 - t / TL.TURN))
            set_lamp(lamps[9], max(0.0, 0.5 - t / TL.TURN))
        else:
            i = int((t - TL.TURN) * 15)
            k = 0.4 if flick[i % 200] > 0.45 else 0.04
            set_lamp(lamps[7], 0.0); set_lamp(lamps[9], 0.0)
        set_lamp(lamps[8], k)
        return None
    return update
