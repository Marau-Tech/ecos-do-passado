# Analog Planetas

Gerador de vídeos verticais de analog horror, no formato "escolha um planeta para passar 24 horas". Tudo é feito por código: cenas 3D, filtro VHS, trilha, legendas e narração. O projeto não usa imagens nem músicas prontas.

## Como funciona

| Etapa | Ferramenta |
|---|---|
| Cenas 3D | Blender, com o Cycles na CPU |
| Filtro VHS, legendas e OSD | NumPy, SciPy e Pillow |
| Trilha e efeitos sonoros | Síntese em NumPy |
| Narração | Kokoro, local, sem chave de API |
| Montagem | ffmpeg |

O resultado é um MP4 de 1080×1920, com o quadro 4:3 no centro e as legendas nas barras pretas. Os vídeos prontos não ficam no repositório, só o código que os gera.

## Instalação

Requer Ubuntu 24.04 ou WSL, com Python 3.12.

```bash
git clone https://github.com/Felipe-Meneguzzi/analog-planetas.git
cd analog-planetas
sudo apt install curl xz-utils python3-venv fonts-dejavu-core libgl1 libsm6 libx11-6 libxext6 libxfixes3 libxi6 libxkbcommon0 libxrender1
./setup.sh
```

O `setup.sh` baixa o Blender, o ffmpeg e o modelo de voz para a pasta `tools/`.

## Uso

```bash
./video 02-four-more-planets preview   # versão rápida, em cerca de 10 minutos
./video 02-four-more-planets final     # render completo, em cerca de 1h30 na CPU
./video 02-four-more-planets status    # frames prontos
```

Os vídeos saem em `out/<video>/`.

## Estrutura

```
engine/    código compartilhado: cenas, filtro, áudio e narração
videos/    roteiro, cenas e trilha de cada vídeo
site/      site do app do TikTok
GUIA.md    guia completo para criar um vídeo novo
```

Para criar um vídeo novo, siga o [GUIA.md](GUIA.md).
