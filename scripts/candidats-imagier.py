# -*- coding: utf-8 -*-
"""Planches de candidats, pour choisir soi-même la photographie de chaque espèce.

Le tri automatique d'iNaturalist met en avant les photographies les plus
« aimées », qui sont souvent spectaculaires plutôt qu'illustratives (un ours
en train de manger des pissenlits, un bourgeon en gros plan…). Pour un
imagier, il faut au contraire une image où l'espèce est le sujet, entière et
reconnaissable. Ce script rassemble plusieurs candidates par espèce et les
assemble en une planche numérotée, à regarder avant de renseigner OVERRIDES
dans classe/imagier.py.

Usage : python3 scripts/candidats-imagier.py [1-faune | pigeon-biset …]
        PLACE=97391   restreint à l'Europe (écarte les espèces voisines
                      d'un autre continent) ;
        MOIS=5,6,7    restreint aux mois de floraison, pour une plante ;
        PAGES=4       explore plus loin quand le vivier est pauvre ;
        CAPTIVE=1     pour une plante cultivée (betterave, vigne, noyer…) ;
        NB_CANDIDATS  vignettes par espèce (défaut 8).
        (sans argument : les dix planches ; sinon des planches entières
        « N-faune » / « N-flore » et/ou des espèces isolées, par leur slug)
Sortie : <DOSSIER>/candidats-p<N>-<groupe>.jpg  et  le JSON des identifiants
         (DOSSIER : variable d'environnement CANDIDATS_DIR, /tmp par défaut)
"""
import io, json, os, ssl, sys, time, urllib.error, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
# Le manifeste est du contenu de la classe : son chemin vient de classe.yml.
sys.path.insert(0, ICI)
import classe  # noqa: E402
ns = classe.manifeste("imagier")
ENTREES = list(ns["entrees"]())
DOMESTIQUES = ns["DOMESTIQUES"]
# mêmes renommages acceptés que scripts/verifier-imagier.py
SYNONYMES = {"Ammophila arenaria": "Calamagrostis arenaria",
             "Anemone nemorosa": "Anemonoides nemorosa",
             "Ichthyosaura alpestris": "Mesotriton alpestris",
             "Halimione portulacoides": "Atriplex portulacoides"}

DOSSIER = os.environ.get("CANDIDATS_DIR", "/tmp")
NB = int(os.environ.get("NB_CANDIDATS", "8"))
# Quand le vivier d'une espèce est pauvre — des troupeaux et des zébus pour
# « la vache », des rosettes de feuilles hivernales pour « la digitale » —,
# il faut l'élargir plutôt que se rabattre sur une mauvaise vignette. Ces
# trois réglages évitent d'écrire un moissonneur jetable à côté.
PLACE = os.environ.get("PLACE")      # place_id : 97391 = l'Europe
MOIS = os.environ.get("MOIS")        # « 5,6,7 » : les mois de floraison
PAGES = int(os.environ.get("PAGES", "1"))
# Un champ cultivé est « captive » au sens d'iNaturalist, comme un animal de
# ferme : sans ce filtre, Beta vulgaris ne rend que la betterave maritime
# sauvage, la vigne aucune grappe et le noyer aucune noix.
CAPTIVE = os.environ.get("CAPTIVE") == "1"
os.makedirs(DOSSIER, exist_ok=True)
CELL, LEG = 330, 34
MIN_COTE = 1000
LICENCES = "cc0,cc-by,cc-by-sa"

cafile = "/root/.ccr/ca-bundle.crt"
ctx = ssl.create_default_context(cafile=cafile) if os.path.exists(cafile) else ssl.create_default_context()
opener = urllib.request.build_opener(urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=ctx))
opener.addheaders = [("User-Agent", "imagier-scolaire/1.0 (cartes de nomenclature pour l'école maternelle)")]
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)


def ouvre(url, timeout=45):
    for attente in (0, 3, 8, 20):
        if attente:
            time.sleep(attente)
        try:
            return opener.open(url, timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500:
                raise
    raise RuntimeError("serveur indisponible")


_taxons = {}


def taxon_id(nom):
    """Identifiant iNaturalist du nom scientifique.

    Indispensable : le paramètre taxon_name accroche aussi les noms
    vernaculaires et rend des espèces d'un autre continent — « Meles meles »
    ramenait le blaireau d'Amérique, « Capreolus capreolus » un rhebok
    d'Afrique du Sud. On accepte donc le nom scientifique exact, ou à défaut
    le terme sur lequel iNaturalist a accroché, ce qui rattrape les
    renommages (Ammophila arenaria est devenu Calamagrostis arenaria)."""
    if nom in _taxons:
        return _taxons[nom]
    # sans le filtre de rang, la recherche floue peut ne rendre que du bruit :
    # « Glis glis » (le loir) remontait des fougères et des graminées
    with ouvre("https://api.inaturalist.org/v1/taxa?"
               + urllib.parse.urlencode({"q": nom, "per_page": "20", "is_active": "true",
                                         "rank": "species,subspecies,variety,hybrid"})) as r:
        res = json.load(r).get("results", [])
    trouve = next((t for t in res if t.get("name", "").lower() == nom.lower()), None) \
        or next((t for t in res if (t.get("matched_term") or "").lower() == nom.lower()), None)
    if trouve is None:
        raise RuntimeError("taxon « %s » introuvable sur iNaturalist" % nom)
    _taxons[nom] = trouve["id"]
    return trouve["id"]


def candidates(taxon, recherche_seule=True):
    """Plusieurs photographies libres et imprimables, les plus appréciées
    d'abord. Le classement d'iNaturalist met en avant de belles images, pas
    forcément illustratives : c'est bien pourquoi on les regarde avant de
    choisir."""
    params = {"taxon_id": taxon_id(taxon), "photo_license": LICENCES, "photos": "true",
              "order_by": "votes", "per_page": "60"}
    if taxon in DOMESTIQUES or CAPTIVE:
        params["captive"] = "true"        # la ferme et les cultures, pas le féral
    elif recherche_seule:
        params["quality_grade"] = "research"
    if PLACE:
        params["place_id"] = PLACE
    if MOIS:
        params["month"] = MOIS
    out, vus = [], set()
    for page in range(1, PAGES + 1):
        params["page"] = str(page)
        with ouvre("https://api.inaturalist.org/v1/observations?" + urllib.parse.urlencode(params)) as r:
            d = json.load(r)
        for obs in d.get("results", []):
            photo = (obs.get("photos") or [None])[0]   # la première photo est la mieux cadrée
            if not photo:
                continue
            dim = photo.get("original_dimensions") or {}
            l, h = dim.get("width", 0), dim.get("height", 0)
            if min(l, h) < MIN_COTE:
                continue
            # un seul cliché par observateur : quarante candidates sont parfois
            # quarante photos du même pied, prises le même jour
            qui = ((obs.get("user") or {}).get("login")) or obs["id"]
            if qui in vus:
                continue
            vus.add(qui)
            out.append({"id": photo["id"], "vignette": photo["url"].replace("square", "medium"),
                        "accords": obs.get("num_identification_agreements", 0),
                        "espece": (obs.get("taxon") or {}).get("name", "?"),
                        "paysage": l >= h})
        if not d.get("results") or page * 60 >= d.get("total_results", 0):
            break
    if not out and recherche_seule and taxon not in DOMESTIQUES:
        return candidates(taxon, recherche_seule=False)
    # on garde l'ordre d'iNaturalist ; à qualité égale, une photo en
    # largeur remplit mieux la carte
    out.sort(key=lambda p: not p["paysage"])
    return out[:NB]


def planche(nom_fichier, especes):
    """especes : liste de (nom, taxon, [candidates])."""
    img = Image.new("RGB", (NB * CELL, len(especes) * (CELL + LEG)), "white")
    d = ImageDraw.Draw(img)
    for r, (nom, taxon, cands) in enumerate(especes):
        cy = r * (CELL + LEG)
        d.text((6, cy + CELL + 8), "%s  (%s)" % (nom, taxon), fill="black", font=F)
        for c, cand in enumerate(cands):
            cx = c * CELL
            try:
                with ouvre(cand["vignette"]) as rep:
                    v = Image.open(io.BytesIO(rep.read())).convert("RGB")
                v.thumbnail((CELL - 6, CELL - 6), Image.LANCZOS)
                img.paste(v, (cx + (CELL - v.width) // 2, cy + (CELL - v.height) // 2))
            except Exception as e:
                d.text((cx + 8, cy + 8), "échec", fill="red", font=F)
            d.rectangle([cx, cy, cx + CELL - 1, cy + CELL - 1], outline="#bbb")
            d.text((cx + 8, cy + 6), "%d" % (c + 1), fill="#c00", font=F)
            # le vivier contient des espèces voisines : on les signale plutôt
            # que de laisser choisir un chêne du Cantabrique pour « le chêne ».
            # Un renommage accepté n'est pas une espèce voisine : sans cette
            # exception, toutes les anémones des bois seraient barrées de rouge.
            espece = cand.get("espece") or "?"
            # une sous-espèce de l'espèce demandée en est bien une : le loup
            # d'Italie est un loup. Seules les espèces voisines sont barrées.
            attendus = (taxon, SYNONYMES.get(taxon), "?")
            if espece not in attendus and not any(
                    a and espece.startswith(a + " ") for a in attendus):
                d.rectangle([cx, cy, cx + CELL - 1, cy + CELL - 1], outline="#c00", width=4)
                d.text((cx + 8, cy + CELL - 26), espece[:26], fill="#c00", font=F)
    chemin = os.path.join(DOSSIER, nom_fichier)
    img.save(chemin, "JPEG", quality=86)
    return chemin


cibles = set(a.lower() for a in sys.argv[1:])
groupes = {}
for p, groupe, slug, nom, taxon in ENTREES:
    code = "%d-%s" % (p, groupe)
    if cibles and code not in cibles and slug not in cibles:
        continue
    groupes.setdefault((p, groupe), []).append((slug, nom, taxon))

index = {}
for (p, groupe), especes in sorted(groupes.items()):
    lignes, ids = [], {}
    for slug, nom, taxon in especes:
        cands = candidates(taxon)
        ids[slug] = [{"id": c["id"], "espece": c.get("espece")} for c in cands]
        lignes.append((nom, taxon, cands))
        time.sleep(0.4)
    # une planche par lot de six espèces : au-delà, l'image devient illisible
    for n in range(0, len(lignes), 6):
        suffixe = "" if len(lignes) <= 6 else "-%d" % (n // 6 + 1)
        chemin = planche("candidats-p%d-%s%s.jpg" % (p, groupe, suffixe), lignes[n:n + 6])
        print("p%d %s → %s" % (p, groupe, chemin))
    index.update(ids)

json.dump(index, open(os.path.join(DOSSIER, "candidats-index.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("identifiants : %s/candidats-index.json" % DOSSIER)
