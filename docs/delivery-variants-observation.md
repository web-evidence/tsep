# Delivery variants observer / Observateur de variantes de diffusion — 1

## Français

Cet outil facultatif prépare TS39 en séparant les faits HTTP, les déclarations
de contexte et les conditions de correspondance de `Vary`. Il ne produit aucun
verdict TS39 et ne change aucune règle de draft.26. Les régions, POP, états du
cache et identités d’opérateurs restent des déclarations non authentifiées.

### Entrée et portée

`experiments/delivery_variants.py` lit un objet `delivery-variants-input`, version
`1`, avec un booléen `synthetic`, un `plan` préalable et des `observations`.
Le plan comporte `declared_at`, `window_start`, `window_end`, `cells` et `pairs`.
Une cellule déclare `id`, URL initiale, `user_agent` HTTP complet, `request_fields`
et `context_claims`. Un champ de requête attendu vaut une liste ordonnée de valeurs
ou `null` pour son absence ; `[]` ne représente pas un champ vide. Un champ présent
vide vaut `[""]`. Noms de champs en minuscules, hors Host/User-Agent traités à part.
Une paire nomme un côté `left` (hypothèse de réponse stockée) et un côté `right`.

Chaque observation relie `cell_id` à une liste `http` de requêtes/réponses brutes,
URL, dates d’envoi/réception et déclaration de complétude. Texte UTF-8 ou enveloppe
base64/sha256 du format HTTP existant ; requêtes GET HTTP/1.1 sans corps.
Les origines restent explicites ; aucune URL n’est visitée. Cellules absentes et
captures partielles restent dans la population. Doublon, observation hors plan,
plan tardif ou comparaison inconnue font refuser l’entrée au lieu d’omettre une pièce.

Bornes : 64 cellules, 128 paires, 20 sauts par cellule, 32 champs de requête,
128 membres Vary, fenêtre de 24 heures et 8 Mio d’entrée/HTTP agrégé. L’ordre
chronologique s’applique dans chaque chaîne ; les cellules peuvent se chevaucher.
Ces dates fournies ne sont pas une authentification de l’horloge ou de la collecte.

### Observations conservées

Le lecteur garde le statut, tous les champs de requête/réponse, les empreintes
des messages et du corps décodé, ainsi que la chaîne de redirections. Une capture
tronquée peut conserver ses en-têtes complets tout en laissant le corps inconnu.
Une différence X-Robots-Tag reste donc visible à côté d’un corps non comparable.
Les réponses 204/205/206/304 et requêtes conditionnelles/Range ne sont pas qualifiées
pour comparer une représentation complète ; le statut observé reste disponible.
Un changement gzip/identity peut conserver les mêmes octets décodés.

Les comparaisons de corps ne portent que sur les octets décodés. Elles n’établissent
ni équivalence de contenu, ni langue du texte, ni canonical valide. Les valeurs
Link/X-Robots-Tag/Content-Language sont conservées sans interprétation sémantique.
Une différence peut être légitime ; une égalité ne prouve pas la qualité SEO.

### Vary : correspondance bornée, pas validation du cache

Selon [RFC 9110 §12.5.5](https://www.rfc-editor.org/rfc/rfc9110.html#section-12.5.5),
Vary décrit des dimensions de sélection. [RFC 9111 §4.1](https://www.rfc-editor.org/rfc/rfc9111.html#section-4.1)
définit la comparaison des champs nommés de la requête d’origine et de la nouvelle
requête. L’observateur utilise **le Vary du côté gauche**, pas l’union des réponses.
`*`, y compris parmi d’autres membres, empêche cette correspondance ; le nom des
champs est insensible à la casse. Les membres vides bornés sont ignorés.

Une absence ne correspond qu’à une absence. Des listes de valeurs identiques
correspondent littéralement. Pour Accept-Language/Accept-Encoding seulement,
une syntaxe bornée de plages/codages et poids q qualifie casse, espaces et poids
équivalents. Les doublons de préférence restent inconnus ; un changement d’ordre
seul n’est pas déclaré équivalent. Les autres valeurs différentes restent
indéterminées, sans inventer de normalisation. Une différence certaine sur un
champ suffit à établir la non-correspondance malgré une autre dimension inconnue.

La sortie distingue `matching`, `nonmatching`, `undetermined`, `unconstrained`
(absence de contrainte Vary) et `not-comparable` (URI différentes). Aucune de ces
valeurs n’autorise une réutilisation : stockage, fraîcheur, revalidation, couche
du cache et origine de la réponse ne sont pas établis. Age, ETag ou X-Cache: HIT
restent des champs observés, pas une preuve autonome d’une action du cache.

### Étape normative restante

TS39 nécessite encore trois ensembles de décisions : (1) matrice préalable et
configuration des mécanismes qualifiées par revue liée ; (2) signaux de statut,
redirection, canonical, robots, langue et contenu confrontés à une politique
explicite, en réutilisant les lecteurs qualifiés et les revues sémantiques ;
(3) contexte réel, mécanismes de variation et éventuelles réutilisations rapprochés
de preuves attribuées. Les cases absentes et défauts indépendants doivent coexister.
Ce lecteur est une dépendance préparatoire, pas un remplacement de ces exigences.

La documentation Google sur les [pages adaptées à la région](https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages)
invite à considérer le client sans Accept-Language et plusieurs contextes
géographiques. Un test avec un User-Agent déclaré ne devient pas une visite
[Googlebot authentifiée](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers).
Le contrôle final devra garder distincts politique, accessibilité testée et accès
réel d’un opérateur. Aucun classement, indexation ou cloaking n’est déduit ici.

## English

This optional version-1 observer prepares TS39 without changing draft.26 or
producing control outcomes. Input declares a prior bounded matrix of cells and
directional comparisons, retains original HTTP chains and labels context claims
as unverified. Missing cells remain visible; duplicate/unplanned observations
or malformed/late plans are refused. Bounds and input keys are detailed above.

Each cell retains request/response headers, original message hashes, decoded-body
hashes and redirect chronology. Incomplete bodies do not erase independent header
observations. Whole-representation comparison is unavailable for 204/205/206/304
and conditional/Range requests. Compression differences may preserve decoded bytes.
Byte or header differences are not SEO failures; equality is not semantic content,
language or canonical qualification. No HTML, JavaScript or crawler is executed.

Vary matching uses the left response's named request fields. Wildcard prevents
matching, including when combined with other members. Absence differs from a
present empty field. Equal ordered values match literally; bounded language/coding
preferences permit only explicitly qualified case/whitespace/q normalization.
Duplicate preferences, order-only changes and unsupported differing fields remain
unknown. A known mismatch survives another unknown field. No Vary is unconstrained,
not proof of valid reuse. Different target URIs are not comparable for this purpose.
Storage eligibility, freshness, revalidation and actual reuse are not implemented.

The remaining normative work is a reviewed prior matrix/configuration, policy-based
SEO signal interpretation, semantic language/content reviews and attributed delivery
context/cache evidence. User-Agent, geographic labels, Age and HIT headers do not
authenticate those claims. The referenced RFCs and Google documentation are sources
for method design, not evidence about a particular CDN, Edikka or actual Googlebot.

## Local use / Usage local

```sh
python3 experiments/delivery_variants.py input.json --output observation.json
python3 -m unittest tests.test_delivery_variants -v
```

The output path must be new. It retains the exact input-file hash and parsed-input
hash separately. No network, DNS, subprocess or supplied command execution. The
49 frozen cases are authored exercises, not external observations or 49 controls.
The initial reader passed 44 cases; a subsequent five-case boundary set exposed
the 206 whole-body error, corrected before integration. Both histories are retained.
FR : conserver les captures et outils exacts ; ne pas promouvoir cette observation
en rapport de conformité ou réécrire un ancien dossier.
