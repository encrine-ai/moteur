---
name: partager-ma-classe
description: Partager sa classe dans la galerie de la plateforme (« Les classes »), si l'enseignant le veut — vérifier d'abord que tout est juste et partageable (programme couvert, une page par fiche, licences des images, aucun prénom d'élève ni photo de classe, aucun album ni chanson recopié : scripts/verifier-partage.py), préparer la fiche de la classe (titre, niveau, périodes, auteur, licence, faits vérifiés, commit), recueillir son accord explicite, puis proposer la classe à la galerie par une demande que l'agent galerie relit et que le propriétaire de la plateforme accepte. Une fois acceptée, la galerie montre une COPIE RELUE de la classe, hébergée par Encrine (https://encrine.ai/<id>/), dont on peut partir ; la classe et le site de l'enseignant restent à lui, et ses changements n'arrivent dans la copie qu'après une nouvelle relecture. Couvre aussi la mise à jour de la copie et le retrait. À utiliser seulement à la demande : « je voudrais partager ma classe », « on peut la mettre dans la galerie ? », « je suis fière de ma classe, d'autres pourraient s'en servir », « montre ma classe aux autres enseignants », « mets à jour ma classe dans la galerie », « la galerie montre une vieille version de ma classe », « retire ma classe de la galerie », « /partager-ma-classe ». Ne concerne pas les retours sur l'outil (retours-enseignant, remonter-au-moteur).
---

# Partager ma classe

La galerie de la plateforme montre ce que les enseignants ont fait, pour
donner des idées : chaque classe partagée y a une carte, aux couleurs de son
thème, avec deux gestes — **voir la classe** et **partir de cette classe**.

Décidé par le propriétaire de la plateforme : la galerie montre une **copie
relue**. Quand une classe est acceptée, l'agent de la galerie
en fait une **copie dans l'organisation `encrine-ai`, au commit exact qui a
été relu**, servie sur `https://encrine.ai/<id>/` ; c'est cette copie que
montre la carte, et c'est d'elle que part « Partir de cette classe ».
Ainsi, ce que voient les autres enseignants est toujours ce que quelqu'un a
relu, même si la classe d'origine change le lendemain. Et :

- **on partage si on le veut** : ce skill ne se lance qu'à la demande de
  l'enseignant, jamais de lui-même, jamais en fin d'un autre travail ;
- **les contrôles d'abord, puis une relecture** : l'agent de la galerie
  relit la classe au commit annoncé, et le propriétaire de la plateforme
  accepte ou non ;
- **la classe et le site de l'enseignant restent à lui** : il continue d'y
  travailler comme avant. La copie ne bouge pas toute seule : ses
  changements n'y arrivent qu'après **une nouvelle relecture**, qu'il
  demande quand il veut (étape 5) ;
- **rien ne part sans son accord explicite** (étape 3), et il retire sa
  classe quand il veut (étape 6).

À lui dire, en une phrase, dès qu'il demande : « Une copie relue de ta
classe est montrée dans la galerie ; tes changements y arrivent après une
nouvelle relecture. »

Parler sans jargon : dire
« la galerie », « ta fiche », « la personne qui relit », « la copie »,
jamais « pull request », « JSON », « merge », « fork ».

## 0. Où partager

Lire `galerie.depot` dans `classe.yml` : le dépôt de la galerie d'Encrine
(`encrine-ai/encrine-ai.github.io`), où arrive la demande. S'il manque —
une classe d'avant ce champ ; `classe.py verifier` le signale —, le
reprendre du modèle (`galerie: {depot: encrine-ai/encrine-ai.github.io}`)
et le dire en une phrase, sans en faire une question.

Avant tout :

- `depot` doit être renseigné dans `classe.yml` (`propriétaire/dépôt`,
  celui de `git remote get-url origin`) : la relecture part de ce dépôt.
  `classe.py verifier` le signale s'il manque ;
- **le travail est sur `main`, envoyé, et le site en ligne est à jour** :
  la relecture porte sur un commit précis (`git rev-parse origin/main`), et
  vérifie que le site publié est bien celui de ce commit. Un travail en
  cours se finit d'abord ; un déploiement rouge se répare d'abord (skill
  site-et-calendrier) ;
- `moteur.version` est connue (skill synchroniser-moteur, étape 0, si elle
  vaut `null`) : la demande la porte.

## 1. Vérifier — rien ne se partage s'il reste du rouge

Dans cet ordre, chacun vert avant le suivant :

| Contrôle | Ce qu'il garantit | Si c'est rouge |
|---|---|---|
| `python3 scripts/couverture.py` | l'année couvre tout le programme | skill progressions-programme |
| `bash scripts/generer-pdf.sh <site>` puis `python3 scripts/verifier-pagination.py <site>` | une page par fiche, une page par planche | skill imprimer-pdf |
| `python3 scripts/verifier-imagier.py`, `python3 scripts/verifier-cartes-corpus.py` | la bonne espèce, le bon mot, les crédits | skills imagier-photos, cartes-corpus |
| `python3 scripts/chercher-pictos.py verifier` | chaque pictogramme a sa licence | skill fiches-illustrations |
| `python3 scripts/verifier-partage.py` | aucun prénom d'élève, aucune photo de classe ni scan, aucun album ni chanson recopié | voir ci-dessous |

**Les licences.** Les pictogrammes ARASAAC sont sous licence « pas d'usage
commercial » (NC) : ils se partagent, mais **le dire** sur la fiche (champ
`licence_note`), parce qu'une classe qui en contient ne peut pas servir de
base à un matériel vendu. Une image ND (pas de modification) ne passe jamais.

**`verifier-partage.py` signale un prénom.** Demander, une question à la fois,
avec l'outil de questions interactives de l'agent s'il en a un (`AskUserQuestion` dans Claude Code), sinon une question à la fois dans la conversation : « Je vois le prénom Léa dans les problèmes de
mathématiques. Est-ce un personnage inventé, ou un élève de ta classe ? »
Inventé : l'ajouter à `partage.prenoms_fictifs` dans `classe.yml`. Un élève :
le remplacer partout par un prénom inventé (le skill du document concerné),
puis relancer. **Ne jamais déclarer un prénom fictif sans la réponse de
l'enseignant.**

**Il signale une image** : c'est une photo de classe, une production d'élève
ou une page scannée. La retirer, ou la remplacer par une image des banques
libres (skills fiches-illustrations, imagier-photos). Une photo d'enfant ne
se partage jamais, même floutée.

**Il signale un texte recopié** (des paroles, une page d'album) : garder le
titre et l'auteur, retirer le texte. Si c'est une comptine du domaine public
ou un texte écrit par l'enseignant, le déclarer dans
`partage.textes_autorises` (`{debut: <premiers mots>, raison: <pourquoi>}`),
après lui avoir posé la question.

Noter les chiffres que ces contrôles viennent de donner (les attendus
couverts, le nombre de PDF de `verifier-pagination.py`) : ce sont eux, et
eux seuls, qui vont sur la fiche. Si un contrôle a demandé une correction,
la committer et l'envoyer sur `main`, attendre le déploiement, et refaire
les contrôles sur ce nouveau commit.

## 2. Préparer la fiche de la classe

La fiche a **les noms de champs des cartes de la galerie** (`classes.json`
de `galerie.depot`, décrit dans son `README.md`) : la personne qui relit
n'a rien à traduire. Un enregistrement :

```json
{
  "titre": "<classe.yml : projet>",
  "niveau": "<classe.yml : niveau.libelle>",
  "annee": "<classe.yml : annee>",
  "zone": "<classe.yml : calendrier.zone>",
  "accroche": "<classe.yml : accroche, une ou deux phrases>",
  "semaines": 36,
  "milieux": [{"nom": "<periodes[].milieu, minuscule initiale : « l’Europe »>", "couleur": "<--p1 … --p5 du thème, en hex>", "semaines": 7}],
  "auteur": "<le nom choisi ici>",
  "licence": "CC BY-SA 4.0",
  "licence_note": "sauf les pictogrammes ARASAAC, sous CC BY-NC-SA",
  "site": "<https://<propriétaire>.github.io/<dépôt>/, ou `site` de classe.yml>",
  "depot": "<propriétaire>/<dépôt>",
  "origine": {"depot": "<classe.yml : origine.depot>", "titre": "…", "auteur": "…"},
  "verifie": {"attendus": "159/159", "pdf": 65, "pagination": true, "le": "AAAA-MM-JJ", "commit": "<sha de origin/main, 40 caractères>"},
  "partagee_le": "AAAA-MM-JJ"
}
```

- **Pas d'`id`** : c'est la galerie qui le choisit (le nom de la copie,
  `encrine-ai/<id>`, et son adresse, `https://encrine.ai/<id>/`), et le dit
  dans sa réponse.
- **`site` et `depot`** sont ceux **de la classe de l'enseignant** : c'est
  là que la relecture commence. Sur la carte publiée, la galerie les
  remplace par ceux de la copie relue, et garde les siens comme source
  (« Par <auteur> » mène à son dépôt). La copie garde dans son `classe.yml`
  le `depot` de l'enseignant : la classe qui partira d'elle le créditera
  (`origine`, skill nouvelle-classe).
- **`milieux`** : une entrée par période, dans l'ordre ; son `semaines` est
  le nombre que son site affiche pour la période dans sa zone (« … · 7
  semaines »). **`semaines`**, au premier niveau, est le total de l'année :
  la somme des `semaines` des milieux. Les couleurs viennent du thème de la classe
  (`site/charte/themes/<theme>/theme.css`, `--p1` … `--p5`), pas de la
  marque : la carte porte le style de la classe.
- **`accroche`** : celle de `classe.yml` si elle se lit seule ; sinon une
  ou deux phrases à lui proposer, ou rien.
- **`licence_note`** : les exceptions à la licence, en une phrase (les
  pictogrammes ARASAAC) ; rien s'il n'y en a pas.
- **`origine`** : seulement si la classe est elle-même partie d'une autre
  (`origine` dans `classe.yml`) ; la carte crédite alors l'original.
- **`verifie`** : les faits que les contrôles de l'étape 1 viennent de
  produire (`pdf` : le total que donne `verifier-pagination.py`), jamais de mémoire, et **le commit** sur lequel ils ont tourné
  (`git rev-parse origin/main`, en entier, celui du site en ligne) — c'est ce commit
  que la galerie relit et copie. La galerie refait ses propres contrôles
  et écrit les siens sur la carte ; un écart se signale.
- **`partagee_le`** : la date de la demande.
- La zone n'est qu'une information pour qui regarde : « partir de cette
  classe » ne la reprend jamais, et redemande toujours la sienne à
  l'enseignant (skill nouvelle-classe).
- **L'auteur** : partir de **sa signature** (`enseignant.signature` de
  `classe.yml`, celle que montre déjà son site : « La classe de Mme
  Martin ») et la lui proposer comme auteur de la carte — « Je reprends ta
  signature, Mme Martin, comme auteur : ça te va ? ». S'il n'a pas signé, ou
  veut autre chose, demander comment il veut apparaître — son nom, un
  pseudonyme (« Maîtresse des Écureuils »), ou le nom de l'école (en
  rappelant que l'école se reconnaît). Jamais d'adresse électronique,
  jamais un prénom d'élève. S'il change de signature, l'écrire aussi dans
  `enseignant.signature`, pour que le site et la carte disent la même
  chose.
- **La licence**, à expliquer simplement, en recommandant la première :

  | Licence | Ce qu'elle permet aux autres |
  |---|---|
  | **CC BY-SA 4.0** (recommandée) | réutiliser et modifier ta classe, même pour un usage payant, en te citant et en partageant leurs modifications sous la même licence |
  | CC BY 4.0 | la même chose, sans l'obligation de partager sous la même licence |
  | CC BY-NC-SA 4.0 | réutiliser et modifier, en te citant, mais jamais pour un usage commercial — ta classe se montre sans « Partir de cette classe » |
  | Tous droits réservés | regarder seulement — ta classe se montre sans « Partir de cette classe » |

  Une classe partie d'une classe **CC BY-SA** (`origine.licence`) reste
  **CC BY-SA** : ne pas proposer d'autre choix, et le dire.

Écrire la licence et l'auteur dans `classe.yml` (`partage.licence`,
`partage.auteur`) et dans `LICENCE-CONTENU.md` à la racine (la licence, son
lien, l'auteur, et le crédit de `origine` s'il y en a une) : c'est là que le
mode « enrichir » de nouvelle-classe les lira, dans la classe qui partira
de la copie. Ces deux fichiers changent la classe : les committer et les
envoyer sur `main` **avant** de fixer `verifie.commit`, attendre le
déploiement, puis prendre ce commit-là (les contrôles de l'étape 1 n'ont
pas à être refaits pour ces seules lignes). La fiche elle-même se garde
dans `partage/fiche.json`, committée après la demande : elle ne peut pas
contenir le commit qui la contient, et la galerie relit le commit annoncé,
pas ce qui le suit.

**Aucune case « Template repository » à cocher** dans le dépôt de
l'enseignant : on part de la copie relue, que la galerie marque elle-même
comme modèle quand la licence le permet. Si la case est cochée, elle peut
le rester ; si la licence est NC ou tous droits réservés, proposer de la
décocher (une copie par « Use this template » reprendrait tout le contenu,
ce que la licence n'autorise pas).

## 3. Demander l'accord — une phrase explicite, rien de public sans un oui

Montrer la fiche en clair (le titre, les périodes, le nom affiché, la
licence, ce qui sera visible), puis lui lire **ce qu'il accepte**, en mots
simples, avec son nom et sa licence dedans :

> « J'accepte qu'Encrine héberge une copie de ma classe telle qu'elle aura
> été relue, la montre dans la galerie « Les classes » sous le nom
> « <auteur> », et que d'autres enseignants en partent selon sa licence
> (<licence>). Je peux la retirer à tout moment. »

Et la question, avec l'outil de questions interactives de l'agent s'il en a
un (`AskUserQuestion` dans Claude Code), sinon dans la conversation :
*Oui, j'accepte et je propose ma classe* / *Pas maintenant*. Dire ce qui se
passe ensuite : « Une personne relit avant que ta classe apparaisse. Ce qui
sera montré, c'est une copie de ta classe telle qu'elle est aujourd'hui ; ta
classe et ton site restent à toi. » Un « pas maintenant » est respecté : ne
pas reposer la question dans la séance.

Ce oui ne suffit pas à lui seul : **l'accord se donne sur le formulaire de
la galerie, de sa main**. Ses trois cases (l'accord ci-dessus, « aucune
donnée d'élève », « chaque image et chaque texte peuvent être partagés ») ne
se préremplissent pas, et c'est voulu : seul l'enseignant, depuis son
compte, peut les cocher. Le lui dire avant de donner le lien (étape 4).

## 4. Proposer la classe à la galerie

La demande est une **issue sur `galerie.depot`, ouverte par le formulaire
« Proposer ma classe »** de la galerie, prérempli par un lien. Ses champs :

| Champ du formulaire | Ce qu'on y met |
|---|---|
| `classe` | `depot` de `classe.yml` (`propriétaire/dépôt`) |
| `site` | le site de la classe (`site` de la fiche) |
| `commit` | `verifie.commit` : le commit relu et copié |
| `marque` | `<!-- partage v1 genre=<ajout\|mise-a-jour\|retrait> classe=<propriétaire/dépôt> commit=<sha> moteur=<moteur.version> -->` (`moteur=inconnue` si on n'a pas pu la reconstituer, jamais `null`) |
| `fiche` | la fiche de l'étape 2, en JSON |
| `controles` | chaque contrôle de l'étape 1 et son résultat chiffré, sur ce commit |

```python
import urllib.parse
lien = "https://github.com/%s/issues/new?" % galerie_depot + urllib.parse.urlencode({
    "template": "proposer-ma-classe.yml",
    "title": "Partage : %s (%s)" % (titre, niveau),
    "classe": depot, "site": site, "commit": commit,
    "marque": marque, "fiche": fiche_json, "controles": controles,
}, quote_via=urllib.parse.quote)
```

Titre : **« Partage : <titre> (<niveau>) »** pour un ajout ;
**« Partage (mise à jour) : <titre> (<niveau>) »** pour une mise à jour
(étape 5). Au-delà de 8 000 caractères, raccourcir `controles` (les lignes
de résultat seulement), jamais la fiche.

Le donner **en une phrase, avec les cases** : « Un clic pour proposer ta
classe : … — en bas du formulaire, coche les trois cases (ton accord, aucune
donnée d'élève, des images et des textes partageables), puis *Submit new
issue*. » Il l'envoie **de son compte GitHub**, celui de sa classe : la
galerie ne partage pas la classe de quelqu'un d'autre. La session n'ouvre
pas l'issue à sa place, même si elle en a les droits : les cases sont son
accord.

Puis le dire simplement : « Quand tu l'auras envoyé, une personne relira ta
classe ; une copie apparaîtra dans la galerie si elle est acceptée. »

**Une fois la classe publiée** (la galerie le dit sur l'issue, avec
l'adresse de la copie, `https://encrine.ai/<id>/`) : écrire cette adresse
dans `classe.yml`, `partage.carte`, puis `python3 scripts/classe.py
generer`. Le bloc de tête du README de la classe y renvoie (« Dans la
galerie d'Encrine ») : « Partir de cette classe » ne mène qu'à la copie
relue, jamais au dépôt de l'enseignant. Au retrait (étape 6), vider
`partage.carte`.

## 5. Mettre à jour sa classe dans la galerie

La copie de la galerie est celle du commit relu : elle ne suit pas la
classe toute seule. L'enseignant dit « mets à jour ma classe dans la
galerie », ou s'étonne que la galerie montre une vieille version : le lui
expliquer d'une phrase (« La galerie montre la copie relue de ta classe ; tes
changements y arrivent après une nouvelle relecture. »), puis :

1. les contrôles de l'étape 1, sur le nouveau commit (`origin/main`, site
   en ligne à jour) ;
2. la fiche refaite (étape 2) : les faits du jour, le nouveau
   `verifie.commit`, et ce qui a changé (titre, périodes, auteur, licence) ;
   une licence ne se resserre pas pour ceux qui sont déjà partis de la
   copie : ils gardent celle qu'ils ont reçue ;
3. l'accord, redemandé en une question (étape 3) : il porte sur la copie
   telle qu'elle sera relue, donc sur ce nouveau commit ;
4. la demande (étape 4), même formulaire, `genre=mise-a-jour`, titrée
   « Partage (mise à jour) : … », dont les contrôles disent aussi, en une
   ligne, ce qui a changé depuis la dernière copie relue — et les trois
   cases, à recocher de sa main.

La copie garde sa version précédente tant que la nouvelle n'est pas relue
et acceptée.

## 6. Retirer sa classe

L'enseignant dit « retire ma classe de la galerie » : c'est sans
discussion. Lui donner un lien prérempli simple (sans formulaire), une
issue sur `galerie.depot` titrée « Retrait : <titre> », dont le corps
commence par la marque `genre=retrait` (`commit` = `origin/main`) et dit
« à la demande de l'auteur » ; il l'envoie de son compte, comme pour
l'ajout. (Le formulaire « Signaler une classe » de la galerie, choix « Je
suis l'auteur : retirez ma classe », fait la même chose.) La galerie sort la
carte et coupe le site de la copie. Supprimer `partage/fiche.json`, vider
`partage.carte` et relancer `classe.py generer`. Lui dire
ce qui reste : son site et son dépôt sont à lui, et ne bougent pas ; ceux
qui sont déjà partis de la copie gardent leur propre classe, avec le crédit
que demande la licence.

## Garde-fous

- Jamais de partage sans la demande puis le oui de l'enseignant, et
  jamais une case d'accord cochée à sa place : il envoie le formulaire
  lui-même.
- Jamais un prénom d'élève, une photo d'enfant, une production d'élève, un
  texte d'album ou de chanson recopié, une adresse électronique.
- Jamais de faits de mémoire : seulement la sortie des contrôles du jour,
  sur le commit annoncé.
- Ne rien promettre de la copie : c'est la galerie qui la relit, la copie
  et la montre ; on ne pousse jamais dans `encrine-ai`.
- La classe de l'enseignant reste la sienne : rien n'y change par le
  partage, sauf `partage/`, `partage.licence`, `partage.auteur` et
  `LICENCE-CONTENU.md`.

## Enchaînement

L'enseignant le demande → **partager-ma-classe** (contrôles de l'étape 1,
avec imprimer-pdf pour le PDF) → l'agent de la galerie relit, le
propriétaire accepte, la copie relue apparaît. Une autre classe part de
cette copie par « Partir de cette classe » (« Use this template ») puis
**nouvelle-classe** (mode « enrichir »). Une idée pour l'outil lui-même,
pas pour la galerie → remonter-au-moteur.
