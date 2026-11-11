# Modelo: survive

Uma simulação que parece um jogo. No centro há algo com vida: uma fogueira, uma lanterna, um planeta, um rádio. Um perigo tira vida dele, como chuva, mariposas ou meteoros. Aliados vêm das bordas para trazer vida e podem ser destruídos no caminho. No escuro, fora do lugar seguro, alguma coisa espera: quando a vida cai, ela chega mais perto, e quando a vida sobe, ela recua. O espectador torce como num vídeo de "will the ball escape?", e o horror cresce junto com o perigo.

O formato vem da onda de simulações de física do TikTok e dos Shorts, que prendem com uma pergunta no topo, duas forças opostas, um placar e um som para cada colisão. Parece que tudo está por um fio, mas o resultado é escolhido: a física é determinística por semente, e o vídeo usa a semente com o drama que quer.

Tudo é desenhado em 2D, sem Blender. São cerca de 3 min de preview para 40s.

## Mecânica e skin

O modelo separa duas coisas:

| Parte | Onde fica | O que define |
|---|---|---|
| **Mecânica** | `sim.py` | Vida, colisões, ritmo das ameaças e dos aliados, lugar seguro, vigias e eventos. Não sabe o que cada coisa é |
| **Skin** | `skins/<nome>.py`, ou `videos/<video>/skin.py` se for só daquele vídeo | O que cada coisa é: cenário, desenho, sons, os números da física que combinam com ela e o fim |
| **Kit** | `kit.py` | Peças que qualquer skin usa: silhueta alta, olhos no escuro, campo de calor (fogo, brasa, vela), luz e camadas |

O vídeo escolhe com `SKIN = '<nome>'`. Uma skin que serve para mais de um vídeo vai para `skins/`.

| Skin | Centro | Perigo | Aliado | No escuro |
|---|---|---|---|---|
| `campfire` | Fogueira numa clareira | Chuva, que vira tempestade com relâmpagos | Brasas vindas dos cantos de cima | Silhuetas altas e uma multidão entre as árvores |

Ideias que a mecânica já cobre: lanterna e mariposas (`aim`), planeta e meteoros (`aim` com `anchor = 0`), vela e vento, rádio e estática, farol e neblina.

## Regras fixas

| Item | Padrão |
|---|---|
| Texto | Só o título na barra de cima, `TITLE` ou `TITLES[take]`, e o placar na de baixo. **Sem legenda.** O `timing()` recusa legenda |
| Placar | Barra de vida e contagem até o `until`. Os textos são `HUD_NAME` e `HUD_CLOCK`, ou o `HUD` da skin |
| Narração | Nenhuma |
| Duração | De 25 a 60s |
| Filtro | `vhs`, sem OSD no quadro |
| Fim | **Muda a cada vídeo.** A mecânica diz se venceu (passou do `until`) ou perdeu (vida a zero, sem volta). A skin desenha cada caso, e o vídeo pode pôr uma coisa a mais |
| Legenda do post | Uma pergunta sem dizer o fim: "Did it make it?", "Would you have kept it alive?" |

## Mecânica

O vídeo troca qualquer valor com `SIM = dict(...)` no `timeline.py`. A ordem é: padrão do `sim.py`, depois o `SIM` da skin, depois o do vídeo. Os dicionários de dentro (`core`, `threat`, `ally`) se juntam chave a chave: `SIM = dict(threat=dict(dmg=2.5))` só troca o dano.

| Chave | O que faz |
|---|---|
| `hp0`, `burn`, `until` | Vida inicial, vida que o centro perde sozinho por segundo, e o segundo em que a contagem acaba |
| `core` | Posição, tamanho conforme a vida (`w`, `h`, `exp`), área de colisão (`anchor`, `ry`) e o ponto para onde os aliados vão (`aim`). `anchor = 0.45` é algo apoiado no chão, como uma fogueira. `anchor = 0` é algo centrado, como um planeta |
| `threat` | `mode`: `rain` cai de cima com vento, `aim` vem das bordas mirando o centro com desvio `spread`. Também `rate` (curva de ameaças por segundo), `wind`, `speed`, `dmg` e `floor` (o chão do `rain`) |
| `ally` | Vida (`hp`, em acertos), intervalo (`gap`, curva), primeiro (`first`), pausa antes do `until` (`stop`), velocidade, balanço, faixa de altura em que nascem e ganho ao chegar (`gain0 + gain1 × vida que sobrou`) |
| `dark` | Raio do lugar seguro: `r0 + r1 × vida` |
| `watch` | Vigias: quantos, quando chega o primeiro e o intervalo entre eles, e o tamanho |

As curvas são listas `(segundo, valor)` com interpolação entre os pontos.

O perigo que conta precisa ser legível: o espectador tem que conseguir seguir uma ameaça até o aliado. Enfeite no fundo, como a chuva fina da `campfire`, não entra na física.

Há dois geradores aleatórios. Um decide o placar, e o outro (`sim.rv`) só enfeita e é o que a skin usa. Por isso a busca, que roda sem desenho, dá o mesmo resultado do vídeo. Mexer no `SIM` muda o resultado de todas as sementes: refaça a busca.

Eventos que a física gera, para o desenho e o som: `spawn` (aliado nasce), `hit` (ameaça acerta o centro), `block` (ameaça acerta o aliado), `lost` (aliado destruído), `feed` (aliado chega), `floor` (ameaça do `rain` bate no chão, só com desenho) e `out` (a vida acabou).

## Escolher a semente

```bash
VIDEO=<video> PYTHONPATH=engine tools/venv/bin/python -m modelos.survive.sim 300           # escapa por pouco
VIDEO=<video> PYTHONPATH=engine tools/venv/bin/python -m modelos.survive.sim 300 out       # perde depois de lutar
```

Roda 300 sementes em cerca de 7s, com a skin e o `SIM` do vídeo, e lista as 10 melhores com: vida no `until`, a menor vida e quando ela ocorre, o segundo em que perdeu, aliados que chegaram, aliados perdidos e viradas. O que funciona:

- **Escapar:** a menor vida abaixo de 5%, nos últimos 8s antes do `until`.
- **Perder:** tarde, depois de pelo menos uma virada. Perder cedo frustra, e o espectador sai.
- O começo nunca abaixo de 30%, para o vídeo não parecer perdido de cara.
- Com a `campfire` padrão, o fogo apaga em cerca de 30% das sementes. Uma skin nova precisa de uma busca para afinar `dmg`, `rate` e `gain` até ficar perto de 1 em 3.

## Criar uma skin

Um arquivo `.py` com:

| Nome | O que é | Obrigatório |
|---|---|---|
| `SIM` | Os números da física que combinam com a skin | Não |
| `CFG` | Opções de desenho, que o vídeo troca com `SKIN_CFG` | Não |
| `HUD` | `name`, `clock` e `color` (cor da barra vazia e cheia) | Não |
| `prepare(sim, cfg)` | Monta o que é fixo, como o cenário, uma vez antes dos frames | Não |
| `step(sim, eventos)` | Partículas que precisam ir em ordem, a cada passo da física. Guarde em `sim.fx` e use só `sim.rv` | Não |
| `snap(sim)` | O que do `sim.fx` vai para o estado do frame | Não, mas sim se tiver `step` |
| `world(t, fr, sim, cfg)` | **A imagem 960x720 no tempo global t.** `fr` tem `hp`, `w`, `h`, `dead`, `watch`, `threats`, `allies` e o que o `snap` pôs | Sim |
| `sound(s, cfg, A, hp)` | Os sons do mundo a partir de `s.events`. `A` é o `synth`, `hp` é a vida amostra a amostra | Não |

A tensão é igual em toda skin e fica no `sound.py`: zumbido grave quando a vida cai abaixo de 55%, e coração abaixo de 25%. O placar e o vermelho piscando abaixo de 20% também são do modelo.

Comece copiando a `campfire`. Antes do roteiro, faça um protótipo de 10s, para afinar a física e o desenho juntos.

## Skin `campfire`

Uma fogueira numa clareira à noite. A chuva tem duas camadas: a fina, de fundo, é enfeite, e as gotas azuis maiores contam. O relâmpago mostra a multidão entre as árvores. Quando o fogo fica abaixo de 28%, olhos aparecem também nessa multidão.

- **Física:** dano 2,2, garoa até 8s, chuva até 24s, tempestade até 33s, nascer do sol em 36s.
- **Venceu:** o céu clareia e os vigias vão embora em 1,2s.
- **Perdeu:** sobe fumaça, a lenha fica em brasa por alguns segundos e os vigias vêm até o fogo.
- **`SKIN_CFG`:**
  - `lightning`: segundos dos relâmpagos.
  - `crowd`: número de figuras entre as árvores (22).
  - `stand`: figuras de pé que o vídeo põe, como `dict(at=38.6, dx=108, h=205, lean=-0.05, eyes=False)`, com `until` opcional.

## Roteiro

Além do que o `GUIA.md` pede, o roteiro apresentado traz:

- A skin, e se for nova, o que é o centro, o perigo, o aliado e o que espera no escuro.
- A semente e a linha dela na busca: menor vida, quando e o resultado.
- O fim: o que acontece depois do `until`, ou depois de perder.
- O título e o placar.
- O que o vídeo muda no `SIM` e no `SKIN_CFG`.

O que faz o formato funcionar:

- **A pergunta está no topo desde o primeiro frame.** Não tem abertura.
- **O horror chega devagar.** Nos primeiros segundos não há ninguém, e os vigias chegam um a um.
- **O pior momento vem perto do fim.** É ele que segura o espectador até o último segundo.
- **O fim tem uma coisa só**, pequena e errada, como no `glimpse`: uma figura que ficou, um par de olhos que não foi embora.

## Timeline

```python
from modelos import survive as MODELO
from modelos.survive import *

SKIN = 'campfire'
SEED = 118
SHOTS = [('night', 36.0, []), ('dawn', 4.0, [])]
TOTAL, START, END_CARD = timing(SHOTS)

TITLE = ('KEEP THE FIRE ALIVE', 'UNTIL SUNRISE')
TITLES = {'dawn': ('SUNRISE.', '')}
SIM = dict(threat=dict(dmg=2.4))                   # opcional
SKIN_CFG = dict(stand=[dict(at=38.6, dx=108, h=205)])
EVENTS = [(24.3, 0.35, 0.12)]                      # glitch, por exemplo no relâmpago
SUBLIM, SUBLIM_GRADE, GRADE = [], None, {}

def frame_fx(a, shot, rt):
    return a
```

- Os takes só dividem o tempo, para trocar o título. A simulação corre contínua por todos eles, no tempo global.
- Coisas só do vídeo, por cima do mundo, vão no `cards.py` com `paint_<take>(img, rt)`.

## Som

No `audio.py`:

```python
from synth import *
from modelos.survive import sound

sound.night()        # os sons da skin e a tensão
...                  # sons do fim deste vídeo
sound.master()       # compressão: o vídeo sai perto de -13 LUFS
finish()
```
