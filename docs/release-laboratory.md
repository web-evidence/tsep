# Controlled release laboratory / Laboratoire de déploiement contrôlé — 1

## Français

Ce laboratoire rend TS41 concret : seize GET anonymes sur une origine numérique
`127.0.0.1`, seize vrais processus Python et des opérations observées sur des
fichiers dans un nouveau dossier isolé. Les pages, défauts injectés, revue de
représentativité et revues finales sont **fictifs**. Aucun déploiement de production,
accès Googlebot, audit Edikka ou avis humain n’est déduit.

La recette est figée avant le programme dans
`tests/fixtures/release-laboratory-v1.json` et son empreinte associée. Le programme
enregistre avant la fenêtre les URL, paquets candidats, matrice, commande/version,
environnement et politique. Les invariants sous-jacents sont seulement TS01-A01
(réponse complète en 200) et TS07-A01 (directives source cohérentes avec l’intention).
Ils ne valent pas réussite des contrôles TS01 ou TS07 entiers.

| Scénario prévu | Observation attendue | Verdict TS41 attendu |
| --- | --- | --- |
| Déploiement sain | Test négatif bloqué, précontrôle réussi, copie du candidat puis contrôle après application réussi | C |
| `noindex` bloqué | Processus en échec, action explicite de blocage, fichier actif inchangé | C, défaut SEO conservé |
| Réponse incomplète bloquée | EOF avant Content-Length, résultat inconclusif, code 2 et blocage | C, inconnue SEO conservée |
| Inconnue masquée | Sorties inconclusives, code 0 fautif, application et acceptation observées | NC |
| Test rouge ignoré | Code 1 conservé, superviseur fautif appliquant quand même le candidat | NC |
| Défaut après application suspendu | Précontrôle réussi, défaut `noindex` prévu dans la variante activée, code 1 et suspension explicite | C, défaut SEO conservé |

Les seize réponses annoncent 200, mais trois sont volontairement incomplètes.
Un code HTTP reçu ne suffit donc ni à qualifier une réponse complète ni à décider
du déploiement. Le sixième paquet contient un défaut fictif dépendant de la phase,
déclaré dans la recette ; ce n’est pas une découverte fortuite ni une preuve
causale applicable à un site réel. Les phases pre/post examinent le même paquet
candidat. L’ancien paquet n’est qu’un contexte préalable conservé.

Le serveur lit les octets du paquet préparé avant application, puis ceux du fichier
actif après une copie atomique. Chaque action conserve les octets/empreintes
avant et après, son début/sa fin et le lien à l’événement. Un blocage est une
action explicite du superviseur avec état inchangé, pas une conclusion tirée
de l’absence d’une ligne. Ces fichiers locaux ne sont pas un service CI distant.

### Exécution et rejeu

```sh
python3 examples/release_laboratory.py run --output /tmp/tsep-release-run
python3 examples/release_laboratory.py replay /tmp/tsep-release-run --output /tmp/tsep-release-replay.json
```

Choisir de nouveaux chemins. Le serveur ne résout aucun nom, n’utilise ni proxy,
cookie, authentification ni destination externe. Par GET : trois secondes et
16 384 octets ; par enfant : six secondes. La fenêtre complète fixée avant les
observations dure quinze secondes. Une sortie de processus est observée, jamais
reconstituée à partir du seul verdict. Les commandes du laboratoire sont
construites par son code ; aucune commande issue d’une preuve n’est exécutée.

Le dossier conserve recette, plans, paquets, requêtes/réponses brutes, journal du
serveur, entrées natives, stdout/stderr, PID et codes processus, déclencheurs,
actions et états de fichiers. Les rapports restent scellés séparément. Une
interruption garde ses pièces partielles et `failure.json`, sans manifeste de
réussite. Le rejeu vérifie ces liaisons, rejoue les bundles hors réseau et ne
lance aucun processus ni aucune application d’artefact. Les fichiers supplémentaires
et liens symboliques sont refusés ; modifier toutes les empreintes ne rend pas
cohérents un autre corps HTTP, une autre sortie ou une autre action.

Les chemins d’interpréteur et du programme consignés sont ceux de l’exécution
observée, pas des commandes à réutiliser automatiquement. Rejouer avec les outils
exacts de l’archive ; ces chemins historiques ne sont pas des dépendances du
rejeu. Les horloges/PID/fichiers et empreintes n’authentifient pas une machine tierce.
Les rapports HTML doivent être générés **hors des bundles scellés**.

## English

This optional TS41 laboratory performs sixteen anonymous numeric-loopback GETs,
sixteen actual Python child processes and observed sandbox file operations. Pages,
faults and scope/final reviews are authored. No production deployment, real CI,
human approval, Edikka assessment or Googlebot access is established.

The recipe and checksum were frozen before implementation. Prior registration
retains URLs, candidate packages, matrix, command/version, environment and strict
policy. Only TS01-A01 and TS07-A01 are native invariants; their atomic outcomes
do not establish either whole control. Six expected scenarios are: clean cycle C;
noindex blocked C; incomplete response blocked C; unknown masked by exit 0 NC;
red test ignored NC; post-application noindex explicitly held C. SEO defects and
unknowns remain visible beside a conforming process.

All sixteen responses announce 200, but three deliberately end before their
declared Content-Length. The final scenario’s phase-dependent fault is preregistered,
not a fortuitous finding or a real-site causal claim. Pre/post assess the same
candidate package around application; the prior package is retained context only.
The server reads actual package bytes; atomic file replacement and explicit holds
retain before/after bytes, hashes, dates and event links. Absence of a log line
never establishes a block.

Use the commands above with new destinations. No DNS, proxy, cookies, authentication
or external destination. Bounds: three seconds/16,384 bytes per GET, six seconds
per child, a preregistered fifteen-second collection window. Child return codes
are observed, not inferred from outcomes. Only fixed laboratory code constructs
execution commands; supplied evidence commands are never run.

Keep registration, packages, raw HTTP/server logs, native inputs, stdout/stderr,
PID/exit receipts, triggers and file effects. Interrupted runs retain partial
evidence/failure.json without a success manifest. Offline replay checks these
bindings and sealed bundles without network, child execution or artifact application.
Extra files/symlinks are refused. Coherently rehashing altered evidence does not
make it agree with the fixed recipe/program. Recorded original executable paths
are observations, not replay dependencies. Use exact archived tools; hashes,
clocks and PIDs do not authenticate a third-party machine. Render HTML outside
the sealed bundles.
