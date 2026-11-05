# Modelo: glimpse

Vislumbre sem contexto: de 6 a 15s de uma imagem perturbadora, sem legenda, sem narração e sem explicação, que termina onde começa para rodar em loop. Dois dos cinco vídeos de horror mais vistos no TikTok em outubro de 2026 eram assim, e um teve alcance de 2.018 vezes os seguidores, porque as pessoas assistem de novo para entender.

É o modelo mais barato: um ou dois takes, quase sempre com câmera parada.

## Regras fixas

| Item | Padrão |
|---|---|
| Texto | **Nenhum.** Sem título, sem legenda e sem tela final. As barras ficam pretas |
| Narração | **Nenhuma** |
| Duração | **De 6 a 15s.** O `timing()` recusa vídeo fora disso ou com legenda |
| Loop | **O último frame emenda no primeiro.** O mesmo enquadramento e o mesmo estado da cena no começo e no fim. O áudio emenda sem estalo sozinho |
| Câmera | Parada, ou com um movimento que volta ao ponto de partida |
| OSD | Só o carimbo de data da câmera no rodapé, se houver `STAMP` |
| Glitch | No máximo um, no acontecimento |
| Filtro | `webcam`: webcam dos anos 2000 a 10 fps, com blocos de compressão e cor em degraus. O vídeo pode trocar com `LOOK = 'cctv'` ou `'vhs'` no `timeline.py` |
| Legenda do post | **Vazia, ou só as hashtags.** Sem pergunta, sem frase, sem aviso de spoiler |

## Roteiro

Além do que o `GUIA.md` pede, o roteiro apresentado traz:

- O lugar, o enquadramento e o que acontece, com o segundo em que acontece.
- Como o fim volta ao começo.
- Os sons.

O que faz o formato funcionar:

- **Uma coisa só, pequena e errada.** Uma pessoa parada no fundo que não estava lá no começo do loop. Uma porta que está aberta na primeira volta e fechada na segunda. Um rosto que só aparece em um frame.
- **O loop esconde o início.** A pessoa só percebe que o vídeo recomeçou depois de algumas voltas, e passa a procurar o que mudou.
- **Nada explica.** Se o espectador entende na primeira volta, o formato perdeu.
- Lugares liminares funcionam bem: corredor, estacionamento, piscina vazia, quarto à noite pela webcam.

## Timeline

Além do que o `GUIA.md` pede:

- Takes sem legenda: `('a', 12.0, [])`.
- `TOTAL, START, END_CARD = timing(SHOTS)`.
- `STAMP = '2004-03-17'` e `CLOCK = 3 * 3600 + 14 * 60` para o carimbo; sem `STAMP`, o OSD fica vazio.
- `EVENTS` com no máximo um glitch.
- `LOOK` só se o vídeo trocar o filtro.
- `GRADE`: chave `cam`.
- Sem `VOICE`.

## Cenas

Tudo em `scene.py`, com `HOLD_STATES = True` quando a câmera é parada. Para o loop, o `update(t, u)` precisa devolver o mesmo estado em `u = 0` e `u = 1`.
