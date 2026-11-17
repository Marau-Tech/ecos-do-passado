"""Materiais do personagem POV. As texturas usam o UV em metros das gaiolas, e não as
coordenadas do objeto: a malha deforma a cada frame e a textura precisa ir junto com o tecido."""
import math
from lib import mat, n, L, ramp, math_, mix, out


def lin(c):
    """sRGB 0..1 -> linear."""
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def _bsdf(nt, color, rough, **kw):
    p = nt.nodes.new('ShaderNodeBsdfPrincipled')
    if isinstance(color, tuple):
        p.inputs['Base Color'].default_value = (*color, 1)
    else:
        L(nt, color, p.inputs['Base Color'])
    if isinstance(rough, (int, float)):
        p.inputs['Roughness'].default_value = rough
    else:
        L(nt, rough, p.inputs['Roughness'])
    for k, v in kw.items():
        name = {'metal': 'Metallic', 'spec': 'Specular IOR Level', 'sheen': 'Sheen Weight',
                'sheen_rough': 'Sheen Roughness', 'sss': 'Subsurface Weight', 'sss_radius': 'Subsurface Radius',
                'sss_scale': 'Subsurface Scale', 'coat': 'Coat Weight', 'coat_rough': 'Coat Roughness'}[k]
        p.inputs[name].default_value = v
    return p


def _uv(nt):
    uv = n(nt, 'ShaderNodeUVMap')
    uv.uv_map = 'UVMap'
    sep = n(nt, 'ShaderNodeSeparateXYZ')
    L(nt, uv.outputs['UV'], sep.inputs[0])
    return uv.outputs['UV'], sep


def _noise(nt, vec, scale, detail=3.0, rough=0.55):
    x = n(nt, 'ShaderNodeTexNoise', Scale=scale, Detail=detail, Roughness=rough)
    L(nt, vec, x.inputs['Vector'])
    return x.outputs['Fac']


def _bump(nt, height, strength, dist, normal=None):
    b = n(nt, 'ShaderNodeBump', Strength=strength, Distance=dist)
    L(nt, height, b.inputs['Height'])
    if normal is not None:
        L(nt, normal, b.inputs['Normal'])
    return b.outputs['Normal']


def _line(nt, coord, at, half):
    """1 numa faixa estreita em torno de coord = at, 0 fora."""
    d = math_(nt, 'ABSOLUTE', math_(nt, 'SUBTRACT', coord, at))
    return math_(nt, 'SUBTRACT', 1.0, math_(nt, 'DIVIDE', d, half), clamp=True)


def fabric(name, color, rough=0.9, sheen=0.25, mottle=0.14, fine=0.25, quilt=None, seams=(), crease=None):
    """Lã ou algodão: variação de tom, felpa fina, brilho de tecido (sheen).
    quilt: período (m) do pesponto ao longo de u; seams: valores de u com costura (abertura da frente);
    crease: u do vinco da calça."""
    m, nt = mat(name)
    uv, sep = _uv(nt)
    base = lin(color)
    dark = tuple(c * (1 - mottle) for c in base)
    light = tuple(min(1.0, c * (1 + mottle * 0.7)) for c in base)
    big = _noise(nt, uv, 9.0, 4.0)
    col = ramp(nt, [(0.3, dark), (0.72, light)], big).outputs[0]
    fuzz = _noise(nt, uv, 340.0, 2.0, 0.6)
    height = math_(nt, 'MULTIPLY', fuzz, 0.4)
    normal = _bump(nt, math_(nt, 'ADD', height, math_(nt, 'MULTIPLY', big, 0.6)), fine, 0.0015)
    if quilt:
        ph = math_(nt, 'MULTIPLY', sep.outputs['X'], math.pi / quilt)
        puff = math_(nt, 'POWER', math_(nt, 'ABSOLUTE', math_(nt, 'SINE', ph)), 0.45)
        col = mix(nt, 1.0, col, mix(nt, puff, (0.55, 0.55, 0.55), (1.0, 1.0, 1.0)), 'MULTIPLY')
        normal = _bump(nt, puff, 0.9, 0.006, normal)
    for u in seams:
        ln = _line(nt, sep.outputs['X'], u, 0.004)
        col = mix(nt, math_(nt, 'MULTIPLY', ln, 0.55), col, (0.0, 0.0, 0.0))
        normal = _bump(nt, math_(nt, 'SUBTRACT', 1.0, ln), 0.6, 0.003, normal)
    if crease is not None:
        ln = _line(nt, sep.outputs['X'], crease, 0.006)
        normal = _bump(nt, ln, 0.35, 0.003, normal)
    p = _bsdf(nt, col, rough, sheen=sheen, sheen_rough=0.5, spec=0.25)   # lã: brilho de fibra discreto
    L(nt, normal, p.inputs['Normal'])
    out(nt, p.outputs[0])
    return m


def knit(name, color):
    """Tricô de lã (luvas): carreiras finas ao longo do dedo."""
    m, nt = mat(name)
    uv, sep = _uv(nt)
    rows = n(nt, 'ShaderNodeTexWave', {'wave_type': 'BANDS', 'bands_direction': 'Y'}, Scale=180.0, Distortion=1.5)
    L(nt, uv, rows.inputs['Vector'])
    big = _noise(nt, uv, 12.0)
    base = lin(color)
    col = ramp(nt, [(0.25, tuple(c * 0.8 for c in base)), (0.75, base)], big).outputs[0]
    normal = _bump(nt, rows.outputs['Fac'], 0.35, 0.0015)
    p = _bsdf(nt, col, 0.95, sheen=0.6, sheen_rough=0.4, spec=0.2)
    L(nt, normal, p.inputs['Normal'])
    out(nt, p.outputs[0])
    return m


def _rest(nt):
    """Coordenadas de repouso da pele (atributo 'pov_rest'): a textura não escorrega nem tem costura."""
    a = nt.nodes.new('ShaderNodeAttribute')
    a.attribute_name = 'pov_rest'
    return a.outputs['Vector']


def skin(name, color):
    m, nt = mat(name)
    uv = _rest(nt)
    base = lin(color)
    blotch = _noise(nt, uv, 22.0, 5.0, 0.6)
    red = (min(1, base[0] * 1.06), base[1] * 0.88, base[2] * 0.86)
    col = ramp(nt, [(0.25, tuple(c * 0.86 for c in base)), (0.5, base), (0.78, red)], blotch).outputs[0]
    freck = _noise(nt, uv, 160.0, 2.0)
    col = mix(nt, math_(nt, 'MULTIPLY', math_(nt, 'GREATER_THAN', freck, 0.68), 0.25), col, tuple(c * 0.7 for c in base))
    pores = _noise(nt, uv, 900.0, 2.0)
    lumps = _noise(nt, uv, 110.0, 3.0)
    # brilho irregular (mais oleoso nos nós, mais seco no resto) e penugem fina (sheen):
    # é o que tira o aspecto de plástico liso
    oil = _noise(nt, uv, 40.0, 4.0, 0.6)
    rough = ramp(nt, [(0.3, (0.42,) * 3), (0.5, (0.55,) * 3), (0.72, (0.68,) * 3)], oil).outputs[0]
    p = _bsdf(nt, col, 0.5, sss=0.45, sss_radius=(1.0, 0.42, 0.25), sss_scale=0.007, spec=0.24,
              sheen=0.12, sheen_rough=0.45)
    L(nt, rough, p.inputs['Roughness'])
    L(nt, _bump(nt, pores, 0.1, 0.0004, _bump(nt, lumps, 0.12, 0.001)), p.inputs['Normal'])
    out(nt, p.outputs[0])
    return m


def skin_tint(name, color):
    """Unha: quase da cor da pele, um pouco mais clara e lisa."""
    m, nt = mat(name)
    p = _bsdf(nt, lin(color), 0.36, sss=0.3, sss_radius=(1.0, 0.4, 0.25), sss_scale=0.003, spec=0.38)
    out(nt, p.outputs[0])
    return m


def leather(name, color, rough=0.4, polish=0.0):
    m, nt = mat(name)
    uv, _ = _uv(nt)
    base = lin(color)
    wear = _noise(nt, uv, 18.0, 5.0)
    col = ramp(nt, [(0.35, base), (0.8, tuple(min(1, c * 1.9) for c in base))], wear).outputs[0]
    r = ramp(nt, [(0.3, (rough * 0.8,) * 3), (0.8, (min(1, rough * 1.35),) * 3)], wear).outputs[0]
    grain = _noise(nt, uv, 260.0, 3.0)
    creases = n(nt, 'ShaderNodeTexWave', {'wave_type': 'BANDS', 'bands_direction': 'Y'}, Scale=28.0, Distortion=6.0, Detail=3.0)
    L(nt, uv, creases.inputs['Vector'])
    h = math_(nt, 'ADD', math_(nt, 'MULTIPLY', grain, 0.5), math_(nt, 'MULTIPLY', creases.outputs['Fac'], 0.3))
    p = _bsdf(nt, col, 0.4, spec=0.5, coat=polish, coat_rough=0.2)
    L(nt, r, p.inputs['Roughness'])
    L(nt, _bump(nt, h, 0.25, 0.001), p.inputs['Normal'])
    out(nt, p.outputs[0])
    return m


def wood(name, color):
    m, nt = mat(name)
    uv, _ = _uv(nt)
    grain = n(nt, 'ShaderNodeTexWave', {'wave_type': 'BANDS', 'bands_direction': 'Y'}, Scale=90.0, Distortion=9.0, Detail=4.0)
    L(nt, uv, grain.inputs['Vector'])
    base = lin(color)
    col = ramp(nt, [(0.2, tuple(c * 0.62 for c in base)), (0.75, base)], grain.outputs['Fac']).outputs[0]
    wear = _noise(nt, uv, 6.0)
    col = mix(nt, math_(nt, 'MULTIPLY', wear, 0.25), col, tuple(min(1, c * 1.4) for c in base))
    p = _bsdf(nt, col, 0.45, spec=0.45, coat=0.25, coat_rough=0.35)
    L(nt, _bump(nt, grain.outputs['Fac'], 0.08, 0.001), p.inputs['Normal'])
    out(nt, p.outputs[0])
    return m


def metal(name, color, rough=0.35, metallic=0.9):
    m, nt = mat(name)
    uv, _ = _uv(nt)
    wear = _noise(nt, uv, 40.0, 4.0)
    r = ramp(nt, [(0.3, (rough * 0.7,) * 3), (0.75, (min(1, rough * 1.6),) * 3)], wear).outputs[0]
    p = _bsdf(nt, lin(color), 0.35, metal=metallic, spec=0.5)
    L(nt, r, p.inputs['Roughness'])
    out(nt, p.outputs[0])
    return m


def flat(name, color, rough=0.5, metallic=0.0):
    m, nt = mat(name)
    out(nt, _bsdf(nt, lin(color), rough, metal=metallic).outputs[0])
    return m


def enamel(name, color):
    """Mostrador de esmalte: branco quente, brilhante, com leve variação."""
    m, nt = mat(name)
    uv, _ = _uv(nt)
    v = _noise(nt, uv, 400.0, 3.0)
    col = ramp(nt, [(0.3, tuple(c * 0.96 for c in lin(color))), (0.7, lin(color))], v).outputs[0]
    p = _bsdf(nt, col, 0.12, spec=0.5, coat=0.6, coat_rough=0.05)
    out(nt, p.outputs[0])
    return m


def glass(name):
    """Vidro fino do relógio: transparente, com reflexo pela borda (Fresnel). Não usa
    transmissão, para não escurecer o mostrador com poucos rebatimentos de luz."""
    m, nt = mat(name)
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    gl = nt.nodes.new('ShaderNodeBsdfGlossy')
    gl.inputs['Roughness'].default_value = 0.02
    lw = nt.nodes.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.12
    mx = nt.nodes.new('ShaderNodeMixShader')
    L(nt, lw.outputs['Fresnel'], mx.inputs[0])
    L(nt, tr.outputs[0], mx.inputs[1])
    L(nt, gl.outputs[0], mx.inputs[2])
    out(nt, mx.outputs[0])
    return m
