---
name: criar-video
description: Planejar, criar, renderizar, editar e preparar episódios históricos do ECOS DO PASSADO com qualidade fotorrealista, câmera POV e publicação multiplataforma.
---

# Criar vídeo — ECOS DO PASSADO

Skill permanente para produzir episódios históricos imersivos em primeira pessoa.
Use-a sempre que o usuário pedir um episódio novo, uma revisão de episódio existente
ou a preparação de materiais de publicação. O atalho é `/criar-video <tema>`.

**Idioma:** português brasileiro.

## 0. Regra de ouro

O padrão vigente é a **Fase 3.1** de Sarajevo, em
`experimentos/sarajevo_fase3_1/`. Não reconstrua essa referência do zero e não
volte à estética antiga descrita em `README.md` e `GUIA.md` (analog horror, VHS,
HUD, `REC`, contador, quadro 4:3, 15/30 fps). Esses dois arquivos documentam o
projeto anterior; para o ECOS DO PASSADO eles são contexto histórico, não
especificação visual.

Antes de qualquer operação, execute a auditoria de segurança da seção 10.
Nunca publique, faça commit ou push sem autorização explícita.

---

## 1. Identidade visual permanente

Padrão aprovado na Fase 3.1 — preservar em todos os episódios:

- Fotorrealismo histórico e direção cinematográfica.
- Vertical **9:16**, tela integral, sem barras decorativas.
- Sem VHS, moldura `REC`, contador, HUD ou marcações de tempo na imagem.
- Câmera **POV imersiva**, origem `(0, 0, 1,65)` m, alvo `(0, 12, 1,55)` m,
  lente **28 mm**, `sensor_fit='VERTICAL'`, `sensor_height=36`.
- Arquitetura modular detalhada, com vãos, vidro, jambas, peitoris, cornijas.
- Materiais **PBR compartilhados**: um grupo `f31_surface` com variação de cor,
  roughness, manchas, micro-relevo, anisotropia, vidro (transmissão 0,22,
  IOR 1,46) e metais (0,74–0,80).
- Personagens articulados com **três LODs** (hero / mid / far), pivôs de
  quadril, joelhos, cotovelos, mãos, dedos, chapéus e acessórios.
- Veículos históricos detalhados: malha do `cortejo.automobile()`, raios,
  refletores, câmbio, pedais e instrumentos.
- Iluminação cinematográfica contida: céu de 4 bandas, sol principal
  `(1, 0,91, 0,80)` a 3,2°, sol difuso frio a 12°, uma área de 7 m / 170 W.
  **Três luzes no total** — uma quarta luz já causou abortos por RAM.
- Cycles com **CUDA**, **AgX**, look `AgX - Medium High Contrast`,
  exposição **+0,4**.
- Render candidato: **864×1536**, **24 fps reais**, **16 samples**, OIDN
  (`RGB_ALBEDO_NORMAL`), adaptive sampling com limiar **0,05**.
- Bounces `max=3 / diffuse=1 / glossy=2 / transmission=1`, clamp indireto 4,0,
  `use_light_tree=False`, `use_persistent_data=False`, filtro 1,4.
- Master de publicação: **1080×1920**, MP4 H.264, `yuv420p`, `faststart`,
  AAC estéreo, 24 fps. O 3D pode ser renderizado em 864×1536 e ampliado.

Exposições alternativas (+0,2 e +0,6) estão em
`experimentos/sarajevo_fase3_1/comparacoes/07_exposicoes.png`. Não altere o
padrão +0,4 sem decisão explícita do usuário.

---

## 2. Hardware e limites

Máquina real:

- CPU AMD Ryzen 7 7435HS.
- NVIDIA GeForce RTX 3050 Laptop, **4 GB VRAM**.
- 16 GB RAM no Windows, mas o **WSL enxerga apenas ~2,9 GB** — esse é o limite.
- Blender 4.5 LTS (em `tools/blender/blender`), FFmpeg em `tools/ffmpeg`,
  Python 3.12.3, Kokoro local em `tools/kokoro`.

Medições da Fase 3.1 (não teóricas):

- 10,31–10,34 s/frame em blocos estáveis de 36 frames.
- Pico RSS ~1701 MB; pico VRAM ~2059 MB.
- RAM livre mínima em bloco bom: 375–387 MB.
- Guarda de RAM em **350 MB**; quatro abortos reais abaixo dela (340, 346,
  337 e 316 MB). Picos transientes de ~585 MB ocorreram em
  `Updating Lights | Computing distribution`.
- Sem CUDA, o fallback por software chegou a 55,8 s/frame.

Regras:

1. Meça `MemAvailable` em `/proc/meminfo`, `VmRSS` do Blender e VRAM via
   `nvidia-smi` **antes** e **durante** cada bloco.
2. Se RAM livre cair abaixo de **350 MB**, interrompa o Blender com `SIGTERM`
   (depois `SIGKILL` se necessário), registre o incidente e otimize antes de
   continuar. Não "tente só mais um frame".
3. Execute **no máximo um Blender por vez** nesta máquina. O script antigo
   `video` usa `xargs -P 3` na GPU; não use esse paralelismo aqui.
4. Nunca reduza resolução, FPS ou samples para contornar falta de memória.
   Reduza escopo: menos luzes, bounces, geometria duplicada; divida em blocos.
5. Não recomende GPUs de 12 GB/16 GB. A meta é caber na RTX 3050 de 4 GB.
6. Samples reduzidos são permitidos **somente em Preview**.

Planejamento realista: 162 s × 24 fps = 3888 frames. O valor de 10,34 s/frame
da Fase 3.1 (≈ 11,2 h) pressupõe processo persistente, que nesta máquina já
abortou a 317 MB. Com **um Blender por frame** — único modo estável — o
`F4_CLIP_R1` mediu 21,0 s/frame, ou **~22,7 h**. Comunique isso antes de
prometer prazo; nunca reduza qualidade para caber no tempo.

O gargalo é a RAM de 2,84 GiB do WSL, não a GPU (~2 GB de VRAM livres) nem o
disco (~0,26 s por PNG em ext4). Cerca de 7,7 s/frame (36%) são reconstrução
da cena + ciclo de processo. Cache de `.blend` da cena base é o próximo
candidato de otimização; processo persistente/lotes são alto risco.

---

## 3. Estrutura do projeto (verificada nesta worktree)

Worktree de trabalho: diretório atual do checkout (`ecos-do-passado-atualizado`).
O clone `ecos-do-passado` **não** é o diretório de trabalho.

```
engine/                     bibliotecas compartilhadas (lib, project, render, post, voice, synth, pov/)
modelos/pov/                corpo e animação do personagem POV
modelos/<outros>/           formatos do projeto antigo — consultar, não misturar
videos/02-pov-sarajevo/     episódio 01: 12 takes, timeline, áudio, cenas
videos/26-pov-stalingrado/  outro episódio ECOS, referência de processo
out/02-pov-sarajevo/        previews/mudos refino_v2/v3/v4 + áudio
render/02-pov-sarajevo/     PNGs de preview/v2/v3/v4_tests + log.txt
experimentos/               tudo de Sarajevo, não integrado ao engine/
  sarajevo_ab_v1/           Fase 2 — A/B (referência)
  sarajevo_fase3/           Fase 3 (referência)
  sarajevo_fase3_1/         REFERÊNCIA VISUAL OFICIAL (Fase 3.1)
  sarajevo_fase4/           takes reais, Fase 4.1 e benchmarks
    render_f4.py            wrapper (ECOS_BENCH=1 liga a instrumentação)
    blend_cache.py          congela/restaura closure update(t) + globals
    diag_cache.py           diagnóstico sem render (fingerprints)
    render_f4_cache.py      cache .blend (ECOS_BLEND_CACHE=1, desligado por padrão)
    bench_f4.py             driver curto, um Blender por job
    bench/results|logs      resultados e logs dos benchmarks A/B e validação
tools/                      symlinks absolutos para o outro worktree — essenciais
docs/PRODUCAO_ECOS_DO_PASSADO.md   manual vigente
relatorios/                 relatórios, métricas, incidentes, pacote de publicação
.opencode/skills/           esta Skill
.opencode/commands/         atalho /criar-video
README.md / GUIA.md         contexto histórico do Analog Planetas — não são especificação visual
video                       CLI genérico: ./video <pasta-em-videos> <comando>
```

Os diretórios `videos/01-*…25-*`, `out/01-*…25-*`, `site/` e os
`tmp_video_f3/`/`tmp_video_f31/` foram removidos na Missão 02 após backup
verificado em backup local preservado (`ecos-do-passado-pre-limpeza-2026-11-18/`).
Referências antigas em `GUIA.md`/`README.md` são históricas.

 Não presuma outros caminhos: verifique com `ls`/`find` antes de usar.
 Não modifique `engine/`, modelos compartilhados ou outros episódios sem
 necessidade e autorização. `engine/project.py` deriva `videos/<VIDEO>`,
 `render/<VIDEO>` e `out/<VIDEO>` da variável `VIDEO`, e a renomeação de
 `videos/02-pov-sarajevo/` exigiria atualizar 75 referências (25 executáveis,
 13 documentais, 31 de relatórios e 6 de logs). Só reorganizar com
 autorização explícita.

---

## 4. Procedimento para um novo episódio

Executar por etapas, apresentando o resultado de cada uma antes de avançar:

1. **Tema** — identificar o acontecimento, o local e a data.
2. **Pesquisa** — ver a seção 5.
3. **Narrativa** — definir o arco, o ponto de vista e o arco emocional.
4. **Takes** — planejar cenas curtas (Sarajevo usa 12 × 13,5 s). Cada take
   precisa de uma ação, um evento e uma transição.
5. **Roteiro e narração** — escrever falas curtas alinhadas aos eventos;
   a narração é gerada por Kokoro local, sem API externa.
6. **Cenários** — reutilizar `places.py`, fachadas, calçamento, iluminação.
7. **Personagens e veículos** — usar `modelos/pov`, `engine/pov/` e
   `cortejo.automobile()` antes de criar qualquer coisa nova.
8. **Reutilização** — ver a seção 6.
9. **Timeline** — centralizar tempos de take, eventos, legendas e câmera em
   `timeline.py` do episódio, como em `videos/02-pov-sarajevo/timeline.py`.
10. **Sincronização** — explosão, disparos, passos e narração usam os mesmos
    tempos compartilhados (`BLAST_LOCAL`, `SHOT_TIMES`). Nunca duplique números.
11. **Preview** — alguns frames, samples baixos, só para câmera/composição.
12. **Validação visual** — comparar com `experimentos/sarajevo_fase3_1/`.
13. **Render por partes** — blocos com logs, retomada e guarda de RAM.
14. **Pós-produção** — áudio, mixagem, legendas quando aplicáveis, cortes.
15. **Revisão completa** — assistir o vídeo inteiro; ver a seção 4.1.
16. **Publicação** — preparar master e materiais; **não publicar** sem ordem.

### 4.1 Checklist de revisão

- [ ] Sincronização entre áudio e eventos visuais.
- [ ] Cortes e continuidade entre takes (especialmente antes/depois de explosões).
- [ ] Qualidade de imagem e ausência de VHS/HUD/barras.
- [ ] Volume e inteligibilidade da narração.
- [ ] Nenhum frame preto e nenhum take faltando.
- [ ] Duração, resolução, FPS e contagem de frames conferidos.
- [ ] MP4 íntegro, `yuv420p`, `faststart`, trilha AAC estéreo.
- [ ] Master 1080×1920 gerado a partir do render 864×1536.

---

## 5. Pesquisa histórica

Para cada episódio:

- Identificar local, data e período exato; registrar a cronologia.
- Verificar vestimentas, arquitetura, veículos, objetos e iluminação natural
  da época e do horário representado.
- Separar explicitamente **fatos documentados** de **reconstruções visuais**.
- Não inventar detalhes e apresentá-los como fato. Se uma cena for hipotética,
  diga isso na descrição ou no relatório.
- Guardar fontes e referências usadas em um arquivo de notas do episódio.
- Manter coerência temporal e geográfica entre takes (ex.: o relógio da cidade
  deve avançar de forma compatível com a ação).

---

## 6. Reutilização de recursos

Antes de criar qualquer recurso novo, procure um equivalente:

- Arquitetura modular: `videos/02-pov-sarajevo/places.py`.
- Calçamento e atributos PBR: `places.cobblestones()` + Fase 3.1
  `cobble_pbr()`.
- Materiais PBR e grupo compartilhado: `experimentos/sarajevo_fase3_1/scene_f31.py`.
- Personagens e LODs: `engine/pov/`, `modelos/pov/` e `scene_f31.person()`.
- Veículos: `videos/02-pov-sarajevo/cortejo.py::automobile()`.
- Iluminação: `scene_f31.lighting()` / `sky_world()`.
- Câmera POV e marcha: `places.walk_pov()`, `pov_pose()`.
- Multidão e reações: `videos/02-pov-sarajevo/crowd.py`.
- Áudio e narração: `engine/synth.py`, `engine/voice.py`,
  `videos/02-pov-sarajevo/audio.py`.
- Pós e FFmpeg: `engine/post.py`.

A Fase 3.1 **não foi integrada** ao `engine/`: ela vive em `experimentos/`.
Para levar o visual a um take real, use um wrapper isolado em um diretório
experimental novo; não sobrescreva takes originais nem bibliotecas
compartilhadas. Exemplo de local: `experimentos/<episodio>_fase4/`.

---

## 7. Controle de memória

- Sempre comece com um job de **construção** (0 frames) para medir objetos,
  materiais, RSS e VRAM antes de renderizar.
- Em seguida, um **smoke test** de 1–2 frames, depois blocos curtos.
- Use `PYTHONPATH` apontando para `engine/`, `videos/<episodio>/` e o diretório
  do experimento; defina `VIDEO=<pasta>` e `GPU=1`.
- Monitore a cada 0,2 s: `MemAvailable`, `VmRSS` e `nvidia-smi`.
- Registre por bloco: frames, primeiro frame, média estável, picos de RSS/VRAM,
  RAM livre mínima, tempo de construção, configuração e caminho do log.
- Grave um JSON de resultado e um log por bloco. Nunca substitua logs antigos
  de incidentes.
- Se o processo cair, os PNGs já salvos permitem retomar somente os frames
  faltantes. Não apague frames concluídos.
- Se a margem de RAM ficar entre 350 e 400 MB, renderize **um frame por
  processo Blender**, com retomada por PNG e espera até haver memória
  suficiente antes de iniciar o próximo. Medições reais em Sarajevo
  mostraram que dois frames no mesmo processo derrubavam a livre para
  317 MB, enquanto um frame por processo concluía com 360 MB.
- Prefira geometria compartilhada e instâncias; evite reconstruir a cidade a
  cada frame; mantenha `use_persistent_data=False` se a retenção de memória
  causar instabilidade.
- Otimize a cena **antes** de construí-la (interceptando geradores de rua,
  calçamento e multidão), não depois: apagar objetos após a construção
  fragmenta a memória e não reduz o pico de RSS.
- Para medir sem render longo, use `experimentos/sarajevo_fase4/bench_f4.py`
  com `ECOS_BENCH=1`: no máximo um frame por job, guarda de 350 MB e espera
  por memória. O marcador `frame` de `render_f4.py` já é emitido após
  render+save; some as durações ao timestamp e o `shutdown_residual` fica
  negativo (erro corrigido em `bench/results/B_T4_T4.json`).
- Benchmark A (frame 90): `wall=25,68 s`, build 5,374 s, render 15,797 s,
  PNG 0,263 s, RAM mínima 353,2 MB — apenas 3,2 MB acima do guarda. Não
  reexecutar sem folga nem com auditorias concorrentes. Nenhuma qualidade
  foi reduzida; a instrumentação é inerte sem `ECOS_BENCH=1`.

---

## 8. Modos de produção

**Preview**
- Poucos frames, samples reduzidos (por exemplo 6), empresa apenas de câmera,
  animação, composição e sincronização.
- Nunca usar o resultado de Preview como master.

**Produção otimizada**
- Padrão aprovado: Cycles CUDA, 864×1536, 24 fps, 16 samples, AgX +0,4, OIDN,
  adaptive 0,05. Controle rigoroso de RAM, um Blender por vez, blocos curtos.
- É o modo padrão para episódios.

**Produção cinematográfica**
- Maior qualidade possível **dentro do mesmo hardware**: mais bounces, mais
  detalhe de geometria, iluminação refinada.
- Só aplicar depois de medir o custo real em Preview e em blocos da produção
  otimizada. Nunca exceder a memória disponível.

Não reduza silenciosamente resolução, FPS ou samples. Qualquer mudança precisa
ser registrada e aprovada.

---

## 9. Publicação

Preparar, sem publicar:

1. Master vertical único: 1080×1920, MP4 H.264, 24 fps, AAC estéreo,
   `yuv420p`, `+faststart`. Reutilize-o para todas as plataformas.
2. YouTube Shorts, Instagram Reels, TikTok e Facebook Reels (se viável).
3. Título principal, títulos alternativos, descrição, legenda, hashtags,
   thumbnail/capa e texto curto de apresentação.
4. Não inventar fatos históricos na descrição.
5. Verificar requisitos atuais de formato e duração antes de sugerir alterações.
6. **Nunca** entrar em contas, enviar, publicar ou agendar sem autorização
   explícita do usuário.

---

## 10. Segurança e Git

Antes de qualquer operação:

1. Confirmar `pwd`.
2. `git rev-parse HEAD`, `git branch --show-current`, `git status --porcelain`.
3. Identificar alterações locais, arquivos novos e experimentos existentes.
4. Confirmar a worktree correta com `git worktree list`.

Proibido:

- `git reset`, `git clean`, checkout forçado ou qualquer operação destrutiva.
- Commit ou push sem autorização.
- Sobrescrever arquivos existentes, backups, previews, renders ou logs.
- Substituir alterações do usuário; em caso de conflito, parar e perguntar.
- Instalar ou baixar dependências/modelos sem autorização.
- Alterar outros episódios ou `engine/` sem necessidade e autorização.

Preservar integralmente:

- `out/02-pov-sarajevo/refino_v2`, `refino_v3`, `refino_v4`.
- `render/02-pov-sarajevo/v4_tests`.
- `experimentos/sarajevo_ab_v1/`, `experimentos/sarajevo_fase3/`,
  `experimentos/sarajevo_fase3_1/` e `experimentos/sarajevo_fase4/`
  (inclui `F4_CLIP_R1`, F4.1, benchmarks e `INCIDENTE_RAM.md`).
- `relatorios/`, `docs/` e `.opencode/` — Skill, comando, manual, métricas,
  logs de incidente e pacote de publicação.
- `tools/` e seus symlinks para o outro worktree — são essenciais.
- Os 7 arquivos `.py` modificados e `crowd.py` (untracked) em
  `videos/02-pov-sarajevo/` — são trabalho do usuário e são necessários ao
  timeline de 162 s.

`F4_CLIP_R1` foi **reprovado visualmente**: é referência de diagnóstico, não
produto final. O novo `t4` da Fase 4.1 ainda aguarda avaliação do usuário;
não declare aprovação nem renderize o episódio completo sem autorização.

O cache de `.blend` em `experimentos/sarajevo_fase4/` é um **protótipo
isolado**, desligado por padrão (`ECOS_BLEND_CACHE=1` para ativar). Não o
promova à produção nem altere a qualidade aprovada: detalhes, benchmark,
incidentes de RAM e recomendação em
`relatorios/producao_sarajevo_episodio_01/RELATORIO_OTIMIZACAO_E_LIMPEZA.md`.

Toda implementação nova deve ser rastreável e reversível. Em caso de dúvida,
pare e apresente a situação.
