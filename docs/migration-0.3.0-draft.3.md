# Migration 0.3.0-draft.2 → 0.3.0-draft.3

## Français

Préversion non publiée, issue du lot URL vérifié d95be6c. Ajoute TS21-A01/A02,
TS22-A01/A02, TS40-A01/A02 :38 contrôles à règles,85 règles atomiques. Les79 règles
précédentes conservent leurs objets et versions ; les contrôles TS01–TS44 et leur
provenance restent permanents. RC1 et le lot TS12–TS18 restent conservés séparément.

Créer un nouveau dossier prospectif selon [le contrat](indexing-locale-evidence.md).
Conserver les résultats antérieurs ; aucun réétiquetage automatique des C. TS21
qualifie une documentation de diagnostic sur familles sélectionnées avec pièces
API/logs/sitemap fournies et revues ; aucune cause ni correction future établie.
Les comptes Google ne sont pas sollicités. TS22 vérifie des codes et des signaux
fournis ; TS40 vérifie chaque méthode complète puis leurs accords. Les cas
nécessitant un rendu restent NT dans ce profil source explicitement revu.

**Modification explicite de TS40 :** required_inputs communs deviennent hreflang
et intent, avec HTTP/HTML/sitemap requis selon les méthodes déclarées. La liste
inconditionnelle précédente aurait obligé à inventer un sitemap pour un usage
HTML seul. La qualification native exige les originaux propres à chaque méthode ;
le validateur de rapport seul ne parse pas ces pièces. Migration normative distincte,
aucun ancien rapport n’est réinterprété silencieusement.

Interpréteur49, adaptateur48 ; HTML27 et rejeu3 inchangés. Le registre de codes
est dérivé d’une capture publique datée et empreintée ; aucun remplacement implicite
de code obsolète. La capacité de références explicites du corpus passe de16 à24,
avec bornes8Mio/fichier et32Mio au total, chemins autorisés, manifeste et SHA inchangés.
Les overlays inversibles documentent cette limite et12 nouveaux cas CLI ; toutes
les anciennes fixtures restent inchangées.53 cas bruts, neuf cas de méthode et
neuf captures de démonstration sont explicitement synthétiques. Les tests préparés
ne valent pas résultats observés ; lire le dossier de qualification et ses échecs.
Aucune application/site/publication ou reconnaissance extérieure n’est déduite.

## English

Unpublished prerelease from verified URL batch d95be6c. Adds TS21-A01/A02,
TS22-A01/A02 and TS40-A01/A02:38 rule-bearing controls,85 atomic rules. All79 prior
rule objects/versions remain exact; TS01–TS44 identities/provenance are permanent.
RC1 and TS12–TS18 remain separately preserved.

Create a new prospective dossier under the [contract](indexing-locale-evidence.md).
Retain previous results; no automatic C relabeling. TS21 qualifies selected-family
diagnostic documentation with supplied API/logs/sitemap and reviews, not causes
or future corrections. No Google account is accessed. TS22 checks supplied codes
and signals; TS40 checks each complete method and their agreement. Render-dependent
cases remain NT in this explicitly reviewed source profile.

**Explicit TS40 change:** common required_inputs become hreflang and intent, with
HTTP/HTML/sitemap conditional on declared methods. The previous unconditional list
would require inventing a sitemap for HTML-only use. Native qualification requires
each method's originals; report validation alone does not parse them. This distinct
normative migration never silently reinterprets an old report.

Interpreter49, adapter48; HTML27/replay3 unchanged. Code facts derive from a dated,
fingerprinted public capture; no automatic deprecated-code replacement. Explicit
corpus references increase16→24;8MiB/file,32MiB total, safe paths, manifest and SHA
guards are retained. Reversible overlays document this cap and12 new CLI cases;
all previous fixtures remain unchanged.53 raw cases, nine method cases and nine
capture demonstrations are synthetic. Prepared tests are not observed results;
consult the qualification record and retained failures. No application/site change,
publication or outside recognition is inferred.
