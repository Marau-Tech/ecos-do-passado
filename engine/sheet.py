import sys
from PIL import Image
import project
# uso: sheet.py saida.png shot/frame ...
outp = sys.argv[1]; fs = sys.argv[2:]
c = min(4, len(fs)); r = (len(fs) + c - 1) // c
W = Image.new('RGB', (c * 400, r * 300))
for i, f in enumerate(fs):
    d, k = f.split('/')
    W.paste(Image.open(f'{project.FRAMES}/{d}/{int(k):04d}.png').resize((400, 300)), ((i % c) * 400, (i // c) * 300))
W.save(outp)
