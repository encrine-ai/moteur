# Interroger iNaturalist pour l'imagier

Référence des paramètres et des recours, à lire quand une espèce résiste ou
qu'il faut écrire une requête à la main. Le fonctionnement courant est décrit
dans `SKILL.md` ; ici, le détail.

## Résoudre un nom scientifique en identifiant de taxon

`GET https://api.inaturalist.org/v1/taxa?q=<nom>&per_page=20&is_active=true`
`&rank=species,subspecies,variety,hybrid`

**Le filtre de rang n'est pas facultatif.** Sans lui, la recherche floue peut
ne rendre que du bruit : `q=Glis glis` — le loir — remontait une famille de
fougères, deux genres de graminées et la chélidoine, sans jamais l'espèce
demandée, qui n'apparaissait donc dans aucun des vingt résultats.

Ne **jamais** se contenter du premier résultat non plus : `q=Salamandra
salamandra` renvoie *Plethodon cinereus* en tête. La règle appliquée par les
scripts :

1. retenir le résultat dont le champ `name` est **exactement** le nom demandé ;
2. à défaut, celui dont `matched_term` est exactement le nom demandé — ce qui
   rattrape les renommages (`Ammophila arenaria` est devenu
   `Calamagrostis arenaria`, et c'est iNaturalist qui a raison) ;
3. sinon, échouer bruyamment plutôt que de deviner.

Ces renommages acceptés sont consignés dans le dictionnaire `SYNONYMES` de
`scripts/verifier-imagier.py`, sans quoi le contrôle les signalerait à chaque
passage.

## Chercher des observations

`GET https://api.inaturalist.org/v1/observations`

| Paramètre | Valeur | Pourquoi |
|---|---|---|
| `taxon_id` | l'identifiant résolu ci-dessus | `taxon_name` accroche les noms vernaculaires et rend des espèces d'un autre continent |
| `photo_license` | `cc0,cc-by,cc-by-sa` | les seules licences publiables ; une clause NC est disqualifiante |
| `quality_grade` | `research` | l'espèce a été confirmée par plusieurs naturalistes |
| `captive` | `true` | pour les animaux de la ferme, qui n'ont pas d'observation « sauvage » ; remplace `quality_grade` |
| `captive` | `true` | **et pour les plantes cultivées** : sans lui, `Beta vulgaris` ne rend que la betterave maritime sauvage, la vigne aucune grappe et le noyer aucune noix — un champ cultivé est « captive » au sens d'iNaturalist |
| `place_id` | `97391` (Europe) | écarte les espèces voisines d'Amérique du Nord |
| `order_by` | `votes` | le moins mauvais des tris, mais il faut regarder ce qu'il remonte |
| `month` | `5,6,7` | pour une plante : sans cela le tri remonte des rosettes hivernales et des pieds défleuris |
| `per_page`, `page` | jusqu'à 60, plusieurs pages | pour élargir le vivier quand une espèce résiste |

Filtrer ensuite côté script sur `original_dimensions` : en deçà de 1000 px de
côté, la photographie ne s'imprime pas proprement sur une carte. Et préférer
les photographies en largeur (`width >= height`), qui perdent moins au
recadrage.

**Un seul observateur peut tenir tout le vivier.** Quarante candidates sont
parfois quarante clichés du même pied, pris le même jour par la même
personne : `candidats-imagier.py` ne retient donc qu'une photographie par
`user.login`, sinon le choix n'est qu'apparent.

**Retrouver les crédits demande d'aller loin.** La photographie choisie à la
main se trouve parfois à la quatrième page du vivier : `credits_photo()`
pagine jusqu'à épuisement (`PAGES_MAX`), et non plus jusqu'à la page 3 — un
arrêt court faisait rejeter la photographie faute d'auteur.

**Une sous-espèce et un renommage restent la bonne espèce.** *Canis lupus
italicus* est un loup, *Anemonoides nemorosa* est le nom actuel de l'anémone
des bois : les planches ne les encadrent pas en rouge, et le contrôle les
accepte, y compris une sous-espèce d'un nom renommé (*Mesotriton alpestris
alpestris* pour *Ichthyosaura alpestris*). Seule une espèce **voisine** est
signalée.

**Sauf quand la sous-espèce est une autre carte de l'imagier.** *Sus scrofa
domesticus* est une sous-espèce de *Sus scrofa* : avec `captive=true`, le
vivier du sanglier est aux trois quarts fait de cochons de ferme. Le
contrôle refuse qu'une carte porte l'espèce d'une autre, mais la planche ne
le signale pas — vérifier la colonne « espèce » de `candidats-index.json`.

**Le taxon rendu n'est pas garanti.** Même avec `taxon_id`, la recherche
remonte des observations d'espèces voisines : un `Quercus orocantabrica`
parmi les `Quercus robur`. Toujours comparer `observation.taxon.name` au nom
attendu — c'est ce que font les planches de candidats (encadré rouge) et
`scripts/verifier-imagier.py`.

## Récupérer un fichier

Deux hôtes, plusieurs extensions ; les essayer tous :

```
https://inaturalist-open-data.s3.amazonaws.com/photos/<id>/<taille>.<ext>
https://static.inaturalist.org/photos/<id>/<taille>.<ext>
```

`<taille>` vaut `square`, `medium`, `large` ou `original` ; `<ext>` vaut
`jpeg`, `jpg` ou `png`. Les URL rendues par l'API pointent sur `square` : il
suffit de remplacer le mot.

Chaque fichier source est gardé dans `/tmp/imagier-source`, ce qui permet de
**rejouer un recadrage sans réseau** :

```sh
RECADRER=1 python3 scripts/chercher-images-imagier.py
```

utile après un changement du format des cartes.

## Retrouver les crédits d'une photographie imposée

Une photographie choisie à la main vient souvent d'une recherche plus fine
que celle du script (Europe, captivité, page 3…). `credits_photo()` rejoue
donc les variantes — `research`, sans filtre, `captive`, Europe, `needs_id` —
sur plusieurs pages et deux tris, jusqu'à retrouver l'observation. S'il
échoue, il lève une erreur : publier sans auteur ni licence n'est pas une
option.

## Variables d'environnement

| Variable | Script | Effet |
|---|---|---|
| `FORCE=1` | `chercher-images-imagier.py` | retélécharge même si l'image existe |
| `RECADRER=1` | `chercher-images-imagier.py` | refabrique depuis le cache, sans réseau |
| `IMAGIER_CACHE` | `chercher-images-imagier.py` | dossier du cache (défaut `/tmp/imagier-source`) |
| `CANDIDATS_DIR` | `candidats-imagier.py` | où écrire les planches |
| `NB_CANDIDATS` | `candidats-imagier.py` | candidates par espèce (défaut 8) |
| `PLACE` | `candidats-imagier.py` | `place_id`, par exemple 97391 pour l'Europe |
| `MOIS` | `candidats-imagier.py` | `month`, par exemple `5,6,7` pour une plante en fleur |
| `PAGES` | `candidats-imagier.py` | pages de 60 explorées quand le vivier est pauvre (défaut 1) |
| `CADRE` | `zoom-imagier.py` | applique le recadrage des cartes aux candidates |
| `ZOOM_CELL` | `zoom-imagier.py` | côté d'une vignette agrandie (défaut 520 px) |
| `REVUE_DIR` | `revoir-imagier.py` | où écrire les planches de revue |

## Géométrie des cartes

La zone photo mesure 90,6 × 62 mm, soit un rapport de **1,46**. Les images
sont produites en 1100 × 753 px. Le recadrage découpe le plus grand
rectangle à ce rapport : quand c'est le haut et le bas qu'il faut rogner, la
coupe est décalée vers le haut (35 %), où se trouve le plus souvent le sujet.
