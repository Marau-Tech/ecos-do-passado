# Modelo: probe_feed

Transmissão de uma sonda espacial: as imagens chegam linha por linha no monitor do controle de missão, com telemetria no OSD. As primeiras são normais e a última mostra algo que não deveria estar lá. Termina em "LOSS OF SIGNAL".

É found footage institucional, o 2º formato de horror mais visto no TikTok em outubro de 2026, e combina com o tema de planetas do canal.

## Regras fixas

| Item | Padrão |
|---|---|
| Abertura | Take `head` desenhado: terminal da estação digitando `HEADER` (estação, sonda, alvo, tempo-luz, "RECEIVING IMAGE SEQUENCE") |
| Imagens | **De 4 a 7**, uma por take. Cada uma é uma imagem parada que chega de cima para baixo em `REVEAL_SECS` (3,5s) e fica parada até o fim do take |
| Barra de cima | `IMAGE 03` em branco e o alvo em dourado (`TARGET`, ou `SUBTITLES[take]`) |
| Barra de baixo | Log do operador, digitado, sem narração: "IMAGE 03 RECEIVED. CHECKSUM OK." |
| OSD | `RX` com a luz, `IMG 03/06` no canto direito e sinal e taxa de erro (`SIGNAL`) no rodapé, piorando até o fim |
| Narração | **Nenhuma.** O silêncio com os dados chegando assusta mais. Pode ter uma fala de rádio do controle (`VOICE` com `fx: 'radio'`), se o roteiro pedir |
| Duração | **De 30 a 60s.** O `timing()` recusa vídeo fora disso |
| Glitch | **Só perda de pacote** num acontecimento: linhas pretas, repetidas ou de lixo. Sem glitch de corte |
| Filtro | `probe`: 6 bits por canal, erros de bit soltos e fósforo de CRT |
| Tela final | "LOSS OF SIGNAL" por 2s, só com chiado (`END_TONE = False`) |

## Roteiro

Além do que o `GUIA.md` pede, o roteiro apresentado traz:

- Estação, sonda, alvo e as linhas do `HEADER`.
- Cada imagem: o que mostra, a distância (de órbita alta até a superfície) e a cor (filtro de banda, falsa cor ou preto e branco).
- O log de cada imagem, curto e técnico. A virada vem no tom do log: de "CHECKSUM OK" para "IMAGE 06 WAS NOT REQUESTED".
- Onde o sinal falha.

O que faz o formato funcionar:

- **Lentidão.** A imagem chegando linha por linha prende a pessoa, porque ela quer ver o resto. A revelação está na última faixa de linhas que chega.
- **A sonda é a vítima.** Ela não deveria ser notada, e a última imagem mostra que foi. Exemplos: algo olhando para a câmera, a própria sonda vista de fora, uma imagem tirada depois do horário de desligamento.
- **Linguagem fria.** Nenhum adjetivo no log. O horror fica entre o que o operador escreve e o que a imagem mostra.

## Timeline

Além do que o `GUIA.md` pede:

- Takes: `head` e depois `i1`, `i2`... Todo take que começa com `i` é imagem. Takes que não são imagem, como uma tela "NO DATA", vão em `DRAWN` e são desenhados no `cards.py`.
- `PROBE = 'VESPER-2'`, `TARGET = 'TARGET: HD 40307 g'`.
- `HEADER`: linhas do terminal da abertura. Calcule a duração do `head` em 40 letras por segundo, mais 0,25s por linha e 1s de folga.
- `SIGNAL = (-138.0, -151.0)`: sinal em dBm no início e no fim.
- `REVEAL = {'i6': (0.3, 6.0)}` muda o tempo de chegada de um take. A última imagem costuma chegar mais devagar.
- `TOTAL, START, END_CARD = timing(SHOTS)`.
- `EVENTS` só com as perdas de pacote.
- `GRADE`: chave `img` para todas, ou uma chave por take para mudar a cor de uma.

## Cenas

Todos os takes de imagem ficam em `scene.py`, com `HOLD_STATES = True` e o `update` devolvendo um estado fixo. Assim cada take renderiza **um frame só** e o vídeo inteiro sai em poucos minutos.

- Enquadramento de sonda: câmera de lente longa, de cima ou rasante, sem movimento.
- A imagem que vem depois do take parado é desenhada pelo post, então não é preciso animar a revelação no Blender.
- Pode reaproveitar planetas, terreno e névoa dos vídeos do `choose_planet`, copiando o código para o vídeo novo.

## Áudio

No `audio.py`, `downlink(secs)` toca os dados chegando. Coloque um em cada revelação, com a duração de `REVEAL`. Entre as imagens fica só o chiado da portadora.

## Legenda do post

A legenda **cita a premissa**: a sonda, o alvo e quantas imagens chegaram. "VESPER-2 reached Planet Nine and sent back 6 images."

- **Pode:** a sonda, o alvo e apontar para uma imagem sem dizer o que ela tem ("Pause on image 05. What's wrong with it?"). Isso puxa comentário e faz a pessoa assistir de novo.
- **Não pode:** o que a última imagem mostra, nem o log da virada.
- O vídeo imita imagem real de missão: manter "Fictional transmission." e `#analoghorror`, e deixar de fora `#nasa`.
