"""Envia o vídeo para a caixa de entrada do TikTok (Content Posting API, escopo video.upload).

  ./video <video> tiktok login   autoriza a conta, uma vez só
  ./video <video> tiktok         envia out/<video>/<video>.mp4 (PREVIEW=1 envia o preview.mp4)

O vídeo chega como rascunho: a publicação e a legenda são feitas no app do TikTok.
Credenciais e tokens ficam em ~/.config/analog-planetas/tiktok.json, fora do git.
"""
import getpass, json, os, secrets, sys, time, urllib.error, urllib.parse, urllib.request
import project

API = 'https://open.tiktokapis.com'
AUTHORIZE = 'https://www.tiktok.com/v2/auth/authorize/'
CONFIG = os.path.expanduser('~/.config/analog-planetas/tiktok.json')
CHUNK = 10_000_000       # a API aceita de 5 a 64 MB por chunk; o último absorve o resto
STATUS_WAIT = 300
POLL = 5


def load():
    if not os.path.exists(CONFIG):
        return {}
    with open(CONFIG) as f:
        return json.load(f)


def save(cfg):
    os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
    tmp = CONFIG + '.tmp'
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(cfg, f, indent=2)
    os.replace(tmp, CONFIG)


def call(url, data, headers):
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f'Erro {e.code} em {url}: {e.read().decode(errors="replace")}')


def token_request(cfg, **fields):
    body = urllib.parse.urlencode({
        'client_key': cfg['client_key'], 'client_secret': cfg['client_secret'], **fields,
    }).encode()
    r = call(f'{API}/v2/oauth/token/', body, {'Content-Type': 'application/x-www-form-urlencoded'})
    if 'access_token' not in r:
        sys.exit(f'TikTok recusou o token: {r}')
    # o refresh_token muda a cada renovação, então precisa ser gravado antes de qualquer uso
    cfg.update(access_token=r['access_token'], refresh_token=r['refresh_token'],
               open_id=r.get('open_id'), expires_at=time.time() + r['expires_in'])
    save(cfg)


def login():
    cfg = load()
    if 'client_key' not in cfg:
        cfg['client_key'] = input('Client key: ').strip()
        cfg['client_secret'] = getpass.getpass('Client secret: ').strip()
        cfg['redirect_uri'] = input('Redirect URI cadastrada no app: ').strip()
        save(cfg)
    state = secrets.token_urlsafe(16)
    print('\nAbra no navegador, logado na conta do TikTok:\n')
    print(AUTHORIZE + '?' + urllib.parse.urlencode({
        'client_key': cfg['client_key'], 'scope': 'user.info.basic,video.upload',
        'response_type': 'code', 'redirect_uri': cfg['redirect_uri'], 'state': state,
    }))
    query = urllib.parse.parse_qs(urllib.parse.urlparse(
        input('\nCole aqui o endereço completo para onde o navegador foi: ').strip()).query)
    if 'code' not in query:
        sys.exit(f'Autorização sem code: {query}')
    if query.get('state') != [state]:
        sys.exit('O state não confere. Rode o login de novo.')
    token_request(cfg, code=query['code'][0], grant_type='authorization_code',
                  redirect_uri=cfg['redirect_uri'])
    user = api('/v2/user/info/?fields=open_id,display_name', cfg['access_token'])['user']
    print(f'Conta autorizada: {user["display_name"]}. Tokens em {CONFIG}')


def access_token():
    cfg = load()
    if 'refresh_token' not in cfg:
        sys.exit('Sem autorização. Rode: ./video <video> tiktok login')
    if cfg['expires_at'] - 60 < time.time():
        token_request(cfg, grant_type='refresh_token', refresh_token=cfg['refresh_token'])
    return cfg['access_token']


def api(path, token, body=None):
    data = json.dumps(body).encode() if body else None
    r = call(f'{API}{path}', data, {
        'Authorization': f'Bearer {token}', 'Content-Type': 'application/json; charset=UTF-8',
    })
    if r.get('error', {}).get('code') != 'ok':
        sys.exit(f'TikTok recusou {path}: {r.get("error")}')
    return r['data']


def chunks(size):
    """Devolve chunk_size, total e os intervalos (início, fim) de cada envio."""
    chunk = min(size, CHUNK)
    total = size // chunk
    ranges = [(i * chunk, (i + 1) * chunk - 1) for i in range(total)]
    ranges[-1] = (ranges[-1][0], size - 1)
    return chunk, total, ranges


def put(url, data, first, last, size):
    headers = {'Content-Type': 'video/mp4', 'Content-Length': str(len(data)),
               'Content-Range': f'bytes {first}-{last}/{size}'}
    for attempt in range(4):
        req = urllib.request.Request(url, data=data, headers=headers, method='PUT')
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == 3:
                sys.exit(f'Erro {e.code} no envio de {first}-{last}: {e.read().decode(errors="replace")}')
        except urllib.error.URLError as e:
            if attempt == 3:
                sys.exit(f'Falha de rede no envio de {first}-{last}: {e.reason}')
        time.sleep(2 ** attempt)


def caption():
    path = f'{project.OUT}/caption.txt'
    if not os.path.exists(path):
        return ''
    with open(path) as f:
        return f.read().split('--- Notas')[0].strip()


def upload():
    path = f'{project.OUT}/{"preview" if project.PREVIEW else project.VIDEO}.mp4'
    if not os.path.exists(path):
        sys.exit(f'Não existe: {path}')
    size = os.path.getsize(path)
    chunk, total, ranges = chunks(size)
    token = access_token()
    data = api('/v2/post/publish/inbox/video/init/', token, {'source_info': {
        'source': 'FILE_UPLOAD', 'video_size': size, 'chunk_size': chunk, 'total_chunk_count': total,
    }})
    publish_id = data['publish_id']
    with open(path, 'rb') as f:
        for n, (first, last) in enumerate(ranges, 1):
            status = put(data['upload_url'], f.read(last - first + 1), first, last, size)
            print(f'chunk {n}/{total}: {status}')
    if status != 201:
        sys.exit(f'O último chunk devolveu {status}, esperado 201.')

    deadline = time.time() + STATUS_WAIT
    while time.time() < deadline:
        r = api('/v2/post/publish/status/fetch/', access_token(), {'publish_id': publish_id})
        state = r.get('status')
        if state == 'FAILED':
            sys.exit(f'TikTok falhou ao processar: {r.get("fail_reason")}')
        if state in ('SEND_TO_USER_INBOX', 'PUBLISH_COMPLETE'):
            print(f'\nPronto: abra a notificação na caixa de entrada do TikTok ({state}).')
            print(f'\nLegenda para colar:\n\n{caption()}')
            return
        time.sleep(POLL)
    sys.exit(f'Sem resposta final em {STATUS_WAIT}s. publish_id: {publish_id}')


if __name__ == '__main__':
    login() if sys.argv[1:] == ['login'] else upload()
