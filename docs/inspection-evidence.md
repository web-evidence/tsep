# TS08 — Inspection evidence / Preuves d’inspection, profil 1

## Français

`google-inspection-evidence-v1` évalue le dossier de l’ensemble d’URL explicitement
sélectionné. Trois règles semiAuto : A01 périmètre/objectifs et revue préalables ;
A02 inspections natives attribuées, datées et lisibles ; A03 interprétation et
décision effectivement fournies. C signifie documentation qualifiée de cet ensemble,
jamais « indexé », réussite SEO, représentativité statistique ou état actuel du site.
L’ancien diagnostic 1 reste une comparaison sans verdict. TS12 reste distinct.

### Plan et pièces

La cible captures contient url (ancre du périmètre, membre de la sélection),
observed_at (évaluation), context (network/bounds/tool/tool_version),
inspection_synthetic booléen et intent.declared_at. intent.inspection contient
reader, site_url, selection_method, population, prior_knowledge et 1–16 members
uniques {url, objective, objective_source, selection_reason}. L’objectif et sa source
sont déclarés ; leur sincérité n’est pas authentifiée. Une connaissance antérieure
est admise et affichée, jamais transformée en découverte prospective. Décrire la
liste et son origine concrète ; un mot « représentatif » ne prouve aucune couverture.
max_retrieval_age_hours (1–8760) et max_crawl_age_hours (1–8760) fixent des seuils
locaux préalables, pas des délais Google. Le premier seuil compare acquisition et
évaluation, le second dernier crawl et acquisition. Ils ne datent pas chaque champ.

inspection_plan_review lie SHA-256(JSON compact trié UTF-8 de {url,intent}), après
le plan et avant chaque acquisition. Les jugements selection/objectives sont
supported, contradiction ou unknown. Sans revue, A01 reste inconclusive ; une
contradiction fournie ou une acquisition explicitement antérieure au plan donne
fail. Une pièce absente ne prouve pas une mauvaise sélection. Les dates restent
fournies, sans preuve cryptographique de l’ordre historique.

inspection_records contient exactement un record par membre : url, retrieved_at,
provenance (supplied-google-api ou synthetic-exercise), description, http_status,
request et response. Chaque corps {raw_text,sha256} conserve le JSON UTF-8 natif
et l’empreinte de ces octets, ≤512 Kio par corps ; cible totale ≤4 Mio. Le profil
ne convertit ni CSV, ni écran, ni test live. L’attribution de la requête/réponse
reste déclarée : l’API ne fournit pas une identité autonome de requête dans sa
réponse. Propriété et URL sont vérifiées par le lecteur borné du diagnostic 1.
Une URL inspectée différente de celle à laquelle le record est attribué donne
fail A02 ; propriété invalide, empreinte fausse, réponse inexploitable ou erreur
API donnent inconclusive. Aucune erreur API ne devient un état Google négatif.

### Champs et qualification

A02 conserve toutes les lectures du diagnostic 1 et leurs états. Ce premier
profil exige verdict, robotsTxtState, indexingState, pageFetchState et crawledAs
présents, connus et non réservés. coverageState est conservé sans classifier son
texte traduit. Google/userCanonical valides sont comparées littéralement dans
l’observation, sans verdict TS12. userCanonical absente est admise comme absence
du champ API, sans inférence HTML/DOM. googleCanonical absente est admise seulement
pour FAIL/NEUTRAL. lastCrawlTime absent est admis seulement pour FAIL/NEUTRAL et
pageFetchState différent de SUCCESSFUL. Autres absences, valeurs vides, invalides,
réservées, crawl futur ou ancien hors politique restent inconclusifs. Une réponse
« URL inconnue » privée des champs requis reste donc NT dans ce profil strict ;
son texte n’est pas analysé pour reconstituer les valeurs absentes. Aucun NA atomique.

inspection_reviews comporte une revue par URL, liée à {url,intent,record} exact.
Toutes les revues ont reviewer, assistance, provenance (human, human-assisted ou
synthetic-exercise), reason, complete:true, observed_at et binding_sha256. La revue
A03 se situe après acquisition et avant évaluation. Aucun auteur n’est authentifié.
claimed_verdict doit égaler le verdict API connu : divergence explicite = fail.
interpretation supported/contradiction/unknown qualifie le sens de la lecture.
objective_relation aligned/different/undetermined reste une appréciation fournie,
jamais une comparaison automatique de l’indexation. Une relation indéterminée ne
réussit pas A03. temporal_scope doit être reported-index-version ; une affirmation
current-live-page constitue une contradiction de portée. L’API n’est pas live.

explanation contient kind et text : observation, hypothesis (avec test observable)
ou unresolved (cause non établie). established-cause est hors du premier profil,
reste inconclusive et demande des preuves et une méthode distinctes : pas de cause
inventée. decision contient kind, reason, owner : accept, correct, monitor ou
revise-objective. monitor exige criterion et due_at après revue ; correct exige
action ; revise-objective exige new_plan_reference. Ce sont des décisions fournies,
aucune action ni modification du plan n’est exécutée. Un nouvel objectif demande
un nouveau plan ; les anciennes pièces restent intactes.

Chaque facette est conservée : un fail attribuable survit aux inconnues des autres
facettes ; sinon toute lacune donne inconclusive. Une seule URL omise interdit C.
Une revue contradictoire peut établir NC malgré un crawl trop ancien ; elle ne
prouve aucun défaut actuel du site. L’absence d’une revue ne donne jamais NC à
elle seule. Les champs absents légitimes restent visibles même lorsqu’A02 passe.
Données de compte : accès restricted. Exercices et revues rédigées : synthetic.
FR/EN et rejeu conservent octets, limites, sélection et connaissances antérieures.

## English

`google-inspection-evidence-v1` assesses the explicit selected URL set: A01 prior
scope/objectives and supplied plan review; A02 attributed, dated native inspections;
A03 supplied interpretation and decision. All are semiAuto. C means qualified
documentation of that set, never indexing, SEO success, statistical representation
or current site state. Diagnostic1 remains comparison-only; TS12 is separate.

A captures target retains scope-anchor url (a member), assessment observed_at,
context network/bounds/tool/tool_version, inspection_synthetic boolean, and
intent.declared_at. intent.inspection contains reader, site_url, selection_method,
population, prior_knowledge and1–16 unique members with url/objective/objective_source/
selection_reason. Disclose existing knowledge; do not invent prospective discovery.
Objectives and their sources are supplied, not authenticated. Describe the concrete
list and its basis; “representative” alone establishes nothing. Prior integer
max_retrieval_age_hours and max_crawl_age_hours (each1–8760) compare retrieval to
assessment and crawl to retrieval. These are local policies, not Google deadlines
or timestamps for every returned field.

inspection_plan_review binds sorted compact UTF-8 JSON {url,intent}; its date is
between plan and every acquisition. selection/objectives judgments are supported,
contradiction or unknown. Missing review is inconclusive; supplied contradiction
or acquisition explicitly before the plan fails. Supplied dates/hashes do not
authenticate historical ordering or honest selection.

inspection_records has exactly one record per member: url/retrieved_at/provenance
(supplied-google-api|synthetic-exercise)/description/http_status/request/response.
Bodies retain raw_text and its UTF-8 SHA-256, ≤512KiB each; total target≤4MiB.
No CSV/screenshot/live-test conversion. Diagnostic1's bounded URL/property reader
checks lexical scope, not account access or authentic request/response linkage.
An inspected URL different from its record attribution fails A02; invalid property,
changed hashes, unusable response or API error are inconclusive, never non-indexing.

A02 preserves all diagnostic1 field readings. verdict, robotsTxtState, indexingState,
pageFetchState and crawledAs must be present/known/nonreserved. coverageState remains
unclassified descriptive text. Canonical values use literal comparison only, never
TS12 judgment. Absent userCanonical is allowed as an absent API field, not HTML/DOM
absence. Absent googleCanonical is allowed only for FAIL/NEUTRAL. Absent lastCrawlTime
is allowed only for FAIL/NEUTRAL with pageFetchState other than SUCCESSFUL. Other
missing/empty/invalid/reserved values, future crawl and old dates outside prior
policy are inconclusive. An “unknown URL” response lacking mandatory fields remains
NT in this strict profile; its localized label does not reconstruct missing fields.
No automatic atomic NA.

inspection_reviews has one review per member, binding exact {url,intent,record}.
Every review retains reviewer/assistance/provenance (human|human-assisted|
synthetic-exercise)/reason/complete:true/observed_at/binding_sha256. A03 review follows
acquisition and precedes assessment; identity is not authenticated. claimed_verdict
must equal the known API verdict; a mismatch fails. interpretation judgment is
supported/contradiction/unknown. objective_relation is supplied aligned/different/
undetermined; undetermined cannot pass. temporal_scope must be reported-index-version;
current-live-page is an explicit scope contradiction. Inspection is not live.

explanation has kind/text: observation, hypothesis (also an observable test), or
unresolved (cause unestablished). established-cause remains outside this first
profile and inconclusive pending separate evidence/method. decision has kind/reason/
owner: accept, correct (also action), monitor (also criterion and due_at after
review), or revise-objective (also new_plan_reference). These supplied decisions
execute no action or plan edit. Changed objectives need a new retained plan.

Retain each facet. Any attributable failure wins; otherwise any gap is inconclusive.
One omitted member prevents C. A contradictory review can establish NC despite an
old crawl without establishing a current site defect. Missing review alone never
fails. Legitimate absent fields remain visible even when A02 passes. Real account
data is restricted, authored evidence/reviews synthetic. Bilingual reports/replay
retain exact bodies, limits, selection and prior knowledge. No invented human review.
