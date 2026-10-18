# -*- coding: utf-8 -*-
"""Mesure si un skill du dépôt se déclenche sur les bonnes demandes.

Un skill que Claude n'ouvre pas au bon moment ne sert à rien, et un skill
qui s'ouvre pour tout encombre les autres tâches. Ce script rejoue une liste
de demandes réalistes et regarde, pour chacune, si le skill est consulté.

**Ne pas utiliser le banc d'essai du skill-creator pour cela.** Il pose un
faux fichier de *commande* dans `.claude/commands/` en espérant que Claude
l'expose comme un skill ; cette version de Claude Code ne le fait pas, si
bien qu'aucune demande ne déclenche jamais rien. Le score qu'il annonce
n'est alors fait que des cas négatifs, qui passent par défaut : il avait
rendu 10/20 là où la mesure directe donne 20/20.

Chaque exécution tourne dans un clone jetable du dépôt, parce que Claude y
travaille pour de bon. Un déclenchement = un appel à l'outil Skill nommant
le skill ; on s'arrête dès qu'on le voit, ou après huit appels d'outil —
au-delà, le skill n'a manifestement pas guidé le travail. Ce seuil n'est
qu'un garde-fou de coût : trop bas, il compte comme non-déclenchements des
exécutions où Claude explore le dépôt avant d'ouvrir le skill.

Usage : python3 scripts/mesurer-declenchement.py <cas.json>
        SKILL=<nom>              le skill à mesurer (défaut : imagier-photos)
        RUNS=<n>                 essais par demande (défaut : 2)
        DECLENCHEMENT_DIR=<dir>  clones et résultat (défaut : /tmp/declenchement)

Le fichier de cas est une liste d'objets {"query": "...",
"should_trigger": true|false}. Les cas négatifs les plus utiles sont les
voisins : une demande qui parle d'imagier mais relève du CSS des cartes ou
de la génération des PDF ne doit pas ouvrir le skill des photographies.
"""
import json, os, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor

ICI = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.abspath(os.path.join(ICI, ".."))
TRAVAIL = os.environ.get("DECLENCHEMENT_DIR", "/tmp/declenchement")
SKILL = os.environ.get("SKILL", "imagier-photos")
RUNS = int(os.environ.get("RUNS", "2"))
# Claude explore souvent le dépôt avant d'ouvrir un skill : couper trop tôt
# compte ces exécutions comme des non-déclenchements et sous-estime la
# description. Huit appels laissent la place à cette exploration.
LIMITE_OUTILS = int(os.environ.get("LIMITE_OUTILS", "8"))
MODELE = "claude-opus-5"
verrou = threading.Lock()


def clone(i):
    d = os.path.join(TRAVAIL, "clones", "c%d" % i)
    if not os.path.exists(d):
        os.makedirs(os.path.dirname(d), exist_ok=True)
        subprocess.run(["git", "clone", "-q", DEPOT, d], check=True)
    return d


def une_execution(requete, cwd):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    p = subprocess.Popen(
        ["claude", "-p", requete, "--output-format", "stream-json", "--verbose", "--model", MODELE],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=cwd, env=env, text=True)
    outils = 0
    try:
        for ligne in p.stdout:
            ligne = ligne.strip()
            if not ligne.startswith("{"):
                continue
            try:
                d = json.loads(ligne)
            except Exception:
                continue
            message = d.get("message")
            if not isinstance(message, dict):   # le flux rend parfois du texte brut
                continue
            contenu = message.get("content") or []
            if isinstance(contenu, str):
                continue
            for c in contenu:
                if not isinstance(c, dict) or c.get("type") != "tool_use":
                    continue
                if c["name"] == "Skill" and SKILL in json.dumps(c.get("input", {})):
                    return True
                outils += 1
                if outils >= LIMITE_OUTILS:
                    return False
        return False
    finally:
        p.kill()


def mesure(args):
    idx, cas = args
    cwd = clone(idx % 5)
    n = 0
    for _ in range(RUNS):
        try:
            if une_execution(cas["query"], cwd):
                n += 1
        except Exception as e:
            with verrou:
                print("  erreur :", e, file=sys.stderr)
    taux = n / float(RUNS)
    ok = (taux >= 0.5) == cas["should_trigger"]
    with verrou:
        print("  [%s] %d/%d attendu=%s : %s" % ("OK " if ok else "RATÉ", n, RUNS,
              "oui" if cas["should_trigger"] else "non", cas["query"][:64]), flush=True)
    return {"query": cas["query"], "should_trigger": cas["should_trigger"],
            "taux": taux, "ok": ok}


cas = json.load(open(sys.argv[1], encoding="utf-8"))
for i in range(5):
    clone(i)
with ThreadPoolExecutor(max_workers=5) as ex:
    resultats = list(ex.map(mesure, enumerate(cas)))
pos = [r for r in resultats if r["should_trigger"]]
neg = [r for r in resultats if not r["should_trigger"]]
print("\nDéclenche quand il faut     : %d/%d" % (sum(r["ok"] for r in pos), len(pos)))
print("Se tait quand il faut       : %d/%d" % (sum(r["ok"] for r in neg), len(neg)))
print("Total                       : %d/%d" % (sum(r["ok"] for r in resultats), len(resultats)))
json.dump(resultats, open(os.path.join(TRAVAIL, "mesure.json"), "w"),
          ensure_ascii=False, indent=1)
