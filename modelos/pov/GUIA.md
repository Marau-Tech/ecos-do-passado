# Modelo: pov

Relato em primeira pessoa do canal Ecos do Passado: o espectador está num lugar e numa data reais da história, como se a fita tivesse sido gravada por quem estava lá. Câmera na altura dos olhos, andando, com o balanço de quem segura a câmera.

## Regras fixas

| Item | Padrão |
|---|---|
| Idioma | **Português do Brasil** em legendas, títulos, OSD, tela final e legenda do post. É a exceção à regra "Inglês em tudo" do `GUIA.md`, por decisão do autor |
| Abertura | Lugar e data falados e na barra de cima (`PLACE` em branco, `DATE` em dourado), só no primeiro take |
| Contador | `STAMP HH:MM` no OSD: data curta e a hora do relato, que anda com o tempo. Cada take tem sua hora em `CLOCK` |
| Câmera | POV na altura dos olhos (cerca de 1,65 m), andando ou parada, com balanço de mão. Nada de câmera aérea ou de fora do personagem |
| Duração | **De 30 a 60s.** O `timing()` recusa vídeo fora disso. Referência: 5 a 6 takes de 5 a 8s e 1,5s de tela final |
| Tela final | Tela preta com "ECOS DO PASSADO" por 1,5s, sem tom |
| Narração | Em todo vídeo, lendo as legendas: `pm_alex`, `pt-br`, efeito `tape` |
| Filtro | VHS, com glitch leve em todo corte |

## Roteiro

Além do que o `GUIA.md` pede, o roteiro apresentado traz:

- O lugar e a data exatos da abertura.
- Por take: o que o personagem faz (anda, para, desce, sai) e a hora do relato.
- A frase que fecha o vídeo, ligando o momento ao que veio depois, sem moral.

Precisão histórica:

- Nada de datas exatas, nomes de unidades, citações ou números que não estejam confirmados. Na dúvida, descrição geral.
- Falas de outros personagens são dramatização. O personagem não tem nome nem patente se o roteiro não pedir.
- Sem gore e sem glorificar a guerra: frio, medo, cansaço e silêncio contam mais.

## Timeline

Além do que o `GUIA.md` pede:

- `PLACE`, `DATE`: título e subtítulo da abertura, em maiúsculas (`'STALINGRADO'`, `'NOVEMBRO DE 1942'`).
- `STAMP`: data curta do OSD (`'NOV 1942'`) e `CLOCK`: segundos do dia em que cada take começa.
- `SCENE_OF`: arquivo de cada take (`{'t1': 'rua', 't3': 'porao'}`).
- `TOTAL, START, END_CARD = timing(SHOTS)`.
- `EVENTS = base_events(SHOTS, START)`, mais os glitches do vídeo.
- `VOICE = {'voice': 'pm_alex', 'lang': 'pt-br', 'speed': 1.0}`.

## Cenas

Um arquivo por lugar (`rua.py`, `porao.py`), com `build_<take>()` e `SHOTS`. A câmera anda com `walk()` do vídeo: passo, balanço e um pouco de `shake()`.
