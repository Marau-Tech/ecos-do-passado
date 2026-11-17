"""Sarajevo pela manhã: ruas, fachadas e pessoas aguardando o cortejo."""
from lib import *
from places import *
import timeline as TL

SHOTS = {
    'intro': 15.0,
    't1': 15.0,
}


def crowd(seed=10):
    """Espectadores em roupas civis, vistos como figuras de fundo."""
    positions = [
        (-7.0, 5.0), (7.0, 8.0),
        (-7.1, 12.0), (7.0, 16.0),
        (-7.0, 21.0), (7.1, 25.0),
        (-7.0, 30.0), (7.0, 34.0),
        (-7.1, 40.0), (7.0, 44.0),
    ]
    for i, (x, y) in enumerate(positions):
        figure((x, y, 0), yaw=math.pi if x < 0 else 0,
               s=1.0, color=(0.035, 0.028, 0.022))


def build_intro():
    """Parado na rua, observando Sarajevo antes da passagem do cortejo."""
    reset(24)
    summer_light()
    city_street(100, width=12, seed=3)
    crowd()

    cam = camera((0.0, 0.0, EYE), (0.0, 12.0, EYE), 30)
    me = pov_body(cam)

    def update(t, u):
        # tira o relógio do bolso e confere a hora antes do cortejo
        walk_pov(cam, t, (0.0, 0.0, EYE),
                 speed=0.0, pitch=-1.5, seed=2.0, gaze=[(3.6, 10.4, -40.0, 1.0)])
        pov_pose(me, cam, t, actions=[('watch', 3.0, 11.0, 0.9)])
        return None

    return update


def build_t1():
    """Avança lentamente pela rua, observando os espectadores."""
    reset(24)
    summer_light()
    city_street(110, width=12, seed=3)
    crowd()

    cam = camera((0.0, 5.0, EYE), (0.0, 16.0, EYE), 30)
    me = pov_body(cam)

    def update(t, u):
        # olha o calçamento enquanto anda: a -67 graus o sapato da frente entra pela borda de
        # baixo a cada passo e ainda se vê de 3 a 4 m da rua
        walk_pov(cam, t, (0.0, 5.0, EYE),
                 speed=0.55, pitch=-2.0, seed=3.0, gaze=[(5.8, 9.2, -67.0, 1.2)])
        pov_pose(me, cam, t, speed=0.55)
        return None

    return update
