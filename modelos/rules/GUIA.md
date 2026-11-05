# Modelo: rules

Filme educativo de segurança dos anos 80, gravado em fita: uma instituição ensina regras numeradas para uma situação. As regras ficam estranhas, e **a última contradiz a primeira**. "Rules horror" prende até o fim, porque a pessoa quer saber a última regra, e puxa "parte 2".

## Regras fixas

| Item | Padrão |
|---|---|
| Abertura | Take `slate` desenhado: contagem 3, 2, 1 do filme (0,8s por número) e a cartela com quem apresenta, número e título do filme. Cerca de 4,5s |
| Regras | **De 4 a 7.** Cada uma tem uma cartela desenhada (`r1`, `r2`...) e de 1 a 2 takes de ilustração (`r1a`, `r1b`) |
| Última regra | **Contradiz a primeira**, ou revela por que a primeira existe |
| Barra de cima | `RULE 3 OF 6` em branco e o nome curto da regra em dourado |
| Barra de baixo | O que o narrador fala, digitado |
| OSD | `PLAY` com a luz e o tempo da fita no rodapé |
| Narração | Voz calma de filme institucional: `bm_lewis` ou `bm_george`, `en-gb`, velocidade 0,92. Tom de quem ensina criança |
| Duração | **De 40 a 80s.** O `timing()` recusa vídeo fora disso |
| Glitch | Leve em cada cartela de regra e forte na virada |
| Filtro | VHS |
| Tela final | "BE SAFE." por 1,2s, sem tom (`END_TONE = False`). O vídeo pode trocar o `END_TEXT` |

## Roteiro

Além do que o `GUIA.md` pede, o roteiro apresentado traz:

- A instituição, o número e o título do filme (`FILM`).
- Cada regra: o nome curto (vai na barra e na cartela), a fala inteira e o que a ilustração mostra.
- Onde está a virada.

O que faz o formato funcionar:

- **Regras 1 e 2 plausíveis**, quase de verdade. A 3 tem um detalhe errado. Da 4 em diante, a lógica é de outro mundo, dita com a mesma calma.
- **A regra mais estranha é a mais curta.** "Rule 5. Do not count the windows."
- **A última volta para a primeira.** Se a regra 1 era "Stay inside after dark", a última é "If you are reading this inside, you are already outside."
- Detalhe para quem pausa: o número de regras na barra (`OF 6`) pode não bater com o total que aparece.

## Timeline

Além do que o `GUIA.md` pede:

- Takes: `slate`, depois `r1`, `r1a`, `r1b`, `r2`, `r2a`... `r<n>` é a cartela, desenhada pelo modelo. `r<n><letra>` é a ilustração, renderizada no `scene.py` ou desenhada no `cards.py` (com o take em `DRAWN`).
- `FILM = ('THE DEPARTMENT OF CIVIL READINESS', 'SAFETY FILM No. 12', 'WHEN THE SKY TURNS GREEN')`.
- `RULES = [('STAY INSIDE AFTER DARK', 'moon'), ('KEEP A RADIO NEARBY',), ...]`: nome curto e ícone opcional da cartela (os mesmos do `weather`).
- A cartela `r<n>` dura de 2 a 3s e a fala dela é "Rule three." ou a regra inteira. A ilustração leva a explicação.
- O slate tem a legenda grande na barra de cima, se tiver legenda.
- `TOTAL, START, END_CARD = timing(SHOTS)`.
- `EVENTS`: um glitch leve em cada `r<n>` e um forte na virada.
- `VOICE = {'voice': 'bm_lewis', 'lang': 'en-gb', 'speed': 0.92}`.
- `GRADE`: chave `scene`, ou `r3` para mudar a cor de uma regra inteira.

## Cenas

As ilustrações ficam em `scene.py`. Filme educativo tem câmera parada ou com movimento lento, então `HOLD_STATES = True` funciona na maioria. Cenários simples e bem iluminados: o susto vem do texto e de um detalhe pequeno na imagem.

## Áudio

No `audio.py`, um `beep()` em cada número da contagem (`START['slate'] + i * SLATE_COUNT`, para i de 0 a 2). Por baixo das regras, um acorde calmo de filme institucional, que desafina na virada.
