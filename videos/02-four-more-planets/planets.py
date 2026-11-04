from lib import *

def _clouds(name, r, loc, color, scale, lo, hi, alpha=1.0):
    m, nt = mat(name)
    tc = n(nt, 'ShaderNodeTexCoord')
    a = n(nt, 'ShaderNodeTexNoise', Scale=scale, Detail=9.0, Roughness=0.58); L(nt, tc.outputs['Object'], a.inputs['Vector'])
    c = ramp(nt, [(lo, (0, 0, 0)), (hi, (alpha, alpha, alpha))], a.outputs['Fac']).outputs[0]
    p = principled(nt, color, 0.9)
    tr = n(nt, 'ShaderNodeBsdfTransparent')
    ms = n(nt, 'ShaderNodeMixShader')
    L(nt, c, ms.inputs[0]); L(nt, tr.outputs[0], ms.inputs[1]); L(nt, p.outputs[0], ms.inputs[2])
    out(nt, ms.outputs[0])
    return sphere(name, r, loc, m, 128, 64)

def planet_feast(r=1.0, loc=(0, 0, 0)):
    """glacê, caramelo e rios de chocolate"""
    m, nt = mat('feast')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    warp = n(nt, 'ShaderNodeTexNoise', Scale=2.4, Detail=5.0, Roughness=0.55); L(nt, tc, warp.inputs['Vector'])
    wv = n(nt, 'ShaderNodeVectorMath', {'operation': 'ADD'})
    L(nt, tc, wv.inputs[0])
    sc = n(nt, 'ShaderNodeVectorMath', {'operation': 'SCALE'}); L(nt, warp.outputs['Color'], sc.inputs[0]); sc.inputs['Scale'].default_value = 0.9
    L(nt, sc.outputs[0], wv.inputs[1])
    reg = n(nt, 'ShaderNodeTexNoise', Scale=1.5, Detail=5.0, Roughness=0.5); L(nt, wv.outputs[0], reg.inputs['Vector'])
    base = ramp(nt, [(0.36, (0.90, 0.22, 0.38)), (0.46, (0.98, 0.74, 0.50)), (0.56, (0.95, 0.56, 0.14)), (0.66, (0.42, 0.16, 0.05))], reg.outputs['Fac']).outputs[0]
    # rios: bordas de voronoi deformadas
    vo = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=2.3); L(nt, wv.outputs[0], vo.inputs['Vector'])
    riv = math_(nt, 'LESS_THAN', vo.outputs['Distance'], 0.022)
    col = mix(nt, riv, base, (0.11, 0.04, 0.015))
    # confeitos
    sp = n(nt, 'ShaderNodeTexVoronoi', Scale=46.0); L(nt, tc, sp.inputs['Vector'])
    dot = math_(nt, 'LESS_THAN', sp.outputs['Distance'], 0.13)
    col = mix(nt, math_(nt, 'MULTIPLY', dot, 0.9), col, sp.outputs['Color'])
    # ondas de glacê
    wave = n(nt, 'ShaderNodeTexWave', {'wave_type': 'RINGS'}, Scale=3.2, Distortion=7.0, Detail=3.0); L(nt, wv.outputs[0], wave.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.16, Distance=0.03); L(nt, wave.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.32, spec=0.6, normal=bp.outputs[0]).outputs[0])
    return sphere('p_feast', r, loc, m, 192, 96)

def planet_woods(r=1.0, loc=(0, 0, 0)):
    m, nt = mat('woods')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=3.0, Detail=11.0, Roughness=0.62); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.30, (0.008, 0.035, 0.022)), (0.46, (0.014, 0.075, 0.03)), (0.58, (0.04, 0.12, 0.04)), (0.70, (0.15, 0.17, 0.09))], a.outputs['Fac']).outputs[0]
    f = n(nt, 'ShaderNodeTexNoise', Scale=60.0, Detail=5.0, Roughness=0.7); L(nt, tc, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.9, Distance=0.03); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    lk = n(nt, 'ShaderNodeTexNoise', Scale=7.0, Detail=6.0, Roughness=0.6); L(nt, tc, lk.inputs['Vector'])
    lake = math_(nt, 'LESS_THAN', lk.outputs['Fac'], 0.31)
    col = mix(nt, lake, col, (0.02, 0.06, 0.10))
    p = sphere('p_woods', r, loc, m, 192, 96)
    out(nt, principled(nt, col, 0.85, spec=0.3, normal=bp.outputs[0]).outputs[0])
    c = _clouds('c_woods', r * 1.012, loc, (0.85, 0.86, 0.84), 4.2, 0.54, 0.70, 0.85)
    return p, c

def planet_deep(r=1.0, loc=(0, 0, 0)):
    m, nt = mat('deep')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.0, Detail=8.0, Roughness=0.6); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.35, (0.002, 0.012, 0.018)), (0.65, (0.006, 0.05, 0.06))], a.outputs['Fac']).outputs[0]
    f = n(nt, 'ShaderNodeTexNoise', Scale=90.0, Detail=4.0, Roughness=0.6); L(nt, tc, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.25, Distance=0.01); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.16, spec=0.8, normal=bp.outputs[0]).outputs[0])
    p = sphere('p_deep', r, loc, m, 192, 96)
    c = _clouds('c_deep', r * 1.015, loc, (0.42, 0.47, 0.47), 2.6, 0.50, 0.66, 0.9)
    return p, c

def planet_crowd(r=1.0, loc=(0, 0, 0)):
    """poeira cinza coberta de pontos claros que, de perto, são gente"""
    m, nt = mat('crowd')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.2, Detail=8.0, Roughness=0.55); L(nt, tc, a.inputs['Vector'])
    base = ramp(nt, [(0.35, (0.16, 0.155, 0.15)), (0.65, (0.34, 0.33, 0.31))], a.outputs['Fac']).outputs[0]
    def dots(scale, size):
        v = n(nt, 'ShaderNodeTexVoronoi', Scale=scale); L(nt, tc, v.inputs['Vector'])
        return math_(nt, 'LESS_THAN', v.outputs['Distance'], size)
    d = math_(nt, 'MAXIMUM', dots(210.0, 0.30), dots(520.0, 0.32))
    dens = ramp(nt, [(0.30, (1, 1, 1)), (0.52, (0.25, 0.25, 0.25))], a.outputs['Fac']).outputs[0]
    col = mix(nt, math_(nt, 'MULTIPLY', d, dens), base, (0.88, 0.86, 0.80))
    out(nt, principled(nt, col, 0.95, spec=0.2).outputs[0])
    return sphere('p_crowd', r, loc, m, 192, 96)
