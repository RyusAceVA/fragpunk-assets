# FragPunk Data API — guide d'intégration

> **Ce fichier est autosuffisant : donne-le tel quel à une IA (ou un dev) pour
> construire un projet consommant ces données.** Aucun autre dossier n'est
> nécessaire pour un projet web/mobile classique.

Données extraites du jeu FragPunk (Bad Guitar Studio / NetEase). Projet fan non
officiel : ne pas monétiser, créditer « données FragPunk © NetEase », ne pas
redistribuer les archives du jeu.

## 1. API statique publique (recommandée — aucun serveur, aucune clé)

Base URL :

```
https://raw.githubusercontent.com/RyusAceVA/fragpunk-assets/main
```

CORS ouvert (`Access-Control-Allow-Origin: *`), cache CDN ~5 min. Mise à jour à
chaque patch du jeu via le pipeline du propriétaire.

### Endpoints JSON

| URL | Contenu |
|---|---|
| `/data/lancers.json` | Les 21 Lancers (personnages) et toutes leurs skins |
| `/data/armory.json` | Armes + leurs skins, charms, stickers, avatars, bannières, headwear, armwear |

### Forme de `lancers.json`

```json
{
  "lancers": [
    {
      "code": "C025",
      "name": "Calamity",
      "portrait": "https://raw.githubusercontent.com/RyusAceVA/fragpunk-assets/main/lancers/portraits/Icon_Lancers_Head01__H_208025010.png",
      "skins": [
        {
          "code": "CS1906",
          "name": null,
          "rarity": null,
          "icon": "https://raw.githubusercontent.com/.../lancers/skins_icon/Icon_Lancers_Roleskin_S5__C025_CS1906.png",
          "model": "https://raw.githubusercontent.com/.../lancers/models/C025/CS1906.glb"
        }
      ]
    }
  ]
}
```

Notes :
- `code` de skin `"Base"` = tenue par défaut. `model` est `null` si pas de 3D.
- `name`/`rarity` des skins sont souvent `null` : le jeu chiffre ces libellés.
  Les codes (`CSxxxx`) sont l'identifiant fiable.

### Forme de `armory.json`

```json
{
  "weapons":  [ { "code": "W004", "name": "Clampdown", "icon": "https://...png",
                  "skins": [ { "code": "WS0000", "name": null, "rarity": null, "icon": "https://...png" } ] } ],
  "charms":   [ { "id": "GZ345", "icon": "https://...png" } ],
  "headwear": [ { "id": "C009_TS002", "icon": "https://...png" } ],
  "armwear":  [ { "id": "C008_SS011", "icon": "https://...png" } ],
  "stickers": [ { "id": "ST386A", "icon": "https://...png" } ],
  "avatars":  [ { "id": "C001_01", "icon": "https://...png" } ],
  "banners":  [ { "id": "ACTIVITY01", "icon": "https://...png" } ],
  "ranks":    [ { "id": "Rank03", "icon": "https://...png" } ]
}
```

- Skin d'arme `WS0000` = skin par défaut de l'arme.
- Rangs : `Rank00`–`Rank09` = badges de tiers grand format (00 = non classé),
  `Rank0`–`Rank9` = petits formats, + variantes `Rank_Classic_*`/`Rank_Head_*`.
- Volumes : 43 armes / 713 skins, 337 charms, 731 stickers, 261 avatars,
  244 bannières, 96 headwear, 102 armwear, ~25 badges de rang,
  21 lancers / ~305 skins.

### Modèles 3D (.glb)

`lancers/models/<C0xx>/<CSxxxx|Base>.glb` — ~4 à 9 Mo chacun, optimisés web :
- géométrie **quantizée** (KHR_mesh_quantization), **PAS de compression meshopt/Draco** ;
- textures **KTX2 / BasisU** (KHR_texture_basisu), max 1024 px.

Compatibilité viewer :
- `<model-viewer>` (Google, web component) : fonctionne tel quel — recommandé.
  ```html
  <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js"></script>
  <model-viewer src="https://.../lancers/models/C025/CS1906.glb" camera-controls auto-rotate
                camera-orbit="180deg 82deg auto" style="width:100%;height:500px"></model-viewer>
  ```
- three.js : `GLTFLoader` + `KTX2Loader` (transcoder basis) obligatoire.
- Les modèles regardent vers l'arrière (export Unreal) : démarrer la caméra à
  `180deg` d'azimut.

### Images

Toutes les icônes référencées dans les JSON sont des PNG déjà hébergés (URLs
absolues dans les JSON). Arbo brute si besoin : `lancers/portraits/`,
`lancers/skins_icon/`, `lancers/art/` (affiches), `weapons/skins_icon/`,
`weapons/charms/`, `weapons/stickers/`, `cosmetics/{headwear,armwear,avatar_cards}/`.

## 2. API REST locale (optionnelle — pour un projet sur la machine du propriétaire)

Serveur ASP.NET Core en lecture seule sur les mêmes données, avec en plus les
cartes/minimaps et les artworks non publiés :

```bash
cd C:\Users\abdou\Documents\Coding\FModel\FragPunkApi\api\FragPunk.Api
dotnet run    # -> http://localhost:5000
```

| Endpoint | Contenu |
|---|---|
| `GET /v1/lancers`, `/v1/lancers/{code}` | Lancers + skins (icônes, .glb) |
| `GET /v1/weapons`, `/v1/weapons/{code}` | Armes + skins (icônes) |
| `GET /v1/charms`, `/v1/headwear`, `/v1/armwear` | Cosmétiques |
| `GET /images/...`, `GET /models/...` | Fichiers statiques |

CORS ouvert. Mêmes formes de données que l'API publique (casse camelCase).

## 3. Ce qui n'est PAS accessible aux projets tiers

- La base Firestore du site FragTracker (noms de skins saisis à la main,
  raretés, captures d'écran) : privée, réservée au site.
- Les archives du jeu et les extractions brutes (uasset, textures sources).

## 4. Conseils d'implémentation

- Télécharger les JSON au build ou les fetch au runtime — 102 Ko (lancers) et
  433 Ko (armory), parfaitement fetchables côté client.
- Mettre en cache côté app : les données ne changent qu'aux patchs du jeu.
- Pour filtrer les vraies armes à feu : codes `W###` (les `GW###`/autres sont
  des armes spéciales/melee).
- IDs stables dans le temps : `C0xx` (lancer), `CSxxxx` (skin lancer),
  `W0xx`/`WSxxxx` (arme/skin), `GZxxx` (charm), `STxxx` (sticker).
