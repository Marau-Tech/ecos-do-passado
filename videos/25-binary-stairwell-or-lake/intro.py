"""As duas opções lado a lado, como miniaturas no escuro: a escada à esquerda, o lago com a cabana à direita."""
from lib import *
from places import *

SHOTS = {'intro': 4.0}


def mini_tower():
    stairwell(12, lamp_at=(0, 4, 8), walls=(0, 1), top=0.8)


def mini_lake():
    v, t = lathe([(0.0, 0.0), (9.0, 0.0), (9.0, -1.2), (0.0, -1.2)], 48)
    fast_mesh('lake', v, t, ice_mat('mini_ice'))
    cabin((0, 0, 0), math.radians(-15), window=12.0)
    pines(22, 7.6, seed=4, h=(2.0, 3.6))


def build_intro():
    reset(20)
    world_space((0.015, 0.012, 0.02), 1.0)
    sun(2.2, (-0.5, -0.9, 0.6), (0.8, 0.86, 1.0), 2.0)
    tower = group(mini_tower, (-1.6, 0, 1.0), 0.19, (math.radians(12), 0, math.radians(-30)))
    lake = group(mini_lake, (1.6, 0, -0.25), 0.14, (math.radians(14), 0, math.radians(20)))
    cam = camera((0, -7.4, 1.3), (0, 0, 0.1), 42)
    def update(t, u):
        tower.rotation_euler.z = math.radians(-30) + 0.12 * t
        lake.rotation_euler.z = math.radians(20) - 0.1 * t
        cam.location = (0, -7.4 + 0.4 * u, 1.3 + 0.03 * math.sin(t))
        look(cam, (0, 0, 0.1))
    return update
