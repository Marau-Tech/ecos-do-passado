"""Imagens de inspeção do personagem POV (roda dentro do Blender, nada de render de episódio).

    tools/blender/blender -b -P engine/pov/inspect.py -- studio <perfil> [vista ...]
    tools/blender/blender -b -P engine/pov/inspect.py -- real <perfil> <take> [vista ...]

studio: cena neutra, com vistas de fora (anatomia, vínculo com a câmera) e vistas POV.
real:   monta o take do episódio (Sarajevo, ou Stalingrado com VIDEO=26-pov-stalingrado), sem
        render dele nem alteração de arquivo; põe o personagem na câmera real e renderiza vistas
        com a direção de câmera de cada teste.
Saída em render/pov-inspect/<perfil>/ (pasta ignorada pelo git).
"""
import os
import sys
import math

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.dirname(HERE)
os.environ.setdefault('VIDEO', '02-pov-sarajevo')
os.environ.setdefault('GPU', '0')
sys.path.insert(0, ENGINE)

import bpy                       # noqa: E402
from mathutils import Vector     # noqa: E402
import lib                       # noqa: E402
from lib import *                # noqa: E402,F401
import project                   # noqa: E402
from pov.character import PovCharacter   # noqa: E402
from pov.motion import head_eye          # noqa: E402

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['studio', 'sarajevo_civilian_1914']
MODE, PROFILE = argv[0], argv[1]
OUT = os.path.join(project.ROOT, 'render', 'pov-inspect', os.environ.get('POV_INSPECT_DIR', ''), PROFILE)
os.makedirs(OUT, exist_ok=True)
SAMPLES = int(os.environ.get('SAMPLES', '24'))

SOLDIER = PROFILE.startswith('ww2')
HOLD = ('rifle', -1.0, 100.0, 0.0) if SOLDIER else ('watch', -1.0, 100.0, 0.0)

# nome: (pose_t, speed, pitch POV em graus, ações, câmera externa ou None, lente)
STUDIO = {
    'ext_front_parado': (0.0, 0.0, -2, (), ((1.3, 2.6, 1.25), (0, 0, 0.95)), 50),
    'ext_lado_andando': (0.3, 1.0, -2, (), ((3.2, 0.3, 1.0), (0, 0.15, 0.85)), 50),
    'ext_tras_andando': (0.85, 1.0, -2, (), ((-1.4, -2.6, 1.6), (0, 0.1, 0.9)), 50),
    'ext_mao_direita': (0.0, 0.0, -2, (('reach', -1, 100, 0),), ((0.55, 0.95, 1.55), (0.20, 0.52, 1.36)), 85),
    'ext_mao_palma': (0.0, 0.0, -2, (('reach', -1, 100, 0),), ((0.45, 0.62, 1.05), (0.20, 0.52, 1.36)), 85),
    'ext_sombra': (0.3, 0.8, -2, (), ((0.0, 2.2, 3.2), (0.6, 0.9, 0.0)), 30),
    'ext_acao': (0.0, 0.0, -2, (HOLD,), ((0.9, 1.6, 1.5), (0.0, 0.3, 1.25)), 50),
    'ext_protecao': (0.5, 0.0, -2, (('shield', -1, 100, 0),), ((0.9, 1.7, 1.6), (0.0, 0.25, 1.45)), 50),
    'pov_olhar_frente': (0.0, 0.8, -2, (), None, 30),
    'pov_olhar_baixo_parado': (0.0, 0.0, -70, (), None, 30),
    'pov_olhar_baixo_andando': (7.15, 0.55, -67, (), None, 30),
    'pov_protecao': (0.5, 0.0, -2, (('shield', -1, 100, 0),), None, 30),
    'pov_acao': (0.0, 0.0, -24 if SOLDIER else -42, (HOLD,), None, 30),
    'pov_acao_andando': (0.4, 0.8, -20 if SOLDIER else -3, (HOLD,), None, 30),
    'pov_mao_estendida': (0.0, 0.0, -12, (('reach', -1, 100, 0),), None, 30),
}


def studio_scene():
    s = reset(SAMPLES)
    world_flat((0.50, 0.56, 0.62), 0.9)
    sun(2.6, (-0.35, -0.55, 0.8), (1.0, 0.92, 0.80), 6)
    m = simple('studio_ground', (0.23, 0.215, 0.19), 0.9)
    box('studio_floor', (40, 40, 0.1), (0, 0, -0.05), m)
    for i in range(12):               # marcas no chão, para ler escala e movimento
        box('mark', (0.04, 0.6, 0.002), ((i % 4 - 1.5) * 0.6, (i // 4 - 1) * 0.6, 0.001), simple('mk', (0.4, 0.38, 0.33), 0.9))
    return s


def pov_cam(name='pov_cam'):
    d = bpy.data.cameras.new(name)
    d.lens, d.sensor_width = 30, 36
    d.clip_start, d.clip_end = 0.05, 1000
    o = bpy.data.objects.new(name, d)
    link(o)
    return o


def aim(cam, loc, pitch_deg, yaw=0.0):
    """loc é o olho com a cabeça reta; inclinar a cabeça move o olho em torno do pescoço."""
    p = math.radians(pitch_deg)
    loc = tuple(head_eye(loc, p, yaw))
    cam.location = loc
    look(cam, Vector(loc) + Vector((-math.sin(yaw) * math.cos(p), math.cos(yaw) * math.cos(p), math.sin(p))))


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print('[inspect]', path, flush=True)


def run_studio(views):
    studio_scene()
    pc = pov_cam()
    ch = PovCharacter(pc, PROFILE, ground=0.0)
    ext = pov_cam('ext_cam')
    for name in views:
        t, speed, pitch, actions, extv, lens = STUDIO[name]
        aim(pc, (0, speed * t, 1.65 + (0.0175 * abs(math.sin(math.pi * 1.8 * t)) - 0.00875 if speed else 0)), pitch)
        ch.update(t, pc, speed=speed, actions=actions, heading=0.0)
        if extv:
            ext.data.lens = lens
            ext.location = Vector(extv[0]) + Vector((0, speed * t, 0))
            look(ext, Vector(extv[1]) + Vector((0, speed * t, 0)))
            bpy.context.scene.camera = ext
        else:
            pc.data.lens = lens
            bpy.context.scene.camera = pc
        render(os.path.join(OUT, f'{name}.png'))


# take: (pose_t, speed do take, pitch do teste ou None para a câmera real sem mexer, ações)
# Os takes são só lidos e montados; nenhum arquivo do episódio é alterado.
REAL_STALIN = {
    'st_intro_frente': ('intro', 2.5, 0.0, None, ()),
    'st_t1_andando': ('t1', 3.0, 1.0, None, ()),
    'st_t1_fuzil': ('t1', 3.0, 1.0, -22, (('rifle', -1, 100, 0),)),
    'st_t1_olhar_chao': ('t1', 3.3, 1.0, -66, ()),
    'st_t2_protecao': ('t2', 4.1, 0.7, None, (('shield', -1, 100, 0),)),
}
REAL = {
    'intro_frente': ('intro', 4.0, 0.0, None, ()),
    'intro_relogio': ('intro', 4.0, 0.0, -40, (('watch', -1, 100, 0),)),
    't1_frente': ('t1', 5.0, 0.55, None, ()),
    't1_olhar_chao': ('t1', 5.3, 0.55, -66, ()),
    't4_protecao': ('t4', 3.2, 0.15, None, (('shield', -1, 100, 0),)),
    't9_mao_parapeito': ('t9', 2.0, 0.22, -14, (('reach', -1, 100, 0),)),
}


def run_real(take, views):
    import importlib
    import timeline as TL
    mod = importlib.import_module(TL.MODELO.scene_module(TL, take))
    upd = getattr(mod, 'build_' + take)()
    bpy.context.scene.cycles.samples = SAMPLES
    cam = bpy.context.scene.camera
    ch = PovCharacter(cam, PROFILE)
    table = REAL_STALIN if os.environ['VIDEO'].startswith('26') else REAL
    for name in views:
        tk, t, speed, pitch, actions = table[name]
        assert tk == take
        upd(t, 0.0)
        if pitch is not None:            # direção de teste: mesma posição, olhar mais para baixo
            f = cam.rotation_euler.to_matrix() @ Vector((0, 0, -1))
            yaw = math.atan2(-f.x, f.y)
            aim(cam, tuple(cam.location), pitch, yaw)
        ch.update(t, cam, speed=speed, actions=actions, heading=0.0)
        render(os.path.join(OUT, f'real_{name}.png'))


if MODE == 'studio':
    run_studio(argv[2:] or list(STUDIO))
else:
    take = argv[2]
    table = REAL_STALIN if os.environ['VIDEO'].startswith('26') else REAL
    run_real(take, argv[3:] or [k for k, v in table.items() if v[0] == take])
