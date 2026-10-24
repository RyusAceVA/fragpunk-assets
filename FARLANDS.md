# FarLands : tout ce que contiennent les fichiers du jeu

> Base de connaissances construite à partir des fichiers du patch FragPunk du **22/10/2026**
> (Saison 6 chapitre 2), comparés au dump du 27/08/2026. Projet fan non officiel : assets et textes
> © Bad Guitar Studio / NetEase. Au moment de l'extraction, FarLands **n'est pas encore sorti**.
>
> Données machine : [`farlands/data/farlands.json`](farlands/data/farlands.json) (index de tout le contenu, URLs absolues)
> et [`data/patches/2026-10-22.json`](data/patches/2026-10-22.json) (nouveautés du patch).

## Fiabilité des informations

| Niveau | Signification |
|---|---|
| **Officiel** | Annoncé sur [fragpunk.com](https://www.fragpunk.com/news/update/20261013/40588_1316523.html). |
| **Textes du jeu** | Lu tel quel dans les fichiers de traduction du patch (`farlands/textes/`). Fiable, mais le jeu peut encore changer avant la sortie. |
| **Fichiers** | Déduit des noms de fichiers, dossiers, images ou modèles. Fiable sur l'existence, pas sur le rôle exact. |
| **Non vérifié** | Hypothèse, signalée comme telle. |

## Le mode en bref

- **Nom** : FarLands (*officiel*). Nom interne dans les fichiers : **HappyLand**, préfixe `HL`.
- **Concept** : « expérience multijoueur à haut risque centrée sur la livraison » : prendre des commandes, se préparer, décider jusqu'où aller (*officiel*). Les fichiers montrent un mode d'**extraction** : point d'évacuation, stockage, butin, véhicules (*fichiers*).
- **Accès anticipé** : 5 novembre 2026 (*officiel*). Un événement « FarLands Challenge » est prévu : « Search 20 containers in FarLands mode », « Kill 5 monsters in FarLands mode » (*textes du jeu*).
- **Volume** : 76 823 fichiers ajoutés par le patch, dont la grande majorité pour ce mode (*fichiers*).

## Le personnage joueur : le coursier

- Le joueur incarne un **coursier en combinaison jaune** (visière-écran, sac de livraison « RO-1 », logo « ESV »). C'est le personnage des cinématiques et de l'artwork du « Lancer **C002** » (id 208002010) ajouté au roster (*fichiers*).
- Corps de base **HC002**, homme et femme, avec presets de visage et de coiffure (`FacePresets`) : création de personnage (*fichiers* : fenêtres `HL_FaceCustomization`, `HL_BodySelection`).
- **Tenues complètes** : HLCS3900, HLCS3901, HLCS3902, HLCS3903 (homme/femme) (*fichiers*).
- **Équipement modulaire** : 53 « Suits » (Suit10001 à Suit5xxxx), découpés en tête, torse, bras, mains, jambes et pieds, plus **83 sacs à dos** (*fichiers*). Exemples de noms : « Eastvale Standard Armguard », « East Valley Standard Equipment - Head » (*textes du jeu*, table `equipement`).
- **Lancers jouables dans le mode** : des versions FarLands de Broker (C001), Nitro (C004), Hollowpoint (C008) et Pathojen (C015) existent (`Char_Base`), ainsi qu'une fenêtre `HL_LancerSelection` (*fichiers*). Broker, Nitro et Sonar apparaissent aussi comme PNJ (*textes du jeu*).

## Le monde

### Zones de jeu (sélection de planète)

Écrans de sélection : **Coastal Port**, **Edge Sector**, **Sand Land**, plus 6 planètes (`HL_Select_Map_New_Map00` à `05`) et la notion de serveurs (`HL_Sel_Server_New`) (*fichiers*).

### Cartes

| Carte | Contenu | Source |
|---|---|---|
| **Lobby** (`HL_Lobby`) | Hub : plateforme en croix suspendue dans des câbles au-dessus des nuages, vaisseau, modules. | *fichiers* (reconstruit en 3D) |
| **Chapitre 0** (`HL_Chapter00`) | Ville dans un canyon (Town, TownHall, hôpital, quartier d'affaires, pont, camp, parc), tutoriel, vallée enneigée du crash. Terrain + 95 370 objets. | *fichiers* (reconstruit en 3D) |
| **Chapitre 3** (`HL_Chapter03_01`) | Monde ouvert de 444 tuiles de terrain ; camps de monstres : Orques, Hommes-poissons (*FishMan*), Gang du Dragon (*DragonGanster*), Crabes, Marché noir ; un bâtiment PvP. | *fichiers* (non reconstruit) |
| **Niveau de boss** (`HL_BossLevel_N115056`) | Forteresse de ferraille, avec sa cinématique. | *fichiers* |

### Lieux (extraits)

Avant-poste côtier, Zone urbaine principale, Avant-poste frontalier, Montagnes de la Frontière, Île d'Ombrelle,
Centrale photovoltaïque, Sommet des Nuages, Avant-poste des Orques, Raffinerie d'orques, Col des Orques,
Hôpital, Anneau du destin, Tunnel effondré, Cascade en forêt, Sentier périlleux du canyon, Os de dragon géant,
Ville abandonnée de Toyland, Chantier de recyclage, Bastion et Colonie des Chelae, Tas d'épaves abandonnées,
Nid du Dragon Furieux, Camp des Charognards, Ancien hôtel de ville, Désert, Marais boueux, Village de Mariana…
(*textes du jeu*, environ 90 lieux avec descriptions dans [`farlands/textes/regions_histoire.json`](farlands/textes/regions_histoire.json)).

Exemple de description : « Après le "deuxième Effondrement", les réfugiés exilés ont établi leur campement principal
à la périphérie de Ville fantôme. » (*textes du jeu*)

### Factions

Neutre · **Ases** (*Aesir*, peuple des montagnes glacées, technologies énergétiques et de chauffage) · **Orques** ·
**Kepler** (« entreprise technologique oligarchique ») · **Chelae** (faction de crustacés) · **Gang du Dragon Furieux** ·
**Charognards** (*Scavengers*) · **Gang du Fourneau** (*Boiler Gang*) · **Mariana** · **Kemet** · Faune sauvage
(*textes du jeu*, [`factions.json`](farlands/textes/factions.json)).

### Monstres (82 noms)

Soldat / Archer / Porteur de bouclier Aesir (et versions « altérées »), Grognard / Canonnier / Centurion orc,
Loup des glaces et son roi, Ours de cristal de givre et son roi, Lézard du destin et son roi, Loups mutants,
Chercheur Kepler muté, Agents et capitaine de sécurité Kepler, Fantassin / Tireur / Bouclier / Mère couvée Chelae,
Capitaine et guerriers du Dragon Fou, Charognards (maraudeur, cogneur, artilleur, bouclier),
**Roi des récupérateurs · Brutus au visage rouillé**, Crabe féroce, Orbes (cryogel, toxigel, gel enflammé),
Larve et Ver de cendre… (*textes du jeu*, [`monstres.json`](farlands/textes/monstres.json)).
Les modèles 3D sont codés `N1xxxxx` / `N2xxxxx` : 81 sont dans `farlands/models/monstres/`. La correspondance
nom ↔ code n'est **pas établie** (les tables du jeu qui la donnent sont chiffrées).

### PNJ (extraits)

Imprimante universelle, Le Fixeur Pinces, Chanteuse principale Siren, Vigie Allen, Officier de transaction 7 paires,
La Grande Dame des Plaisirs, Gardien n° 21, Garde du corps Requin exécuteur, Marchands (Grand Chapeau, Glaneur,
Collectionneur, le Borgne), Harpagon l'Avare, Messager de la paix Paz, Érudit Tiye, Gardien de tombe Écaille d'Argent,
Veilleur de nuit Sonar… (*textes du jeu*, [`pnj_noms.json`](farlands/textes/pnj_noms.json), dialogues dans `pnj_dialogues.json`).

## Systèmes de jeu (d'après les fenêtres d'interface et les textes)

- **Commandes et quêtes** : `HL_Order`, `HL_Task_Order`, 924 objectifs (« Repair the Signal Tower », « Obtain "Light Alloy" »…).
- **Livraison** : stations de livraison express (`HL_ExpressDeliveryStation`), transporteur (`HL_Carrier`), emballage des colis (`HL_Packup` + vidéo).
- **Économie** : stockage (`HL_Storage`), hôtel des ventes (`HL_Auction`), échange (`HL_Trade`), marchands, cours des marchandises sur la carte (prix haut/bas/stable, pénurie/abondance, marchand avide/aimable/rare, festival des récoltes, alerte météo).
- **Fabrication** : `HL_Craft`, plans (`icon_Blueprint`), démontage (`HL_Breakdown`), imprimante universelle.
- **Progression** : niveaux (`HL_LevelUp`), talents (`Hl_Talent`), base (`HL_Base`).
- **Véhicules** : garage, modifications (`HL_VehMod`), carburant et recharge (stations sur la carte), 16 véhicules en 5 familles (`VEH01` à `VEH05`).
- **Carte** : marqueurs (avant-postes petits/moyens/grands, **point d'évacuation**, tyroliennes horizontales/verticales, pont énergétique, chauffage/refroidisseur portables, panneaux « boss / danger / ravitaillement / piège »).
- **Autres** : donjons (`HL_Dungeon`), dôme écologique, avis de recherche, vol (`HL_Theft`), entraînement tactique, discussion avec les PNJ, cadeaux, chat vocal.

## Armes

Armes à feu `HLW0001` à `HLW0017` et armes de mêlée `HLMW0001` à `HLMW0017` : haches, épées, lances, arcs, arbalètes,
pistolets, fusils (*fichiers* ; 27 modèles dans `farlands/models/armes/`). Des skins d'armes de la série WS5xxx sont
propres au mode (WS5001, WS5101, WS5102, WS5201, WS5202, WS5301, WS5302, WS5401) (*fichiers*).

## Cinématiques

| Vidéo | Durée | Contenu (d'après les images) |
|---|---|---|
| CT_Ch00_Vid_01 | 41 s | Crash d'un vaisseau en flammes dans les montagnes |
| CT_Ch00_Vid_02 | 29 s | Le coursier traverse la neige avec sa caisse |
| CT_Ch00_Vid_03 | 35 s | Forêt aux feuillages rouges, de nuit |
| CT_Ch00_Vid_04 | 17 s | Récupération d'une caisse, vue sur la vallée |
| CT_Ch00_Vid_05 | 15 s | Rencontre avec un orc |
| CT_Ch00_Vid_06_CN | 52 s | Affrontement avec les orcs, explosion |
| CT_Boss_Vid_115056 | 24 s | Cinématique du niveau de boss |
| HL_Packup_AnimationVideo1 | 21 s | Chaîne automatisée d'emballage des colis |
| HL_Evacuate_Video | 1 s | Effet d'évacuation |

Fichiers : `farlands/videos/` (versions 720p).

## Nouveautés du patch hors FarLands

Détail et statut dans [`data/patches/2026-10-22.json`](data/patches/2026-10-22.json).

- **Zephyr CS3954 « Incomplete Shadow » / « Ombre inachevée »** : Superb, 5 variantes, « coming soon » (*officiel + textes du jeu*).
- **Axon CS3908 « Wasteland Rhapsody »** : Superb, 6 variantes, « coming soon » ; texte : « To Axon, the end of the world is merely the carnival stage he has always dreamed of » (*officiel + textes du jeu*).
- **WS3106 « Crimson Strike »** sur Couteau MW002, Discipline, Mad Dog-S, Highlife, Vicious : les 5 skins Superb du passe (*officiel + textes du jeu*).
- CS2922 sur Wildstyle, Spider, Calamity, Counterfeit, Sonar ; CS2919 (Hollowpoint) ; CS2920 (Hurricane) ; WS3136, WS2104, WS2101 ; charms GZ407 à GZ412 : **noms non identifiés** (le set CS2922 correspond probablement aux skins Rare « Graffiti Mischief » du passe, *non vérifié*).

## Contenu de ce dépôt

| Chemin | Contenu |
|---|---|
| `farlands/data/farlands.json` | Index complet : faits clés, images groupées par dossier (URLs), sélection d'images phares, vidéos, modèles, cartes, tables de textes. |
| `farlands/images/` | 4 539 images d'interface (écrans de chargement, menus, icônes de tenues, armes, véhicules, objets, plans, HUD, marqueurs). Structure = dossiers du jeu sous `UIWidgets/Textures/`. |
| `farlands/videos/` | 9 cinématiques en mp4. |
| `farlands/models/<groupe>/<id>.glb` | 160 modèles 3D texturés (tenues, corps, monstres, véhicules, PNJ, armes), compressés pour le web (textures KTX2 1024 px) ; miniatures dans `farlands/models/_apercus/`. |
| `farlands/maps/<carte>/` | Aperçus des cartes reconstruites en 3D (les fichiers Blender complets, trop lourds pour GitHub, restent hors dépôt). |
| `farlands/textes/*.json` + `.tsv` | Tables FarLands en anglais/français : lieux, factions, monstres, PNJ, dialogues, quêtes, marqueurs, documents, équipement, objets, conteneurs, bonus d'ensembles, messages. |
| `farlands/textes/_tous_les_textes_du_jeu.tsv` | Les 67 714 textes du jeu (colonnes `table`, `cle`, `anglais`, `francais`), pour vérifier n'importe quelle information. |
| `data/patches/2026-10-22.json` | Nouveautés du patch (codes, noms vérifiés, statut). |

Les modèles `.glb` utilisent des textures KTX2 : avec three.js, activer `KTX2Loader` ; `<model-viewer>` les lit directement.
