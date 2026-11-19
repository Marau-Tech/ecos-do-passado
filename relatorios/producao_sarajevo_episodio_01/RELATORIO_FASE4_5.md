# Relatório técnico — Fase 4.5 (Sarajevo, take t4)

**Status:** candidato técnico. A aprovação estética pertence ao usuário.
**Data:** 2026-11-18.

## 1. Auditoria e preservação

Antes de qualquer implementação:

- `pwd`: `ecos-do-passado-atualizado`
- `HEAD`: `31ab246d0540c7f5b5eb1612754c76d4db789228` (detached HEAD; branch vazio)
- `git status --porcelain`: `5 ??` (topo), `153 D`, `8 M` — todos pré-existentes
- Worktrees: `ecos-do-passado` (`episodio-01-sarajevo`, `00a216f`) e o diretório atual (`31ab246`)
- Blender ativos: 0; RAM disponível: ~1,7 GB; GPU: 1448/4096 MB
- Backup `ecos-do-passado-pre-limpeza-2026-11-18` (fora do repositório): preservado

Todo o trabalho foi criado em `experimentos/sarajevo_fase4_5/`. Nenhum arquivo
das Fases 3.1, 4.1, 4.2, 4.3, 4.4, `engine/`, `modelos/` ou dos takes originais
foi alterado. A Skill `/criar-video` não foi alterada como parte da
implementação da Fase 4.5. Para este pacote de publicação, recebeu apenas
normalização de caminhos locais. Não houve commit, push, publicação nem
operação destrutiva no Git. A auditoria final confirmou HEAD, worktrees e o
conjunto de arquivos modificados idênticos aos do início.

## 2. Diagnóstico da F4.4

| Defeito reportado | Causa estrutural identificada |
| --- | --- |
| Nuvem lisa, clara e uniforme | Dois domos com densidade modulada por ruído escalar suave e contraste baixo |
| Silhueta geométrica artificial | Envelope radial mantinha densidade até perto da fronteira da malha |
| Bola de fogo grande, sem núcleo | Núcleo emissivo compartilhava domínio com o volume e crescia até ~2,6 m |
| Pouca evolução entre 110/140/180 | Mesmos corpos com ganho de luz e deslocamento mínimos |
| Artefato preto no topo em 110 | Combinação de domínio de volume emissivo, material de solo muito escuro e resíduos de transform em versões anteriores de `hide()` |
| Destroços sem trajetória convincente | Repouso instantâneo e ausência de poeira de impacto individual |

## 3. Arquitetura da F4.5

Cinco sistemas independentes, ligados por `f45_flash`, `f45_fire`,
`f45_smoke`, `f45_debris`, `f45_dust` no JSON:

- **A — Flash:** luz `pt` com ataque de 0,012 s, `tau=0,13 s` e cauda de 11 %
  com `tau=2,4 s`; núcleo emissivo minúsculo que desaparece antes de 0,4 s.
  A exposição global não é alterada.
- **B — Fogo:** núcleo compacto, 22 línguas com atrasos/fases/vidas/alturas
  distintas e 10 faíscas balísticas. Ganho `exp(-age/0,42)`; fogo termina
  antes da fumaça dominar.
- **C — Fumaça:** três domínios (`core`, `body`, `plume`) de `Principled
  Volume`. Densidade = envelope radial (zera antes da fronteira) × ruído em
  duas escalas × Voronoi × alfa do objeto. Interior escuro e denso, bordas
  difusas; deriva temporal nos três eixos e motion ascendente por convecção.
- **D — Destroços:** 48 fragmentos de seis geometrias, impulso radial e
  ascendente, gravidade 9,8 m/s², rotação, tempo de voo calculado, repouso em
  altura dependente do tamanho e poeira de impacto no ponto de queda.
- **E — Poeira:** 24 manchas irregulares rente ao solo, expansão progressiva,
  dissipação em 7 s e queimadura de pavimento que nunca é preto puro.

`f45_explosion=true` curto-circuita `f41_explosion.make_explosion` e
`f42_explosion.refine`. `with_blast=False` (t5) suprime apenas flash e luz de
evento; fumaça, destroços e poeira permanecem no mesmo estado de `age`.

## 4. Evolução temporal

| Frame | Idade (s) | Estado |
| --- | --- | --- |
| 82 | −0,083 | pré-detonação, sem energia |
| 84 | 0,083 | clarão, início do núcleo de fogo |
| 90 | 2,70 | fogo extinto, fumaça em formação, destroços em queda |
| 110 | 7,93 | fumaça expandida/turbulenta, destroços em repouso |
| 140 | 11,27 | fogo ausente, pluma volumosa e em dissipação |
| 180 | 15,27 | fumaça residual ténue, sem bola de fogo estática |

Todas as transformações, alfas, energias e valores de nó de shader são
atribuições absolutas de `age = t + age0 - t0`; `hide()` restaura transforms
canônicos. Não há `+=`, cache de simulação nem estado global mutável.

## 5. Investigação do artefato preto

Foram eliminadas as causas estruturais: `hide()` redefine escala/rotação/
posição; o flash é minúsculo e curto; nenhum material de fragmento ou poeira é
preto puro; o envelope de densidade zera antes da fronteira do volume.

A análise de pixels (somente leitura) procura componentes conectados de
luminância < 14 cercados por vizinhança média > 38. No frame 110:

- F4.4: maior componente 1517 px, bbox `(471,812)–(642,872)`;
- F4.5: maior componente 605 px, bbox `(534,860)–(637,872)`, faixa horizontal
  provável de silhueta de veículo/pavimento.

O componente dominante da F4.4 não reaparece na F4.5. Essa é uma evidência
numérica, não uma confirmação visual; a inspeção final permanece com o usuário.

## 6. Desempenho e segurança

Padrão inalterado: 864×1536, 24 FPS, Cycles CUDA, 16 samples, AgX `AgX -
Medium High Contrast`, exposição +0,4, OIDN `RGB_ALBEDO_NORMAL`, adaptive 0,05,
`volume_step_rate=1,0`, `volume_max_steps=256`.

Um Blender por frame, sem renders concorrentes. RAM disponível amostrada a
cada linha de log; RSS e VRAM a cada ~2 s. Guarda de abort em 350 MB e espera
de início em 1500 MB.

### Operacional consolidado

| Perfil | Frames OK | Wall total | Render por frame | RAM livre mín. | RSS pico | ΔVRAM |
| --- | --- | --- | --- | --- | --- | --- |
| `EXPLOSION` | 6/6 | 257,0 s | 17,3–24,4 s | 792,1 MB | 1143,3 MB | 957–1008 MB |
| `ALL` | 7/7 | 298,4 s | 14,9–18,7 s | 793,8 MB | 1149,6 MB | 914–1193 MB |
| `FIRE` | 4/4 | 144,1 s | 14,8–16,1 s | 890,2 MB | 1147,0 MB | 922–965 MB |
| `SMOKE` | 5/5 | 178,6 s | 13,9–17,9 s | 810,4 MB | 1150,7 MB | 896–993 MB |
| `DEBRIS` | 4/4 | 146,1 s | 13,6–19,2 s | 929,3 MB | 1072,6 MB | 890–919 MB |
| `DUST` | 5/5 | 2646,0 s* | 14,0–2445,7 s* | 888,4 MB | 1134,5 MB | 752–928 MB |
| `COMBINED` | 6/6 | 249,8 s | 16,9–23,9 s | 748,6 MB | 1146,3 MB | 960–1003 MB |

\* Um frame do perfil `DUST` sofreu uma lentidão extrema de render
(2445,7 s) sem abort, sem queda de RAM e sem render concorrente; os demais
frames do mesmo perfil levaram 14,0–56,1 s. O valor está registrado como
outlier operacional, não como comportamento representativo.

A RAM disponível nunca ficou abaixo de **748,6 MB** em nenhum frame — acima do
limite de 350 MB e do objetivo de 500 MB. Nenhum abort por RAM, nenhum render
concorrente, nenhum Blender ativo ao final.

### Cena

- `EXPLOSION` / `ALL`: 547.151 / 547.685 triângulos; 2.615 / 2.735 objetos;
  45 / 46 materiais; 3 luzes; 97 / 124 geometrias compartilhadas.
- Build: 17,9 s (`EXPLOSION`) e 19,7 s (`ALL`).
- Configuração de volume: `Principled Volume`, 3 domínios (ico sub=4), ruído
  em duas escalas + Voronoi, `volume_step_rate=1,0`, `volume_max_steps=256`,
  anisotropia 0,45.

### Comparação numérica com F4.4 (perfil EXPLOSION)

| Frame | Branco clipado F4.4 → F4.5 | Saturação (>0,5) F4.4 → F4.5 | Média luminância F4.4 → F4.5 |
| --- | --- | --- | --- |
| 110 | 2,676 % → **0 %** | 18,67 % → 14,93 % | 102,46 → 94,17 |
| 140 | 2,801 % → **0 %** | 22,15 % → 16,29 % | 97,01 → 84,29 |
| 180 | 2,033 % → **0 %** | 18,75 % → 10,81 % | 98,26 → 83,44 |

A diferença média de pixels entre frames consecutivos da F4.5 permanece
substancial (EXPLOSION: 13,0 / 22,5 / 18,1 / 23,0 / 26,6 entre 82→84→90→110→140→180),
indicando mudança temporal mensurável, mas não provando qualidade estética.

## 7. Testes

- **Estado estrutural (perfil ALL):** `A_84 = f7410311…ded`; A→B→A e sequências
  fora de ordem com hash idêntico; B diferente de A. Registro da execução
  local, fora do pacote: `logs/F45_TESTES_FINAIS.log` e
  `logs/F45_ALL_STATE_ALL.log`.
- **Observação F4.1:** no perfil EXPLOSION (`f42_characters=false`), o patch
  pré-existente `_animate_rigs` acumula rotação de braços com `+=`; por isso o
  teste canônico usa ALL, onde a F4.2 substitui esse patch por atribuição
  absoluta. A explosão F4.5 não possui estado mutável.
- **A→B→A renderizado e fora de ordem:** sufixos `_DETA1`, `_DETA2`, `_DETA3`.
  Repetições de A: `mean_abs=0,208` e `0,094` (ruído CUDA); A vs B: `30,124`,
  razão de **144,8×**. PNGs não são idênticos bit a bit, como esperado.
- **Continuidade t4→t5:** `continuidade_ok=true`; 158 objetos comparados em
  `age=10,1 s`, mesmo hash `6a8393ee…2e08` nos dois takes (`with_blast=False`
  em t5).
- **Geometria:** `estrutura_valida=true`; 158 objetos, 0 faces degeneradas,
  0 vértices não finitos, 0 escalas/transformações inválidas em 84/90/110/140/180.
- **Primitivas proibidas:** nenhuma; luzes da cena: `f41_fill`, `pt`, `sun`.

## 8. Limitações

- Nenhuma aprovação estética foi declarada; métricas não substituem avaliação
  visual.
- O ruído CUDA impede PNGs bit-idênticos para a mesma cena; o estado
  estrutural é idêntico.
- A fumaça depende de volume local (sem raymarching global/cache), portanto
  detalhes finos podem ser limitados por `volume_max_steps=256`.

## 9. Caminhos exatos

- Código: `experimentos/sarajevo_fase4_5/f45_explosion.py`, `render_f45.py`, `preview_f45.py`
- Análise: `analyze_f45.py`, `make_contact_f45.py`, `run_previews.sh`, `run_tests_f45.py`
- Config: `experimentos/sarajevo_fase4_5/config_f45.json`
- Pesquisa: `experimentos/sarajevo_fase4_5/results/F45_PESQUISA.json`
- Métricas: `experimentos/sarajevo_fase4_5/results/F45_METRICAS.json`
- Previews: `experimentos/sarajevo_fase4_5/frames/` — artefatos da execução local, excluídos deste pacote.
- Logs: `experimentos/sarajevo_fase4_5/logs/` — artefatos da execução local, excluídos deste pacote.
- Folhas: `experimentos/sarajevo_fase4_5/contatos/`

## 10. Recomendação

Após a avaliação visual das folhas de contato, se aprovado: estender a cobertura
de frames e validar continuidade t4→t5 com o mesmo `age`/`seed` antes de
qualquer integração. Se reprovado: ajustar apenas `config_f45.json` (densidade
e contraste de fumaça, ganho de fogo, contagem de línguas/fragmentos), sem
tocar fases anteriores. Não commitar, publicar nem renderizar o take completo
sem instrução explícita.
