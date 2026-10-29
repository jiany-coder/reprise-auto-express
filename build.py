#!/usr/bin/env python3
# Générateur du site statique Reprise Auto Express (Morbihan)
import os, re, json, html, hashlib, unicodedata, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enrich import ENRICH

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "dist")

# ------------------------------------------------------------------ CONFIG
SITE_URL = os.environ.get("SITE_URL", "https://repriseautoexpress.online").rstrip("/")
PREPROD = os.environ.get("PREPROD", "0") == "1"   # 1 = noindex tant que le domaine final n'est pas branché
BRAND = "Reprise Auto Express"
PHONE = os.environ.get("PHONE", "")       # ex: "02 97 00 00 00"
EMAIL = os.environ.get("EMAIL", "dawsondelorme77@gmail.com")       # ex: "contact@..."
ADDRESS = os.environ.get("ADDRESS", "")   # ex: "12 rue ..., 56000 Vannes"
TODAY = "2026-10-29"

# ------------------------------------------------------------------ DONNÉES
def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower().replace("'", "").replace("œ", "oe")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

communes = []
for line in open(os.path.join(ROOT, "data", "communes.txt"), encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    n, cp = line.split("|")
    communes.append({"name": n, "cp": cp, "slug": slugify(n)})
communes.sort(key=lambda c: slugify(c["name"]))
BY_SLUG = {c["slug"]: c for c in communes}
BY_CP = {}
for c in communes:
    BY_CP.setdefault(c["cp"], []).append(c)
CPS = sorted(BY_CP)

def prep(name):
    """à / au / aux / sur l' selon le nom de la commune"""
    if name.startswith("Le "): return "au " + name[3:]
    if name.startswith("Les "): return "aux " + name[4:]
    if name.startswith("Île") or name.startswith("Hœdic"): return "sur l'" + name if name.startswith("Île") else "à " + name
    return "à " + name

def de(name):
    if name.startswith("Le "): return "du " + name[3:]
    if name.startswith("Les "): return "des " + name[4:]
    if name[0] in "AEIOUÉÈÎÂÊHhœ" and not name.startswith("Hennebont"): return "d'" + name
    return "de " + name

def hv(s, n):
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % n

E = html.escape

# ------------------------------------------------------------------ PAGES VÉHICULES
VEHICLES = [
 dict(slug="rachat-voiture-morbihan", nav="Voiture", name="voiture", h1="Rachat de voiture dans le Morbihan",
  title="Rachat voiture Morbihan | Reprise cash Vannes – Reprise Auto Express",
  desc="Rachat de voiture dans tout le Morbihan : citadine, berline, SUV, 4x4, diesel, essence, hybride. Sans CT, même HS. Offre ferme après expertise.",
  lead="Reprise Auto Express rachète votre voiture à Vannes et dans tout le Morbihan, sans obligation d'achat, dans l'état où elle se trouve : avec ou sans contrôle technique, roulante, en panne ou accidentée.",
  sections=[
   ("Quelles voitures rachetons-nous ?", "Toutes les voitures particulières : citadines, compactes, berlines, breaks, monospaces, SUV, 4x4, coupés et cabriolets, en essence, diesel, hybride, électrique ou GPL. Les marques courantes (Renault, Peugeot, Citroën, Dacia, Volkswagen, Toyota, Ford, Opel, BMW, Audi, Mercedes) comme les modèles plus rares sont étudiés au cas par cas. Le kilométrage, l'année et l'historique d'entretien orientent le prix, pas la marque."),
   ("Voiture avec beaucoup de kilomètres, ancienne ou abîmée", "Un fort kilométrage, une carrosserie marquée ou un entretien en retard ne ferment pas la porte au rachat. Nous partons de la valeur de marché de votre modèle, puis nous déduisons le coût réel des remises en état. Vous n'avez rien à réparer avant la vente."),
   ("Un prix clair, expliqué", "L'estimation se fait à partir de la cote du modèle, des options, de l'état constaté et des véhicules comparables proposés dans la région. Après l'expertise, vous recevez une offre ferme : le montant annoncé est celui qui est payé si vous acceptez."),
   ("Démarches prises en charge", "Nous préparons le certificat de cession et la déclaration de cession : une fois la vente conclue, vous n'êtes plus responsable du véhicule. Il reste à prévenir votre assureur pour résilier ou transférer le contrat."),
  ],
  faq=[
   ("Quelle voiture pouvez-vous racheter dans le Morbihan ?", "Toutes les voitures particulières, quelle que soit la motorisation : essence, diesel, hybride, électrique ou GPL. Un véhicule ancien, très kilométré ou à réparer peut aussi être repris, au prix de son état réel."),
   ("Faut-il passer le contrôle technique avant de vendre ?", "Non. Le contrôle technique de moins de 6 mois est exigé pour vendre à un particulier. Pour une vente à un professionnel de l'automobile, il n'est pas demandé : votre voiture est reprise dans l'état."),
   ("Puis-je vendre une voiture encore en crédit ?", "Dans certains cas oui : le solde doit être régularisé auprès de l'organisme de financement. Indiquez-le dès la demande d'estimation pour que le dossier soit traité correctement."),
   ("Combien de temps dure un rachat ?", "Un conseiller se déplace chez vous dans les 24 h suivant votre demande ; l'expertise, l'offre ferme et la signature des documents peuvent se faire sur place. Le règlement a lieu par virement ou en espèces (dans la limite légale)."),
  ]),
 dict(slug="rachat-voiture-sans-permis-morbihan", nav="Sans permis", name="voiture sans permis", h1="Rachat de voiture sans permis dans le Morbihan",
  title="Rachat voiture sans permis Morbihan | Aixam, Ligier, Microcar",
  desc="Vendez votre voiture sans permis (voiturette) dans le Morbihan : Aixam, Ligier, Microcar, Chatenet, JDM. Reprise sans CT, estimation gratuite.",
  lead="Votre voiture sans permis (voiturette ou quadricycle léger) ne sert plus ? Reprise Auto Express la rachète à Vannes et partout dans le Morbihan, diesel ou électrique, en état de marche ou non.",
  sections=[
   ("Quelles voitures sans permis rachetons-nous ?", "Les voiturettes des marques courantes du segment : Aixam, Ligier, Microcar, Chatenet, JDM, ainsi que les modèles électriques récents. Une voiturette diesel d'occasion garde une demande réelle, notamment en zone rurale et pour les jeunes conducteurs titulaires du permis AM (BSR)."),
   ("Pas de contrôle technique à prévoir", "Les voitures sans permis (quadricycles légers, limitées à 45 km/h) ne sont pas soumises au contrôle technique périodique. Vous n'avez donc aucune formalité de ce type avant de vendre."),
   ("Ce qui fait varier le prix", "L'année, le kilométrage (ou les heures moteur), l'état de la carrosserie et des pneus, l'entretien du moteur diesel, l'état des batteries pour une voiturette électrique, et la présence de la carte grise et du carnet d'entretien."),
   ("Une vente sans prise de tête", "Estimation à partir des informations de votre demande, expertise, offre ferme, puis signature du certificat de cession. Nous nous occupons de la déclaration de cession."),
  ],
  faq=[
   ("Rachetez-vous une voiture sans permis qui ne démarre plus ?", "Oui, elle peut être étudiée. Une voiturette en panne est reprise au prix de son état : indiquez le problème dans la demande pour obtenir une estimation réaliste."),
   ("Y a-t-il un contrôle technique pour une voiture sans permis ?", "Non. Les voitures sans permis ne sont pas soumises au contrôle technique périodique, ce qui simplifie la vente."),
   ("Quels papiers faut-il pour vendre ma voiturette ?", "La carte grise, une pièce d'identité, et si possible le carnet d'entretien et le double des clés. Nous établissons le certificat de cession avec vous."),
   ("Reprenez-vous les voitures sans permis électriques ?", "Oui, selon l'état et l'autonomie des batteries. Précisez l'année et le modèle pour une première estimation."),
  ]),
 dict(slug="rachat-camping-car-morbihan", nav="Camping-car", name="camping-car", h1="Rachat de camping-car dans le Morbihan",
  title="Rachat camping-car Morbihan | Profilé, capucine, van – Vannes",
  desc="Vendez votre camping-car dans le Morbihan : profilé, capucine, intégral, van aménagé, fourgon. Estimation gratuite, offre ferme, sans CT.",
  lead="Reprise Auto Express rachète les camping-cars et vans aménagés dans tout le Morbihan, du fourgon aménagé au profilé ou à l'intégral, dans l'état et sans que vous ayez à le mettre en vente vous-même.",
  sections=[
   ("Quels camping-cars sont repris ?", "Profilés, capucines, intégraux, vans et fourgons aménagés, sur base Fiat Ducato, Citroën Jumper, Peugeot Boxer, Renault Master, Mercedes Sprinter ou Ford Transit. Les marques d'aménagement courantes (Rapido, Pilote, Challenger, Bürstner, Hymer, Dethleffs, Adria, Font Vendôme…) sont étudiées modèle par modèle."),
   ("Ce que nous regardons en priorité", "L'état de la cellule (traces d'humidité ou d'infiltration), le moteur et la boîte, le kilométrage, l'âge, le poids total autorisé en charge, les équipements (panneaux solaires, toit relevable, porte-vélos, chauffage, frigo) et la présence du carnet d'entretien et des factures."),
   ("Vendre sans contrôle technique à fournir", "Pour une vente à un professionnel, le contrôle technique n'est pas demandé. Si votre camping-car est en panne, a séjourné longtemps à l'arrêt ou nécessite des réparations, il peut quand même être étudié."),
   ("Démarches et paiement", "Nous établissons le certificat de cession, vérifions la situation administrative du véhicule et déclarons la cession. Vous recevez une offre écrite avant toute signature, puis vous êtes réglé par virement ou en espèces (dans la limite légale)."),
  ],
  faq=[
   ("Rachetez-vous un camping-car qui n'a pas roulé depuis longtemps ?", "Oui, il est étudié sur place. Un camping-car resté à l'arrêt peut nécessiter une remise en route ; ce coût est pris en compte dans l'offre."),
   ("Reprenez-vous les vans et fourgons aménagés ?", "Oui. Les vans aménagés, fourgons transformés et camions aménagés sont repris selon leur état, leur équipement et la conformité de l'aménagement."),
   ("Qu'est-ce qui décote le plus un camping-car à la revente ?", "Surtout l'humidité dans la cellule, un kilométrage élevé, un entretien incomplet et un moteur fatigué. Des factures d'entretien à jour valorisent le véhicule."),
   ("Dois-je venir à vous avec mon camping-car ?", "Non. Un conseiller se déplace à votre domicile dans les 24 h suivant votre demande, y compris pour un véhicule volumineux ou non roulant."),
  ]),
 dict(slug="rachat-utilitaire-morbihan", nav="Utilitaire", name="utilitaire", h1="Rachat d'utilitaire dans le Morbihan",
  title="Rachat utilitaire Morbihan | Fourgon, camionnette – Reprise Auto Express",
  desc="Rachat d'utilitaire dans le Morbihan : fourgon, camionnette, pick-up, benne, frigo. Pros et particuliers, sans CT, même HS. Offre ferme.",
  lead="Artisan, entreprise ou particulier : Reprise Auto Express rachète votre véhicule utilitaire à Vannes et dans tout le Morbihan, que vous renouveliez votre flotte ou que vous vous en sépariez simplement.",
  sections=[
   ("Quels utilitaires rachetons-nous ?", "Fourgons, camionnettes, fourgonnettes, pick-up, plateaux, bennes, utilitaires frigorifiques, véhicules d'entreprise et d'artisan, du petit citadin utilitaire au grand volume : Renault Kangoo et Master, Peugeot Partner et Boxer, Citroën Berlingo et Jumper, Fiat Ducato, Ford Transit, Mercedes Sprinter, Volkswagen Crafter, Iveco Daily."),
   ("Particuliers, artisans, entreprises", "Les professionnels peuvent vendre avec facture : nous gérons la facturation (HT ou TTC) selon votre statut. Pour les flottes, plusieurs véhicules peuvent être étudiés dans la même démarche."),
   ("Vendre dans l'état, avec ou sans contrôle technique", "Un utilitaire fortement kilométré, marqué par le travail ou en panne reste reprenable. Nous estimons la valeur de marché et déduisons les remises en état nécessaires. Aucun contrôle technique n'est demandé pour la vente à un professionnel."),
   ("Papiers à prévoir", "Carte grise, pièce d'identité (ou Kbis pour une société), carnet d'entretien et clés. Les aménagements spécifiques (étagères, rack, hayon) sont pris en compte dans l'estimation."),
  ],
  faq=[
   ("Rachetez-vous des utilitaires d'entreprise ?", "Oui. Les sociétés et artisans peuvent vendre leur véhicule avec facture ; le traitement (HT ou TTC) dépend de votre statut et se précise lors de la demande."),
   ("Mon utilitaire a beaucoup de kilomètres, est-ce un problème ?", "Non. Un utilitaire à fort kilométrage est une situation courante ; il est repris à sa valeur de marché diminuée des travaux à prévoir."),
   ("Reprenez-vous les pick-up et les camionnettes plateau ?", "Oui. Pick-up, plateaux, bennes et caisses frigorifiques sont étudiés selon leur état et leur équipement."),
   ("Peut-on vendre plusieurs utilitaires en même temps ?", "Oui. Précisez le nombre et la nature des véhicules dans votre demande pour une estimation globale."),
  ]),
 dict(slug="rachat-camion-morbihan", nav="Camion", name="camion", h1="Rachat de camion dans le Morbihan",
  title="Rachat camion Morbihan | Porteur, plateau, benne – Vannes",
  desc="Rachat de camion dans le Morbihan : porteur, plateau, benne, tracteur routier. Estimation gratuite, offre ferme, sans CT.",
  lead="Vous vendez un camion ou un porteur dans le Morbihan ? Reprise Auto Express étudie votre véhicule, vous propose une offre ferme et s'occupe des documents de cession.",
  sections=[
   ("Quels camions rachetons-nous ?", "Porteurs, camions plateau, bennes, camions-grues, caisses fourgon, frigorifiques, tracteurs routiers et véhicules de chantier de 3,5 tonnes et plus. Chaque dossier est étudié selon la marque, l'âge, le kilométrage, l'état mécanique et l'équipement."),
   ("Ce qui compte pour l'estimation", "Le poids total autorisé en charge, la configuration (carrosserie, hayon, grue, benne), le kilométrage, l'état du moteur et de la boîte, les pneus, le carnet d'entretien et les contrôles techniques à jour. Les photos et la carte grise accélèrent l'étude."),
   ("Vendre dans l'état", "Un camion en fin de vie, accidenté ou non conforme peut être étudié : l'offre déduit les travaux nécessaires. Aucun passage préalable au contrôle technique n'est demandé pour la vente à un professionnel."),
   ("Un interlocuteur, une offre écrite", "Vous échangez avec un seul interlocuteur, l'offre est écrite et ferme après expertise, et les documents de cession sont préparés avec vous."),
  ],
  faq=[
   ("Rachetez-vous les camions hors d'usage ou accidentés ?", "Ils peuvent être étudiés au cas par cas. L'état réel et les réparations à prévoir sont pris en compte dans l'offre."),
   ("Quels documents faut-il pour vendre un camion ?", "La carte grise, une pièce d'identité ou un Kbis pour une société, et si possible l'historique d'entretien et le dernier contrôle technique."),
   ("Reprenez-vous les tracteurs routiers et les bennes ?", "Oui, selon l'état, l'âge et le kilométrage. Indiquez la marque, le modèle, l'année et le PTAC dans votre demande."),
   ("Un camion est-il un utilitaire ?", "Non : au-delà de 3,5 tonnes de PTAC, on parle de camion. En dessous, il s'agit généralement d'un véhicule utilitaire léger."),
  ]),
 dict(slug="rachat-voiture-sans-controle-technique-morbihan", nav="Sans CT", name="voiture sans contrôle technique", h1="Rachat de voiture sans contrôle technique dans le Morbihan",
  title="Rachat voiture sans contrôle technique Morbihan (sans CT)",
  desc="Vendez votre voiture sans contrôle technique ou recalée au CT dans le Morbihan. Reprise dans l'état à Vannes, aucune réparation à faire.",
  lead="Pas de contrôle technique, contrôle expiré ou contre-visite impossible ? Reprise Auto Express rachète votre véhicule sans CT dans le Morbihan, dans l'état, sans réparation de votre part.",
  sections=[
   ("Pourquoi le contrôle technique n'est pas nécessaire", "L'obligation de présenter un contrôle technique de moins de 6 mois (2 mois en cas de contre-visite) s'applique à la vente d'un véhicule d'occasion à un particulier. Quand le rachat est fait par un professionnel de l'automobile, ce document n'est pas demandé."),
   ("Voiture recalée au contrôle technique", "Si votre voiture a été refusée, avec défaillances majeures ou critiques, inutile d'engager des frais de remise en état avant de la vendre : nous estimons le coût des réparations et le déduisons de la valeur de marché."),
   ("Contrôle périmé, véhicule immobilisé", "Une voiture restée à l'arrêt, dont le contrôle technique est périmé, peut être rachetée. Nous indiquons ce qu'il faut prévoir pour l'enlèvement si le véhicule n'est plus en état de rouler."),
   ("Un dossier simple", "Carte grise, pièce d'identité, clés. Le reste (certificat de cession, déclaration de cession) est préparé avec vous."),
  ],
  faq=[
   ("Peut-on vendre une voiture sans contrôle technique à un professionnel ?", "Oui. Le contrôle technique de moins de 6 mois est requis pour une vente à un particulier, pas pour une reprise par un professionnel de l'automobile."),
   ("Ma voiture a été recalée au contrôle technique, puis-je la vendre ?", "Oui, elle est reprise dans l'état. Le coût des réparations à prévoir est déduit de la valeur du véhicule."),
   ("Mon contrôle technique est périmé depuis longtemps, est-ce bloquant ?", "Non. Il suffit de l'indiquer dans la demande. Si le véhicule n'est plus en état de rouler, l'enlèvement est étudié."),
   ("Dois-je faire réparer avant de vendre ?", "Non. Vous vendez dans l'état, sans aucune dépense préalable."),
  ]),
 dict(slug="rachat-vehicule-hs-accidente-morbihan", nav="HS / accidenté", name="véhicule HS ou accidenté", h1="Rachat de voiture HS, en panne ou accidentée dans le Morbihan",
  title="Rachat voiture HS, en panne ou accidentée Morbihan – Vannes",
  desc="Voiture HS, moteur cassé, boîte HS, en panne ou accidentée dans le Morbihan ? Rachat dans l'état à Vannes, enlèvement étudié, offre ferme.",
  lead="Moteur cassé, boîte de vitesses HS, panne coûteuse, accident : votre véhicule n'est plus utilisable. Reprise Auto Express étudie son rachat dans tout le Morbihan, sans que vous ayez à le réparer.",
  sections=[
   ("Quels véhicules HS sont repris ?", "Voitures, voitures sans permis, utilitaires et camping-cars avec une panne moteur, une boîte de vitesses hors d'usage, un embrayage, une turbo ou un injecteur défaillant, une casse suite à un sinistre, un incendie partiel ou une inondation. Chaque dossier est étudié selon les pièces concernées et la valeur de marché du modèle."),
   ("Comment le prix d'un véhicule HS est fixé", "On part de la valeur du véhicule en bon état, puis on déduit le coût de la réparation ou de la remise en état. Parfois, le véhicule garde une valeur de pièces ou d'export : c'est pris en compte."),
   ("Enlèvement et papiers", "Un conseiller se déplace à votre domicile dans les 24 h. Si votre véhicule ne roule plus, l'enlèvement peut être étudié selon sa localisation dans le Morbihan. Indiquez l'adresse (commune et code postal) pour une organisation adaptée. Carte grise, pièce d'identité et certificat de situation administrative suffisent en général."),
   ("Épave ou véhicule économiquement irréparable", "Certains véhicules fortement endommagés relèvent d'une procédure réglementaire spécifique. Nous vous indiquons la marche à suivre au cas par cas."),
  ],
  faq=[
   ("Rachetez-vous une voiture avec un moteur HS ?", "Oui, elle est étudiée. Le coût estimé de la réparation est déduit de la valeur du véhicule en bon état."),
   ("Mon véhicule ne roule plus, comment faire ?", "Indiquez la commune et le code postal. L'expertise et l'enlèvement sont organisés selon le cas."),
   ("Rachetez-vous une voiture accidentée non roulante ?", "Oui, selon l'ampleur des dégâts. Des photos et l'état administratif du véhicule permettent une première estimation."),
   ("Que faire de la carte grise d'un véhicule HS vendu ?", "Elle est remise lors de la cession, barrée et signée, avec le certificat de cession. Nous déclarons la cession pour vous décharger de la responsabilité du véhicule."),
  ]),
]
VBY = {v["slug"]: v for v in VEHICLES}

HOME_FAQ = [
 ("Comment fonctionne le rachat de ma voiture à Vannes ?", "Vous remplissez la demande d'estimation en ligne, un conseiller vous recontacte et se déplace chez vous dans les 24 h pour expertiser le véhicule, puis vous recevez une offre ferme. Si vous acceptez, les documents de cession sont signés et vous êtes payé, sans obligation d'achat."),
 ("Faut-il un contrôle technique pour vendre à un professionnel ?", "Non. Le contrôle technique de moins de 6 mois est obligatoire pour vendre à un particulier, pas pour une reprise par un professionnel. Votre véhicule est repris sans CT, dans l'état."),
 ("Rachetez-vous les voitures HS, en panne ou accidentées ?", "Oui, elles sont étudiées au cas par cas. Le coût des réparations est déduit de la valeur du véhicule en bon état, et l'enlèvement peut être organisé dans le Morbihan."),
 ("Quels véhicules rachetez-vous ?", "Voitures, voitures sans permis, camping-cars, utilitaires et camions, particuliers comme professionnels, en essence, diesel, hybride ou électrique."),
 ("Quels documents faut-il fournir ?", "La carte grise, une pièce d'identité, les clés (si possible le double), le carnet d'entretien et, si vous en avez un, le dernier contrôle technique. Nous préparons le certificat de cession avec vous."),
 ("Comment le prix de rachat est-il calculé ?", "À partir de la cote du modèle, des options, de l'état constaté, des réparations à prévoir et des véhicules comparables dans la région. Après expertise, l'offre est ferme et écrite."),
 ("Dois-je acheter un autre véhicule pour vendre le mien ?", "Non. Le rachat est indépendant de tout achat. Vous vendez votre véhicule sans aucune obligation."),
 ("Vous déplacez-vous à domicile ?", "Oui. Un conseiller se déplace à votre domicile dans les 24 h suivant votre demande, examine le véhicule et vous remet une offre ferme. Aucun déplacement de votre part n'est nécessaire."),
 ("Comment suis-je payé : espèces ou virement ?", "Au choix : virement bancaire ou espèces. Le paiement en espèces est plafonné par la loi (1 000 € pour une transaction avec un professionnel) ; au-delà, le règlement se fait par virement."),
 ("Puis-je vendre un véhicule encore en crédit ?", "Dans certains cas oui, si le solde est régularisé auprès de l'organisme de financement. Indiquez-le dès votre demande."),
 ("Quelles communes du Morbihan couvrez-vous ?", "Toutes les communes du département, de Vannes à Lorient, Pontivy, Ploërmel, Auray, Questembert ou Sarzeau, soit les 76 codes postaux du Morbihan (56)."),
 ("Quelle différence entre une estimation en ligne et une offre ferme ?", "Une estimation en ligne est indicative. L'offre ferme est établie après expertise du véhicule : c'est le montant que vous recevez si vous acceptez."),
 ("Que faire de la carte grise et de l'assurance après la vente ?", "La carte grise est barrée et signée au moment de la cession et la déclaration de cession est déposée. Il vous reste à prévenir votre assureur pour résilier ou transférer le contrat."),
 ("Pourquoi vendre à un professionnel plutôt qu'à un particulier ?", "Pas d'annonces, pas de visites ni de négociations, pas de contrôle technique à fournir, pas de risque d'impayé. Le prix peut être légèrement inférieur à une vente entre particuliers, mais la démarche est plus rapide et sécurisée."),
]

STEPS = [
 ("Estimation", "Vous remplissez le formulaire avec la marque, le modèle, l'année, le kilométrage et l'état de votre véhicule."),
 ("Déplacement", "Un conseiller vous rappelle et se déplace à votre domicile dans les 24 h pour examiner le véhicule."),
 ("Offre ferme", "Vous recevez une offre écrite et ferme, sans obligation d'achat."),
 ("Signature et paiement", "Vous signez le certificat de cession et vous êtes réglé par virement ou en espèces (dans la limite légale). Nous déclarons la cession à votre place."),
]

NEAR_VANNES = ["Séné","Saint-Avé","Arradon","Plescop","Theix-Noyalo","Surzur","Sarzeau","Elven","Monterblanc","Meucon","Ploeren","Saint-Nolff","Sulniac","Grand-Champ","Baden","Île-aux-Moines","Larmor-Baden","Le Hézo","Arzon","Locmariaquer","Auray","Questembert","Muzillac","Pluneret"]
TOP = ["Vannes","Lorient","Auray","Pontivy","Ploërmel","Lanester","Ploemeur","Hennebont","Séné","Saint-Avé","Sarzeau","Questembert","Muzillac","Languidic","Quéven","Plescop","Elven","Guidel","Pluvigner","Locminé"]

# ------------------------------------------------------------------ COMPOSANTS
def url(path):
    return SITE_URL + path

def phone_href():
    return "tel:" + re.sub(r"[^0-9+]", "", PHONE) if PHONE else ""

def head(title, desc, path, schema, noindex=False, og_image=True):
    robots = "noindex,nofollow" if (PREPROD or noindex) else "index,follow,max-image-preview:large,max-snippet:-1"
    ld = "".join('<script type="application/ld+json">%s</script>' % json.dumps(s, ensure_ascii=False, separators=(",", ":")) for s in schema)
    return f"""<!doctype html>
<html lang="fr"{(' data-email="%s"' % E(EMAIL)) if EMAIL else ''}><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url(path)}">
<meta name="theme-color" content="#0b2a5b">
<meta property="og:type" content="website"><meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="{BRAND}"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url(path)}">
<meta property="og:image" content="{url('/assets/og-reprise-auto-express.jpg')}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/style.css">
{ld}</head><body>"""

def header():
    nav = "".join(f'<a href="/{v["slug"]}/">{E(v["nav"])}</a>' for v in VEHICLES[:5])
    nav += "".join(f'<a class="mo" href="/{v["slug"]}/">{E(v["nav"])}</a>' for v in VEHICLES[5:])
    cta = '<a class="btn btn-red" href="#estimation">Je vends mon véhicule</a>'
    tel = f'<a class="tel" href="{phone_href()}">{E(PHONE)}</a>' if PHONE else ""
    return f"""<div class="ann"><div class="wrap">Déplacement à domicile sous 24 h · Paiement par virement ou espèces</div></div>
<header class="hd"><div class="wrap hd-in">
<a class="brand" href="/" aria-label="Reprise Auto Express – accueil"><img src="/assets/logo-header.jpg" width="75" height="88" alt="Reprise Auto Express – rachat de véhicule et utilitaire"></a>
<nav class="nav" id="nav" aria-label="Navigation principale"><a href="/reprise-voiture-vannes/">Vannes</a>{nav}<a href="/zone-intervention-morbihan/">Zones</a></nav>
<div class="hd-cta">{tel}{cta}<button class="burger" type="button" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="nav"><span></span></button></div></div></header>"""

def footer():
    vl = "".join(f'<li><a href="/{v["slug"]}/">{E(v["h1"])}</a></li>' for v in VEHICLES)
    tl = "".join(f'<li><a href="/reprise-voiture-{BY_SLUG[slugify(t)]["slug"]}/">Reprise voiture {E(t)}</a></li>' for t in TOP[:14])
    contact = ""
    if PHONE: contact += f'<p><a href="{phone_href()}">{E(PHONE)}</a></p>'
    if EMAIL: contact += f'<p><a href="mailto:{E(EMAIL)}">{E(EMAIL)}</a></p>'
    if ADDRESS: contact += f"<p>{E(ADDRESS)}</p>"
    return f"""<footer class="ft"><div class="wrap ft-grid">
<div><p class="ft-t">{BRAND}</p><p>Rachat de voiture, voiture sans permis, camping-car, utilitaire et camion à Vannes et dans tout le Morbihan (56). Sans contrôle technique, même HS.</p>{contact}</div>
<div><p class="ft-t">Véhicules rachetés</p><ul>{vl}</ul></div>
<div><p class="ft-t">Villes</p><ul>{tl}<li><a href="/zone-intervention-morbihan/">Tous les codes postaux du Morbihan</a></li></ul></div>
</div><div class="wrap ft-bot"><span>© 2026 {BRAND}</span> <a href="/mentions-legales/">Mentions légales</a></div></footer>
<a class="sticky-cta" href="#estimation">Estimer mon véhicule</a>
<script src="/assets/app.js" defer></script></body></html>"""

def breadcrumb(items):
    lis = "".join(f'<li>{"<a href=%s>%s</a>" % (chr(34)+h+chr(34), E(t)) if h else E(t)}</li>' for t, h in items)
    return f'<nav class="bc wrap" aria-label="Fil d\'Ariane"><ol>{lis}</ol></nav>'

def ld_breadcrumb(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": t, "item": url(h)} for i, (t, h) in enumerate(items)]}

def ld_faq(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

def ld_business():
    b = {"@context": "https://schema.org", "@type": ["LocalBusiness", "AutomotiveBusiness"], "@id": url("/#business"),
         "name": BRAND, "url": url("/"), "image": url("/assets/og-reprise-auto-express.jpg"),
         "description": "Rachat de voiture, voiture sans permis, camping-car, utilitaire et camion à Vannes et dans tout le Morbihan, sans contrôle technique, même HS. Déplacement à domicile sous 24 h, paiement par virement ou en espèces.",
         "areaServed": [{"@type": "AdministrativeArea", "name": "Morbihan"}] + [{"@type": "City", "name": c} for c in TOP],
         "knowsAbout": ["Rachat de voiture", "Reprise de véhicule", "Voiture sans permis", "Camping-car", "Utilitaire", "Camion", "Véhicule sans contrôle technique", "Véhicule HS"],
         "serviceType": "Rachat de véhicules d'occasion"}
    if PHONE: b["telephone"] = PHONE
    if EMAIL: b["email"] = EMAIL
    if ADDRESS: b["address"] = {"@type": "PostalAddress", "streetAddress": ADDRESS, "addressCountry": "FR"}
    return b

def ld_service(name, path, area):
    return {"@context": "https://schema.org", "@type": "Service", "name": name, "url": url(path),
            "provider": {"@id": url("/#business")}, "areaServed": area, "serviceType": "Rachat de véhicules d'occasion"}

def form(default_commune=""):
    opts = "".join(f'<option value="{E(c["name"])} ({c["cp"]})">' for c in communes)
    return f"""<section class="est" id="estimation"><div class="wrap"><div class="est-card">
<h2>Estimation gratuite de votre véhicule</h2><p class="muted">Un conseiller vous rappelle rapidement. Sans obligation d'achat.</p>
<form id="est-form" novalidate>
<div class="g2"><label>Type de véhicule<select name="type" required><option>Voiture</option><option>Voiture sans permis</option><option>Camping-car</option><option>Utilitaire</option><option>Camion</option></select></label>
<label>Commune ou code postal<input name="commune" list="communes" value="{E(default_commune)}" required autocomplete="off"></label></div>
<div class="g2 k"><label>Marque<input name="marque" required></label><label>Modèle<input name="modele" required></label></div>
<div class="g2 k"><label>Année<input name="annee" inputmode="numeric" required></label><label>Kilométrage<input name="km" inputmode="numeric" required></label></div>
<div class="g2"><label>Nom<input name="nom" required autocomplete="name"></label><label>Téléphone<input name="tel" type="tel" required autocomplete="tel"></label></div>
<details class="more"><summary>Ajouter des précisions (facultatif)</summary><div class="g3">
<label>État<select name="etat"><option>Roulant, bon état</option><option>Sans contrôle technique</option><option>Recalé au contrôle technique</option><option>HS / en panne</option><option>Accidenté</option></select></label>
<label>Énergie<select name="energie"><option>Diesel</option><option>Essence</option><option>Hybride</option><option>Électrique</option><option>GPL</option></select></label>
<label>E-mail<input name="mail" type="email" autocomplete="email"></label></div></details>
<datalist id="communes">{opts}</datalist>
<button class="btn btn-red btn-lg btn-block" type="submit">Recevoir mon estimation</button>
<p class="fine">Les informations transmises servent uniquement à étudier votre demande et à vous recontacter. Contact : {E(EMAIL)}</p>
<p id="est-msg" class="msg" role="status" hidden></p></form></div></div></section>"""

def steps_html():
    items = "".join(f'<li><span class="n">{i+1}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(STEPS))
    return f'<section class="sec"><div class="wrap"><h2>Comment fonctionne le rachat ?</h2><ol class="steps">{items}</ol></div></section>'

ICONS = {
 "car": '<svg viewBox="0 0 48 36" aria-hidden="true"><path d="M4 24l3-9c1-3 3-5 7-5h14c3 0 5 1 7 4l6 4c2 1 3 2 3 5v3H4z" fill="currentColor"/><circle cx="14" cy="28" r="4" fill="#fff" stroke="currentColor" stroke-width="2.5"/><circle cx="36" cy="28" r="4" fill="#fff" stroke="currentColor" stroke-width="2.5"/></svg>',
 "camper": '<svg viewBox="0 0 48 36" aria-hidden="true"><path d="M3 11c0-2 1-4 4-4h30c2 0 4 1 5 3l4 8v9H3z" fill="currentColor"/><rect x="9" y="12" width="10" height="7" rx="1.5" fill="#fff"/><rect x="23" y="12" width="9" height="7" rx="1.5" fill="#fff"/><circle cx="14" cy="28" r="4" fill="#fff" stroke="currentColor" stroke-width="2.5"/><circle cx="37" cy="28" r="4" fill="#fff" stroke="currentColor" stroke-width="2.5"/></svg>',
 "van": '<svg viewBox="0 0 48 36" aria-hidden="true"><path d="M3 8h27v19H3zM30 13h9l7 7v7H30z" fill="currentColor"/><circle cx="13" cy="28" r="4" fill="#fff" stroke="currentColor" stroke-width="2.5"/><circle cx="37" cy="28" r="4" fill="#fff" stroke="currentColor" stroke-width="2.5"/></svg>',
 "truck": '<svg viewBox="0 0 48 36" aria-hidden="true"><path d="M2 5h28v22H2zM30 11h10l6 8v8H30z" fill="currentColor"/><circle cx="12" cy="29" r="4" fill="#fff" stroke="currentColor" stroke-width="2.5"/><circle cx="21" cy="29" r="4" fill="#fff" stroke="currentColor" stroke-width="2.5"/><circle cx="38" cy="29" r="4" fill="#fff" stroke="currentColor" stroke-width="2.5"/></svg>',
 "doc": '<svg viewBox="0 0 48 36" aria-hidden="true"><path d="M14 2h15l8 8v24H14z" fill="currentColor"/><path d="M20 17l12 12M32 17L20 29" stroke="#fff" stroke-width="3"/></svg>',
 "warn": '<svg viewBox="0 0 48 36" aria-hidden="true"><path d="M24 2L45 34H3z" fill="currentColor"/><rect x="22.3" y="13" width="3.4" height="10" fill="#fff"/><rect x="22.3" y="26" width="3.4" height="3.4" fill="#fff"/></svg>',
}
VICON = {"rachat-voiture-morbihan": "car", "rachat-voiture-sans-permis-morbihan": "car", "rachat-camping-car-morbihan": "camper",
         "rachat-utilitaire-morbihan": "van", "rachat-camion-morbihan": "truck",
         "rachat-voiture-sans-controle-technique-morbihan": "doc", "rachat-vehicule-hs-accidente-morbihan": "warn"}

def vcard(v, txt):
    return f'<a class="card" href="/{v["slug"]}/"><span class="ic">{ICONS[VICON[v["slug"]]]}</span><div><h3>{E(v["h1"])}</h3><p>{txt}</p></div></a>'

def vehicles_grid():
    cards = "".join(vcard(v, E(v["lead"][:118].rsplit(" ", 1)[0]) + "…") for v in VEHICLES)
    return f'<section class="sec alt"><div class="wrap"><h2>Tous les véhicules que nous rachetons</h2><div class="cards">{cards}</div></div></section>'

def faq_html(faq, title="Questions fréquentes"):
    items = "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq)
    return f'<section class="sec"><div class="wrap narrow"><h2>{title}</h2>{items}</div></section>'

def compare_table():
    cols = ["Entre particuliers", "En concession (reprise)", "Reprise Auto Express"]
    rows = [
     ("Annonce et visites", "Oui, à gérer", "Non", "Non"),
     ("Contrôle technique de moins de 6 mois", "Obligatoire", "Non", "Non"),
     ("Véhicule HS, accidenté, très kilométré", "Très difficile", "Souvent refusé", "Étudié au cas par cas"),
     ("Obligation d'achat d'un autre véhicule", "Non", "Souvent liée", "Non"),
     ("Déplacement à domicile", "Vous recevez des visiteurs", "Vous vous déplacez", "Oui, sous 24 h"),
     ("Paiement", "Variable, risque d'impayé", "Variable", "Virement ou espèces (limite légale)"),
     ("Démarches de cession", "À votre charge", "Prises en charge", "Prises en charge"),
     ("Offre ferme après expertise", "Négociable", "Oui", "Oui"),
    ]
    body = "".join("<tr><th>%s</th>%s</tr>" % (r[0], "".join('<td data-label="%s">%s</td>' % (cols[i], r[i + 1]) for i in range(3))) for r in rows)
    head = "".join("<th>%s</th>" % c for c in cols)
    return f'''<section class="sec alt"><div class="wrap"><h2>Vente à un particulier, en concession ou à Reprise Auto Express : le comparatif</h2>
<div class="tw"><table class="cmp"><thead><tr><th></th>{head}</tr></thead><tbody>{body}</tbody></table></div></div></section>'''

def zone_links(names, title):
    lis = "".join(f'<li><a href="/reprise-voiture-{BY_SLUG[slugify(n)]["slug"]}/">{E(n)}</a></li>' for n in names)
    return f'<section class="sec"><div class="wrap"><h2>{title}</h2><ul class="chips">{lis}</ul></div></section>'

def enriched_html(c, e):
    nm = c["name"]
    for n in e["voisines"]:
        assert slugify(n) in BY_SLUG, n
    vs = ", ".join(f'<a href="/reprise-voiture-{BY_SLUG[slugify(n)]["slug"]}/">{E(n)}</a>' for n in e["voisines"])
    return (f'<section class="sec alt"><div class="wrap narrow"><h2>Vendre son véhicule {prep(nm)} : le secteur</h2>'
            f'<p>{E(e["desc"])}</p><p>{E(e["atout"])}</p>'
            f'<p><b>Communes voisines couvertes :</b> {vs}.</p>'
            f'<h3>Un conseiller chez vous sous 24 h</h3><p>Pour {E(nm)} comme pour les communes voisines, un conseiller se déplace à votre domicile dans les 24 h suivant votre demande, examine le véhicule, vous remet une offre ferme et prépare le certificat de cession. Le règlement se fait par virement ou en espèces, dans la limite fixée par la loi.</p></div></section>')

def page(path, title, desc, schema, body, crumbs=None, hero=""):
    out = head(title, desc, path, schema) + header()
    if crumbs: out += breadcrumb(crumbs)
    out += hero + body + footer()
    d = os.path.join(OUT, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)

def hero(h1, lead, kicker, show_img=True):
    img = '<img class="hero-img" src="/assets/reprise-auto-express-logo.jpg" width="360" height="421" alt="Reprise Auto Express – rachat de véhicule et utilitaire, remise de clés et paiement" fetchpriority="high">' if show_img else ""
    return f"""<section class="hero"><div class="wrap hero-in"><div><p class="kicker">{kicker}</p><h1>{h1}</h1><p class="lead">{lead}</p>
<ul class="ticks"><li>Déplacement à domicile sous 24 h</li><li>Sans contrôle technique, même HS</li><li>Offre ferme, sans obligation d'achat</li><li>Paiement par virement ou en espèces*</li></ul>
<p><a class="btn btn-red btn-lg" href="#estimation">Estimer mon véhicule</a> {f'<a class="btn btn-ghost btn-lg" href="{phone_href()}">Appeler {E(PHONE)}</a>' if PHONE else ''}</p><p class="fine">* Espèces dans la limite fixée par la loi (1 000 € pour une transaction avec un professionnel).</p></div>{img}</div></section>"""

def tldr(items):
    li = "".join(f"<li>{x}</li>" for x in items)
    return f'<section class="sec"><div class="wrap narrow"><div class="tldr"><p class="tldr-t">En bref</p><ul>{li}</ul></div></div></section>'

# ------------------------------------------------------------------ BUILD
def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "assets"))
    for f in os.listdir(os.path.join(ROOT, "assets")):
        shutil.copy(os.path.join(ROOT, "assets", f), os.path.join(OUT, "assets", f))
    urls = []

    # ---------- Accueil
    path = "/"
    h = hero("Rachat de voiture à Vannes et dans tout le Morbihan",
             "Voiture, voiture sans permis, camping-car, utilitaire, camion : Reprise Auto Express rachète votre véhicule dans l'état, sans contrôle technique, même HS, et vous remet une offre ferme après expertise.",
             "Reprise Auto Express · Vannes · Morbihan (56)")
    body = form()
    body += tldr([
        "<b>Reprise Auto Express</b> rachète les véhicules d'occasion des particuliers et des professionnels dans tout le Morbihan (56).",
        "<b>Véhicules :</b> voiture, voiture sans permis, camping-car, utilitaire, camion.",
        "<b>Sans contrôle technique</b> à fournir : le CT de moins de 6 mois n'est exigé que pour une vente à un particulier.",
        "<b>Même HS :</b> panne, moteur ou boîte cassés, accident, véhicule non roulant : étudié au cas par cas.",
        "<b>Déplacement à domicile sous 24 h</b>, offre ferme et écrite après expertise, <b>sans obligation d'achat</b>.",
        "<b>Paiement</b> par virement ou en espèces (dans la limite légale).",
    ])
    body += steps_html()
    body += vehicles_grid()
    body += """<section class="sec"><div class="wrap narrow"><h2>Pourquoi faire racheter votre véhicule par Reprise Auto Express ?</h2>
<p>Vendre sa voiture entre particuliers prend du temps : photos, annonce, appels, visites, négociations, contrôle technique de moins de 6 mois, risque d'impayé. Le rachat par un professionnel simplifie tout : vous présentez le véhicule, vous recevez une offre ferme, vous signez.</p>
<h3>Rachat sans contrôle technique</h3><p>Pour la reprise par un professionnel de l'automobile, le contrôle technique n'est pas demandé. Votre véhicule est repris dans l'état, avec ses défauts, sans passage préalable en centre de contrôle.</p>
<h3>Rachat de véhicule HS, en panne ou accidenté</h3><p>Une panne coûteuse ou un accident ne rend pas votre véhicule invendable. Nous estimons le coût de remise en état et le déduisons de la valeur de marché pour vous proposer un prix réaliste.</p>
<h3>Un conseiller chez vous sous 24 h</h3><p>Vous n'avez pas à vous déplacer : un conseiller vient à votre domicile dans les 24 h suivant votre demande, examine le véhicule et vous remet une offre ferme. Vous êtes réglé par virement ou en espèces (dans la limite fixée par la loi).</p>
<h3>Un seul interlocuteur, des démarches prises en charge</h3><p>Nous préparons le certificat de cession et déclarons la cession à votre place, ce qui vous décharge de la responsabilité du véhicule. Il vous reste à informer votre assureur.</p></div></section>"""
    body += """<section class="sec alt"><div class="wrap narrow"><h2>Comment est calculé le prix de rachat ?</h2>
<p>Le prix repose sur la valeur de marché du modèle (cote, annonces comparables dans la région), puis sur ce que nous constatons : année, kilométrage, version, options, état de la carrosserie et de la mécanique, historique d'entretien. Les réparations nécessaires sont chiffrées et déduites. Après l'expertise, l'offre est <b>ferme</b> : le montant annoncé est celui qui est proposé à la signature.</p>
<p>Une estimation en ligne ne peut qu'être indicative : seul un examen du véhicule permet de confirmer un prix.</p></div></section>"""
    body += compare_table()
    body += """<section class="sec"><div class="wrap narrow"><h2>Documents à prévoir pour vendre votre véhicule</h2>
<ul class="list"><li>La carte grise du véhicule (certificat d'immatriculation)</li><li>Une pièce d'identité du propriétaire (ou le Kbis pour une société)</li><li>Les clés et, si possible, le double</li><li>Le carnet d'entretien et les factures</li><li>Le dernier contrôle technique, si vous en avez un (non obligatoire)</li></ul>
<p>Nous vérifions la situation administrative du véhicule (gage, opposition) et établissons le certificat de cession avec vous.</p></div></section>"""
    body += zone_links(TOP, "Rachat de voiture dans les principales villes du Morbihan")
    body += f'<section class="sec alt"><div class="wrap narrow"><h2>Nous intervenons dans tout le Morbihan (56)</h2><p>Les 76 codes postaux et toutes les communes du département sont couverts, de la presqu\'île de Rhuys au pays de Pontivy, du golfe du Morbihan à Lorient et au pays de Ploërmel. <a href="/zone-intervention-morbihan/">Voir tous les codes postaux et toutes les communes du Morbihan</a>.</p></div></section>'
    body += faq_html(HOME_FAQ)
    body += '<section class="sec cta-band"><div class="wrap"><h2>Prêt à vendre votre véhicule ?</h2><p>Estimation gratuite, sans obligation.</p><a class="btn btn-red btn-lg" href="#estimation">Estimer mon véhicule</a>' + (f'<p style="margin-top:14px">Ou écrivez-nous : <a style="color:#fff;font-weight:700" href="mailto:{E(EMAIL)}">{E(EMAIL)}</a></p>' if EMAIL else '') + '</div></section>'
    schema = [ld_business(),
              {"@context": "https://schema.org", "@type": "WebSite", "@id": url("/#website"), "url": url("/"), "name": BRAND, "inLanguage": "fr-FR", "publisher": {"@id": url("/#business")}},
              ld_service("Rachat de véhicules dans le Morbihan", "/", {"@type": "AdministrativeArea", "name": "Morbihan"}),
              ld_faq(HOME_FAQ)]
    page(path, "Reprise Auto Express – Rachat voiture Vannes | Sans CT | HS | Morbihan",
         "Rachat de voiture, sans permis, camping-car, utilitaire et camion à Vannes et dans le Morbihan. Sans CT, même HS. Offre ferme, estimation gratuite.", schema, body, None, h)
    urls.append("/")

    # ---------- Pages véhicules
    for v in VEHICLES:
        path = f"/{v['slug']}/"
        crumbs = [("Accueil", "/"), (v["h1"], path)]
        body = form()
        body += tldr([f"Rachat de <b>{v['name']}</b> dans tout le Morbihan, par un professionnel, dans l'état.",
                      "Contrôle technique non exigé pour une vente à un professionnel.",
                      "Offre ferme et écrite après expertise, sans obligation d'achat.",
                      "Déplacement à domicile sous 24 h, paiement par virement ou en espèces (dans la limite légale).",
                      "Certificat et déclaration de cession préparés avec vous."])
        for t, p in v["sections"]:
            body += f'<section class="sec"><div class="wrap narrow"><h2>{E(t)}</h2><p>{E(p)}</p></div></section>'
        body += steps_html()
        body += faq_html(v["faq"], f"Questions sur le rachat de {E(v['name'])}")
        others = [x for x in VEHICLES if x["slug"] != v["slug"]]
        body += '<section class="sec alt"><div class="wrap"><h2>Autres véhicules rachetés</h2><div class="cards">' + "".join(vcard(x, "Voir le rachat →") for x in others[:4]) + "</div></div></section>"
        body += zone_links(TOP[:12], f"Rachat de {E(v['name'])} près de chez vous")
        schema = [ld_business(), ld_service(v["h1"], path, {"@type": "AdministrativeArea", "name": "Morbihan"}), ld_faq(v["faq"]), ld_breadcrumb(crumbs)]
        page(path, v["title"], v["desc"], schema, body, crumbs, hero(v["h1"], v["lead"], "Reprise Auto Express · Morbihan (56)", True))
        urls.append(path)

    # ---------- Vannes (page principale locale)
    path = "/reprise-voiture-vannes/"
    crumbs = [("Accueil", "/"), ("Reprise voiture Vannes", path)]
    vfaq = [
     ("Où faire racheter sa voiture à Vannes ?", "Chez Reprise Auto Express, qui rachète les véhicules à Vannes (56000) et dans tout le Morbihan. Vous demandez une estimation en ligne, un conseiller se déplace à votre domicile dans les 24 h, expertise le véhicule et vous remet une offre ferme."),
     ("Peut-on vendre sa voiture à Vannes sans contrôle technique ?", "Oui, pour une vente à un professionnel le contrôle technique n'est pas demandé. Le contrôle de moins de 6 mois n'est exigé que pour la vente à un particulier."),
     ("Rachetez-vous les voitures HS ou accidentées à Vannes ?", "Oui, au cas par cas. Le coût des réparations est déduit de la valeur du véhicule, et l'enlèvement peut être étudié autour de Vannes."),
     ("Quels véhicules rachetez-vous à Vannes ?", "Voitures, voitures sans permis, camping-cars, utilitaires et camions, pour les particuliers et les professionnels du Vannetais."),
     ("Quelles communes autour de Vannes sont couvertes ?", "Séné, Saint-Avé, Arradon, Plescop, Theix-Noyalo, Elven, Sarzeau, Grand-Champ, Ploeren, Monterblanc, Meucon, Saint-Nolff, Sulniac et toutes les communes du Morbihan."),
     ("Dois-je acheter un autre véhicule pour vendre le mien ?", "Non. Le rachat est sans obligation d'achat."),
     ("Comment suis-je payé à Vannes ?", "Par virement bancaire ou en espèces, selon votre choix. Le paiement en espèces est plafonné par la loi (1 000 € pour une transaction avec un professionnel) ; au-delà, le règlement se fait par virement."),
     ("Quels documents faut-il pour vendre à Vannes ?", "Carte grise, pièce d'identité, clés, carnet d'entretien si disponible. Le certificat de cession est établi avec vous."),
     ("Comment est fixé le prix de reprise à Vannes ?", "À partir de la cote du modèle, de l'état constaté, des réparations à prévoir et des véhicules comparables proposés dans la région. L'offre est ferme après expertise."),
    ]
    body = form("Vannes (56000)")
    body += tldr(["<b>Rachat de voiture à Vannes (56000)</b> et dans tout le Morbihan, par Reprise Auto Express.",
                  "Sans contrôle technique, même HS, accidentée ou en panne.",
                  "Offre ferme après expertise, sans obligation d'achat.",
                  "Voiture, voiture sans permis, camping-car, utilitaire et camion."])
    body += """<section class="sec"><div class="wrap narrow"><h2>Faire reprendre sa voiture à Vannes sans tracas</h2>
<p>Vous ne voulez pas perdre de temps à vendre votre voiture ? Reprise Auto Express propose la <b>reprise de votre véhicule à Vannes</b> : une solution rapide, sans obligation d'achat, qui évite les annonces, les visites et les négociations entre particuliers.</p>
<p>Votre véhicule est repris dans l'état. Vous n'avez pas besoin de le passer au contrôle technique ni de le réparer. Le prix est calculé à partir de la cote de votre modèle, de ses options, de son état et du marché local.</p></div></section>"""
    body += steps_html()
    body += """<section class="sec alt"><div class="wrap narrow"><h2>Pourquoi choisir la reprise à Vannes ?</h2>
<p>Une vente entre particuliers demande du temps et expose à des risques : visites, négociations, chèque ou virement douteux, contrôle technique à fournir. Avec un rachat professionnel, vous vendez en une seule démarche, avec une offre écrite et ferme.</p>
<h3>Aucune réparation à prévoir en amont</h3><p>Votre véhicule est repris dans l'état. Si des réparations sont nécessaires, elles sont chiffrées et déduites de la valeur du véhicule.</p>
<h3>Le contrôle technique n'est pas obligatoire</h3><p>L'obligation d'un contrôle de moins de 6 mois concerne la vente à un particulier. Pour une reprise par un professionnel, le contrôle n'est pas demandé.</p>
<h3>Les démarches administratives sont prises en charge</h3><p>Nous vérifions la situation administrative, préparons le certificat de cession et déclarons la cession. Vous n'avez plus qu'à signer et à informer votre assureur.</p></div></section>"""
    body += """<section class="sec"><div class="wrap narrow"><h2>Comment est déterminé le prix de reprise à Vannes ?</h2>
<p>Le point de départ est la valeur de marché de votre modèle. S'y ajoutent les options et particularités, puis l'état constaté à l'expertise. Si des réparations sont nécessaires, leur coût est déduit. Nous tenons aussi compte des véhicules similaires proposés à la vente dans la région. Une fois l'offre acceptée, nous finalisons les documents de cession.</p></div></section>"""
    body += compare_table()
    body += vehicles_grid()
    body += zone_links(NEAR_VANNES, "Rachat de voiture autour de Vannes")
    body += faq_html(vfaq, "Reprise de voiture à Vannes : vos questions")
    schema = [ld_business(), ld_service("Reprise de voiture à Vannes", path, {"@type": "City", "name": "Vannes"}), ld_faq(vfaq), ld_breadcrumb(crumbs)]
    page(path, "Reprise voiture Vannes (56000) – Rachat cash, sans CT, HS | Reprise Auto Express",
         "Reprise de voiture à Vannes : rachat cash, sans contrôle technique, même HS ou accidentée. Offre ferme après expertise, sans obligation d'achat.",
         schema, body, crumbs, hero("Reprise de votre voiture à Vannes", "Voiture, utilitaire, camping-car, camion : Reprise Auto Express rachète votre véhicule à Vannes, dans l'état, sans contrôle technique et sans obligation d'achat.", "Vannes (56000) · Morbihan"))
    urls.append(path)

    # ---------- Pages communes
    intro = [
     "Vous habitez {prep} ({cp}) et vous souhaitez vendre votre véhicule sans passer par les annonces ? Reprise Auto Express rachète les voitures, voitures sans permis, camping-cars, utilitaires et camions {prep}, dans l'état.",
     "Faire racheter son véhicule {prep} ({cp}), c'est éviter les visites, les négociations et le contrôle technique à fournir. Reprise Auto Express vous remet une offre ferme après expertise, sans obligation d'achat.",
     "{name} ({cp}) fait partie du Morbihan (56), département entièrement couvert par Reprise Auto Express. Voiture en panne, utilitaire fatigué ou camping-car inutilisé : le rachat se fait dans l'état.",
    ]
    for c in communes:
        if c["slug"] == "vannes":
            continue
        nm, cp = c["name"], c["cp"]
        path = f"/reprise-voiture-{c['slug']}/"
        crumbs = [("Accueil", "/"), ("Zones d'intervention", "/zone-intervention-morbihan/"), (f"Reprise voiture {nm}", path)]
        same = [x for x in BY_CP[cp] if x["slug"] != c["slug"]]
        faq = [
         (f"Peut-on vendre sa voiture sans contrôle technique {prep(nm)} ?", f"Oui. Pour une vente à un professionnel comme Reprise Auto Express, le contrôle technique n'est pas demandé : votre voiture est reprise dans l'état {prep(nm)} ({cp}) comme ailleurs dans le Morbihan."),
         (f"Rachetez-vous les véhicules HS ou accidentés {prep(nm)} ?", f"Oui, au cas par cas. Le coût des réparations est déduit de la valeur du véhicule. Indiquez {nm} ({cp}) dans votre demande pour étudier l'enlèvement si le véhicule ne roule plus."),
         (f"Quels véhicules rachetez-vous {prep(nm)} ?", f"Voitures, voitures sans permis, camping-cars, utilitaires et camions, pour les particuliers et les professionnels {prep(nm)} et dans les communes voisines."),
         (f"Dois-je acheter un autre véhicule pour vendre le mien {prep(nm)} ?", "Non. Le rachat est indépendant de tout achat : vous vendez sans obligation."),
         (f"Vous déplacez-vous à domicile {prep(nm)} ?", f"Oui. Un conseiller se déplace chez vous {prep(nm)} ({cp}) dans les 24 h suivant votre demande, examine le véhicule et vous remet une offre ferme."),
         (f"Comment suis-je payé {prep(nm)} : espèces ou virement ?", "Au choix : virement bancaire ou espèces. Le paiement en espèces est plafonné par la loi (1 000 € pour une transaction avec un professionnel) ; au-delà, le règlement se fait par virement."),
        ]
        e = ENRICH.get(c["slug"])
        if e: faq.append(e["faq"])
        body = form(f"{nm} ({cp})")
        body += tldr([f"Rachat de véhicules {prep(nm)} ({cp}), Morbihan (56).",
                      "Sans contrôle technique, même HS ou en panne.",
                      "Offre ferme après expertise, sans obligation d'achat.",
                      "Cession et démarches préparées avec vous."])
        i = hv(c["slug"], 3)
        body += f'<section class="sec"><div class="wrap narrow"><h2>Reprise de véhicule {prep(nm)} ({cp})</h2><p>{intro[i].format(prep=prep(nm), name=nm, cp=cp)}</p>'
        body += f'<p>Un conseiller se déplace chez vous {prep(nm)} dans les 24 h suivant votre demande. Le prix est calculé à partir de la valeur de marché de votre modèle, de son état et des réparations éventuelles. Vous recevez une offre écrite : si vous acceptez, nous préparons le certificat de cession, déclarons la cession à votre place et vous réglons par virement ou en espèces (dans la limite légale).</p>'
        if same:
            body += f'<p>Le code postal {cp} regroupe aussi : ' + ", ".join(f'<a href="/reprise-voiture-{x["slug"]}/">{E(x["name"])}</a>' for x in same) + ".</p>"
        body += "</div></section>"
        if e: body += enriched_html(c, e)
        body += steps_html()
        cards = "".join(vcard(v, "Voir le rachat →") for v in VEHICLES[:5])
        body += f'<section class="sec alt"><div class="wrap"><h2>Véhicules rachetés {prep(nm)}</h2><div class="cards">{cards}</div></div></section>'
        body += faq_html(faq, f"Reprise de voiture {prep(nm)} : questions fréquentes")
        pool = [x for x in communes if x["slug"] not in (c["slug"],)]
        k = hv(c["slug"], len(pool))
        near = [pool[(k + j * 37) % len(pool)]["name"] for j in range(10)]
        near = ["Vannes"] + [n for n in near if n != nm][:9]
        body += zone_links(near, "Autres communes couvertes dans le Morbihan")
        schema = [ld_business(), ld_service(f"Reprise de véhicule {prep(nm)}", path, {"@type": "City", "name": nm}), ld_faq(faq), ld_breadcrumb(crumbs)]
        title = f"Reprise voiture {nm} ({cp}) – Rachat sans CT, HS | Reprise Auto Express"
        page(path, title, f"Reprise de voiture {prep(nm)} ({cp}) : rachat cash, sans contrôle technique, même HS. Voiture, utilitaire, camping-car, camion. Offre ferme, sans obligation d'achat.",
             schema, body, crumbs, hero(f"Reprise de voiture {prep(nm)} ({cp})", f"Rachat de votre véhicule {prep(nm)} et dans le Morbihan, dans l'état, sans contrôle technique et sans obligation d'achat.", f"{nm} · {cp} · Morbihan (56)", False))
        urls.append(path)

    # ---------- Pages code postal (multi-communes)
    for cp in CPS:
        group = BY_CP[cp]
        if len(group) < 2:
            continue
        path = f"/reprise-voiture-{cp}/"
        crumbs = [("Accueil", "/"), ("Zones d'intervention", "/zone-intervention-morbihan/"), (f"Code postal {cp}", path)]
        names = [g["name"] for g in group]
        faq = [(f"Reprenez-vous les véhicules dans le code postal {cp} ?", f"Oui. Le code postal {cp} (Morbihan) regroupe {', '.join(names)} : toutes ces communes sont couvertes par Reprise Auto Express."),
               ("Faut-il un contrôle technique pour vendre à un professionnel ?", "Non, le contrôle technique n'est pas demandé pour la reprise par un professionnel. Votre véhicule est repris dans l'état."),
               ("Reprenez-vous les véhicules HS ?", "Oui, au cas par cas, avec une offre qui déduit le coût des réparations.")]
        body = form(f"{names[0]} ({cp})")
        lis = "".join(f'<li><a href="/reprise-voiture-{g["slug"]}/">Reprise voiture {E(g["name"])}</a></li>' for g in group)
        body += f'<section class="sec"><div class="wrap narrow"><h2>Communes du code postal {cp}</h2><p>Le code postal <b>{cp}</b> couvre {len(group)} communes du Morbihan. Pour chacune, Reprise Auto Express rachète voitures, voitures sans permis, camping-cars, utilitaires et camions, dans l\'état.</p><ul class="chips">{lis}</ul></div></section>'
        body += steps_html() + faq_html(faq)
        schema = [ld_business(), ld_service(f"Rachat de véhicules code postal {cp}", path, [{"@type": "City", "name": n} for n in names]), ld_faq(faq), ld_breadcrumb(crumbs)]
        page(path, f"Reprise voiture {cp} Morbihan – {', '.join(names[:3])} | Reprise Auto Express",
             f"Reprise de voiture dans le {cp} ({', '.join(names[:4])}). Rachat sans CT, même HS, offre ferme après expertise.",
             schema, body, crumbs, hero(f"Reprise de voiture dans le {cp} ({', '.join(names[:2])}…)" if len(names) > 2 else f"Reprise de voiture dans le {cp} ({' et '.join(names)})", f"Rachat de véhicules dans toutes les communes du code postal {cp}, dans l'état et sans contrôle technique.", f"Code postal {cp} · Morbihan (56)", False))
        urls.append(path)

    # ---------- Zone d'intervention : tous les codes postaux
    path = "/zone-intervention-morbihan/"
    crumbs = [("Accueil", "/"), ("Zones d'intervention", path)]
    rows = ""
    for cp in CPS:
        g = BY_CP[cp]
        cell = ", ".join(f'<a href="/reprise-voiture-{x["slug"]}/">{E(x["name"])}</a>' for x in g)
        link = f'<a href="/reprise-voiture-{cp}/">{cp}</a>' if len(g) > 1 else cp
        rows += f"<tr><th>{link}</th><td>{cell}</td></tr>"
    body = form()
    body += f'<section class="sec"><div class="wrap"><h2>Les {len(CPS)} codes postaux du Morbihan et leurs communes</h2><p>Reprise Auto Express rachète votre véhicule dans les {len(communes)} communes listées ci-dessous, soit tous les codes postaux du département du Morbihan (56).</p><div class="tw"><table class="zt"><thead><tr><th>Code postal</th><th>Communes</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>'
    schema = [ld_business(), ld_service("Rachat de véhicules dans tout le Morbihan", path, {"@type": "AdministrativeArea", "name": "Morbihan"}), ld_breadcrumb(crumbs)]
    page(path, "Codes postaux du Morbihan – Zones de rachat de voiture | Reprise Auto Express",
         f"Liste des {len(CPS)} codes postaux et {len(communes)} communes du Morbihan (56) où Reprise Auto Express rachète voitures, utilitaires, camping-cars et camions.",
         schema, body, crumbs, hero("Rachat de véhicules dans tout le Morbihan (56)", "Tous les codes postaux et toutes les communes du département sont couverts.", "Zone d'intervention", False))
    urls.append(path)

    # ---------- Mentions légales
    path = "/mentions-legales/"
    body = """<section class="sec"><div class="wrap narrow"><h1>Mentions légales</h1>
<p><b>Éditeur du site :</b> [raison sociale] – [forme juridique] – SIRET [numéro] – [adresse].</p>
<p><b>Directeur de la publication :</b> [nom].</p><p><b>Contact :</b> """ + (EMAIL or "[e-mail]") + """ – [téléphone].</p>
<p><b>Hébergement :</b> Cloudflare, Inc., 101 Townsend St, San Francisco, CA 94107, États-Unis.</p>
<p><b>Données personnelles :</b> les informations saisies dans le formulaire d'estimation servent uniquement à étudier votre demande et à vous recontacter. Ces informations sont transmises par e-mail via le service FormSubmit. Vous pouvez exercer vos droits d'accès, de rectification et de suppression en écrivant à l'adresse ci-dessus.</p></div></section>"""
    page(path, "Mentions légales – Reprise Auto Express", "Mentions légales du site Reprise Auto Express.", [ld_breadcrumb([("Accueil", "/"), ("Mentions légales", path)])], body, None)

    # ---------- 404
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(head("Page introuvable – Reprise Auto Express", "Page introuvable", "/404.html", [], True) + header() +
                '<section class="sec"><div class="wrap narrow"><h1>Page introuvable</h1><p><a href="/">Retour à l\'accueil</a> ou <a href="/zone-intervention-morbihan/">voir les zones d\'intervention</a>.</p></div></section>' + footer())

    # ---------- sitemap / robots / llms / headers
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        pr = "1.0" if u == "/" else ("0.9" if (u.startswith("/rachat-") or u == "/reprise-voiture-vannes/") else "0.6")
        sm += f"<url><loc>{url(u)}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>\n"
    sm += "</urlset>\n"
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(sm)

    if PREPROD:
        robots = "User-agent: *\nDisallow: /\n"
    else:
        bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bingbot", "Googlebot"]
        robots = "User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"Sitemap: {url('/sitemap.xml')}\n"
    open(os.path.join(OUT, "robots.txt"), "w").write(robots)

    llms = f"""# {BRAND}

> Reprise Auto Express rachète les véhicules d'occasion (voiture, voiture sans permis, camping-car, utilitaire, camion) à Vannes et dans tout le Morbihan (56), sans contrôle technique, même HS, avec offre ferme après expertise et sans obligation d'achat.

## Faits clés
- Zone : département du Morbihan (56), {len(CPS)} codes postaux, {len(communes)} communes, siège de service à Vannes (56000).
- Véhicules : voiture, voiture sans permis, camping-car, utilitaire, camion.
- Sans contrôle technique : le CT de moins de 6 mois n'est obligatoire que pour une vente à un particulier.
- Véhicules HS, en panne ou accidentés : étudiés au cas par cas, coût des réparations déduit.
- Offre ferme et écrite après expertise, sans obligation d'achat.
- Déplacement à domicile d'un conseiller dans les 24 h suivant la demande.
- Paiement par virement ou en espèces (plafond légal de 1 000 € en espèces pour une transaction avec un professionnel).
- Cession : certificat et déclaration de cession préparés avec le vendeur.

## Pages principales
""" + "".join(f"- [{v['h1']}]({url('/'+v['slug']+'/')}): {v['desc']}\n" for v in VEHICLES) + f"""- [Reprise voiture Vannes]({url('/reprise-voiture-vannes/')})
- [Tous les codes postaux du Morbihan]({url('/zone-intervention-morbihan/')})
"""
    open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8").write(llms)
    open(os.path.join(OUT, "_headers"), "w").write("/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n")
    print(len(urls), "pages", "PREPROD" if PREPROD else "PROD")

build()
