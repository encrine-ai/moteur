# Le moteur Encrine

Ce dépôt est **le modèle** d'Encrine (https://encrine.ai) : le moteur qui
fabrique l'année d'une classe — programmation, progressions conformes au
programme, fiches, imagier, cartes de vocabulaire, PDF — à partir de
`classe.yml`. Chaque enseignant crée **son** dépôt depuis ce modèle, puis
tape `/nouvelle-classe`. Le modèle **ne publie rien** (le déploiement saute
tant que le dépôt est un modèle) ; la **classe de démonstration** est un
dépôt à part, `encrine-ai/tour-du-monde`, publié sur
https://encrine.ai/tour-du-monde/, et créé depuis ce modèle comme toute
classe.

Tout est écrit **en français**, y compris les noms de fichiers, les
commentaires et les messages de commit.

## Organisation

| Chemin | Rôle |
|---|---|
| `01-…`, `02-…`, `03-progressions/`, `04-evaluations/` | les documents de l'enseignant, en Markdown |
| `site/` | l'application web (JS sans cadriciel), publiée sur GitHub Pages |
| `site/charte/` | la charte, en deux couches : `socle.css` (Andika, espacements, mécanique des périodes, commun à toutes les classes) et `themes/<thème>/theme.css` (couleurs et polices du thème de la classe ; `demo` dans le modèle), assemblés dans `charte.css` par `classe.py` — la seule source des couleurs (skill `charte-graphique`) |
| `site/fiches/` | les fiches élève imprimables, une page A4 par fiche |
| `site/imagier/` | l'imagier Montessori, un cahier de cartes par période |
| `site/cartes-corpus/` | les cartes-corpus de vocabulaire, un cahier par période |
| `classe.yml` | **la classe** : nom, niveau, année, projet, calendrier, milieux, documents — la seule source de ce qui la distingue d'une autre ; `scripts/classe.py verifier` refuse qu'une de ces données soit écrite en dur dans le code |
| `classe/` | le contenu propre à la classe, que `classe.yml` désigne : les espèces de l'imagier (`imagier.py`), les cartes-corpus (`corpus.py`), ce que l'année traite du programme (`annotations.yml`) |
| `scripts/` | fabrication des pages et des images |
| `.claude/skills/` | les procédures outillées du dépôt (voir ci-dessous) |
| `referentiel/` | le programme sous forme de liste numérotée, et le contrôle de couverture |

Les PDF **ne sont pas versionnés** : `scripts/generer-pdf.sh` les fabrique à
chaque déploiement avec Chromium en mode `--print-to-pdf`.

Après avoir touché à un manifeste ou à un gabarit, régénérer les pages :

```sh
python3 scripts/classe.py generer        # site/classe.json et classe.js, après toute retouche de classe.yml
python3 scripts/generer-cartes-corpus.py # site/cartes-corpus/periode-N.html
python3 scripts/generer-imagier.py     # site/imagier/periode-N.html
python3 scripts/generer-credits.py     # page des crédits des fiches
```

Après avoir touché aux photographies de l'imagier, les contrôler :

```sh
python3 scripts/verifier-imagier.py    # espèce, crédits, cadrage, nombres annoncés ; code 1 s'il reste une anomalie
REVUE_DIR=/tmp python3 scripts/revoir-imagier.py   # les cartes telles qu'elles s'imprimeront
```

Et **finir par le PDF, jamais par le HTML** : la page d'un navigateur
s'allonge, une feuille A4 non. Les deux pires défauts de ce matériel — les
étiquettes non paginées qui s'imprimaient par-dessus les crédits, le pied de
la garde seul sur une page — n'existaient pas à l'écran. Le contrôle est
outillé, et le déploiement le refait :

```sh
bash scripts/generer-pdf.sh /tmp/site            # le site assemblé (voir le skill imprimer-pdf)
python3 scripts/verifier-pagination.py /tmp/site # une page par fiche et par planche ; code 1 sinon
```

La marche à suivre est dans le skill [`imprimer-pdf`](.claude/skills/imprimer-pdf/SKILL.md).

Après avoir touché à une progression, vérifier que l'année couvre toujours
le programme :

```sh
python3 scripts/couverture.py          # tous les attendus du programme ; code 1 s'il en manque
```

`referentiel/cycle1-gs.yml` porte les attendus, un par ligne avec un
identifiant ; `classe/annotations.yml` dit ce que chaque
période traite. Une séance ajoutée sans accroche ne sera pas comptée.

**`referentiel/` ne contient que des exigences du programme**, relues contre le
BO. Une règle que la classe se donne (le nombre d'espèces de l'imagier, par
exemple) n'y a pas sa place : elle vit dans le script du matériel concerné.


## Les skills du dépôt

Chaque capacité du dépôt a son skill : c'est par eux qu'une session reprend
le travail sans repartir de zéro. Charger le skill **avant** de toucher au
matériel qu'il couvre, et finir par [`capitaliser`](.claude/skills/capitaliser/SKILL.md).

| Skill | Quand |
|---|---|
| [`progressions-programme`](.claude/skills/progressions-programme/SKILL.md) | le projet annuel, la programmation, une progression, une batterie d'évaluation — et la couverture du programme (`couverture.py`) |
| [`fiches-eleve`](.claude/skills/fiches-eleve/SKILL.md) | créer, modifier ou réparer une fiche élève d'évaluation ou d'entraînement (`site/fiches/`) |
| [`imagier-photos`](.claude/skills/imagier-photos/SKILL.md) | ajouter, remplacer ou vérifier une photographie de l'imagier — y compris quand la demande dit seulement « on ne voit pas bien l'animal » ou « change cette image » |
| [`fiches-illustrations`](.claude/skills/fiches-illustrations/SKILL.md) | ajouter, remplacer ou vérifier un pictogramme des fiches élève (`site/fiches/img/`) — y compris « le dessin de la poule est bizarre » ou « il me faut une image de tracteur » |
| [`cartes-corpus`](.claude/skills/cartes-corpus/SKILL.md) | les cahiers de cartes de vocabulaire (`site/cartes-corpus/`) — ajouter un mot à un corpus, refaire un cahier, produire les étiquettes de tri des fiches X.1 |
| [`charte-graphique`](.claude/skills/charte-graphique/SKILL.md) | toute question d'apparence : couleurs des périodes, polices, icônes, composants de l'écran et du papier, et le design system publié qui en est le miroir |
| [`imprimer-pdf`](.claude/skills/imprimer-pdf/SKILL.md) | fabriquer les PDF et prouver qu'ils sont justes — avant tout commit qui touche à ce qui s'imprime |
| [`site-et-calendrier`](.claude/skills/site-et-calendrier/SKILL.md) | l'application, la liste des documents, les zones et dates de vacances, le changement d'année, le déploiement |
| [`nouvelle-classe`](.claude/skills/nouvelle-classe/SKILL.md) | faire du dépôt la classe d'un autre enseignant : l'entretien (niveau, zone, thème, matériel), puis `classe.yml`, les progressions, les cahiers et les PDF |
| [`retours-enseignant`](.claude/skills/retours-enseignant/SKILL.md) | l'enseignant fait ses retours avec ses mots (une fiche, une image, une idée) : les trier, corriger la classe, remonter ce qui vaut pour toutes |
| [`remonter-au-moteur`](.claude/skills/remonter-au-moteur/SKILL.md) | un défaut, une amélioration ou une idée qui servirait à toutes les classes devient une issue sur le dépôt du moteur (`moteur` dans `classe.yml`) |
| [`synchroniser-moteur`](.claude/skills/synchroniser-moteur/SKILL.md) | mettre à jour le moteur d'une classe depuis le dépôt modèle, sans toucher à son contenu, contrôles et PDF compris |
| [`partager-ma-classe`](.claude/skills/partager-ma-classe/SKILL.md) | à la demande de l'enseignant seulement : vérifier (dont `verifier-partage.py` : aucun prénom d'élève, aucune photo de classe, aucun texte recopié), préparer la fiche et proposer la classe à « Les classes » d'encrine.ai, ou l'en retirer |
| [`capitaliser`](.claude/skills/capitaliser/SKILL.md) | en fin de tâche : verser ce qu'elle a appris dans le bon skill, le bon script ou ce fichier |

Un skill se mesure : `scripts/mesurer-declenchement.py` rejoue une liste de
demandes réalistes et regarde si le skill s'ouvre au bon moment (les cas de
l'imagier sont dans `tests/`). **Ne pas se fier au banc d'essai du
skill-creator** pour cela : il passe par un faux fichier de commande que
cette version de Claude Code n'expose pas comme un skill, si bien qu'aucune
demande ne déclenche jamais rien — il annonçait 10/20 là où la mesure
directe donne 20/20.


## Branches, commits, publication

- **Le dépôt d'une classe est public** (GitHub Pages publie gratuitement les
  dépôts publics) : une branche poussée est lisible par tous, même sans être
  déployée. Aucune donnée d'élève n'y entre jamais — ni prénom, ni photo, ni
  production scannée.
- Le travail se fusionne sur **`main`**, en avance rapide, et seulement
  quand les contrôles sont verts : `main` se déploie, et un état
  intermédiaire publierait des cartes sans image. Confirmer la fusion sur
  pièces (`git log origin/main`).
- **Travailler sur `main`** dans Claude Code : Pages publie la branche par
  défaut, et une session partie sur une autre branche fait échouer le
  premier déploiement.
- **L'auteur d'un commit n'est jamais l'adresse de l'enseignant.**
- Dire ce qui est fait, ce qui reste, ce qui attend sa décision — jamais
  « commité et poussé » pendant que le chantier continue.
- Le proxy d'une session **refuse les écritures destructives** (supprimer une
  branche distante, créer un dépôt) : le dire et laisser l'enseignant le
  faire, sans essayer de contourner.


## Travailler avec l'enseignant

L'outil travaille **pour un enseignant**, qui dicte souvent depuis un
téléphone, photos et captures à l'appui : lire les messages pour leur sens
(« SDG » était « SVG »). Le ton est réglé par `ton` dans `classe.yml`
(`tu` par défaut, comme entre collègues, annoncé à la première question).

- **Aller droit au résultat.** Une source qui bloque se dit tout de suite et
  l'on change d'approche ; ne jamais boucler sur une attente.
- **Montrer, régulièrement**, ce qui est produit — planches d'images, pages
  rendues — pour qu'il juge la qualité ; son verdict l'emporte, et s'écrit
  dans le message de commit.
- **Ne pas lui renvoyer le travail** : ne poser que les questions qu'il est
  seul à pouvoir trancher (pédagogie, goût, diffusion), une à la fois, et
  attendre la réponse plutôt que trancher seul.
- **Sans jargon** : dire « la liste numérotée du programme », pas « le
  référentiel » ; expliquer un chiffre pas à pas.
- **Vérifier avant d'affirmer** et reconnaître une erreur sans détour : un
  nombre donné de mémoire, une règle prêtée à tort au programme.
- **Lire le dépôt avant de refaire** : skills, `git log`, scripts.
- **La qualité attendue est celle du commerce**, imprimée pour de vrai :
  l'à-peu-près se refait.
- Ce qui vaut pour toutes les classes remonte au moteur (skills
  `retours-enseignant`, `remonter-au-moteur`) ; les mises à jour du moteur
  reviennent par `synchroniser-moteur`.


## Images : quelles sources, et laquelle éviter

### Wikimedia Commons — à éviter pour toute nouvelle moisson

`upload.wikimedia.org` limite très sévèrement l'adresse de sortie mutualisée
depuis laquelle tourne l'agent : au-delà de quelques fichiers, il répond
`429` avec un `Retry-After: 600`, soit **environ cinq images par tranche de
dix minutes**. Quatre-vingt-dix images demandent alors plusieurs heures — et
le seau de jetons est partagé, si bien que **le moindre `curl` de
vérification vers ce domaine relance le compteur**. Ni le parallélisme, ni le
regroupement des appels d'API, ni le passage par les fichiers d'origine
plutôt que les vignettes n'y changent quoi que ce soit : la limite porte sur
l'adresse, pas sur la manière de demander.

Les illustrations des fiches élève n'en dépendent plus : ce sont des
**pictogrammes** (Mulberry Symbols via jsDelivr, ARASAAC via son API — deux
sources sans bridage), versionnés dans `site/fiches/img/` avec leurs crédits.
La procédure complète — sources dans l'ordre, pièges des noms trompeurs,
planche de candidats obligatoire, installation, contrôles — est dans le
skill [`fiches-illustrations`](.claude/skills/fiches-illustrations/SKILL.md),
outillée par `scripts/chercher-pictos.py` (chercher / installer / verifier).
`scripts/chercher-images.py` et `scripts/images-manifest.py` sont l'ancienne
moisson Commons : ne pas les relancer.

### Vérifier la licence avant de retenir une image

Toute image entrant dans le dépôt doit porter une licence **compatible avec
un usage commercial et avec la modification** — CC0, la marque du domaine
public, CC BY ou CC BY-SA — parce que le matériel est susceptible d'être
diffusé au-delà du site gratuit, et qu'une carte recadre l'image.

Deux clauses disqualifient :

- **NC**, qui interdit l'usage commercial. Les pictogrammes **ARASAAC** sont
  dans ce cas ; c'est accepté tant que le matériel reste
  gratuit, et c'est la raison pour laquelle Mulberry passe toujours d'abord ;
- **ND**, qui interdit les œuvres dérivées, et qui est le piège vicieux :
  le filtre `license_type=commercial` d'Openverse **la laisse passer**,
  puisqu'une image ND autorise bien le commerce. Une photographie de givre
  est entrée ainsi, avec des crédits parfaitement corrects. Il faut énumérer
  les licences (`license=cc0,pdm,by,by-sa`), et non se fier au filtre —
  `chercher-pictos.py` le fait, à la recherche comme à l'installation, et
  `chercher-pictos.py verifier` relit la licence de chaque crédit.

`scripts/pictos-libres.py` interroge le registre **Global Symbols**
(`globalsymbols.com`), qui fédère une trentaine de jeux de pictogrammes en
publiant la licence de chacun, et ne retient que les jeux libres — Mulberry
(le style de maison des fiches), OpenMoji, PiCom. **Personne ne dessine les
concepts qu'il ne retrouve pas** : on élargit les mots-clés, on cherche
ailleurs dans l'ordre des sources, et on se rabat sur une photographie
Openverse — un dessin fait ici est proscrit, le skill
[`fiches-illustrations`](.claude/skills/fiches-illustrations/SKILL.md) le
dit noir sur blanc. Deux pièges : le registre cherche
en **sous-chaîne**, si bien que « lama » ramène *flamant* et « vague »
*microwave* — d'où le filtre sur le mot entier ; et Blissymbolics, bien que
libre, est un système d'écriture symbolique, inutilisable comme illustration.

### iNaturalist — la source des photographies d'espèces

`scripts/chercher-images-imagier.py` interroge
`https://api.inaturalist.org/v1/observations`. Aucune limitation gênante :
une période entière de l'imagier se fabrique en quelques minutes. Les paramètres qui comptent :

- `taxon_name` — **toujours le nom scientifique** (`Quercus robur`, et non
  « chêne ») ; c'est pourquoi `classe/imagier.py` porte le taxon de
  chaque espèce. Une recherche par nom vernaculaire est bien moins fiable.
- `quality_grade=research` — l'espèce a été confirmée par plusieurs
  naturalistes. À relâcher pour les animaux domestiques (vache, poule,
  cochon), qui n'ont jamais d'observation de « qualité recherche »
  puisqu'ils ne sont pas sauvages : le script le fait tout seul.
- `photo_license=cc0,cc-by,cc-by-sa` — les seules licences qui autorisent la
  publication sur le site avec mention de l'auteur.
- `original_dimensions` — filtrer en deçà de 1000 px de côté, une photo plus
  petite ne s'imprime pas proprement sur une carte.

Les fichiers sont servis par deux hôtes
(`inaturalist-open-data.s3.amazonaws.com` et `static.inaturalist.org`) et
sous plusieurs extensions ; `url_photo()` les essaie tous. Chaque source est
gardée en cache dans `/tmp/imagier-source`, ce qui permet de **rejouer un
recadrage sans réseau** (`RECADRER=1`).

### Choisir une photographie de carte : voir le skill

La procédure complète — planches de candidats, critères de sélection,
paramètres d'iNaturalist, contrôle avant publication — est dans le skill
[`imagier-photos`](.claude/skills/imagier-photos/SKILL.md), à charger avant
de toucher aux images de l'imagier. L'essentiel, en bref :

**Aucun tri automatique ne convient.** `order_by=votes` met en avant les
photographies les plus *aimées*, spectaculaires plutôt qu'illustratives : un
ours mangeant des pissenlits pour « le pissenlit », un renard argenté pour
« le renard roux ». Chaque photographie se choisit à l'œil, sur une planche
de candidats, et son identifiant s'inscrit dans `OVERRIDES`
(`classe/imagier.py`).

**Cinq critères**, tous nés d'une carte qu'il a fallu refaire : un seul
individu ; une image qui convient à des enfants de cinq ans (le vivier est
plein de saillies, de prédation et de crânes) ; l'animal entier, de face ou
de profil ; une image qui remplit la carte ; rien autour du sujet.

**Deux pièges qui donnent la mauvaise espèce.** Chercher par `taxon_id`,
jamais par `taxon_name` : ce dernier accroche les noms vernaculaires et a
fait publier un blaireau d'Amérique pour « le blaireau », un rhebok
d'Afrique du Sud pour « le chevreuil », une marmotte d'Amérique pour « la
marmotte ». Et les animaux de la ferme se cherchent avec `captive=true`,
faute de quoi le cochon d'élevage devient un sanglier féral. Même avec
`taxon_id`, le vivier contient des espèces voisines : les planches les
encadrent en rouge, et `scripts/verifier-imagier.py` refuse de laisser
passer une carte mal identifiée.

### Faune **et flore**

La flore ne se réduit pas aux fleurs : elle comprend les arbres, les
arbustes, les fougères, les mousses, les graminées, les algues et les
cultures. Quand un thème a un imagier de faune et de flore, cette dernière liste doit
rester variée — un milieu représenté par neuf fleurs serait faux.

