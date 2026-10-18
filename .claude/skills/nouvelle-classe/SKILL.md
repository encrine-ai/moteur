---
name: nouvelle-classe
description: Le skill d'amorçage du moteur — transformer ce dépôt en LA classe d'un autre enseignant, à partir d'un court entretien (niveau, double niveau, année et zone de vacances, thème de l'année et milieu de chaque période, matériel voulu, profil de la classe), puis écrire classe.yml et le contenu, réécrire le projet, la programmation et les progressions jusqu'à ce que le programme soit couvert, fabriquer les cahiers et finir par le PDF. À utiliser quand quelqu'un veut sa propre version : « je veux faire ma classe », « crée une classe de moyenne section », « adapte tout ça pour ma GS de l'an prochain, zone B », « je voudrais le même matériel mais sur le thème des contes », « j'ai une classe de MS-GS », « /nouvelle-classe », « on repart de zéro pour une autre école », « je voudrais partir de la classe des contes de la galerie », « j'ai cliqué sur Partir de cette classe », « fais-moi la même que celle-ci : <lien> ». Commence toujours par regarder si une classe est déjà dans le dépôt (copie faite par « Use this template » d'une classe partagée) : alors il l'enrichit au lieu de repartir de zéro. Ne concerne pas une retouche de la classe actuelle (une séance, une fiche, une image, une date : voir les skills de chaque matériel).
---

# Nouvelle classe

Ce dépôt est **une** classe faite avec le moteur. Ce skill en fait une
autre : la sienne, à l'enseignant qui lance la session. Une classe, c'est
`classe.yml` (ce qui la distingue d'une autre), le dossier `classe/` (les
espèces de l'imagier, les mots des corpus, ce que l'année traite du
programme), les documents `01-…` à `04-…`, et les cahiers fabriqués dans
`site/`. **Le moteur ne se touche pas** : `site/*.js`, `scripts/`,
`referentiel/`, `.claude/skills/` restent tels quels, et
`python3 scripts/classe.py verifier` le garantit.

## Étape 0 — Une classe est-elle déjà là ?

Décidé le 18 octobre 2026 : chaque classe partagée est elle-même un
dépôt-modèle GitHub. « Partir de cette classe », c'est **« Use this
template » sur le dépôt de cette classe** : l'enseignant arrive avec tout
son contenu, son thème et ses PDF, puis tape `/nouvelle-classe`, **sans
adresse**. Avant toute question, regarder donc ce que contient le dépôt :

```sh
git remote get-url origin                       # le dépôt courant
python3 -c "import yaml; c = yaml.safe_load(open('classe.yml')); print(c.get('depot'), c.get('materiel'))"
ls 03-progressions/ 2>/dev/null                 # des progressions écrites ?
```

Ramener l'adresse du remote à `propriétaire/dépôt` (sans `https://github.com/`,
`git@github.com:`, ni `.git` ; un proxy de session peut la préfixer, ne
garder que les deux derniers segments). Puis :

| Ce qu'on voit | Ce que c'est | Le mode |
|---|---|---|
| `classe.yml` a du contenu (`materiel` non vide, **ou** des progressions dans `03-progressions/`) **et** `depot` ≠ le dépôt courant | une copie d'une classe partagée, faite par « Use this template » | **enrichir** (ci-dessous) |
| `depot` = le dépôt courant | l'auteur lui-même relance l'entretien | l'entretien habituel (étape 1), sur sa propre classe |
| ni matériel ni progression (la classe de départ du modèle `moteur`, `depot: à définir`) | partir de zéro | l'entretien habituel (étape 1) |

Une classe ancienne sans `depot`, mais avec du contenu : demander une seule
fois « Cette classe est-elle la tienne, ou es-tu parti de celle d'un
collègue ? », puis suivre la ligne qui correspond.

## Le mode « enrichir » — on part d'une classe déjà là

1. **Annoncer ce qu'on garde**, en une phrase, avant toute question :
   « Tu pars de « <projet> » : je garde son thème, ses périodes, son style
   et son contenu. »
2. **Lire la licence** : `LICENCE-CONTENU.md` s'il existe, sinon
   `classe.yml` (`partage.licence` et `partage.auteur`, écrits par
   partager-ma-classe), sinon la fiche `partage/fiche.json`. **La dire** :
   - **CC BY-SA** : « Ta classe restera sous CC BY-SA, comme celle d'origine :
     c'est la condition de sa licence. » Garder ou écrire la même licence ;
   - **CC BY** : la nouvelle classe choisira la sienne au partage ; le crédit
     reste obligatoire ;
   - **NC, tous droits réservés, licence absente** : cette classe n'aurait
     pas dû être un modèle (partager-ma-classe l'empêche). Le dire, ne garder
     que le thème et les milieux (une idée ne se protège pas), et réécrire
     tout le reste comme pour une classe partie de zéro.
3. **Ne poser que** (un seul appel `AskUserQuestion`, avec la phrase du
   tutoiement) : **le niveau**, **la zone**, **l'année**, **le profil de la
   classe** — plus **par où commencer** (une période ou les cinq) si le
   niveau change. Le thème, les milieux, le matériel et le style sont repris
   sans question. La zone se redemande toujours : ne jamais garder le
   `calendrier` de la classe d'origine sans la réponse.
4. **Écrire `origine`** dans `classe.yml`, depuis ce que dit le dépôt :

   ```yaml
   origine:
     depot: <l'ancienne valeur de `depot`>
     titre: <le projet de la classe d'origine>
     auteur: <LICENCE-CONTENU.md, sinon partage.auteur ou partage/fiche.json>
     licence: CC BY-SA 4.0
     site: https://<propriétaire>.github.io/<dépôt>/
     reprise_le: AAAA-MM-JJ          # aujourd'hui
   ```

   puis **mettre `depot` au dépôt courant**. `classe.py verifier` refuse une
   `origine` sans titre ni licence, et une `origine.depot` égale à `depot`.
   Le pied du site crédite alors l'original (« Classe partie de « … », de …
   (…) », avec le lien) : c'est l'obligation de CC BY et CC BY-SA.
5. **Remettre à zéro ce qui appartient à l'auteur d'origine** : le `nom` de
   la classe change (demander lequel), l'`accroche` et le `sous_titre`
   aussi si l'enseignant le veut ; `partage` garde ses
   `prenoms_fictifs` (ce sont des personnages, pas des élèves), mais
   `partage.auteur` se vide (l'auteur de la nouvelle classe le choisira en
   partageant ; `partage.licence` reste CC BY-SA si l'origine l'est) ; supprimer
   `partage/fiche.json` (la fiche de galerie de l'autre classe). Réécrire la
   tête du `README.md` (étape 7) avec le crédit : « D'après *<titre>*, de
   <auteur> (<site>), sous licence <licence>. »
   `LICENCE-CONTENU.md`, s'il existe, se réécrit de même : la licence (la
   même, si l'origine est CC BY-SA), et le crédit de l'original.
6. **Selon le niveau** :
   - **le même niveau** : on garde tout. Recaler les dates sur la nouvelle
     zone et la nouvelle année (`calendrier.zone`, `annee` ; skill
     site-et-calendrier), `python3 scripts/classe.py generer`, régénérer les
     cahiers, puis refaire tous les contrôles (`classe.py verifier`,
     `couverture.py`, `verifier-imagier.py`…) et **les PDF** (étape 6) ;
   - **un autre niveau** : on garde le thème, les milieux et le style, mais
     les progressions, les évaluations et les fiches **se réécrivent** pour
     le nouveau niveau, sur la liste numérotée de son programme (étapes 3 et
     4). Un contenu d'un autre niveau ne se recopie pas ; l'imagier et les
     cartes-corpus peuvent rester, à revoir avec l'enseignant.
7. Les images gardent leurs crédits : ils sont déjà dans le dépôt, n'y rien
   retirer.

## Ce que le moteur sait faire aujourd'hui — le dire avant de commencer

Ne rien promettre que le moteur ne tient pas. À l'enseignant, en une phrase
simple, selon son niveau :

| Niveau | Aujourd'hui |
|---|---|
| **Grande Section** | tout : la liste numérotée du programme existe (`referentiel/cycle1-gs.yml`, 159 attendus), le contrôle de couverture tourne, tous les cahiers se fabriquent |
| **Petite ou Moyenne Section** | les cahiers et le site se fabriquent, mais **la liste du programme de ce niveau n'existe pas encore** : il faut d'abord l'écrire, ligne par ligne, BO à l'appui (skill progressions-programme), sinon personne ne peut dire que l'année couvre le programme |
| **Double niveau** (MS-GS…) | pas encore traité par le moteur : une seule liste du programme, un seul jeu de fiches. Proposer de commencer par le niveau le plus nombreux, et noter le besoin dans `docs/vers-un-moteur.md` |
| **Élémentaire** (CP → CM2) | pas encore : ni programme, ni gabarits de fiches. Le dire franchement |

## Une période, ou les cinq : l'enseignant choisit

Décidé le 18 octobre 2026 : **on pose la question**, au second appel de
l'entretien (question 6). Deux façons de faire :

- **une période complète d'abord** — sa progression dans chaque domaine, ses
  cahiers, ses PDF — puis les suivantes, une par une, en itérant. C'est la
  recommandation à annoncer : on juge sur pièce, imprimée, et une erreur de
  la première période ne se recopie pas dans les quatre autres ;
- **les cinq d'un coup**, pour qui veut voir l'année entière avant de la
  retoucher. Fabriquer alors période par période quand même, et contrôler
  chacune (couverture, pagination) avant de passer à la suivante.

## Repli : partir d'une classe par son adresse

Le chemin normal est « Partir de cette classe » (« Use this template ») et
le mode « enrichir » ci-dessus. Ce repli ne sert que pour une classe **qui
n'est pas un modèle** mais dont la licence permet la reprise : l'enseignant
a créé son dépôt depuis `moteur` et tape `/nouvelle-classe <adresse>` (son
site, son dépôt, ou sa carte de galerie).

1. **Lire sa fiche** dans `classes.json` du dépôt de la galerie
   (`galerie.depot`), ou à défaut le `classe.yml` de son dépôt : projet,
   niveau, milieux, licence, auteur, `depot`.
2. **L'entretien en repart** : le thème, les cinq milieux, le style du
   thème, les choix de matériel deviennent les **valeurs par défaut
   annoncées** de l'étape 1. Le niveau, l'année, la zone et le profil
   restent ceux de l'enseignant : toujours les demander, et ne jamais
   recopier le `calendrier` de la classe d'origine. Si le niveau change,
   même règle qu'en mode « enrichir » (point 6).
3. **Le contenu ne se copie que si la licence le permet** :
   - CC BY, CC BY-SA : on peut reprendre les progressions, les fiches, les
     choix d'espèces et de mots, en les adaptant ; une classe CC BY-SA reste
     CC BY-SA ;
   - CC BY-NC(-SA) : la même chose, et la nouvelle classe ne pourra jamais
     servir à un usage commercial — le dire, et le noter dans le README ;
   - tous droits réservés, ou licence absente : reprendre **seulement** le
     thème et les milieux, et réécrire tout le reste.
4. **Écrire `origine`** comme en mode « enrichir » (point 4), `depot` au
   dépôt courant, et citer l'auteur en tête du README. Les images gardent
   leurs propres crédits, à recopier avec elles.

## Étape 1 — L'entretien

Un ou deux appels `AskUserQuestion`, pas plus. Ne demander que **ce qui
change le résultat** ; pour le reste, prendre la valeur par défaut et
**l'annoncer** (« je pars sur 2 à 3 fiches par semaine, dis-moi si c'est trop »).

**Le ton, d'abord.** L'outil tutoie l'enseignant, comme entre collègues
(décidé le 18 octobre 2026), et le dit **une fois**, dans le texte de la
première question : « Je te tutoie, comme entre collègues — si tu préfères
le vous, dis-le-moi. » Puis il s'y tient, dans toutes les questions et tous
les messages. Si l'enseignant choisit le vous, passer au vous aussitôt et
l'écrire dans `classe.yml` (`ton: vous`), que les autres skills lisent. (La
page d'accueil de la plateforme, elle, vouvoie : elle s'adresse à tous les
enseignants avant qu'ils commencent.)

**Premier appel** (le cadre) :

1. **Le niveau** : PS, MS, GS, double niveau — avec ce que le moteur en fait
   (tableau ci-dessus).
2. **L'année scolaire et la zone de vacances** (A, B, C). La zone est **le
   seul réglage du calendrier** de la classe : `calendrier: {zone: X}` dans
   `classe.yml`. Les dates des trois zones sont dans le moteur
   (`referentiel/calendrier-<année>.yml`), relevées une fois pour toutes les
   classes dans le jeu de données officiel ; une année qui n'a pas encore
   son fichier se prépare d'abord dans le moteur (skill site-et-calendrier,
   « Changer d'année scolaire »). Ne jamais écrire de date dans
   `classe.yml`.
3. **Le thème de l'année** (partie de zéro ; en mode « enrichir », il est
   repris sans question) : la faune et la flore, ou un
   autre (la faune et la flore, les saisons, le tour du monde, les contes…). Proposer ensuite **un milieu ou
   un sous-thème par période**, cinq en tout, que l'enseignant corrige.
4. **Le matériel voulu** : fiches d'entraînement, fiches d'évaluation, imagier
   photographique, cartes de vocabulaire (choix multiples, tout coché par défaut).
   La réponse s'écrit dans `materiel` de classe.yml, avec les périodes de
   chaque cahier : l'accueil n'annonce que ce qui y figure, et
   `classe.py verifier` refuse un cahier déclaré qui n'est pas encore fabriqué.

**Second appel** — la question 6 se pose toujours ; la question 5
seulement si les réponses ne permettent pas de trancher :

5. **Le profil de la classe** : plus soutenu ou plus accessible ? (ici : « un
   quartier où les enfants ont de bonnes compétences », des exercices « un
   peu corsés »). Il règle la différenciation ★ / ★★.
6. **Par où commencer** : une période complète d'abord (recommandé), ou les
   cinq d'un coup (voir plus haut).

Les réglages que cette classe-ci avait fixés sans qu'on les demande (rythme
des fiches, codage A / EC / NE, nombre d'espèces de l'imagier, espèces
sensibles, albums, sorties, piscine, modèle de cursive, matériel de la
classe) sont listés dans `docs/vers-un-moteur.md` §3 : les reprendre comme
**valeurs par défaut annoncées**, et ne les poser en question que plus tard,
au moment où le matériel concerné se fabrique.

**Règles de l'entretien**, celles du dépôt :

- **le ton de `classe.yml`** (`tu` par défaut), **sans jargon** : dire « la liste numérotée du programme », pas
  « le référentiel » ; « vérifier que l'année couvre tout le programme »,
  pas « la couverture » ;
- **une question pédagogique à la fois** une fois l'entretien passé, et
  attendre la réponse plutôt que trancher seul ;
- **confirmer tout ce qui vient d'une dictée** avant de s'en servir (« SDG »
  était « SVG », « Poulepi » un poulpe et non un poussin) : un milieu, un
  album, un nom d'espèce se répètent à l'enseignant avant d'être écrits ;
- **aucune donnée d'élève** : ni prénom, ni liste ; l'effectif seulement s'il
  sert à estimer un volume d'impression.

## Étape 2 — Écrire la classe

1. **`classe.yml`** : nom, niveau, année, projet, accroche, `ton` (`tu`, ou
   `vous` si l'enseignant l'a demandé), `depot` (ce dépôt-ci,
   `propriétaire/dépôt`, tiré de `git remote get-url origin`), `origine` si
   la classe est partie d'une autre (mode « enrichir »), `moteur` (le dépôt modèle d'où vient
   ce dépôt et le commit copié : skill synchroniser-moteur), `calendrier`
   — la zone seule, plus un pont propre à l'école s'il y en a
   (`calendrier.ponts`), les dates venant du moteur —, les cinq `periodes` (clé, milieu,
   icône du sprite, couleur, phrase de l'imagier), la section `contenu` et
   la liste des `documents`. Puis :

   ```sh
   python3 scripts/classe.py generer    # site/classe.json et site/classe.js
   python3 scripts/classe.py verifier   # code 0 attendu
   ```
2. **Le dossier `classe/`** : `annotations.yml` vide de blocs pour commencer,
   `imagier.py` et `corpus.py` sur le modèle de ceux de la classe de départ
   (garder leur structure : les scripts en dépendent). Si le niveau n'a pas
   sa liste du programme, l'écrire d'abord dans `referentiel/` et pointer
   `contenu.referentiel` dessus.

## Étape 3 — Les documents de l'enseignant

Avec le skill **progressions-programme** : le projet annuel, la
programmation, les progressions de chaque domaine pour la période choisie,
la batterie d'évaluation. Chaque séance s'accroche à un attendu dans
`classe/annotations.yml`, et l'étape ne finit que quand

```sh
python3 scripts/couverture.py    # code 0 : rien ne manque pour ce qui est écrit
```

est vert. Une séance sans accroche n'est pas comptée.

## Étape 4 — Les cahiers

Dans l'ordre, chacun avec son skill, et seulement le matériel demandé :

- **fiches-eleve** (+ **fiches-illustrations** pour les images) : évaluation
  et entraînement de la période ;
- **imagier-photos** : les espèces du milieu, choisies à l'œil sur planche,
  jamais par tri automatique ;
- **cartes-corpus** : les mots des trois corpus de la période.

Un cahier entre dans `materiel` (classe.yml) quand sa page existe — pas avant :
une période encore vide n'est annoncée nulle part, et les générateurs la sautent
en le disant.

Le style des cahiers est **celui de la classe** (étape 5), pas celui du
moteur. La police des mots de l'enfant (Andika) et les règles d'impression
ne changent pas.

## Étape 5 — Le style

Chaque classe a **son** design system, fait avec l'enseignant (décidé le
18 octobre 2026) : la galerie doit montrer des classes vraiment
différentes. La marche complète, et le contrat du thème, sont dans le skill
**charte-graphique** (« Créer le design system d'une classe ») ; ici,
l'essentiel de l'entretien.

1. **Une question** (une seule, `AskUserQuestion`) : l'univers qui lui
   ressemble, tiré du thème de l'année, avec deux ou trois exemples
   concrets — pour le tour du monde : « un carnet de voyage, avec tampons et
   étiquettes de bagage », « l'affiche d'une gare, avec ses billets »,
   « l'album de cartes postales ». Jamais le cliché du thème (la carte au
   trésor, l'ancre marine) ; chercher les objets qu'un enfant de cinq ans
   manipule. Ses goûts déclarés (couleurs, « pas trop chargé ») passent
   avant.
2. **Deux ou trois directions nettement distinctes** — polices, ornements,
   couverture, frise différents, pas trois palettes du même gabarit —,
   chacune dans `site/charte/themes/<nom>/`, acceptée par
   `python3 scripts/verifier-theme.py <nom>`.
3. **Les montrer en captures, sur de vraies pages** : l'accueil (1280 et
   390 px), une fiche, une carte d'imagier, une couverture — et la fiche et
   la couverture **au PDF**, aussi en niveaux de gris (la photocopie).
   Tant que la classe n'a pas de cahier, les montrer sur le contenu d'une
   autre classe, assemblé dans le scratchpad. Dire en une phrase ce que
   chaque direction a pour elle.
4. **L'enseignant choisit, puis ajuste** (une retouche à la fois, montrée
   aussitôt). Le style s'écrit dans `themes/<thème>/` — le verdict dans
   `theme.yml` et le message de commit —, `theme: <thème>` dans
   `classe.yml`, et les directions écartées sortent du dépôt.

S'il ne veut pas s'en occuper maintenant : garder le thème neutre (`demo`)
et le dire ; le style peut venir plus tard, sans rien refaire d'autre.

## Étape 6 — Finir par le PDF

Skill **imprimer-pdf** : fabriquer les PDF, puis
`python3 scripts/verifier-pagination.py` — une page par fiche et par
planche. **Le HTML ne prouve rien** : les pires défauts de ce matériel
n'existaient qu'imprimés. Montrer ensuite à l'enseignant une planche de
chaque cahier, et écrire son verdict dans le message de commit.

## Étape 7 — Mettre le site en ligne

Skill **site-et-calendrier**. Réécrire la tête du `README.md` avec le nom de
la classe et le lien de son site, tiré du remote. Rappeler à l'enseignant,
en deux phrases et sans technique, les deux gestes qu'aucune session ne peut
faire à sa place : le dépôt doit être **public**, et GitHub Pages doit être
réglé sur **GitHub Actions** (Settings → Pages) ; sans cela, le premier
déploiement échoue.

## Garde-fous

- **Le moteur ne se modifie pas pour du contenu.** S'il manque une capacité
  (un double niveau, un nouveau type de cahier), l'ajouter de façon
  générique, sans un mot de la classe dedans — `classe.py verifier` vert —
  et la noter dans `docs/vers-un-moteur.md`.
- **Une modification faite à la main par l'enseignant n'est jamais écrasée**
  par une régénération : relire avant de régénérer.
- **Licences** : CC0, domaine public, CC BY, CC BY-SA ; jamais ND ; NC
  pour les seuls pictogrammes ARASAAC, crédités (CLAUDE.md, « Images »).
- Une période juste et imprimée vaut mieux que cinq approximatives — même
  quand l'enseignant a choisi les cinq d'un coup.
- **La classe reste dans le dépôt de l'enseignant** : « mettre en ligne »,
  c'est son propre site. La montrer dans la galerie de la plateforme est un
  autre geste, volontaire (skill partager-ma-classe), à ne jamais proposer
  de soi-même.

## Enchaînement

**nouvelle-classe** → site-et-calendrier (dates) → progressions-programme
(couverture verte) → fiches-eleve + fiches-illustrations → imagier-photos →
cartes-corpus → charte-graphique (le style : deux ou trois directions, le choix de
l'enseignant) → imprimer-pdf → mettre
le site en ligne → **capitaliser**. Ensuite, la vie de la classe :
**retours-enseignant** (les retours, une question à la fois),
**remonter-au-moteur** (ce qui vaut pour toutes les classes),
**synchroniser-moteur** (les nouvelles versions du moteur), et, si
l'enseignant le veut, **partager-ma-classe** (la galerie).
