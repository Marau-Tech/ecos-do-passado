---
description: Inicia o fluxo de produção de um episódio do ECOS DO PASSADO a partir de um tema histórico.
---

# /criar-video

Você é o diretor técnico de produção do ECOS DO PASSADO.

**Primeira ação obrigatória:** carregue a Skill `criar-video` com a ferramenta
`skill` (id exato: `criar-video`) e siga o fluxo completo dela nesta sessão.
O arquivo está em `.opencode/skills/criar-video/SKILL.md`. Ela contém a identidade visual
aprovada, os limites reais de hardware, a estrutura do projeto, o procedimento
de produção, as regras de pesquisa histórica, os modos de render, os cuidados
de memória, a política de publicação e as regras de segurança.

Tema informado pelo usuário: `$ARGUMENTS`

## 1. Tema

- Se `$ARGUMENTS` estiver vazio, pergunte ao usuário qual episódio ou
  acontecimento histórico ele deseja produzir. Não escolha um tema sozinho.
- Use o tema fornecido como o assunto do novo episódio.
- Identifique local, data e período; se faltarem informações essenciais,
  pergunte antes de planejar.

## 2. Segurança antes de qualquer operação

- Confirme `pwd` e que a worktree é o diretório atual do checkout
  (`ecos-do-passado-atualizado`).
- Verifique `git rev-parse HEAD`, `git branch --show-current` e
  `git status --porcelain`.
- Liste alterações locais, arquivos novos e experimentos existentes.
- Não execute `git reset`, `git clean`, checkout forçado, commit ou push.
- Não apague nem sobrescreva arquivos, backups, previews, renders ou logs.
- Não modifique `engine/`, bibliotecas compartilhadas, materiais, modelos ou
  outros episódios sem necessidade e autorização.

## 3. Episódio existente

- Verifique se já existe episódio com nome correspondente ao tema em `videos/`.
- Se existir, **não sobrescreva e não duplique automaticamente**.
  Pergunte se o usuário deseja:
  1. continuar a produção existente,
  2. revisar/validar o material já produzido, ou
  3. criar uma nova versão em diretório novo.
- Se não existir, crie um diretório novo para o episódio, seguindo a
  convenção observada em `videos/` e validando o nome antes de criar.

## 4. Planejamento

Consulte a Skill e apresente um plano curto antes de executar:

- arco narrativo e cronologia;
- takes propostos, com ação e evento por take;
- narração, efeitos sonoros e trilha;
- cenários, personagens e veículos reutilizáveis;
- dependências e riscos, em especial de RAM/VRAM;
- estimativa de tempo com base em medições reais, não otimista.

Referência honesta: **~21,0 s/frame com um Blender por frame**, medidos no
`F4_CLIP_R1`, ou **~22,7 h** para os 3888 frames do episódio. Os 10,34 s/frame
da Fase 3.1 dependem de processo persistente, que nesta máquina já abortou a
317 MB. Nunca reduza resolução, FPS ou samples para caber no prazo.

## 5. Execução por etapas

Execute o fluxo em etapas, reportando o resultado de cada uma:

1. pesquisa histórica e separação entre fato documentado e reconstrução visual;
2. roteiro, narração e timeline sincronizada;
3. cenários e atores reaproveitando os recursos catalogados na Skill;
4. Preview com poucos frames e samples reduzidos **somente neste modo**;
5. validação visual contra a referência da Fase 3.1 — o `F4_CLIP_R1` foi
   reprovado e o novo `t4` da Fase 4.1 ainda aguarda decisão do usuário;
   não trate as melhorias isoladas como aprovadas;
6. produção otimizada em blocos, com logs e retomada segura;
7. pós-produção, mixagem e revisão integral do vídeo;
8. master vertical 1080×1920 e pacote multiplataforma.

Respeite sempre: Cycles CUDA, AgX, exposição +0,4, 864×1536, 24 fps reais,
16 samples, OIDN e adaptive sampling. Se a RAM livre cair abaixo de 350 MB,
interrompa com segurança, registre o incidente e otimize antes de continuar.
Nunca reduza resolução, FPS ou samples silenciosamente.

## 6. Entrega

- Separar claramente: concluído, testado, pendente e dependente de aprovação.
- Preparar título, descrição, legenda, hashtags e thumbnail.
- **Não entrar em contas, não enviar, não publicar e não agendar** sem
  autorização explícita do usuário.
- Não fazer commit nem push sem autorização explícita.

Se a Skill `criar-video` não estiver disponível no ambiente, pare e informe:
o fluxo não deve continuar sem ela.
