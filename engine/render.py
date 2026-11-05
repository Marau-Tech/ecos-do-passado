import sys, os, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import project, lib, timeline

# uso: render.py -- shot [all|preview|f1,f2,...] [samples]
PREVIEW_FRAMES = 5
PREVIEW_SAMPLES = 6
argv = sys.argv[sys.argv.index('--') + 1:]
shot = argv[0]
fr = argv[1] if len(argv) > 1 else 'all'
samples = int(argv[2]) if len(argv) > 2 else None
mod = importlib.import_module(timeline.MODELO.scene_module(timeline, shot))
upd = getattr(mod, 'build_' + shot)()
if upd is None:                 # take de preparo: só gera texturas
    sys.exit(0)
dur = mod.SHOTS[shot]
nf = int(round(dur * lib.FPS))
if fr == 'all':
    frames = None
elif fr == 'preview':
    # com estados, o preview renderiza cada mudança, porque são poucas e dão o tempo exato
    frames = None if getattr(mod, 'HOLD_STATES', False) else sorted({round(i * (nf - 1) / (PREVIEW_FRAMES - 1)) for i in range(PREVIEW_FRAMES)})
    samples = samples or PREVIEW_SAMPLES
else:
    frames = [int(x) for x in fr.split(',')]
lib.render_shot(shot, upd, dur, frames, samples=samples, force=fr == 'preview')
