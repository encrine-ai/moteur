---
name: partager-ma-classe
description: Partager sa classe dans la galerie de la plateforme (« Les classes »), si l'enseignant le veut — vérifier d'abord que tout est juste et partageable (programme couvert, une page par fiche, licences des images, aucun prénom d'élève ni photo de classe, aucun album ni chanson recopié : scripts/verifier-partage.py), préparer la fiche de la classe (projet, niveau, milieux, auteur, licence, faits vérifiés), demander son accord, puis proposer la classe à la galerie par une demande de fusion que le propriétaire de la plateforme relit. La classe reste dans le dépôt de l'enseignant : la galerie n'en montre qu'un lien. Explique aussi comment la retirer. À utiliser seulement à la demande : « je voudrais partager ma classe », « on peut la mettre dans la galerie ? », « je suis fière de ma classe, d'autres pourraient s'en servir », « montre ma classe aux autres enseignants », « retire ma classe de la galerie », « /partager-ma-classe ». Ne concerne pas les retours sur l'outil (retours-enseignant, remonter-au-moteur).
---

# Partager ma classe

La galerie de la plateforme montre ce que les enseignants ont fait, pour
donner des idées : chaque classe partagée y a une carte, aux couleurs de son
thème, avec deux gestes — **voir la classe** (son site, chez son auteur) et
**partir de cette classe** (skill nouvelle-classe). Décidé le 18 octobre
2026 :

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
  "zone": "<la zone que l'enseignant indique, ou null>",
  "milieux": [{"nom": "<periodes[].milieu>", "couleur": "<--p1 … --p5 du thème, en hex>"}],
  "auteur": "<nom ou pseudonyme, au choix de l'enseignant>",
  "licence": "CC BY-SA 4.0",
  "restrictions": ["pictogrammes ARASAAC : pas d'usage commercial"],
  "site": "https://<propriétaire>.github.io/<dépôt>/",
  "depot": "https://github.com/<propriétaire>/<dépôt>",
  "faits": {"attendus": "159/159", "pdf": 155, "pagination": "vérifiée", "moteur": "<moteur.version>"},
  "partage_le": "AAAA-MM-JJ"
}
```

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
  | CC BY-NC-SA 4.0 | réutiliser et modifier, en te citant, mais jamais pour un usage commercial |
  | Tous droits réservés | regarder seulement : « partir de cette classe » reprendra ton thème et tes milieux, pas tes textes |

Écrire la fiche dans `partage/fiche.json` de la classe.

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
`partage/fiche.json`. Rappeler que son site et son dépôt restent à lui : les
rendre privés ou les supprimer se fait dans ses réglages GitHub, et la carte
de la galerie, qui n'est qu'un lien, cesse alors de mener quelque part.

## Garde-fous

- Jamais de partage sans la demande puis le oui de l'enseignant.
- Jamais un prénom d'élève, une photo d'enfant, une production d'élève, un
  texte d'album ou de chanson recopié, une adresse électronique.
- Jamais de faits de mémoire : seulement la sortie des contrôles du jour.
- Ne rien copier dans la galerie que la fiche : la classe reste chez son
  auteur.

## Enchaînement

L'enseignant le demande → **partager-ma-classe** (contrôles de l'étape 1,
avec imprimer-pdf pour le PDF). Une autre classe part de celle-ci par
**nouvelle-classe** (« partir d'une classe de la galerie »). Une idée pour
l'outil lui-même, pas pour la galerie → remonter-au-moteur.
