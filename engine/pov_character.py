"""Sistema reutilizável de personagens em primeira pessoa."""

import math
from lib import *


PROFILES = {
    "sarajevo_civilian_1914": {
        "jacket": (0.075, 0.060, 0.045),
        "shirt": (0.68, 0.63, 0.52),
        "skin": (0.48, 0.31, 0.22),
        "trousers": (0.075, 0.065, 0.052),
        "boots": (0.035, 0.025, 0.018),
    },
    "ww2_german_soldier": {
        "jacket": (0.20, 0.22, 0.14),
        "shirt": (0.25, 0.26, 0.18),
        "skin": (0.48, 0.31, 0.22),
        "trousers": (0.20, 0.22, 0.14),
        "boots": (0.035, 0.025, 0.018),
    },
    "ww2_soviet_soldier": {
        "jacket": (0.27, 0.25, 0.14),
        "shirt": (0.30, 0.28, 0.17),
        "skin": (0.48, 0.31, 0.22),
        "trousers": (0.27, 0.25, 0.14),
        "boots": (0.035, 0.025, 0.018),
    },
}


def _attach(obj, parent, location=(0, 0, 0)):
    obj.parent = parent
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = location
    return obj


def _empty(name, parent):
    obj = bpy.data.objects.new(name, None)
    link(obj)
    return _attach(obj, parent)


def _tube(name, parent, points, radii, material):
    obj = tube(name, points, radii, material, res=6, bevel=4)
    return _attach(obj, parent)



def _sleeve_mesh(name, parent, points, radii, material):
    """Manga orgânica formada por anéis de malha 3D."""
    from mathutils import Vector

    sides = 16
    verts = []
    faces = []

    pts = [Vector(v) for v in points]

    for i, point in enumerate(pts):
        if i == 0:
            tangent = (pts[1] - pts[0]).normalized()
        elif i == len(pts) - 1:
            tangent = (pts[-1] - pts[-2]).normalized()
        else:
            tangent = (pts[i + 1] - pts[i - 1]).normalized()

        reference = Vector((0, 1, 0))
        if abs(tangent.dot(reference)) > 0.92:
            reference = Vector((1, 0, 0))

        axis_a = tangent.cross(reference).normalized()
        axis_b = tangent.cross(axis_a).normalized()

        for j in range(sides):
            angle = 2.0 * math.pi * j / sides
            offset = (
                axis_a * math.cos(angle) * radii[i]
                + axis_b * math.sin(angle) * radii[i] * 0.88
            )
            verts.append(tuple(point + offset))

    for i in range(len(pts) - 1):
        for j in range(sides):
            a = i * sides + j
            b = i * sides + (j + 1) % sides
            c = (i + 1) * sides + (j + 1) % sides
            d = (i + 1) * sides + j
            faces.append((a, b, c, d))

    # A extremidade do ombro fica aberta e fora do enquadramento.
    # Mantemos apenas o fechamento próximo ao punho.
    last = (len(pts) - 1) * sides
    faces.append(tuple(last + j for j in range(sides)))

    obj = mesh_from(name, verts, faces, material, smooth=True)
    return _attach(obj, parent)

def _sphere(name, parent, radius, location, material, scale):
    obj = sphere(name, radius, (0, 0, 0), material, seg=32, rings=24)
    obj.scale = scale
    return _attach(obj, parent, location)


def create_pov_character(cam, profile="sarajevo_civilian_1914"):
    """Cria personagem POV em coordenadas locais da câmera."""

    if profile not in PROFILES:
        raise ValueError(f"Perfil desconhecido: {profile}")

    cfg = PROFILES[profile]

    jacket = simple("pov_jacket", cfg["jacket"], 0.88)
    shirt = simple("pov_shirt", cfg["shirt"], 0.9)
    skin = simple("pov_skin", cfg["skin"], 0.72)
    trousers = simple("pov_trousers", cfg["trousers"], 0.92)
    boots = simple("pov_boots", cfg["boots"], 0.75)

    arms = []
    legs = []

    for side in (-1, 1):
        arm = _empty(f"pov_arm_{side}", cam)
        arm.location = (0.0, -0.05, -0.90)
        arm.scale = (0.58, 0.72, 0.72)

        # Manga do paletó: mais fina e com volume gradual.
        _sleeve_mesh(
            "pov_sleeve", arm,
            [
                (side * 1.45, -0.18, -0.78),
                (side * 1.08, -0.34, -0.92),
                (side * 0.67, -0.48, -1.12),
                (side * 0.34, -0.58, -1.34),
            ],
            [0.115, 0.100, 0.075, 0.052],
            jacket,
        )

        # Punho claro da camisa.
        _tube(
            "pov_cuff", arm,
            [
                (side * 0.32, -0.37, -1.29),
                (side * 0.30, -0.38, -1.34),
                (side * 0.29, -0.39, -1.38),
            ],
            [0.047, 0.046, 0.043],
            shirt,
        )

        # Antebraço e palma.
        _tube(
            "pov_forearm", arm,
            [
                (side * 0.29, -0.39, -1.37),
                (side * 0.27, -0.41, -1.43),
                (side * 0.25, -0.43, -1.48),
            ],
            [0.043, 0.039, 0.034],
            skin,
        )

        _sphere(
            "pov_palm", arm, 0.045,
            (side * 0.245, -0.445, -1.515),
            skin, (0.78, 0.62, 1.20),
        )

        # Quatro dedos simplificados, próximos uns dos outros.
        for finger in range(4):
            offset = (finger - 1.5) * 0.018
            length = 0.075 - abs(finger - 1.5) * 0.012

            x = side * (0.245 + offset)
            _tube(
                f"pov_finger_{finger}", arm,
                [
                    (x, -0.445, -1.54),
                    (x, -0.45, -1.54 - length * 0.55),
                    (x, -0.44, -1.54 - length),
                ],
                [0.012, 0.010, 0.007],
                skin,
            )

        # Polegar lateral.
        _tube(
            "pov_thumb", arm,
            [
                (side * 0.21, -0.44, -1.51),
                (side * 0.19, -0.45, -1.54),
                (side * 0.185, -0.44, -1.57),
            ],
            [0.019, 0.015, 0.010],
            skin,
        )

        arms.append((arm, side))

    # Parte inferior do corpo: volumes menores, na borda da imagem.
    for side in (-1, 1):
        leg = _empty(f"pov_leg_{side}", cam)
        leg.location = (0.0, -0.05, -0.85)
        leg.scale = (0.78, 0.78, 0.78)

        _tube(
            "pov_trouser_leg", leg,
            [
                (side * 0.17, -0.43, -1.42),
                (side * 0.18, -0.49, -1.51),
                (side * 0.19, -0.53, -1.59),
            ],
            [0.075, 0.065, 0.055],
            trousers,
        )

        boot = box(
            "pov_boot",
            (0.13, 0.075, 0.20),
            (0, 0, 0),
            boots,
        )
        _attach(
            boot, leg,
            (side * 0.19, -0.54, -1.64),
        )

        legs.append((leg, side))

    def update(t, walking=True):
        intensity = 1.0 if walking else 0.12
        phase = t * 2.8

        for arm, side in arms:
            swing = math.sin(
                phase + (math.pi if side > 0 else 0)
            )
            arm.rotation_euler.x = 0.075 * swing * intensity
            arm.rotation_euler.y = 0.018 * swing * intensity
            arm.rotation_euler.z = 0.030 * swing * intensity

        for leg, side in legs:
            swing = math.sin(
                phase + (math.pi if side > 0 else 0)
            )
            leg.rotation_euler.x = 0.045 * swing * intensity

    return update
