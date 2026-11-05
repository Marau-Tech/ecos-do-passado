# Modelo: eas

Alerta de emergência na TV: a programação normal é cortada pelo Emergency Alert System, e as instruções começam genéricas e ficam específicas demais. É o núcleo do analog horror (Local 58) e o formato que mais usa a "autoridade distorcida": a voz oficial que deveria proteger é a que assusta.

## Regras fixas

| Item | Padrão |
|---|---|
| Abertura | Até 3s de programação normal (barras de cor, cartela da emissora ou um take renderizado), cortada por glitch |
| Alerta | Cabeçalho SAME (3 rajadas de dados) e tom de atenção de 853 e 960 Hz, **no máximo 4s de tom**. Depois vem a mensagem |
| Telas de alerta | Desenhadas, sem Blender: cabeçalho, texto e letreiro correndo. Estilos `red`, `blue`, `black` e `bars` |
| Barra de cima | `HEADLINE`, por exemplo `('EMERGENCY ALERT', 'CIVIL DANGER WARNING')`. `TITLES[take]` muda num take |
| Barra de baixo | O que a voz fala, digitado |
| OSD | Prefixo da emissora no canto esquerdo (`STATION`, sem luz de REC) e o relógio no direito |
| Narração | Voz robótica de alerta: `am_michael` ou `am_onyx`, `en-us`, velocidade 0,9, `fx: 'radio'` |
| Duração | **De 25 a 75s.** O `timing()` recusa vídeo fora disso |
| Glitch | No corte para o alerta, quando a mensagem vira e na tela final |
| Filtro | `broadcast`: TV de antena, com fantasma, chuvisco fino e barra de zumbido. No glitch a imagem rasga e rola |
| Tela final | "END OF MESSAGE" por 1,5s, com o tom de atenção. O vídeo pode trocar o `END_TEXT` |

## Roteiro

Além do que o `GUIA.md` pede, o roteiro apresentado traz:

- A emissora (`STATION`), a hora (`CLOCK`) e a programação que é cortada.
- O tipo de alerta, real e reconhecível: `CIVIL DANGER WARNING`, `SHELTER IN PLACE`, `LOCAL AREA EMERGENCY`, `EVACUATION IMMEDIATE`.
- Cada tela: estilo, cabeçalho, texto e letreiro.
- A fala de cada tela, que é a legenda.
- Os cortes para takes renderizados, se houver: a câmera da emissora mostrando o céu, a rua ou a coisa.

O que faz o formato funcionar:

- **O horror está na instrução específica demais.** "Stay indoors" é normal. "Do not answer the door if they already know your name" assusta. A regra é que cada instrução seja algo que uma autoridade diria, só que precisa demais.
- **Escalar em 3 passos:** instrução genérica, instrução estranha e instrução impossível ou que se contradiz.
- **Tom burocrático.** Nada de "monstro" ou "criatura". Use "individuals", "the phenomenon", "the event".
- Uma linha do letreiro pode contradizer a voz, para quem lê.

## Timeline

Além do que o `GUIA.md` pede:

- `STATION = 'KXLT 58'`, `CLOCK = 23 * 3600 + 42 * 60`, `HEADLINE = ('EMERGENCY ALERT', 'CIVIL DANGER WARNING')`.
- `ALERTS`: para cada take desenhado, um dicionário que sobrescreve o `ALERT_STYLE`:

```python
ALERTS = {
    'tone': {'lines': ['CIVIL DANGER WARNING'], 'blink': True},
    'm1': {'lines': ['THE FOLLOWING MESSAGE IS FOR', 'BRIDGEFORD COUNTY'], 'crawl': 'REMAIN INDOORS. ...'},
    'm3': {'style': 'blue', 'head': 'INSTRUCTIONS', 'lines': ['COVER ALL WINDOWS FACING EAST'], 'type': True},
    'pgm': {'style': 'bars', 'lines': ['PLEASE STAND BY']},
}
```

- `lines` são parágrafos, quebrados sozinhos. `type: True` digita o texto; `blink: True` pisca o cabeçalho.
- Takes que não estão em `ALERTS` são renderizados (`scene.py`) ou desenhados pelo `cards.py`, se estiverem em `DRAWN`.
- `TOTAL, START, END_CARD = timing(SHOTS)`.
- `VOICE = {'voice': 'am_michael', 'lang': 'en-us', 'speed': 0.9, 'fx': 'radio'}`.
- `GRADE`: chave `scene` para os takes renderizados. Os desenhados não passam pela cor.

## Áudio

No `audio.py`:

- `same_header(t0)` toca as 3 rajadas e devolve quando acabam.
- `put(attention(4.0), t)` toca o tom de atenção.
- `eom(t0)` toca o fim de mensagem, logo antes da tela final.
- A narração abaixa o resto sozinha.

## Legenda do post

Diferente do `choose_planet`, aqui a legenda **cita a premissa do alerta**, porque é ela que faz a pessoa parar: "At 3:12 AM, KXLT 58 cut in with a warning about the two moons." Uma legenda genérica ("an emergency alert") não diz nada sobre o vídeo.

- **Pode:** a emissora, a hora e o assunto do alerta.
- **Não pode:** a virada, ou seja, a instrução impossível e o que o fim revela.
- O vídeo imita um alerta real: manter "Fictional broadcast." e `#analoghorror`, e deixar de fora `#emergencyalert` e `#eas`.
