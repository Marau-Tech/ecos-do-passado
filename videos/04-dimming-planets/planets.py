from lib import *

def planet_evening(r=1.0, loc=(0, 0, 0)):
    """campos dourados e colinas cor de pêssego"""
    m, nt = mat('evening')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=3.2, Detail=10.0, Roughness=0.62); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.36, (0.30, 0.13, 0.05)), (0.46, (0.72, 0.38, 0.12)), (0.56, (0.98, 0.70, 0.24)), (0.66, (1.0, 0.90, 0.60))], a.outputs['Fac']).outputs[0]
    vo = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=14.0); L(nt, tc, vo.inputs['Vector'])
    col = mix(nt, math_(nt, 'LESS_THAN', vo.outputs['Distance'], 0.02), col, (0.40, 0.20, 0.08))     # divisas dos campos
    f = n(nt, 'ShaderNodeTexNoise', Scale=26.0, Detail=6.0, Roughness=0.6); L(nt, tc, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.35, Distance=0.03); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.7, spec=0.3, normal=bp.outputs[0]).outputs[0])
    return sphere('p_evening', r, loc, m, 192, 96)

def planet_broadcast(r=1.0, loc=(0, 0, 0)):
    """deserto de ferrugem com crateras rasas"""
    m, nt = mat('broadcast')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=3.0, Detail=10.0, Roughness=0.6); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.32, (0.16, 0.06, 0.03)), (0.52, (0.42, 0.17, 0.07)), (0.68, (0.62, 0.34, 0.16))], a.outputs['Fac']).outputs[0]
    f = n(nt, 'ShaderNodeTexNoise', Scale=18.0, Detail=9.0, Roughness=0.66); L(nt, tc, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.7, Distance=0.04); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.85, spec=0.2, normal=bp.outputs[0]).outputs[0])
    return sphere('p_broadcast', r, loc, m, 192, 96)

def planet_shutter(r=1.0, loc=(0, 0, 0)):
    """rocha quase preta"""
    m, nt = mat('shutter')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=3.4, Detail=11.0, Roughness=0.62); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.32, (0.012, 0.012, 0.014)), (0.68, (0.09, 0.09, 0.10))], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=0.9, Distance=0.05); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.6, spec=0.4, normal=bp.outputs[0]).outputs[0])
    return sphere('p_shutter', r, loc, m, 192, 96)

def planet_dimming(r=1.0, loc=(0, 0, 0)):
    """pedra cinza, com a luz vermelha vindo de fora"""
    m, nt = mat('dimming')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.8, Detail=10.0, Roughness=0.6); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.32, (0.10, 0.08, 0.09)), (0.68, (0.46, 0.40, 0.40))], a.outputs['Fac']).outputs[0]
    f = n(nt, 'ShaderNodeTexNoise', Scale=30.0, Detail=6.0, Roughness=0.65); L(nt, tc, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.7, Distance=0.03); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.8, spec=0.2, normal=bp.outputs[0]).outputs[0])
    return sphere('p_dimming', r, loc, m, 192, 96)

def halo(r, loc, color, strength=1.0):
    """brilho em volta de uma estrela: forte no centro, some na borda"""
    m, nt = mat('halo')
    lw = n(nt, 'ShaderNodeLayerWeight', Blend=0.5)
    a = math_(nt, 'POWER', math_(nt, 'SUBTRACT', 1.0, lw.outputs['Facing']), 3.0)
    e = n(nt, 'ShaderNodeEmission', Strength=strength)
    e.inputs['Color'].default_value = (*color, 1)
    tr = n(nt, 'ShaderNodeBsdfTransparent')
    ms = n(nt, 'ShaderNodeMixShader')
    L(nt, a, ms.inputs[0]); L(nt, tr.outputs[0], ms.inputs[1]); L(nt, e.outputs[0], ms.inputs[2])
    out(nt, ms.outputs[0])
    return sphere('halo', r, loc, m, 48, 24), m
