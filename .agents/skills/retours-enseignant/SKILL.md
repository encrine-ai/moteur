---
name: retours-enseignant
description: Le mode « retours » — l'enseignant dit, avec ses mots, ce qui ne va pas ou ce qu'il voudrait (une fiche, une image, une séance, une consigne, une idée), et la session s'en charge sans jargon et sans question technique, une question pédagogique à la fois. Elle trie chaque retour : retouche de la classe (corrigée ici, avec le skill du matériel), défaut du moteur (corrigé ici s'il est simple, et remonté), idée qui vaudrait pour toutes les classes (remontée au moteur). À utiliser quand l'enseignant vient faire ses retours ou en enchaîne plusieurs : « j'ai des retours », « ma collègue a testé les fiches », « plusieurs choses ne vont pas », « on fait le point sur la période 2 », « j'ai une idée pour le matériel », « ce serait bien que l'outil sache… », « /retours-enseignant ». Fin du mode : « c'est tout pour les retours », « on a fini ». Pour une retouche isolée et précise (« change l'image du hérisson »), le skill du matériel suffit.
---

# Retours de l'enseignant

Le mode « retours », pour une classe : quelqu'un qui
n'est pas technicien fait évoluer **sa** classe en parlant normalement, et
tout le travail se fait derrière. La personne est souvent l'enseignant
lui-même, parfois une collègue qui a essayé le matériel ; elle dicte souvent
depuis un téléphone, photos à l'appui.

## Entrer, rester, sortir

- **Entrer** quand la personne annonce des retours (« j'ai des retours »,
  « on fait le point sur la période 2 ») ou en donne plusieurs d'affilée.
- **Rester** dans le mode pour tous les retours qui suivent.
- **Sortir** sur « c'est tout pour les retours », « on a fini » : finir par
  le bilan (plus bas), puis reprendre le travail ordinaire.

## Les règles du mode

- **Aucune question technique**, aucun nom de fichier, de script, de branche
  ou de commit dans ce qu'on lui écrit. Ni « je régénère le cahier », ni
  « le contrôle de pagination ».
- **Le ton de la classe** : `ton` dans `classe.yml` (`tu` par défaut, comme
  entre collègues ; `vous` si l'enseignant l'a demandé).
- **Sans jargon** (règle du dépôt) : « la liste numérotée du programme », pas
  « le référentiel » ; « vérifier que l'année couvre tout le programme », pas
  « la couverture ».
- **Une question à la fois**, seulement si elle change le résultat et que
  la personne seule peut y répondre (pédagogie, goût, diffusion), avec l'outil de questions interactives de l'agent s'il en a un (`AskUserQuestion` dans Claude Code), sinon une question à la fois dans la conversation,
  dans ses mots. Attendre la réponse plutôt que trancher.
- **Relire ce qui vient d'une dictée** avant de s'en servir : un mot, un
  album, un nom d'espèce se répète à la personne s'il est douteux (« SDG »
  était « SVG »).
- **Montrer le résultat**, pas le raconter : la fiche refaite, la planche de
  cartes, la page imprimée — une capture envoyée dans la conversation, pas
  seulement un lien. Son verdict l'emporte et s'écrit dans le message de
  commit.

## Pour chaque retour

1. **Écouter** le retour en entier, photo comprise.
2. **Trier** soi-même, sans le demander :

   | Le retour porte sur… | C'est… | Ce qu'on fait |
   |---|---|---|
   | le contenu de **cette** classe : une fiche, une consigne, une image, une séance, une date, un album | **une retouche** | la faire ici, avec le skill du matériel (tableau des skills de `AGENTS.md`) |
   | un défaut qui toucherait **toutes** les classes : un cahier qui déborde quel que soit le thème, un contrôle qui laisse passer une erreur, un skill qui a mené de travers | **un défaut du moteur** | le corriger ici s'il est simple et générique (`classe.py verifier` vert), puis le **remonter** (skill remonter-au-moteur) |
   | un souhait qui vaudrait pour d'autres enseignants : un nouveau type de cahier, une question de plus dans l'entretien, un niveau | **une idée pour le moteur** | la **remonter** telle quelle, sans la construire ici ; proposer, si la personne la veut tout de suite, une version propre à sa classe |
   | une préférence qui ne vaut que pour cette classe (le rythme des fiches, une espèce qu'on refuse) | **une convention de la classe** | la noter là où le skill du matériel la range, jamais comme une règle du programme |

   « Ce n'est pas beau », « ça ne fait pas professionnel » : c'est aussi un
   défaut des contrôles. Corriger le résultat, et chercher le contrôle ou la
   règle de skill qui l'aurait attrapé (skill capitaliser).
3. **Faire le travail** en silence, avec le skill concerné, et finir comme
   lui : régénérer, contrôler, **finir par le PDF** (skill imprimer-pdf) dès
   que la retouche touche ce qui s'imprime.
4. **Confirmer** en une ou deux phrases, avec la capture : ce qui a changé,
   vu de la classe (« La fiche 3.4 tient maintenant sur une page, et les
   cases sont assez grandes pour écrire. »). Proposer de revenir en arrière
   si la personne n'est pas convaincue.
5. **Capitaliser** (skill capitaliser) ce que le retour a appris, avant de
   passer au suivant.

## Le bilan, en sortant du mode

Trois lignes au plus, sans technique : ce qui est fait et visible, ce qui
attend une réponse de la personne (une seule question, la plus importante),
et ce qui est parti vers le moteur (« J'ai aussi transmis ton idée de
cartes-chiffres, pour que les autres classes en profitent. »). Ne pas dire
« c'est en ligne » avant de l'avoir vu en ligne (skill site-et-calendrier).

## Quand ça coince

Pas d'erreur technique montrée. Dire simplement ce qui n'a pas pu se faire
et ce qu'on propose à la place ; garder le diagnostic technique pour le
message de commit ou pour la remontée au moteur.

## Garde-fous

- **Aucune donnée d'élève**, jamais : ni prénom, ni photo d'enfant, ni
  production d'élève recopiée. Une photo de fiche remplie sert à comprendre
  le retour, elle n'entre pas dans le dépôt.
- Une modification faite à la main par l'enseignant n'est jamais écrasée
  par une régénération : relire avant de régénérer.
- Le moteur ne se modifie pas pour du contenu : un retour sur la classe se
  règle dans la classe.

## Enchaînement

Retouche → le skill du matériel → imprimer-pdf → capitaliser.
Défaut ou idée pour toutes les classes → **remonter-au-moteur**.
