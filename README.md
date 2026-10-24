# fragpunk-assets

Icônes extraites de FragPunk pour alimenter [FragTracker](https://github.com/RyusAceVA/studio)
(projet fan, non officiel). Les assets appartiennent à Bad Guitar Studio / NetEase —
aucune redistribution commerciale.

Structure (miroir de `FragPunkApi/data/images/`) :

```
lancers/portraits/    portraits des Lancers
lancers/skins_icon/   icônes des skins de Lancers
```

Les fichiers sont servis via `https://raw.githubusercontent.com/RyusAceVA/fragpunk-assets/main/...`
et ajoutés automatiquement par `studio/scripts/sync-fragpunk.mjs` (voir `studio/scripts/SYNC.md`).

## FarLands (mode à venir, patch du 22/10/2026)

Tout le contenu du mode FarLands trouvé dans les fichiers du jeu : voir **[FARLANDS.md](FARLANDS.md)**
(base de connaissances) et `farlands/data/farlands.json` (index machine, URLs absolues).

```
farlands/images/        4 539 images d'interface (écrans, menus, icônes)
farlands/videos/        cinématiques mp4
farlands/models/        160 modèles 3D .glb (web, textures KTX2) + _apercus/
farlands/maps/          aperçus des cartes reconstruites
farlands/textes/        textes FR/EN (.json + .tsv), dont _tous_les_textes_du_jeu.tsv
data/patches/           nouveautés par patch (codes, noms vérifiés, statut)
```
