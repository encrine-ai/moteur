---
name: fiches-illustrations
description: Choisir, vérifier et installer les illustrations des fiches élève (site/fiches/img/) — pictogrammes Mulberry Symbols et ARASAAC, jamais d'émoji, jamais de dessin à main levée. À utiliser dès qu'il faut ajouter une image à une fiche d'entraînement ou d'évaluation, remplacer un pictogramme jugé mauvais, illustrer une nouvelle notion, ou toucher à site/fiches/img/, credits.json, scripts/chercher-pictos.py, scripts/remplace-emojis.py ou scripts/generer-credits.py. Se déclenche aussi quand la demande ne nomme aucun fichier : « le dessin de la poule est bizarre sur la fiche », « il me faut une image de tracteur pour l'exercice », « remplace ce picto », « ajoute des illustrations à cette fiche », « cette image ne convient pas à des enfants ». Charger ce skill AVANT de télécharger la moindre image : les noms des pictogrammes mentent (« chicken » était un poulet rôti), et plusieurs sources en apparence évidentes sont piégées ou bloquées.
---

# Les illustrations des fiches élève

Les dix cahiers de fiches (`site/fiches/periode-N.html` et
`entrainement-periode-N.html`) sont illustrés par des **pictogrammes**, pas
par des émojis ni des photos. Les enfants ont cinq ans et ne lisent pas
encore : dans un exercice de comptage, de tri ou de vocabulaire, l'image
porte seule le sens. Un pictogramme ambigu ne fait pas un exercice médiocre,
il fait un exercice faux.

## La banque

Tout vit dans `site/fiches/img/` (~145 fichiers) :

- **pictogrammes Mulberry Symbols** (`.svg`) — l'essentiel de la banque, le
  style de référence ;
- **pictogrammes ARASAAC** (`.png`) — pour ce que Mulberry n'a pas ;
- **4 photographies** seulement (arbre-creux, bouquetin, filet-peche,
  glacier) — des concepts introuvables en pictogramme ;
- **formes auto-fabriquées** (dés `de-1..6.svg`, `rond.svg`,
  `rond-plein.svg`, `triangle.svg`, `etoile-jaune.svg`) — géométrie simple,
  seul dessin « maison » autorisé.

`credits.json` est la source de vérité : `slug → {fichier, source, page,
licence, auteur}`. Une image sans crédit n'existe pas. Les fiches affichent
tout via `<img class="pic" src="img/<slug>.<ext>">` ; les tailles sont dans
`fiches.css` (`.pic`, `.case .img .pic`, etc.), ne pas mettre de taille en
dur sauf besoin ponctuel.

## L'ordre des sources — et pourquoi

**1. Mulberry Symbols d'abord, toujours.** 3 436 pictogrammes cohérents,
CC BY-SA 4.0 (compatible commercial). GitHub (API et `raw.githubusercontent`)
est **bloqué par le proxy de l'agent** ; passer par jsDelivr, qui passe :

```
catalogue : https://data.jsdelivr.com/v1/packages/gh/mulberrysymbols/mulberry-symbols@3.5.2
fichier   : https://cdn.jsdelivr.net/gh/mulberrysymbols/mulberry-symbols@3.5.2/EN/<nom>.svg
```

Les noms sont anglais, parfois avec virgules à encoder (`ski_,_to`,
`blow_,_to`). La recherche se fait dans les noms (`hen`, `tractor`,
`potted_plant`…).

**2. ARASAAC ensuite**, pour les concepts absents de Mulberry (la banque en
compte une trentaine : fourmilière, terrier, igloo, lama, marmotte, chamois,
sanglier, aigle, phare, vague, vent, calamar, pirate, neige, goutte…). API
gratuite, sans clé, sans bridage, **recherche en français** :

```
recherche : https://api.arasaac.org/api/pictograms/fr/search/<mot>
fichier   : https://static.arasaac.org/pictograms/<id>/<id>_500.png
```

ARASAAC est **CC BY-NC-SA** — clause NC. C'est accepté, crédité, et
signalé sur la fiche de partage de la classe ; Mulberry, entièrement libre
et style de la maison, passe toujours d'abord. Crédit obligatoire : « Sergio
Palao — propriété du Gouvernement d'Aragon (Espagne) ».

**3. Openverse en troisième recours** (un clipart introuvable en
pictogramme — le flocon de neige comptable vient de là ; puis la clairière,
le sous-bois, le pelage, le givre, la marée et la dune des cartes-corpus).
`https://api.openverse.org/v1/images/?q=…&license=cc0,pdm,by,by-sa`, sans
clé. **Ne pas utiliser `license_type=commercial`** : il laisse passer les
images **CC BY-ND**, qui autorisent bien le commerce mais interdisent les
œuvres dérivées — et recadrer une photographie pour une carte, c'est
dériver. Une photographie de givre est entrée ainsi, avec des crédits
parfaitement corrects ; seul un contrôle relisant la licence l'a rattrapée.
Énumérer les licences, donc, jamais se fier au filtre.
`chercher-pictos.py` s'en charge, mais **sur demande explicite** — la
requête est en anglais et va dans `OPENVERSE`, jamais dans le slug :

```sh
OPENVERSE="forest clearing glade" python3 scripts/chercher-pictos.py chercher clairiere ""
python3 scripts/chercher-pictos.py installer clairiere openverse:f801f396
```

Le second argument accepte les 8 premiers caractères de l'UUID, ceux que
porte le nom du fichier candidat ; la table qui les rend complets ne garde
que **la dernière recherche du slug**, donc un identifiant relevé sur une
planche plus ancienne demande de relancer `chercher`.

Quatre pièges, tous outillés : la licence ci-dessus, revérifiée à
l'installation et par `chercher-pictos.py verifier` ; les fichiers qui
arrivent parfois en **WebP ou SVG sous une extension .jpg** (le type est lu
dans les octets, pas dans le nom) ; les téléchargements coupés au-delà de
8 Mo ; et Openverse qui **sert aussi Wikimedia Commons** — ces résultats-là
sont écartés d'office, sans quoi la planche s'arrête en `429`. Sans clé
d'API, `page_size` est plafonné à 20 : au-delà, l'API répond `401`.

Et un piège qui ne s'outille pas : **la requête décide de tout**. « sand
dune beach » rend des dunes ; « coastal sand dunes » rend six gros plans de
fleurs de dune, et « sand dune beach marram » six plages sans dune. Quand
une planche ne donne rien, changer les mots avant de conclure que la notion
est introuvable.

**4. Une photographie en tout dernier recours**, et jamais au milieu d'une
grille de pictogrammes dans un exercice de discrimination (« entoure
l'intrus ») : l'enfant entoure la photo parce qu'elle détonne, pas parce
qu'il a raisonné.

## À ne surtout pas faire

- **Wikimedia Commons.** `upload.wikimedia.org` limite l'adresse de sortie
  mutualisée de l'agent à ~5 fichiers par 10 minutes (`429`,
  `Retry-After: 600`) ; le compteur est partagé et le moindre `curl` de
  vérification le relance. Une moisson y prend des heures. Ne pas y
  retourner, même « pour un seul fichier ».
- **Dessiner des SVG à main levée.** Interdit par l'enseignante (« tu fais
  ça très très mal »). Seules les formes géométriques élémentaires (dés,
  ronds, triangles, frises, escaliers de carrés) sont acceptées. Adapter
  mécaniquement un pictogramme existant est en revanche permis : la
  feuille-morte est la `leaf` Mulberry recolorée en brun, le flocon un SVG
  Openverse recoloré et débarrassé de son animation.
- **Les émojis.** Aucun, nulle part dans les fiches. Liste blanche des seuls
  glyphes autorisés : `★ ✓ ✗ ● ▲ ☐ ✂ → ← ↓ ·` (le contrôle est dans
  `scripts/remplace-emojis.py`, passe 4).
- **Se fier au nom d'un pictogramme.** C'est le piège qui a fait le plus de
  dégâts : `chicken` Mulberry est un **poulet rôti**, `dove` une colombe
  blanche (publiée un temps pour « le pigeon »), `plane` un **rabot**,
  `deer` un cerf médiocre (`stag` est le bon), `snow` un nuage qui neige
  (incomptable), `shells` un tas de coquillages (inutilisable pour compter) ;
  côté ARASAAC, « glacier » rend des **marchands de glaces** et « tronc »
  des bûches de Noël. Les cartes-corpus en ont ajouté d'autres :
  `M:calf` est un **mollet** (pas un veau), `M:lamb` une **côtelette**,
  ARASAAC 37633 un **tsunami** pour « la marée » ; en français, « forêt »
  ramène un foret de perceuse, « ferme » l'adjectif *fermé*, « glace » un
  dessert, « agneau » un gigot. **Chaque image se juge à l'œil, sur une
  planche, avant installation** — sans exception.
- **Chercher une autre source que celles de la liste.** Openclipart et
  Commons ont été rajoutés par une session qui n'avait pas lu cette page,
  puis retirés : l'adresse PNG d'Openclipart rendait le logo du site au lieu
  du dessin, et un identifiant Global Symbols passé au registre Openclipart
  a donné un ruban de sensibilisation à l'autisme — **chaque registre a sa
  numérotation**. Le filtre des jeux libres existe déjà
  (`scripts/pictos-libres.py`) ; il a été réécrit trois fois faute d'avoir
  été cherché. Lire ce skill et `git log` avant d'outiller quoi que ce soit.

## Les règles de choix

1. **Un seul sujet par image.** Pour un exercice de comptage, l'image doit
   être *comptable* : un flocon, pas un nuage qui neige ; un coquillage,
   pas un tas.
2. **Adapté à cinq ans** : ni arme, ni peur, ni ambiguïté.
3. **Cohérence de style dans un même exercice** : tout en pictogrammes.
   Mélanger picto et photo dans une grille fausse les exercices de tri. Et
   sur une même page, Mulberry partout où il existe : l'enseignante a jugé
   les images du premier mélange « pas du tout cohérentes les unes avec
   les autres », et les
   pictogrammes-photos de PiCom cassent le trait Mulberry.
4. **Un lieu ou une matière ne se dessine pas** : clairière, trottoir,
   glacier, pelage, givre n'ont pas de pictogramme lisible. C'est le cas où
   la photographie s'impose (point 4 de l'ordre des sources).
5. **Une partie d'un tout** (la pince, la carapace, l'écaille) se montre
   en cernant la partie sur l'image de l'animal entier, d'un liseré **qui
   contraste** et **posé au bon endroit** : les premiers repères étaient mal
   placés, et rouges sur un crabe orange — invisibles.
6. **La licence avant l'esthétique** : CC0, CC BY, CC BY-SA sans réserve ;
   CC BY-NC-SA (ARASAAC) accepté faute de mieux ; toute autre clause
   disqualifie.

## Montrer avant de conclure

L'enseignante veut **voir** les images et trancher (« n'hésite pas à me
montrer régulièrement ce que tu produis ») : lui montrer la planche des
candidats retenus pour les cas douteux, plutôt qu'annoncer « 64 images
installées ». Son jugement prime sur les critères ci-dessus : elle a désigné
elle-même la photographie de la grange, délabrée (« une grange ce n'est
jamais en bon état », commit « La grange : une vraie grange, et tant pis
pour la tôle »), et gardé l'écume avec sa flèche. Une décision de ce genre
s'écrit dans le message de commit, pour qu'une revue future ne la
« corrige » pas.

## La boucle de travail

```sh
# 1 — chercher des candidats (Mulberry en anglais, ARASAAC en français)
python3 scripts/chercher-pictos.py chercher tracteur "tractor"
#     → planche /tmp/pictos/tracteur.png : LA REGARDER, juger chaque image
#     (ARASAAC=<mot> remplace le slug pour la recherche française)

# 2 — installer le candidat retenu (copie + credits.json)
python3 scripts/chercher-pictos.py installer tracteur mulberry:tractor

# 3 — référencer l'image dans les fiches HTML
#     <img class="pic" src="img/tracteur.svg" alt="">

# 4 — régénérer les pages de crédits des dix cahiers
python3 scripts/generer-credits.py

# 5 — contrôler la banque (crédits complets, références cassées, orphelins)
python3 scripts/chercher-pictos.py verifier
```

## Toujours finir par le PDF

Une fiche = une page A4, et l'écran ne le montre pas (la page d'un
navigateur s'allonge, pas une feuille). Après toute modification :

```sh
cd site/fiches
CH=$(ls -d /opt/pw-browsers/chromium*/chrome-linux/chrome | head -1)
"$CH" --headless --no-sandbox --no-pdf-header-footer --virtual-time-budget=20000 \
      --print-to-pdf=/tmp/f.pdf entrainement-periode-1.html
pdfinfo /tmp/f.pdf | grep Pages    # attendu : nb de fiches + 1 page de crédits
```

Un nombre de pages en trop = une fiche qui déborde. La repérer avec
`pdftoppm -png -r 25 /tmp/f.pdf /tmp/pg` et compacter (marges des `.exo`,
hauteur des cases) plutôt que supprimer du contenu. Les cahiers comptent
12 fiches (entraînement) ou 6-8 (évaluation) ; les fiches `paysage`
(découpage) doivent rester en orientation paysage (`pdfinfo` les montre).

Les PDF publiés ne sont pas versionnés : `scripts/generer-pdf.sh` les
refabrique au déploiement (push sur `main` → GitHub Actions → site).
