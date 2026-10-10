# Replay workflow 3 / Parcours de rejeu 3

## Français

Cette version change le **parcours de comparaison**, pas les règles de draft.18,
l'interpréteur 18 ni l'adaptateur 19. Les outils de workflow 2 restent nécessaires
pour reproduire leur propre comportement historique. Aucun paquet ancien n'est
réécrit. La nouvelle comparaison optionnelle peut lire un ancien paquet seulement
si ses sources d'adaptateur/interpréteur correspondent exactement aux outils utilisés.

### Deux comparaisons explicites

```sh
python3 adapters/replay.py /chemin/paquet --output /chemin/rejeu-exact
python3 adapters/replay.py /chemin/paquet --output /chemin/rejeu-python \
  --comparison python-supervisor-v1
```

`exact`, par défaut, exige une égalité JSON typée des observations source : ordre
des tableaux significatif, ordre des clés d'objet indifférent. Les espaces de
sérialisation ne sont pas comparés. Contrairement à l'ancienne égalité Python,
`true`, `1` et `1.0` sont distingués. Les résultats atomiques, résultats de contrôle,
décision, protocole et sources des outils doivent toujours correspondre.

`python-supervisor-v1` ajoute une seule exception : les chaînes de version Python
du superviseur, aux emplacements fermés ci-dessous, peuvent différer. Chaque valeur
doit correspondre à `import.json.runtime.python` de son propre paquet. Le runtime
du nouveau paquet est aussi contrôlé contre l'exécution courante. Le profil accepte
CPython stable 3.9 et suivantes dans Python 3 (`3.mineure.correctif`), sans liste
blanche limitée aux versions essayées localement. Il ne qualifie pas cette plage
entière. Une implémentation différente, une version absente ou incohérente ne permet
pas l'exception ; une comparaison exactement identique reste possible.

| Règle et lecteur/version | Emplacement dans chaque observation | Identité requise |
| --- | --- | --- |
| TS07-A01/A03, html-tree-directives-v1 / 1 | inventory.supervisor.python_version | unapplied-http-source-tree, experiment_version 1, metadata_extension 1 |
| TS10-A01/A02, html-tree-canonical-v1 / 1 | inventory.supervisor.python_version | précédente + head_extension 1 |
| TS10-A04, html-tree-links-v1 / 1 ou html-tree-links-v2 / 2 | inventory.supervisor.python | unapplied-link-elements, version 1 |
| mêmes TS10-A04 | base_policy_metadata.supervisor.python_version | unapplied-http-source-tree, experiment_version 1, metadata_extension 1 |
| mêmes TS10-A04 | url_runs[i].supervisor.python | unapplied-url-resolution, version 1 |

Chaque ouvrier doit porter `normative_effect: none`. Aucune recherche récursive
de clés nommées « python » ou « runtime » n'est effectuée. Node, parseur, empreintes,
délais, tailles, décodage, attributs, URL, populations, offsets, hypothèses, motifs
et décisions restent comparés exactement. Les champs inconnus restent comparés,
pas supprimés. Un champ ajouté, absent, de type changé ou un fichier d'observation
supplémentaire empêche la correspondance. Un refus identique, sans inventaire,
peut se rejouer : ce n'est pas la réussite du contrôle.

### Lire le reçu

- `same_source_observations` reste l'égalité exacte, même lorsque le profil accepte
  des différences. Il n'est jamais transformé en `true` par l'exception.
- `comparison_profile` nomme la méthode choisie ; `source_observations_match`
  indique la correspondance **selon cette méthode**.
- `source_observation_comparisons` détaille par fichier les chemins JSON Pointer,
  types/empreintes des valeurs divergentes et les versions exactes admises. Au-delà
  de 1 000 différences par fichier, comparaison incomplète et rejet ; jamais succès
  sur une liste tronquée. Les fichiers propres à un seul côté sont listés séparément.
- `original_runtime` et `current_runtime` conservent les environnements déclarés.
  Unicode est observé pour le nouveau rejeu ; sa valeur historique est `null`,
  non renseignée, et n'est pas reconstruite.
- `replayed` exige la correspondance selon le profil **et** les mêmes résultats
  atomiques, résultats de contrôle et décision. Un code 0 peut donc coexister avec
  `same_source_observations: false`, mais uniquement sous le profil explicite.

Code 64 : entrée invalide, outils incompatibles ou divergence. Les divergences
calculées conservent leur sortie dans les bornes du paquet ; les erreurs de lecture,
d'intégrité ou de budget empêchent la livraison. Le dossier `bundle/` garde le nouveau
calcul ; `original-evidence/` garde les octets des observations, de l'import et du
manifeste d'origine. Cette copie est **partielle** : son manifeste référence le paquet
initial complet, elle ne constitue pas un autre paquet autonome. Garder aussi le
paquet original. Le manifeste racine du rejeu couvre les deux côtés et le reçu.
Les bornes existantes (1 024 fichiers, 32 Mio/fichier, 128 Mio/paquet) restent en
vigueur, y compris pour la sortie doublant certaines pièces.

### Migration, cas contradictoires et limites

La migration est volontaire : conserver l'ancien exécutable/reçu de workflow 2,
créer une nouvelle sortie sous workflow 3, choisir explicitement le profil si
nécessaire. Ce n'est pas une migration normative des contrôles et cela ne remplace
aucun résultat historique. Pour comparer exactement le comportement de workflow 2,
rester sur son archive. Les nouveaux outils sont identifiés par leurs empreintes.

Le jeu synthétique [préparé avant l'implémentation](../tests/fixtures/replay-python-supervisor-v1.json)
contient 37 cas, SHA-256 `ffe3152329afd039c1a564281a116282145c03459a9073bdef93cc0e3e0464df`.
Il a été écrit après le premier échec de portabilité, pas avant sa découverte.
Il couvre changements de destination, version Node, sources, limites, types,
population et attribut « python », ainsi que versions fausses, ouvriers inconnus,
refus exacts et versions admises. Ce sont des cas de comparaison, pas 37 contrôles
SEO ni 37 observations indépendantes de navigateurs.

Un accord entre deux exécutions porte sur les entrées réellement rejouées. Il ne
prouve pas l'équivalence générale des versions de Python, Node, systèmes ou moteurs.
L'intégrité et la cohérence des versions déclarées n'authentifient pas l'environnement
historique, la sincérité des captures ou les revues. Aucune conclusion Google,
certification, nouvelle conformité ou correction du site n'en découle.

## English

Workflow **3** changes comparison only. Draft.18, interpreter 18 and adapter 19
remain unchanged. Keep workflow 2 archives/receipts for their historical behavior;
never overwrite an old bundle. The new workflow can compare an older bundle only
when its adapter/interpreter sources match exactly. Use a new output directory.

The commands above select `exact` by default or explicitly `python-supervisor-v1`.
Exact comparison is typed JSON equality: object key order and serialization
whitespace do not matter; list order does. Unlike the old Python equality, boolean,
integer and floating-point types are distinct. Atomic results, control results,
gate, protocol and tool identities must still match.

The optional profile permits only Python supervisor version strings at the closed
reader/rule/worker slots in the table above, with `normative_effect: none`. Each
string must match its own import runtime record; the replay record is also checked
against the executing runtime. Supported exceptions require stable CPython 3.9+
within Python 3, using three numeric components. This is not a two-version allowlist
or qualification of every supported environment. No exception applies to unknown
implementations, missing or incoherent versions. Exact equality can still succeed.

No recursive removal of runtime/python keys occurs. Every other value, including
unknown fields, Node/parser versions, source hashes, budgets, decoding, URLs,
attributes, offsets, populations, assumptions, reasons and outcomes remains exact.
Added/missing/type-changed fields or differing observation file sets fail. An
identical refusal can replay without establishing a successful SEO control.

`same_source_observations` always reports exact equality. `comparison_profile` and
`source_observations_match` name and report the selected comparison. Per-file
`source_observation_comparisons` retain JSON Pointers and typed digests for differences,
plus exact before/after values for admitted version exceptions. More than 1,000
differences per file is incomplete and fails closed. One-sided files are listed.
Both declared runtimes are retained. Current Unicode data version is observed;
historical Unicode remains null, not reconstructed. `replayed` combines the selected
comparison with unchanged atomic/control/gate checks. Thus exit 0 can coexist with
exact equality false only under the explicit profile, including NC/NT/NO_GO outcomes.

Exit 64 covers invalid inputs, incompatible tools or mismatch. Calculated mismatches
retain outputs within package bounds; reading, integrity and budget failures prevent
delivery. `bundle/` contains the new calculation. `original-evidence/` preserves raw
original observation/import/manifest bytes but is a **partial** copy, not a standalone
bundle: its manifest refers to the complete original bundle. Retain that original
too. The root replay manifest covers both sides and receipt. Existing limits of
1,024 files, 32 MiB/file and 128 MiB/package still apply, including duplicated output.

Migration is explicit and non-normative: retain workflow 2, create a separate workflow
3 result and choose the exception if needed. The 37 synthetic cases linked above were
frozen before implementation, after discovering the portability mismatch. They cover
destinations, Node, sources, limits, types, extra/missing facts, misleading python
attributes, false versions and unknown readers/workers. These are comparator tests,
not SEO controls or independent browser observations. Their hash is printed above.

Matching two executions proves only agreement on the replayed inputs, not general
cross-runtime/platform/engine equivalence. Version bindings and integrity do not
authenticate historical environments, capture truth or reviews. No Google outcome,
certification, new control conformity or site repair is inferred.
