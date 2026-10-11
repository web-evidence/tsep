# Controlled delivery laboratory 1 / Laboratoire de diffusion contrôlé 1

## Français

Ce laboratoire facultatif applique les trois règles TS39 de **draft.27** à huit
scénarios figés avant son implémentation. Deux serveurs locaux exécutent réellement
les requêtes : une origine et un cache, sur deux ports distincts de `127.0.0.1`.
Une campagne complète conserve **24 requêtes au cache et 14 à l’origine**, soit
38 échanges HTTP. La page, la politique et toutes les revues sont fictives.
Il ne s’agit pas d’un audit Edikka ni d’un CDN de production.

| Scénario figé | Expérience | A01 / A02 / A03 | TS39 dans ce périmètre fictif |
| --- | --- | --- | --- |
| `vary-correct` | Le cache distingue les requêtes avec et sans langue déclarée | pass / pass / pass | C |
| `identical-body-bad-reuse` | Vary est ignoré ; les corps restent identiques | pass / pass / fail | NC |
| `wrong-language` | Une réponse allemande est réutilisée pour la requête sans langue | pass / fail / fail | NC |
| `repair-purged` | Configuration corrigée, ancienne entrée conservée puis explicitement purgée ; nouvelle collecte à la même URL | pass / pass / pass | C |
| `origin-canonical-error` | Canonical incorrecte à l’origine, cache contourné | pass / fail / pass | NC |
| `legitimate-validators` | Variantes linguistiques légitimes, validateurs distincts | pass / pass / pass | C |
| `linkage-withheld` | Preuve de réutilisation volontairement omise de l’entrée normative | pass / pass / inconclusive | NT |
| `encoding-variants` | Identity et gzip : octets et ETag différents, contenu décodé identique | pass / pass / pass | C |

Ces résultats attendus sont des cas contradictoires, pas une cible de huit résultats
C. Le second scénario révèle une erreur du mécanisme de cache sans prétendre
qu’un mauvais contenu a été livré. Le défaut de canonical du cinquième vient de
l’origine. Dans le septième, le journal complet du laboratoire reste conservé à
part ; le lecteur normatif ne reçoit pas la liaison nécessaire et doit rester NT.

### Exécuter et rejouer

Depuis une copie complète des outils, avec Python 3.9+ et des répertoires neufs :

```sh
python3 examples/delivery_laboratory.py run --output /tmp/tsep-delivery-run
python3 examples/delivery_laboratory.py replay /tmp/tsep-delivery-run --output /tmp/tsep-delivery-replay.json
```

La collecte dure au moins la fenêtre préalable de 15 secondes. Chaque échange est
borné à trois secondes, 32 768 octets reçus et 4 096 octets de requête. Aucun DNS,
proxy, cookie, authentification ou site externe. Les octets reçus par les deux
serveurs sont liés aux octets émis par les clients, aux configurations effectivement
écrites, aux entrées du cache, aux opérations de purge et aux horloges conservées.
Le rejeu ne fait aucun appel réseau, ne lance aucun processus et ne purge rien.

La recette et son empreinte sont distribuées dans `tests/fixtures/`. Le dossier
conserve le plan préalable, les captures, les journaux, les changements de
configuration, les résultats et huit dossiers de preuves scellés. Il ne faut pas
ajouter de rapports HTML dans ce dossier : les dérivés de présentation vont à côté.
Une interruption laisse les captures partielles et `failure.json`, sans manifeste
de réussite. Un résultat inattendu reste enregistré ; consulter
`all_expectations_matched`, le succès du transport ne prouvant pas cet accord.
Un rejeu exige les sources exactes liées à la campagne, pas leur dernière version.

### Limites et provenance

Le cache implémente un profil fermé : GET complet, statut 200, langue absente ou
`de`, encodage `identity` ou `gzip`, Vary explicite, fraîcheur `max-age=300`.
L’âge utilise l’âge apparent, le délai mesuré et la résidence monotone. Il n’existe
ici ni revalidation, ni réponse périmée, ni heuristique, ni streaming, ni variation
authentifiée, ni qualification d’une implémentation HTTP générale. La règle Vary
et le calcul d’âge sont fondés sur [RFC 9111, sections 4.1 et 4.2.3](https://www.rfc-editor.org/rfc/rfc9111.html).

Les jugements de langue, de contexte, d’accès, d’exemption de rendu et de provenance
sont **rédigés pour l’exercice**. Les captures HTTP et opérations locales sont
réelles ; ces revues ne constituent pas une relecture humaine ni une observation
navigateur. Aucune visite de Googlebot, région, indexation, position ou vérité du
contenu n’est établie. Empreintes et rejeu détectent les incohérences couvertes ;
ils n’authentifient pas l’auteur d’un journal. L’encodage gzip dépend du runtime :
le rejeu exact est qualifié avec les outils et le runtime conservés, sans promesse
d’identité entre toutes les versions Python/zlib.

Le premier essai a conservé une omission du profil robots dans le plan : six
attentes de cas n’étaient pas satisfaites. Le plan a été corrigé sans modifier
les règles ou les attendus figés. Un test ultérieur a révélé une liaison manquante
entre la réponse robots du cache et celle de l’origine ; elle a été ajoutée au
vérificateur du laboratoire. Voir [la provenance](../provenance/delivery-laboratory-v1.json).
Draft.27, ses 33 règles et le corpus normatif restent inchangés.

## English

This optional laboratory applies draft.27's three TS39 rules to eight scenarios
frozen before implementation. Two numeric-loopback servers perform actual HTTP:
an origin and a cache on distinct ports. One complete campaign retains **24 edge
and 14 origin requests**, or 38 exchanges. The page, policies and all reviews are
fictional; this is neither an Edikka assessment nor a production CDN test.

The table above preserves the eight recipe IDs and ordered A01/A02/A03 outcomes.
It distinguishes correct Vary reuse, invalid reuse with identical content, a wrong
cached language, repair plus explicit purge at the same URL, an origin canonical
error with cache bypass, legitimate language validators, deliberately withheld
linkage, and legitimate identity/gzip variants. Expected control statuses are
C/NC/NC/C/NC/C/NT/C. A mechanism failure does not imply that wrong content was
delivered. In the withheld case, full laboratory traces remain separate while
the normative input lacks the required cache linkage and stays inconclusive.

Use the two commands above from a complete tool copy with Python 3.9+ and new
output paths. Collection lasts at least its prior 15-second window; each exchange
is limited to three seconds, 32,768 response bytes and 4,096 request bytes. No DNS,
proxy, cookies, authentication or external collection. Exact server-received and
client-emitted bytes, actual configuration files, cache entries, purge operations
and clocks are retained. Offline replay performs no network request, child process
or cache operation. Keep HTML derivatives outside the sealed laboratory folder.
An interruption retains partial observations and a failure record without a success
manifest. Unexpected outcomes remain visible in `all_expectations_matched`;
successful transport alone does not establish that expectations matched.
Historical campaigns require their exact retained sources, not newer tools.

This is a closed cache profile: complete 200 GETs, absent or `de` language,
identity/gzip encoding, explicit Vary, max-age=300, apparent age plus measured
delay and monotonic residence. There is no revalidation, stale delivery, heuristic,
streaming, authenticated variation or general HTTP cache conformance claim.
RFC 9111 sections 4.1 and 4.2.3 are the method reference linked above.

Semantic/context/access/rendering-exemption/provenance judgments are authored
exercise data. HTTP and local operations are actual; no human review, browser
observation, actual operator visit, geography, indexing, ranking or factual truth
is established. Hashes/replay check covered consistency, not journal authorship.
Exact gzip reproduction is qualified against retained tools/runtime, not every
Python/zlib version. The first experiment's missing prior robots profile and the
subsequent robots origin/edge binding test failure remain documented in provenance.
Neither correction changes the frozen expectations, draft.27 rules or corpus.
