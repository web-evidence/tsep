# TS15 — supplied sitemap files / fichiers sitemap fournis

Profile `native-sitemap-files-v1`, reader1, draft.35. Interpreter34 / adapter35 /
HTML19 / replay3. Three rules; execution and application delivery recorded separately.
44 native reader expectations,31 set expectations and4 review counterexamples were
frozen before their corresponding implementation/change. These are authored synthetic
cases, never independent validation or actual server observations.

## Français

Le résultat porte uniquement sur une **population déclarée de fichiers fournis**.
Une racine n’est pas découverte ni attribuée à robots.txt/Search Console/CMS par
le lecteur. Le nombre de fichiers, les racines et `root_discovery=not-established`
restent visibles, même pour C. Un index non fourni peut désigner d’autres fichiers ;
aucune exhaustivité des sitemaps du site n’est établie. Les URL, dates, provenance
et complétude sont déclarées, non authentifiées. Un NC désigne le fichier fourni
déclaré pour une URL, jamais une réponse du serveur observée.

L’entrée de l’adaptateur reste `input_version=2`, rules et targets. Chaque cible
contient url (première racine), observed_at, sitemap_synthetic booléen, context
(network,bounds,tool,tool_version) et intent.declared_at. intent.sitemap_files contient
reader, selection_reason non vide, window_start/end (<=24h), roots et documents.
Le plan précède la fenêtre ; celle-ci précède observed_at.1–16 URL de documents
distinctes, roots non vide/distinct/sous-ensemble ; URL absolues HTTP(S), sans
identifiants, fragment ni espaces. Comparaison exacte, sans normalisation ni requête.

`sitemap_files` contient au plus16 objets : url déclarée exacte, description,
observed_at dans la fenêtre, provenance=`synthetic-exercise` ou `supplied-native-file`,
et native={raw_base64,sha256,encoding,complete}. encoding vaut identity ou gzip,
complete est booléen, base64 est strict et canonique. SHA-256 lie l’original exact.
Le nom de fichier ne détermine pas l’encodage. Aucun original n’est recompressé.
La provenance synthétique doit correspondre à l’accès synthetic du dossier ; une
pièce fictive ne devient jamais publique par un changement d’étiquette.

L’import refuse techniquement tout original altéré, base64 invalide, encodage
inconnu ou fichier brut >5 242 880 octets. L’enveloppe JSON entière conserve sa borne
8 388 608 octets : plusieurs fichiers peuvent l’atteindre avant leur limite
individuelle. Un XML brut de50Mio est donc refusé ; un gzip fourni assez petit peut
être évalué à sa taille décompressée réelle. Refus de transport ≠ NC/NT du contrôle,
aucun rapport réussi n’est créé à la destination. Données absentes dans un dossier
intègre : inconclusive, jamais C/NA.

A01 lit UTF-8 strict sur les octets décompressés, BOM UTF-8 inclus dans la taille ;
un défaut d’encodage donne fail pour le fichier complet seulement si une lecture
secondaire bornée à65 536 octets attribue sa racine à Sitemaps0.9. Cette lecture
s’arrête au premier élément, refuse DTD/entités avant expansion et n’accepte ni
ne répare un sitemap UTF-16. RSS UTF-16, binaire ou texte sans racine attribuée :
inconclusive. Une racine urlset/sitemapindex lue normalement avec namespace erroné
reste une contradiction explicite. Une racine trop tardive reste inconnue.
Racines urlset/sitemapindex dans le namespace exact
`http://www.sitemaps.org/schemas/sitemap/0.9` ; préfixes libres. Namespace absent ou
erroné d’une de ces formes : fail. Autre format (RSS/Atom) : inconclusive.
Un élément url/sitemap direct exige un loc non vide unique, en tête, puis feuilles
ordinaires uniques et ordonnées : lastmod/changefreq/priority pour url, lastmod pour
sitemap. XML globalement mal formé complet, loc absent/doublé, texte mixte ou élément
de base inattendu : fail. DTD et déclarations d’entités sont arrêtés avant expansion,
sans chargement réseau ; extensions/attributs inconnus et xml:base : inconclusive.
La seule annotation de racine qualifiée est xsi:schemaLocation, conservée sans
charger ni appliquer le schéma. Commentaires et instructions sont inertes.

A02 compte les octets bruts réellement décompressés (BOM, caractères multioctets,
échappements et fins de ligne inclus), et tous les éléments url/sitemap directement
sous leur racine qualifiée. Les doublons et entrées sans loc comptent ; les extensions
ne sont pas des entrées. Maximum inclusif52 428 800 octets et50 000 éléments par
fichier ou index.52 428 801 octets ou50 001 éléments effectivement lus donnent fail,
si le préfixe attribue une racine Sitemaps0.9, même si la lecture s’arrête là.
Sans cette attribution, la mesure arrêtée reste descriptive et A02 inconclusive ;
RSS, DTD et racine au-delà du préfixe ne deviennent pas NC par cette mesure.
Le diagnostic dit exact ou borne inférieure ; le
champ ISIZE, un compteur fourni ou le nom .gz ne suffisent jamais. Une lecture
arrêtée ne qualifie pas A01. Un comptage complet peut passer malgré une feuille
malformée ; A01 reste alors fail. Les trois axes ne doivent pas être confondus.

Un seul membre gzip complet est qualifié. Flux tronqué, CRC erroné, membres concaténés
ou données finales : inconclusive, sauf dépassement déjà établi indépendamment.
CRC/fin de flux n’authentifient pas la source. Capture déclarée incomplète : inconclusive.
Bornes internes : profondeur16,300 000 éléments,4096 caractères par feuille ; dépasser
une borne interne donne inconclusive, jamais une violation de sitemap inventée.

A03 requiert exactement les documents déclarés, un original non ambigu par URL et
une couverture par les racines. Chaque enfant loc d’index doit correspondre à une
URL déclarée et à un fichier feuille complet qualifié. Pas de parcours réseau,
normalisation, suivi de redirection ou attribution depuis le nom. Enfant absent,
orphelin, format illisible, cycle ou index imbriqué : inconclusive. L’absence de
preuve de couverture n’est pas une contradiction démontrée : cette règle ne produit
pas fail. Une contradiction A01/A02 indépendante reste fail malgré cette lacune.

C exige les trois pass pour toute la population déclarée ; NC exige une contradiction,
sinon NT. Aucun NA automatique. Ce profil ne valide pas tout XML Schema, les valeurs
des feuilles facultatives, le sens/la fraîcheur de lastmod, l’hôte/le chemin/la longueur
des URL, leur canonical, leur indexation, les soumissions ni le périmètre éditorial.
Il ne faut pas présenter C comme « sitemap valide pour Google » ou conformité globale.
Les originaux restent dans input.json et les pièces dérivées ; le rejeu exige le même
moteur exact, sans réseau. Les autres règles qui emploient Node gardent leur exigence
propre ; TS15 utilise uniquement Python standard.

## English

The outcome covers only a **declared population of supplied files**. Roots are not
discovered or attributed to robots.txt/Search Console/CMS. Declared document count,
roots and root_discovery=not-established remain visible even for C. An omitted index
may reference other files; no site-wide sitemap completeness is established. URLs,
dates, provenance and completeness are supplied and unauthenticated. NC concerns a
supplied file declared for a URL, never an observed server response.

The exact input fields, bounds and constants are specified above. A target is anchored
to its first root and has an explicit synthetic boolean, dated prior plan, <=24h window,
context,1–16 distinct document URLs and nonempty distinct roots within that list.
There are at most16 supplied records with declared URL, description, provenance,
windowed timestamp and native raw_base64/SHA-256/identity-or-gzip/boolean completeness.
URLs are literal absolute HTTP(S), without credentials, fragment or whitespace.
No network request, URL normalization or implicit file recompression takes place.
Synthetic provenance must match dossier access.

Technical intake rejects changed bytes, invalid/noncanonical base64, unknown encoding,
or original files larger than5,242,880 bytes. The entire JSON retains its8,388,608-byte
bound, which multiple files may reach first. A50MiB plain XML file is refused; a small
enough supplied gzip can exercise the true decompressed threshold. Transport refusal
is not a C/NC/NT control outcome and creates no successful report. Missing evidence
in an intact dossier stays inconclusive, never C/NA.

A01 checks strict UTF-8 bytes, optional UTF-8 BOM, compatible encoding declaration,
exact Sitemaps0.9 namespace and minimal base structure. Prefixes are arbitrary.
A complete known root with wrong/missing namespace fails; RSS/Atom/other roots are
outside the profile. Each direct url/sitemap requires one nonempty loc first, then
unique ordered optional leaves: lastmod/changefreq/priority for url, lastmod for
sitemap. Attributed malformed XML, missing/duplicate loc, mixed base text or unexpected
base elements fail. DTD/entities stop before expansion without network loading.
Unqualified extensions/attributes/xml:base stay inconclusive. Root xsi:schemaLocation
is retained, never fetched or applied. Comments and processing instructions are inert.

Encoding failures establish fail only when a separate bounded first-root reader
attributes Sitemaps0.9 within65,536 bytes. It stops at the first element, rejects
DTD/entities before expansion and never accepts or repairs UTF-16. UTF-16 RSS,
binary or unassigned text remains inconclusive; a late root remains unknown.

A02 measures actual decompressed bytes, including BOM, multibyte characters, escapes
and line endings, and counts all direct url/sitemap elements under their qualified
root, including duplicates and entries missing loc. Foreign extensions do not count.
Inclusive bounds are52,428,800 bytes and50,000 direct entries per file/index. Actually
reading the first excess byte/entry establishes fail only with an attributed
Sitemaps0.9 root. Without that attribution, the stopped byte measurement remains
descriptive and A02 inconclusive, including RSS, DTD and a root beyond the prefix.
Diagnostics distinguish an exact
measure from a lower bound. No decision from ISIZE, filename or supplied counters.
A stopped prefix cannot qualify A01. Complete counts may pass despite a malformed leaf,
whose A01 remains fail. A complete single gzip member is qualified; truncation, bad CRC,
multiple members or trailing data stay unknown except an independently established
excess. Stream integrity never authenticates origin. Declared incomplete files stay
unknown. Internal limits16depth/300,000elements/4,096characters per leaf cause unknown,
never a fabricated sitemap violation.

A03 binds exactly one unambiguous supplied record to every declared URL and traverses
only root index→leaf relationships among that declared set. Every index loc must bind
to a complete qualified supplied leaf. No fetch, redirect following, filename attribution
or normalization. Missing/orphan/unreadable children, cycles or nested indexes stay
inconclusive. Missing coverage is not a proven contradiction, so A03 has no fail
outcome. Independent A01/A02 failures survive missing branches.

C needs all three passes across the declared population; evidenced contradiction gives
NC, otherwise NT. No automatic NA. No complete XSD validation, optional leaf value
semantics, lastmod truth/freshness, URL host/path/length, canonical, indexing, submission
or editorial-scope conclusion. Never describe C as Google eligibility or whole-site
conformity. Original bytes remain in the native input and derived evidence. Standalone
replay requires the exact engine and no network. TS15 uses Python standard library;
other controls keep their own explicit Node runtime requirements.

## Sources / Sources

[Official captured sources and fingerprints](../research/sitemap-files-2026-10-14/provenance.json):
Sitemaps.org protocol and0.9 schemas, Google's large sitemap documentation. Their
syntax/size requirements inform this bounded editorial profile; they do not endorse
TSEP or establish independent validation. No Google account collection was performed.

### Closed outcome domain / Issues fermées — TS15-A03

FR : la règle TS15-A03 déclare dans spec/protocol.json
`allowed_outcomes: ["pass", "inconclusive"]`. Aucun fail ni not-applicable n'est
admis pour cette règle, y compris dans un rapport fourni. Le banc exige au moins
un cas pour chacune de ces deux issues. Toutes les autres règles gardent leurs
issues historiques et l'exigence pass/fail/inconclusive du banc. Supprimer une
classe du corpus ne réduit jamais cette exigence. Le profil ne contient aucune
affirmation déclarative de lien parent/enfant : un fichier déclaré orphelin donne
inconclusive. Une future assertion de parent contradictoire exigerait une autre
version ; elle ne doit pas être déduite de la déclaration de population.

EN: TS15-A03 declares `allowed_outcomes: ["pass", "inconclusive"]` in the canonical
protocol. Neither fail nor not-applicable is accepted for that rule, including
in supplied reports. The corpus must contain each of its two declared outcomes.
Every other rule retains its historical domain and required pass/fail/inconclusive
coverage. Removing a class from the corpus never weakens this requirement.
The profile has no declared parent/child assertion: an orphan declared file stays
inconclusive. A future contradicted parent assertion would require another version;
it must not be inferred from the population declaration.
