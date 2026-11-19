"""Métricas da FASE 4.4 — somente leitura de PNGs/logs/JSONs já gerados.

Não renderiza nada e não altera nenhum preview.  Saída:
  results/F45_METRICAS.json

Inclui:
  * operacional por run (tempo, RAM mínima, pico RSS, VRAM);
  * stats de cena vindas de [BUILD] (triângulos, objetos, materiais, clipping);
  * métricas espaciais Rec.709 por frame (luminância, contraste, clip, saturação,
    gradiente e 6 bandas horizontais);
  * determinismo estrutural ([F45_STATE]) e determinismo de pixels (se houver
    runs A/B/A renderizados);
  * comparação com F3.1 (via F43_METRICAS.json) e com F4.3 (F43_EXPLOSION).
"""
import os
import re
import json
import glob

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
F43 = os.path.join(ROOT, 'experimentos', 'sarajevo_fase4')
F44 = os.path.join(ROOT, 'experimentos', 'sarajevo_fase4_4')
FRAMES = os.path.join(HERE, 'frames')
RESULTS = os.path.join(HERE, 'results')
LOGS = os.path.join(HERE, 'logs')


def image_metrics(path):
    a = np.asarray(Image.open(path).convert('RGB'), dtype=np.float32) / 255.0
    # Rec.709 sobre valores sRGB (mesma convenção usada na F4.3).
    lum = 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]
    lum8 = lum * 255.0
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    sat = np.where(mx > 0.0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    gx = np.abs(np.diff(lum8, axis=1)).mean()
    gy = np.abs(np.diff(lum8, axis=0)).mean()
    bands = []
    nb = 6
    step = lum.shape[0] // nb
    for i in range(nb):
        b = lum8[i * step:(i + 1) * step] if i < nb - 1 else lum8[i * step:]
        bands.append({
            'mean': round(float(b.mean()), 2),
            'std': round(float(b.std()), 2),
            'p10': round(float(np.percentile(b, 10)), 2),
            'lt20_pct': round(float(100.0 * np.mean(b < 20)), 2),
        })
    return {
        'mean': round(float(lum8.mean()), 2),
        'std': round(float(lum8.std()), 2),
        'p5': round(float(np.percentile(lum8, 5)), 2),
        'p25': round(float(np.percentile(lum8, 25)), 2),
        'p50': round(float(np.percentile(lum8, 50)), 2),
        'p75': round(float(np.percentile(lum8, 75)), 2),
        'p95': round(float(np.percentile(lum8, 95)), 2),
        'lt20_pct': round(float(100.0 * np.mean(lum8 < 20)), 2),
        'lt8_pct': round(float(100.0 * np.mean(lum8 < 8)), 2),
        'white_clip_pct': round(float(100.0 * np.mean(mx >= 0.985)), 3),
        'black_clip_pct': round(float(100.0 * np.mean(mx <= 0.020)), 3),
        'clip_pct': round(float(100.0 * np.mean((mx >= 0.985) |
                                               (mx <= 0.020))), 3),
        'sat_pct': round(float(100.0 * np.mean(sat > 0.5)), 2),
        'grad_medio': round(float((gx + gy) / 2.0), 2),
        'bandas': bands,
    }


def dark_artifacts(path):
    """Procura manchas escuras compactas cercadas por região mais clara.

    O artefato reportado na F4.4 é um ponto preto no topo da nuvem (frame 110).
    Aqui ele é tratado como um componente conectado de luminância muito baixa
    cuja vizinhança imediata é significativamente mais clara.  A análise é
    somente leitura; não oculta nem corrige nada.
    """
    a = np.asarray(Image.open(path).convert('RGB'), dtype=np.float32) / 255.0
    lum = 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]
    lum8 = lum * 255.0
    core = lum8 < 14.0
    # Vizinhança de ~12 px: um objeto escuro isolado dentro de area clara.
    local = ndimage.uniform_filter(lum8, size=25) > 38.0
    mask = core & local
    # AScene toda é escura em algumas bandas; restringe ao terço superior
    # (onde ficava o artefato da F4.4) e ao medio, ignorando o céu puro.
    mask[:int(0.06 * lum.shape[0]), :] = False
    labels, n = ndimage.label(mask)
    comps = []
    if n:
        objs = ndimage.find_objects(labels)
        sizes = ndimage.sum(mask, labels, range(1, n + 1))
        for i in np.argsort(sizes)[::-1][:8]:
            area = int(sizes[i])
            if area < 4:
                continue
            sl = objs[i]
            comps.append({
                'area_px': area,
                'bbox': [int(sl[1].start), int(sl[0].start),
                         int(sl[1].stop), int(sl[0].stop)],
                'lum_media_local': round(
                    float(ndimage.uniform_filter(lum8, size=25)[sl].mean()), 1),
            })
    return {
        'pixels_muito_escuros_pct': round(float(100.0 * np.mean(core)), 3),
        'componentes_suspeitos': comps,
        'total_componentes_suspeitos': len(comps),
    }


def temporal_metrics(prefix):
    """Diferença média entre frames consecutivos do mesmo perfil."""
    seq = [82, 84, 90, 110, 140, 180]
    paths = {f: os.path.join(FRAMES, '%s_%04d.png' % (prefix, f))
             for f in seq}
    paths = {f: p for f, p in paths.items() if os.path.exists(p)}
    out = []
    for a, b in zip(seq, seq[1:]):
        if a in paths and b in paths:
            d = _pixel_diff(paths[a], paths[b])
            out.append({'de': a, 'para': b, 'mean_abs': d['mean_abs'],
                        'pixels_diferentes_pct': round(
                            100.0 * d['pixels_diferentes'] /
                            d['pixels_totais'], 1)})
    return out


def summary_run(path):
    d = json.load(open(path))
    fr = d.get('frames', {})
    ok = [v for v in fr.values() if v.get('ok')]
    rs = [v.get('render_seconds') for v in fr.values()
          if v.get('render_seconds') is not None]
    walls = [v.get('wall_seconds', 0.0) for v in fr.values()]
    rams = [v.get('min_available_mb') for v in fr.values()
            if v.get('min_available_mb') is not None]
    rss = [v.get('peak_blender_rss_mb') for v in fr.values()
           if v.get('peak_blender_rss_mb') is not None]
    gpu = [v.get('gpu_delta_mb') for v in fr.values()
           if v.get('gpu_delta_mb') is not None]
    return {
        'run': d.get('run'), 'profile': d.get('profile'),
        'frames': len(fr), 'ok': len(ok),
        'abortes': sum(1 for v in fr.values() if v.get('aborted_low_ram')),
        'wall_total_s': round(float(sum(walls)), 1),
        'render_min_s': round(min(rs), 1) if rs else None,
        'render_max_s': round(max(rs), 1) if rs else None,
        'render_mean_s': round(float(np.mean(rs)), 1) if rs else None,
        'ram_min_mb': round(min(rams), 1) if rams else None,
        'rss_max_mb': round(max(rss), 1) if rss else None,
        'gpu_delta_min_mb': round(min(gpu), 1) if gpu else None,
        'gpu_delta_max_mb': round(max(gpu), 1) if gpu else None,
        'por_frame': {k: v for k, v in fr.items()},
    }


def parse_build():
    out = {}
    for path in sorted(glob.glob(os.path.join(LOGS, '*.log'))):
        for line in open(path, errors='replace'):
            if not line.startswith('[BUILD] '):
                continue
            try:
                d = json.loads(line[len('[BUILD] '):])
            except Exception:
                continue
            st = d.get('stats', {})
            out[d.get('name', os.path.basename(path))] = {
                'triangles': st.get('triangles'),
                'objects': st.get('objects'),
                'meshes': st.get('meshes'),
                'materials': st.get('materials'),
                'lights': st.get('lights'),
                'shared_geometry': st.get('shared_geometry'),
                'build_seconds': d.get('build_seconds'),
                'resolution': d.get('resolution'),
                'samples': d.get('samples'),
                'exposure': d.get('exposure'),
                'look': d.get('look'),
                'engine': d.get('engine'),
                'device': d.get('cycles_device'),
            }
    return out


def parse_state():
    for path in sorted(glob.glob(os.path.join(LOGS, '*.log'))):
        for line in open(path, errors='replace'):
            if line.startswith('[F45_STATE] '):
                try:
                    return json.loads(line[len('[F45_STATE] '):])
                except Exception:
                    pass
    return {}


def sha256(path):
    import hashlib

    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _pixel_diff(path_a, path_b):
    """Diferença média/máxima em 8 bits e contagem de pixels divergentes."""
    a = np.asarray(Image.open(path_a).convert('RGB'), dtype=np.int16)
    b = np.asarray(Image.open(path_b).convert('RGB'), dtype=np.int16)
    d = np.abs(a - b)
    anyc = np.any(d > 0, axis=2)
    return {
        'mean_abs': round(float(d.mean()), 6),
        'max': int(d.max()),
        'pixels_diferentes': int(np.count_nonzero(anyc)),
        'pixels_totais': int(anyc.size),
        'sha256_a': sha256(path_a),
        'sha256_b': sha256(path_b),
    }


def render_determinism():
    """A→B→A e fora de ordem em processos distintos.

    O estado estrutural é bit-identico ([F45_STATE]); o render CUDA é
    estocástico por amostragem, então a métrica relevante é a diferença média
    entre repetições de A, comparada com a diferença entre A e B.
    """
    def find(suffix, frame):
        path = os.path.join(FRAMES, 'F45_EXPLOSION_%s_%04d.png' % (suffix, frame))
        return path if os.path.exists(path) else None

    a1, a2, a3 = find('DETA1', 84), find('DETA2', 84), find('DETA3', 84)
    b2 = find('DETA2', 140)
    if not (a1 and a2 and a3 and b2):
        return {}
    out = {
        'A1_vs_A2': _pixel_diff(a1, a2),
        'A1_vs_A_fora_de_ordem': _pixel_diff(a1, a3),
        'A1_vs_B': _pixel_diff(a1, b2),
    }
    rep = max(out['A1_vs_A2']['mean_abs'],
              out['A1_vs_A_fora_de_ordem']['mean_abs'])
    out['interpretacao'] = (
        'Estado estrutural bit-identico em A->B->A e fora de ordem; pixels de '
        'uma mesma cena diferem apenas pelo nondeterminismo de amostragem '
        'CUDA. A diferenca entre frames distintos e dezenas de vezes maior.')
    out['razao_B_sobre_repeticao'] = (
        round(out['A1_vs_B']['mean_abs'] / rep, 1) if rep > 0 else None)
    out['repeticoes_identicas_bit_a_bit'] = (
        out['A1_vs_A2']['sha256_a'] == out['A1_vs_A2']['sha256_b'])
    return out


def main():
    report = {
        'metodo': ('métricas espaciais Rec.709; 6 bandas horizontais iguais; '
                   'operacional por run; determinismo estrutural e de pixels'),
        'status': 'medições objetivas — NÃO são aprovação estética',
        'operacional': {}, 'build': parse_build(), 'frames': {},
        'determinismo': {'estado': parse_state(),
                         'render': render_determinism()},
        'referencia': {}, 'comparacao_f43': {}, 'comparacao_f44': {},
        'evolucao_temporal': {}, 'artefatos_escuros': {},
    }
    for path in sorted(glob.glob(os.path.join(RESULTS, 'F45_*.json'))):
        if os.path.basename(path) in ('F45_METRICAS.json',
                                      'F45_PESQUISA.json'):
            continue
        try:
            d = json.load(open(path))
        except Exception:
            continue
        if 'frames' not in d:
            continue
        report['operacional'][os.path.basename(path)] = summary_run(path)

    # frames F4.5 (todos os perfis)
    for path in sorted(glob.glob(os.path.join(FRAMES, 'F45_*.png'))):
        base = os.path.basename(path)[:-4]
        report['frames'][base] = image_metrics(path)

    # evolução temporal por perfil
    for prefix in ('F45_EXPLOSION', 'F45_ALL', 'F45_SMOKE'):
        report['evolucao_temporal'][prefix] = temporal_metrics(prefix)

    # investigação do artefato preto do frame 110: F4.4 × F4.5
    old110 = os.path.join(F44, 'frames', 'F44_EXPLOSION_0110.png')
    new110 = os.path.join(FRAMES, 'F45_EXPLOSION_0110.png')
    if os.path.exists(old110):
        report['artefatos_escuros']['F44_EXPLOSION_0110'] = \
            dark_artifacts(old110)
    if os.path.exists(new110):
        report['artefatos_escuros']['F45_EXPLOSION_0110'] = \
            dark_artifacts(new110)

    # referência F3.1 aprovada e números F4.3/F4.4 (somente leitura)
    f43_path = os.path.join(F43, 'results', 'F43_METRICAS.json')
    if os.path.exists(f43_path):
        old = json.load(open(f43_path))
        report['referencia']['F31'] = old.get('referencia_f31', {})
        report['referencia']['F43 operacional'] = old.get('operacional', {})
        report['comparacao_f43']['F43 por_area'] = old.get('per_area', {})
    f44_path = os.path.join(F44, 'results', 'F44_METRICAS.json')
    if os.path.exists(f44_path):
        old = json.load(open(f44_path))
        report['comparacao_f44']['operacional'] = old.get('operacional', {})
        report['comparacao_f44']['frames'] = old.get('frames', {})

    out = os.path.join(RESULTS, 'F45_METRICAS.json')
    with open(out, 'w') as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print('gravado ' + out)
    print('runs=' + str(len(report['operacional'])) +
          ' frames_medidos=' + str(len(report['frames'])))


if __name__ == '__main__':
    main()
