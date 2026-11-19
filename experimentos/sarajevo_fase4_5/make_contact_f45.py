"""Folhas de contato da FASE 4.5 — apenas composição de PNGs já renderizados.

Gera oito folhas em contatos/:

  1. folha_F45_F31_F44_F45.png   F3.1 aprovada × F4.4 × F4.5 (ALL)
  2. folha_F45_F44_vs_F45.png    F4.4 × F4.5 (EXP e ALL)
  3. folha_F45_fogo.png          Fogo: isolado e combinado
  4. folha_F45_fumaca.png        Fumaça: F3.1 / F4.4 / F4.5 / isolada
  5. folha_F45_destrocos.png     Destroços: F3.1 / F4.4 / F4.5 / isolados
  6. folha_F45_evolucao.png      Evolução temporal da F4.5 (EXP e ALL)
  7. folha_F45_sistemas.png      Sistemas isolados A–E
  8. folha_F45_poeira.png        Poeira rasteira: isolada e combinada

Nenhuma imagem é gerada de novo e nenhum arquivo antigo é alterado.
Uso: tools/venv/bin/python make_contact_f45.py
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
F44 = os.path.join(ROOT, 'experimentos', 'sarajevo_fase4_4', 'frames')
F43 = os.path.join(ROOT, 'experimentos', 'sarajevo_fase4', 'frames')
FRAMES = os.path.join(HERE, 'frames')
OUT = os.path.join(HERE, 'contatos')
os.makedirs(OUT, exist_ok=True)

W, H = 216, 384
PAD, LABEL = 8, 22

# (rótulo, diretório, prefixo)
F31 = ('F3.1 aprovada', F43, 'F4_CLIP_R1')
F44_EXP = ('F4.4 EXP', F44, 'F44_EXPLOSION')
F44_ALL = ('F4.4 ALL', F44, 'F44_ALL')
F45_EXP = ('F4.5 EXP', FRAMES, 'F45_EXPLOSION')
F45_ALL = ('F4.5 ALL', FRAMES, 'F45_ALL')
F45_FIRE = ('F4.5 FOGO', FRAMES, 'F45_FIRE')
F45_SMOKE = ('F4.5 FUMACA', FRAMES, 'F45_SMOKE')
F45_DEBRIS = ('F4.5 DESTROCOS', FRAMES, 'F45_DEBRIS')
F45_DUST = ('F4.5 POEIRA', FRAMES, 'F45_DUST')


def src(col, frame):
    label, directory, prefix = col
    path = os.path.join(directory, '%s_%04d.png' % (prefix, frame))
    return path if os.path.exists(path) else None


def draw_sheet(dest, rows, cols):
    cw = W + 2 * PAD
    rh = H + 2 * PAD + LABEL
    sheet = Image.new('RGB', (cw * cols, rh * len(rows)), (18, 18, 18))
    d = ImageDraw.Draw(sheet)
    for r, (title, cells) in enumerate(rows):
        for c in range(cols):
            x = c * cw + PAD
            y = r * rh + PAD + LABEL
            if c >= len(cells) or cells[c][1] is None:
                d.text((x, y + H // 2), 'SEM PREVIEW', fill=(120, 120, 120))
                continue
            label, path = cells[c]
            im = Image.open(path).convert('RGB').resize(
                (W, H), Image.LANCZOS)
            sheet.paste(im, (x, y))
            d.text((x, y - LABEL + 4), '%s  %s' % (label, title),
                   fill=(235, 235, 225))
    sheet.save(dest, optimize=True)
    print('%s -> %s (%d linhas)' % (os.path.basename(dest), dest, len(rows)))


def make(name, frames, columns, min_columns=2):
    rows = []
    for f in frames:
        cells = [(col[0], src(col, f)) for col in columns]
        if sum(1 for c in cells if c[1]) >= min_columns:
            rows.append(('f%03d' % f, cells))
    if rows:
        draw_sheet(os.path.join(OUT, name), rows, len(columns))


def main():
    make('folha_F45_F31_F44_F45.png', [36, 82, 84, 90, 110, 140, 180],
         [F31, F44_ALL, F45_ALL], min_columns=2)

    make('folha_F45_F44_vs_F45.png', [82, 84, 90, 110, 140, 180],
         [F31, F44_EXP, F44_ALL, F45_EXP, F45_ALL], min_columns=4)

    make('folha_F45_fogo.png', [84, 90, 110, 140],
         [F31, F44_EXP, F45_EXP, F45_FIRE], min_columns=3)

    make('folha_F45_fumaca.png', [84, 90, 110, 140, 180],
         [F31, F44_EXP, F45_EXP, F45_SMOKE], min_columns=3)

    make('folha_F45_destrocos.png', [84, 90, 110, 140],
         [F31, F44_EXP, F45_EXP, F45_DEBRIS], min_columns=3)

    make('folha_F45_evolucao.png', [82, 84, 90, 110, 140, 180],
         [F45_EXP, F45_ALL], min_columns=2)

    make('folha_F45_sistemas.png', [84, 90, 110, 140],
         [F45_FIRE, F45_SMOKE, F45_DEBRIS, F45_DUST], min_columns=2)

    make('folha_F45_poeira.png', [84, 90, 110, 140, 180],
         [F31, F44_EXP, F45_EXP, F45_DUST], min_columns=3)


if __name__ == '__main__':
    main()
