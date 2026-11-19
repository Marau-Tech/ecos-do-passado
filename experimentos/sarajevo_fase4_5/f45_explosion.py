"""Fase 4.5 — reconstrução cinematográfica da explosão do take t4.

Evolução da F4.4 (reprovada visualmente: nuvem lisa/clara, silhueta
geométrica, bola de fogo grande, pouca evolução temporal e artefato preto no
topo da nuvem no frame 110).  Este módulo NÃO importa f44/f43/f42/f41.

Cinco sistemas independentes, ativáveis individualmente:

  A. flash     — clarão breve e localizado (luz ``pt`` + núcleo minúsculo)
  B. fire      — núcleo compacto + línguas curtas, quentes e irregulares
  C. smoke     — 3 domos de Principled Volume com turbulência multiescala
  D. debris    — fragmentos balísticos com repouso e poeira de impacto
  E. dust      — poeira rasteira que se dissipa

Estado puro e absoluto: ``age = t + age0 - t0``.  Nenhum ``+=``, nenhum
cache, nenhum estado global mutável.  A ordem de renderização é irrelevante.
Contrato preservado:

    explosion(center, t0, age0, seed, with_blast) -> update(t)
"""
import math
import json

import bpy
import numpy as np

import lib


PHASES = (
    (0.00, 'pre_detonacao'),
    (0.04, 'flash'),
    (0.18, 'nucleo_fogo'),
    (0.60, 'expansao_inicial'),
    (1.50, 'formacao_fumaca'),
    (2.80, 'expansao_turbulencia'),
    (4.20, 'queda_destrocos'),
    (6.00, 'fumaca_residual'),
    (10.00, 'dissipacao'),
)


def phase_of(age):
    if age < 0.0:
        return 'pre_detonacao'
    for limit, name in PHASES[1:]:
        if age < limit:
            return name
    return 'dissipacao'


def _map(nt, value, lo, hi, out_lo=0.0, out_hi=1.0, smooth=True):
    m = lib.n(nt, 'ShaderNodeMapRange')
    if smooth and hasattr(m, 'interpolation'):
        try:
            m.interpolation = 'SMOOTHSTEP'
        except Exception:
            pass
    if hasattr(m, 'clamp'):
        m.clamp = True
    m.inputs['From Min'].default_value = float(lo)
    m.inputs['From Max'].default_value = float(hi)
    m.inputs['To Min'].default_value = float(out_lo)
    m.inputs['To Max'].default_value = float(out_hi)
    if value is not None:
        lib.L(nt, value, m.inputs['Value'])
    return m.outputs['Result']


def _value(nt, name, initial=0.0):
    v = lib.n(nt, 'ShaderNodeValue')
    v.name = name
    v.label = name
    v.outputs[0].default_value = float(initial)
    return v


def _time_warp(nt, tc_socket, time_socket, cfg, prefix):
    """Desloca a coordenada do ruído com o tempo: fumaça que sobe e evolui."""
    comb = lib.n(nt, 'ShaderNodeCombineXYZ')
    for axis, scale in (('X', cfg.get(prefix + '_drift_x', 0.12)),
                        ('Y', cfg.get(prefix + '_drift_y', -0.05)),
                        ('Z', cfg.get(prefix + '_drift_z', -0.26))):
        mul = lib.math_(nt, 'MULTIPLY', time_socket, float(scale))
        lib.L(nt, mul, comb.inputs[axis])
    add = lib.n(nt, 'ShaderNodeVectorMath', _a={'operation': 'ADD'})
    lib.L(nt, tc_socket, add.inputs[0])
    lib.L(nt, comb.outputs[0], add.inputs[1])
    return add.outputs['Vector']


def _smoke_material(name, cfg, kind):
    """Volume com densidade = turbulência multiescala × envelope radial.

    A malha é apenas um domínio: a densidade chega a zero antes da fronteira
    da malha, então a silhueta poligonal nunca aparece.  O núcleo é escuro e
    denso, as bordas são difusas e claras.
    """
    m, nt = lib.mat(name)
    out = lib.n(nt, 'ShaderNodeOutputMaterial')
    tc = lib.n(nt, 'ShaderNodeTexCoord')
    oi = lib.n(nt, 'ShaderNodeObjectInfo')

    tv = _value(nt, 'f45_age_' + kind, 0.0)
    emit = _value(nt, 'f45_emit_' + kind, 0.0)
    warp = _time_warp(nt, tc.outputs['Object'], tv.outputs[0], cfg,
                      'f45_smoke')

    n1 = lib.n(nt, 'ShaderNodeTexNoise',
               Scale=cfg.get('f45_smoke_noise_a', 2.6),
               Detail=5.0, Roughness=0.62, Distortion=0.62)
    lib.L(nt, warp, n1.inputs['Vector'])
    n2 = lib.n(nt, 'ShaderNodeTexNoise',
               Scale=cfg.get('f45_smoke_noise_b', 7.4),
               Detail=3.0, Roughness=0.72, Distortion=0.48)
    lib.L(nt, warp, n2.inputs['Vector'])
    vor = lib.n(nt, 'ShaderNodeTexVoronoi',
                Scale=cfg.get('f45_smoke_voronoi', 4.6), Randomness=0.92)
    lib.L(nt, warp, vor.inputs['Vector'])

    # turbulência combinada: estrutura grande + detalhe fino + células
    t1 = lib.math_(nt, 'MULTIPLY', n1.outputs['Fac'], 0.54)
    t2 = lib.math_(nt, 'MULTIPLY', n2.outputs['Fac'], 0.30)
    t3 = lib.math_(nt, 'SUBTRACT', 1.0, vor.outputs['Distance'])
    t3 = lib.math_(nt, 'MULTIPLY', t3, 0.16)
    turb = lib.math_(nt, 'ADD', t1, t2)
    turb = lib.math_(nt, 'ADD', turb, t3)

    # envelope radial suave: densidade = 0 muito antes da fronteira
    dist = lib.n(nt, 'ShaderNodeVectorMath', _a={'operation': 'DISTANCE'})
    dist.inputs[1].default_value = (0.5, 0.5, 0.5)
    lib.L(nt, tc.outputs['Generated'], dist.inputs[0])
    envelope = _map(nt, dist.outputs['Value'], 0.06, 0.42, 1.0, 0.0)

    holes = _map(nt, turb, cfg.get('f45_smoke_cut_lo', 0.30),
                 cfg.get('f45_smoke_cut_hi', 0.66), 0.0, 1.0)
    dens = lib.math_(nt, 'MULTIPLY', envelope, holes)
    dens = lib.math_(nt, 'MULTIPLY', dens, oi.outputs['Alpha'])
    dens = lib.math_(nt, 'MULTIPLY', dens,
                     cfg.get('f45_smoke_density_' + kind, 0.80))

    vol = lib.n(nt, 'ShaderNodeVolumePrincipled')
    lib.L(nt, dens, vol.inputs['Density'])
    vol.inputs['Anisotropy'].default_value = cfg.get('f45_anisotropy', 0.45)
    vol.inputs['Absorption Color'].default_value = (
        0.24, 0.21, 0.18, 1.0) if kind != 'core' else (0.16, 0.14, 0.12, 1.0)

    # interior escuro/denso, exterior claro/difuso
    tone = lib.ramp(nt, [
        (0.00, (0.028, 0.026, 0.024)),
        (0.30, (0.085, 0.076, 0.066)),
        (0.62, (0.225, 0.202, 0.174)),
        (1.00, (0.39, 0.35, 0.30)),
    ], dist.outputs['Value'])
    lib.L(nt, tone.outputs[0], vol.inputs['Color'])

    if kind == 'core':
        heat = lib.ramp(nt, [
            (0.00, (0.45, 0.07, 0.01)),
            (0.45, (1.00, 0.30, 0.04)),
            (1.00, (1.00, 0.72, 0.24)),
        ], turb)
        lib.L(nt, heat.outputs[0], vol.inputs['Emission Color'])
        estrength = lib.math_(nt, 'MULTIPLY', emit.outputs[0],
                              oi.outputs['Alpha'])
        lib.L(nt, estrength, vol.inputs['Emission Strength'])

    nt.links.new(vol.outputs['Volume'], out.inputs['Volume'])
    return m, {'age': tv, 'emit': emit}


def _fire_material(name, cfg):
    """Fogo: emissão quente com bordas irregulares e ganho temporal."""
    m, nt = lib.mat(name)
    out = lib.n(nt, 'ShaderNodeOutputMaterial')
    tc = lib.n(nt, 'ShaderNodeTexCoord')
    oi = lib.n(nt, 'ShaderNodeObjectInfo')
    gain = _value(nt, 'f45_fire_gain', 0.0)

    sep = lib.n(nt, 'ShaderNodeSeparateXYZ')
    lib.L(nt, tc.outputs['Generated'], sep.inputs['Vector'])
    heat = lib.ramp(nt, [
        (0.00, (1.00, 0.94, 0.62)),
        (0.18, (1.00, 0.72, 0.20)),
        (0.46, (1.00, 0.36, 0.045)),
        (0.78, (0.72, 0.12, 0.012)),
        (1.00, (0.24, 0.02, 0.004)),
    ], sep.outputs['Z'])

    noise = lib.n(nt, 'ShaderNodeTexNoise', Scale=cfg.get('f45_fire_noise', 6.2),
                  Detail=3.0, Roughness=0.65, Distortion=0.55)
    lib.L(nt, tc.outputs['Object'], noise.inputs['Vector'])
    edge = _map(nt, noise.outputs['Fac'], 0.22, 0.68, 0.0, 1.0)
    alpha = lib.math_(nt, 'MULTIPLY', edge, oi.outputs['Alpha'])

    em = lib.n(nt, 'ShaderNodeEmission')
    lib.L(nt, heat.outputs[0], em.inputs['Color'])
    strength = lib.math_(nt, 'MULTIPLY', gain.outputs[0], alpha)
    strength = lib.math_(nt, 'MULTIPLY', strength,
                         cfg.get('f45_fire_strength', 3.0))
    lib.L(nt, strength, em.inputs['Strength'])

    tr = lib.n(nt, 'ShaderNodeBsdfTransparent')
    mix = lib.n(nt, 'ShaderNodeMixShader')
    lib.L(nt, alpha, mix.inputs[0])
    lib.L(nt, tr.outputs[0], mix.inputs[1])
    lib.L(nt, em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return m, {'gain': gain}


def _flash_material(name):
    """Clarão minúsculo: só no ponto da detonação, some em ~0,25 s."""
    m, nt = lib.mat(name)
    out = lib.n(nt, 'ShaderNodeOutputMaterial')
    oi = lib.n(nt, 'ShaderNodeObjectInfo')
    gain = _value(nt, 'f45_flash_gain', 0.0)
    em = lib.n(nt, 'ShaderNodeEmission')
    em.inputs['Color'].default_value = (1.0, 0.86, 0.62, 1.0)
    strength = lib.math_(nt, 'MULTIPLY', gain.outputs[0], oi.outputs['Alpha'])
    strength = lib.math_(nt, 'MULTIPLY', strength, 6.0)
    lib.L(nt, strength, em.inputs['Strength'])
    tr = lib.n(nt, 'ShaderNodeBsdfTransparent')
    mix = lib.n(nt, 'ShaderNodeMixShader')
    lib.L(nt, oi.outputs['Alpha'], mix.inputs[0])
    lib.L(nt, tr.outputs[0], mix.inputs[1])
    lib.L(nt, em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return m, {'gain': gain}


def _surface_material(name, color, rough=0.95, alpha=True):
    m, nt = lib.mat(name)
    out = lib.n(nt, 'ShaderNodeOutputMaterial')
    bs = lib.n(nt, 'ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value = (*color, 1.0)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = 0.0
    if alpha:
        oi = lib.n(nt, 'ShaderNodeObjectInfo')
        tr = lib.n(nt, 'ShaderNodeBsdfTransparent')
        mix = lib.n(nt, 'ShaderNodeMixShader')
        lib.L(nt, oi.outputs['Alpha'], mix.inputs[0])
        lib.L(nt, tr.outputs[0], mix.inputs[1])
        lib.L(nt, bs.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs['Surface'])
    else:
        nt.links.new(bs.outputs[0], out.inputs['Surface'])
    return m


def _volume_sphere(name, seed, sub=4, amp=0.12):
    """Ico de alta subdivisão deformada — domínio do volume, não silhueta."""
    proto = lib.ico(name + '_proto', 1.0, (0, 0, -500), None, sub)
    me = proto.data.copy()
    me.name = name
    rs = np.random.RandomState(seed)
    for v in me.vertices:
        c = np.asarray(v.co, np.float32)
        v.co = tuple(c * (1.0 + rs.uniform(-amp, amp)))
    me.update()
    bpy.data.objects.remove(proto, do_unlink=True)
    return me


def _flame_mesh(name, seed, sides=9, levels=7):
    """Língua de fogo: gota irregular e achatada, com ponta torta."""
    rs = np.random.RandomState(seed)
    prof = [(0.02, 0.02), (0.14, 0.22), (0.30, 0.46), (0.48, 0.52),
            (0.66, 0.36), (0.84, 0.16), (1.00, 0.0)]
    verts, tris = [], []
    bend = rs.uniform(-0.22, 0.22)
    for z, r in prof:
        for k in range(sides):
            a = math.tau * k / sides
            rr = r * rs.uniform(0.6, 1.4)
            verts.append((math.cos(a) * rr + bend * z * z,
                          math.sin(a) * rr * 0.72 + rs.uniform(-0.03, 0.03),
                          z + rs.uniform(-0.02, 0.02)))
    for j in range(levels - 1):
        for k in range(sides):
            a = j * sides + k
            b = j * sides + (k + 1) % sides
            c = (j + 1) * sides + k
            d = (j + 1) * sides + (k + 1) % sides
            tris.append((a, b, d))
            tris.append((a, d, c))
    o = lib.fast_mesh(name, verts, tris, None, smooth=True)
    me = o.data
    bpy.data.objects.remove(o, do_unlink=True)
    return me


def _fragment_meshes(name, seed, count=6):
    """Fragmentos pequeños e variados — nunca blocos grandes."""
    out = []
    for kind in range(count):
        rs = np.random.RandomState(seed + kind * 41)
        sx = (0.09, 0.14, 0.20, 0.11, 0.17, 0.07)[kind]
        sy = (0.13, 0.09, 0.06, 0.18, 0.11, 0.20)[kind]
        sz = (0.05, 0.08, 0.04, 0.05, 0.10, 0.03)[kind]
        base = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
        verts = [(x * sx * rs.uniform(0.6, 1.4),
                  y * sy * rs.uniform(0.6, 1.4),
                  z * sz * rs.uniform(0.6, 1.4)) for x, y, z in base]
        faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
                 (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
                 (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
        o = lib.fast_mesh('%s_%d' % (name, kind), verts, faces, None)
        out.append(o.data)
        bpy.data.objects.remove(o, do_unlink=True)
    return out


def _disc_mesh(name, seed, sides=19, rough=0.34):
    rs = np.random.RandomState(seed)
    verts = [(0.0, 0.0, 0.0)]
    for k in range(sides):
        a = math.tau * k / sides
        r = 1.0 + rs.uniform(-rough, rough)
        verts.append((math.cos(a) * r, math.sin(a) * r,
                      rs.uniform(0.0, 0.006)))
    tris = [(0, 1 + (k + 1) % sides, 1 + k) for k in range(sides)]
    o = lib.fast_mesh(name, verts, tris, None)
    me = o.data
    bpy.data.objects.remove(o, do_unlink=True)
    return me


def make_explosion(cfg):
    """Fábrica com a assinatura exigida pelo take original."""
    n_fire = int(cfg.get('f45_fire_count', 22))
    n_sparks = int(cfg.get('f45_sparks', 10))
    n_debris = int(cfg.get('f45_debris', 48))
    n_dust = int(cfg.get('f45_dust', 24))
    peak = float(cfg.get('f45_light_peak', 3200.0))
    flash_tau = float(cfg.get('f45_flash_tau', 0.13))
    tail_tau = float(cfg.get('f45_tail_tau', 2.4))
    tail_frac = float(cfg.get('f45_tail_fraction', 0.11))

    def explosion(center, t0=0.0, age0=0.0, seed=19, with_blast=True):
        cx, cy, cz = center

        # ---------------- materiais ------------------------------------------
        m_smoke_core, n_core = _smoke_material('f45_smoke_core_mat', cfg, 'core')
        m_smoke_body, n_body = _smoke_material('f45_smoke_body_mat', cfg, 'body')
        m_smoke_plume, n_plume = _smoke_material('f45_smoke_plume_mat', cfg,
                                                 'plume')
        smoke_nodes = {'core': n_core, 'body': n_body, 'plume': n_plume}

        m_fire, fire_nodes = _fire_material('f45_fire_mat', cfg)
        m_flash, flash_nodes = _flash_material('f45_flash_mat')
        m_dust = _surface_material('f45_dust_mat', (0.30, 0.25, 0.18))
        m_scorch = _surface_material('f45_scorch_mat', (0.055, 0.048, 0.040),
                                     0.98, alpha=False)
        # Revestimento de poeira: nunca preto puro, evita pontos escuros.
        m_frag = [
            _surface_material('f45_frag_%d' % k, col, 0.93, alpha=False)
            for k, col in enumerate((
                (0.19, 0.16, 0.13), (0.28, 0.23, 0.17),
                (0.22, 0.20, 0.17), (0.33, 0.27, 0.20),
                (0.16, 0.15, 0.13), (0.25, 0.21, 0.16)))
        ]

        # ---------------- domínios de volume (sub=4, 5120 tris) --------------
        smoke_meshes = {
            'core': _volume_sphere('f45_smoke_core_mesh', seed + 11),
            'body': _volume_sphere('f45_smoke_body_mesh', seed + 23),
            'plume': _volume_sphere('f45_smoke_plume_mesh', seed + 37),
        }
        smoke_mats = {'core': m_smoke_core, 'body': m_smoke_body,
                      'plume': m_smoke_plume}

        flame_meshes = [_flame_mesh('f45_flame_%d' % k, seed + 101 + k * 7)
                        for k in range(3)]
        spark_mesh = _volume_sphere('f45_spark_mesh', seed + 151, sub=2,
                                    amp=0.22)
        frag_meshes = _fragment_meshes('f45_frag', seed + 201)
        dust_mesh = _disc_mesh('f45_dust_mesh', seed + 251)
        impact_mesh = _disc_mesh('f45_impact_mesh', seed + 271, 15)
        scorch_mesh = _disc_mesh('f45_scorch_mesh', seed + 291, 23)
        flash_mesh = _volume_sphere('f45_flash_mesh', seed + 311, sub=2,
                                    amp=0.06)

        def spawn(name, me, mat):
            o = bpy.data.objects.new(name, me)
            lib.link(o)
            me.materials.clear()
            me.materials.append(mat)
            o.color = (1.0, 1.0, 1.0, 0.0)
            o.hide_render = True
            return o

        # A — flash
        flash = spawn('f45_flash', flash_mesh, m_flash)
        # B — fogo
        fire_core = spawn('f45_fire_core', smoke_meshes['core'], m_fire)
        flames = []
        rs = np.random.RandomState(seed + 401)
        for i in range(n_fire):
            ang = rs.uniform(0.0, math.tau)
            flames.append((spawn('f45_fire_%02d' % i,
                                 flame_meshes[i % 3], m_fire), {
                'ox': math.cos(ang), 'oy': math.sin(ang),
                'r0': rs.uniform(0.05, 0.75),
                'w': rs.uniform(0.16, 0.46),
                'h': rs.uniform(0.40, 1.35),
                'delay': rs.uniform(0.0, 0.22),
                'phase': rs.uniform(0.0, math.tau),
                'life': rs.uniform(0.45, 1.05),
            }))
        sparks = []
        rs = np.random.RandomState(seed + 503)
        for i in range(n_sparks):
            ang = rs.uniform(0.0, math.tau)
            vel = rs.uniform(1.6, 5.0)
            sparks.append((spawn('f45_spark_%02d' % i, spark_mesh, m_fire), {
                'vx': math.cos(ang) * vel, 'vy': math.sin(ang) * vel,
                'vz': rs.uniform(2.4, 6.2),
                'size': rs.uniform(0.05, 0.13),
                'life': rs.uniform(0.30, 0.80),
                'phase': rs.uniform(0.0, math.tau),
            }))

        # C — fumaça
        smoke = {k: spawn('f45_smoke_' + k, smoke_meshes[k], smoke_mats[k])
                 for k in ('core', 'body', 'plume')}

        # D — destroços
        debris, impacts = [], []
        rs = np.random.RandomState(seed + 601)
        for i in range(n_debris):
            ang = rs.uniform(0.0, math.tau)
            vel = rs.uniform(1.8, 7.0)
            kind = i % len(frag_meshes)
            p = {
                'vx': math.cos(ang) * vel, 'vy': math.sin(ang) * vel,
                'vz': rs.uniform(2.2, 6.4),
                'spin': rs.uniform(-13.0, 13.0),
                'phase': rs.uniform(0.0, math.tau),
                'size': rs.uniform(0.65, 1.35),
            }
            debris.append((spawn('f45_debris_%02d' % i, frag_meshes[kind],
                                 m_frag[kind]), p))
            impacts.append(spawn('f45_impact_%02d' % i, impact_mesh, m_dust))

        # E — poeira
        dusts = []
        rs = np.random.RandomState(seed + 701)
        for i in range(n_dust):
            ang = rs.uniform(0.0, math.tau)
            dusts.append((spawn('f45_dust_%02d' % i, dust_mesh, m_dust), {
                'dx': math.cos(ang), 'dy': math.sin(ang),
                'r0': rs.uniform(0.20, 1.10),
                'speed': rs.uniform(1.2, 3.8),
                'size': rs.uniform(0.28, 0.80),
                'delay': rs.uniform(0.0, 0.55),
                'phase': rs.uniform(0.0, math.tau),
            }))
        scorch = spawn('f45_scorch', scorch_mesh, m_scorch)

        light = lib.point(center, 0.0, (1.0, 0.86, 0.68), 2.2)
        light.data.shadow_soft_size = 2.0

        # ---------------- estado absoluto ------------------------------------
        systems = set()
        for key in ('flash', 'fire', 'smoke', 'debris', 'dust'):
            if cfg.get('f45_' + key, True):
                systems.add(key)

        all_objects = ([flash, fire_core] + [x[0] for x in flames] +
                       [x[0] for x in sparks] +
                       list(smoke.values()) +
                       [x[0] for x in debris] + impacts +
                       [x[0] for x in dusts] + [scorch])

        def hide(o):
            o.hide_render = True
            o.color = (1.0, 1.0, 1.0, 0.0)
            o.location = (0.0, 0.0, 0.0)
            o.rotation_euler = (0.0, 0.0, 0.0)
            o.scale = (1.0, 1.0, 1.0)

        def show(o, alpha):
            o.hide_render = False
            o.color = (1.0, 1.0, 1.0, max(0.0, min(1.0, alpha)))

        def update(t):
            """Atribuições absolutas, inclusive de nós de shader."""
            sc = bpy.context.scene
            sc.cycles.volume_step_rate = float(
                cfg.get('f45_volume_step_rate', 1.0))
            sc.cycles.volume_max_steps = int(
                cfg.get('f45_volume_max_steps', 256))

            age = t + age0 - t0
            live = age >= 0.0
            k = max(0.0, age)

            # Nós de tempo: avançam mesmo quando o sistema está desligado,
            # para que o estado seja sempre função de age.
            for nodes in smoke_nodes.values():
                nodes['age'].outputs[0].default_value = k
            fire_nodes['gain'].outputs[0].default_value = 0.0
            flash_nodes['gain'].outputs[0].default_value = 0.0
            smoke_nodes['core']['emit'].outputs[0].default_value = 0.0

            if not live:
                light.data.energy = 0.0
                for o in all_objects:
                    hide(o)
                return None

            # --- A: flash (luz curta + núcleo minúsculo) ---------------------
            # ``with_blast=False`` (take t5) preserva fumaça/destroços/poeira;
            # apenas o clarão e a luz de evento são suprimidos.
            flash_env = math.exp(-k / flash_tau)
            tail = tail_frac * math.exp(-k / tail_tau)
            attack = min(1.0, k / 0.012)
            light.data.energy = (peak * attack * (flash_env + tail)
                                 if with_blast else 0.0)
            warm = math.exp(-k / 0.55)
            light.data.color = (1.0, 0.58 + 0.34 * warm, 0.26 + 0.48 * warm)
            if (with_blast and 'flash' in systems and
                    flash_env > 0.01 and k < 0.4):
                flash_nodes['gain'].outputs[0].default_value = flash_env
                show(flash, min(1.0, k / 0.01) * flash_env)
                s = 0.12 + 0.30 * min(1.0, k / 0.09)
                flash.location = (cx, cy, cz + 0.05)
                flash.scale = (s, s * 0.9, s)
                flash.rotation_euler = (0.0, 0.0, 0.0)
            else:
                hide(flash)

            # --- B: fogo compacto e de curta duração -------------------------
            fire_gain = min(1.0, k / 0.035) * math.exp(-k / 0.42)
            fire_gain = max(0.0, fire_gain)
            if 'fire' in systems and fire_gain > 0.015:
                fire_nodes['gain'].outputs[0].default_value = fire_gain
                # núcleo de fogo: pequeno e luminoso, não um domo gigante
                s = 0.42 + 1.0 * min(1.0, k / 0.28)
                show(fire_core, min(1.0, k / 0.05) *
                     max(0.0, 1.0 - max(0.0, k - 0.35) / 0.55))
                fire_core.location = (cx, cy, cz + 0.10 + 0.35 * k)
                fire_core.scale = (s, s * 0.92, s * 1.15)
                fire_core.rotation_euler = (0.0, 0.0, 0.21 * k)
                smoke_nodes['core']['emit'].outputs[0].default_value = (
                    1.1 * min(1.0, k / 0.05) * math.exp(-k / 0.32))
                for o, p in flames:
                    a = k - p['delay']
                    if a <= 0.0 or a > p['life'] or fire_gain <= 0.015:
                        hide(o)
                        continue
                    flick = 0.78 + 0.16 * math.sin(19.0 * a + p['phase']) + \
                        0.08 * math.sin(41.0 * a + 2.1 * p['phase'])
                    alpha = min(1.0, a / 0.035) * \
                        math.exp(-a / (0.40 * p['life'])) * max(0.2, flick)
                    if alpha <= 0.03:
                        hide(o)
                        continue
                    r = p['r0'] + 0.95 * (1.0 - math.exp(-a / 0.16))
                    show(o, alpha)
                    o.location = (cx + p['ox'] * r, cy + p['oy'] * r,
                                  cz + 0.06)
                    w = p['w'] * (0.5 + 0.7 * min(1.0, a / 0.05))
                    o.scale = (w, w, p['h'] * (0.35 + 0.8 *
                                               min(1.0, a / 0.07)))
                    o.rotation_euler = (0.0, 0.0, p['phase'] + a * 2.6)
                for o, p in sparks:
                    a = k - 0.02
                    z = cz + p['vz'] * a - 4.9 * a * a
                    alpha = max(0.0, 1.0 - a / p['life'])
                    if a <= 0.0 or z <= 0.05 or alpha <= 0.02:
                        hide(o)
                        continue
                    show(o, alpha)
                    o.location = (cx + p['vx'] * a, cy + p['vy'] * a, z)
                    s = p['size'] * (0.6 + 0.5 * alpha)
                    o.scale = (s, s * 0.85, s * 1.3)
                    o.rotation_euler.z = p['phase'] + a * 9.0
            else:
                hide(fire_core)
                for o, _p in flames:
                    hide(o)
                for o, _p in sparks:
                    hide(o)

            # --- C: fumaça volumétrica, ascendente e turbulenta -------------
            if 'smoke' in systems:
                specs = {
                    'core': dict(tau=0.55, delay=0.10, life=3.4,
                                 rx=0.9, ry=2.6, rz=1.6,
                                 z0=0.25, vz=0.55, drift=(0.0, 0.0, 0.0)),
                    'body': dict(tau=1.25, delay=0.32, life=8.0,
                                 rx=1.1, ry=5.4, rz=2.4,
                                 z0=0.45, vz=0.78, drift=(0.16, -0.07, 0.0)),
                    'plume': dict(tau=2.30, delay=1.30, life=14.0,
                                  rx=0.9, ry=3.4, rz=3.2,
                                  z0=1.70, vz=1.35, drift=(0.30, -0.12, 0.0)),
                }
                for key, o in smoke.items():
                    sp = specs[key]
                    a = k - sp['delay']
                    if a <= 0.0 or a > sp['life']:
                        hide(o)
                        continue
                    grow = 1.0 - math.exp(-a / sp['tau'])
                    fade = min(1.0, a / 0.30) * max(
                        0.0, 1.0 - max(0.0, a - sp['life'] * 0.45) /
                        (sp['life'] * 0.55))
                    if fade <= 0.01:
                        hide(o)
                        continue
                    show(o, fade)
                    sx = sp['rx'] + sp['ry'] * grow
                    sz = sp['rz'] * (0.35 + 0.75 * grow)
                    o.location = (cx + sp['drift'][0] * a,
                                  cy + sp['drift'][1] * a,
                                  cz + sp['z0'] + sp['vz'] * a)
                    o.scale = (sx, sx * 0.94, sz)
                    o.rotation_euler = (0.08 * a * sp['drift'][0],
                                        0.08 * a * sp['drift'][1],
                                        0.42 + 0.07 * a)
            else:
                for o in smoke.values():
                    hide(o)

            # --- D: destroços com impulso radial e repouso ------------------
            if 'debris' in systems:
                for (o, p), imp in zip(debris, impacts):
                    a = k - 0.02
                    if a <= 0.0:
                        hide(o)
                        hide(imp)
                        continue
                    vz, g = p['vz'], 9.8
                    z = cz + vz * a - 0.5 * g * a * a
                    disc = max(0.0, vz * vz + 2.0 * g * (cz - 0.06))
                    tl = (vz + math.sqrt(disc)) / g
                    if a < tl and z > 0.06:
                        show(o, 1.0)
                        o.location = (cx + p['vx'] * a,
                                      cy + p['vy'] * a, z)
                        o.rotation_euler = (p['spin'] * a,
                                            p['spin'] * 0.53 * a,
                                            p['phase'] + p['spin'] * 0.35 * a)
                        o.scale = (p['size'], p['size'], p['size'])
                        hide(imp)
                    else:
                        # repouso: altura dependente do tamanho, sem flutuar
                        settle = min(1.0, max(0.0, a - tl) / 0.25)
                        hx = cx + p['vx'] * tl
                        hy = cy + p['vy'] * tl
                        hz = 0.05 + 0.055 * p['size']
                        show(o, 1.0)
                        o.location = (hx, hy, hz)
                        o.rotation_euler = (
                            p['spin'] * tl * (1.0 - 0.92 * settle),
                            p['spin'] * 0.53 * tl * (1.0 - 0.92 * settle),
                            p['phase'] + p['spin'] * 0.35 * tl)
                        o.scale = (p['size'], p['size'], p['size'])
                        since = a - tl
                        if 0.0 <= since <= 0.75:
                            aimp = min(1.0, since / 0.04) * max(
                                0.0, 1.0 - since / 0.75)
                            s = p['size'] * (0.3 + 1.2 *
                                             min(1.0, since / 0.22))
                            show(imp, aimp * 0.55)
                            imp.location = (hx, hy, 0.02)
                            imp.scale = (s * 1.4, s * 1.15, 1.0)
                        else:
                            hide(imp)
            else:
                for o, _p in debris:
                    hide(o)
                for imp in impacts:
                    hide(imp)

            # --- E: poeira rasteira -----------------------------------------
            if 'dust' in systems:
                for o, p in dusts:
                    a = k - p['delay']
                    if a <= 0.0 or a > 7.0:
                        hide(o)
                        continue
                    alpha = min(1.0, a / 0.22) * max(0.0, 1.0 - a / 7.0)
                    if alpha <= 0.02:
                        hide(o)
                        continue
                    rad = p['r0'] + p['speed'] * (1.0 - math.exp(-a / 1.3))
                    s = p['size'] * (0.35 + 1.5 * min(1.0, a / 1.6))
                    show(o, alpha * 0.6)
                    o.location = (cx + p['dx'] * rad,
                                  cy + p['dy'] * rad * 0.92,
                                  0.055 + 0.02 * math.sin(p['phase'] + a * 2))
                    o.scale = (s * 1.9, s * 1.3, s * 0.28)
                    o.rotation_euler.z = p['phase'] * 0.11
                s = 0.6 + 2.0 * min(1.0, k / 2.0)
                show(scorch, 1.0)
                scorch.location = (cx, cy, 0.012)
                scorch.scale = (s, s, 1.0)
            else:
                for o, _p in dusts:
                    hide(o)
                hide(scorch)

            return None

        report = {
            'versao': 'F45',
            'contrato': 'explosion(center,t0,age0,seed,with_blast)->update(t)',
            'fases': [name for _l, name in PHASES] + ['dissipacao'],
            'sistemas': sorted(systems),
            'center': list(center), 'seed': seed, 't0': t0, 'age0': age0,
            'idade': 't + age0 - t0',
            'smoke_volumes': 3, 'smoke_subdivisao': 4,
            'fogo_linguas': n_fire, 'faiscas': n_sparks,
            'destrocos': n_debris, 'poeira': n_dust,
            'luzes': [light.name], 'sem_estado_global': True,
            'sem_primitivas_proibidas': True,
            'volume_step_rate': cfg.get('f45_volume_step_rate', 1.0),
            'volume_max_steps': cfg.get('f45_volume_max_steps', 256),
        }
        print('[F45_EXPLOSION] ' + json.dumps(report, sort_keys=True),
              flush=True)
        return update

    return explosion
