# Observations Search Console / Search Console observations

## Français

Diagnostic **1**, sans changement du protocole draft.11. Cet outil rapproche une
réponse d'inspection d'URL fournie et un paquet de captures TSEP de la même URL.
Il ne se connecte pas au compte Google, ne collecte rien et ne produit pas de
verdict TS08/TS12. Ces contrôles demandent encore qualification et décision humaines.

### Entrée Google réellement conservée

La voie prise en charge est la réponse JSON de l'[API URL Inspection](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect).
Cet endpoint décrit la version indexée, pas un test de la page en direct. Conserver
le corps JSON original de la requête (`inspectionUrl`, `siteUrl`, éventuellement
`languageCode`) dans `request.json` et celui de la réponse dans `response.json`.
Les exports CSV de performances, les copies manuelles d'un écran et les tests en
direct de l'interface ne sont pas convertis implicitement en réponses de cette API.
Ne pas mettre d'identifiant OAuth, cookie ou en-tête d'authentification dans ces fichiers.

Ajouter `manifest.json` dans le même dossier :

```json
{
  "kind": "tsep-url-inspection-observation",
  "format_version": "1",
  "provenance": "supplied-google-api",
  "description": "Origine réelle et moyen de conservation à renseigner",
  "retrieved_at": "2026-10-10T12:00:00Z",
  "http_status": 200,
  "request_sha256": "REMPLACER_PAR_L_EMPREINTE_DES_OCTETS_ORIGINAUX",
  "response_sha256": "REMPLACER_PAR_L_EMPREINTE_DES_OCTETS_ORIGINAUX",
  "change": null
}
```

Cet extrait est un **gabarit**, pas une observation. Renseigner la date réelle de
récupération, le statut fourni et les empreintes des fichiers exacts, sans reformater
les originaux. `synthetic-exercise` identifie exclusivement les exemples rédigés.
Ne jamais présenter un exemple comme issu du compte d'Edikka.

La propriété doit contenir l'URL inspectée selon la portée déclarée : domaine et
sous-domaines pour `sc-domain:`, ou origine et préfixe de chemin exact pour une
propriété URL. Ce contrôle lexical ne prouve ni accès au compte, ni propriété,
ni correspondance authentifiée de la requête et de la réponse. La réponse ne
fournissant pas une identité de requête autonome, cette liaison reste déclarée.

Un changement réel peut être documenté séparément avec `change` contenant
`occurred_at`, `description` et `evidence_sha256`, plus `change-evidence.txt`.
Une date de plan n'est pas une preuve de déploiement. Sans pièce de changement,
laisser `change: null` : la comparaison crawl/changement restera indisponible.

### Comparer puis rejouer hors ligne

```sh
python3 diagnostics/search_console.py compare /chemin/inspection \
  --technical /chemin/paquet-captures --output /chemin/rapprochement-neuf
python3 diagnostics/search_console.py replay /chemin/rapprochement-neuf \
  --output /chemin/rejeu-neuf
```

Le paquet technique est d'abord rejoué avec ses outils exacts. Une version différente
requiert une réévaluation explicite séparée, jamais un remplacement des pièces.
L'URL d'inspection doit être une cible exacte ou un membre déclaré d'une famille
canonical ; une URL de destination n'est pas automatiquement assimilée à sa source.
Les résultats atomiques d'une famille restent ceux de la famille, pas un verdict
individuel pour chaque URL. Aucun mélange entre preuves réelles et synthétiques.

La sortie conserve les octets d'inspection, le paquet technique original, son rejeu,
comparison.json, deux rapports HTML FR/EN, les empreintes et les versions. Conserver
**tout le dossier**. Les réponses API en erreur restent visibles ; une erreur 403
ne devient pas une absence d'indexation. Une entrée JSON illisible ou une liaison
incorrecte est refusée avant livraison ; son fichier d'origine n'est pas modifié.

### Lire le résultat

L'[objet documenté par Google](https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult)
contient notamment les canonical rapportées, l'état d'indexation et le dernier
crawl. Le diagnostic conserve leurs valeurs originales. Il distingue valeur
présente, absente, vide, invalide, non spécifiée ou inconnue/réservée.

Les rapprochements `equal`, `different` et `unavailable` sont des comparaisons de
valeurs, **pas des pass/fail TSEP**. Les URL sont comparées littéralement : slash,
paramètres et encodages restent distincts. Les limitations du lecteur source/rendu
demeurent visibles. Une permission `INDEXING_ALLOWED` n'établit pas une indexation.
Un champ canonical absent n'autorise pas à inventer une URL ou une explication.
Le `verdict` API porte l'intitulé « Verdict rapporté par Google (API) », séparé
des résultats TSEP. `coverageState` reste un texte descriptif, sans logique fondée
sur son libellé. Le client HTTP, le navigateur fourni et `crawledAs` sont affichés
ensemble, sans prétendre qu'une catégorie mobile/desktop identifie un agent exact.

La chronologie distingue intention, capture source, récupération de l'inspection,
dernier crawl rapporté et changement documenté éventuel. Les fractions de seconde
jusqu'à neuf chiffres sont conservées pour les comparaisons. Un crawl postérieur à
la récupération est une incohérence, pas une observation fraîche. `lastCrawlTime`
ne date pas chaque champ retourné ; même un crawl ultérieur ne prouve pas que
Google a reçu le même contenu que notre client. Une différence n'est donc ni une
régression automatiquement établie, ni une cause démontrée, ni un gain SEO.
Un accord après le changement peut préexister à celui-ci ; un écart peut encore
refléter le délai de traitement. La prise en compte du changement n'est pas prouvée.

Bornes : Python 3.9+, bibliothèque standard, JSON 8 Mio par fichier, paquets selon
les limites communes (1 024 fichiers, 32 Mio par fichier, 128 Mio). URL HTTP(S)
ASCII sans identifiants ni fragment ; les formes non couvertes restent invalides
dans le diagnostic, avec réponse brute conservée. Aucun appel réseau. Les dates,
l'origine, l'acquisition et l'accès restent déclaratifs, pas authentifiés.

Les onze cas figés dans `tests/fixtures/search-console-v1-cases.json` précèdent
l'implémentation et sont synthétiques. Les tests supplémentaires couvrent propriété,
liaison URL, chronologie, erreurs API, changement documenté, intégrité et rejeu.
Ils ne prouvent pas l'usage avec un export réel ni une recette humaine.

## English

Diagnostic **1** is an offline bridge between a supplied URL Inspection API response
and an exact technical target or declared canonical-family member. It does not
access Google accounts, run live URL tests or issue TS08/TS12 outcomes. Protocol
draft.11, existing interpreters and previous results are unchanged.

Use original `request.json` and `response.json` bodies plus the manifest above,
with actual retrieval time, supplied HTTP status, provenance description and byte
hashes. Use `synthetic-exercise` only for authored examples. Do not include credentials
or authentication headers. Performance CSVs, screenshots and UI live tests are not
silently converted into this API format. Domain/URL-prefix checks are lexical,
not proof of account ownership or authentic request/response attribution.

Optional documented change requires occurred_at, description, evidence_sha256 and
the matching change-evidence.txt. A planning date is not deployment evidence.
Without a change record, crawl/change comparison is unavailable. Original request,
response, technical bundle and replay remain in the output; retain the whole folder.
Use the exact historical tool archive. Real and synthetic evidence cannot be mixed.

The commands above produce bilingual HTML and replayable JSON comparisons, never
TSEP pass/fail judgments. Missing, empty, malformed, unspecified and unknown/reserved
fields stay distinct. API errors are retained. Canonical values are literal strings;
indexing permission is distinct from indexing. Family findings remain family findings.
Source/render-reader limitations are retained alongside any extractable signals.
The Google API verdict is labeled separately from TSEP outcomes. coverageState is
retained as descriptive text, never a decision enum. Actual technical client and
supplied rendering browser appear beside Google's reported crawler category;
this does not establish equal representations or exact Google user-agent identity.

Intent, source capture, retrieval, reported crawl and actual change have separate
timestamps. Nanosecond ordering is preserved. Crawl after retrieval is inconsistent;
lastCrawlTime does not timestamp every returned field. Neither a later crawl nor a
canonical difference proves the same served representation, a regression, causality
or ranking impact. No authentic Google-origin/account-access claim is established.

Python 3.9+ standard library, no network, 8 MiB JSON, shared package bounds. Bounded
ASCII HTTP(S) URLs without credentials/fragments; unsupported response-field forms
remain unavailable and raw responses remain intact. Eleven prefrozen cases and
additional adverse workflow tests are synthetic, not evidence of real-account use.
