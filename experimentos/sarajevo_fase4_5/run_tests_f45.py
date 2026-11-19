"""Testes sem render da Fase 4.5 (um Blender por vez)."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BLENDER = os.path.join(ROOT, 'tools', 'blender', 'blender')
SCRIPT = os.path.join(HERE, 'render_f45.py')

BASE = {
    'res': [864, 1536], 'fps': 24, 'samples': 16, 'adaptive': 0.05,
    'bounces': 3, 'diffuse': 1, 'glossy': 2, 'transmission': 1,
    'clamp': 4.0, 'exposure': 0.4, 'pbr': True, 'cinematic_lights': True,
    'light_mode': 'sky_sun', 'build_lean': True, 'lean_length': 25,
    'lean_pave_len': 35, 'lean_pave_near': 14, 'lean_crowd_end': 35,
    'purge_materials': True, 'inventory': False,
    'f41_explosion': True, 'f41_vehicle': True, 'f41_people': True,
    'f41_light': True, 'f42_explosion': True, 'f42_vehicle': True,
    'f42_characters': True, 'f42_light': True, 'f42_materials': True,
    'f45_explosion': True, 'f45_volume_step_rate': 1.0,
    'f45_volume_max_steps': 256,
}

import json

env = os.environ.copy()
env['VIDEO'] = '02-pov-sarajevo'
env['GPU'] = '1'
env['PYTHONPATH'] = os.pathsep.join([
    os.path.join(ROOT, 'engine'),
    os.path.join(ROOT, 'videos', '02-pov-sarajevo'),
    os.path.join(ROOT, 'experimentos', 'sarajevo_fase3_1'),
    os.path.join(ROOT, 'experimentos', 'sarajevo_fase4'),
    HERE,
])

runs = [
    ('ESTADO_E_CONTINUIDADE',
     dict(BASE, f45_state_test=True, f45_continuity_test=True)),
    ('GEOMETRIA', dict(BASE, f45_state_test=True, f45_geometry_test=True)),
]

for name, cfg in runs:
    cmd = [BLENDER, '-b', '-t', '4', '-P', SCRIPT, '--',
           'F45_TESTE_' + name, HERE, '', json.dumps(cfg)]
    print('=== ' + name + ' ===', flush=True)
    rc = subprocess.call(cmd, env=env)
    print('=== ' + name + ' rc=' + str(rc) + ' ===', flush=True)
    if rc != 0:
        sys.exit(rc)
