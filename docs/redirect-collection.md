# TS02 — prospective collection / collecte prospective

Collector contract **1**, prepared 2026-10-13 before implementation. This is a
non-normative application workflow for existing TS02-A01/A02, not a new rule.
Protocol draft.33, its 44 controls and 48 atomic rules remain unchanged.

## Français

Le parcours prépare le plan, importe une approbation réellement fournie, collecte
les trajectoires HTTP déclarées et remet les pièces au moteur existant. Il ne
modifie aucune redirection du site et ne renseigne aucune décision humaine.

`prepare` reçoit un plan TS02 sans revue et des paramètres de collecte. Il ajoute
au contexte, **avant approbation**, le nom/version du collecteur, ses empreintes
et les paramètres exacts. Il remplace les libellés techniques `tool`,
`tool_version` et `bounds` par ceux effectivement utilisés. Le réseau et les
attendus métier restent ceux fournis. La fiche existante expose le contexte
complet. Une préparation ne réalise aucune requête.

L'import de la réponse utilise `adapters/redirect_plan.py import-response`.
`collect` vérifie le paquet, le reçu, les réponses, les empreintes des outils et
l'approbation de **toutes** les cibles avant toute requête. Un refus ou une revue
absente bloque cette collecte ; les imports documentaires existants gardent leur
comportement, y compris les contradictions connues sans approbation.

Paramètres explicites : 1–10 cibles, 1–20 origines autorisées, User-Agent du plan,
`accept_encoding` (`identity` ou `gzip, deflate`), délai par saut 0,1–30 secondes,
réponse 1 Kio–1 Mio, 0–19 redirections de collecte, total des réponses 1 Kio–2 Mio,
durée supervisée 1–300 secondes, `allow_loopback` booléen. Les bornes de collecte
sont distinctes des attendus TS02 : atteindre une borne ne suffit pas à établir
une non-conformité. Le délai total inclut les sous-processus/DNS, avec le coût
ordinaire de supervision et d'écriture ; ce n'est pas une garantie temps réel.

Les URL sont HTTP(S), anonymes, ASCII et sans fragment. Chaque origine source et
attendue est explicitement autorisée. Chaque saut réutilise le transport HTTP/1.1
du moteur : TLS vérifié, aucune authentification, cookie ou proxy, adresses DNS
contrôlées avant connexion à une adresse numérique. Les destinations non publiques
restent refusées ; la boucle locale n'est permise que dans un exercice déclaré
synthétique avec origines littérales de boucle locale. Une redirection sortant
des origines, abaissant HTTPS vers HTTP, ambiguë ou dépassant une borne est
conservée sans requête suivante. Une boucle s'arrête sans revisiter l'URL.

Chaque tentative conserve requête disponible, réponse reçue et métadonnées de
supervision ; une requête préparée n'est pas la preuve qu'un serveur l'a reçue.
Une absence de réponse n'est pas inventée comme HTTP 200/404. Les échecs de réseau,
limites et préfixes interrompus restent disponibles. `captures.json` contient
uniquement les cibles et contextes du plan, leurs dates réelles et octets encodés.
Le budget épuisé laisse les cibles restantes avec une trace vide et une limite.

`assess` est hors réseau : il vérifie les empreintes, reconstruit les captures
depuis les fichiers bruts, rattache la revue historique avec le workflow existant
et produit un dossier moteur ainsi que des rapports FR/EN. Il ne décide aucun
verdict. Une contradiction démontrée par un préfixe complet reste NC ; une trace
incomplète sans contradiction reste NT ; l'approbation ne garantit jamais C.

Les sorties doivent être neuves, leurs parents existants. Les tentatives brutes
restent sur disque si la collecte échoue ; un état incomplet ne peut pas être
évalué comme une collecte terminée. Un paquet historique exige les outils de sa
version. Les empreintes lient les pièces, pas l'identité du responsable, la
sincérité de son jugement ou une authentification indépendante de l'acquisition.
Le rejeu ne contacte pas le site. Aucun rendu, Googlebot réel, indexation,
équivalence de contenu, audit global ou certification n'est établi.

## English

This prospective workflow prepares the existing TS02 plan, consumes an actual
supplied approval, collects the declared HTTP trajectories, then uses the unchanged
engine. It neither edits the website nor supplies a human judgment.

Before approval, `prepare` adds exact settings and collector source fingerprints
to each context and sets its technical tool/version/bounds labels. Supplied
network description and business expectations remain. The existing readable
request shows the complete context. Preparation is offline. Existing
`redirect_plan.py import-response` imports the supplied owner answers.

`collect` verifies the reviewed package, receipt, answers, tools and approval of
every target before any request. Rejection/missing review blocks this prospective
workflow, without altering the existing offline interpreter's behavior.

Bounds: 1–10 targets, 1–20 allowed origins, the planned User-Agent, explicit
identity or gzip/deflate encoding, 0.1–30 seconds per hop, 1 KiB–1 MiB per response,
0–19 collection redirects, 1 KiB–2 MiB aggregate responses and a 1–300 second
supervised phase. Collection bounds are not normative redirect expectations.
Supervisor deadlines include DNS/child execution, with ordinary scheduling and
file-writing overhead, not a hard real-time guarantee.

Anonymous ASCII HTTP(S) URLs without fragments only. Source and expected origins
must be allowed. Each hop uses the existing HTTP/1.1 worker, verified TLS and
checked DNS addresses; no cookies, authentication or proxy. Nonpublic addresses
are refused. Explicit loopback is restricted to synthetic exercises with literal
loopback origins. Out-of-origin, HTTPS downgrade, ambiguous or bounded redirects
are retained without fetching the next URL. Detected loops stop before revisiting.

Available request bytes, received response bytes and supervision metadata survive
failures. Prepared request bytes do not prove server receipt. Absent responses
are not fabricated. Exhausted aggregate/time budgets leave remaining targets
with empty traces and an explicit limit. Captures retain exact planned contexts
and intents, actual observation dates and binary native data.

Offline `assess` checks fingerprints, reconstructs captures from retained raw files,
then invokes the existing owner-plan attachment and FR/EN renderer. It does not
calculate verdicts. A proven independent contradiction survives gaps; otherwise
incomplete evidence remains NT. Outputs are new directories; failed attempts
remain available but cannot be treated as completed acquisitions. Historical
packages require their exact historical tools. Hashes do not authenticate people
or acquisition. Replay is offline. No whole-site, rendering, Googlebot, indexing,
semantic equivalence or certification claim follows.

## Frozen exercises / exercices figés

`tests/fixtures/redirect-collection-v1.json` fixes local HTTP responses and expected
control outcomes before implementation. Loopback exchanges are actual local
transport; scenarios and owner reviews remain explicitly synthetic.

## CLI and application integration / CLI et intégration applicative

```sh
python3 collectors/ts02.py prepare /private/plan.json --settings /private/settings.json --output /private/request-new
python3 adapters/redirect_plan.py import-response /private/request-new --response /private/owner-response.json --output /private/reviewed-new
python3 collectors/ts02.py collect /private/reviewed-new --output /private/collection-new
python3 collectors/ts02.py assess /private/collection-new --output /private/report-new
python3 adapters/replay.py /private/report-new/assessment/bundle --output /private/replay-new
```

FR : chaque parent de sortie doit exister et chaque dossier de sortie être neuf.
Les exemples `redirect-collection-plan.json` et `redirect-collection-settings.json`
préparent une demande hors ligne. Leur collecte exige un serveur local démarré
séparément et une réponse de revue fictive explicitement fournie ; ils ne créent
aucune approbation réelle. L’application présente les champs du plan, les bornes
et la revue au responsable puis construit les fichiers JSON dans un espace privé.
Elle appelle un Python fixé avec des arguments séparés, sans interpolation shell.
Code 0 : opération terminée, jamais verdict C ; code 64 : erreur de workflow.
Une collecte terminée peut contenir des erreurs de transport et conduire à NT.
Afficher également les limites de `collection.json`. Conserver le dossier complet
de collecte et le dossier de rapport ; ce dernier contient le paquet rejouable et
les rapports HTML FR/EN. Aucun verdict applicatif ne doit remplacer celui du moteur.

EN: Output parents must exist and output directories must be new. The two examples
prepare an offline request; collection separately requires a local fixture server
and explicitly supplied fictional review. They create no real approval. The app
presents plan, bounds and review fields, then writes private JSON files. Invoke a
pinned Python with separate arguments, without shell interpolation. Exit 0 means
operation completion, never C; exit 64 means workflow error. Completed collection
can retain transport errors and produce NT. Show `collection.json` limits. Retain
the entire collection alongside the report directory containing the replayable
bundle and bilingual HTML. The engine supplies verdicts.

## Migration and limits / Migration et limites

FR : collecteur non normatif version 1, protocole draft.33 et 48 règles inchangés.
Les anciens dossiers et l’adaptateur de redirections restent valides avec leurs
outils historiques. Une nouvelle collecte prospective exige une nouvelle demande
qui lie ce collecteur, puis une réponse du responsable ; ne pas modifier une revue
ancienne pour l’utiliser ici. TSEP Control conserve son moteur fixé jusqu’à une
importation explicite du commit complet et ses vérifications ; ne pas copier ce
seul script. L’intégration PHP et l’essai réel Edikka restent des étapes distinctes.

EN: Non-normative collector version 1; draft.33 and its 48 rules are unchanged.
Historical dossiers and redirect adapter remain usable with their original tools.
Prospective collection requires a new collector-bound request and supplied owner
response; do not retrofit an old review. TSEP Control keeps its pinned engine
until explicit import and verification of the whole commit; do not copy this
script alone. PHP integration and actual Edikka qualification remain separate.
