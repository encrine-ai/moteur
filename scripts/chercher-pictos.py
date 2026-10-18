# -*- coding: utf-8 -*-
"""Chercher, regarder puis installer un pictogramme pour les fiches élève.

Trois commandes :

  # 1 — chercher des candidats (Mulberry + ARASAAC) et fabriquer une planche
  python3 scripts/chercher-pictos.py chercher poule "hen chicken"
  #   1er argument après « chercher » : le slug (nom du fichier cible)
  #   2e : les mots-clés ANGLAIS pour Mulberry (cherchés dans le nom des
  #        3436 pictos) ; la recherche ARASAAC utilise le slug (français),
  #        sauf si ARASAAC=<mot> le remplace (accents permis)
  #   → candidats dans /tmp/pictos/<slug>/, planche /tmp/pictos/<slug>.png

  # 1 bis — Openverse, TROISIÈME RECOURS seulement : quand ni Mulberry ni
  #     ARASAAC ne rendent la notion (« la clairière », « le pelage »).
  #     OPENVERSE porte la requête, en anglais ; ce sont des photographies.
  OPENVERSE="forest clearing" python3 scripts/chercher-pictos.py chercher clairiere ""

  # 2 — installer le candidat retenu : copie dans site/fiches/img/ et
  #     inscrit la source, la licence et l'auteur dans credits.json
  python3 scripts/chercher-pictos.py installer poule mulberry:hen
  python3 scripts/chercher-pictos.py installer poule arasaac:2403
  python3 scripts/chercher-pictos.py installer clairiere openverse:2056bb48-…

  # 3 — vérifier la banque : crédits complets, fichiers orphelins,
  #     images référencées manquantes
  python3 scripts/chercher-pictos.py verifier

Ne JAMAIS installer un candidat sans avoir regardé la planche : les noms
mentent (« chicken » Mulberry est un poulet rôti, « dove » une colombe,
« plane » un rabot). Le skill fiches-illustrations raconte les pièges.
"""
import json, os, re, ssl, subprocess, sys, urllib.parse, urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ICI, "..", "site", "fiches", "img")
CACHE = os.environ.get("PICTOS_DIR", "/tmp/pictos")
MULB_VERSION = "3.5.2"
CA = "/root/.ccr/ca-bundle.crt"

ctx = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
opener = urllib.request.build_opener(urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=ctx))
opener.addheaders = [("User-Agent", "Mozilla/5.0 (fiches pedagogiques GS)")]


def telecharge(url, chemin=None, timeout=40):
    with opener.open(url, timeout=timeout) as r:
        donnees = r.read()
    if chemin:
        open(chemin, "wb").write(donnees)
    return donnees


def catalogue_mulberry():
    """La liste des noms EN de Mulberry, mise en cache (GitHub est bloqué
    par le proxy de l'agent ; jsDelivr passe)."""
    c = os.path.join(CACHE, "mulberry-%s.json" % MULB_VERSION)
    if not os.path.exists(c):
        os.makedirs(CACHE, exist_ok=True)
        d = json.loads(telecharge(
            "https://data.jsdelivr.com/v1/packages/gh/mulberrysymbols/mulberry-symbols@" + MULB_VERSION))
        def parcours(noeud, prefixe=""):
            for f in noeud.get("files", []):
                if "files" in f:
                    yield from parcours(f, prefixe + f.get("name", "") + "/")
                else:
                    yield prefixe + f.get("name", "")
        noms = [n.split("/")[-1][:-4] for n in parcours(d)
                if ("EN/" in n and not n.split("EN/")[0].strip("/")) and n.endswith(".svg")]
        json.dump(noms, open(c, "w"))
    return json.load(open(c))


def url_mulberry(nom):
    return ("https://cdn.jsdelivr.net/gh/mulberrysymbols/mulberry-symbols@"
            + MULB_VERSION + "/EN/" + urllib.parse.quote(nom) + ".svg")


def chercher(slug, cles_en):
    dossier = os.path.join(CACHE, slug)
    os.makedirs(dossier, exist_ok=True)
    trouves = []

    # — Mulberry : recherche dans les noms —
    noms = catalogue_mulberry()
    motifs = [m.lower() for m in cles_en.split()]
    hits = [n for n in noms if any(m in n.lower() for m in motifs)][:10]
    for n in hits:
        f = os.path.join(dossier, "mulberry_" + n.replace(",", "_") + ".svg")
        try:
            telecharge(url_mulberry(n), f)
            trouves.append(("mulberry:" + n, f, "CC BY-SA 4.0"))
        except Exception as e:
            print("  mulberry", n, ":", e)

    # — ARASAAC : recherche en français —
    mot = os.environ.get("ARASAAC", slug)
    try:
        d = json.loads(telecharge(
            "https://api.arasaac.org/api/pictograms/fr/search/" + urllib.parse.quote(mot)))
    except Exception as e:
        print("  arasaac :", e)
        d = []
    for x in d[:6]:
        pid = x["_id"]
        kw = ", ".join(str(k.get("keyword")) for k in x.get("keywords", [])[:2])
        f = os.path.join(dossier, "arasaac_%d.png" % pid)
        try:
            telecharge("https://static.arasaac.org/pictograms/%d/%d_500.png" % (pid, pid), f)
            trouves.append(("arasaac:%d (%s)" % (pid, kw), f, "CC BY-NC-SA"))
        except Exception as e:
            print("  arasaac", pid, ":", e)

    # — Openverse : troisième recours, sur demande explicite —
    requete = os.environ.get("OPENVERSE")
    if requete:
        try:
            resultats = openverse_cherche(requete)
        except Exception as e:
            print("  openverse :", e)
            resultats = []
        for r in resultats:
            try:
                f, _ = openverse_telecharge(r, dossier, "openverse_" + r["id"][:8])
            except Exception as e:
                print("  openverse", r["id"][:8], ":", e)
                continue
            trouves.append(("openverse:%s (%s)" % (r["id"], (r.get("title") or "")[:30]),
                            f, (r.get("license") or "").upper() + " " + (r.get("license_version") or "")))
        # Le nom du fichier ne porte que les 8 premiers caractères de l'UUID —
        # sans cette table, l'identifiant complet est perdu dès que la sortie
        # du terminal a défilé, et il faut relancer toute la recherche.
        json.dump({r["id"][:8]: r["id"] for r in resultats},
                  open(os.path.join(dossier, "openverse.json"), "w"))

    if not trouves:
        print("aucun candidat — élargir les mots-clés, ou Openverse en dernier recours")
        return

    # — la planche, à regarder AVANT de choisir —
    cellules = "".join(
        '<div class="c"><img src="%s"><div>%s<br><small>%s</small></div></div>'
        % (os.path.abspath(f), ident, lic) for ident, f, lic in trouves)
    html = os.path.join(CACHE, slug + ".html")
    open(html, "w", encoding="utf-8").write(
        '<meta charset="utf-8"><style>body{font:12px sans-serif}'
        '.g{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}'
        '.c{border:1px solid #ccc;text-align:center;padding:5px}'
        '.c img{width:130px;height:130px;object-fit:contain}</style>'
        "<h3>%s — juger chaque image, ne pas se fier aux noms</h3>"
        '<div class="g">%s</div>' % (slug, cellules))
    png = os.path.join(CACHE, slug + ".png")
    chromes = [p for p in
               subprocess.run(["sh", "-c", "ls -d /opt/pw-browsers/chromium*/chrome-linux/chrome 2>/dev/null"],
                              capture_output=True, text=True).stdout.split() ]
    if chromes:
        subprocess.run([chromes[0], "--headless", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", "--screenshot=" + png,
                        "--window-size=800,%d" % (200 + 190 * (1 + len(trouves) // 5)),
                        "file://" + html], capture_output=True)
        print("planche : %s" % png)
    else:
        print("planche : %s (pas de Chromium trouvé pour le PNG)" % html)
    for ident, f, lic in trouves:
        print("  %-40s %s" % (ident, lic))


# Openverse fédère Flickr, Commons, Rawpixel… ATTENTION : son filtre
# `license_type=commercial` ne veut PAS dire « les licences du dépôt ». Il
# laisse passer **CC BY-ND**, qui autorise bien l'usage commercial mais
# interdit les œuvres dérivées — une carte du givre est entrée comme ça.
# On énumère donc les licences admises, et `installer` revérifie : le filtre
# de recherche et la règle du dépôt doivent être la même liste, pas deux.
# Deux pièges, tous deux vécus : les fichiers arrivent parfois en **WebP ou
# SVG sous une extension .jpg** — d'où `type_reel()`, qui lit les octets et
# non le nom ; et le vivier contient des images énormes, coupées à 8 Mo.
# Un troisième, propre à ce dépôt : Openverse sert aussi Wikimedia Commons,
# dont l'adresse de sortie de l'agent est bridée à ~5 fichiers par 10 min.
# Ces résultats-là sont écartés, sans quoi la planche s'arrête en 429.
OPENVERSE_API = "https://api.openverse.org/v1/images/"
# CC0, marque du domaine public, BY, BY-SA — et rien d'autre. NC est exclu
# (usage commercial interdit), ND aussi (recadrer, c'est déjà dériver).
LICENCES_OK = ("cc0", "pdm", "by", "by-sa")
HOTES_BANNIS = ("upload.wikimedia.org", "commons.wikimedia.org")
MAX_OCTETS = 8 * 1024 * 1024


def type_reel(donnees):
    """L'extension ment ; les premiers octets, non."""
    if donnees[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if donnees[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if donnees[:4] == b"RIFF" and donnees[8:12] == b"WEBP":
        return ".webp"
    if donnees[:5] in (b"<?xml", b"<svg ") or b"<svg" in donnees[:512]:
        return ".svg"
    return None


def openverse_cherche(requete, nb=6):
    url = (OPENVERSE_API + "?q=" + urllib.parse.quote(requete)
           + "&license=" + ",".join(LICENCES_OK)
           + "&page_size=%d" % min(nb * 3, 18))   # 20 max sans clé d'API
    d = json.loads(telecharge(url))
    gardes = []
    for r in d.get("results", []):
        if any(h in (r.get("url") or "") for h in HOTES_BANNIS):
            continue
        gardes.append(r)
        if len(gardes) == nb:
            break
    return gardes


def openverse_fiche(ident):
    return json.loads(telecharge(OPENVERSE_API + urllib.parse.quote(ident) + "/"))


def openverse_telecharge(r, dossier, base):
    donnees = telecharge(r["url"])
    if len(donnees) > MAX_OCTETS:
        raise ValueError("%.1f Mo — trop lourd" % (len(donnees) / 1048576))
    ext = type_reel(donnees)
    if ext is None:
        raise ValueError("format inconnu")
    chemin = os.path.join(dossier, base + ext)
    open(chemin, "wb").write(donnees)
    return chemin, ext


CRED_MULBERRY = {"source": "Mulberry Symbols", "page": "https://mulberrysymbols.org/",
                 "licence": "CC BY-SA 4.0", "auteur": "Paxtoncrafts Charitable Trust"}


def installer(slug, choix):
    credits = json.load(open(os.path.join(IMG, "credits.json"), encoding="utf-8"))
    if choix.startswith("mulberry:"):
        nom = choix.split(":", 1)[1]
        dest = slug + ".svg"
        telecharge(url_mulberry(nom), os.path.join(IMG, dest))
        credits[slug] = dict(fichier=dest, **CRED_MULBERRY)
    elif choix.startswith("arasaac:"):
        pid = int(choix.split(":", 1)[1].split()[0])
        dest = slug + ".png"
        telecharge("https://static.arasaac.org/pictograms/%d/%d_500.png" % (pid, pid),
                   os.path.join(IMG, dest))
        credits[slug] = {"fichier": dest, "source": "ARASAAC",
                         "page": "https://arasaac.org/pictograms/fr/%d" % pid,
                         "licence": "CC BY-NC-SA",
                         "auteur": "Sergio Palao — propriété du Gouvernement d’Aragon (Espagne)"}
    elif choix.startswith("openverse:"):
        ident = choix.split(":", 1)[1].split()[0]
        if len(ident) < 36:                    # préfixe court lu sur la planche
            table = os.path.join(CACHE, slug, "openverse.json")
            if not os.path.exists(table):
                sys.exit("identifiant court sans table : relancer « chercher »")
            complet = json.load(open(table)).get(ident[:8])
            if not complet:
                # la table ne garde que la DERNIÈRE recherche du slug : un
                # identifiant lu sur une planche précédente n'y est plus.
                sys.exit("« %s » absent de la table de %s — relancer « chercher »"
                         % (ident, slug))
            ident = complet
        r = openverse_fiche(ident)
        if any(h in (r.get("url") or "") for h in HOTES_BANNIS):
            sys.exit("Wikimedia Commons : source bannie (bridage 429), en choisir une autre")
        if (r.get("license") or "").lower() not in LICENCES_OK:
            sys.exit("licence %s : hors de la liste du dépôt (%s)"
                     % ((r.get("license") or "?").upper(), ", ".join(LICENCES_OK)))
        chemin, ext = openverse_telecharge(r, IMG, slug)
        dest = slug + ext
        credits[slug] = {"fichier": dest,
                         "source": "« %s » (Openverse)" % (r.get("title") or ident),
                         "page": r.get("foreign_landing_url") or r.get("url"),
                         "licence": "CC %s %s" % ((r.get("license") or "").upper(),
                                                  r.get("license_version") or ""),
                         "auteur": r.get("creator") or "auteur non indiqué"}
    else:
        sys.exit("choix attendu : mulberry:<nom>, arasaac:<id> ou openverse:<id>")
    # une seule extension par slug : purger l'ancienne version
    for ext in (".svg", ".png", ".jpg", ".jpeg", ".webp"):
        f = os.path.join(IMG, slug + ext)
        if os.path.exists(f) and slug + ext != dest:
            os.remove(f)
            print("supprimé :", slug + ext)
    json.dump(credits, open(os.path.join(IMG, "credits.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("installé : img/%s — penser à : generer-credits.py, contrôle PDF" % dest)


# ARASAAC est CC BY-NC-SA : la clause NC est acceptée pour ces fiches
# diffusées gratuitement, c'est écrit dans le skill fiches-illustrations.
# Toute autre restriction (ND en particulier) est refusée.
ADMISES = ("cc0", "pdm", "domaine public", "by 2.0", "by 3.0", "by 4.0",
           "by-sa", "by-nc-sa")


def licence_admise(texte):
    t = texte.lower().replace("cc ", "").strip()
    return any(t.startswith(a) or t == a for a in ADMISES)


AUTO = {"de-1", "de-2", "de-3", "de-4", "de-5", "de-6",
        "rond", "rond-plein", "triangle", "etoile-jaune", "seau", "pelle"}


def verifier():
    credits = json.load(open(os.path.join(IMG, "credits.json"), encoding="utf-8"))
    fichiers = {f for f in os.listdir(IMG) if f != "credits.json"}
    soucis = 0
    for slug, c in credits.items():
        if c["fichier"] not in fichiers:
            print("crédit sans fichier :", slug, "→", c["fichier"]); soucis += 1
        for champ in ("source", "licence", "auteur"):
            if not c.get(champ):
                print("crédit incomplet :", slug, "(", champ, ")"); soucis += 1
        # Les crédits complets ne suffisent pas : ils doivent aussi être
        # admissibles. Une image CC BY-ND est passée avec des crédits
        # parfaits, parce que rien ne relisait la licence après coup.
        if c.get("licence") and not licence_admise(c["licence"]):
            print("licence non admise :", slug, "—", c["licence"]); soucis += 1
    # La banque est PARTAGÉE : les fiches y puisent, mais aussi les
    # cartes-corpus (site/cartes-corpus/, chemins « ../fiches/img/… »). Ne
    # regarder que site/fiches/ ferait déclarer « jamais référencées » —
    # donc supprimables — les images qui ne servent qu'aux cartes.
    references = set()
    site = os.path.join(IMG, "..", "..")
    for racine, _, noms in os.walk(site):
        for nom in noms:
            if not nom.endswith(".html"):
                continue
            txt = open(os.path.join(racine, nom), encoding="utf-8").read()
            for m in re.findall(r'src="(?:\.\./)*(?:fiches/)?img/([^"]+)"', txt):
                if "/" in m:               # ../imagier/img/… : une autre banque
                    continue
                references.add(m)
                if m not in fichiers and racine.endswith("fiches"):
                    print("image référencée absente :", nom, "→", m); soucis += 1
    par_credit = {c["fichier"] for c in credits.values()}
    for f in sorted(fichiers - par_credit):
        if f.rsplit(".", 1)[0] not in AUTO:
            print("fichier sans crédit :", f); soucis += 1
    for f in sorted(fichiers - references):
        print("fichier jamais référencé (à supprimer ?) :", f)
    print("OK" if not soucis else "%d problème(s)" % soucis)
    sys.exit(1 if soucis else 0)


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "chercher":
        chercher(sys.argv[2], " ".join(sys.argv[3:]))
    elif len(sys.argv) == 4 and sys.argv[1] == "installer":
        installer(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 2 and sys.argv[1] == "verifier":
        verifier()
    else:
        sys.exit(__doc__)
