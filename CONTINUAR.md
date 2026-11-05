# Continuação da sessão

Anotação de onde a sessão de 2026-11-05 parou, para retomar em outro PC. Para continuar, peça ao Claude: "lê o `CONTINUAR.md` e segue de onde parou". Apague este arquivo quando tudo abaixo estiver feito.

## O que foi feito

### Pesquisa e modelos novos

Pesquisa de tendências de analog horror (novembro de 2026), que virou 6 modelos novos, cada um com o seu `modelos/<modelo>/GUIA.md`:

| Modelo | Formato |
|---|---|
| `binary` | Dilema de 2 opções ruins, "Pick one", de 20 a 35s |
| `probe_feed` | Imagens de sonda chegando linha a linha, sem narrador |
| `eas` | Alerta de emergência na TV, com instruções específicas demais |
| `weather` | Previsão do tempo da TV local que deixa de fazer sentido |
| `rules` | Filme de segurança dos anos 80 com regras numeradas |
| `glimpse` | Vislumbre de 6 a 15s, sem texto, em loop |

### Engine

- **Takes desenhados em 2D:** saem direto do post, sem Blender (`modelos/base.py`, `engine/gfx.py`).
- **Filtros novos:** `broadcast`, `webcam` e `probe`, em `engine/looks.py`.
- **Sons novos:** tons e rajadas do EAS, telemetria e muzak, em `engine/synth.py`.
- **Voz:** efeitos `radio` e `broadcast`, em `engine/voice.py`.
- **Tela final sem tom de alerta** (`END_TONE = False`) em `probe_feed`, `weather`, `rules` e `glimpse`.
- **Estradas no mapa do `weather`** (`roads`).
- **Nome das pastas:** agora é `<número>-<modelo>-<nome>`, e as pastas antigas foram renomeadas. A regra está no `GUIA.md`.

### Vídeos

| Vídeo | Estado |
|---|---|
| `06-eas-lower-moon` | **Pronto.** Final renderizado e legenda em `out/.../caption.txt` |
| `07-probe-feed-planet-nine` | **Pronto.** Final renderizado e legenda em `out/.../caption.txt` |
| `08-binary-quiet-or-kind` | Preview feito. **Falta a aprovação, o final e a legenda** |
| `09-weather-new-star` | Preview feito. **Falta a aprovação, o final e a legenda** |
| `10-rules-green-sky` | Preview feito. **Falta a aprovação, o final e a legenda** |
| `11-glimpse-doorway` | Preview feito. **Falta a aprovação, o final e a legenda** |

Os mp4 não vão para o git. Os finais de 06 e 07 ficaram no PC do trabalho, em `out/<video>/<video>.mp4`, e os previews de 08 a 11 também.

## O que falta fazer

1. **Preview de 08 a 11 neste PC:** os previews ficaram no PC do trabalho. Rode `./video <video> preview` para assistir antes do final, ou pule direto para o final se já aprovou.
2. **Aprovar ou corrigir cada um.** Pontos para conferir:
   - **08:** se as silhuetas da mesa e das janelas assustam ou parecem bonecos.
   - **10:** a regra 6 aparece num único frame, aos 47,7s. Só dá para ver no final, a 30 fps.
   - **11:** se o rosto na fresta está visível demais ou de menos.
3. **Final dos 4:** `./video <video> final`.
   - O 08 renderiza frame a frame, porque a câmera se move: uns 15 a 20 min na CPU, menos na GPU.
   - O 09, o 10 e o 11 têm câmera parada, então saem em poucos minutos cada.
4. **Legenda do post** (`out/<video>/caption.txt`) de 08 a 11, seguindo o `GUIA.md` e o guia de cada modelo:
   - pesquisar as tendências no dia;
   - a legenda pode citar a premissa, mas nunca a virada;
   - o `glimpse` sai só com as hashtags.
5. **Commit** das legendas.
6. **Publicar de 06 a 11 perto um do outro** e comparar o resultado por formato. A ideia é descobrir quais formatos funcionam melhor, para fazer mais vídeos deles.

## Roteiros aprovados de 08 a 11

O roteiro de cada vídeo está no próprio `videos/<video>/timeline.py` (falas e tempos) e no `scene.py` (o que cada take mostra). Resumo:

- **08 binary:** A, o planeta quieto (poeira, pegadas que você não ouve, uma respiração que não é sua no visor), contra B, o planeta simpático (casas iguais, gente acenando, uma mesa posta com um lugar vazio). Tela final "PICK.".
- **09 weather:** a WKBR 58 às 11:04 PM. Um sistema anda contra o vento até a cidade, a câmera do céu mostra uma estrela nova e a previsão de sexta não existe. Termina com "Do not look up until Thursday.".
- **10 rules:** "Safety Film No. 12: When the Sky Turns Green", com 5 regras. A janela a mais aparece no telhado, a regra 5 mostra a sala sem teto e a regra 6 ("LET THEM IN") aparece em um frame.
- **11 glimpse:** quarto pela webcam de 2004, com um rosto pálido na fresta da porta que some depois do glitch e volta no loop.
