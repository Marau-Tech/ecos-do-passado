#!/usr/bin/env bash
# Execução sequencial de todos os previews da Fase 4.5.
# Um Blender por frame; nenhum render concorrente.
set -euo pipefail
cd "$(dirname "$0")/../.."
P="tools/venv/bin/python experimentos/sarajevo_fase4_5/preview_f45.py"

$P EXPLOSION 82,84,90,110,140,180
$P ALL 36,82,84,90,110,140,180
$P FIRE 84,90,110,140
$P SMOKE 84,90,110,140,180
$P DEBRIS 84,90,110,140
$P DUST 84,90,110,140,180
$P COMBINED 82,84,90,110,140,180

F45_RUN_SUFFIX=_DETA1 $P EXPLOSION 84
F45_RUN_SUFFIX=_DETA2 $P EXPLOSION 140,84
F45_RUN_SUFFIX=_DETA3 $P EXPLOSION 82,180,90,84

echo PREVIEWS_F45_CONCLUIDOS
