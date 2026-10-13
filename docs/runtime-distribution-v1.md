# Closed runtime distribution 1 / Distribution d'exécution fermée 1

## English

This non-normative packaging tool creates a new, explicitly reduced distribution
of either of two historical imports: draft.31 at
`640d7f18621e7b518c5a20cf144fed7a8107adb5`, or draft.33 at
`1fdc0cb909e276c457d7dfc68bb42fc2d6e252f6`. It neither updates their tools nor
changes their native report contracts. The version of this transport is `1`;
protocol/interpreter/adapter/replay identities remain historical and exact.

`distribution/runtime-profiles.json` contains two closed, fingerprinted source
inventories. One named file is excluded from each runtime tree:
`provenance/source-canonical-signal-correction.json`, SHA-256
`53811612988d5c6b96c9203ee5a8246b368beb236edfe015eb55b7f8b435c910`.
This is a non-executable synthetic diagnostic containing a personal executable
location. Its original bytes remain in the complete historical source archives.
The distribution records its name, hash and French/English omission reason.
No other file may be omitted, changed or added. Runtime code, normative data,
fixtures, licenses, reports and observations retained in the tree stay byte-exact.
This is not the smallest possible runtime: the narrowly scoped exclusion preserves
all other historical files to avoid silently changing dependency assumptions.

The complete-source map remains in the profile definition. The draft.31 import
has 709 files and no SHA256SUMS; its runtime retains 708. The draft.33 import has
752 files, including its original SHA256SUMS; its runtime retains 751. The original
release-files.json and SHA256SUMS, when present, are historical source references,
not inventories of the reduced tree. Do not claim that full-source `maintain.py
check`, `maintain.py build` or `scripts/verify.py` passed on this reduced tree.
Those commands require the complete original source population.

Build from an exact complete historical import, with no extra files or symlinks:

```sh
python3 -I -B scripts/runtime_distribution.py build \
  --profile draft31-640d7f18621e --source /path/to/full-import \
  --output /path/outside-source/new-runtime.zip
```

For draft.33 select `draft33-1fdc0cb909e2`. There is no arbitrary exclusion option.
The output must be new and outside the source tree. The builder reads a bounded,
exact file population before creating the archive; it never writes in that source.
File and directory aliases, extra files, changed/missing originals and altered
profile definitions are refused. The byte and file-count limits are transport
bounds, not changes to the normative evidence schema.

The ZIP contains `runtime/`, the closed profile definitions, the verifier,
`RUNTIME-DISTRIBUTION.txt` and `distribution.json`. The descriptor has separate
original-source and retained-runtime inventory identities, the exact omission,
and a complete included-file map. The verifier requires its exact deterministic
descriptor and checks every included file. Reintroducing even the authentic excluded
file is refused. The original complete archive remains a separate private artifact.

After checking the archive hash against a trusted delivery, extract and run:

```sh
python3 -I -B runtime_distribution.py check --root .
```

An exit-zero integrity result is not a control verdict or a successful native
replay. Execute the relevant native tools from `runtime/` with the historical
versions and replay anchor. Missing evidence stays NT; technical refusal does not
produce C/NA. A new evaluation remains distinct from historical replay. Do not
rewrite a native report to add distribution identity: retain the separate transport
receipt alongside it. A consumer must explicitly import this transport version,
verify its closed profile and update its export envelope and reader together.
Do not silently weaken a legacy complete-tree lock or edit an application vendor.
Legacy native reports remain replayable with their exact historical runtime;
legacy portable exports containing the original diagnostic stay private and do
not become qualified simply because a new profile exists.

Qualification must compare native conformance and original synthetic replays on
the exact extracted profile, not just verify hashes. Report the actual optional
runtime profile used (including absent optional Node), observed results and limits.
The source implementation still requires its own full `scripts/verify.py` and
reproducible complete-source archive before integration. Tests of reduced runtime
execution and full-source delivery are different evidence.

Archive byte reproducibility is qualified in the recorded local Python/zlib environment,
not across arbitrary compression-library versions or machines. Invoke the verifier
with Python; executable permission bits are not required.

A bounded personal-path scan does not establish absence of every secret. A
self-consistent archive does not authenticate its author, reviewer or observations.
An attacker replacing the verifier, its definitions and the delivery digest is
outside this internal consistency boundary. No Google access, Edikka review,
publication, normative upgrade or certification follows from this packaging tool.

## Français

Cet outil d'empaquetage non normatif crée une distribution réduite explicite de
l'un des deux imports historiques indiqués ci-dessus. La version du transport
est `1` ; outils, règles, contrats de rapports et versions historiques restent
inchangés. Les deux inventaires source sont fermés et liés par empreinte au
vérificateur. Le seul fichier exclu est le diagnostic synthétique non exécutable
nommé ci-dessus, car il contient un chemin personnel. Nom, empreinte et motif
bilingue restent dans le profil. L'original intégral est conservé dans les archives
sources historiques ; aucun rapport, échec, observation ou original n'est réécrit.
Tous les autres fichiers gardent leurs octets exacts, y compris code, données,
licences et jeux de cas. Ce choix limite le changement à la pièce identifiée ;
ce n'est pas une distribution minimale générale.

Le profil draft.31 passe de 709 fichiers à 708 et ne possédait pas SHA256SUMS.
Le profil draft.33 passe de 752 à 751, avec SHA256SUMS original conservé. L'inventaire
source complet du profil, release-files.json et SHA256SUMS éventuel décrivent
l'origine, pas l'arbre réduit. Les commandes de maintenance/vérification de source
complète ne s'appliquent pas à cet arbre ; ne pas en déclarer un succès fictif.
Les commandes ci-dessus construisent un ZIP neuf, hors de la source, puis vérifient
sa distribution extraite. Le constructeur exige l'import complet exact, refuse
ajouts, absences, modifications, alias et liens symboliques, et ne modifie pas
la source. Aucun filtre libre ou second fichier exclu n'est accepté.

Le descripteur sépare identité source et identité de l'inventaire réellement
fourni. Le vérificateur contrôle tous les fichiers et son descripteur déterministe.
Réintroduire le fichier exclu, même authentique, provoque un refus. L'archive source
complète reste une pièce privée distincte. Comparer l'empreinte du ZIP à une
livraison de confiance avant d'exécuter le code qu'il contient.

Le succès d'intégrité n'est ni un verdict TSEP ni un rejeu natif. Exécuter ensuite
les outils du répertoire runtime avec leurs versions et l'ancre historique du
rejeu. Une preuve absente reste NT ; un refus technique ne produit pas C/NA.
Une nouvelle évaluation reste distincte. L'identité du transport figure dans un
reçu séparé, jamais ajoutée rétroactivement aux anciens rapports natifs.
Le consommateur importe explicitement ce transport et adapte conjointement son
enveloppe d'export et son lecteur ; pas d'affaiblissement silencieux d'un verrou
historique ni d'édition du vendor applicatif. Les anciens exports contenant le
diagnostic restent privés : l'existence d'un nouveau profil ne les qualifie pas.

La recette doit exécuter les cas natifs et rejouer les paquets synthétiques depuis
les octets extraits, en indiquant le profil réellement utilisé, dont l'éventuelle
absence du runtime Node facultatif. Les empreintes seules ne suffisent pas. Le
nouveau code de distribution exige aussi sa propre vérification complète dans le
dépôt source et une archive reconstruite identique avant intégration. Ces deux
recettes ont des objets distincts.

La reproductibilité octet à octet du ZIP est qualifiée dans l'environnement
Python/zlib local consigné, sans garantie pour d'autres bibliothèques ou machines.
Le lancement par Python ne dépend pas des bits de permission d'exécution.

Un balayage borné de chemins personnels n'est pas un audit universel des secrets.
Les empreintes internes ne prouvent ni auteur, ni revue humaine, ni vérité des
observations. Le remplacement du vérificateur et de toute sa chaîne de confiance
est hors de cette vérification de cohérence. Aucun accès Google, jugement Edikka,
publication, changement normatif ou certification n'est déduit de ce transport.
