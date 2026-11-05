"""Caminhos do projeto. Todo script do engine descobre o vídeo atual por aqui."""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO = os.environ.get('VIDEO')
if not VIDEO:
    sys.exit('Defina VIDEO=<pasta em videos/> ou use ./video')
VIDEO_DIR = f'{ROOT}/videos/{VIDEO}'
PREVIEW = os.environ.get('PREVIEW') == '1'
RENDER = f'{ROOT}/render/{VIDEO}'
FRAMES = f'{RENDER}/{"preview" if PREVIEW else "final"}'
OUT = f'{ROOT}/out/{VIDEO}'
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, VIDEO_DIR)
sys.path.append(ROOT)
