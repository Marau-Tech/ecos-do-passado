"""Quarto à noite pela webcam do notebook: cadeira na frente, cama ao lado, a porta entreaberta no fundo
e um rosto pálido na fresta, que some depois do glitch."""
from lib import *
import timeline as TL

SHOTS = {'a': 10.0}
HOLD_STATES = True


def build_a():
    reset(64)
    world_flat((0, 0, 0), 0.0)
    wall = simple('wall', (0.42, 0.42, 0.45), 0.9)
    box('floor', (5, 6, 0.1), (0, 1, -0.05), simple('carpet', (0.18, 0.16, 0.17), 0.95))
    box('ceil', (5, 6, 0.1), (0, 1, 2.6), wall)
    box('wallL', (0.1, 6, 2.6), (-2.5, 1, 1.3), wall); box('wallR', (0.1, 6, 2.6), (2.5, 1, 1.3), wall)
    # parede do fundo com o vão da porta em x de 0.3 a 1.2
    box('wallB1', (2.8, 0.1, 2.6), (-1.1, 4, 1.3), wall)
    box('wallB2', (1.3, 0.1, 2.6), (1.85, 4, 1.3), wall)
    box('wallB3', (0.9, 0.1, 0.5), (0.75, 4, 2.35), wall)
    dark = simple('dark', (0.02, 0.02, 0.022), 1.0)                       # corredor oco e escuro atrás da porta
    box('hallB', (3, 0.1, 2.6), (0.75, 6.6, 1.3), dark); box('hallL', (0.1, 2.6, 2.6), (-0.4, 5.3, 1.3), dark)
    box('hallR', (0.1, 2.6, 2.6), (1.9, 5.3, 1.3), dark); box('hallF', (3, 2.6, 0.1), (0.75, 5.3, 0.0), dark)
    door = box('door', (0.9, 0.05, 2.1), (0, 0, 0), simple('doorm', (0.5, 0.48, 0.46), 0.7))
    pivot = bpy.data.objects.new('hinge', None); link(pivot); pivot.location = (0.3, 4.02, 1.05)
    door.parent = pivot; door.location = (0.45, 0, 0)
    pivot.rotation_euler.z = math.radians(35)          # abre para o corredor: sobra uma fresta do lado direito, perto do batente
    bed = simple('bed', (0.30, 0.32, 0.40), 0.95)
    box('bed', (1.5, 2.1, 0.5), (-1.6, 2.4, 0.25), bed)
    box('pillow', (1.2, 0.4, 0.15), (-1.6, 3.3, 0.55), simple('pil', (0.6, 0.6, 0.62), 0.95))
    box('blanket', (1.55, 1.3, 0.12), (-1.6, 2.0, 0.55), simple('blk', (0.22, 0.24, 0.34), 0.95))
    chair = simple('chair', (0.04, 0.04, 0.045), 0.6)
    box('chairback', (0.5, 0.06, 0.5), (-0.62, -0.25, 0.62), chair)      # só a ponta, no canto de baixo
    box('poster', (0.6, 0.02, 0.85), (-1.3, 3.94, 1.6), simple('posterm', (0.35, 0.3, 0.38), 0.9))
    face = pale_figure((1.13, 4.8, 0.0))               # atrás da fresta, além da ponta da porta
    face.scale = (0.88, 0.88, 0.88)
    point((0.0, -0.9, 0.9), 22.0, (0.6, 0.72, 1.0), 0.5)   # brilho da tela do notebook
    point((1.15, 4.5, 1.7), 0.3, (0.7, 0.75, 0.9), 0.15)    # um resto de luz no corredor: só o rosto aparece
    camera((0.0, -0.95, 1.05), (0.3, 4.0, 1.2), 28)

    def upd(t, u):
        here = t < TL.GONE
        for o in [face] + list(face.children_recursive):
            o.hide_render = not here
        return here
    return upd
