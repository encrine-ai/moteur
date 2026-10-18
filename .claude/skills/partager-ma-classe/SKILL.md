---
name: partager-ma-classe
description: Partager sa classe dans la galerie de la plateforme (« Les classes »), si l'enseignant le veut — vérifier d'abord que tout est juste et partageable (programme couvert, une page par fiche, licences des images, aucun prénom d'élève ni photo de classe, aucun album ni chanson recopié : scripts/verifier-partage.py), préparer la fiche de la classe (projet, niveau, milieux, auteur, licence, faits vérifiés), demander son accord, puis proposer la classe à la galerie par une demande de fusion que le propriétaire de la plateforme relit. La classe reste dans le dépôt de l'enseignant : la galerie n'en montre qu'un lien. Explique aussi comment la retirer. À utiliser seulement à la demande : « je voudrais partager ma classe », « on peut la mettre dans la galerie ? », « je suis fière de ma classe, d'autres pourraient s'en servir », « montre ma classe aux autres enseignants », « retire ma classe de la galerie », « /partager-ma-classe ». Ne concerne pas les retours sur l'outil (retours-enseignant, remonter-au-moteur).
---

# Partager ma classe

La galerie de la plateforme montre ce que les enseignants ont fait, pour
donner des idées : chaque classe partagée y a une carte, aux couleurs de son
thème, avec deux gestes — **voir la classe** (son site, chez son auteur) et
**partir de cette classe**. Décidé le 18 octobre 2026 : chaque classe
partagée qui le permet est elle-même un **dépôt-modèle GitHub** (« Template
repository ») ; « partir de cette classe », c'est « Use this template » sur
son dépôt, puis `/nouvelle-classe` sans adresse (skill nouvelle-classe,
mode « enrichir »). Le site d'une classe-modèle continue de se publier : le
déploiement ne saute que pour le dépôt du moteur lui-même. Et :

- **on partage si on le veut** : ce skill ne se lance qu'à la demande de
  l'enseignant, jamais de lui-même, jamais en fin d'un autre travail ;
- **les contrôles d'abord, puis une personne relit** : pour commencer, le
  propriétaire de la plateforme, qui accepte ou non la demande de fusion ;
- **rien n'est copié** : la galerie garde un lien vers le site de
  l'enseignant ; la classe reste dans son dépôt, et il la retire quand il veut.

Parler sans jargon, en suivant `ton` dans `classe.yml` (tu par défaut) : dire
« la galerie », « ta fiche », « la personne qui relit », jamais « pull
request », « JSON », « merge ».

## 0. Où partager

Lire `galerie.depot` dans `classe.yml`. **À définir** : la galerie n'existe
pas encore. Faire quand même les contrôles et la fiche (étapes 1 et 2), les
garder sous `partage/fiche.json` dans la classe, et le dire : « Tout est
prêt ; la galerie n'est pas encore ouverte, je la proposerai dès qu'elle le
sera. »

Avant tout, `depot` doit être renseigné dans `classe.yml`
(`propriétaire/dépôt`, celui de `git remote get-url origin`) : la fiche de
galerie en tire ses liens. `classe.py verifier` le signale s'il manque.

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
`restrictions`), parce qu'une classe qui en contient ne peut pas servir de
base à un matériel vendu. Une image ND (pas de modification) ne passe jamais.

**`verifier-partage.py` signale un prénom.** Demander, une question à la fois,
avec `AskUserQuestion` : « Je vois le prénom Léa dans les problèmes de
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

## 2. Préparer la fiche de la classe

Le format est celui de `classes.json` dans le dépôt de la galerie, un
enregistrement par classe :

```json
{
  "id": "<propriétaire>-<dépôt>",
  "projet": "<classe.yml : projet>",
  "niveau": "<classe.yml : niveau.libelle>",
  "annee": "<classe.yml : annee>",
  "zone": "<classe.yml : calendrier.zone>",
  "milieux": [{"nom": "<periodes[].milieu>", "couleur": "<--p1 … --p5 du thème, en hex>"}],
  "auteur": "<nom ou pseudonyme, au choix de l'enseignant>",
  "licence": "CC BY-SA 4.0",
  "restrictions": ["pictogrammes ARASAAC : pas d'usage commercial"],
  "site": "https://<propriétaire>.github.io/<dépôt>/",
  "depot": "<propriétaire>/<dépôt>",
  "modele": true,
  "origine": {"depot": "<classe.yml : origine.depot>", "titre": "…", "auteur": "…"},
  "faits": {"attendus": "159/159", "pdf": <le total que donne verifier-pagination.py, 65 pour une GS complète>, "pagination": "vérifiée", "moteur": "<moteur.version>"},
  "partage_le": "AAAA-MM-JJ"
}
```

- **`depot`** est `classe.yml : depot`, sous la forme `propriétaire/dépôt`.
  La page d'accueil de la galerie en tire le lien du dépôt
  (`https://github.com/<depot>`) et, si `modele` est vrai, celui du bouton
  « Partir de cette classe » :
  `https://github.com/new?template_owner=<propriétaire>&template_name=<dépôt>`.
- **`modele`** : `true` seulement si la licence permet la reprise (CC BY ou
  CC BY-SA) **et** que l'enseignant a coché « Template repository »
  (étape 2 bis) ; sinon `false`, et la carte se montre sans « Partir de
  cette classe ».
- **`origine`** : seulement si la classe est elle-même partie d'une autre
  (`origine` dans `classe.yml`) ; la carte crédite alors l'original.
- La zone n'est qu'une information pour qui regarde : « partir de cette
  classe » ne la reprend jamais, et redemande toujours la sienne à
  l'enseignant (skill nouvelle-classe).
- Les couleurs viennent du thème de la classe
  (`site/charte/themes/<theme>/theme.css`, `--p1` … `--p5`), pas de la
  marque : la carte de la galerie porte le style de la classe.
- Les **faits** sont ceux que les contrôles de l'étape 1 viennent de
  produire, jamais de mémoire.
- **L'auteur** : demander comment il veut apparaître — son nom, un
  pseudonyme (« Maîtresse des Écureuils »), ou le nom de l'école. Jamais
  d'adresse électronique, jamais un prénom d'élève.
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
de celle-ci. Écrire la fiche dans `partage/fiche.json` de la classe.

## 2 bis. Faire de la classe un modèle — seulement si la licence le permet

- **CC BY ou CC BY-SA** : demander à l'enseignant, en une phrase et sans
  technique, le seul geste qu'aucune session ne peut faire à sa place :
  « Dans ton dépôt sur GitHub, ouvre **Settings → General**, et coche
  **Template repository**, juste sous le nom du dépôt. C'est ce qui fait
  marcher le bouton « Partir de cette classe ». » Attendre qu'il dise que
  c'est fait (`gh api repos/<depot> --jq .is_template` le confirme quand
  `gh` répond), puis mettre `"modele": true` dans la fiche.
- **Toute autre licence** (NC, tous droits réservés) : **pas de case
  cochée** — une copie par « Use this template » reprendrait tout le
  contenu, ce que la licence n'autorise pas. `"modele": false`. Si la case
  est déjà cochée, demander de la décocher avant de proposer la classe.

## 3. Demander l'accord — rien de public sans un oui

Montrer la fiche en clair (le projet, les milieux, le nom affiché, la
licence, ce qui sera visible) et demander, avec `AskUserQuestion` :
*Oui, propose ma classe* / *Pas maintenant*. Dire ce qui se passe ensuite :
« Une personne relit avant que ta classe apparaisse ; tu pourras la retirer
quand tu veux. » Un « pas maintenant » est respecté : ne pas reposer la
question dans la séance.

## 4. Proposer la classe à la galerie

Le premier chemin qui marche :

1. **Le serveur GitHub de la session** : une branche `classe/<id>` sur une
   copie (fork) du dépôt de la galerie, qui ajoute l'enregistrement à
   `classes.json`, puis une demande de fusion vers `galerie.depot`, titrée
   « Partage : <projet> (<niveau>) », dont le texte reprend la fiche et la
   sortie des contrôles. Sans droits suffisants, passer au chemin 2.
2. **Un lien prérempli** : une issue sur `galerie.depot`
   (`https://github.com/<galerie.depot>/issues/new?title=<titre encodé>&body=<fiche encodée>`,
   `urllib.parse.quote`) ; l'enseignant clique sur *Submit new issue*, et la
   personne qui relit ajoute la carte. Le donner en une phrase : « Un clic
   pour proposer ta classe : … ».

Puis le dire simplement : « J'ai proposé ta classe à la galerie. Elle
apparaîtra quand elle aura été relue. »

## 5. Retirer sa classe

L'enseignant dit « retire ma classe de la galerie » : même chemin, une
demande de fusion (ou une issue) qui **retire** son enregistrement de
`classes.json`, avec la mention « à la demande de l'auteur ». Supprimer
`partage/fiche.json`. Décocher « Template repository » n'est pas
obligatoire (ceux qui sont déjà partis de la classe gardent leur copie),
mais le proposer. Rappeler que son site et son dépôt restent à lui : les
rendre privés ou les supprimer se fait dans ses réglages GitHub, et la carte
de la galerie, qui n'est qu'un lien, cesse alors de mener quelque part.

## Garde-fous

- Jamais de partage sans la demande puis le oui de l'enseignant.
- Jamais un prénom d'élève, une photo d'enfant, une production d'élève, un
  texte d'album ou de chanson recopié, une adresse électronique.
- Jamais de faits de mémoire : seulement la sortie des contrôles du jour.
- Jamais de case « Template repository » pour une classe dont la licence
  n'autorise pas la reprise (ni NC, ni tous droits réservés).
- Ne rien copier dans la galerie que la fiche : la classe reste chez son
  auteur.

## Enchaînement

L'enseignant le demande → **partager-ma-classe** (contrôles de l'étape 1,
avec imprimer-pdf pour le PDF). Une autre classe part de celle-ci par
« Use this template » puis **nouvelle-classe** (mode « enrichir »). Une idée pour
l'outil lui-même, pas pour la galerie → remonter-au-moteur.
