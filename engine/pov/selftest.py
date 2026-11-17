"""Autoteste do personagem POV dentro do Blender (sem render).

    tools/blender/blender -b -P engine/pov/selftest.py

1. Determinismo: a malha no tempo t é a mesma em ordem crescente, decrescente e aleatória.
2. Vínculo: toda peça é filha da raiz; a raiz segue a posição e o rumo da câmera, não o pitch.
3. Enquadramento: nas ações, quanto de cada peça cai dentro do quadro 640x480.
4. Isolamento: a cena só ganha objetos e materiais do personagem; câmera, mundo e handlers intactos.
"""
import os
import sys
import math
import random

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('VIDEO', '02-pov-sarajevo')
os.environ.setdefault('GPU', '0')
sys.path.insert(0, os.path.dirname(HERE))

import bpy                                   # noqa: E402
import numpy as np                           # noqa: E402
from mathutils import Vector                 # noqa: E402
from bpy_extras.object_utils import world_to_camera_view   # noqa: E402
import lib                                   # noqa: E402
from pov.character import PovCharacter       # noqa: E402
from pov.outfits import PROFILES             # noqa: E402
from pov.motion import head_eye              # noqa: E402

FAIL = []


def check(ok, msg):
    print(('  ok   ' if ok else '  FALHA ') + msg, flush=True)
    if not ok:
        FAIL.append(msg)


def snapshot(ch):
    return {p['ob'].name: np.array([v.co[:] for v in p['me'].vertices]) for p in ch.parts}


def walk_cam(cam, t, pitch_deg=-2.0, speed=0.8):
    step = math.sin(math.pi * 1.8 * t)
    p = Vector((0.021 * step * (speed > 0), speed * t, 1.65 + (0.0175 * abs(step) - 0.00875) * (speed > 0)))
    pr = math.radians(pitch_deg)
    p = Vector(head_eye(p, pr))
    cam.location = p
    lib.look(cam, p + Vector((0, math.cos(pr), math.sin(pr))) * 10 + lib.shake(t, 0.012, 1.6, 3.0) * 10)


def in_frame(scene, cam, ob):
    """Fração dos vértices (já deformados) dentro do quadro e na frente da câmera."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    mw = ob.matrix_world
    pts = [world_to_camera_view(scene, cam, mw @ v.co) for v in ev.data.vertices]
    inside = [0 <= p.x <= 1 and 0 <= p.y <= 1 and p.z > 0 for p in pts]
    return sum(inside) / max(1, len(inside))


for profile in PROFILES:
    print(f'\n== {profile}', flush=True)
    lib.reset(4)
    scene = bpy.context.scene
    cam = lib.camera((0, 0, 1.65), (0, 10, 1.6), 30)
    before_objs = {o.name for o in bpy.data.objects}
    before_mats = {m.name for m in bpy.data.materials}
    world, scam = scene.world, scene.camera
    handlers = len(bpy.app.handlers.frame_change_pre) + len(bpy.app.handlers.frame_change_post)
    ch = PovCharacter(cam, profile, ground=0.0)
    acts = (('shield', 1.0, 2.0), ('rifle' if profile.startswith('ww2') else 'watch', 2.5, 4.0))

    # 1. determinismo
    times = [i / 15 for i in range(0, 75, 7)]
    res = {}
    for order in ('crescente', 'decrescente', 'aleatoria'):
        ts = list(times)
        if order == 'decrescente':
            ts.reverse()
        elif order == 'aleatoria':
            random.Random(7).shuffle(ts)
        res[order] = {}
        for t in ts:
            walk_cam(cam, t)
            ch.update(t, cam, speed=0.8, actions=acts, heading=0.0)
            res[order][t] = snapshot(ch)
    worst = max(float(np.abs(res['crescente'][t][k] - res[o][t][k]).max())
                for o in ('decrescente', 'aleatoria') for t in times for k in res['crescente'][t])
    check(worst == 0.0, f'mesma pose em qualquer ordem de frames (maior diferença {worst:.2e} m)')

    # 2. vínculo com a câmera
    check(all(p['ob'].parent == ch.root for p in ch.parts), f'{len(ch.parts)} peças presas à raiz do corpo')
    walk_cam(cam, 0.0, -2.0, 0.0)
    ch.update(0.0, cam)
    r_level = np.array(ch.root.location)
    walk_cam(cam, 0.0, -60.0, 0.0)
    ch.update(0.0, cam)
    r_down = np.array(ch.root.location)
    check(np.abs(r_level - r_down).max() < 1e-3,
          f'olhar para baixo (com o olho girando no pescoço) não move o corpo ({np.abs(r_level - r_down).max() * 1000:.2f} mm)')
    cam.location = (3.0, 7.0, 1.65)
    lib.look(cam, (3.0 + 10 * math.sin(-0.7), 7.0 + 10 * math.cos(0.7), 1.6))
    ch.update(0.0, cam)
    f = cam.rotation_euler.to_matrix() @ Vector((0, 0, -1))
    dxy = math.hypot(ch.root.location.x - 3.0, ch.root.location.y - 7.0)
    check(abs(ch.root.rotation_euler.z - math.atan2(-f.x, f.y)) < 1e-6 and dxy < 0.15,
          f'a raiz segue a posição e o rumo da câmera (corpo a {dxy * 100:.1f} cm sob o olho)')

    # 3. enquadramento nas ações (câmera de 30 mm, 640x480)
    cases = [('shield', -2, 0.0)] + ([('rifle', -14, 0.0), ('rifle', -3, 0.8)] if profile.startswith('ww2') else [('watch', -42, 0.0)])
    for pose, pitch, speed in cases:
        walk_cam(cam, 0.4, pitch, speed)
        ch.update(0.4, cam, speed=speed, actions=((pose, -1, 100, 0),), heading=0.0)
        bpy.context.view_layer.update()
        rep = []
        for p in ch.parts:
            if p['ob'].hide_render or p['group'] == 'shadow':
                continue
            fr = in_frame(scene, cam, p['ob'])
            if fr > 0:
                rep.append(f"{p['ob'].name.replace('pov_', '')} {fr * 100:.0f}%")
        print(f'  {pose} pitch {pitch} speed {speed}: ' + ', '.join(rep), flush=True)
        check(len(rep) > 0, f'{pose}: alguma parte do corpo aparece no quadro')

    # 4. isolamento
    new_objs = {o.name for o in bpy.data.objects} - before_objs
    new_mats = {m.name for m in bpy.data.materials} - before_mats
    check(all(n.startswith('pov') for n in new_objs), f'{len(new_objs)} objetos novos, todos pov_*')
    check(all(n.startswith('pov') for n in new_mats), f'{len(new_mats)} materiais novos, todos pov_*')
    check(scene.world == world and scene.camera == scam, 'mundo e câmera ativa da cena intactos')
    check(len(bpy.app.handlers.frame_change_pre) + len(bpy.app.handlers.frame_change_post) == handlers,
          'nenhum handler registrado')

print('\nRESULTADO:', 'tudo ok' if not FAIL else f'{len(FAIL)} falha(s): ' + '; '.join(FAIL), flush=True)
