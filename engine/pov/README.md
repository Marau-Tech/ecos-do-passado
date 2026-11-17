# Personagem POV (`engine/pov/`)

Corpo em primeira pessoa reutilizável: anatomia com medidas reais, roupas de época e
movimento ligado à câmera da cena. O corpo é **fisicamente correto**: só aparece na tela o
que um olho a 1,65 m veria. Com a câmera olhando para a frente, nada do corpo aparece. Mãos,
fuzil, pernas e botas entram no quadro quando a cena dirige um gesto ou um olhar para baixo.

## Uso numa cena

```python
from pov import create_character
from pov.motion import head_eye

me = create_character(cam, 'sarajevo_civilian_1914', ground=0.0)

def update(t, u):
    walk_pov(cam, t, (0.0, 5.0, EYE), speed=0.55, pitch=-2.0, seed=3.0)
    me.update(t, cam, speed=0.55, heading=0.0, actions=[('watch', 3.0, 8.0)])
    return None
```

- `speed`: a mesma velocidade da câmera (m/s); 0 é parado. A marcha usa a fase de
  `walk_pov` (`sin(pi * 1.8 * t)`), então passo, balanço da câmera e pés andam juntos.
- `heading`: rumo do corpo em radianos (0 = +Y). Fixar o rumo evita que o tremor da câmera
  gire o corpo.
- `ground`: altura do chão. Com ela, os pés ficam plantados apesar do balanço da câmera.
- `actions`: `(pose, início, fim[, rampa])` em segundos do take.
- `update` é função pura de `t`: qualquer frame pode ser renderizado sozinho, em qualquer ordem.

## Ações

| Pose | Lados | Aparece quando | Uso |
|---|---|---|---|
| `watch` | esquerda | olhar a −40° | Civil olhando o relógio de bolso |
| `shield` | as duas | olhar para a frente | Susto: explosão, disparos (mãos diante do rosto, rampa curta) |
| `reach` | direita | olhar a −12° | Afastar alguém à frente |
| `rail` | direita | olhar a −40°, cabeça virada 45° à direita | Mão apoiada num parapeito de 1,07 m, a 0,5 m do corpo |
| `rifle` | as duas | olhar a −22° ou mais | Soldado com o fuzil pronto, atravessado no peito. Acima de −20° só o cano entra no quadro e o fuzil parece flutuar |

O relógio e o fuzil só existem durante a pose. Comece o take já com a pose (rampa 0 no
início), para o objeto não surgir no meio do quadro.

## Olhar para baixo e para o lado

Com a lente de 30 mm, os pés só entram no quadro com a cabeça a −64° ou mais: a −67° o sapato
da frente aparece pela borda de baixo a cada passo e ainda se veem 3 a 4 m de chão; a −72°
aparecem pernas, botões e a mão que balança. Inclinar o tronco não ajuda: o olho avança e fica
em cima dos pés (testado e descartado).

Em Sarajevo, `walk_pov(..., gaze=[(início, fim, pitch, rampa, giro)])` dirige esses olhares; o
giro (graus, negativo para a direita) vira a cabeça sem virar o corpo.

O olho gira em torno da base do pescoço, uns 19 cm para a frente e 22 cm para baixo. A cena posiciona a câmera com
`head_eye`:

```python
pitch = math.radians(-67)
cam.location = head_eye(olho_com_cabeca_reta, pitch, giro_da_cabeca, rumo_do_corpo)
```

Assim o corpo fica no mesmo lugar. Sem `head_eye`, a câmera continua no alto e o corpo é
puxado para trás.

## Perfis (`outfits.py`)

| Perfil | Roupa | Calçado | Objetos |
|---|---|---|---|
| `sarajevo_civilian_1914` | Paletó de lã de três botões, punho de camisa, calça de terno | Botina de couro de amarrar | Relógio de bolso |
| `ww2_german_soldier` | Sobretudo M40 feldgrau de duas fileiras, punho virado, cinto; luvas de tricô | Bota de marcha | Kar98k |
| `ww2_soviet_soldier` | Telogreika e calça acolchoadas, cinto de couro, sem platinas | Bota de kirza | Mosin-Nagant 91/30 |

As incertezas históricas de cada perfil ficam em `notes`. Para criar um perfil novo, copie
um deles e troque as estações (cortes ao longo do corpo), as cores e o calçado.

## Arquivos

| Arquivo | O quê | Blender? |
|---|---|---|
| `skeleton.py` | Medidas, frames dos ossos, IK de dois ossos, dedos | não |
| `motion.py` | Marcha, poses de ação, agenda, corpo a partir da câmera | não |
| `geometry.py` | Gaiolas procedurais (mãos, mangas, tronco, calça, calçado, fuzis, relógio) | não |
| `outfits.py` | Perfis como dados | não |
| `materials.py` | Lã, acolchoado, tricô, pele, couro, madeira, metal | sim |
| `character.py` | Cria as peças, faz o skinning a cada frame, segue a câmera | sim |
| `fuse.py` | Fusão da mão numa superfície contínua (Geometry Nodes) | sim |
| `inspect.py` | Imagens de inspeção (estúdio e câmeras reais) | sim |
| `selftest.py` | Determinismo, vínculo, enquadramento, isolamento | sim |

A cabeça e o chapéu existem só para a sombra no chão: não aparecem na câmera.

## Mãos fundidas e textura presa à pele

A mão (palma, dedos, polegar e antebraço) é uma gaiola de tubos; um modificador Geometry Nodes
(`fuse.py`) a converte em volume e de volta em malha a cada frame, com voxel de 0,8 mm e
suavização leve. Os dedos saem da palma sem emenda e o punho fica contínuo. Toda peça guarda as
coordenadas de repouso no atributo `pov_rest`; a pele usa esse atributo como coordenada de
textura, então manchas e poros não escorregam quando os dedos dobram e não há costura de UV.

```bash
tools/blender/blender -b -P engine/pov/selftest.py
tools/blender/blender -b -P engine/pov/inspect.py -- studio ww2_soviet_soldier
tools/blender/blender -b -P engine/pov/inspect.py -- real sarajevo_civilian_1914 intro
VIDEO=26-pov-stalingrado tools/blender/blender -b -P engine/pov/inspect.py -- real ww2_german_soldier t1
```

As imagens saem em `render/pov-inspect/<perfil>/`; com `POV_INSPECT_DIR=v2`, em
`render/pov-inspect/v2/<perfil>/` (para não sobrescrever inspeções anteriores).
