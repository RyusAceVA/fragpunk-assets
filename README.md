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

## Site FarLands Leaks (`site/`)

Site statique (HTML, CSS, JS sans framework) qui présente le mode FarLands, avec le style de
FragTracker. Tous les textes du jeu cités viennent de `farlands/textes/_tous_les_textes_du_jeu.tsv`,
avec un badge qui renvoie à leur ligne dans l'explorateur de textes.

```
site/index.html        page du mode (histoire, Hub 9, mécaniques, monde, factions, bestiaire...)
site/galerie.html      galerie d'images
site/modeles.html      visionneuse des modèles 3D (model-viewer)
site/textes.html       explorateur du fichier de textes (FR/EN)
site/data/*.json       données générées depuis le TSV
site/img/              vignettes WebP générées
tools/build_site.py    génère site/data et site/img
```

Les vidéos, les modèles 3D, les PNG d'origine et le TSV ne sont pas copiés dans `site/` : le site les lit
dans ce dépôt via jsDelivr (repli sur raw.githubusercontent).

- **En local** : `python3 -m http.server 8000` à la racine du dépôt, puis ouvrir `http://localhost:8000/site/`.
- **Régénérer** les données et les vignettes (Python 3, Pillow, ffmpeg en option pour les affiches des vidéos) : `python3 tools/build_site.py`
  (`--no-img` pour ne refaire que les JSON).
- **Mise en ligne** : le workflow `.github/workflows/pages.yml` publie `site/` sur GitHub Pages à chaque
  push sur `main`. À activer une fois dans *Settings → Pages → Source : GitHub Actions*.
