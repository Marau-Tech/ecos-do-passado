# (take, duração, legendas [(início, fim, texto)])
from modelos import weather as MODELO
from modelos.weather import *

SHOTS = [
 ('ident', 2.0, []),
 ('map1', 7.0, [(0.3, 3.6, 'Good evening. Clear skies across the county tonight.'), (3.6, 7.0, 'Low of 41, light breeze from the west.')]),
 ('map2', 7.0, [(0.3, 3.4, 'One small system east of Marlow.'), (3.4, 7.0, 'It is moving against the wind.')]),
 ('sky1', 6.5, [(0.4, 3.3, 'Our sky cam can see it now.'), (3.3, 6.5, 'It is the brightest thing up there.')]),
 ('map3', 7.0, [(0.3, 3.5, 'It has already passed Elm Hollow.'), (3.5, 7.0, 'We have lost contact with Elm Hollow.')]),
 ('fc', 7.0, [(1.4, 4.2, 'The rest of the week looks clear.'), (4.2, 7.0, 'We do not have a forecast for Friday.')]),
 ('sky2', 9.2, [(0.4, 3.6, 'Keep your curtains closed tonight.'), (3.6, 7.6, 'Do not look up until Thursday.')]),
]
TOTAL, START, END_CARD = timing(SHOTS)

STATION = 'WKBR 58'
SHOW = 'WEATHER WATCH'
CLOCK = 23 * 3600 + 4 * 60
TEMP = '41°F'
TITLE = ('WEATHER WATCH', 'BRIDGEFORD COUNTY')
TITLES = {'sky1': ('LIVE', 'WKBR SKY CAM'), 'sky2': ('LIVE', 'WKBR SKY CAM'), 'fc': ('WEATHER WATCH', 'THIS WEEK')}

# posições no quadro de 960x720: precisam bater com o mapa renderizado
BRIDGEFORD, ELM, MARLOW = (300, 330), (560, 440), (660, 250)
CITIES = [(BRIDGEFORD, 'BRIDGEFORD', '41°'), (ELM, 'ELM HOLLOW', '40°'), (MARLOW, 'MARLOW', '39°')]
ROADS = [(BRIDGEFORD, ELM), (BRIDGEFORD, MARLOW), (ELM, MARLOW), (BRIDGEFORD, (60, 380)), (MARLOW, (900, 160)), (ELM, (700, 660))]
MAPS = {
 'map1': {'cities': CITIES, 'roads': ROADS},
 'map2': {'cities': CITIES, 'roads': ROADS, 'radar': [(830, 270, 46, 0.9)], 'sweep': True},
 'map3': {'roads': ROADS, 'cities': [(BRIDGEFORD, 'BRIDGEFORD', '41°'), (ELM, 'ELM HOLLOW', '--'), (MARLOW, 'MARLOW', '--')],
          'radar': [(ELM[0] + 10, ELM[1] - 6, 52, 1.0)], 'sweep': True},
}
FORECASTS = {'fc': [('MON', 'sun', '58°', '41°'), ('TUE', 'sun', '60°', '43°'), ('WED', 'cloud', '55°', '40°'),
                    ('THU', 'eye', '--', '--'), ('FRI', 'none', '', '')]}
FORECAST_HEAD = 'BRIDGEFORD COUNTY'

# glitch: (tempo global, força, duração)
EVENTS = [(START['map3'], 0.5, 0.2),             # a música para
          (START['sky2'], 0.4, 0.15),
          (END_CARD - 0.25, 0.8, 0.3)]
SUBLIM = []
SUBLIM_GRADE = 'scene'

VOICE = {'voice': 'am_adam', 'lang': 'en-us', 'speed': 1.0, 'fx': 'broadcast'}

GRADE = {'scene': (1.0, 1.03, (1.0, 1.0, 1.0), 0.0),
         'sky1': (0.9, 1.05, (0.95, 0.98, 1.06), 0.0), 'sky2': (0.9, 1.05, (0.95, 0.98, 1.06), 0.0)}

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    return a
