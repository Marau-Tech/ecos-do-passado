# Modelo: cctv

Gravação de câmera de segurança, em que a história é contada só pela imagem e pelo som.

## Regras fixas

| Item | Padrão |
|---|---|
| Perspectiva | **Sempre câmera de segurança**: fixa, alta, grande angular. Pode cortar entre câmeras, mas nunca mover como câmera de mão |
| Narração | **Nenhuma.** Sem narrador e sem legenda. Todo texto vem de dentro da cena, como uma tela ou uma placa |
| Duração | **Entre 40 e 120 segundos.** O `timing()` recusa vídeo fora disso |
| Atmosfera | Escura, monocromática e com ruído de sensor |
| Glitch | **Só quando algo acontece.** Sem glitch em corte de câmera. A imagem fica estável no resto do tempo |
| Barra de cima | Nome da câmera e do local |
| OSD | Câmera, data e hora correndo |
| Tela final | "NO SIGNAL" por 2s |

## Roteiro

Além do que o `GUIA.md` pede, o roteiro apresentado traz:

- Local, câmeras e horário.
- Os acontecimentos com o segundo em que ocorrem, porque não há fala para guiar o ritmo.
- O que aparece em cada tela ou texto da cena.
- Os sons de cada acontecimento.

O texto da cena precisa ser legível no celular: mostre de perto, em uma câmera próxima.

## Timeline

Além do que o `GUIA.md` pede:

- As legendas de cada take em `SHOTS` ficam vazias.
- `TOTAL, START, END_CARD = timing(SHOTS)`.
- `EVENTS` só com os glitches dos acontecimentos.
- `CAMS`: para cada take, `(câmera, local)`.
- `CLOCK`: hora inicial em segundos. `DATE`: data do OSD.
- `GRADE`: chave `cam`.
- Sem `VOICE`.

## Cenas

Todos os takes ficam em `scene.py`.

- **Render por estado:** com `HOLD_STATES = True`, o `update` devolve o estado da cena, e frames com o mesmo estado viram cópia, sem render. Por isso o preview e o final mostram o tempo exato de cada acontecimento. O vídeo 05 teve 49 renders em 1140 frames, e o final inteiro levou cerca de 9 min no PC principal.
- **Imagens de tela:** `PREP = ['prep']` no `timeline.py` roda `build_prep()` antes dos takes e grava as imagens em `render/<video>/_tex/`. Para refazer uma imagem, apague o PNG dela.
- **Texto de tela:** usar objeto de texto do Blender, porque o Python dele não tem PIL.
- **Escuro:** o `frame_fx` aplica ganho com `a ** 0.6`. Ajustar isso não exige render.
- **Legibilidade:** o que importa para a história precisa de uma câmera perto. Em plano aberto, uma tela vira um retângulo de poucos pixels.
