# Guia: vídeos analog horror

Receita baseada no vídeo "Choose one to spend 24 hours on". Vale tanto para você ler quanto para pedir ao Claude: "faz um vídeo novo seguindo o `GUIA.md`".

## Regras fixas

| Item | Padrão |
|---|---|
| Idioma | **Inglês em tudo**: legendas, títulos, OSD e tela final |
| Formato | 9:16, 1080×1920, 30 fps |
| Layout | Quadro 4:3 no centro, barras pretas em cima e embaixo |
| Barra de cima | Título do trecho (branco) e subtítulo (dourado) |
| Barra de baixo | Legenda digitada letra por letra |
| Quadro central | Só imagem e OSD (REC, contador, SP). Nenhuma legenda em cima da cena |
| Filtro VHS | Na tela inteira, barras incluídas |
| Duração | Cerca de 74s no formato atual: 5s de intro e 17,25s por item |
| Narração | **Em todo vídeo.** Voz `bm_lewis` do Kokoro, local, lendo as legendas e o nome de cada planeta |
| Abertura de cada planeta | Planeta girando com a câmera parada por 2,25s enquanto o narrador diz o nome. Depois vêm o zoom e a explicação |
| Preview | Obrigatório antes do render final |
| Legenda do post | `caption.txt` em inglês em todo vídeo, com até 5 hashtags e tendências do dia |

## Pastas

```
engine/            compartilhado por todos os vídeos
  lib.py           nós, objetos, câmera, névoa, render
  nature.py        céu, grama, árvores, casas
  post.py          filtro VHS, OSD, barras e legendas
  synth.py         mix de áudio, filtros, efeitos comuns, fita
  voice.py         narração com Kokoro
  render.py        render de um take
  project.py       caminhos do projeto
videos/<video>/    tudo que é só daquele vídeo
  timeline.py      takes, legendas, títulos, glitches, cores
  intro.py, p1.py  cenas (p1 a p4)
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

O nome do vídeo é numerado: `01-choose-one-planet`, `02-...`.

Regra de reaproveitamento: o que servir para mais de um vídeo vai para `engine/`. Código de um vídeo não importa código de outro.

### Git

Repo público: `Felipe-Meneguzzi/analog-planetas`.

Versionam-se `engine/`, `videos/`, `site/`, `GUIA.md`, `video`, `setup.sh`, `requirements.txt` e os `caption.txt`. Frames, vídeos, áudio e `tools/` ficam de fora pelo `.gitignore`.

### Outro PC

Precisa de Ubuntu 24.04 ou WSL com Python 3.12.

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

### Pendências

- Vídeo 2: o código e o preview já têm narração, mas o mp4 final é o antigo, de 65s, e não será refeito. O código fica como referência do padrão. Vídeo 1 segue sem narração.
- TikTok: `./video <video> tiktok` só foi testado contra servidor falso. Falta criar o app no portal, publicar o `site/` e rodar o login.
- GPU: `engine/lib.py` força o Cycles na CPU. No PC com GTX 1660 o render pode ficar mais rápido, mas isso exige mudar o código.

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
| 1 | Roteiro | Passa a ideia | Minutos |
| 2 | Cenas | Nada | Minutos |
| 3 | Preview | Assiste e aponta correções | Cerca de 10 min por rodada |
| 4 | Render final | Nada | 1h15 a 1h40 para 971 frames neste PC |
| 5 | Legenda do post | Nada | Minutos |
| 6 | Entrega | Assiste com som antes de postar | Minutos |

### 1. Roteiro

Criar `videos/<video>/` e definir em `timeline.py`:

- `SHOTS`: nome do take, duração e legendas `(início, fim, texto)`.
- `PLANETS`: título, subtítulo e primeiro take de cada trecho.
- `EVENTS`: glitches, com tempo, força e duração.
- `SUBLIM`: quadros subliminares.
- `VOICE`: voz, velocidade e o texto falado com o nome de cada planeta.
- `NAME_HOLD`: segundos do planeta girando antes do zoom, 2,25 no padrão. Somar nas durações dos takes `p1a` a `p4a` e em `SECTION`, e começar a legenda desses takes em `NAME_HOLD + 0.5`.
- `GRADE`, `END_TEXT`, `INTRO_LABELS`, `SECTION` e `frame_fx`: cor por trecho, tela final, números da intro, duração do trecho e efeito extra por frame.

O formato que funcionou:

- Abrir com a pergunta e todas as opções na tela.
- Em cada planeta, deixar ele girando enquanto o narrador diz o nome. Só depois vêm o zoom e a explicação.
- Mostrar cada opção em 4 takes de 3,5 a 4s, do mais distante para o mais próximo.
- Fechar cada trecho com uma frase que vira a chave ("No visitor ever wanted to go back.").
- Variar o tom entre as opções, porque o contraste assusta mais que quatro monstros seguidos.
- Terminar com uma tela preta de uma palavra ("CHOOSE.").

Legendas curtas: até 2 linhas de cerca de 26 caracteres, com frases secas no presente.

A narração sai do texto das legendas. O `voice.py` acelera a fala só o necessário para caber antes da próxima, até 1,25x, e o `build` imprime o tempo de cada fala. A trilha abaixa enquanto o narrador fala. Um vídeo sem `VOICE` no `timeline.py` sai sem narração.

### 2. Cenas

Um arquivo por trecho, com uma função `build_<take>()` por take e um dicionário `SHOTS` com as durações. Os takes se chamam `intro` e `p1a` a `p4d`: o módulo sai do nome do take.

Nos takes de planeta, a primeira linha do `update` segura o zoom até o nome terminar:

```python
def update(t, u):
    u = zoom_after(t, NAME_HOLD, SHOTS['p1a'])
```

Como o quadro central é 4:3, o enquadramento atual já serve. Se um vídeo novo usar a tela vertical inteira, a câmera e o `RES` precisam mudar antes do render.

### 3. Preview

```bash
./video <video> preview
```

Renderiza 5 frames por take com 6 samples e monta com legendas, filtro, narração e áudio, como uma animação quadro a quadro. O preview mostra enquadramento, cores, ritmo e texto. O movimento e os detalhes finos só aparecem no render final.

Só seguir para a etapa 4 depois da sua aprovação.

### 4. Render final

```bash
./video <video> final
```

Roda 2 Blenders em paralelo, cada um com metade dos núcleos, só na CPU, porque a GT 610 não serve. Ao fim, confere se todos os frames existem e monta o vídeo.

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
