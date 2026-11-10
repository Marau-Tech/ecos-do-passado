from lib import *

TILT = (0.3, -0.2, 0)


def toward_camera(world=(-0.35, -1.0, 0.2), tilt=TILT, z=1.2):
    """direção, no espaço do planeta, que fica virada para a câmera no meio do take de abertura"""
    R = Euler((tilt[0], tilt[1], z), 'XYZ').to_matrix()
    return tuple(R.transposed() @ Vector(world).normalized())


def spot(nt, tc, d, cos_in, cos_out):
    """máscara 0..1 de uma mancha redonda na superfície, em volta da direção d"""
    nv = n(nt, 'ShaderNodeVectorMath', {'operation': 'NORMALIZE'}); L(nt, tc, nv.inputs[0])
    dot = n(nt, 'ShaderNodeVectorMath', {'operation': 'DOT_PRODUCT'}); L(nt, nv.outputs[0], dot.inputs[0])
    dot.inputs[1].default_value = d
    mr = n(nt, 'ShaderNodeMapRange', From_Min=cos_out, From_Max=cos_in); L(nt, dot.outputs['Value'], mr.inputs['Value'])
    return mr.outputs[0]


def planet_aurora(r=1.0, loc=(0, 0, 0)):
    """neve azulada de noite"""
    m, nt = mat('aurora')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=3.0, Detail=8.0, Roughness=0.6); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.4, (0.32, 0.38, 0.48)), (0.62, (0.72, 0.78, 0.88))], a.outputs['Fac']).outputs[0]
    out(nt, principled(nt, col, 0.55, spec=0.5).outputs[0])
    return sphere('p_aurora', r, loc, m, 192, 96)


def aurora_shell(r=1.0, loc=(0, 0, 0)):
    """cortinas de luz verde e violeta em volta dos dois polos"""
    m, nt = mat('aurshell')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    sp = n(nt, 'ShaderNodeSeparateXYZ'); L(nt, tc, sp.inputs[0])
    lat = math_(nt, 'ABSOLUTE', math_(nt, 'DIVIDE', sp.outputs['Z'], r * 1.06))
    band = ramp(nt, [(0.62, (0, 0, 0)), (0.76, (1, 1, 1)), (0.86, (0.6, 0.6, 0.6)), (0.95, (0, 0, 0))], lat).outputs[0]
    w = n(nt, 'ShaderNodeTexWave', Scale=3.0, Distortion=6.0, Detail=4.0); L(nt, tc, w.inputs['Vector'])
    nz = n(nt, 'ShaderNodeTexNoise', Scale=2.0, Detail=3.0); L(nt, tc, nz.inputs['Vector'])
    hue = ramp(nt, [(0.4, (0.15, 1.0, 0.55)), (0.62, (0.7, 0.25, 1.0))], nz.outputs['Fac']).outputs[0]
    bw = n(nt, 'ShaderNodeRGBToBW'); L(nt, band, bw.inputs[0])
    k = math_(nt, 'MULTIPLY', bw.outputs[0], w.outputs['Fac'])
    e = n(nt, 'ShaderNodeEmission'); L(nt, hue, e.inputs['Color'])
    L(nt, math_(nt, 'MULTIPLY', k, 4.0), e.inputs['Strength'])
    add = n(nt, 'ShaderNodeAddShader')
    L(nt, n(nt, 'ShaderNodeBsdfTransparent').outputs[0], add.inputs[0]); L(nt, e.outputs[0], add.inputs[1])
    out(nt, add.outputs[0])
    return sphere('aurshell', r * 1.06, loc, m, 128, 64)


def planet_field(r=1.0, loc=(0, 0, 0)):
    """faixas de plantação ocre, de polo a polo"""
    m, nt = mat('field')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    w = n(nt, 'ShaderNodeTexWave', Scale=18.0, Distortion=1.5, Detail=2.0); L(nt, tc, w.inputs['Vector'])
    a = n(nt, 'ShaderNodeTexNoise', Scale=4.0, Detail=6.0); L(nt, tc, a.inputs['Vector'])
    c1 = ramp(nt, [(0.3, (0.48, 0.38, 0.14)), (0.7, (0.68, 0.56, 0.24))], w.outputs['Fac']).outputs[0]
    c2 = ramp(nt, [(0.4, (0.36, 0.34, 0.14)), (0.6, (0.62, 0.5, 0.22))], a.outputs['Fac']).outputs[0]
    out(nt, principled(nt, mix(nt, 0.4, c1, c2), 0.85, spec=0.2).outputs[0])
    return sphere('p_field', r, loc, m, 192, 96)


def planet_well(r=1.0, loc=(0, 0, 0)):
    """terra marrom rachada, lisa, com um único ponto escuro"""
    m, nt = mat('well')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.5, Detail=6.0); L(nt, tc, a.inputs['Vector'])
    base = ramp(nt, [(0.4, (0.42, 0.3, 0.18)), (0.62, (0.6, 0.46, 0.3))], a.outputs['Fac']).outputs[0]
    v = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=14.0); L(nt, tc, v.inputs['Vector'])
    cracks = mix(nt, math_(nt, 'LESS_THAN', v.outputs['Distance'], 0.03), base, (0.22, 0.15, 0.09))
    dot = spot(nt, tc, toward_camera(), 0.99975, 0.9996)
    out(nt, principled(nt, mix(nt, dot, cracks, (0.0, 0.0, 0.0)), 0.9, spec=0.15).outputs[0])
    return sphere('p_well', r, loc, m, 192, 96)


def planet_spires(r=1.0, loc=(0, 0, 0)):
    """mar preto e liso; num ponto, uma mancha de luzes verdes"""
    m, nt = mat('spires')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=5.0, Detail=4.0); L(nt, tc, a.inputs['Vector'])
    sea = ramp(nt, [(0.4, (0.004, 0.008, 0.01)), (0.65, (0.012, 0.03, 0.03))], a.outputs['Fac']).outputs[0]
    city = spot(nt, tc, toward_camera(), 0.9994, 0.9982)
    v = n(nt, 'ShaderNodeTexVoronoi', Scale=900.0); L(nt, tc, v.inputs['Vector'])
    specks = math_(nt, 'MULTIPLY', math_(nt, 'LESS_THAN', v.outputs['Distance'], 0.25), city)
    emis = mix(nt, specks, (0, 0, 0), (0.3, 1.0, 0.55))
    col = mix(nt, city, sea, (0.02, 0.05, 0.035))
    out(nt, principled(nt, col, 0.2, spec=0.6, emis=emis, emis_str=6.0).outputs[0])
    return sphere('p_spires', r, loc, m, 256, 128)


def glow(r, loc, color, strength):
    """halo: forte no centro, some na borda"""
    m, nt = mat('glow')
    lw = n(nt, 'ShaderNodeLayerWeight', Blend=0.5)
    a = math_(nt, 'POWER', math_(nt, 'SUBTRACT', 1.0, lw.outputs['Facing']), 3.0)
    e = n(nt, 'ShaderNodeEmission', Strength=strength); e.inputs['Color'].default_value = (*color, 1)
    tr = n(nt, 'ShaderNodeBsdfTransparent')
    ms = n(nt, 'ShaderNodeMixShader')
    L(nt, a, ms.inputs[0]); L(nt, tr.outputs[0], ms.inputs[1]); L(nt, e.outputs[0], ms.inputs[2])
    out(nt, ms.outputs[0])
    return sphere('glow', r, loc, m, 48, 24)


def orbit(planet, atmo_color, sd, tilt=TILT, extra=None):
    """take de abertura: planeta girando com a câmera parada enquanto o nome é dito, depois zoom"""
    from timeline import NAME_HOLD
    reset(20)
    world_space((0.02, 0.014, 0.022), 1.0)
    sun(4.5, sd, (1, 0.96, 0.92))
    p = planet(1.0); atmosphere(1.0, atmo_color, sd, 1.03, power=5, strength=0.55)
    p.rotation_euler = tilt
    if extra: extra(p)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u, dur):
        u = zoom_after(t, NAME_HOLD, dur)
        p.rotation_euler.z = 0.8 + 0.1 * t
        cam.location = vlerp((0.1, -3.6, 0.1), (0.05, -2.3, 0.05), ease(u))
        look(cam, (-0.05 * u, 0, 0))
    return update
