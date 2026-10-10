# TS04 et TS07 — politique robots partagée / Shared robots policy

## Français

Draft.13 ajoute le profil préalable facultatif `google-robotstxt-fields-v2`.
Le lecteur 3 conserve les champs d'un registre fermé issu de `google/robotstxt`
et `sitemap`, sans leur attribuer d'effet sur les règles d'accès ni les groupes.
Les noms inconnus restent indéterminés ; les profils antérieurs sont inchangés.
Les valeurs relevées ne constituent pas une évaluation TS42 ou de préférences
d'usage. Liste exacte, sources, conservation et migration : [draft.13](migration-draft.13.md).

Draft.12 étend à TS04 le champ préalable `directive_crawler=googlebot` de TS07.
Il conserve le client HTTP exact dans `crawler`, exige un `robots_policy` explicite
avec produit Googlebot concordant, et limite la conclusion à la représentation
reçue par ce client. Les refus HTTP de ressources sont qualifiés pour ce client,
sans conclure à un refus Googlebot. Champ absent : ancien comportement ; champ
invalide : aucune politique favorable par repli. [Migration](migration-draft.12.md).

Draft.9 ajoute TS04-A01 (politique contre intention) et TS04-A02 (accès aux
ressources nécessaires avec revue fournie). Les deux sont semiAuto. Une réussite
de la politique seule ne valide pas tout TS04 ; une contradiction connue n'est
pas effacée par une autre pièce manquante. Le lecteur `conformance/robots.py` est
commun à TS04 et TS07-A02, via `conformance/robots_control.py`.

### Plan préalable d'une origine

La cible est l'URL racine de l'origine, avec `observed_at` et `context` (network,
bounds, tool, tool_version). L'intention porte `declared_at`, le User-Agent HTTP
exact `crawler`, puis :

```json
{
  "robots_policy": {
    "profile": "google-documented-core-v1",
    "product_token": "Googlebot"
  },
  "robots_plan": {
    "origin": "https://example.com/",
    "required_resources_basis": "Page et feuille CSS nécessaires dans ce périmètre",
    "resources": [
      {
        "url": "https://example.com/page",
        "expected": "allow",
        "required": true,
        "expected_final_url": "https://example.com/page",
        "terminal_statuses": [200]
      },
      {
        "url": "https://example.com/private",
        "expected": "disallow",
        "required": false
      }
    ]
  }
}
```

Le plan comporte 1 à 100 URL uniques de la même origine. Une ressource nécessaire
doit être attendue autorisée, avec destination finale de même origine et statuts
2xx explicitement admis. Déclarer les ressources réellement nécessaires ; le
logiciel ne prouve pas l'exhaustivité de cet inventaire. Séparer les rapports pour
des profils/contextes incompatibles ; le profil n'est jamais choisi après mesure
selon le verdict souhaité. Les empreintes ne prouvent pas la date réelle du plan.

`robots` contient `observed_at` et `http`, une trace brute ou binaire captures v2
commençant à `/robots.txt` de l'origine. Les réponses nécessaires sont dans
`documents`, chacune avec `url`, `observed_at` et `http`. Toutes ces captures sont
datées entre déclaration et `target.observed_at`. Le robot ciblé et le client HTTP
sont distingués ; le nom du client ne prouve aucune visite Googlebot authentique.

A01 compare chaque autorisation/interdiction attendue à la politique observée et
conserve profil, chemin et lignes gagnantes dans son motif. A02 vérifie aussi tous
les sauts observés d'une ressource, sa destination, son statut final et la revue de
la réponse. Les collectes ou redirections incomplètes restent indéterminées. Une
interdiction robots connue ou une réponse finale contradictoire reste un échec
même si une autre preuve ou revue manque. Un détour interorigine non couvert ne
donne pas pass. Le HTTP reste borné aux capacités du décodeur commun.

### Revue des ressources

Chaque document nécessaire contient `access_review` : `reviewer`, `observed_at`,
`outcome` (`no-obstacle`, `obstacle` ou `inconclusive`), `reason`, `assistance`,
`provenance` (`human`, `human-assisted` ou `synthetic-exercise`) et `source_sha256`.
La date est postérieure ou égale à la capture examinée. L'empreinte lie le JSON
`{intent, context, url, observed_at, http}` du document et de sa cible : UTF-8,
clés triées, ensure_ascii=False, séparateurs `(',', ':')`, sans saut final.
Une revue périmée ne réussit pas. Le nom, la sincérité et la suffisance du jugement
ne sont pas authentifiés. Un exercice synthétique ne peut être importé comme réel.

Le parcours `adapters/review.py` version 3 prépare les questions TS04-A02, sans
préremplir les réponses, puis importe les décisions fournies dans un nouveau paquet.
Il conserve les réponses originales, pièces examinées et historique. Une revue
positive n'efface ni un blocage robots ni une limite du lecteur. Voir aussi le
[parcours de revue et rejeu](review-and-replay.md).

Si aucune ressource n'est nécessaire, A02 n'accepte une exemption qu'avec
`robots_plan.no_required_resources` : `reviewer`, `reason`, `observed_at` et
`provenance`, issus d'une revue d'inventaire datée au plus tard à la déclaration.
Une liste vide ou une collecte manquante ne remplace pas cette preuve. A01 doit
quand même évaluer la matrice déclarée.

### Profils et limites conservées

Les profils `rfc9309-bounded-v1` et `google-documented-core-v1` conservent les choix
et bornes du [lecteur candidat](robots-policy-experiment.md) : groupes, jokers,
priorités et encodages ; le sous-ensemble Google refuse les tolérances ambiguës.
Le profil RFC ne devient pas une simulation de Google. Le profil Google traite
les 4xx sauf 429 comme absence de restriction dans la réponse observée ; le cache
réel reste inconnu. 429, erreurs serveur/réseau et autres cas non pris en charge
restent indéterminés. Le HTML ne donne pas une autorisation implicite.

Un 200 robots exige UTF-8 text/plain complet ; Google 204 exige un corps vide.
Limites : cinq redirections robots, 500 Kio de corps sans troncature implicite,
20 000 lignes, 5 000 règles, 8 192 caractères d'URL/chemin normalisé et un million
d'étapes de matching. Tout dépassement reste inconnu. La spécificité est la
longueur ASCII du motif normalisé, `*` et `$` compris ; Allow gagne à égalité.
Une redirection robots conserve l'origine initiale de la politique.

TS07 accepte le même `intent.robots_policy` explicite, déclaré avant sa capture
robots. Les anciennes entrées sans ce champ gardent le profil fixe
`legacy-exact-v1` : règles simples exactes, HTTP 200 text/plain, sans jokers ni
chemins encodés. Ce profil historique est plus limité et n'est pas un repli depuis
un profil explicite refusé. Une nouvelle évaluation ne doit pas ajouter une date
ou un plan rétroactivement. Un refus HTTP 401/403 attribuable est désormais retenu
même sans robots ; les autres règles TS07 ne sont pas implicitement complétées.

45 cas synthétiques nouveaux ont été figés avant les implémentations concernées,
dans deux fixtures `robots-control-v1-*`. Les 254 cas antérieurs sont conservés.
Le laboratoire local reste synthétique, même quand les requêtes HTTP sont réelles.
Aucune réussite ne prouve l'indexation, le rendu du moteur ou une conformité d'Edikka.

## English

Draft.13 adds optional predeclared `google-robotstxt-fields-v2`. Reader 3 records
a closed registry from pinned `google/robotstxt` source plus sitemap, without
turning these fields into access rules or group boundaries. Unknown names remain
inconclusive; earlier profiles are unchanged. Recorded values are not a TS42 or
usage-preference assessment. See [registry, sources and migration](migration-draft.13.md).

Draft.12 extends TS07's prior `directive_crawler=googlebot` field to TS04. Keep
the exact HTTP client in `crawler`, require an explicit matching Googlebot product
profile and qualify results as interpretation of this client's representation.
Resource HTTP denials concern this client, without inferring Googlebot denial.
Absent field keeps legacy behavior; invalid values never fall back favorably.
See [migration](migration-draft.12.md).

Draft.9 adds semiAuto TS04-A01 (declared policy matrix) and TS04-A02 (required
resource access with supplied review). TS04 and TS07-A02 share one reader.
Declare a root origin target, observation interval, collection context, exact HTTP
User-Agent, explicit policy profile/product token and 1–100 unique same-origin
resource expectations before capture. Required resources must be expected allowed,
with explicit same-origin final URL and permitted 2xx statuses. Inventory adequacy
is declared, not proven by the software. Never choose a favorable profile after
observation; split incompatible campaign contexts.

Supply dated robots and document HTTP traces using captures v1/v2. A01 retains
per-path profile and winning lines. A02 also checks each observed redirect hop,
final destination/status and bound resource review. A known policy or HTTP
contradiction survives other missing evidence. Incomplete or unsupported cross-
origin access remains inconclusive. No test-client identity authenticates Googlebot.

Resource review fields, canonical JSON digest and dates are specified above.
The workflow version 2 prepares blank TS04-A02 questions and imports supplied
responses into a new package with preserved history. Synthetic reviews cannot be
imported as public/restricted evidence. Reviewer identity and truth are not
authenticated. A positive review never erases an observed contradiction.
No required resource needs a supplied, reasoned inventory review predating intent;
an empty list or absent capture alone cannot establish the A02 exemption.

The named RFC/Google profiles retain documented bounds and refusals. They do not
claim complete standards compliance or engine equivalence. Actual crawler cache,
rendering, access, ingestion and indexing remain unobserved. Legacy TS07 inputs
without a profile keep the fixed legacy-exact-v1 semantics, not automatic selection
between profiles. An attributable HTTP 401/403 now remains fail without robots.
The 45 prefrozen additions coexist with all 254 prior raw cases. Preserve historical
tools/reports and follow [draft.9 migration](migration-draft.9.md).
