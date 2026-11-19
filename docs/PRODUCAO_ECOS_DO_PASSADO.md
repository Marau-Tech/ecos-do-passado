# Produção — ECOS DO PASSADO

Manual curto para criar episódios históricos imersivos em POV.

## 1. Antes de começar

1. Entre na worktree correta:

   ```bash
   cd ecos-do-passado-atualizado
   ```

2. Audite o repositório:

   ```bash
   pwd
   git rev-parse HEAD
   git branch --show-current
   git status --porcelain
   git worktree list
   ```

3. Leia a Skill `criar-video` em `.opencode/skills/criar-video/SKILL.md`.
   Ela é a fonte autoritativa da identidade visual, dos limites de memória e
   das regras de segurança.

4. Meça o ambiente:

   ```bash
   free -m
   nvidia-smi --query-gpu=name,memory.used,memory.free --format=csv,noheader
   ```

Se houver alterações locais, trate-as como trabalho do usuário. Em caso de
conflito, pare e pergunte. Nunca use `git reset`, `git clean` ou checkout
forçado. Não faça commit nem push sem autorização.

## 2. Iniciar um episódio

```bash
/criar-video Stalingrado
```

O comando:

- carrega a Skill `criar-video`;
- usa o argumento como tema;
- verifica se o episódio já existe;
- pergunta o que fazer se existir (continuar, revisar ou nova versão);
- cria um diretório novo quando necessário;
- apresenta um plano antes de executar.

Sem argumento, o comando pergunta qual acontecimento histórico produzir.

Outros episódios servem de referência de processo: `videos/02-pov-sarajevo/`
(12 takes, 162 s) e `videos/26-pov-stalingrado/`.

## 3. Modos

| Modo | Uso | Configuração |
|---|---|---|
| Preview | câmera, animação, composição | poucos frames, samples reduzidos |
| Produção otimizada | episódio real | 864×1536, 24 fps, 16 samples, Cycles CUDA, AgX +0,4, OIDN, adaptive 0,05 |
| Produção cinematográfica | refinamento extra | só após medir; nunca estourar a RAM |

Samples reduzidos **somente em Preview**. Não diminua resolução, FPS ou
samples em produção sem autorização explícita.

## 4. Roteiro e takes

- Escreva falas curtas e alinhadas a eventos visuais concretos.
- Centralize tempos em `timeline.py` do episódio: início de take, eventos,
  legendas, câmera, narração.
- Sarajevo usa 12 takes de 13,5 s. Cada take tem uma ação e um evento.
- Explosões, disparos e passos compartilham as mesmas constantes de tempo
  (`BLAST_LOCAL`, `SHOT_TIMES`) com o áudio. Não duplique números.
- Narração: Kokoro local, sem API externa (`engine/voice.py`).
- Áudio e efeitos: síntese local (`engine/synth.py`, `audio.py` do episódio).

## 5. Reutilização

Antes de criar algo novo, procure em:

- `videos/02-pov-sarajevo/places.py` — arquitetura, calçamento, câmera POV;
- `videos/02-pov-sarajevo/crowd.py` — multidão e reações;
- `videos/02-pov-sarajevo/cortejo.py` — veículos, explosão;
- `experimentos/sarajevo_fase3_1/scene_f31.py` — materiais PBR, personagens
  com LOD, iluminação aprovada;
- `engine/pov/`, `modelos/pov/` — corpo e animação POV;
- `engine/lib.py`, `engine/post.py` — Blender e FFmpeg.

A Fase 3.1 não foi integrada ao `engine/`. Para aplicá-la a um take real, crie
um wrapper em `experimentos/<episodio>_fase4/`; não altere o take original.

## 6. Renderizar

Sequência obrigatória:

1. **Build** — 0 frames. Meça objetos, materiais, RSS, VRAM, tempo de
   construção. Confira se o dispositivo do Cycles é CUDA/GPU.
2. **Smoke test** — 1 ou 2 frames no ponto de maior complexidade do take
   (em Sarajevo, o instante da explosão no `t4`).
3. **Blocos curtos** — por exemplo 36 frames por bloco, com log e JSON de
   métricas. Um Blender por vez.

Exemplo de medição e guarda (adaptado de `bench_f31.py` e `bench_f4.py`):

- `MemAvailable` em `/proc/meminfo`;
- `VmRSS` do processo em `/proc/<pid>/status`;
- VRAM com `nvidia-smi`;
- limite de abort: **350 MB** de RAM disponível.

Ao cair abaixo do limite: `SIGTERM`, registrar incidente, otimizar, nunca
"tentar só mais um frame".

Blocos interrompidos podem ser retomados: os PNGs já gravados são a fonte da
verdade. Não apague frames concluídos. Não sobrescreva logs antigos de abortos.

Se a margem de RAM ficar entre 350 e 400 MB, use **um Blender por frame**, com
retomada por PNG e espera por memória antes de cada processo. Em Sarajevo, dois
frames no mesmo processo derrubaram a livre para 317 MB; um frame por processo
concluiu com 360 MB. Otimize a cena **antes** de construí-la (rua, calçamento e
multidão enxutos desde a origem), não apagando objetos depois: isso fragmenta a
memória e não reduz o pico de RSS.

### Benchmark de fases sem render longo

Use `experimentos/sarajevo_fase4/bench_f4.py` com `ECOS_BENCH=1`: no máximo um
frame por job, guarda de 350 MB e espera por memória. A instrumentação em
`render_f4.py` é **inerte sem essa variável**. Resultado medido no frame 90:
`wall=25,68 s`, build 5,374 s, render 15,797 s, PNG 0,263 s, RAM mínima
**353,2 MB** — apenas 3,2 MB acima do guarda. Não repetir sem folga de memória.

A decomposição dos 145 frames do `F4_CLIP_R1` mostra que ~7,7 s/frame (36%)
são reconstrução da cena + ciclo de processo evitáveis, contra ~9,61 s (46%)
de amostragem CUDA. O gargalo é a RAM de **2,84 GiB** no WSL, não a GPU
(~2 GB de VRAM livres) nem o disco (~0,26 s por PNG em ext4). Processo
persistente/lotes são alto risco (dois frames já abortaram a 317 MB).
Detalhes em `relatorios/producao_sarajevo_episodio_01/METRICAS_RENDER.md`.

#### Cache de `.blend` (Missão 02 — protótipo, não aplicado)

`experimentos/sarajevo_fase4/render_f4_cache.py` congela `update(t)` e o estado
F4.1, grava a cena base em `.blend` e a reabre por frame, evitando os ~5,37 s
de build. O recurso é **desligado por padrão**: ative apenas com
`ECOS_BLEND_CACHE=1` (opcionalmente `ECOS_BLEND_CACHE_DIR`). Sem cache válido,
o script constrói a cena, grava o cache e segue com o método atual. Nunca use
isso para alterar a configuração visual aprovada nem os takes originais.

O cache foi validado sem render (fingerprints idênticos em dois tempos) e por
SSIM ≥0,9995 nos PNGs, com economia projetada de ~18% (~5 h em 3888 frames).
**Não promova à produção** sem repetir o A/B full-res num ambiente com mais
RAM livre: o caminho cache-hit abortou pelo guarda de 350 MB nesta VM. Veja
`relatorios/producao_sarajevo_episodio_01/RELATORIO_OTIMIZACAO_E_LIMPEZA.md`.

### Fase 4.1 — estado visual

O `F4_CLIP_R1` foi **reprovado**. Melhorias isoladas de explosão, veículos,
personagens e iluminação vivem em `experimentos/sarajevo_fase4/` sob as flags
`f41_*`; 22 previews foram renderizados sem abortos (RAM livre mínima 934 MB).
**A aprovação visual do novo `t4` depende do usuário** — este manual não a
declara. Não renderize o episódio completo antes dessa decisão.

## 7. Pós-produção e revisão

- Monte narração, efeitos, trilha e cortes na timeline.
- Exporte o master vertical: **1080×1920**, MP4 H.264, 24 fps, AAC estéreo,
  `yuv420p`, `+faststart`.
- Assista ao vídeo **inteiro** antes de considerá-lo concluído.
- Confira: sincronização, cortes, continuidade, imagem, volume, inteligibilidade,
  ausência de frames pretos e de takes faltando, duração, resolução, FPS e
  integridade do MP4.

## 8. Publicação

Prepare um único master e reutilize-o em:

1. YouTube Shorts;
2. Instagram Reels;
3. TikTok;
4. Facebook Reels, se viável.

Para cada plataforma: título principal, alternativas, descrição, legenda,
hashtags, capa/thumbnail e texto curto. Não invente fatos históricos.

**Não entre em contas, não envie, não publique e não agende sem autorização
explícita.**

## 9. Checklist reutilizável

### Produção

- [ ] Worktree, HEAD e status auditados.
- [ ] Tema, data e local definidos.
- [ ] Fontes históricas separadas de reconstruções visuais.
- [ ] Roteiro e narração alinhados aos eventos.
- [ ] Takes planejados com ação, evento e transição.
- [ ] Recursos existentes verificados antes de criar novos.
- [ ] Timeline única para imagem, áudio e legendas.
- [ ] Build medido (RSS, VRAM, objetos, materiais).
- [ ] Preview validado.
- [ ] Blocos renderizados com log e retomada.
- [ ] Guarda de 350 MB ativa e incidentes registrados.
- [ ] Vídeo inteiro assistido e conferido.

### Publicação

- [ ] Master 1080×1920, 24 fps, H.264, AAC, `yuv420p`, `faststart`.
- [ ] Título, descrição, legenda, hashtags e thumbnail prontos.
- [ ] Requisitos de cada plataforma verificados.
- [ ] Nenhuma ação externa executada sem autorização.
- [ ] Concluído / testado / pendente / dependente de aprovação discriminados.
