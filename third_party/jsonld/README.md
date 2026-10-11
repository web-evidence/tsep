# Pinned optional JSON-LD processor / Processeur JSON-LD facultatif figé

`jsonld-9.0.0.tgz` is the **unmodified official npm archive** obtained from
[the npm registry](https://registry.npmjs.org/jsonld/-/jsonld-9.0.0.tgz) on
2026-10-11T09:19:10.421760+00:00. Its SHA-512 matched the registry metadata.
The SHA-256 is
`3628c8df4ceaf4da1f0b55dc7a006287dc4362ed78f6f7c85e83bd99b9328627`.

`packages.json` lists all 35 regular files and their fingerprints. `LICENSE` is
copied byte-for-byte from that archive (BSD-3-Clause). The upstream README and
package metadata remain inside the archive. No package-manager installation,
lifecycle scripts or external dependencies are run by the observer.

Only the unminified, self-contained `dist/jsonld.esm.js` member is executed,
copied without changing its bytes to temporary `jsonld.cjs` for Node loading.
Its SHA-256 is
`d4cfcc3ad466b29fdc49b8eb0c7ed2545830fae79c99526999db2c5d6e913f7f`.
The upstream member name does not determine the temporary module extension.
Its embedded copyright/license comments remain. The archive contains other
bundles which the observer does not execute. This reader selects Node 24 even
though the upstream package declares a wider supported range.

Before execution, the supervisor verifies the archive, complete member inventory,
member hashes, selected bundle and retained license. Context loading is replaced
by exact local supplied-context lookup. Runtime qualification is explicit and
separate from Python unit verification; see the [observation method](../../docs/jsonld-processing.md).

FR : archive npm officielle intégrale, non modifiée, empreintes vérifiées et licence
conservée. Seul le bundle non minifié indiqué est exécuté dans le processus Node 24
facultatif ; aucune installation ni exécution des scripts d'installation. Les
contextes restent des pièces locales fournies. Cette inclusion ne constitue ni
une certification du processeur ni une validation complète de JSON-LD ou TS31–33.
