import bpy, math, random, os, sys, time
import numpy as np
from project import ROOT, RENDER, FRAMES
from mathutils import Vector, Euler, Matrix, noise

RES = (640, 480)
FPS = 15

def reset(samples=24):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    c = s.cycles
    c.device = 'CPU'
    if os.environ.get('GPU', '1') == '1':
        p = bpy.context.preferences.addons['cycles'].preferences
        p.compute_device_type = 'CUDA'
        p.get_devices()
        gpus = [d for d in p.devices if d.type == 'CUDA']
        for d in p.devices:
            d.use = d in gpus
        if gpus:
            c.device = 'GPU'
    c.samples = samples
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.06
    c.use_denoising = True
    c.denoiser = 'OPENIMAGEDENOISE'
    c.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    c.max_bounces = 4
    c.diffuse_bounces = 2
    c.glossy_bounces = 2
    c.transmission_bounces = 2
    c.transparent_max_bounces = 8
    c.volume_bounces = 0
    c.caustics_reflective = False
    c.caustics_refractive = False
    c.use_light_tree = True
    c.sample_clamp_indirect = 4
    s.render.use_persistent_data = True
    s.render.resolution_x, s.render.resolution_y = RES
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = 'PNG'
    s.render.image_settings.color_mode = 'RGB'
    s.render.image_settings.compression = 15
    s.view_settings.view_transform = 'Standard'
    s.view_settings.look = 'None'
    s.render.film_transparent = False
    w = bpy.data.worlds.new('w'); w.use_nodes = True
    s.world = w
    return s

# ---------- nós ----------
def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    m.node_tree.nodes.clear()
    return m, m.node_tree

def n(nt, typ, _a=None, **ins):
    """cria nó; _a = dict de atributos; ins = inputs por nome"""
    x = nt.nodes.new(typ)
    for k, v in (_a or {}).items():
        setattr(x, k, v)
    for k, v in ins.items():
        k = k.replace('_', ' ')
        x.inputs[k].default_value = v
    return x

def L(nt, a, b):
    nt.links.new(a, b)

def ramp(nt, stops, inp=None, interp='LINEAR'):
    r = nt.nodes.new('ShaderNodeValToRGB')
    cr = r.color_ramp
    cr.interpolation = interp
    while len(cr.elements) < len(stops):
        cr.elements.new(0.5)
    for e, (p, c) in zip(cr.elements, stops):
        e.position = p
        e.color = (*c, 1) if len(c) == 3 else c
    if inp is not None:
        L(nt, inp, r.inputs['Fac'])
    return r

def math_(nt, op, a, b=None, clamp=False):
    x = nt.nodes.new('ShaderNodeMath'); x.operation = op; x.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if v is None: continue
        if isinstance(v, (int, float)):
            x.inputs[i].default_value = v
        else:
            L(nt, v, x.inputs[i])
    return x.outputs[0]

def mix(nt, fac, a, b, mode='MIX', clamp=True):
    x = nt.nodes.new('ShaderNodeMixRGB'); x.blend_type = mode; x.use_clamp = clamp
    for key, v in (('Fac', fac), ('Color1', a), ('Color2', b)):
        if isinstance(v, (int, float)):
            x.inputs[key].default_value = v
        elif isinstance(v, tuple):
            x.inputs[key].default_value = (*v, 1) if len(v) == 3 else v
        else:
            L(nt, v, x.inputs[key])
    return x.outputs[0]

def out(nt, shader):
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    L(nt, shader, o.inputs['Surface'])
    return o

def principled(nt, color=None, rough=0.5, metal=0.0, spec=0.5, normal=None, emis=None, emis_str=1.0):
    p = nt.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Roughness'].default_value = rough if isinstance(rough, (int, float)) else 0.5
    if not isinstance(rough, (int, float)): L(nt, rough, p.inputs['Roughness'])
    p.inputs['Metallic'].default_value = metal
    p.inputs['Specular IOR Level'].default_value = spec
    if isinstance(color, tuple):
        p.inputs['Base Color'].default_value = (*color, 1)
    elif color is not None:
        L(nt, color, p.inputs['Base Color'])
    if normal is not None:
        L(nt, normal, p.inputs['Normal'])
    if emis is not None:
        if isinstance(emis, tuple):
            p.inputs['Emission Color'].default_value = (*emis, 1)
        else:
            L(nt, emis, p.inputs['Emission Color'])
        p.inputs['Emission Strength'].default_value = emis_str
    return p

def simple(name, color, rough=0.5, metal=0.0, emis=None, emis_str=1.0):
    m, nt = mat(name)
    out(nt, principled(nt, color, rough, metal, emis=emis, emis_str=emis_str).outputs[0])
    return m

def emission(name, color, strength=1.0):
    m, nt = mat(name)
    e = n(nt, 'ShaderNodeEmission', Strength=strength)
    e.inputs['Color'].default_value = (*color, 1)
    out(nt, e.outputs[0])
    return m

# ---------- objetos ----------
def link(o):
    bpy.context.scene.collection.objects.link(o); return o

def sphere(name, r=1.0, loc=(0, 0, 0), m=None, seg=128, rings=64):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=r, location=loc)
    o = bpy.context.object; o.name = name
    o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
    o.data.update()
    if m: o.data.materials.append(m)
    return o

def ico(name, r=1.0, loc=(0, 0, 0), m=None, sub=3):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=loc)
    o = bpy.context.object; o.name = name
    o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
    o.data.update()
    if m: o.data.materials.append(m)
    return o

def box(name, size, loc=(0, 0, 0), m=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    o.scale = size
    if m: o.data.materials.append(m)
    return o

def mesh_from(name, verts, faces, m=None, smooth=False, uvs=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.update()
    if smooth:
        me.polygons.foreach_set('use_smooth', [True] * len(me.polygons)); me.update()
    o = bpy.data.objects.new(name, me); link(o)
    if m: me.materials.append(m)
    return o

def fast_mesh(name, verts, tris, m=None, smooth=False):
    """verts Nx3, tris Mx3 via foreach_set (milhões de faces sem from_pydata)"""
    verts = np.asarray(verts, np.float32); tris = np.asarray(tris, np.int32)
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(verts)); me.vertices.foreach_set('co', verts.ravel())
    me.loops.add(tris.size); me.loops.foreach_set('vertex_index', tris.ravel())
    me.polygons.add(len(tris))
    me.polygons.foreach_set('loop_start', np.arange(0, tris.size, 3, dtype=np.int32))
    me.update(calc_edges=True)
    if smooth:
        me.polygons.foreach_set('use_smooth', [True] * len(me.polygons)); me.update()
    o = bpy.data.objects.new(name, me); link(o)
    if m: me.materials.append(m)
    return o

def tube(name, pts, radii, m=None, res=4, bevel=3, kind='NURBS'):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'; c.bevel_depth = 1.0; c.bevel_resolution = bevel
    c.resolution_u = res; c.use_fill_caps = True
    sp = c.splines.new(kind)
    sp.points.add(len(pts) - 1)
    sp.use_endpoint_u = True
    sp.order_u = min(4, len(pts))
    set_tube_data(sp, pts, radii)
    o = bpy.data.objects.new(name, c); link(o)
    if m: c.materials.append(m)
    return o

def set_tube_data(sp, pts, radii):
    for p, co, r in zip(sp.points, pts, radii):
        p.co = (*co, 1); p.radius = r

def set_tube(o, pts, radii):
    set_tube_data(o.data.splines[0], pts, radii)

def sun(strength=3.0, direction=(1, -1, 0.5), color=(1, 1, 1), angle=1.0):
    l = bpy.data.lights.new('sun', 'SUN')
    l.energy = strength; l.color = color; l.angle = math.radians(angle)
    o = bpy.data.objects.new('sun', l); link(o)
    d = Vector(direction).normalized()
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o

def point(loc, energy, color=(1, 1, 1), r=0.1):
    l = bpy.data.lights.new('pt', 'POINT'); l.energy = energy; l.color = color; l.shadow_soft_size = r
    o = bpy.data.objects.new('pt', l); link(o); o.location = loc
    return o

def camera(loc=(0, -5, 0), target=(0, 0, 0), lens=35, clip=(0.05, 100000)):
    d = bpy.data.cameras.new('cam'); d.lens = lens; d.sensor_width = 36
    d.clip_start, d.clip_end = clip
    o = bpy.data.objects.new('cam', d); link(o)
    bpy.context.scene.camera = o
    o.location = loc
    look(o, target)
    return o

def look(o, target, roll=0.0):
    d = Vector(target) - o.location
    q = d.to_track_quat('-Z', 'Y')
    if roll:
        q = q @ Euler((0, 0, roll)).to_quaternion()
    o.rotation_euler = q.to_euler()

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)

def lerp(a, b, u):
    return a + (b - a) * u

def vlerp(a, b, u):
    return Vector(a).lerp(Vector(b), u)

def shake(t, amp, freq=9.0, seed=0.0):
    return Vector((noise.noise(Vector((t * freq, seed, 0))),
                   noise.noise(Vector((t * freq, seed + 7, 3))),
                   noise.noise(Vector((t * freq, seed + 13, 9))))) * amp

# ---------- mundo ----------
def world_space(nebula=(0.02, 0.01, 0.03), neb_strength=1.0, star=1.0):
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    tc = n(nt, 'ShaderNodeTexCoord')
    v = n(nt, 'ShaderNodeTexVoronoi', Scale=70.0)
    L(nt, tc.outputs['Generated'], v.inputs['Vector'])
    near = math_(nt, 'LESS_THAN', v.outputs['Distance'], 0.075)
    bright = n(nt, 'ShaderNodeSeparateColor')
    L(nt, v.outputs['Color'], bright.inputs[0])
    vis = math_(nt, 'GREATER_THAN', bright.outputs[0], 0.72)
    amp = math_(nt, 'POWER', bright.outputs[1], 3.0)
    s1 = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', near, vis), math_(nt, 'MULTIPLY', amp, 4.0 * star))
    nz = n(nt, 'ShaderNodeTexNoise', Scale=1.6, Detail=8.0, Roughness=0.6)
    L(nt, tc.outputs['Generated'], nz.inputs['Vector'])
    nb = ramp(nt, [(0.42, (0, 0, 0)), (0.75, nebula)], nz.outputs['Fac'])
    col = mix(nt, 1.0, nb.outputs[0], s1, 'ADD', clamp=False)
    b = n(nt, 'ShaderNodeBackground', Strength=neb_strength)
    L(nt, col, b.inputs['Color'])
    o = n(nt, 'ShaderNodeOutputWorld')
    L(nt, b.outputs[0], o.inputs['Surface'])

def world_flat(color, strength=1.0):
    w = bpy.context.scene.world; nt = w.node_tree; nt.nodes.clear()
    b = n(nt, 'ShaderNodeBackground', Strength=strength)
    b.inputs['Color'].default_value = (*color, 1)
    o = n(nt, 'ShaderNodeOutputWorld')
    L(nt, b.outputs[0], o.inputs['Surface'])

def fog(color, start, depth, strength=1.0, falloff='QUADRATIC'):
    """névoa barata: passe mist + compositor (sem volume)"""
    s = bpy.context.scene
    vl = s.view_layers[0]
    vl.use_pass_mist = True
    m = s.world.mist_settings
    m.start, m.depth, m.falloff = start, depth, falloff
    s.use_nodes = True
    nt = s.node_tree; nt.nodes.clear()
    rl = nt.nodes.new('CompositorNodeRLayers')
    mx = nt.nodes.new('CompositorNodeMixRGB'); mx.blend_type = 'MIX'
    mx.inputs[2].default_value = (*color, 1)
    mul = nt.nodes.new('CompositorNodeMath'); mul.operation = 'MULTIPLY'
    mul.inputs[1].default_value = strength
    nt.links.new(rl.outputs['Mist'], mul.inputs[0])
    nt.links.new(mul.outputs[0], mx.inputs[0])
    nt.links.new(rl.outputs['Image'], mx.inputs[1])
    c = nt.nodes.new('CompositorNodeComposite')
    nt.links.new(mx.outputs[0], c.inputs[0])

def atmosphere(parent_r, color, sun_dir, thick=1.04, power=3.5, strength=1.6, loc=(0, 0, 0)):
    m, nt = mat('atmo')
    lw = n(nt, 'ShaderNodeLayerWeight', Blend=0.5)
    g = n(nt, 'ShaderNodeNewGeometry')
    dot = n(nt, 'ShaderNodeVectorMath', {'operation': 'DOT_PRODUCT'})
    L(nt, g.outputs['Normal'], dot.inputs[0]); dot.inputs[1].default_value = Vector(sun_dir).normalized()
    lit = math_(nt, 'MAXIMUM', math_(nt, 'ADD', math_(nt, 'MULTIPLY', dot.outputs['Value'], 0.8), 0.3), 0.0)
    rim = math_(nt, 'POWER', lw.outputs['Facing'], power)
    fac = math_(nt, 'MULTIPLY', rim, lit)
    e = n(nt, 'ShaderNodeEmission'); e.inputs['Color'].default_value = (*color, 1)
    L(nt, math_(nt, 'MULTIPLY', fac, strength), e.inputs['Strength'])
    tr = n(nt, 'ShaderNodeBsdfTransparent')
    add = n(nt, 'ShaderNodeAddShader')
    L(nt, tr.outputs[0], add.inputs[0]); L(nt, e.outputs[0], add.inputs[1])
    out(nt, add.outputs[0])
    return sphere('atmo', parent_r * thick, loc, m, 96, 48)

def lathe(profile, sides=8):
    """perfil [(raio, z), ...] girado em Z; devolve vértices e triângulos com tampas"""
    pr = np.asarray(profile, np.float32); R = len(pr)
    a = np.arange(sides) * 2 * np.pi / sides
    v = np.stack([pr[:, None, 0] * np.cos(a), pr[:, None, 0] * np.sin(a),
                  np.repeat(pr[:, None, 1], sides, 1)], -1).reshape(-1, 3)
    r, k = np.meshgrid(np.arange(R - 1), np.arange(sides), indexing='ij')
    p0 = r * sides + k; p1 = r * sides + (k + 1) % sides
    t = np.concatenate([np.stack([p0, p1, p1 + sides], -1).reshape(-1, 3),
                        np.stack([p0, p1 + sides, p0 + sides], -1).reshape(-1, 3)])
    n0 = len(v)
    v = np.vstack([v, [[0, 0, pr[0, 1]], [0, 0, pr[-1, 1]]]]).astype(np.float32)
    k = np.arange(sides); k2 = (k + 1) % sides
    caps = np.concatenate([np.stack([np.full(sides, n0), k2, k], 1),
                           np.stack([np.full(sides, n0 + 1), (R - 1) * sides + k, (R - 1) * sides + k2], 1)])
    return v, np.vstack([t, caps])

def scatter(name, v, t, pos, yaw=None, scale=None, m=None, smooth=True):
    """copia a malha (v, t) em N posições, numa malha só. scale: N, Nx3 ou None"""
    v = np.asarray(v, np.float32); t = np.asarray(t, np.int32); pos = np.asarray(pos, np.float32)
    N = len(pos)
    yaw = np.zeros(N, np.float32) if yaw is None else np.asarray(yaw, np.float32)
    sc = np.ones((N, 3), np.float32) if scale is None else np.asarray(scale, np.float32)
    if sc.ndim == 1: sc = np.repeat(sc[:, None], 3, 1)
    P = v[None] * sc[:, None, :]
    c = np.cos(yaw)[:, None]; s = np.sin(yaw)[:, None]
    V = np.stack([P[..., 0] * c - P[..., 1] * s, P[..., 0] * s + P[..., 1] * c, P[..., 2]], -1) + pos[:, None, :]
    T = (t[None] + (np.arange(N) * len(v))[:, None, None]).reshape(-1, 3)
    return fast_mesh(name, V.reshape(-1, 3), T, m, smooth)

def clone(objs, loc, rot=0.0, s=1.0):
    """cópias leves (mesma malha) de uma lista de objetos, presas a um empty"""
    root = bpy.data.objects.new('grp', None); link(root)
    root.location = loc; root.rotation_euler.z = rot; root.scale = (s, s, s)
    for o in objs:
        c = o.copy(); link(c); c.parent = root
        c.hide_render = False; c.hide_viewport = False
    return root

def hide(objs):
    for o in objs:
        o.hide_render = True; o.hide_viewport = True

def facing(pos, target):
    """yaw para a frente (-Y) de cada ponto olhar para o alvo"""
    d = np.asarray(target, np.float32)[:2] - np.asarray(pos, np.float32)[:, :2]
    return np.arctan2(d[:, 0], -d[:, 1])

def zoom_after(t, hold, dur):
    """progresso 0..1 de um movimento que só começa depois de hold segundos"""
    return min(1.0, max(0.0, (t - hold) / (dur - hold)))

# ---------- render ----------
def render_shot(name, update, dur, frames=None, res=None, samples=None):
    s = bpy.context.scene
    if res: s.render.resolution_x, s.render.resolution_y = res
    if samples: s.cycles.samples = samples
    nf = int(round(dur * FPS))
    d = f'{FRAMES}/{name}'; os.makedirs(d, exist_ok=True)
    todo = frames if frames is not None else range(nf)
    for i in todo:
        p = f'{d}/{i:04d}.png'
        if frames is None and os.path.exists(p): continue
        t0 = time.time()
        update(i / FPS, i / max(1, nf - 1))
        s.frame_set(i)
        s.render.filepath = p
        bpy.ops.render.render(write_still=True)
        print(f'[{name}] {i+1}/{nf} {time.time()-t0:.1f}s', flush=True)


# ---------- ruído vetorizado ----------
_rs = np.random.RandomState(11)
_G = _rs.rand(256, 256).astype(np.float32)
def vnoise(x, y):
    xi = np.floor(x).astype(int); yi = np.floor(y).astype(int)
    fx = x - xi; fy = y - yi
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
    a = _G[yi % 256, xi % 256]; b = _G[yi % 256, (xi + 1) % 256]
    c = _G[(yi + 1) % 256, xi % 256]; d = _G[(yi + 1) % 256, (xi + 1) % 256]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy

def fbm(x, y, o=5, lac=2.0, g=0.5):
    v = 0; a = 1; s = 0
    for i in range(o):
        v = v + a * vnoise(x + i * 17.3, y + i * 9.1); s += a; a *= g; x = x * lac; y = y * lac
    return v / s

def grid_mesh(name, size, n_, hfun, m=None, center=(0, 0), smooth=True):
    xs = np.linspace(-size / 2, size / 2, n_) + center[0]
    ys = np.linspace(-size / 2, size / 2, n_) + center[1]
    X, Y = np.meshgrid(xs, ys)
    Z = hfun(X, Y)
    v = np.stack([X, Y, Z], -1).reshape(-1, 3)
    i = np.arange(n_ - 1)
    a = (i[:, None] * n_ + i[None, :]).ravel()
    t = np.concatenate([np.stack([a, a + 1, a + n_ + 1], 1), np.stack([a, a + n_ + 1, a + n_], 1)])
    return fast_mesh(name, v, t, m, smooth)
