# Fase 4.5 — reconstrução visual da explosão (Sarajevo, take t4)

Experimento isolado. Nenhum arquivo de fases anteriores foi modificado.

## Estrutura

- `f45_explosion.py` — cinco sistemas independentes (flash, fogo, fumaça, destroços, poeira).
- `render_f45.py` — wrapper Blender sobre `render_f42.py`; `f45_explosion=true` substitui apenas a explosão.
- `preview_f45.py` — driver de previews (um Blender por frame, guarda de RAM 350 MB).
- `config_f45.json` — configuração canônica, perfis e parâmetros.
- `run_previews.sh` — sequência completa de renders (sem concorrência).
- `analyze_f45.py` — métricas operacionais, espaciais, temporais e de determinismo.
- `make_contact_f45.py` — oito folhas de contato.
- `frames/`, `logs/` — artefatos da execução local, excluídos deste pacote.
- `results/`, `contatos/`, `relatorios/` — artefatos gerados.

## Perfis

| Perfil | Conteúdo |
| --- | --- |
| `EXPLOSION` | explosão F4.5 sobre F4.1, refinos F4.2 desligados |
| `ALL` | explosão F4.5 + todos os refinos F4.2 |
| `FIRE` | somente flash + fogo |
| `SMOKE` | somente fumaça volumétrica |
| `DEBRIS` | somente destroços |
| `DUST` | somente poeira rasteira |
| `COMBINED` | cinco sistemas, base F4.1 |

## Comandos

```bash
tools/venv/bin/python experimentos/sarajevo_fase4_5/preview_f45.py ALL 82,84,90,110,140,180
F45_CFG_OVERRIDE='{"f45_state_test":true}' tools/venv/bin/python experimentos/sarajevo_fase4_5/preview_f45.py ALL 84
tools/venv/bin/python experimentos/sarajevo_fase4_5/analyze_f45.py
tools/venv/bin/python experimentos/sarajevo_fase4_5/make_contact_f45.py
```

Padrão de render inalterado: 864×1536, 24 FPS, Cycles CUDA, 16 samples, AgX
`AgX - Medium High Contrast`, exposição +0,4, OIDN `RGB_ALBEDO_NORMAL`,
adaptive sampling 0,05.

## Estado

`age = t + age0 - t0`; todas as transformações e parâmetros de shader são
atribuções absolutas. `hide()` restaura transforms canônicos. A ordem dos
frames não altera o estado estrutural.
