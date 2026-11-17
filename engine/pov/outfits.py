"""Perfis de personagem: roupa, calçado, cores e objetos de cada época, como dados.

Cores em sRGB 0..1 (convertidas para linear nos materiais). Medidas em metros, no espaço do
corpo (ver skeleton.py). As estações de cada peça são cortes ao longo do corpo:
- tronco: (z, meia-largura, meia-profundidade, deslocamento do centro em y)
- manga: (distância a partir do ombro, raio lateral, raio frontal)
- calça: (z, raio)

Incertezas históricas ficam em 'notes', em vez de precisão inventada.
"""

JACKET_1914 = [
    (0.70, 0.186, 0.132, 0.000), (0.80, 0.181, 0.124, 0.000), (0.93, 0.171, 0.117, 0.005),
    (1.05, 0.166, 0.114, 0.012), (1.18, 0.176, 0.120, 0.015), (1.30, 0.188, 0.124, 0.012),
    (1.37, 0.212, 0.112, 0.004), (1.415, 0.205, 0.095, -0.004), (1.45, 0.150, 0.076, -0.010),
    (1.50, 0.074, 0.062, -0.010),
]
GREATCOAT_M40 = [
    (0.36, 0.275, 0.225, 0.000), (0.52, 0.240, 0.190, 0.000), (0.72, 0.212, 0.158, 0.000),
    (0.93, 0.195, 0.140, 0.005), (1.03, 0.184, 0.134, 0.012), (1.18, 0.194, 0.136, 0.015),
    (1.30, 0.206, 0.137, 0.012), (1.37, 0.226, 0.124, 0.004), (1.42, 0.215, 0.105, -0.004),
    (1.47, 0.160, 0.088, -0.010), (1.53, 0.092, 0.078, -0.010),
]
TELOGREIKA = [
    (0.73, 0.203, 0.150, 0.000), (0.84, 0.198, 0.144, 0.000), (0.95, 0.190, 0.138, 0.005),
    (1.05, 0.187, 0.136, 0.012), (1.18, 0.193, 0.138, 0.015), (1.30, 0.202, 0.138, 0.012),
    (1.37, 0.224, 0.124, 0.004), (1.415, 0.212, 0.102, -0.004), (1.46, 0.155, 0.084, -0.010),
    (1.51, 0.086, 0.072, -0.010),
]

SLEEVE_1914 = [(0.0, 0.044, 0.048), (0.05, 0.058, 0.058), (0.17, 0.055, 0.053), (0.27, 0.051, 0.050),
               (0.33, 0.050, 0.049), (0.43, 0.047, 0.045), (0.51, 0.044, 0.042), (0.555, 0.043, 0.041)]
SLEEVE_GREATCOAT = [(0.0, 0.052, 0.056), (0.05, 0.066, 0.066), (0.17, 0.062, 0.061), (0.27, 0.058, 0.057),
                    (0.33, 0.057, 0.056), (0.43, 0.055, 0.053), (0.51, 0.054, 0.052), (0.575, 0.054, 0.052)]
SLEEVE_TELOGREIKA = [(0.0, 0.054, 0.058), (0.05, 0.069, 0.068), (0.17, 0.066, 0.064), (0.27, 0.061, 0.059),
                     (0.33, 0.060, 0.058), (0.43, 0.056, 0.054), (0.51, 0.051, 0.049), (0.56, 0.046, 0.044)]

TROUSERS_1914 = [(1.00, 0.104), (0.90, 0.094), (0.75, 0.082), (0.60, 0.068), (0.49, 0.061),
                 (0.38, 0.058), (0.25, 0.057), (0.14, 0.058), (0.075, 0.060)]
TROUSERS_GERMAN = [(1.00, 0.108), (0.90, 0.098), (0.75, 0.086), (0.60, 0.072), (0.49, 0.066),
                   (0.43, 0.068), (0.40, 0.064), (0.36, 0.055)]
TROUSERS_QUILTED = [(1.00, 0.118), (0.90, 0.108), (0.75, 0.096), (0.60, 0.082), (0.49, 0.076),
                    (0.43, 0.077), (0.40, 0.070), (0.36, 0.057)]

PROFILES = {
    'sarajevo_civilian_1914': {
        'label': 'Civil em Sarajevo, junho de 1914',
        'torso': {'stations': JACKET_1914, 'fabric': 'jacket', 'front': 'single', 'quilt': None,
                  'buttons': [(1.17, 0.0), (1.07, 0.0), (0.97, 0.0)], 'collar': 'lapel'},
        'sleeve': {'stations': SLEEVE_1914, 'fabric': 'jacket', 'turnback': False,
                   'cuff_buttons': 3, 'quilt': None},
        'shirt_cuff': True,
        'trousers': {'stations': TROUSERS_1914, 'fabric': 'trousers', 'quilt': None, 'tucked': False},
        'footwear': 'ankle_boot',
        'hat': 'homburg',
        'gloves': False,
        'belt': None,
        'rifle': None,
        'colors': {
            'jacket': (0.19, 0.165, 0.14), 'trousers': (0.19, 0.165, 0.14), 'shirt': (0.88, 0.86, 0.80),
            'leather': (0.055, 0.047, 0.042), 'sole': (0.075, 0.06, 0.05), 'button': (0.11, 0.085, 0.065),
            'skin': (0.76, 0.585, 0.49), 'metal': (0.78, 0.76, 0.72),
        },
        'leather_rough': 0.36,
        'notes': [
            'Terno de passeio de lã escura (paletó curto, de três botões, com colete), comum entre '
            'homens urbanos da Europa Central em 1914. O tom exato e a padronagem (liso, espinha de '
            'peixe, risca) variavam; usamos marrom-acinzentado liso.',
            'Botina de couro de amarrar, de cano curto, era o calçado masculino mais comum; o sapato '
            'baixo (oxford) também existia. Ficamos com a botina.',
            'O chapéu (homburg, chapéu-coco, palheta ou fez, em Sarajevo) nunca aparece no POV; '
            'existe só como volume simples para a sombra no chão (usamos o homburg).',
            'O relógio de bolso é um objeto da época plausível, não um detalhe documentado da cena.',
        ],
    },
    'ww2_german_soldier': {
        'label': 'Soldado alemão (Heer), Stalingrado, novembro de 1942',
        'torso': {'stations': GREATCOAT_M40, 'fabric': 'coat', 'front': 'double', 'quilt': None,
                  'buttons': [(z, x) for z in (1.27, 1.15, 1.08, 0.93, 0.82, 0.71) for x in (-0.06, 0.06)],
                  'collar': 'coat'},
        'sleeve': {'stations': SLEEVE_GREATCOAT, 'fabric': 'coat', 'turnback': True,
                   'cuff_buttons': 0, 'quilt': None},
        'shirt_cuff': False,
        'trousers': {'stations': TROUSERS_GERMAN, 'fabric': 'trousers', 'quilt': None, 'tucked': True},
        'footwear': 'jackboot',
        'hat': 'stahlhelm',
        'gloves': True,
        'belt': {'z': 1.03, 'color': 'belt'},
        'rifle': 'kar98k',
        'colors': {
            'coat': (0.33, 0.345, 0.30), 'trousers': (0.31, 0.32, 0.29), 'glove': (0.34, 0.34, 0.32),
            'leather': (0.045, 0.043, 0.042), 'sole': (0.05, 0.045, 0.04), 'button': (0.30, 0.31, 0.27),
            'belt': (0.05, 0.048, 0.046), 'skin': (0.76, 0.585, 0.49),
            'wood': (0.36, 0.19, 0.10), 'steel': (0.075, 0.075, 0.08),
        },
        'leather_rough': 0.55,
        'notes': [
            'Sobretudo M40 de lã feldgrau, de duas fileiras de seis botões, com punho virado, usado '
            'sobre a Feldbluse. A partir de 1940 a gola deixou de ser verde-escura; a cor real variou '
            'muito entre lotes (do cinza-esverdeado ao acinzentado).',
            'Calça de lã feldgrau enfiada na bota de marcha (Marschstiefel) de couro preto. Em 1942 o '
            'cano já tinha sido encurtado e parte da tropa usava botina com polaina; mantivemos a bota alta.',
            'Luvas de tricô cinza eram distribuídas; o uniforme de inverno acolchoado reversível '
            'só chegou em quantidade no inverno de 1942-43 e não foi usado aqui.',
            'Fuzil Kar98k com coronha de nogueira ou de madeira laminada (as duas existiam em 1942).',
        ],
    },
    'ww2_soviet_soldier': {
        'label': 'Soldado soviético (Exército Vermelho), Stalingrado, novembro de 1942',
        'torso': {'stations': TELOGREIKA, 'fabric': 'quilted', 'front': 'single', 'quilt': 0.065,
                  'buttons': [(1.30, 0.0), (1.19, 0.0), (1.08, 0.0), (0.97, 0.0), (0.86, 0.0)],
                  'collar': 'stand'},
        'sleeve': {'stations': SLEEVE_TELOGREIKA, 'fabric': 'quilted', 'turnback': False,
                   'cuff_buttons': 0, 'quilt': 0.06},
        'shirt_cuff': False,
        'trousers': {'stations': TROUSERS_QUILTED, 'fabric': 'quilted_trousers', 'quilt': 0.07, 'tucked': True},
        'footwear': 'kirza_boot',
        'hat': 'ushanka',
        'gloves': False,
        'belt': {'z': 1.04, 'color': 'belt'},
        'rifle': 'mosin',
        'colors': {
            'quilted': (0.38, 0.35, 0.23), 'quilted_trousers': (0.36, 0.33, 0.22),
            'leather': (0.07, 0.062, 0.055), 'sole': (0.06, 0.05, 0.045), 'button': (0.10, 0.10, 0.09),
            'belt': (0.30, 0.19, 0.10), 'skin': (0.76, 0.585, 0.49),
            'wood': (0.40, 0.20, 0.09), 'steel': (0.075, 0.075, 0.08),
        },
        'leather_rough': 0.6,
        'notes': [
            'Telogreika (jaqueta acolchoada de algodão) e calça acolchoada (vatnye sharovary) cáqui. '
            'O pesponto do corpo é vertical; nas mangas, o desenho variava entre fabricantes e '
            'usamos linhas ao longo da manga.',
            'Sem platinas: as dragonas (pogony) só voltaram com o decreto de janeiro de 1943.',
            'Bota de kirza (couro artificial). Valenki (botas de feltro) e botina com perneira '
            '(obmotki) também foram muito usadas em Stalingrado; o perfil escolhe a kirza.',
            'Fuzil Mosin-Nagant 1891/30 com ferrolho de alavanca reta. Mãos nuas: as luvas de três '
            'dedos existiam, mas a distribuição era irregular.',
        ],
    },
}
