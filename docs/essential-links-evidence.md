# TS17 — supplied essential links / liens essentiels fournis

Profile `essential-document-links-v1`, draft.36; interpreter35 / adapter36 /
HTML20 / replay3. Two rules. Qualification and app delivery are recorded separately.
The authored source52, DOM37, combined31, malformed36 and identity3 cases were
frozen before their respective implementations/changes. The additional five native
HTTP-member boundaries and twelve revised intake cases retain the earlier uniform-NT
proposal and its explicit review-driven revision. They are synthetic tests,
not actual site observations or independent review approval.

## Français

TS17-A01 examine les liens dans la source fournie. TS17-A02 examine chacun des
états DOM déclarés. Le profil exige une stratégie préalable `source-and-rendered` :
ce choix éditorial TSEP n’est pas une obligation universelle de présence source
imposée par Google. Chaque stade conserve ses résultats et ses limites. C exige
toutes les destinations à chacun des stades requis ; une absence qualifiée donne
fail pour ce stade, même si un autre stade reste inconnu. Aucun NA automatique.

L’entrée `input_version=2` contient rules et targets. Une cible contient url,
observed_at, link_synthetic booléen, context(network,bounds,tool,tool_version),
http et render.states, ainsi que intent.crawler et intent.declared_at.
intent.essential_links contient reader, strategy, selection_reason, window_start,
window_end, max_duration_ms, final_url, destinations et states. Le plan précède une
fenêtre d’au plus24h, terminée avant observed_at.1–16 échanges HTTP ; chaque durée
est positive ou nulle et bornée par max_duration_ms (entier1–30000). Le dernier
échange est un200 complet à final_url. Les octets/empreintes du transport v2 sont
conservés ; un original altéré est refusé techniquement, sans rapport réussi.
À l’import TS17, un conteneur HTTP non nul doit être une liste d’objets : un
mauvais type est refusé avec le motif « TS17 HTTP structure », sans rapport.
HTTP absent, nul ou vide et objets partiels (y compris objet vide ou
complete=false) restent des preuves insuffisantes, conservées avec NT et motif.
Le lecteur natif seul reste indéterminé sur ces structures ; ce n’est pas une
validation du transport. Les empreintes corrompues ont leur refus distinct.

Destinations :1–32 objets {url,reason}, URL distinctes HTTP(S), sans identifiants,
fragment ou auto-lien à url/final_url. Chaque URL doit déjà égaler sa sérialisation
WHATWG. Les raisons d’importance sont fournies, non jugées par l’outil. Les href
sont résolus WHATWG avec la base effective qualifiée puis leur fragment retiré :
comparaison exacte de documents, sans visite réseau, redirection, canonical,
équivalence éditoriale ou existence de l’ancre. La casse des échappements pourcent
reste significative. Une autre destination de requête, hôte ou chemin ne convient pas.

Source : HTTP/HTML UTF-8 complet, inventaire natif `html-tree-links-v2` sous les
deux hypothèses statiques de scripts. Les deux doivent donner la même issue. Un
élément HTML a avec href résoluble dans le document principal témoigne de la
présence ; area/link/bouton/onclick, texte de script/commentaire et contenu template
ne remplacent pas a/href. Une erreur de parsing, un contexte étranger/shadow non
qualifié ou une hypothèse divergente reste inconclusive. Une balise base active
sort du profil initial, même si des liens absolus existent. Aucun arbre réparé
silencieusement, aucune sérialisation DOM substituée à l’arbre natif.

États :1–16 objets préalables {id,browser,browser_version,scenario}, non vides,
ids distincts. Chaque état fourni a cet id/navigateur/version, observed_at entre
la réception HTTP et window_end, complete=true, javascript_enabled=true, errors=[],
et structured_dom v2 avec snapshot original, empreinte, acquisition et support.
Document URL et base_uri égalent final_url ; aucune base active admise. Le profil
v2 vérifie l’association aux octets HTTP et à l’agent déclarés. Cela ne prouve pas
que cette réponse a réellement alimenté la navigation. Un échange ou agent distinct
non lié rend le stade inconclusive ; plusieurs navigations indépendantes avec leurs
propres réponses exigeraient un autre profil. Rien ne prouve les actions du scénario.
Le libellé est toujours « états déclarés par le fournisseur ». Des snapshots
identiques pour plusieurs états sont signalés, sans fail automatique.

Inventaire qualifié complet sans une destination essentielle : fail. Capture
absente, tronquée, état manquant/dupliqué/non prévu, base changée, mauvais binding,
média/encodage/runtime inconnu : inconclusive, jamais C/NA. Un fail d’un état
qualifié survit à un autre état absent. Une capture déclarée synthétique reste
synthétique, même sans plan. Les revues et décisions humaines ne sont pas créées.

Limites : profils source/DOM existants et leurs bornes s’appliquent, entrée JSON
<=8Mio et Node24 explicitement sélectionné, aucun repli silencieux. Pas de serveur
ou navigateur exécuté, authenticité, visibilité, clic effectif, consentement,
importance du lien, nofollow, qualité de texte d’ancre, indexation ou classement.
Les preuves sans plan peuvent être conservées intactes avec NT ; aucun plan n’est
reconstruit depuis l’état observé. L’export autonome garde le moteur exact.

## English

TS17-A01 evaluates supplied source links; TS17-A02 evaluates each declared DOM
state. A prior `source-and-rendered` strategy is required by this bounded TSEP
profile, not as a universal Google requirement. C requires every declared destination
in both stages. Qualified complete absence fails that stage; independent failure
survives another missing/unknown stage. There is no automatic NA.

Input2 targets provide url, observed_at, boolean link_synthetic, named capture
context, original http, render.states, intent.crawler and prior declared_at.
intent.essential_links contains reader, strategy, selection_reason, window_start/end,
max_duration_ms, final_url, destinations and states. Prior plan <= window start <=
end <= observed_at; window <=24h,1–16 HTTP exchanges, each within a declared integer
1–30000ms bound. Final complete response200 must match final_url. Corrupt original
bytes are a technical intake refusal, never a successful assessment report.
At TS17 intake, non-null HTTP must be a list of objects; a wrong container/member
type produces a distinct “TS17 HTTP structure” refusal and no report. Omitted,
null or empty HTTP, and partial objects (including empty or complete=false records),
remain retained insufficient evidence with explicit NT reasons. The standalone
native reader stays inconclusive on these structures; it does not validate intake.
Corrupt fingerprints retain their separate technical refusal.

The1–32 distinct {url,reason} destinations must be exact pre-serialized WHATWG
HTTP(S), credential/fragment-free and different from requested/final document URLs.
Their importance is supplied, not adjudicated. Resolve hrefs and discard fragments
only for exact document comparison. No network, redirect/canonical equivalence,
fragment existence or editorial equivalence is inferred; percent-escape case remains
exact. Qualified HTML a/href in the main document is required; area/link/button,
onclick, script/comment text and template content do not replace it.

Native source reading uses both static scripting hypotheses of html-tree-links-v2;
disagreement, reported parse recovery or unsupported foreign/shadow context stays
inconclusive. Any active base is outside the closed initial profile, including when
absolute links exist. No silent tree repair or substituted DOM serialization.

The prior1–16 states are {id,browser,browser_version,scenario}. Supplied states match
id/browser/version, have complete=true, javascript_enabled=true, errors=[], dated
within paired HTTP reception/window_end, and original structured_dom v2 snapshot,
fingerprint, acquisition and supporting pieces. Document URL/base_uri equal final_url;
active base is unsupported. Existing v2 checks the supplied exact HTTP/client binding,
not actual acquisition, causality or interaction history. Different unbound navigation
HTTP/client leaves rendering inconclusive; independent multi-navigation exchanges are
deferred to another profile. Results explicitly say provider-declared states, and
repeated snapshot fingerprints across state IDs are disclosed without automatic failure.

Missing/partial/unplanned/duplicate state, changed base, bad binding or unavailable
media/encoding/runtime never becomes C/NA. A known failure survives another state’s
missing evidence. Explicit synthetic provenance is retained even without a plan;
no human review, plan or decision is fabricated. Current bounded source/DOM transports
and8MiB JSON limit apply, with explicit qualified Node24 and no silent fallback.
No actual server/browser execution, authenticity, visibility, activation, consent,
importance, nofollow, anchor quality, indexing or ranking is established. Export/replay
retains exact originals/runtime; missing plans remain missing, not reconstructed.

## Sources and observed-review limits / Sources et limites des revues

Dated public captures and fingerprints: `research/essential-links-2026-10-14/`.
Google links-crawlable and WHATWG links/semantics explain HTML link/URL concepts;
they do not approve this TSEP profile. Claude’s method suggestions are retained in
local sprint evidence, not treated as human approval or executed tests. TS01–TS44
and historical upstream provenance are retained. This is not certification.
