# Lecteur robots partagé candidat / Candidate shared robots reader

## Français

Cette étape prépare TS04 et la dépendance TS07-A02. Elle **ne modifie pas** le
protocole draft.8, son lecteur actif ou ses verdicts. `experiments/robots_policy.py`
version 1 émet des observations `allow`, `disallow` ou `unknown`, jamais C/NC/NA/NT.
Une politique autorisée ne suffit pas à valider TS04 : elle doit être confrontée
à l'intention, aux ressources nécessaires et aux autres preuves. L'intégration
normative exigera une nouvelle candidate, des règles FR/EN et une migration.

Deux profils doivent être choisis explicitement :

- `rfc9309-bounded-v1` : modèle borné de lecture du corps. Groupes exacts du
  product token fusionnés, repli sur `*` seulement en l'absence de groupe exact,
  chemins sensibles à la casse, `*` et `$` final, plus longue chaîne normalisée,
  Allow à égalité. Les champs inconnus et lignes invalides sont consignés comme
  ignorés selon ce modèle ; ce résultat n'est pas une politique Google.
- `google-documented-core-v1` : sous-ensemble conservateur, sans reproduction
  intégrale du parseur Google. Un groupe mal formé, champ inconnu (sauf Sitemap,
  Crawl-delay et Host), ligne sans séparateur, règle sans `/`, normalisation de
  caractères non réservés encodés, cas particulier Allow `/index.htm…` ou requête
  `/robots.txt` restent inconnus. Il n'y a pas de repli silencieux sur le profil RFC.

L'algorithme renvoie les groupes retenus et lignes gagnantes, leur règle originale,
forme normalisée et spécificité. La spécificité est la longueur ASCII de la chaîne
normalisée, caractères `*` et `$` inclus. Les caractères UTF-8 sont encodés ; les
échappements hexadécimaux sont uniformisés sans décoder les séparateurs réservés.
Dans le profil RFC, les caractères non réservés encodés sont décodés. `%2A` ne
devient pas un joker. Le product token est distinct du User-Agent HTTP déclaré.
Ces choix sont explicites ; aucune conformité complète RFC ou équivalence au
code/serveur Google n'est revendiquée.

L'enveloppe HTTP exige origine et cible de même origine (schéma, hôte et port),
contexte et intention antérieurs, requête GET attribuable et réponse complète.
Elle conserve l'origine initiale même si robots.txt redirige vers un autre hôte.
Elle utilise le décodeur HTTP existant, sans requête réseau. Au plus cinq
redirections complètes sont interprétées ; limite, boucle ou chaîne inachevée
restent inconnues ici. Ce plafond local n'est pas présenté comme une limite
exacte de Google.

Le profil Google interprète les 4xx sauf 429 comme une absence de restrictions
dans la réponse observée ; cela ne démontre pas le cache réellement utilisé.
Un 200 exige un corps UTF-8 text/plain complet ; un 204 exige un corps vide.
Les autres états, dont 429, 5xx, erreurs réseau, HTML et historique de cache absent,
restent inconnus. Le profil RFC n'infère pas une politique HTTP depuis un 4xx.
Une absence volontaire documentée peut être compatible avec TS04 : aucun 200
universel n'est imposé. Aucun corps HTML n'est implicitement déclaré sans règles.

Bornes : 500 Kio de corps, 20 000 lignes, 5 000 règles, 8 192 caractères d'URL ou
de chemin normalisé et un million d'étapes de correspondance. Un dépassement
donne `unknown`, sans tronquer puis conclure. Le refus est plus conservateur que
le comportement complet d'un moteur. Le matching utilise une boucle bornée,
sans expression régulière construite depuis le fichier.

64 cas ont été figés avant le code dans `robots-policy-v1-cases.json`, puis leurs
64 attentes du profil Google et 18 états HTTP dans `robots-profiles-v1-cases.json`.
Les empreintes sont conservées à côté. Les tests comparent aussi le matching à
une énumération indépendante exhaustive sur un petit langage ; ce n'est pas une
comparaison avec une exécution de Googlebot.

## Laboratoire reproductible

```sh
python3 experiments/robots_laboratory.py --output /tmp/tsep-robots-new-lab
```

Le dossier doit être nouveau. Le serveur éphémère écoute uniquement 127.0.0.1 ;
18 requêtes réelles collectent des **scénarios synthétiques** : interdiction de
préproduction, CSS nécessaire interdit, noindex associé à Disallow, témoin correct.
Chaque défaut est corrigé puis recapturé. Plan préalable, octets HTTP et empreintes,
observations, lignes gagnantes et journal sont conservés. Le serveur est fermé à
la fin. Les statuts des ressources sont effectivement décodés ; un 200 n'est pas
utilisé comme preuve d'autorisation d'exploration.

Le laboratoire version 2 utilise réellement le User-Agent `googlebot`, exigé
littéralement par l'interpréteur actif. Le premier essai local, avec `Googlebot`,
a conservé A01 indéterminé ; ses captures ne sont pas réécrites. Cette limite
de casse de l'interpréteur actif reste à corriger explicitement lors de son
évolution ; elle n'est pas attribuée au moteur.

Le cas noindex est également évalué par les règles TS07-A01/A02 **actives** :
A01 est compatible avec l'intention d'exclusion, A02 échoue avant correction ;
après, A02 reste indéterminé faute de revue humaine fournie. Aucun avis humain
n'est inventé et TS07-A03 n'est pas évalué. L'exemple n'est pas un audit Edikka.

Pour réinterpréter un fichier collecté, sans réseau et vers un nouveau fichier :

```sh
python3 experiments/robots_policy.py /tmp/tsep-robots-new-lab/preproduction/before/input-1.json --output /tmp/robots-observation-new.json
```

L'entrée porte `profile`, `origin`, `target`, `product_token`,
`request_user_agent`, `declared_at`, `observed_at`, `context` (network, bounds,
tool, tool_version) et `http` (échanges au format brut ou binaire captures v2).
La sortie CLI conserve l'empreinte de l'entrée et des sources chargées. Un exit 0
signifie sortie produite, y compris `unknown`, pas réussite d'un contrôle.

## English

Version 1 is an unapplied shared-reader candidate for TS04 and TS07-A02. Draft.8
and its active interpreter remain unchanged. Outputs are experimental observations,
not control statuses. Normative integration requires a new bilingual candidate
and explicit migration. Policy permission alone cannot establish TS04 conformity.

Select either the bounded RFC body model or the conservative documented Google
subset explicitly. Both retain selected groups, winning source lines and original
patterns. RFC-specific normalizations and Google parser tolerances must not be
silently conflated. The Google subset refuses ambiguous agent syntax, unknown
records except the three named ignored extensions, malformed lines, non-rooted
rules, unreserved percent decoding, index.htm Allow tolerance and implicit robots
self-allowance. Full RFC compliance and Google equivalence are not claimed.

The HTTP wrapper verifies the supplied request, initial origin, target, context,
dates and complete trace. Redirected robots content belongs to the initial origin.
Up to five redirects are supported; incomplete/excessive traces stay unknown.
Google-profile 4xx except 429 describe no restrictions in the observed response;
200 requires complete UTF-8 text/plain, 204 an empty body. Other statuses, HTML,
network failures and unresolved cache-dependent outcomes stay unknown. The RFC
profile has no automatic HTTP failure policy. No actual crawler cache is observed.

Bounds and refusal behavior are specified above. The two prefrozen fixtures cover
64 body cases under each profile and 18 HTTP states. A separate small-language
enumeration checks matching without sharing its algorithm. This is not a Google
execution comparison. The portable loopback laboratory creates new evidence only,
performs 18 real local requests for four synthetic scenarios, retains exact bytes,
recaptures corrections and demonstrates why HTTP 200 alone is insufficient.
The noindex case preserves missing human review after correction. No Edikka
assessment, real engine visit, ranking gain or indexing outcome is inferred.
Laboratory version 2 actually sends lowercase `googlebot`, as required literally
by the active TS07 interpreter. The first local run sent `Googlebot` and retained
A01 inconclusive; its evidence is preserved. This active-interpreter case limit
must be addressed explicitly later and is not attributed to Google.
