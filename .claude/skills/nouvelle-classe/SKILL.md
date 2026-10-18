---
name: nouvelle-classe
description: Le skill d'amorçage du moteur — transformer ce dépôt en LA classe d'un autre enseignant, à partir d'un court entretien (niveau, double niveau, année et zone de vacances, thème de l'année et milieu de chaque période, matériel voulu, profil de la classe, diffusion gratuite ou payante), puis écrire classe.yml et le contenu, réécrire le projet, la programmation et les progressions jusqu'à ce que le programme soit couvert, fabriquer les cahiers et finir par le PDF. À utiliser quand quelqu'un veut sa propre version : « je veux faire ma classe », « crée une classe de moyenne section », « adapte tout ça pour ma GS de l'an prochain, zone B », « je voudrais le même matériel mais sur le thème des contes », « j'ai une classe de MS-GS », « /nouvelle-classe », « on repart de zéro pour une autre école », « je voudrais partir de la classe des contes de la galerie », « fais-moi la même que celle-ci : <lien> ». Ne concerne pas une retouche de la classe actuelle (une séance, une fiche, une image, une date : voir les skills de chaque matériel).
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
l'entretien (question 7). Deux façons de faire :

- **une période complète d'abord** — sa progression dans chaque domaine, ses
  cahiers, ses PDF — puis les suivantes, une par une, en itérant. C'est la
  recommandation à annoncer : on juge sur pièce, imprimée, et une erreur de
  la première période ne se recopie pas dans les quatre autres ;
- **les cinq d'un coup**, pour qui veut voir l'année entière avant de la
  retoucher. Fabriquer alors période par période quand même, et contrôler
  chacune (couverture, pagination) avant de passer à la suivante.

## Partir d'une classe de la galerie

L'enseignant peut donner le lien d'une classe partagée dans la galerie de la
plateforme (« partir de cette classe », skill partager-ma-classe) : son
site, son dépôt, ou sa carte. Décidé le 18 octobre 2026 :

1. **Lire sa fiche** dans `classes.json` du dépôt de la galerie
   (`galerie.depot`), ou à défaut le `classe.yml` de son dépôt : projet,
   niveau, milieux, licence, auteur.
2. **L'entretien en repart** : le thème, les cinq milieux, le style du
   thème, les choix de matériel deviennent les **valeurs par défaut
   annoncées** de l'étape 1 (« je reprends le thème des contes et ses cinq
   milieux ; dis-moi ce que tu veux changer »). Le niveau, l'année, la zone
   et le profil de la classe restent ceux de l'enseignant : toujours les
   demander. **La zone surtout se redemande toujours**, même quand la classe
   d'origine en a une (sa fiche de galerie la donne) : la nouvelle classe
   a **ses** vacances. Ne jamais recopier le `calendrier` de la classe
   d'origine.
3. **Le contenu ne se copie que si la licence le permet** :
   - CC BY, CC BY-SA : on peut reprendre les progressions, les fiches, les
     choix d'espèces et de mots, en les adaptant ; une classe CC BY-SA reste
     CC BY-SA ;
   - CC BY-NC(-SA) : la même chose, et la nouvelle classe ne pourra jamais
     servir à un usage commercial — le dire, et le noter dans le README ;
   - tous droits réservés, ou licence absente : reprendre **seulement** le
     thème et les milieux (une idée ne se protège pas), et réécrire tout le
     reste.
4. **Citer l'auteur** dans le README de la nouvelle classe, en tête :
   « D'après *<projet>*, de <auteur> (<lien du site>), sous licence
   <licence>. » Et ne rien reprendre de ce qui n'est pas à l'auteur : les
   images gardent leurs propres crédits, à recopier avec elles.
5. Le reste — les séances, les fiches, les retouches — reste à la main de
   l'enseignant, comme pour une classe partie de zéro.

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
3. **Le thème de l'année** : reprendre celui de la classe d'origine, ou un
   autre (la faune et la flore, les saisons, le tour du monde, les contes…). Proposer ensuite **un milieu ou
   un sous-thème par période**, cinq en tout, que l'enseignant corrige.
4. **Le matériel voulu** : fiches d'entraînement, fiches d'évaluation, imagier
   photographique, cartes de vocabulaire (choix multiples, tout coché par défaut).
   La réponse s'écrit dans `materiel` de classe.yml, avec les périodes de
   chaque cahier : l'accueil n'annonce que ce qui y figure, et
   `classe.py verifier` refuse un cahier déclaré qui n'est pas encore fabriqué.

**Second appel** — la question 7 se pose toujours ; les questions 5 et 6
seulement si les réponses ne permettent pas de trancher :

5. **Le profil de la classe** : plus soutenu ou plus accessible ? (ici : « un
   quartier où les enfants ont de bonnes compétences », des exercices « un
   peu corsés »). Il règle la différenciation ★ / ★★.
6. **La diffusion** : matériel gratuit, ou vendu un jour ? Payant interdit les
   pictogrammes ARASAAC (licence NC) : seules les sources libres du skill
   fiches-illustrations restent permises.
7. **Par où commencer** : une période complète d'abord (recommandé), ou les
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
   `vous` si l'enseignant l'a demandé), `moteur` (le dépôt modèle d'où vient
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
  seulement si la diffusion reste gratuite (CLAUDE.md, « Images »).
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
