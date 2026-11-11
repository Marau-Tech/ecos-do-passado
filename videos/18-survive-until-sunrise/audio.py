from synth import *
from modelos.survive import sound
from timeline import SKIN_CFG

sound.night()

# a figura que ficou: um baque grave quando ela aparece
n = int(3.5 * SR); tv = np.arange(n) / SR
put(lp(rs.randn(n), 90, 4) * 9 * np.exp(-tv * 1.2) + np.sin(2 * np.pi * 41 * tv) * np.exp(-tv * 1.0) * 0.6,
    SKIN_CFG['stand'][0]['at'], 0.7)

sound.master()
finish()
