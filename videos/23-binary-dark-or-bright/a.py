"""A: o planeta escuro. Só a borda acende; no chão, uma lanterna, e uma forma alta no limite da luz."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'a1': 4.5, 'a2': 4.0, 'a3': 4.5}


def build_a1():
    """O planeta preto contra as estrelas, com uma estrela escondida atrás dele: só um anel fino na borda."""
    reset(20)
    world_space((0.02, 0.015, 0.03), 1.0, 1.4)
    behind = (0.25, 1.0, 0.18)                                           # a estrela está atrás do planeta
    sun(3.0, behind, (0.75, 0.82, 1.0), 0.5)
    p = planet_dark(1.0); p.rotation_euler = (0.25, -0.15, 0)
    atmosphere(1.0, (0.6, 0.72, 1.0), behind, 1.015, power=8, strength=3.0)
    point((-3.0, -4.0, 1.5), 6.0, (0.6, 0.65, 0.8), 1.0)                # luz de estrelas: o relevo aparece de leve
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, TL.NAME_HOLD, SHOTS['a1'])
        p.rotation_euler.z = 0.6 + 0.08 * t
        cam.location = vlerp((0.1, -3.6, 0.1), (0.35, -2.3, 0.3), ease(u))
        look(cam, (0.25 * u, 0, 0.2 * u))
    return update


def dark_world():
    world_space((0.0, 0.0, 0.0), 1.0, 0.5)


def build_a2():
    """No chão, o facho da lanterna varre pedra preta e a poeira no ar."""
    reset(24)
    dark_world()
    h = rocky_ground(2)
    cam = camera((0, 0, 1.6), (0, 6, 0), 30)
    torch = flashlight(cam, 700.0, 30.0)
    rs = np.random.RandomState(7)
    k = 900
    c = np.stack([rs.uniform(-3, 3, k), rs.uniform(1.0, 7.0, k), rs.uniform(0.2, 2.2, k)], 1)
    dust = scatter('dust', *lathe([(0.0, -0.01), (0.008, 0.0), (0.0, 0.01)], 4), c, m=simple('dustm', (0.5, 0.48, 0.45), 0.9))
    def update(t, u):
        sw = 0.9 * math.sin(2 * math.pi * t / 3.6 - 0.6)                # varre da esquerda para a direita e volta
        cam.location = (0.0, 0.25 * u, 1.6)
        look(cam, (sw * 3.0, 5.5 + 0.25 * u, h(sw * 3.0, 5.5) - 0.2))
        dust.location = (0.02 * t, 0.0, -0.03 * t)
        return None
    return update


def build_a3():
    """O facho aponta para frente e pisca; nos apagões a forma chega mais perto, sempre na borda da luz.
    Na chave a lanterna morre, volta um instante com a forma perto, e apaga de vez."""
    reset(24)
    dark_world()
    h = rocky_ground(4)
    cam = camera((0, 0, 1.6), (0, 7, 1.0), 32)
    torch = flashlight(cam, 900.0, 38.0)
    form = figure((0.0, 0.0, 0.0), 0.0, 1.12, eyes=True)
    m, nt = mat('formbody')                                             # preto fosco: a lanterna não clareia a pele
    out(nt, principled(nt, (0.002, 0.002, 0.002), 1.0, spec=0.0).outputs[0])
    for o in form.children:
        if o.name.startswith('figure'):
            o.data.materials[0] = m
        else:                                                          # olhos: dois pontos fracos, não faróis
            em = o.data.materials[0].node_tree.nodes.get('Emission')
            if em:
                em.inputs['Strength'].default_value = 12.0
    def place(d):
        x = 0.17 * d                                                    # na borda direita do facho: as pernas cortam o chão aceso
        form.location = (x, d, h(x, d) - 0.05)
    def update(t, u):
        blink = any(a <= t < b for a, b in TL.BLINKS)
        if t < TL.TURN:
            k = sum(t >= b for _, b in TL.BLINKS)
            place(TL.FORM_DIST[k])
            on = 0.0 if blink else 1.0
            on *= 1.0 if (t * 15) % 7 else 0.7                          # o filamento treme
        else:
            sp = TL.SPUTTER[0] <= t < TL.SPUTTER[1]
            place(TL.SPUTTER_DIST if sp else TL.FORM_DIST[-1])
            on = 0.3 if sp else max(0.0, 1.0 - (t - TL.TURN) / 0.15) * 0.6
        torch.data.energy = 900.0 * on
        cam.location = (0.0, 0.0, 1.6)
        return (round(on, 2), tuple(round(v, 2) for v in form.location))
    return update
