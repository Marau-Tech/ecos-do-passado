# Modelo: choose_planet

Vídeo "Choose one": 4 planetas na tela, um trecho para cada um e uma tela final que pede a escolha. Vídeos deste modelo: `01` a `04`. O vídeo 1 é anterior à narração.

## Regras fixas

| Item | Padrão |
|---|---|
| Abertura | **Sempre "Choose one. You stay for 24 hours."** na intro, com os 4 planetas na tela e a regra do jogo completa |
| Barra de cima | `PLANET 1` em branco e o nome do planeta em dourado |
| Contador | `T-24:00:00` no OSD, zerando a cada planeta |
| Duração | Cerca de 74s: 5s de intro e 17,25s por planeta |
| Abertura de cada planeta | Planeta girando com a câmera parada por 2,25s enquanto o narrador diz o nome. Depois vêm o zoom e a explicação |
| Tela final | Tela preta com "CHOOSE." por 0,7s |
| Narração | Em todo vídeo, lendo as legendas e o nome de cada planeta |
| Filtro | VHS, com glitch em todo corte |

## Roteiro

Além do que o `GUIA.md` pede, o roteiro apresentado traz:

- A abertura.
- Os 4 planetas, com o papel de cada um no tom do vídeo (um quase bonito, um de tensão lenta, um de susto seco, um cósmico) e sem repetir planeta de vídeo anterior.
- O fecho de cada trecho, a cor de cada trecho e o nome falado de cada planeta.

O formato que funcionou:

- Abrir com a pergunta e todas as opções na tela.
- Mostrar cada opção em 4 takes de 3,5 a 4s, do mais distante para o mais próximo.
- Fechar cada trecho com uma frase que vira a chave ("No visitor ever wanted to go back.").
- Variar o tom entre as opções, porque o contraste assusta mais que quatro monstros seguidos.
- Terminar com uma tela preta de uma palavra ("CHOOSE.").

## Timeline

Além do que o `GUIA.md` pede:

- `PLANETS`: título, subtítulo e primeiro take de cada trecho.
- `EVENTS = base_events(SHOTS, PLANETS, START)`, mais os glitches do vídeo.
- `TOTAL, START, END_CARD = timing(SHOTS, END_SECS)`.
- `VOICE['names']`: take e texto falado com o nome de cada planeta. `VOICE['name_at']`: quando o nome começa no take.
- `NAME_HOLD`: somar nas durações dos takes `p1a` a `p4a` e começar a legenda deles em `NAME_HOLD + 0.5`.

`NAME_HOLD`, `SECTION`, `END_SECS`, `END_TEXT`, `INTRO_LABELS`, `FPS_SRC` e `FPS_OUT` já vêm do modelo. Um vídeo só os define se fugir do padrão.

## Cenas

Os takes se chamam `intro` e `p1a` a `p4d`, e cada trecho fica em `p1.py` a `p4.py`. A `intro` fica em `intro.py`, e os planetas em `planets.py`.

Nos takes de planeta, a primeira linha do `update` segura o zoom até o nome terminar:

```python
def update(t, u):
    u = zoom_after(t, NAME_HOLD, SHOTS['p1a'])
```
