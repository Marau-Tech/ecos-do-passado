# Guia: vídeos analog horror

Este guia vale para qualquer vídeo. O que é de um formato específico fica no guia do modelo, em `modelos/<modelo>/GUIA.md`. Para pedir ao Claude: "faz um vídeo novo do modelo choose_planet seguindo o `GUIA.md`".

## Modelos

| Modelo | Formato | Guia |
|---|---|---|
| `choose_planet` | "Choose one": 4 planetas, 24 horas, tela final "CHOOSE." | [`modelos/choose_planet/GUIA.md`](modelos/choose_planet/GUIA.md) |
| `cctv` | Câmera de segurança sem narrador, de 40 a 120s | [`modelos/cctv/GUIA.md`](modelos/cctv/GUIA.md) |
| `binary` | "Pick one": 2 opções ruins, de 20 a 35s, tela final "PICK." | [`modelos/binary/GUIA.md`](modelos/binary/GUIA.md) |
| `probe_feed` | Imagens de sonda chegando linha a linha, sem narrador, de 30 a 60s | [`modelos/probe_feed/GUIA.md`](modelos/probe_feed/GUIA.md) |
| `eas` | Alerta de emergência na TV, com voz robótica, de 25 a 75s | [`modelos/eas/GUIA.md`](modelos/eas/GUIA.md) |
| `weather` | Previsão do tempo da TV local, de 35 a 75s | [`modelos/weather/GUIA.md`](modelos/weather/GUIA.md) |
| `rules` | Filme de segurança dos anos 80 com regras numeradas, de 40 a 80s | [`modelos/rules/GUIA.md`](modelos/rules/GUIA.md) |
| `glimpse` | Vislumbre sem texto e sem voz, em loop, de 6 a 15s | [`modelos/glimpse/GUIA.md`](modelos/glimpse/GUIA.md) |

Os modelos `binary` a `glimpse` vieram da pesquisa de tendências de novembro de 2026 e ainda não têm vídeo. O primeiro vídeo de cada um valida o guia: o que não funcionar no preview volta para o guia do modelo.

Separação:

- **`engine/` é o estilo:** render, filtros, OSD, barras, legendas, glitches, desenho 2D, trilha, fita e narração. Vale para todo modelo.
- **`modelos/<modelo>/` é o formato:** o que aparece nas barras, o contador, a abertura, a tela final e as regras do roteiro.
- **`videos/<video>/` é o conteúdo:** falas, cenas, cores e trilha daquele vídeo.

### Criar um modelo novo

1. Criar `modelos/<nome>/__init__.py` com `from modelos.base import *`.
2. Sobrescrever só as funções que mudam. A lista está em `modelos/base.py`:

| Função | O que define | Padrão |
|---|---|---|
| `LOOK` | Filtro da imagem (tabela abaixo) | `vhs` |
| `REC_DOT` | Luz vermelha de gravação no OSD | `True` |
| `rec_label` | Texto do canto superior esquerdo do OSD. `None` não mostra nada | `REC` |
| `counter` | Texto do canto superior direito do OSD | Nada |
| `footer` | Texto do canto inferior esquerdo do OSD | Tempo da fita |
| `title` | Título e subtítulo da barra de cima | Barra vazia |
| `opens_section` | Take que abre um trecho, para o título no modo 4:3 | Nenhum |
| `big_caption` | Take com legenda grande na barra de cima | Nenhum |
| `labels` | Rótulos em cima da imagem | Nenhum |
| `grade_key` | Chave de `GRADE` do take | O nome do take |
| `scene_module` | Arquivo que tem `build_<take>()` | O nome do take |
| `drawn` | Se o take é desenhado em 2D, sem Blender | Takes em `DRAWN` |
| `card` | Imagem de um take desenhado | `draw_<take>(rt)` do `cards.py` do vídeo |
| `paint` | Desenho por cima de um take, antes do OSD | `paint_<take>(img, rt)` do `cards.py`, se existir |

Para a duração, `bounded(shots, tela_final, mínimo, máximo, nome)` faz o `timing` e recusa vídeo fora da faixa do modelo. `shot_of(tl, t)` diz o take que está na tela, para o contador.

3. Criar `modelos/<nome>/GUIA.md` com as regras do formato: abertura, estrutura, duração e o que o roteiro precisa trazer.
4. Acrescentar o modelo na tabela acima.

Esse arquivo roda também dentro do Blender, então não pode importar PIL nem scipy. O desenho 2D de um modelo fica em `modelos/<nome>/draw.py` e só é importado dentro de `card` e `paint`, que nunca rodam no Blender.

### Filtros

| `LOOK` | Imagem | No glitch | Modelos |
|---|---|---|---|
| `vhs` | Fita: croma borrado, tracking, head switching | Neve, rolagem, faixas | `choose_planet`, `binary`, `rules` |
| `cctv` | Câmera de segurança: monocromática, granulada, 15 fps | Blocos corrompidos, perda de sinal | `cctv` |
| `broadcast` | TV de antena: fantasma, chuvisco fino, barra de zumbido | Rasga, rola e vira chuvisco | `eas`, `weather` |
| `webcam` | Webcam dos anos 2000: pouca resolução, blocos, cor em 5 bits, 10 fps | Blocos arrastados | `glimpse` |
| `probe` | Monitor de missão: 6 bits, erros de bit, fósforo | Pacotes perdidos | `probe_feed` |

Um vídeo pode trocar o filtro do modelo com `LOOK = '...'` no `timeline.py`. Os filtros ficam em `engine/looks.py`.

### Takes desenhados

Um take desenhado não passa pelo Blender: o post desenha a imagem dele em 2D a cada frame, a 960x720. Serve para telas de texto, cartelas, mapas e gráficos, e custa quase nada no render. O `./video` pula esses takes no render e na contagem de frames.

- O modelo pode desenhar takes próprios, como a tela de alerta do `eas` ou a cartela de regra do `rules`.
- O vídeo desenha os seus em `videos/<video>/cards.py`, com `draw_<take>(rt)`, e lista esses takes em `DRAWN` no `timeline.py`.
- `paint_<take>(img, rt)` no `cards.py` desenha por cima de um take renderizado, como um rótulo que acompanha o tempo.
- Take desenhado não passa pelo `GRADE` nem pelo `frame_fx`: a cor que sai do desenho é a final. O filtro e o glitch valem igual.
- `SUBLIM` aceita take desenhado, com o frame contado a 15 fps.
- `engine/gfx.py` tem o que se repete: fontes, texto digitado, parágrafo, letreiro, barras de cor, chuvisco, contagem de filme e ícones de tempo.
- O OSD fica em y < 70 e y > 610 do quadro. Deixe essas faixas livres no desenho.

## Regras fixas

| Item | Padrão |
|---|---|
| Idioma | **Inglês em tudo**: legendas, títulos, OSD e tela final |
| Formato | 9:16, 1080×1920, 30 fps |
| Layout | Quadro 4:3 no centro, barras pretas em cima e embaixo |
| Barra de cima | Título e subtítulo, se o modelo tiver |
| Barra de baixo | Legenda digitada letra por letra, se o modelo tiver |
| Quadro central | Só imagem e OSD (REC, SP e contador, se o modelo tiver). Nenhuma legenda em cima da cena |
| Filtro | Na tela inteira, barras incluídas. O modelo escolhe qual |
| Contexto | **Cada vídeo se explica sozinho**, como se fosse o único. Quem vê só ele não sabe que existiu outro vídeo. Nada de "mais", "outros", "de novo", "último" nas legendas, na narração e na legenda do post. O nome da pasta pode ser qualquer um, porque o espectador não vê |
| Narração | O modelo decide se há e qual voz do Kokoro usa. O padrão é `bm_lewis`, local, lendo as legendas |
| Preview | Obrigatório antes do render final |
| Legenda do post | `caption.txt` em inglês em todo vídeo, com até 5 hashtags e tendências do dia |

## Pastas

```
engine/            compartilhado por todos os vídeos
  lib.py           nós, objetos, câmera, névoa, render
  nature.py        céu, grama, árvores, casas
  post.py          montagem dos frames: imagem, cor, OSD, barras e legendas
  looks.py         filtros: vhs, cctv, broadcast, webcam, probe
  gfx.py           desenho 2D dos takes desenhados
  synth.py         mix de áudio, filtros, efeitos comuns, fita
  voice.py         narração com Kokoro
  render.py        render de um take
  project.py       caminhos do projeto
modelos/           formatos de vídeo
  base.py          contrato de um modelo, com os valores padrão
  <modelo>/        regras, títulos e contador daquele formato
    draw.py        desenho 2D do modelo, se tiver
videos/<video>/    tudo que é só daquele vídeo
  timeline.py      modelo usado, takes, legendas, glitches, cores
  *.py             cenas, um arquivo por trecho
  cards.py         takes desenhados do vídeo, se tiver
  audio.py         trilha
render/<video>/    frames, fora do git
  preview/         frames do preview
  final/           frames do render final
out/<video>/       entregas
  <video>.mp4      vídeo final, fora do git
  preview.mp4      preview, fora do git
  caption.txt      legenda do post, no git
site/              site do app do TikTok
tools/             Blender, venv, ffmpeg e modelo de voz, fora do git
video              comando único do projeto
setup.sh           reinstala o tools/
```

O nome do vídeo é `<número>-<modelo>-<nome>`, com o modelo que o vídeo segue logo depois do número e `_` virando `-`: `05-cctv-he-is-coming`, `06-eas-lower-moon`, `01-choose-planet-choose-one-planet`. A numeração é uma só para todos os modelos.

Regra de reaproveitamento: o que servir para mais de um modelo vai para `engine/`, e o que servir para vários vídeos do mesmo modelo vai para `modelos/<modelo>/`. Código de um vídeo não importa código de outro.

### Git

Repo público: `Felipe-Meneguzzi/analog-planetas`.

Versionam-se `engine/`, `modelos/`, `videos/`, `site/`, `GUIA.md`, `video`, `setup.sh`, `requirements.txt` e os `caption.txt`. Frames, vídeos, áudio e `tools/` ficam de fora pelo `.gitignore`.

### Outro PC

Precisa de Ubuntu 24.04 ou WSL com Python 3.12. Com Python 3.13 ou mais novo (Ubuntu 26.04 vem com 3.14) o `kokoro-onnx` não instala: crie o venv com 3.12 antes do `./setup.sh`, por exemplo `uv venv --python 3.12 tools/venv && tools/venv/bin/python -m ensurepip && ln -s pip3 tools/venv/bin/pip`. O `uv` pode vir de `pip install uv` num venv temporário.

```bash
git clone git@github.com:Felipe-Meneguzzi/analog-planetas.git
cd analog-planetas
sudo apt install curl xz-utils python3-venv fonts-dejavu-core libgl1 libsm6 libx11-6 libxext6 libxfixes3 libxi6 libxkbcommon0 libxrender1
./setup.sh
```

O `setup.sh` já instala a voz: coloca o `kokoro-onnx` no venv e baixa o modelo em `tools/kokoro/`. Veja "Voz do narrador" abaixo.

Isso basta para gerar vídeos novos. Vídeos prontos e frames não vão para o GitHub, então editar um vídeo antigo em outra máquina exige novo render.

O login do TikTok fica em `~/.config/analog-planetas/tiktok.json`, fora do repo. Em outro PC, rode `./video <video> tiktok login`.

`site/` é uma cópia do site do app do TikTok (termos, privacidade e callback), feito para `tiktok.felipemeneguzzi.dev`.

### Testar o PC novo

Fazer antes do primeiro render em um PC novo. O objetivo é descobrir o que o PC acessa e o que renderiza mais rápido.

**1. Ver o que o PC acessa:**

```bash
nproc                        # núcleos disponíveis
free -g                      # RAM disponível; no WSL costuma ser metade da real
nvidia-smi                   # GPU, driver e VRAM; se falhar, a GPU não está acessível
tools/blender/blender -b --python-expr "import bpy; p = bpy.context.preferences.addons['cycles'].preferences; [print(t, [d.name for d in p.get_devices_for_type(t)]) for t in ('CUDA', 'OPTIX')]"
```

No WSL, a GPU depende do driver NVIDIA instalado no Windows. Não instale driver dentro do WSL.

**2. Medir a CPU.** Rodar um take leve e um pesado, com a qualidade do render final:

```bash
export VIDEO=02-choose-planet-four-more-planets
tools/blender/blender -b -t $(($(nproc) / 2)) -P engine/render.py -- p1b 0,25,50 20 | grep '^\['
tools/blender/blender -b -t $(($(nproc) / 2)) -P engine/render.py -- p4c 0,25,50 20 | grep '^\['
```

O comando imprime os segundos por frame e grava em `render/<video>/final/`. Apague esses frames depois do teste.

**3. Medir a GPU.** Se ela apareceu no passo 1, pedir ao Claude para ligar a GPU no `reset()` do `engine/lib.py` e repetir os mesmos comandos. O `reset()` já liga a GPU (CUDA) sozinho quando existe uma, e cai na CPU quando não existe. `GPU=0` na frente do comando força a CPU. O `read_factory_settings` apaga as preferências, por isso o dispositivo é escolhido depois dele. Ignore o primeiro frame, porque ele inclui a preparação da GPU.

**4. Comparar.** A CPU roda 2 Blenders ao mesmo tempo, então divida o tempo dela por 2. A GPU roda 1 só: nesse caso, trocar o `-P 2` do `render()` no `./video` para `-P 1`.

| Resultado | Decisão |
|---|---|
| GPU não aparece no passo 1 | Ficar na CPU |
| GPU falha por falta de VRAM em algum take | Ficar na CPU, ou usar a GPU só nos takes leves |
| GPU menos de 30% mais rápida | Ficar na CPU, que é o caminho já testado |
| GPU 30% mais rápida ou mais | Usar a GPU |

Comparar também um frame de cada, porque o resultado visual precisa ser o mesmo. Anotar a decisão e os tempos na tabela abaixo.

| PC | CPU | GPU | Tempo por frame | Usa |
|---|---|---|---|---|
| Principal | i5-12400F, 12 threads | GT 610, não serve para o Cycles | Cerca de 4,5s por frame, com 2 Blenders | CPU |
| Secundário | i5-10400F, 12 threads | GTX 1660 SUPER (CUDA) | CPU, 2 Blenders: 3,5s (p1b) e 2,5s (p4c) por frame. GPU, 2 Blenders: 2,15s e 1,9s. GPU, 3 Blenders: 2,07s e 1,53s | GPU, 3 Blenders |

### Voz do narrador

Roda local, na CPU, sem chave e sem custo. São 350 MB de modelo, e a narração de um vídeo leva cerca de 15s.

Para instalar em um projeto que já tem `tools/`, rode `./setup.sh` de novo: ele pula o que já existe. Se precisar baixar à mão:

```bash
tools/venv/bin/pip install -r requirements.txt
mkdir -p tools/kokoro && cd tools/kokoro
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

Para testar sem render: `./video <video> build`. O comando imprime o tempo de cada fala.

`VOICE` no `timeline.py`:

| Chave | O que faz |
|---|---|
| `voice`, `lang`, `speed` | Voz do Kokoro, idioma (`en-gb` ou `en-us`) e velocidade. Vozes úteis: `bm_lewis` e `bm_george` (britânicas, narrador), `am_michael` e `am_onyx` (alerta), `am_adam` e `af_heart` (apresentador) |
| `fx` | Efeito em toda fala: `tape` (padrão, fita velha), `radio` (alto-falante pequeno) ou `broadcast` (TV, sem oscilação) |
| `radio` | Falas que saem pelo rádio mesmo com outro `fx` |
| `names`, `name_at` | Falas extras no começo de um take, como o nome de cada opção |

### Sons prontos

Em `engine/synth.py`, além do `boom`, `click`, `digital`, `bell` e `chord`:

| Função | Som |
|---|---|
| `beep(f, dur)` | Bipe curto, de contagem ou teste |
| `attention(dur)` | Tom de atenção do EAS, 853 e 960 Hz |
| `same_header(t0)` / `eom(t0)` | Rajadas de dados do cabeçalho e do fim de mensagem do EAS |
| `downlink(dur)` | Dados de telemetria chegando |
| `muzak(a, b)` | Música de previsão do tempo entre a e b |

`END_TONE = False` tira o tom da tela final, e `LOOP = True` emenda o fim do áudio no começo. Os dois vêm do modelo.

### Pendências

- Vídeo 2: o código e o preview já têm narração, mas o mp4 final é o antigo, de 65s, e não será refeito. O código fica como referência do padrão. Vídeo 1 segue sem narração.
- TikTok: `./video <video> tiktok` só foi testado contra servidor falso. Falta criar o app no portal, publicar o `site/` e rodar o login.
- PC secundário: teste feito, usa a GPU com 2 Blenders (24% a 39% mais rápida que a CPU). Frame da GPU igual ao da CPU. GPU e CPU ao mesmo tempo ficou pior que a GPU sozinha, porque a GPU precisa dos threads da CPU para preparar a cena e fazer o denoise.

## Comandos

```bash
./video <video> preview [takes]   # render rápido e monta preview.mp4
./video <video> final [takes]     # render completo e monta <video>.mp4
./video <video> build             # só áudio, pós e montagem
./video <video> status            # frames prontos do render final
./video <video> still 7 33.8      # frames de conferência, em segundos
./video <video> tiktok login      # autoriza a conta do TikTok, uma vez só
./video <video> tiktok            # envia o vídeo para os rascunhos do TikTok
```

- Sem `takes`, o comando roda todos. `preview p1a p3b` refaz só esses dois.
- `final` continua de onde parou, porque pula frames que já existem.
- Para refazer um take no final, apague `render/<video>/final/<take>/` e rode `final <take>`.
- Trocar texto ou cor não exige render: edite `timeline.py` e rode `build`. `PREVIEW=1 ./video <video> build` faz o mesmo com os frames do preview.
- `VERT=0` gera 4:3 sem as barras.

## Etapas

| # | Etapa | Você faz | Tempo aproximado |
|---|---|---|---|
| 1 | Roteiro | Passa a ideia, lê o roteiro que o Claude propôs e edita falas e direção | Minutos |
| 2 | Cenas | Nada, só depois de aprovar o roteiro | Minutos |
| 3 | Preview | Assiste e aponta correções | Cerca de 6 min por rodada |
| 4 | Render final | Nada | 1h15 a 1h40 para 971 frames no PC principal (CPU). No secundário (GPU), 27 min para 1107 frames |
| 5 | Legenda do post | Nada | Minutos |
| 6 | Entrega | Assiste com som antes de postar | Minutos |

### 1. Roteiro

**Antes de escrever qualquer cena, o Claude apresenta o roteiro e espera sua aprovação.** É o momento barato de mudar falas e direção, porque depois disso cada ajuste custa um novo preview. O roteiro apresentado traz:

- A confirmação de que nada depende de outro vídeo.
- Por take: a legenda exata, se houver, e o que a câmera mostra.
- O que o guia do modelo exigir.
- O que o vídeo exige de novo no engine (objetos, materiais, efeitos) e o que reaproveita.

Você pode reescrever legenda ou mudar a direção. Só com o "aprovado" o Claude cria `videos/<video>/` e segue para as cenas. Se mudar o roteiro depois de pronto o preview, avise: legenda e cor se refazem rápido, mas direção de câmera e cena pedem novo render.

Depois de aprovado, definir em `timeline.py`:

- `MODELO`: o modelo do vídeo. As duas primeiras linhas são `from modelos import <modelo> as MODELO` e `from modelos.<modelo> import *`.
- `SHOTS`: nome do take, duração e legendas `(início, fim, texto)`.
- `TOTAL, START, END_CARD = timing(SHOTS, segundos_da_tela_final)`.
- `EVENTS`: glitches, com tempo, força e duração.
- `SUBLIM` e `SUBLIM_GRADE`: quadros subliminares.
- `VOICE`: voz, idioma e velocidade.
- `GRADE` e `frame_fx`: cor por trecho e efeito extra por frame.

Legendas curtas: até 2 linhas de cerca de 26 caracteres, com frases secas no presente.

A narração sai do texto das legendas. O `voice.py` acelera a fala só o necessário para caber antes da próxima, até 1,25x, e o `build` imprime o tempo de cada fala. A trilha abaixa enquanto o narrador fala. Um vídeo sem `VOICE` no `timeline.py` sai sem narração.

### 2. Cenas

Um arquivo por trecho, com uma função `build_<take>()` por take e um dicionário `SHOTS` com as durações. O `scene_module` do modelo diz em qual arquivo cada take está.

Como o quadro central é 4:3, o enquadramento atual já serve. Se um vídeo novo usar a tela vertical inteira, a câmera e o `RES` precisam mudar antes do render.

### 3. Preview

```bash
./video <video> preview
```

Renderiza 5 frames por take com 6 samples e monta com legendas, filtro, narração e áudio, como uma animação quadro a quadro. O preview sai a 15 fps e com encode rápido, e a montagem leva cerca de 4 min. O final segue em 30 fps com `preset slow`. O preview mostra enquadramento, cores, ritmo e texto. O movimento e os detalhes finos só aparecem no render final.

Se só texto ou cor mudou, `PREVIEW=1 ./video <video> build` remonta sem renderizar de novo. Não rode `build` depois de `preview`, porque o `preview` já monta o vídeo.

Só seguir para a etapa 4 depois da sua aprovação.

### 4. Render final

```bash
./video <video> final
```

Roda 3 Blenders em paralelo na GPU (cada um com um terço dos núcleos) ou 2 na CPU (metade dos núcleos cada). Usa a GPU quando o `nvidia-smi` responde e cai na CPU quando não (a GT 610 do PC principal não serve). `GPU=0 ./video ...` força a CPU e `BLENDERS=n` troca o número de Blenders. Ao fim, confere se todos os frames existem e monta o vídeo.

### 5. Legenda do post

Todo vídeo sai com `out/<video>/caption.txt`:

```
Frase que puxa comentário, em inglês. 👇

⚠️ Flashing lights

#tags #do #video


--- Notas, não postar ---
Data, tendências usadas, tendências descartadas e fontes.
```

- **Sem spoiler:** a legenda e as hashtags não podem revelar o que aparece no vídeo. Nada de citar planetas, monstros, reviravoltas ou o que cada opção tem. A frase só faz a pergunta e puxa o comentário.
- Hashtags falam do gênero e do formato, nunca do conteúdo: `#analoghorror` pode, `#backrooms` não, se o vídeo tiver um planeta de Backrooms.
- Pesquisar as tendências no dia da geração, não reaproveitar de vídeo anterior. Um bom ponto de partida é o [TokChart](https://tokchart.com/tiktok-trending-hashtags).
- Usar só tendências que têm a ver com o vídeo e não entregam nada dele. As descartadas ficam nas notas, para você decidir.
- **Máximo de 5 hashtags**, porque TikTok e Reels só aceitam 5. Escolher as 5 mais relevantes para o conteúdo e as tendências do dia. As que ficarem de fora vão para as notas.
- Se o vídeo demorar a sair, refazer o arquivo perto da postagem, porque tendência envelhece em dias.

### 6. Entrega

- Conferir frames de cada trecho: título, legenda, OSD e tela final.
- Assistir com som. O Claude mede o áudio, mas não ouve, e confere frames, mas não vê o movimento.
- Conferir o limite de duração da plataforma.

## Armadilhas já conhecidas

| Problema | Solução |
|---|---|
| Textura gerada em memória não chega ao Cycles | Salvar em PNG e carregar do disco |
| Câmera dentro do terreno | Conferir a altura da câmera contra o relevo no preview |
| Frame todo preto | A câmera entrou em um objeto: conferir a posição dela contra o que se move |
| Revelação antes da hora | Conferir se a imagem não entrega o que a legenda seguinte vai contar |
| Emissão forte estourando a cor | Baixar a força e saturar a cor |
| OSD ilegível em céu claro | Manter o contorno preto no texto |
| Texto sumindo na parte de baixo do quadro | Manter o OSD acima da faixa de head switching |
| Arquivo gigante por causa do ruído VHS | Usar `crf 25`, preset `slow` |
