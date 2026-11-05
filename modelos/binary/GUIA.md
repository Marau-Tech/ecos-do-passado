# Modelo: binary

Dilema de duas opções: "Pick one", com duas opções ruins na tela, um trecho curto para cada e a tela final "PICK.". É o formato de horror que mais engajou no TikTok em outubro de 2026, porque a escolha leva as pessoas a comentar.

É o `choose_planet` encurtado: mesmas barras, narração, contador e glitch de corte, mas com 2 opções e cerca de 30s.

## Regras fixas

| Item | Padrão |
|---|---|
| Abertura | **"Pick one." mais a regra do jogo**, com as 2 opções na tela e os rótulos `A` e `B`. Ex.: "Pick one. You spend one night there." |
| Opções | **Duas, e as duas ruins.** O espectador escolhe a "menos pior", nunca a boa |
| Barra de cima | `OPTION A` em branco e o nome da opção em dourado |
| Contador | `T-HH:MM:SS` no OSD, de `STAKE_SECS` até zero em cada opção. O padrão é 24h; uma noite é `8 * 3600` |
| Duração | **De 20 a 35s.** O `timing()` recusa vídeo fora disso. Referência: 4s de intro, 2 trechos de 12s e 0,7s de tela final |
| Abertura de cada opção | Opção parada por 1,5s (`NAME_HOLD`) enquanto o narrador diz o nome. Depois vêm o zoom e a explicação |
| Tela final | Tela preta com "PICK." por 0,7s |
| Narração | Em todo vídeo, lendo as legendas e o nome de cada opção |
| Filtro | VHS, com glitch em todo corte |

## Roteiro

Além do que o `GUIA.md` pede, o roteiro apresentado traz:

- A abertura, com a regra do jogo em uma frase.
- As 2 opções, com o custo de cada uma. O contraste funciona melhor que dois monstros: uma de ameaça lenta e certa, outra de ameaça rápida e incerta ("You will be hungry" contra "Something knocks once").
- 3 takes por opção, do mais distante para o mais próximo, e a frase que vira a chave no último.
- O nome falado de cada opção.

O que faz o formato funcionar:

- **As duas opções precisam ser defensáveis.** Se uma é claramente pior, ninguém comenta. Teste: dá para imaginar metade dos comentários em cada uma?
- A segunda opção não pode ser "a mesma coisa, só que pior".
- A legenda do post faz a pergunta direta: "A or B? 👇".

## Timeline

Além do que o `GUIA.md` pede:

- Takes: `intro`, `a1`, `a2`, `a3`, `b1`, `b2`, `b3`. A primeira letra diz a opção.
- `OPTIONS = [('OPTION A', 'THE STAIRWELL', 'a1'), ('OPTION B', 'THE LAKE', 'b1')]`: título, subtítulo e primeiro take.
- A legenda do primeiro take de cada opção começa depois de `NAME_HOLD + 0.4`.
- `TOTAL, START, END_CARD = timing(SHOTS)`.
- `EVENTS = base_events(SHOTS, OPTIONS, START)`, mais os glitches do vídeo.
- `VOICE['names'] = {'a1': 'Option A. The stairwell.', 'b1': 'Option B. The lake.'}`, com `name_at` em 0.3.
- `GRADE`: chaves `intro`, `a` e `b`.
- `STAKE_SECS` só se o tempo não for 24h.
- `INTRO_LABELS` só se o enquadramento da intro não deixar as opções na esquerda e na direita.

## Cenas

Arquivos `intro.py`, `a.py` e `b.py`, um por trecho, como no `choose_planet`. A intro mostra as 2 opções lado a lado, a da esquerda é a A.
