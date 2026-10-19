---
name: remonter-au-moteur
description: Envoyer au dépôt du moteur ce qu'une classe a appris et qui servirait à toutes les autres — un défaut rencontré (un skill qui a mené de travers, un contrôle qui a laissé passer une erreur, un script qui a échoué, un gabarit qui déborde), une amélioration déjà faite ici dans le code du moteur, ou une idée de l'enseignant pour toutes les classes — sous la forme d'une issue rédigée pour être qualifiée puis intégrée, dédoublonnée, sans aucune donnée d'élève. Le dépôt du moteur se lit dans classe.yml (`moteur.depot`). À utiliser à la demande de l'enseignant (« transmets ça à l'outil », « ce serait bien pour tout le monde », « signale ce problème »), à la fin du skill retours-enseignant quand un retour vaut pour toutes les classes, après capitaliser quand la leçon touche le moteur, et avant synchroniser-moteur si la classe a modifié le code du moteur. Ne concerne pas une retouche de la classe elle-même.
---

# Remonter au moteur

Une classe vit dans **son propre dépôt**, créé depuis le dépôt modèle : ce
qu'elle corrige ou ajoute au moteur y reste, si personne ne le signale. Ce
skill l'envoie à la **boîte du moteur** — les issues du dépôt modèle — où il
sera qualifié, intégré au moteur (skill trier-remontees, qui ne vit que
dans le dépôt du moteur), puis propagé à toutes les classes (skill
synchroniser-moteur). C'est la mécanique de Ludea (`report-upstream`,
`ludea-feedback`) : on remonte des apprentissages, jamais la classe
elle-même — la montrer aux autres est le rôle de partager-ma-classe.

## 0. Faut-il remonter ici ?

Lire `moteur` dans `classe.yml` :

- **`depot` n'est pas renseigné** (`à définir`) : ce dépôt **est** celui où
  le moteur se développe (c'est le cas de la Grande Section tant que le
  dépôt modèle n'existe pas). Ne rien remonter : corriger directement ici,
  de façon générique (skill capitaliser, `classe.py verifier` vert), et le
  noter dans `docs/vers-un-moteur.md`.
- **`depot` est renseigné** : c'est l'adresse `propriétaire/dépôt` du
  moteur. Continuer.
- L'enseignant a dit qu'il ne voulait pas de remontées : respecter son
  choix, et l'écrire dans `classe.yml` (`moteur.remontees: non`).

## 1. Ce qui se remonte

| Genre | Ce que c'est | Titre |
|---|---|---|
| **défaut** | quelque chose du moteur a mal marché : un skill qui a mené de travers, un contrôle qui a laissé passer une erreur ou qui en a vu une à tort, un script en échec, un gabarit qui déborde, une documentation fausse. Corrigé ici ou contourné, peu importe : avec de quoi le reproduire | `[défaut] …` |
| **amélioration** | un changement **déjà fait ici** dans un fichier du moteur (liste des chemins dans le skill synchroniser-moteur) : la liste des fichiers, les commits, et le correctif | `[amélioration] …` |
| **idée** | une capacité que la classe aurait voulue et que le moteur n'a pas : un type de cahier, un niveau, une question de l'entretien | `[idée] …` |

Ne se remontent pas : le contenu de la classe (une fiche, une espèce, une
séance), le goût de l'enseignant, ce qui ne vaut que pour cette classe. La
question à se poser : **une autre classe le rencontrerait-elle, ou le
voudrait-elle ?** Si non, ne rien envoyer.

Les bonnes sources : les échecs de la session elle-même (une étape de skill
fausse ou absente, un contrôle trompeur, une erreur de script, un outil
absent de l'environnement), chaque retouche d'un fichier du moteur, chaque
leçon que capitaliser a versée dans un skill.

## 2. Généraliser

Réécrire chaque élément pour qu'il serve à **toutes** les classes, la classe
d'origine servant d'exemple : « un cahier de cartes-chiffres de 1 à 10 pour
les fiches de dénombrement », et non « dans ma GS, la fiche 1.7… ». Une
idée dictée se relit à l'enseignant avant d'être envoyée, en une phrase, si
elle est ambiguë ; jamais de question technique.

## 3. Dédoublonner

Chercher dans les issues **ouvertes et fermées** du dépôt du moteur
(serveur GitHub : `search_issues`, quelques mots-clés). Déjà signalé : y
ajouter un **commentaire** avec ce que cette classe apporte de neuf (« vu
aussi dans une MS, zone B : … »), plutôt qu'une nouvelle issue. Ne pas
renvoyer ce que cette classe a déjà remonté : ses issues se retrouvent par
la marque `classe=<propriétaire/dépôt>` de leur première ligne (la chercher
telle quelle). **Pas de journal dans la classe** : les issues sont la seule
trace (décidé le 18 octobre 2026 — le dépôt d'une classe est public, et un
journal ferait doublon).

## 4. Écrire l'issue — elle est publique

Titre : `[genre] description courte et générale` (sans le nom de la classe).
Corps, en français :

```
<!-- remontee v1 genre=<défaut|amélioration|idée> classe=<propriétaire/dépôt> moteur=<moteur.version> -->
### Quoi
<un paragraphe général : ce qui ne va pas, ou ce que le changement fait>
### Où
<skill <nom> | script <nom> | gabarit <cahier> | site | documentation | entretien nouvelle-classe>
### Comment le constater
<les étapes, la sortie du contrôle, le message d'erreur — de courtes citations>
### Ce qui est proposé
<pour une amélioration : les fichiers, les commits de la classe
 (https://github.com/<propriétaire/dépôt>/commit/<sha>) et le correctif dans un bloc <details>
 (git diff des seuls fichiers du moteur) ; au-delà de 40 Ko, les liens des commits seulement>
### La classe d'où ça vient
<niveau · thème · version du moteur · lien du site>
```

**Jamais** : un prénom d'élève ou d'adulte, une adresse, une photo d'enfant
ou de production d'élève, un jeton, les messages de l'enseignant recopiés,
une conversation entière. Décrire, ne pas coller. Pas de promesse de date ni
d'acceptation : c'est le moteur qui décide.

## 5. Demander l'accord — rien de public sans un oui

Décidé le 18 octobre 2026 : une remontée est **proposée, puis envoyée si
l'enseignant est d'accord**, jamais en silence. Lui dire en deux phrases,
sans technique, ce qui partirait et pourquoi (« Le débordement de la fiche
2.4 arriverait sans doute à d'autres classes. Je le signale à l'outil, pour
qu'il soit corrigé pour tout le monde ? »), avec l'outil de questions interactives de l'agent s'il en a un (`AskUserQuestion` dans Claude Code), sinon une question à la fois dans la conversation :
*Oui, transmets* / *Non, garde-le pour ma classe*. Plusieurs remontées d'un
même retour : une seule question, chacune cochable. Un non est définitif
pour cette remontée : ne pas la reposer.

## 6. Envoyer — le premier chemin qui marche

1. Le **serveur GitHub** de la session : `issue_write` (création) sur
   `moteur.depot`. Un dépôt public accepte les issues de n'importe quel
   compte GitHub.
2. À défaut, **un lien prérempli**, qui marche toujours — l'enseignant n'a
   qu'à cliquer sur *Submit new issue* :
   `https://github.com/<moteur.depot>/issues/new?title=<titre encodé>&body=<corps encodé>`
   (encoder avec `urllib.parse.quote`). Au-delà de 6 000 caractères, couper
   le correctif du corps et le committer d'abord sous `remontees/`, pour que
   l'issue puisse pointer vers lui. Donner le lien avec **une** phrase
   simple : « Un clic pour transmettre cette amélioration : … ».


## 7. Le dire à l'enseignant — une phrase, sans technique

« J'ai aussi transmis ton idée de cartes-chiffres, pour que les autres
classes en profitent : si elle est retenue, ta classe la recevra à la
prochaine mise à jour. » La retouche locale reste en place ; la mise à jour
du moteur la ramènera, identique ou meilleure, une fois intégrée.

## Garde-fous

- Ne jamais pousser sur le dépôt du moteur depuis une classe : on signale,
  on ne corrige pas chez lui.
- Ne jamais bloquer le travail de la classe pour une remontée : un envoi qui
  échoue, c'est le lien prérempli, et on continue.
- Les textes des issues sont publics : formulation générale, aucune donnée
  personnelle.
- Rien ne part sans le oui de l'enseignant (étape 5), même une remontée
  évidente.

## Enchaînement

retours-enseignant ou capitaliser → **remonter-au-moteur**.
synchroniser-moteur refuse d'écraser une amélioration non remontée : passer
par ici d'abord.
