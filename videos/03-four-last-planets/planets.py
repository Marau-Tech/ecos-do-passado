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

def planet_salt(r=1.0, loc=(0, 0, 0)):
    """crosta de sal rachada em polígonos, com lagos azuis"""
    m, nt = mat('salt')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.0, Detail=8.0, Roughness=0.55); L(nt, tc, a.inputs['Vector'])
    base = ramp(nt, [(0.35, (0.80, 0.84, 0.88)), (0.65, (0.97, 0.97, 0.95))], a.outputs['Fac']).outputs[0]
    vo = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=9.0); L(nt, tc, vo.inputs['Vector'])
    crack = math_(nt, 'LESS_THAN', vo.outputs['Distance'], 0.03)
    col = mix(nt, crack, base, (0.45, 0.52, 0.60))
    lk = n(nt, 'ShaderNodeTexNoise', Scale=3.4, Detail=6.0, Roughness=0.6); L(nt, tc, lk.inputs['Vector'])
    lake = math_(nt, 'LESS_THAN', lk.outputs['Fac'], 0.36)
    col = mix(nt, lake, col, (0.35, 0.62, 0.78))
    out(nt, principled(nt, col, 0.25, spec=0.7).outputs[0])
    return sphere('p_salt', r, loc, m, 192, 96)

def planet_cul(r=1.0, loc=(0, 0, 0)):
    """terra escura com malhas de luzes âmbar, como bairros"""
    m, nt = mat('cul')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.4, Detail=8.0, Roughness=0.55); L(nt, tc, a.inputs['Vector'])
    base = ramp(nt, [(0.35, (0.02, 0.018, 0.024)), (0.65, (0.06, 0.05, 0.06))], a.outputs['Fac']).outputs[0]
    v1 = n(nt, 'ShaderNodeTexVoronoi', Scale=16.0); L(nt, tc, v1.inputs['Vector'])
    dots = math_(nt, 'LESS_THAN', v1.outputs['Distance'], 0.2)
    land = math_(nt, 'GREATER_THAN', a.outputs['Fac'], 0.46)
    lights = math_(nt, 'MULTIPLY', dots, land)
    emis = mix(nt, lights, (0, 0, 0), (1.0, 0.62, 0.22))
    out(nt, principled(nt, base, 0.8, spec=0.2, emis=emis, emis_str=9.0).outputs[0])
    return sphere('p_cul', r, loc, m, 192, 96)

def planet_white(r=1.0, loc=(0, 0, 0)):
    """gelo azulado coberto por uma tempestade em faixas"""
    m, nt = mat('white')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.6, Detail=10.0, Roughness=0.6); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.30, (0.50, 0.60, 0.72)), (0.62, (0.90, 0.94, 0.98))], a.outputs['Fac']).outputs[0]
    f = n(nt, 'ShaderNodeTexNoise', Scale=40.0, Detail=5.0, Roughness=0.7); L(nt, tc, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.4, Distance=0.02); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.55, spec=0.4, normal=bp.outputs[0]).outputs[0])
    p = sphere('p_white', r, loc, m, 192, 96)
    c = _clouds('c_white', r * 1.02, loc, (0.93, 0.95, 0.98), 3.2, 0.44, 0.60, 0.95)
    return p, c

def planet_twin(r=1.0, loc=(0, 0, 0)):
    """rocha roxa e preta com veios que brilham"""
    m, nt = mat('twin')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.8, Detail=10.0, Roughness=0.62); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.30, (0.018, 0.010, 0.04)), (0.65, (0.14, 0.07, 0.18))], a.outputs['Fac']).outputs[0]
    vo = n(nt, 'ShaderNodeTexVoronoi', {'feature': 'DISTANCE_TO_EDGE'}, Scale=3.2); L(nt, tc, vo.inputs['Vector'])
    vein = math_(nt, 'LESS_THAN', vo.outputs['Distance'], 0.018)
    emis = mix(nt, vein, (0, 0, 0), (0.75, 0.30, 1.0))
    f = n(nt, 'ShaderNodeTexNoise', Scale=70.0, Detail=5.0, Roughness=0.65); L(nt, tc, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.8, Distance=0.03); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.75, spec=0.3, normal=bp.outputs[0], emis=emis, emis_str=1.6).outputs[0])
    return sphere('p_twin', r, loc, m, 192, 96)
