"""Driver de previews da FASE 4.4 — um Blender por frame, guarda de RAM 350 MB.

Uso:
  python3 preview_f45.py PROFILE [f1,f2,...]

PROFILE: EXPLOSION | ALL | FIRE | SMOKE | DEBRIS | DUST | COMBINED

  EXPLOSION — nova explosão sobre a base F4.1, com os refinos F4.2 desligados
              (isolamento do efeito).
  ALL       — nova explosão sobre a base F4.1 + todos os refinos F4.2.
  FIRE      — somente flash + fogo (isolamento do sistema B).
  SMOKE     — somente fumaça volumétrica (isolamento do sistema C).
  DEBRIS    — somente destroços (isolamento do sistema D).
  DUST      — somente poeira rasteira (isolamento do sistema E).
  COMBINED  — todos os cinco sistemas, base F4.1 (equivalente a EXPLOSION).

Todos os frames usam o padrão de produção: 864x1536, 24 FPS, 16 samples,
Cycles CUDA, AgX Medium High Contrast, exposicao +0,4, OIDN, adaptive 0,05.
"""
import os
import sys
import re
import json
import time
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BLENDER = os.path.join(ROOT, 'tools', 'blender', 'blender')
SCRIPT = os.path.join(HERE, 'render_f45.py')
FRAMES_DIR = os.path.join(HERE, 'frames')
RESULTS_DIR = os.path.join(HERE, 'results')
LOGS_DIR = os.path.join(HERE, 'logs')
for d in (FRAMES_DIR, RESULTS_DIR, LOGS_DIR):
    os.makedirs(d, exist_ok=True)

RAM_ABORT_MB = 350.0
RAM_START_MB = 1500.0
THREADS = 4

# Base tecnica integral F4.1; F4.2 fica desligada por omissao no perfil
# EXPLOSION e ligada no perfil ALL.  f45_explosion substitui a explosao.
BASE = {
    'res': [864, 1536], 'fps': 24, 'samples': 16, 'adaptive': 0.05,
    'bounces': 3, 'diffuse': 1, 'glossy': 2, 'transmission': 1,
    'clamp': 4.0, 'exposure': 0.4,
    'pbr': True, 'cinematic_lights': True, 'light_mode': 'sky_sun',
    'build_lean': True, 'lean_length': 25, 'lean_pave_len': 35,
    'lean_pave_near': 14, 'lean_crowd_end': 35,
    'purge_materials': True, 'inventory': False,
    # base F4.1
    'f41_explosion': True, 'f41_vehicle': True,
    'f41_people': True, 'f41_light': True,
    # base F4.2 — desligada no perfil isolado
    'f42_explosion': False, 'f42_vehicle': False, 'f42_characters': False,
    'f42_light': False, 'f42_materials': False,
    # F4.5
    'f45_explosion': True,
    'f45_volume_step_rate': 1.0,
    'f45_volume_max_steps': 256,
}

PROFILES = {
    'EXPLOSION': {},
    'ALL': {'f42_explosion': True, 'f42_vehicle': True,
            'f42_characters': True, 'f42_light': True,
            'f42_materials': True},
    'FIRE': {'f45_smoke': False, 'f45_debris': False, 'f45_dust': False},
    'SMOKE': {'f45_fire': False, 'f45_debris': False, 'f45_dust': False},
    'DEBRIS': {'f45_fire': False, 'f45_smoke': False, 'f45_dust': False},
    'DUST': {'f45_fire': False, 'f45_smoke': False, 'f45_debris': False},
    'COMBINED': {},
}

DEFAULT_FRAMES = {
    'EXPLOSION': [82, 84, 90, 110, 140, 180],
    'ALL': [36, 82, 84, 90, 110, 140, 180],
    'FIRE': [84, 90, 110, 140],
    'SMOKE': [84, 90, 110, 140, 180],
    'DEBRIS': [84, 90, 110, 140],
    'DUST': [84, 90, 110, 140, 180],
    'COMBINED': [82, 84, 90, 110, 140, 180],
}


def mem_available_mb():
    with open('/proc/meminfo') as f:
        for line in f:
            if line.startswith('MemAvailable:'):
                return int(line.split()[1]) / 1024.0
    return 0.0


def gpu_used_mb():
    try:
        out = subprocess.check_output([
            'nvidia-smi', '--query-gpu=memory.used',
            '--format=csv,noheader,nounits'], text=True)
        return float(out.strip().splitlines()[0])
    except Exception:
        return None


def rss_mb(pid):
    try:
        with open('/proc/%d/status' % pid) as f:
            for line in f:
                if line.startswith('VmRSS:'):
                    return int(line.split()[1]) / 1024.0
    except Exception:
        pass
    return None


def wait_memory():
    waited = 0.0
    while mem_available_mb() < RAM_START_MB:
        if waited > 180:
            raise RuntimeError('RAM insuficiente por mais de 180 s')
        time.sleep(2)
        waited += 2


def parse_build(lines):
    for line in reversed(lines):
        if line.startswith('[BUILD] '):
            try:
                return json.loads(line[len('[BUILD] '):])
            except Exception:
                return None
    return None


def run(profile, frames):
    run_name = 'F45_' + profile + os.environ.get('F45_RUN_SUFFIX', '')
    cfg = dict(BASE)
    cfg.update(PROFILES[profile])
    override = os.environ.get('F45_CFG_OVERRIDE')
    if override:
        cfg.update(json.loads(override))
    result_path = os.path.join(RESULTS_DIR, run_name + '.json')
    log_path = os.path.join(LOGS_DIR, run_name + '.log')
    result = {'run': run_name, 'profile': profile, 'config': cfg,
              'frames': {}, 'aborted': False}
    if os.path.exists(result_path):
        with open(result_path) as f:
            old = json.load(f)
        result['frames'] = old.get('frames', {})
        print('retomando ' + run_name, flush=True)

    for i in frames:
        out = os.path.join(FRAMES_DIR, '%s_%04d.png' % (run_name, i))
        if os.path.exists(out) and os.path.getsize(out) > 100000:
            print('%s: frame %d ja existe' % (run_name, i), flush=True)
            continue
        wait_memory()
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
        cmd = [BLENDER, '-b', '-t', str(THREADS), '-P', SCRIPT, '--',
               run_name, FRAMES_DIR, str(i), json.dumps(cfg)]
        gpu0 = gpu_used_mb()
        t0 = time.time()
        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, bufsize=1)
        lines = []
        min_avail = mem_available_mb()
        peak_rss = 0.0
        peak_gpu = gpu0 or 0.0
        aborted = False
        # Guarda de RAM em TODAS as linhas; nvidia-smi e /proc amostrados
        # no maximo a cada 2 s (correcao validada na F4.2).
        last_sample = time.time() - 2.0
        for line in proc.stdout:
            lines.append(line.rstrip('\n'))
            min_avail = min(min_avail, mem_available_mb())
            now = time.time()
            if now - last_sample >= 2.0:
                last_sample = now
                r = rss_mb(proc.pid)
                if r is not None:
                    peak_rss = max(peak_rss, r)
                g = gpu_used_mb()
                if g is not None:
                    peak_gpu = max(peak_gpu, g)
            if min_avail < RAM_ABORT_MB and not aborted:
                aborted = True
                print('[RAM GUARD] %s frame %d: %.0f MB' %
                      (run_name, i, min_avail), flush=True)
                proc.terminate()
        proc.wait()
        with open(log_path, 'a') as f:
            f.write('\n===== FRAME %d =====\n' % i)
            f.write('\n'.join(lines) + '\n')
        ok = proc.returncode == 0 and os.path.exists(out) \
            and os.path.getsize(out) > 100000
        render_sec = None
        for line in lines:
            m = re.search(r'"render_seconds":\s*([0-9.]+)', line)
            if m:
                render_sec = float(m.group(1))
        result['frames'][str(i)] = {
            'ok': ok, 'aborted_low_ram': aborted,
            'returncode': proc.returncode,
            'wall_seconds': round(time.time() - t0, 2),
            'render_seconds': render_sec,
            'min_available_mb': round(min_avail, 1),
            'peak_blender_rss_mb': round(peak_rss, 1),
            'gpu_baseline_mb': gpu0,
            'gpu_peak_mb': round(peak_gpu, 1),
            'gpu_delta_mb': round(peak_gpu - gpu0, 1) if gpu0 else None,
        }
        if 'build' not in result:
            result['build'] = parse_build(lines)
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2, sort_keys=True)
        print('%s frame %d: %s (%.1f s, RAM %.0f MB, GPU +%s MB)' %
              (run_name, i, 'OK' if ok else 'FALHOU',
               time.time() - t0, min_avail,
               result['frames'][str(i)]['gpu_delta_mb']), flush=True)
        if not ok:
            result['aborted'] = True
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2, sort_keys=True)
            sys.exit(1)
    result['aborted'] = False
    with open(result_path, 'w') as f:
        json.dump(result, f, indent=2, sort_keys=True)
    print('%s concluido: %d frames' % (run_name, len(frames)), flush=True)


if __name__ == '__main__':
    profile = sys.argv[1] if len(sys.argv) > 1 else 'EXPLOSION'
    if profile not in PROFILES:
        sys.exit('perfil desconhecido: %s (use %s)' %
                 (profile, ', '.join(PROFILES)))
    frames = DEFAULT_FRAMES[profile]
    if len(sys.argv) > 2:
        frames = [int(x) for x in sys.argv[2].split(',') if x.strip()]
    print('%s frames=%s' % (profile, frames), flush=True)
    print('config: ' + json.dumps(dict(BASE, **PROFILES[profile]),
                                 sort_keys=True), flush=True)
    run(profile, frames)
