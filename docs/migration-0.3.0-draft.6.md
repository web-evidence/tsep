# Lot 1 — 0.3.0-draft.6 (candidate / candidat)

## Français

Version distincte, non publiée. TS01 et TS02 passent à la version de règle
0.3.0-draft.6 ; les 42 autres versions restent inchangées. 44 contrôles et 98
règles sont conservés. Aucun succès de qualification n'est déduit de ce document.

TS01 : le lecteur parsé exclut, avec leurs octets et positions originaux, les
espaces ASCII directement sous html. Il découpe aussi les nœuds fusionnés directement sous body aux fermetures
body/html et aux commentaires explicitement reconnus. Chaque morceau conserve
son intervalle original ; les morceaux de texte sont comparés séparément et
ne sont jamais joints pour trouver un marqueur. La reconstruction de tout le
texte après normalisation CRLF/CR et références doit égaler le nœud parsé.
Les fermetures, commentaires et morceaux uniquement blancs ASCII sont exclus. Aucun NBSP, texte non blanc, marqueur ou octet du corps n'est supprimé ou
modifié. Les 52 cas historiques restent inchangés. Erreurs parse5, contextes
étrangers non blancs, frames et ambiguïtés restent indéterminés.

TS02 : le collecteur 2 inscrit `redirect_reader: http-trajectory-headers-v1`
dans l'intention **avant** validation. Ce profil peut utiliser les en-têtes
complets d'un préfixe arrêté exactement à la limite d'octets déclarée par le
collecteur. La limite doit égaler la borne par réponse du plan (au plus 1 Mio) ; un arrêt
sur budget de phase réduit porte une raison distincte et reste inconclusif.
La trace doit garder `complete: false`, la limite réelle, le nombre
d'octets conservés et la lecture d'un octet excédentaire. Ces métadonnées restent
déclaratives et ne prouvent pas l'authenticité du serveur. Sans cette attribution,
un arrêt, timeout ou corps incomplet reste inconclusif. Les requêtes restent
attribuées au GET, Host et client déclarés, sans authentification.

Les en-têtes répétés/ambigus, TE+CL, longueurs contradictoires, préfixes chunked
mal formés, Location ambiguë et Refresh restent refusés. Un corps partiel gzip
n'est pas décodé ni déclaré valide. Seule la trajectoire serveur est examinée ;
aucun résultat de contenu, disponibilité complète, rendu ou indexation n'en suit.
Les autres règles continuent d'exiger leurs preuves complètes. L'approbation
responsable A01 reste nécessaire à C pour TS02 ; aucune revue n'est fabriquée.

Les anciens profils sans ce champ gardent la lecture stricte du corps. Rejouer
les dossiers historiques exige leur archive et leur runtime exacts. Ne jamais
réécrire les captures, intentions, références, diagnostics ou manifestes anciens.
Pour adopter les changements, créer un nouveau dossier et une nouvelle intention.

Qualification : Node24 est résolu une fois depuis TSEP_SOURCE_NODE ou PATH,
vérifié puis transmis explicitement à tous les sous-processus. Une valeur
explicite invalide ne déclenche aucun repli. Chemin, version et SHA-256 sont
consignés dans le reçu local. Le plafond par étape est 7200 secondes, fini et
configurable. Un timeout est un échec. `--quick` exécute seulement les régressions
ciblées et ne qualifie pas une distribution ; la commande sans option conserve
toutes les suites, exemples, archives reconstruites et gardes d'immuabilité.

## English

Distinct unpublished candidate. Only TS01/TS02 rule versions become draft.6;
the other 42 rule versions and all 44 controls/98 rules remain. This document
does not claim successful qualification.

The parsed TS01 reader excludes attributable ASCII whitespace directly under
html and exactly reconstructible merged body-tail text. The latter is split at explicit
body/html end tags and comments, retaining each original interval; text pieces
are compared separately, never joined across markup. Reconstructing all parsed
text pieces must equal the original parsed node. Only markup/comments and
ASCII-whitespace-only pieces are excluded. Original intervals/raw bytes remain in exclusions. NBSP, nonblank
text, criteria and body bytes are never removed or normalized. The 52 historical
fixtures remain untouched. Reported parse5 errors, foreign nonblank text, frames
and ambiguous spans remain inconclusive.

Collector 2 declares `redirect_reader: http-trajectory-headers-v1` before owner
approval. Complete HTTP headers may establish the server trajectory when a
retained prefix stops exactly at the collector's byte limit, with complete=false,
actual limit, retained byte count and one observed overflow byte (attested by
the worker, not retained). The limit must equal the declared per-response cap
(up to 1MiB); a smaller remaining phase budget stays inconclusive. Metadata is
not authenticated server evidence. Missing attribution, EOF errors or timeouts
stay inconclusive. GET/Host/client attribution and anonymous-request constraints
remain. Ambiguous headers, TE+CL, contradictory lengths, malformed chunk prefixes,
ambiguous Location and Refresh remain unsupported. Partial gzip bodies are not
decoded or claimed valid. Body-dependent rules are unchanged; A01 approval is
still required for whole TS02 C. No human review is supplied by this change.

Intents without the new profile retain strict complete-body interpretation.
Historical dossiers must use their exact original archive/runtime; never rewrite
their evidence. Adoption requires a new dossier and pre-capture intent.

Qualification resolves and verifies Node24 from the explicit setting or PATH,
propagates that exact executable and records its path/version/digest. Invalid
explicit settings never fall back. The finite step limit becomes 7200 seconds;
timeouts fail. `--quick` checks targeted regressions only. The default verifier
retains full suites, examples, archive reconstruction and source immutability.
