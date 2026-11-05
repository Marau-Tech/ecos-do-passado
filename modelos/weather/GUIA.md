# Modelo: weather

Boletim do tempo da TV local, de madrugada. O apresentador só aparece em voz, o mapa e a previsão são da emissora, e a previsão vai deixando de fazer sentido: "Tonight: clear skies. The sky will be watching."

É um clássico do analog horror (Local 58) e reaproveita céu, névoa, terreno e planetas da engine.

## Regras fixas

| Item | Padrão |
|---|---|
| Abertura | Take `ident` desenhado: vinheta com a emissora (`STATION`) e o quadro (`SHOW`), por 1,5 a 2s |
| Mapa | Takes renderizados de um mapa ou satélite 3D, com cidades, temperaturas e radar desenhados por cima (`MAPS`) |
| Previsão | Takes desenhados com um dia por coluna (`FORECASTS`). O último dia é o errado: ícone `eye` ou `none`, temperatura `--` |
| Céu | Ao menos um take renderizado de câmera de céu ou rua ao vivo |
| Barra de cima | `TITLE`, por exemplo `('WEATHER WATCH', 'BRIDGEFORD COUNTY')`. `TITLES[take]` muda num take |
| Barra de baixo | O que o apresentador fala, digitado |
| OSD | Prefixo da emissora no canto esquerdo (`STATION`, sem luz de REC) e hora e temperatura no direito (`TEMP`) |
| Narração | Apresentador: `am_adam` ou `af_heart`, `en-us`, velocidade 1,0, `fx: 'broadcast'`. Tom simpático até o fim |
| Trilha | `muzak()` de previsão do tempo por baixo, até a virada |
| Duração | **De 35 a 75s.** O `timing()` recusa vídeo fora disso |
| Glitch | Só na virada e na tela final |
| Filtro | `broadcast` |
| Tela final | Preta e muda por 1,2s (`END_TEXT` vazio). O vídeo pode pôr um texto, como "STAY INSIDE." |

## Roteiro

Além do que o `GUIA.md` pede, o roteiro apresentado traz:

- Emissora, quadro, cidade, hora e temperatura.
- Cada take: mapa, previsão ou céu, e o que aparece desenhado por cima.
- A fala de cada take, que é a legenda.
- Onde a música para.

O que faz o formato funcionar:

- **Simpatia que não quebra.** O apresentador fala do evento com o mesmo tom de "leve um casaco". O contraste é o susto.
- **Dado meteorológico real, aplicado ao impossível.** "A high-pressure system is moving in from the east. It is about six feet tall." Use termos de previsão: frente fria, pressão, visibilidade, umidade, índice UV.
- **Escalar:** previsão normal, um detalhe errado (uma cidade que não existe no mapa, um eco de radar que anda contra o vento) e a instrução final ("Do not look up until Thursday.").
- A previsão é o melhor lugar para quem pausa: um dia a mais na tabela, uma temperatura impossível.

## Timeline

Além do que o `GUIA.md` pede:

- `STATION = 'WKBR 58'`, `SHOW = 'WEATHER WATCH'`, `CLOCK = 23 * 3600 + 4 * 60`, `TEMP = '54°F'`, `TITLE = ('WEATHER WATCH', 'BRIDGEFORD COUNTY')`.
- `FORECASTS = {'fc': [('MON', 'sun', '61°', '48°'), ..., ('FRI', 'eye', '--', '--')]}`. Ícones: `sun`, `moon`, `cloud`, `rain`, `storm`, `snow`, `fog`, `eye`, `none`. `FORECAST_HEAD` muda o cabeçalho.
- `MAPS = {'map1': {'cities': [((300, 280), 'BRIDGEFORD', '54°')], 'radar': [(520, 330, 90, 0.8)], 'sweep': True, 'banner': 'SEVERE WEATHER WARNING'}}`. As posições são em pixels do quadro de 960x720. Confira no preview se as cidades caem no lugar.
- `TOTAL, START, END_CARD = timing(SHOTS)`.
- `VOICE = {'voice': 'am_adam', 'lang': 'en-us', 'speed': 1.0, 'fx': 'broadcast'}`.
- `GRADE`: chave `scene`, ou uma por take.

## Cenas

Takes renderizados em `scene.py`. O mapa é melhor como terreno visto de cima, com câmera fixa ou deslizando devagar: `HOLD_STATES = True` com a câmera parada sai com um frame por take. Em um mapa que se move, as cidades desenhadas por cima não acompanham, então cidades só em mapa parado.

## Áudio

No `audio.py`, `add(muzak(START['map1'], virada), 0.05)` toca a música de previsão. Corte a música na virada, com o mesmo `cut` dos outros vídeos.
