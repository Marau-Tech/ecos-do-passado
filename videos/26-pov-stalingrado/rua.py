"""A rua em ruínas: parado na neve (intro), andando entre os escombros (t1), clarões no horizonte (t2) e o amanhecer (t5)."""
from lib import *
from places import *
import timeline as TL

SHOTS = {'intro': 5.0, 't1': 7.0, 't2': 7.0, 't5': 8.5}


def build_intro():
    """Parado no meio da rua, a neve caindo, os prédios sem teto sumindo na névoa."""
    reset(24)
    overcast()
    street(80, seed=3)
    flakes = snowfall(5000, (-8, -2, -1), (8, 40, 9), seed=5)
    cam = camera((0.6, 0.0, EYE), (0.6, 10, EYE), 28)

    def update(t, u):
        walk(cam, t, (0.6, 0.0, EYE), speed=0.0, pitch=-2.0, shake_amp=0.012, seed=2.0)
        flakes.location = (0.2 * t, 0, -0.5 * t)
        return None
    return update


def build_t1():
    """Andando entre o entulho, olhando um pouco para o chão: a neve pisada e suja."""
    reset(24)
    overcast()
    street(80, seed=3)
    flakes = snowfall(5000, (-8, 6, -1), (8, 40, 9), seed=6)
    cam = camera((-0.4, 8.0, EYE), (-0.4, 18, 1.0), 26)

    def update(t, u):
        walk(cam, t, (-0.4, 8.0, EYE), speed=1.0, pitch=-12.0, seed=3.0)
        flakes.location = (0.25 * t, 0, -0.55 * t)
        return None
    return update


def build_t2():
    """Mais adiante, já entardecendo: no fim da rua o horizonte pisca laranja, um clarão depois do outro."""
    reset(24)
    world_flat((0.16, 0.15, 0.16), 1.0)
    sun(0.35, (0.2, -0.7, 0.35), (1.0, 0.75, 0.55), 20)
    fog((0.24, 0.22, 0.22), 10, 170, 0.55)
    street(110, seed=7)
    glow_m = emission('glow', (1.0, 0.45, 0.15), 0.0)
    glow = box('horizon', (300, 1, 60), (0, 150, 10), glow_m)
    lights = [point((x, 130, 12), 0.0, (1.0, 0.55, 0.25), 6.0) for x in (-40, 0, 35)]
    cam = camera((0.3, 20.0, EYE), (0.3, 30, EYE), 30)

    def update(t, u):
        walk(cam, t, (0.3, 20.0, EYE), speed=0.7, pitch=1.0, seed=4.0)
        k = max([math.exp(-max(0.0, t - f) * 3.5) if t >= f else 0.0 for f in TL.FLASHES] + [0.0])
        glow_m.node_tree.nodes['Emission'].inputs['Strength'].default_value = 0.3 + 9.0 * k
        for i, l in enumerate(lights):
            l.data.energy = 2e6 * k * (0.6 + 0.4 * ((i + int(t * 3)) % 2))
        return None
    return update


def build_t5():
    """De volta à rua ao amanhecer: sem neve caindo, luz baixa e quente, névoa e silêncio."""
    reset(24)
    world_flat((0.42, 0.33, 0.28), 1.0)
    sun(2.2, (-0.2, -0.9, 0.18), (1.0, 0.72, 0.48), 3)
    fog((0.55, 0.45, 0.38), 5, 60, 0.9)
    street(80, seed=11)
    cam = camera((0.0, 4.0, EYE), (0.0, 14, EYE), 28)

    def update(t, u):
        walk(cam, t, (0.0, 4.0, EYE), speed=0.6, pitch=3.0, step_hz=1.4, seed=5.0, yaw=-0.12, pan=0.035)
        return None
    return update
