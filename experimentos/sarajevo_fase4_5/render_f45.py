"""Blender-side da FASE 4.4 — wrapper isolado sobre render_f42.py.

Uso:
  blender -b -t 4 -P render_f45.py -- NAME OUTDIR FRAMES_CSV CONFIG_JSON

A Fase 4.3 NÃO é referência aprovada e não é importada.  A base é a Fase 4.2
inalterada; este wrapper substitui apenas a explosão por f45_explosion e
opcionalmente desliga os refinos F4.2 para isolar o efeito (perfil EXPLOSION).

Nenhum arquivo das Fases 3.1/4.1/4.2/4.3, de engine/, de videos/ ou de take
original é alterado.  Toda a personalização vive neste diretório.
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
F31 = os.path.join(ROOT, 'experimentos', 'sarajevo_fase3_1')
F42 = os.path.join(ROOT, 'experimentos', 'sarajevo_fase4')
for p in (HERE, F42, F31, os.path.join(ROOT, 'engine'),
          os.path.join(ROOT, 'videos', '02-pov-sarajevo'), ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

# render_f42 instala os hooks F4.1 e F4.2 e importa cortejo.
import render_f42  # noqa: F401,E402
import render_f4  # noqa: E402
import f41_assets  # noqa: E402
import f41_explosion  # noqa: E402
import bpy  # noqa: E402
import f45_explosion  # noqa: E402


# Funções JÁ embrulhadas pela F4.2: usar como fallback quando f45 estiver off.
_assets_f42 = f41_assets.install
_make_explosion_f42 = f41_explosion.make_explosion


def _assets_install(cortejo, f31, cfg):
    report = _assets_f42(cortejo, f31, cfg) or {}
    if cfg.get('f45_state_test'):
        # Captura o update FINAL, depois de todos os patches F4.1/F4.2/F4.5.
        original = cortejo.build_t4

        def _capture_build_t4():
            u = original()
            globals()['_CAPTURED_UPDATE'] = u
            return u

        cortejo.build_t4 = _capture_build_t4
        report['f45_state_test'] = 'update capturado'
    print('[F45_HOOKS] assets instalados: ' +
          json.dumps(report, sort_keys=True), flush=True)
    return report


def _make_explosion(cfg):
    if cfg.get('f45_explosion'):
        # Curto-circuito: não chama F4.1 nem F4.2 (f42_explosion.refine).
        # Parâmetros de volume são (re)afirmados dentro de update(t), por serem
        # zerados pelo reset() que base_cortejo() executa em build_t4().
        globals()['_F45_FACTORY'] = f45_explosion.make_explosion(cfg)
        return globals()['_F45_FACTORY']
    return _make_explosion_f42(cfg)


f41_assets.install = _assets_install
f41_explosion.make_explosion = _make_explosion


def _config_from_argv():
    argv = sys.argv[sys.argv.index('--') + 1:]
    return json.loads(argv[3]) if len(argv) >= 4 else {}


# --- teste de estado determinístico (sem render) ---------------------------
def _state_rows():
    """Linhas detalhadas de transforms/alfa/energia de todos os objetos."""
    rows = []
    for o in sorted(bpy.data.objects, key=lambda x: x.name):
        row = [
            o.name,
            [round(float(x), 6) for x in o.location],
            [round(float(x), 6) for x in o.rotation_euler],
            [round(float(x), 6) for x in o.scale],
            bool(o.hide_render),
            round(float(o.color[3]), 6),
        ]
        if o.type == 'LIGHT':
            row.append(round(float(o.data.energy), 6))
            row.append([round(float(x), 6) for x in o.data.color])
        rows.append(row)
    return rows


def _state_snapshot(rows=None):
    """Hash SHA256 de transforms/alfa/energia — independente da ordem."""
    import hashlib

    rows = rows if rows is not None else _state_rows()
    payload = json.dumps(rows, sort_keys=True).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def _continuity_test():
    """Compara o estado da explosão no fim de t4 com o início de t5.

    Construir ``build_t5`` completo depois do purge de materiais da F4.2 não é
    seguro, então o teste usa diretamente a fábrica F4.5 com os mesmos
    argumentos do contrato t5 (``with_blast=False``, ``age0=10.1``).
    """
    import cortejo
    import hashlib

    u4 = globals().get('_CAPTURED_UPDATE')
    factory = globals().get('_F45_FACTORY')
    if u4 is None or factory is None:
        print('[F45_CONTINUIDADE] ERRO: update/fabrica nao capturados', flush=True)
        return

    def explosion_rows(suffixed):
        rows = []
        for o in sorted(bpy.data.objects, key=lambda x: x.name):
            if not o.name.startswith('f45_'):
                continue
            if ('.' in o.name) != bool(suffixed):
                continue
            rows.append([
                o.name.split('.')[0],
                [round(float(x), 6) for x in o.location],
                [round(float(x), 6) for x in o.rotation_euler],
                [round(float(x), 6) for x in o.scale],
                bool(o.hide_render),
                round(float(o.color[3]), 6),
            ])
        return rows

    dur = cortejo.SHOTS['t4']
    u4(dur, 1.0)            # age = 13.5 - 3.4 = 10.1 s
    rows4 = explosion_rows(suffixed=False)

    # A fábrica t5 é criada depois do snapshot de t4 para que os objetos ainda
    # não atualizados não contaminem a comparação.
    u5 = factory((1.30, 30.5, 1.05), t0=0.0, age0=10.1, seed=19,
                 with_blast=False)
    u5(0.0)                 # age = 0 + 10.1 - 0 = 10.1 s
    rows5 = explosion_rows(suffixed=True)

    digest = lambda rows: hashlib.sha256(
        json.dumps(rows, sort_keys=True).encode('utf-8')).hexdigest()
    diffs = [[a, b] for a, b in zip(rows4, rows5) if a != b]
    report = {
        'primeiras_diferencas': diffs[:12],
        'age_t4_fim': round(dur - 3.4, 4),
        'age_t5_inicio': 10.1,
        'objetos_comparados': len(rows4),
        'hash_t4': digest(rows4),
        'hash_t5': digest(rows5),
        'continuidade_ok': rows4 == rows5,
    }
    print('[F45_CONTINUIDADE] ' + json.dumps(report, sort_keys=True),
          flush=True)


def _geometry_test():
    """Procura causas estruturais de artefatos escuros nos objetos da explosão."""
    import math
    import cortejo

    update = globals().get('_CAPTURED_UPDATE')
    if update is None:
        print('[F45_GEOMETRIA] ERRO: update nao capturado', flush=True)
        return
    meshes = [o for o in bpy.data.objects
              if o.name.startswith('f45_') and o.type == 'MESH']
    degenerate = {}
    nonfinite = 0
    for o in meshes:
        me = o.data
        bad = sum(1 for p in me.polygons if p.area < 1e-9)
        if bad:
            degenerate[o.name] = bad
        nonfinite += sum(
            1 for v in me.vertices
            if not all(math.isfinite(float(c)) for c in v.co))
    bad_scale = []
    bad_transform = []
    for frame in (84, 90, 110, 140, 180):
        t = frame / 24.0
        update(t, t / cortejo.SHOTS['t4'])
        for o in meshes:
            vals = [float(x) for x in o.scale]
            if any(v <= 0.0 or not math.isfinite(v) for v in vals):
                bad_scale.append((frame, o.name, vals))
            if any(not math.isfinite(float(x)) for x in o.location):
                bad_transform.append((frame, o.name))
    report = {
        'objetos_f45': len(meshes),
        'faces_degeneradas': degenerate,
        'vertices_nao_finitos': nonfinite,
        'escalas_invalidas': bad_scale[:20],
        'transformacoes_invalidas': bad_transform[:20],
        'estrutura_valida': (not degenerate and not nonfinite and
                             not bad_scale and not bad_transform),
    }
    print('[F45_GEOMETRIA] ' + json.dumps(report, sort_keys=True),
          flush=True)


def _state_test():
    """A(84) → B(140) → A(84), depois ordem contrária; exige hashes iguais."""
    import cortejo

    update = globals().get('_CAPTURED_UPDATE')
    if update is None:
        print('[F45_STATE] ERRO: update() nao capturado', flush=True)
        return
    dur = cortejo.SHOTS['t4']

    debug = os.environ.get('F45_DEBUG_STATE')
    debug_dir = os.environ.get('F45_DEBUG_DIR', '/tmp/opencode/f45_state_debug')

    def sample(frame, label=''):
        t = frame / 24.0
        update(t, t / dur)
        rows = _state_rows()
        if debug and label:
            os.makedirs(debug_dir, exist_ok=True)
            with open(os.path.join(debug_dir, label + '.json'), 'w') as f:
                json.dump(rows, f, indent=1)
        return _state_snapshot(rows)

    a1 = sample(84, 'A1_84')
    b = sample(140, 'B_140')
    a2 = sample(84, 'A2_84')
    sample(180, 'X_180')
    sample(36, 'X_36')
    a3 = sample(84, 'A3_84')
    sample(90, 'X_90')
    sample(82, 'X_82')
    a4 = sample(84, 'A4_84')

    forbidden = [o.name for o in bpy.data.objects
                 if any(k in o.name.lower() for k in
                        ('blast_core', 'blast_halo', 'blast_star',
                         'shock_vertical', 'shock_ground', 'torus'))]
    report = {
        'A_84': a1, 'B_140': b,
        'A_repetido_apos_B': a2,
        'A_apos_fora_de_ordem': a3,
        'A_apos_sequencia_invertida': a4,
        'A_B_A_ok': a1 == a2,
        'fora_de_ordem_ok': a1 == a3 == a4,
        'B_diferente_de_A': b != a1,
        'primitivas_proibidas': forbidden,
        'luzes': [o.name for o in bpy.data.objects if o.type == 'LIGHT'],
        'volume_step_rate': bpy.context.scene.cycles.volume_step_rate,
        'volume_max_steps': bpy.context.scene.cycles.volume_max_steps,
    }
    print('[F45_STATE] ' + json.dumps(report, sort_keys=True), flush=True)


if __name__ == '__main__':
    cfg = _config_from_argv()
    print('[F45_WRAPPER] f45_explosion=' +
          str(bool(cfg.get('f45_explosion'))), flush=True)
    print('[F45_WRAPPER] config=' + json.dumps(cfg, sort_keys=True),
          flush=True)
    render_f4.main()
    if cfg.get('f45_state_test'):
        _state_test()
    if cfg.get('f45_continuity_test'):
        _continuity_test()
    if cfg.get('f45_geometry_test'):
        _geometry_test()
