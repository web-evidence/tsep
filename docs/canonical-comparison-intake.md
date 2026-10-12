# TS12 supplied intake / Import fourni

## Français

Le [contrat](canonical-comparison.md) définit le profil et ses limites. Ce parcours
hors ligne ne contacte ni Google ni le site, n’exécute aucun navigateur et ne
fabrique pas de revue. Node 24 explicite est nécessaire à la lecture HTML.

1. Avant acquisition, conserver un plan cible sans documents, inspection_records,
   inspection_reviews ou comparison_reviews. Déclarer inspection + canonical_comparison,
   contexte/client, préférences sourcées, scénarios et limites, puis fournir la
   revue préalable liée à {url,intent}. Une connaissance antérieure reste déclarée.
2. Acquérir réellement les requêtes/réponses API selon [TS08](search-console-acquisition.md).
   Chaque dossier contient request.json, response.json et manifest.json daté, avec
   empreintes et provenance réelles. Aucun secret n’est requis dans le dossier.
   Fournir séparément la liste documents en JSON : traces HTTP et états DOM structurés
   de même navigation. Les outils n’inventent aucune pièce manquante.
3. Importer les fichiers exacts, puis lire input.json et review-request.json.
   Ce dernier laisse auteur, dates, revendications, explication et décision vides.
   Fournir une revue distincte, liée aux octets et au plan. Garder toute tentative.
4. Construire un nouveau paquet, lire synthèse/atomes/observations/preuves puis
   exporter et rejouer avec les outils exacts. Une revue vide donne NT. Les erreurs
   API, limites et différences restent consultables ; C qualifie le dossier.

```sh
TSEP_SOURCE_NODE=/path/to/node24 python3 adapters/comparison_intake.py prepare plan.json \
  --inspection native-url-1 --documents supplied-documents.json --output prepared-new
TSEP_SOURCE_NODE=/path/to/node24 python3 adapters/comparison_intake.py build prepared-new \
  --reviews supplied-reviews.json --output bundle-new --assessor 'Actual assessor'
TSEP_SOURCE_NODE=/path/to/node24 python3 tsep.py html bundle-new/report.json --lang fr --output report-fr.html
TSEP_SOURCE_NODE=/path/to/node24 python3 adapters/replay.py bundle-new --output replay-new
```

Les commandes HTML/rejeu exposent aussi --help. Le plan, les fichiers natifs et leur
empreinte sont conservés ; aucune destination existante n’est remplacée. L’import
est daté au moment réel du calcul, distinct des acquisitions. Changer les outils
exige une réévaluation distincte. Une ancienne preuve ne devient pas prospective.
Données de compte : restricted ; revues/exemples rédigés : synthetic.

Exemples livrés : examples/captures/ts12-agreement.json, ts12-divergence.json,
ts12-contradiction.json, ts12-source-only.json. Tous sont des exercices rédigés,
DOM compris ; aucune navigation navigateur ou approbation humaine réelle.

## English

The [contract](canonical-comparison.md) defines the bounded profile. This offline
workflow contacts neither Google nor the site, executes no browser and creates no
review. Explicit Node24 is needed for HTML reading. Before acquisition, retain a
target plan without documents/inspection_records/inspection_reviews/comparison_reviews,
with inspection and canonical_comparison intent, context/client, sourced preferences,
scenarios/thresholds and supplied prior review bound to {url,intent}. Disclose prior
knowledge. Acquire genuine native API request/response/manifests through the TS08
procedure and separately supply the exact JSON document list, with HTTP and structured
same-navigation DOM. No missing evidence is invented; no credentials belong in it.

Use the commands above to prepare a new intake, inspect input and blank review request,
then supply a separate genuine review and build a new bundle. Empty reviews remain NT.
Read summary/atoms/observations/evidence and replay with exact tools. Preserve attempts,
original files and hashes; existing destinations are never overwritten. Import time
is actual computation time, separate from acquisition. Changed tools require separate
reassessment; old evidence never becomes prospective. Real account data is restricted;
authored examples/reviews are synthetic. The four supplied examples include authored
DOM and establish no real browser navigation or human approval. C is documentation,
not canonical correctness, Google agreement, TS10 conformity or indexing.
