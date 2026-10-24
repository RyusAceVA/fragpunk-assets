#!/usr/bin/env python3
"""Génère les données et les images optimisées du site FarLands (dossier site/).

Toutes les citations du jeu viennent de farlands/textes/_tous_les_textes_du_jeu.tsv :
chaque texte est retrouvé par sa clé (colonne `cle`) et garde sa source (table + clé),
pour que n'importe quelle phrase du site puisse être vérifiée dans le fichier.

Usage, depuis la racine du dépôt :
    python3 tools/build_site.py            # données + images
    python3 tools/build_site.py --no-img   # données seulement

Dépendances : Python 3.9+, Pillow (images WebP), ffmpeg (affiches des vidéos, optionnel).
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FL = os.path.join(ROOT, 'farlands')
IMG = os.path.join(FL, 'images')
SITE = os.path.join(ROOT, 'site')
OUT_DATA = os.path.join(SITE, 'data')
OUT_IMG = os.path.join(SITE, 'img')
TSV = os.path.join(FL, 'textes', '_tous_les_textes_du_jeu.tsv')

HL = 'AtlasTexture/HappyLand/'
ICON = 'AtlasTexture/Icon_HL/'


# --------------------------------------------------------------------------
# Textes du jeu
# --------------------------------------------------------------------------

csv.field_size_limit(10 ** 9)
ROWS = list(csv.DictReader(open(TSV, encoding='utf-8-sig'), delimiter='\t'))
BY_TABLE = defaultdict(list)
for _r in ROWS:
    BY_TABLE[_r['table'][:8]].append(_r)

TAG_RE = re.compile(r'<[^<>]*>')
CJK_RE = re.compile(r'[一-鿿]')


def clean(s):
    """Retire le balisage du jeu (<HL_rare_Thin>…</>, <bgtext …/>) et normalise les retours."""
    if not s:
        return ''
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    s = TAG_RE.sub('', s)
    return s.strip()


def one_line(s):
    return re.sub(r'\s*\n\s*', ' ', s).strip()


# VF manifestement erronée (texte d'une autre ligne, contresens, marqueur de développement) :
# on la retire pour afficher la VO à la place.
BAD_FR_RE = re.compile(r'^(Quête (principale|secondaire) [\d-]+|Description de la Carte de test|\(Aucun paramètre)')
BAD_FR_KEYS = {'8DB489', 'AA5368', 'B059CF', '1381E5'}


def pack(r, single_line=False):
    en, fr = clean(r['anglais']), clean(r['francais'])
    if BAD_FR_RE.match(fr) or r['cle'][:6] in BAD_FR_KEYS:
        fr = ''
    if single_line:
        en, fr = one_line(en), one_line(fr)
    t = {'en': en, 'fr': fr or None, 's': r['table'][:8] + ':' + r['cle'][:8]}
    if en and len(CJK_RE.findall(en)) > len(en) * 0.3:  # la VO de quelques tables n'existe qu'en chinois
        t['zh'] = en
        t['en'] = None
    return t


DIALOGUE_TABLES = ['F4D9BDFB', 'B0AA0F74', '18CD45A0', 'D140F70D', '8C967057']


def T(key, table=None, single_line=False):
    """Texte du jeu par préfixe de clé (et de table si la clé est ambiguë)."""
    hits = [r for r in (BY_TABLE[table] if table else ROWS) if r['cle'].startswith(key)]
    if not table and len({h['table'] for h in hits}) > 1:  # préfixe partagé : tables de dialogues d'abord
        for pref in DIALOGUE_TABLES:
            sub = [h for h in hits if h['table'].startswith(pref)]
            if sub:
                hits = sub
                break
    if not hits:
        raise KeyError(f'clé introuvable : {table}:{key}')
    if len({h['table'] for h in hits}) > 1 or len(hits) > 1 and len({h['anglais'] for h in hits}) > 1:
        raise KeyError(f'clé ambiguë : {key} ({[h["table"][:8] for h in hits]})')
    return pack(hits[0], single_line)


def E(table, en, single_line=True):
    """Texte du jeu par son anglais exact, dans une table."""
    for r in BY_TABLE[table]:
        if one_line(clean(r['anglais'])) == en:
            return pack(r, single_line)
    raise KeyError(f'texte introuvable : {table}:{en}')


# --------------------------------------------------------------------------
# Contenu éditorial : chaque entrée pointe vers une clé du TSV
# --------------------------------------------------------------------------

QUOTES = {
    # Pitch et ton
    'pitch': ('102953', '3A7D2308'), 'free': ('48A42E', 'B2C67F7B'), 'patch': ('3ED9B2', 'B2C67F7B'),
    'mission1': ('F546C2', 'F4D9BDFB'), 'nolancers': ('7BDB45', '3A7D2308'),
    'factions_choice': ('49D7D4', None),
    # Lieux clés
    'hub9': ('8B2C02', '847EA848'), 'fringe': ('040EDF', '847EA848'), 'seaside': ('9A760F', '847EA848'),
    # Lore général
    'lore_eastvale': ('96B604', 'E05105A1'), 'lore_kepler': ('4B037A', 'E05105A1'),
    'lore_lancers': ('01CEB5', 'E05105A1'), 'lore_5years': ('47CE80', 'E05105A1'),
    'lore_sharks': ('665C9D', 'E05105A1'),
    # Journey et la radio du premier jour
    'journey_intro': ('67279D', 'D140F70D'), 'journey_hq': ('57F547', 'D140F70D'),
    'journey_home': ('B70755', None), 'journey_route': ('A57D79', None), 'journey_reports': ('639178', '29936457'),
    'journey_lost': ('4DB8E8', 'B2C67F7B'), 'journey_goose': ('939324', None),
    'radio_signal': ('1E48D2', 'D140F70D'), 'radio_border': ('912A1E', 'D140F70D'),
    'radio_unstable': ('DC75EE', 'D140F70D'), 'radio_crash': ('649190', None),
    'radio_cargo': ('A631DF', 'D140F70D'), 'radio_wait': ('C6AB91', 'D140F70D'),
    'radio_town': ('A7EB50', 'D140F70D'), 'radio_saved': ('98BEA5', 'D140F70D'),
    'radio_snow': ('38D0A4', None),
    # Tutoriel « First Delivery »
    'tuto_badluck': ('2AB906', '8C967057'), 'tuto_snow': ('38EA0E', '8C967057'),
    'tuto_wolves': ('6BB7E4', '8C967057'), 'tuto_cliff': ('E009F0', '8C967057'),
    'tuto_woods': ('0A6DFD', '8C967057'), 'tuto_missing': ('37618D', '8C967057'),
    'tuto_recipient': ('9C090A', '8C967057'), 'tuto_tricked': ('1E0F07', '8C967057'),
    'tuto_kill': ('93B205', '8C967057'), 'tuto_ostrich': ('40518E', '8C967057'),
    'tuto_town': ('26DA60', '8C967057'), 'tuto_chief': ('6333D9', '8C967057'),
    'tuto_death': ('2B0F2F', '8C967057'), 'tuto_crouch': ('E82057', '8C967057'),
    'tuto_backpack': ('AD40A3', '8C967057'), 'tuto_slope': ('9C337A', '8C967057'),
    'tuto_weather': ('C7A7D0', '8C967057'), 'tuto_cargo_drop': ('2A014D', '8C967057'),
    'tuto_100': ('751FD9', '8C967057'), 'tuto_climb': ('78E9B9', '8C967057'),
    'trial_done': ('A7BACA', None), 'tower_done': ('89D4A2', None),
    # Mécaniques
    'perf_intro': ('49120E', 'B52D586F'), 'perf_effect': ('0D7AD7', 'B52D586F'),
    'perf_restore': ('5D5FCA', 'B52D586F'), 'mag_intro': ('448456', 'B52D586F'),
    'mag_adv': ('C5B106', 'B52D586F'), 'mag_recover': ('5B75AC', 'B52D586F'),
    'hud_load': ('440366', 'B52D586F'), 'load': ('444A33', '18981A43'),
    'balance': ('370E0E', '18981A43'), 'health': ('5D06E8', '18981A43'),
    'magnet': ('0FA648', '18981A43'), 'extract': ('BFE2B0', '565E8907'),
    'outpost_s': ('141D6A', '565E8907'), 'outpost_m': ('024174', '565E8907'),
    'outpost_l': ('4B1E91', '565E8907'), 'weather_hurt': ('19061D', None),
    'weather_retreat': ('687AB5', None), 'revive': ('EE05AF', 'B52D586F'),
    'mag_empty': ('9EF3A8', None), 'energy_bridge': ('6BC60E', '4BA0791A'),
    'backpack_layers': ('19693B', '4BA0791A'), 'drone': ('38AF7A', '4BA0791A'),
    'secured_box': ('AC63FE', '9F94063E'),
    # Hub 9
    'stars_intro': ('383E31', '29936457'), 'star_official': ('28DF66', '29936457'),
    'star_three': ('1D9D88', '29936457'), 'star_perms': ('7B5145', '29936457'),
    'register': ('29D49C', None), 'scan_face': ('AAE180', None),
    'order_system': ('028556', '18CD45A0'),
    # Kit du coursier (descriptions d'objets)
    'kit_uniform': ('089F91', '4BA0791A'), 'kit_helmet': ('21E06B', '4BA0791A'),
    'kit_gloves': ('0E2A72', '4BA0791A'), 'kit_legs': ('12AF4D', '4BA0791A'),
    'kit_boots': ('4D1F97', '4BA0791A'), 'kit_box': ('6EB29D', '4BA0791A'),
    'kit_scooter': ('1337CE', '4BA0791A'), 'kit_drink': ('394A1C', '4BA0791A'),
    # Personnages
    'scav_king': ('4C9DF0', 'EF241178'), 'serket': ('A6CC94', 'B0AA0F74'),
    'kemet_great': ('CD3187', 'B0AA0F74'), 'little_king': ('100187', None),
    # Événements de lancement
    'backpack_need': ('9EC1D9', '786A41C5'), 'challenge': ('C44D42', '629EC458'),
    'challenge_search': ('910011', 'D4CE5F38'), 'challenge_kill': ('AA4570', 'D4CE5F38'),
    'ev_prereg': ('AD3EEB', 'B2C67F7B'), 'ev_prehype': ('2BA425', 'B2C67F7B'),
    'ev_team': ('76698A', 'B2C67F7B'), 'ev_twitch': ('41D8E7', 'B2C67F7B'),
    'ev_squad': ('1699B9', 'B2C67F7B'), 'ev_bp': ('4A57CD', 'B2C67F7B'), 'ev_mail': ('572EFC', 'B2C67F7B'),
}

MERCHANTS = [
    {'id': 'oldjoe', 'name': 'Old Joe', 'role': ('7D3695', '832AD19C'), 'img': None,
     'lines': [('DBF202', '18CD45A0')]},
    {'id': 'pathojen', 'name': 'Pathojen', 'role': ('40DEFB', '832AD19C'), 'img': 'lancer-pathojen',
     'lines': [('FA740D', '18CD45A0'), ('1BC8F4', '18CD45A0')]},
    {'id': 'hollowpoint', 'name': 'Hollowpoint', 'role': ('8FD0AF', '832AD19C'), 'img': 'lancer-hollowpoint',
     'lines': [('E6DED6', '18CD45A0'), ('692966', '18CD45A0')]},
    {'id': 'broker', 'name': 'Broker', 'role': ('E0C910', '832AD19C'), 'img': 'lancer-broker',
     'lines': [('C0F20A', '18CD45A0'), ('5C1E1A', '18CD45A0')]},
    {'id': 'nitro', 'name': 'Nitro', 'role': ('en:Vehicle Merchant', '4DF3C170'), 'img': 'lancer-nitro',
     'lines': [('D5551A', '18CD45A0'), ('3D4D7B', '18CD45A0')]},
    {'id': 'journey', 'name': 'Journey', 'role': ('AE8825', '832AD19C'), 'img': None,
     'lines': [('F54231', '18CD45A0'), ('B70755', None)]},
]

FACILITIES = [  # (nom, description, image de l'écran de niveau du hub)
    (('CA2E03', '08074106'), ('FB8371', '08074106')),
    (('F9BDA9', '08074106'), ('2B4952', '08074106')),
    (('9D6578', '08074106'), ('5CC15D', '08074106')),
    (('3E97D0', '08074106'), ('0B04FB', '08074106')),
    (('47F263', '08074106'), ('FACF46', '08074106')),
    (('34528E', '08074106'), ('B4EBD8', '08074106')),
    (('25C4F2', '08074106'), ('74EE1F', '08074106')),
    (('ADE14B', '08074106'), ('9A84BC', '08074106')),
    (('D9124C', '08074106'), ('F9828E', '08074106')),
    (('83AA47', '08074106'), ('4409DD', '08074106')),
]

HUB_SCREENS = ['HL_LevelUp_Bg_%s' % n for n in
               ('1_1', '1_2', '2_1', '3_1', '4_1', '4_2', '5_1', '6_1', '7_1', '7_2', '8_1', '9_1', '10_1')]

HUB_PERKS = [  # icône, texte (table F05CD3BC sauf mention)
    ('ConcurrentOrderLimitBoost', '11990F'), ('WarehouseCapacityBoost', '04260F'),
    ('DismantleFeeDiscount', '1A906A'), ('DismantleRarityLimitBoost', '9A12A5'),
    ('WeaponTierUp', '15F541'), ('EquipmentTierUp', '0CC46B'),
    ('UnlockNewOrderType', '5DBF3D'), ('VehicleLimitBoost', '44544E'),
    ('RandomOrderLimitBoost', 'AF83B8'), ('RandomOrderValueBoost', '4B03B2'),
    ('PerpetualOrderValue', '8DB489'), ('SelfListingQuoteLimitBoost', '0B2B3B'),
    ('TacticalTrainingRoom', 'D9124C:08074106'), ('LevelUpReward', 'E0682C'),
]

RARITIES = [('common', 'A7B3D2'), ('rare', '1C753A'), ('superb', '16E5BD'),
            ('extreme', '0235AA'), ('ultimate', '1423A4')]

ORDER_TYPES = [  # nom (VO chinoise), description (VO chinoise), nom anglais (table F05CD3BC)
    ('9F689E', None, '298E06'),
    ('B90B18', '746858', '91034B'),
    ('A1869A', '933BCA', 'FDA40A'),
    ('C27ACA', 'CE132D', 'C176BE'),
    ('235C8B', '4247ED', '2977DE'),
    ('C2E53F', '527239', 'C4F8CD'),
]
EXTRA_ORDERS = ['8DB489', 'D021DB', '1964E7']  # Perpetual, Automatic packing, Random orders

CUSTOMERS = [('AAEBAC', '9EF2F6'), ('264A29', '9D6CFC'), ('CB53C2', 'AD2C56'),
             ('B711C0', 'FBD85B'), ('E9DDE4', 'C19B16'), (None, 'CF1627')]  # « Bon samaritain » n'a pas de description

MARKET = [  # (clé table 2707679E, icône HL_InGameMap)
    ('700526', 'HL_Map_SupplyShortage'), ('6A1CD6', 'HL_Map_SupplyAbundant'),
    ('12A665', 'HL_Map_PriceHigh'), ('57D329', 'HL_Map_PriceLow'), ('71A27B', 'HL_Map_PriceStable'),
    ('FE0792', 'HL_Map_HarvestFestival'), ('3CE877', 'HL_Map_WeatherAlert'),
    ('25F815', 'HL_Map_RareMerchant'), ('632ED0', 'HL_Map_GreedyMerchant'),
    ('174D3C', 'HL_Map_KindMerchant'), ('06C19B', 'HL_Map_StockFull'), ('A434D7', 'HL_Map_StockLow'),
]

WEATHER = [  # (nom, description éventuelle) table 3D9D6F0B ; description associée d'après le sens
    ('Sunny Day', 'Temperature and humidity are both stable, and wind speed has not changed.'),
    ('Light Rain', None), ('Heavy Rain', None), ('Downpour', None), ('Heavy fog', None),
    ('Windy', None), ('Gale', None),
    ('Hurricane', 'The wind is extremely strong, with falling temperatures and rising humidity'),
    ('Lightning Storm', 'A noticeable drop in temperature, a sharp rise in humidity, and Magnetism will be deducted.'),
    ('Frost Storm', 'The temperature drops sharply, the air is cold and dry, and Frost Storm stacks'),
    ('Extreme Cold', 'The temperature drop is getting worse, and staying outdoors for long periods is dangerous.'),
    ('Flame Storm', 'The temperature rises sharply and the air becomes extremely dry, continuously accumulating Firestorm'),
    ('Radiation Storm', 'The air is extremely dry, the temperature rises sharply, and Radiation Storm stacks'),
    ('Dust Tornado', 'Temperatures rise during the day and drop at night. Humidity increases slightly, winds grow stronger, and sandstorm'),
    ('Miasma Environment', 'The temperature will Go down, the air will become humid, and miasma Environment stacks'),
    ('Earthquake', 'Does not participate in the weather cycle.'),
]

TRAINING = [  # icône, nom, description (table 18981A43)
    ('Vitality', '1006A9', '5D06E8'), ('HP', '3283BA', 'F33AF1'), ('HPRecovery', 'D28D1A', 'E296EE'),
    ('Armor', '3A5D86', '2140D6'), ('AllResistance', '029F93', 'E88849'), ('Impact', '89C0BF', '1A242A'),
    ('Stagger', 'F2D904', '370E0E'), ('Fall', '594FFD', 'FAF812'), ('Magnetism', '2583CF', '0FA648'),
    ('CarryWeight', '776CFF', '444A33'), ('Backpack', 'D21B5A', '993A93'), ('Search', 'D2A6BE', '197139'),
    ('Climb', 'F6FFB3', '2570C4'), ('Wade', 'F09D5C', '65F87D'), ('MoveSpeed', 'F9320B', '1303D6'),
    ('Repair', 'A61583', None), ('Vehicle', 'A63E59', 'FA87A9'), ('Gather', '2C979A', '4F4614'),
]
TRAINING_CATS = ['D82265', '0B3E32', '8D6D82', 'E57E62']  # table CA8AA539

VEHICLES = [  # nom (62E6FB5F), image probable (d'après le visuel), certitude
    ('EFB110', 'VEH02002', True), ('B3BAAD', 'VEH02001', True), ('8E748F', 'VEH03009', True),
    ('6DBFED', 'VEH04003', True), ('EB812B', 'VEH03002', False), ('5CDDC4', 'VEH03003', False),
]
VEHICLE_STATS = ['1733CC', 'A4F107', '88A886', '08655A', 'ADA8B4', 'AC2439', '6E51C3']
VEHICLE_PARTS = [('2A1E36', 1), ('F0FE6F', 2), ('32AD82', 3), ('F6E41F', 4), ('4B4ED8', 5),
                 ('0F5200', 6), ('34485E', 7), ('FE4B12', 8), ('4FAABC', 9), ('FEA518', 10)]

ZONES = [
    {'id': 'hub', 'name': ('2A7F7B', '847EA848'), 'desc': ('8B2C02', '847EA848'), 'img': 'zone-hub',
     'tag': 'Base'},
    {'id': 'fringe', 'name': ('3CAA1B', '847EA848'), 'desc': ('040EDF', '847EA848'), 'img': 'zone-fringe',
     'tag': 'Chapitre 1'},
    {'id': 'seaside', 'name': ('54A5CF', '847EA848'), 'desc': ('9A760F', '847EA848'), 'img': 'zone-seaside',
     'tag': 'Chapitre 2'},
    {'id': 'dunes', 'name': ('0C139A', 'E404DF58'), 'desc': None, 'img': 'zone-dunes', 'tag': 'Désert'},
    {'id': 'arena', 'name': ('0C1D20', '847EA848'), 'desc': None, 'img': 'zone-arena', 'tag': 'Boss'},
]

LOCATIONS = [  # (zone, faction, clé du nom, clé de la description) table B5A8B521
    ('fringe', 'scavengers', 'D1D533', '8E8662'), ('fringe', 'kepler', '8F29C9', '26A30D'),
    ('fringe', 'kepler', 'EF9656', '4CD2DE'), ('fringe', 'kepler', '967E72', '91E7DC'),
    ('fringe', 'scavengers', '1742B5', '9F067D'), ('fringe', 'scavengers', '4B92F5', '7BD19F'),
    ('fringe', 'kepler', '080889', 'FF3351'), ('fringe', 'kepler', '2B4001', '4345E5'),
    ('fringe', 'scavengers', 'C81C50', '23580A'), ('fringe', 'kepler', 'D8D5C5', '726AAD'),
    ('fringe', 'kepler', '959B46', 'FDFD40'), ('fringe', 'kepler', '3DAFCB', '75B8C4'),
    ('fringe', 'scavengers', '43CF54', '077CED'), ('fringe', 'kepler', '5BA8B1', 'EDD1D2'),
    ('fringe', 'scavengers', 'BB8F1A', '00F8B8'), ('fringe', 'kepler', '1FCF08', '6559A4'),
    ('fringe', 'kepler', '28EA42', '18BF17'), ('fringe', 'scavengers', '03BB5E', 'F664DD'),
    ('fringe', 'scavengers', 'F7A847', '4ADAD7'), ('fringe', 'scavengers', '5BA891', 'B8B2DD'),
    ('fringe', 'neutral', '9C2EE3', '22215E'),
    ('seaside', 'neutral', 'BEB6CA', 'BC4D1A'), ('seaside', 'mariana', 'A775B9', '8B9A61'),
    ('seaside', 'mariana', 'D99B1B', '179623'), ('seaside', 'chelae', '5CC0AA', '084EF2'),
    ('seaside', 'mariana', 'F0BACB', '3C18BF'), ('seaside', 'mariana', '22C738', '10C027'),
    ('seaside', 'mariana', 'A52190', 'A0BDD7'), ('seaside', 'mariana', '5F0C95', '95A4A7'),
    ('seaside', 'mariana', '4A6384', '2791E9'), ('seaside', 'neutral', 'D0059E', '7A7829'),
    ('seaside', 'mariana', '35C43E', 'CB1AB9'), ('seaside', 'neutral', '91904E', '2A4EFD'),
    ('seaside', 'chelae', '62AEA9', 'AD7902'), ('seaside', 'chelae', 'D5CE4C', 'CB6466'),
    ('seaside', 'chelae', '46EB06', '86CCC9'), ('seaside', 'chelae', '313094', 'A4CE23'),
    ('seaside', 'chelae', 'AA4692', 'BEAB9C'), ('seaside', 'chelae', '06F3BA', '4E3376'),
    ('seaside', 'chelae', '8EB9E4', '5A995F'), ('seaside', 'orcs', 'ED52B7', 'FEAE74'),
    ('seaside', 'orcs', 'CDA6DB', '9B84F8'), ('seaside', 'orcs', 'C7E988', '623426'),
    ('seaside', 'orcs', '4A6054', '742264'), ('seaside', 'orcs', '7C3AEE', 'BEB7BA'),
    ('seaside', 'dragon', '10E67F', '16E8A8'), ('seaside', 'dragon', '4CC570', '636B80'),
    ('seaside', 'neutral', '321E93', 'E5FD8E'), ('seaside', 'neutral', 'A27C1B', 'C931D7'),
    ('seaside', 'neutral', '59A5A7', '1A919B'), ('seaside', 'neutral', '747E08', '3C8988'),
    ('seaside', 'neutral', '0B13B3', '565065'), ('seaside', 'neutral', 'BE5AAC', '31ED16'),
    ('seaside', 'neutral', '531581', '92B8A4'),
]
REGION_OVERVIEWS = [  # descriptions générales de faction dans la table des régions
    ('kepler', '91DB1B'), ('scavengers', '4F6EAD'), ('mariana', '5D8D81'), ('chelae', 'A55D67'),
    ('orcs', '02A39B'), ('dragon', '6471C1'), ('neutral', '4E5CCA'),
]

FACTIONS = [  # id, nom, description (table 9FEE32F7), couleur, icône de carte probable
    ('kepler', '0F9C66', '06C698', '#00ffff'), ('scavengers', '9ECFBC', 'F1160C', '#ccff00'),
    ('mariana', 'AA5368', '3F9C75', '#3b82f6'), ('chelae', 'CFED47', '5F023E', '#ff00ff'),
    ('orcs', '050F29', 'E1AA2C', '#22c55e'), ('dragon', 'BACE53', '86C51D', '#ef4444'),
    ('aesir', 'CD8071', '700DA2', '#93c5fd'), ('boiler', '3AE728', 'C6873A', '#f97316'),
    ('kemet', '318BE8', 'A15915', '#eab308'), ('wild', '2A29CC', '98248A', '#a3a3a3'),
    ('neutral', '99E960', '15C577', '#ffffff'),
]

MONSTER_GROUPS = [  # regroupement d'après les noms (table EF241178)
    ('scavengers', ['Scavenger Marauder', 'Scavenger Butcher', 'Scavenger Shield', 'Scavenger Blaster']),
    ('kepler', ['Kepler Security Officer', 'Kepler Security Captain', 'Kepler Researcher',
                'Mutated Kepler Researcher', 'Sentry', 'Guardian', 'Sweeper', 'Bastion', 'Anvil',
                'Skyhook', 'Bomber', 'Purifier Construct', 'Stealth Assassin']),
    ('orcs', ['Orc Grunt', 'Orc Cannoneer', 'Orc Centurion', 'Orc Shieldbearer']),
    ('chelae', ['Chelae Infantry', 'Chelae Marksman', 'Chelae Tank', 'Chelae Broodmother']),
    ('mariana', ['Mariana Ruffian', 'Mariana Gunslinger', 'Mariana Guard', 'Siren', 'Cacharo Enforcer']),
    ('dragon', ['Mad Dragon Captain', 'Mad Dragon Martial Artist', 'Mad Dragon Knife Thrower',
                'Mad Dragon Training Dummy', 'Night Market Chef']),
    ('aesir', ['Aesir Soldier', 'Aesir Archer', 'Aesir Shieldbearer', 'Altered Aesir Soldiers',
               'Altered Aesir Archer', 'Altered Bjorn', 'Bloodfreezer']),
    ('boiler', ['Furnace Gang Arsonist', 'Furnace Gang Leader', 'Thermal Leaker']),
    ('kemet', ['Anger Luo Statue']),
    ('wild', ['Ice Pup', 'Ice Wolf', 'Ice Wolf King', 'Frost Cub', 'Frost Crystal Bear', 'Frost Bear King',
              'Doom Hatchling', 'Doom Lizard', 'Doom Lizard King', 'Mutant Wolf Cub', 'Mutant Wolf',
              'Mutant Wolf King', 'Wasteland Pup', 'Wasteland Dog', 'Wasteland Dog King',
              'Swift Leopard Cub', 'Swift Leopard', 'Swift Leopard King', 'Carrion Rat Pup', 'Rusted Rat',
              'Carrion Rat King', 'Zombie Cub', 'Zombie Bear', 'Zombie Bear King', 'Killer Crab',
              'Ash Larva', 'Ash Worm', 'Worker bee', 'Snowblind Stalker']),
    ('orbs', ['Cryogel Orb', 'Toxigel Orb', 'Infernogel Orb', 'Electrogel Orb']),
]
MONSTER_TYPES = ['F14F76', 'BDB7A1', '5DF847', 'D1EFE8', 'C5289A', '1C7177', '9B3B0C']  # 232D4902

STORY = [  # chapitre 0 : la première livraison
    {'title': 'Le crash', 'video': 'CT_Ch00_Vid_01_720',
     'q': ['tuto_badluck', 'radio_crash', 'radio_cargo']},
    {'title': 'Les montagnes enneigées', 'video': 'CT_Ch00_Vid_02_720',
     'q': ['tuto_snow', 'tuto_wolves', 'radio_snow']},
    {'title': 'La falaise', 'video': None, 'q': ['tuto_cliff', 'tuto_climb']},
    {'title': 'La forêt rouge', 'video': 'CT_Ch00_Vid_03_720', 'q': ['tuto_woods']},
    {'title': 'Le colis perdu', 'video': 'CT_Ch00_Vid_04_720', 'q': ['tuto_missing', 'tuto_chief']},
    {'title': 'Le destinataire mystère', 'video': 'CT_Ch00_Vid_05_720',
     'q': ['tuto_recipient', 'tuto_tricked', 'tuto_kill']},
    {'title': 'Embuscade', 'video': 'CT_Ch00_Vid_06_CN_720', 'q': ['radio_wait']},
    {'title': "Tutu, l'autruche robot", 'video': None, 'q': ['tuto_ostrich', 'journey_intro', 'journey_hq']},
    {'title': 'Arrivée au Hub 9', 'video': None, 'q': ['tuto_town', 'radio_saved', 'trial_done', 'tower_done']},
]

CHAPTERS = [  # suite de l'histoire : titres de quêtes (table A9F9E3E7) et répliques
    {'zone': 'fringe', 'quests': ['The Disaster of Harmony Town', 'Restarting the Signal Tower',
                                  'Scavenger Scourge', 'The Source of the Disaster', "Kepler's Cleanup",
                                  'RECAPTURE Line 9', 'The Surviving Miner'],
     'lines': ['396ED6', '65A5C6', '4229A3']},
    {'zone': 'seaside', 'quests': ['Arriving in Akhet', 'The Two Seaside Factions', 'Enemy of the Chelae',
                                   'Evidence of the Chelae', 'Chelae Suspicions', 'Blood Feud',
                                   'The Source of Hatred', 'Enemies of Mariana', 'Slay the Dragon',
                                   'Mad Dragon Mystery', 'Becoming a Leader', 'War Drums'],
     'lines': ['831FBE', '26201E', 'B4D124', '98FAFB', '0123DB', 'AFF600', '47FD25', '89AF55']},
]

QUEST_GROUPS = [  # préfixes de titres de quêtes de PNJ
    ('Old Joe', 'Old Joe:'), ('Broker', 'Broker:'), ('Pathojen', 'Pathojen:'), ('Journey', 'Journey:'),
    ('Nitro', 'Please, Nitro!'),
]
QUEST_PRACTICE = ['Climbing Practice 1', 'Zipline Practice 1', 'Slide Practice 1', 'Dodge Roll Practice 1',
                  'Vehicle Practice 1', 'Heavy Load Lesson 1', 'Recovery Training 1', 'Fully Loaded 1']

DOCS = [  # documents de lore liés au mode (table 87F72AE9) : (clé du corps, titre donné par le site)
    ('3A8624', 'Publicité : Eastvale Logistics'), ('132F8F', 'Dossier secret Eastvale n° 1'),
    ('2A6B4E', 'Dossier secret Eastvale n° 2'), ('AB2415', 'Rapport d\'Eastvale sur Kepler'),
    ('21AB51', 'Enquête : Mariana et sa civilisation'), ('6E2B4E', 'Enquête : les Chelae'),
    ('3A1B2A', 'Communication interceptée'), ('5B2935', 'Enquête : Aesir'),
    ('BAA6E8', 'Enquête : Yggdrasil et la Toundra'),
]

NPC_DIALOGUES = ['A94624', '9A6775', '3D1005', '4400D6', '6C79C8', 'DFB9EF', '769B89', '90EA95',
                 '85C5E3', 'C4ECCA', 'D4D059', '426CB6', '100187', '38BF2A', '1637C3', 'F2210F',
                 'C54C1E', '9D3AFD', 'AB1C40', '05032F']

NPC_NAMES = ['Merchant Big Hat', 'Middleman Big Pincers', 'Lead Vocal: Siren', 'Trading Officer 7 Pairs',
             'Hedonist Lady', 'Caretaker No. 21', 'Bodyguard Thresher Shark', 'Miser Avare',
             'Peace Envoy Paz', 'Scholar Tiye', 'Gravekeeper Silver Scale', 'Shark Dad',
             'Serket, Master of Deserts', 'Little Scavenger King', 'Lawyer White Gloves',
             'Fisherman Santiago', 'Captain Jack', 'Blacksmith Nehet', 'Guitarist Kachinos',
             'Drummer Andrew', 'Translator Xiao Sanyuan', 'Foodie Liangzi', 'Fitness Star Graytusk',
             'Engineer Kroz', 'Master Scrounger Digsby Digs Three Feet Deep', 'Collector Colette',
             'Scientist Mardon', 'Angler Pat', 'Artisan Taka', 'Merchant One-Eyed', 'Merchant Collector',
             'Merchant Scavenger', 'Thief Vaulting Horse', 'Watcher Sotus', 'Lookout Eren',
             'Sailor Ishmael', 'Water Sailor Gibbs', 'Harvester Mogrim', 'Miner Anna', 'Devout Iside']

SETS_FEATURED = ['Eastvale Combat Set', 'Damaged Delivery Set', "Scavenger King's Set", 'Kepler Security Set',
                 'Kepler Blizzard Set', 'Chelae Invader Set', 'Chelae Samurai Set', 'Mad Dragon Assassin Set',
                 'Orcish Plunder Set', 'Luminous Scaled Set', 'Boiler Core Set', 'Aesir Draugr Set',
                 'Prisoner Set', 'Cowboy Set', 'Thorny Nurse Set', 'Fire Salamander Set']
SET_BONUS_EXAMPLES = ['306FFC', 'DD3A95', '9A136B', '3393A7', '15D7D8', 'AEC951', '3DE0C5', 'EC2280',
                      '798624', '856B23', 'E87633', '93D7BC']

# Tables FarLands proposées dans l'explorateur de textes, avec un libellé lisible
CORPUS = [
    ('847EA848', 'Zones'), ('E404DF58', 'Cartes'), ('B5A8B521', 'Lieux'), ('9FEE32F7', 'Factions'),
    ('EF241178', 'Monstres'), ('232D4902', 'Types de monstres'), ('2C6B45C0', 'Affixes de monstres'),
    ('74C9AD90', 'Armes des monstres'), ('4C14E649', 'Armes des monstres'),
    ('4DF3C170', 'PNJ et points d\'intérêt'), ('F4D9BDFB', 'Dialogues'), ('18CD45A0', 'Dialogues de PNJ'),
    ('B0AA0F74', 'Répliques de PNJ'), ('35103BB1', 'Ambiance des factions'),
    ('C1244260', 'Goûts des PNJ (cadeaux)'), ('A3AA7416', 'Réactions aux cadeaux'),
    ('D140F70D', 'Radio du premier jour'), ('8C967057', 'Tutoriel'), ('A9F9E3E7', 'Quêtes'),
    ('87F72AE9', 'Documents (lore)'), ('E05105A1', 'Lore'), ('B52D586F', 'Astuces et mécaniques'),
    ('5DA760B1', 'Perfection'), ('3D9D6F0B', 'Météo'), ('F05CD3BC', 'Améliorations du hub'),
    ('29936457', 'Étoiles du hub'), ('08074106', 'Installations du hub'), ('BAD087CA', 'Actions du hub'),
    ('18981A43', 'Entraînement'), ('CA8AA539', 'Catégories d\'entraînement'),
    ('57B8A26D', 'Types de commandes'), ('522AD18A', 'Personnalités des clients'),
    ('2707679E', 'Événements du marché'), ('62E6FB5F', 'Véhicules'), ('33A91FA5', 'Stats des véhicules'),
    ('59DD60E7', 'Pièces de véhicules'), ('8F8957D9', 'Équipement'), ('C3BA5F4E', 'Ensembles'),
    ('4BA0791A', 'Objets'), ('635867E7', 'Ressources'), ('E63354A7', 'Minerais'),
    ('5C6F1BF1', 'Catégories d\'objets'), ('BB136235', 'Catégories d\'objets'),
    ('9407C103', 'Catégories d\'objets'), ('A281C17A', 'Conteneurs'), ('9F94063E', 'Boîtes sécurisées'),
    ('3E60692C', 'Inventaire'), ('48E4E6D0', 'Marqueurs de carte'), ('565E8907', 'Marqueurs de carte'),
    ('832AD19C', 'Marqueurs de carte'), ('238AE4FB', 'Interactions'), ('C2ACA3E4', 'Pings'),
    ('E7825245', 'Messages système'), ('B63BCA40', 'Rangs'), ('3E00766F', 'Rangs'),
]


def build_data():
    q = {}
    for qid, (k, t) in QUOTES.items():
        q[qid] = T(k, t)

    merchants = []
    for m in MERCHANTS:
        merchants.append({
            'id': m['id'], 'name': m['name'], 'img': m['img'],
            'role': E(m['role'][1], m['role'][0][3:]) if m['role'][0].startswith('en:') else T(*m['role'], single_line=True),
            'lines': [T(k, t) for k, t in m['lines']],
        })

    facilities = [{'name': T(*n, single_line=True), 'desc': T(*d)} for n, d in FACILITIES]

    perks = []
    for icon, key in HUB_PERKS:
        k, _, t = key.partition(':')
        perks.append({'icon': 'perk-' + icon, 'text': T(k, t or 'F05CD3BC', single_line=True)})

    rarities = [{'id': r, 'name': T(k, 'F05CD3BC', single_line=True)} for r, k in RARITIES]
    stars = [{'name': T(k, '29936457', single_line=True), 'img': f'star-{i + 1}'}
             for i, k in enumerate(['CE294A', '8771E2', '365568', '48910E', '4009CF'])]

    orders = []
    for name_k, desc_k, en_k in ORDER_TYPES:
        orders.append({'name': T(name_k, '57B8A26D', True), 'en': T(en_k, 'F05CD3BC', True),
                       'desc': T(desc_k, '57B8A26D') if desc_k else None})
    extra_orders = [T(k, 'F05CD3BC', True) for k in EXTRA_ORDERS]
    customers = [{'desc': T(d, '522AD18A') if d else None, 'name': T(n, '522AD18A')} for d, n in CUSTOMERS]
    market = [{'name': T(k, '2707679E', True), 'icon': 'market-' + icon[7:]} for k, icon in MARKET]

    weather = []
    for name, desc in WEATHER:
        item = {'name': E('3D9D6F0B', name)}
        if desc:
            for r in BY_TABLE['3D9D6F0B']:
                if r['anglais'].startswith(desc):
                    item['desc'] = pack(r)
                    break
            else:
                raise KeyError(desc)
        weather.append(item)

    training = [{'icon': 'train-' + i, 'name': T(n, '18981A43', True),
                 'desc': T(d, '18981A43') if d else None} for i, n, d in TRAINING]
    training_cats = [T(k, 'CA8AA539', True) for k in TRAINING_CATS]

    vehicles = [{'name': T(k, '62E6FB5F', True), 'img': 'veh-' + code, 'code': code, 'sure': sure}
                for k, code, sure in VEHICLES]
    vehicle_stats = [T(k, '33A91FA5', True) for k in VEHICLE_STATS]
    vehicle_parts = [{'name': T(k, '59DD60E7', True), 'icon': 'vehmod-%02d' % i} for k, i in VEHICLE_PARTS]

    zones = [{'id': z['id'], 'tag': z['tag'], 'img': z['img'], 'name': T(*z['name'], single_line=True),
              'desc': T(*z['desc']) if z['desc'] else None} for z in ZONES]
    locations = [{'zone': z, 'faction': f, 'name': T(n, 'B5A8B521', True), 'desc': T(d, 'B5A8B521')}
                 for z, f, n, d in LOCATIONS]
    overviews = {f: T(k, 'B5A8B521') for f, k in REGION_OVERVIEWS}

    factions = [{'id': i, 'name': T(n, '9FEE32F7', True), 'desc': T(d, '9FEE32F7'), 'color': c,
                 'overview': overviews.get(i)} for i, n, d, c in FACTIONS]

    monster_groups = [{'faction': f, 'names': [E('EF241178', n) for n in names]} for f, names in MONSTER_GROUPS]
    monster_types = [T(k, '232D4902', True) for k in MONSTER_TYPES]
    scav = {'name': E('EF241178', 'Scavenger King: Rust-Faced Brutus'), 'desc': T('4C9DF0', 'EF241178')}

    story = [{'title': s['title'], 'video': s['video'], 'q': s['q']} for s in STORY]
    for s in story:
        for qid in s['q']:
            assert qid in q, qid

    chapters = []
    for c in CHAPTERS:
        chapters.append({'zone': c['zone'], 'quests': [E('A9F9E3E7', n) for n in c['quests']],
                         'lines': [T(k) for k in c['lines']]})

    quest_titles = {one_line(clean(r['anglais'])) for r in BY_TABLE['A9F9E3E7']}
    npc_quests = []
    for who, prefix in QUEST_GROUPS:
        names = sorted(n for n in quest_titles if n.startswith(prefix))
        npc_quests.append({'who': who, 'quests': [E('A9F9E3E7', n) for n in names]})
    practice = [E('A9F9E3E7', n) for n in QUEST_PRACTICE]
    bounties = sorted({re.sub(r' \d+$', '', n)[len('Bounty: '):] for n in quest_titles if n.startswith('Bounty: ')})

    docs = [{'title': title, 'body': T(k, '87F72AE9')} for k, title in DOCS]

    npc_lines = [T(k) for k in NPC_DIALOGUES]
    npc_names = [E('4DF3C170', n) for n in NPC_NAMES]

    set_names = sorted({one_line(clean(r['anglais'])) for r in BY_TABLE['C3BA5F4E']
                        if r['anglais'].endswith('Set')})
    sets = [E('C3BA5F4E', n) for n in set_names]
    sets_featured = [E('C3BA5F4E', n) for n in SETS_FEATURED]
    set_bonus = [T(k, 'C3BA5F4E') for k in SET_BONUS_EXAMPLES]

    fl = json.load(open(os.path.join(FL, 'data', 'farlands.json'), encoding='utf-8'))
    videos = [{'id': v['id'], 'file': 'farlands/videos/%s.mp4' % v['id'], 'duration': v['duration_s'],
               'desc': v['description'], 'poster': 'video-' + v['id']} for v in fl['videos']]

    data = {
        'generated': fl['generated'], 'patch': fl['game_patch'], 'mode': fl['mode'],
        'counts': fl['counts'], 'disclaimer': fl['disclaimer'],
        'quotes': q, 'story': story, 'chapters': chapters, 'videos': videos,
        'merchants': merchants, 'facilities': facilities, 'hub_screens': HUB_SCREENS, 'perks': perks,
        'rarities': rarities, 'stars': stars, 'orders': orders, 'extra_orders': extra_orders,
        'customers': customers, 'market': market, 'weather': weather, 'training': training,
        'training_cats': training_cats, 'vehicles': vehicles, 'vehicle_stats': vehicle_stats,
        'vehicle_parts': vehicle_parts, 'zones': zones, 'locations': locations, 'factions': factions,
        'monster_groups': monster_groups, 'monster_types': monster_types, 'scavenger_king': scav,
        'npc_quests': npc_quests, 'practice': practice, 'bounties': bounties, 'docs': docs,
        'npc_lines': npc_lines, 'npc_names': npc_names, 'sets': sets, 'sets_featured': sets_featured,
        'set_bonus': set_bonus,
    }
    return data, fl


def build_corpus():
    """Corpus de l'explorateur : textes FarLands dédoublonnés, [table, anglais, français, clé]."""
    labels = {}
    out = []
    for table, label in CORPUS:
        labels[table] = label
        seen = set()
        for r in BY_TABLE[table]:
            en, fr = clean(r['anglais']), clean(r['francais'])
            if not en and not fr:
                continue
            if (en, fr) in seen:
                continue
            seen.add((en, fr))
            out.append([table, en, fr, r['cle'][:8]])
    return {'labels': labels, 'rows': out}


def build_models(fl):
    groups = {'monstres': 'Monstres', 'armes': 'Armes', 'pnj': 'PNJ', 'vehicules': 'Véhicules',
              'tenues': 'Tenues', 'corps': 'Corps'}
    items = []
    for m in fl['models']:
        rel = m['url'].split('/main/', 1)[1]
        size = os.path.getsize(os.path.join(ROOT, rel))
        items.append({'id': m['id'], 'group': m['group'], 'file': rel, 'size': size,
                      'thumb': 'models/%s__%s' % (m['group'], m['id'])})
    return {'groups': groups, 'items': items}


# --------------------------------------------------------------------------
# Galerie : dossiers d'images présentés sur la page galerie
# --------------------------------------------------------------------------

GALLERY = [  # (id, titre, dossier, filtre, largeur de vignette)
    ('ecrans', 'Écrans de chargement', 'LargeTexture/HappyLand', None, 640),
    ('mondes', 'Mondes et décors', HL + 'HL_Task_Order', r'HL_NewTask_0[23]|HL_NewTask_36|HL_Task_Season_(Main|Sub)_Bg', 640),
    ('zones', 'Sélection de zone', HL + 'HL_PreWar', r'HL_Select_Map_(Bg|New)|HL_Prewar_SmallMap|HL_Prewar_New2_Bg', 480),
    ('hub', 'Installations du Hub 9', HL + 'HL_LevelUp/LevelBg', None, 640),
    ('coursier', 'Création du coursier', HL + 'HL_BodySelection', r'_(0[2-7]|1[0-8]|32)$', 480),
    ('tenues', 'Tenues complètes', HL + 'HL_SkinSuit/200x310BigIcon', None, 200),
    ('tutoriel', 'Tutoriel en images', HL + 'HL_Tutorial', None, 800),
    ('commandes', 'Commandes et clients', HL + 'HL_Task_Order/Order_NPC_Icon', None, 380),
    ('emballage', 'Emballage des colis', HL + 'HL_Packup', r'AnimationBg|Result|SlotMachine|LittleBox', 640),
    ('vehicules', 'Véhicules', ICON + 'Icon_VEH', None, 408),
    ('garage', 'Garage et modifications', HL + 'HL_Vehicle', r'HL_MachineM_13|VehNew_08|HL_VehModIcon|VEH0', 480),
    ('armes', 'Armes (rendus)', ICON + 'Icon_WeaponShow', None, 320),
    ('plans', 'Plans de fabrication', ICON + 'icon_Blueprint', r'Icon_Blueprint', 256),
    ('etoiles', 'Étoiles du hub et niveaux', HL + 'HL_Station', r'HL_StarUpgrade_Level_\d|HL_Task_Season_Sub_Bg2', 256),
    ('carte', 'Icônes de la carte', HL + 'HL_InGameMap', r'HL_Map_(Forces|Price|Greedy|Kind|Rare|Harvest|Stock|Supply|Weather)', 96),
    ('evac', 'Fin de partie', HL + 'HL_Settlement', r'Loadin|Result_(Win|Lost)_Bg3', 480),
]


GALLERY_SKIP = {'HL_loading_Bg1'}  # trait de pinceau d'interface, pas une illustration


def list_gallery():
    out = []
    for gid, title, folder, rx, w in GALLERY:
        d = os.path.join(IMG, folder)
        files = []
        for root, _, fs in os.walk(d):
            for f in sorted(fs):
                if not f.endswith('.png'):
                    continue
                name = f[:-4]
                if (rx and not re.search(rx, name)) or name in GALLERY_SKIP:
                    continue
                rel = os.path.relpath(os.path.join(root, f), ROOT).replace(os.sep, '/')
                files.append({'name': name, 'file': rel, 'thumb': 'gal/%s/%s' % (gid, name)})
        files.sort(key=lambda x: x['name'])
        out.append({'id': gid, 'title': title, 'width': w, 'items': files})
    return out


# --------------------------------------------------------------------------
# Images optimisées (WebP)
# --------------------------------------------------------------------------

def img_jobs(gallery, models):
    j = []  # (source absolue, sortie relative à site/img sans extension, largeur max, qualité)

    def add(src, out, w, q=80):
        j.append((src if os.path.isabs(src) else os.path.join(IMG, src), out, w, q))

    hero = 'LargeTexture/Base_Activity/Activity_S6/S62_HLActivity.png'
    add(hero, 'hero', 2400, 82)
    add(hero, 'hero-sm', 1100, 80)
    add('LargeTexture/Agent/Draw_208002010.png', 'courier-art', 1400, 82)
    for n in ['HL_Loading_5230001', 'HL_Loading_5230301', 'HL_Loading_BossLevel_325325', 'HL_Toturial_Loading',
              'HL_loading_Bg1', 'HL_loading_Bg2', 'HL_loading_Bg3', 'HL_Select_Map_New2_Bg', 'HappyLand_World_Map']:
        add('LargeTexture/HappyLand/%s.png' % n, 'load/' + n, 1600, 80)
    add(HL + 'HL_PreWar/HL_Select_Map_Bg_EdgeSector.png', 'zone-fringe', 1400)
    add(HL + 'HL_PreWar/HL_Select_Map_Bg_CoastalPort.png', 'zone-seaside', 1400)
    add(HL + 'HL_PreWar/HL_Select_Map_Bg_SandLand.png', 'zone-dunes', 1400)
    add('LargeTexture/HappyLand/HL_Loading_BossLevel_325325.png', 'zone-arena', 1400)
    add(HL + 'HL_Task_Order/Task_Season/Task_Season_19.png', 'zone-hub', 1400)  # remplacé plus bas si besoin
    add(HL + 'HL_Station/HL_Task_Season_Sub_Bg2.png', 'hub-interior', 1600)
    add(HL + 'HL_Task_Order/HL_NewTask_02.png', 'world-islands', 1600)
    add(HL + 'HL_Task_Order/HL_NewTask_36.png', 'world-sunset', 1600)
    add(HL + 'HL_Task_Order/HL_Task_Season_Main_Bg.png', 'world-forest', 1600)
    add(HL + 'HL_Settlement/HL_Settlement_Loadin_Bg.png', 'tex-delivery', 1600, 70)
    add(HL + 'HL_ModeSelection/HL_ModeSelection_05.png', 'tex-graffiti', 1600, 70)
    add(HL + 'HL_Settlement/HL_Settlement_Loadin_Deco.png', 'settlement-folder', 700)
    add(HL + 'HL_Packup/HL_Packup_AnimationBg.png', 'packup-bg', 1400)
    add(HL + 'HL_Packup/HL_Packup_Result.png', 'packup-result', 1400)
    add(HL + 'HL_Vehicle/HL_MachineM_13.png', 'garage-craft', 1400)
    add(HL + 'HL_Vehicle/Veh_New/VehNew_08.png', 'garage-new', 1400)
    add(HL + 'HL_BodySelection/HL_Bodytype_Selection_04.png', 'body-graffiti', 1400)
    add(HL + 'HL_BodySelection/HL_Bodytype_Selection_32.png', 'fdh-box', 500)
    add(HL + 'HL_PreWar/HL_Server_New2_Boss_Bg.png', 'esv-banner', 524)
    add(HL + 'HL_PreWar/HL_Server_New2_Bg2.png', 'esv-hub9', 524)
    add(ICON + 'Icon_Cangobox/Icon_Cangobox01_0023.png', 'eastvale-sphere', 256)
    add(HL + 'HL_Vehicle/VEH02001.png', 'journey', 224)
    for i in range(1, 4):
        add(HL + 'HL_Tutorial/HL_Tutorial_Guide%d.png' % i, 'tuto-%d' % i, 1600)
    for i in range(10, 14):
        add(HL + 'HL_BodySelection/HL_Bodytype_Selection_%d.png' % i, 'body-%d' % i, 500)
    for i in range(1, 7):
        add(HL + 'HL_Station/HL_StarUpgrade_Level_%d.png' % i, 'star-%d' % i, 256)
    for n in HUB_SCREENS:
        add(HL + 'HL_LevelUp/LevelBg/%s.png' % n, 'hub/' + n, 1000, 78)
    for icon, _ in HUB_PERKS:
        add(HL + 'HL_LevelUp/Level_Icon/HL_Levelup_%s_Icon.png' % icon, 'perk-' + icon, 120)
    for icon, _, _ in TRAINING:
        add(HL + 'HL_TrainingRoom/HL_TrainingRoom_New/Icon/HL_TrainingRoom_%s.png' % icon, 'train-' + icon, 164)
    for _, icon in MARKET:
        add(HL + 'HL_InGameMap/%s.png' % icon, 'market-' + icon[7:], 96)
    for _, code, _ in VEHICLES:
        add(ICON + 'Icon_VEH/Icon_%s.png' % code, 'veh-' + code, 408)
    for _, i in VEHICLE_PARTS:
        add(HL + 'HL_Vehicle/VehMod/HL_VehModIcon_%02d.png' % i, 'vehmod-%02d' % i, 120)
    for f in sorted(os.listdir(os.path.join(IMG, HL + 'HL_SkinSuit/200x310BigIcon'))):
        add(HL + 'HL_SkinSuit/200x310BigIcon/' + f, 'suit/' + f[:-4], 200)
    for f in sorted(os.listdir(os.path.join(IMG, ICON + 'icon_Blueprint'))):
        if f.startswith('Icon_Blueprint'):
            add(ICON + 'icon_Blueprint/' + f, 'bp/' + f[:-4], 256)
    lan = os.path.join(ROOT, 'lancers', 'portraits', 'Icon_Lancers_Head01__H_%s.png')
    for name, code in [('courier', '208002010'), ('broker', '208001010'), ('nitro', '208004010'),
                       ('hollowpoint', '208008010'), ('pathojen', '208015010')]:
        add(lan % code, 'lancer-' + name, 228)
    for mp in ['HL_Lobby', 'HL_Chapter00']:
        d = os.path.join(FL, 'maps', mp)
        for f in sorted(os.listdir(d)):
            add(os.path.join(d, f), 'maps/%s/%s' % (mp, f[:-4]), 1000, 78)
    for g in gallery:
        for it in g['items']:
            add(os.path.join(ROOT, it['file']), it['thumb'], g['width'], 78)
    for it in models['items']:
        add(os.path.join(FL, 'models', '_apercus', it['thumb'].split('/', 1)[1] + '.png'), it['thumb'], 320, 78)
    return j


def make_images(jobs):
    from PIL import Image
    done = 0
    for src, out, w, q in jobs:
        dst = os.path.join(OUT_IMG, out + '.webp')
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im = Image.open(src)
        im.load()
        if im.mode not in ('RGB', 'RGBA'):
            im = im.convert('RGBA')
        if im.width > w:
            im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=q, method=4)
        done += 1
    print(f'images : {done} générées, {len(jobs)} au total')


def make_og():
    """Image d'aperçu pour les réseaux sociaux (JPEG, mieux reconnu que le WebP)."""
    from PIL import Image
    dst = os.path.join(OUT_IMG, 'og.jpg')
    if os.path.exists(dst):
        return
    im = Image.open(os.path.join(IMG, 'LargeTexture/Base_Activity/Activity_S6/S62_HLActivity.png')).convert('RGB')
    w, hgt = im.size  # recadrage 1200x630 centré sur le coursier
    crop_h = round(w * 630 / 1200)
    top = max(0, (hgt - crop_h) // 2)
    im = im.crop((0, top, w, top + crop_h)).resize((1200, 630), Image.LANCZOS)
    im.save(dst, 'JPEG', quality=84, optimize=True, progressive=True)


POSTER_AT = {  # moment de la vidéo (fraction de la durée) choisi pour l'affiche
    'CT_Ch00_Vid_01_720': .40, 'CT_Ch00_Vid_02_720': .10, 'CT_Ch00_Vid_03_720': .40,
    'CT_Ch00_Vid_04_720': .10, 'CT_Ch00_Vid_05_720': .10, 'CT_Ch00_Vid_06_CN_720': .55,
    'CT_Boss_Vid_115056_720': .55,
}


def make_posters(videos):
    if not shutil.which('ffmpeg'):
        print('ffmpeg absent : affiches des vidéos ignorées')
        return
    from PIL import Image
    for v in videos:
        dst = os.path.join(OUT_IMG, v['poster'] + '.webp')
        if os.path.exists(dst):
            continue
        tmp = dst + '.png'
        t = max(0.4, v['duration'] * POSTER_AT.get(v['id'], 0.45))
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(t), '-i',
                        os.path.join(ROOT, v['file']), '-frames:v', '1', tmp], check=True)
        im = Image.open(tmp).convert('RGB')
        if im.width > 960:
            im = im.resize((960, round(im.height * 960 / im.width)), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=78, method=6)
        os.remove(tmp)


def write_json(name, obj):
    os.makedirs(OUT_DATA, exist_ok=True)
    path = os.path.join(OUT_DATA, name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
    print(f'{name} : {os.path.getsize(path) / 1024:.0f} Ko')


def main():
    data, fl = build_data()
    corpus = build_corpus()
    models = build_models(fl)
    gallery = list_gallery()
    write_json('farlands.json', data)
    write_json('textes.json', corpus)
    write_json('modeles.json', models)
    write_json('galerie.json', gallery)
    if '--no-img' not in sys.argv:
        make_images(img_jobs(gallery, models))
        make_posters(data['videos'])
        make_og()


if __name__ == '__main__':
    main()
