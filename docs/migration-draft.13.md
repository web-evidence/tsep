# Migration draft.13 — champs robots hors portée accès

## Français

Draft.13 ajoute le profil facultatif `google-robotstxt-fields-v2` pour TS04 et
TS07-A02. Le lecteur partagé passe à 3, l'interpréteur à 13, l'adaptateur de
captures à 14 et la CLI d'observation à 3. Le format de rapport, les 44 identités
TS01–TS44 et les treize règles restent conservés.

La documentation Google fonde la règle de regroupement : les champs autres que
`user-agent`, `allow` et `disallow` ne délimitent pas les groupes. La liste fermée
ci-dessous provient séparément du fichier de reporting de `google/robotstxt`,
commit `22b355ff855419e6a3ff8ff09c0ad7fdb17116f9`. Ce n'est pas une liste publiée
par Google dans sa documentation de syntaxe. Sources datées et empreintes :
[provenance](../provenance/robots-fields-v2.json).

Le nouveau profil relève puis ignore, pour la seule interprétation de l'accès :
`clean-param`, `content-signal`, `content-usage`, `crawl-delay`, `domain`, `host`,
`noarchive`, `nofollow`, `noindex`, `request-rate`, `revisit-after`, `visit-time`,
ainsi que `sitemap`. Les noms correspondent exactement, sans distinction de casse
et après retrait des espaces ASCII autour du champ. `content-signals`,
`contentsignal`, fautes de directives et autres champs restent hors couverture.

Ignorer ces champs ne réinitialise ni les agents ni les règles. Leur valeur ne
crée aucune permission ou interdiction d'exploration. Le lecteur conserve numéro,
nom normalisé, valeur et ligne originale ; les captures restent inchangées.
Le motif des règles TS04/TS07 affiche le registre et un aperçu d'au plus seize
champs, limité à 160 caractères par valeur. Toute troncature et tout nombre de
champs supplémentaires sont explicites ; les valeurs intégrales restent dans la
réponse robots retenue et la sortie du lecteur. Le rapport HTML échappe le texte.

Ce relevé n'évalue pas les préférences d'usage, l'entraînement IA ou TS42. Une ligne
`noindex` dans robots.txt ne devient pas une directive d'indexation HTML/HTTP.
Le code source Google comporte aussi des tolérances sur des fautes/préfixes de
directives. Elles ne sont pas reproduites ici : les cas inconnus restent
indéterminés. Ce sous-ensemble ne revendique pas une équivalence avec Googlebot.

Choisir ce profil explicitement dans `intent.robots_policy.profile` **avant** la
capture, avec les autres déclarations TS04/TS07 requises. Aucun choix automatique,
aucun repli depuis un profil refusé. `google-documented-core-v1`,
`rfc9309-bounded-v1` et le lecteur TS07 historique restent inchangés.
Une relecture rétrospective doit être nommée comme telle ; ne jamais ajouter cette
intention aux anciennes captures en prétendant qu'elle était préalable.

Les bornes, erreurs HTTP, limites de syntaxe, qualification du client et exigences
de revue humaine sont conservées. Une politique compatible sans revue ne suffit
pas à établir C. Les 409 cas antérieurs gardent leurs entrées et résultats. Les
44 cas de lecture et 18 cas de contrôle ajoutés sont synthétiques, figés avant
implémentation ; ils ne sont ni un audit réel ni une validation indépendante.

## English

Draft.13 adds optional `google-robotstxt-fields-v2` for TS04 and TS07-A02. Shared
reader 3, interpreter 13, capture adapter 14 and observation CLI 3 retain report
format, all 44 control identities and thirteen rules.

Google's documentation supports ignoring ancillary fields during access-rule
grouping. Separately, the closed list comes from the reporting file in
`google/robotstxt` at commit `22b355ff855419e6a3ff8ff09c0ad7fdb17116f9`; it is not
a documentation-published list. See the dated [source record](../provenance/robots-fields-v2.json).

The new profile records the twelve named unused fields listed above, plus sitemap,
without evaluating them as access rules. Names must match exactly after ASCII
space trimming and case folding. Near names, directive typos and other fields
remain unsupported. Ignored fields never split/reset groups or create permissions.
The reader retains line number, normalized field, value and original line. Rule
reasons name the registry and show at most sixteen fields with 160 characters per
value, explicitly counting truncation and omitted fields. Complete values remain
in the retained robots response and reader output. HTML escapes displayed text.

Usage preferences, AI training and TS42 are not assessed. A robots noindex field
is not converted to a page indexing directive. Google source tolerates additional
typos/prefixes not modeled here, so unknown cases remain inconclusive. This bounded
profile does not claim Googlebot equivalence or an actual engine observation.

Declare the profile before new captures, alongside all existing required fields.
No automatic selection or fallback. Prior Google v1, bounded RFC and legacy TS07
behaviors stay unchanged; retain their tools and reports. Retrospective analysis
must be labeled separately and cannot claim a prior new-profile declaration.
All bounds, HTTP handling, client qualification and human review requirements
remain. Compatible policy alone cannot establish C. All 409 previous cases retain
their inputs and computed results. Forty-four body cases and eighteen control
cases were authored before implementation; they are synthetic, not site assessment
or independent validation.
