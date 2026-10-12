# Première acquisition Search Console / First Search Console acquisition

## Français

Cette procédure prépare un essai local. Aucun accès au compte, inspection réelle
ou objectif d’Edikka n’est acquis par ce document. Un CSV Performance, une capture
d’écran et une réponse JSON de l’API sont trois pièces différentes.

1. Avant l’acquisition, conserver dans un dossier local restreint la propriété
   exacte, les URL retenues, leur motif de sélection, l’objectif de chacune et
   sa source. Noter les états déjà connus et leur origine ; ne pas présenter une
   connaissance antérieure comme un résultat découvert prospectivement. Dater
   réellement ce plan. Un premier essai sur une URL ne couvre pas le site.
2. Avec le compte ayant accès à la propriété, ouvrir la
   [méthode officielle index.inspect](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect).
   Son panneau « Try it » permet de saisir inspectionUrl, siteUrl et, au besoin,
   languageCode. L’utilisateur réalise lui-même l’autorisation Google proposée ;
   le scope en lecture seule suffit à cette méthode. Ne transmettre ici ni token,
   cookie, mot de passe ni en-tête Authorization. Si l’outil n’est pas disponible
   ou l’accès est refusé, conserver le refus et son contexte sans le contourner.
3. Enregistrer le corps de requête dans request.json et le corps JSON de réponse
   dans response.json, sans réécrire les valeurs. Conserver le statut HTTP, la
   date avec fuseau et le moyen d’acquisition réel. Décrire si le JSON a été copié
   depuis le panneau : ce n’est pas une capture authentifiée des octets réseau.
   Une erreur API est une tentative, pas une preuve d’absence d’indexation.
4. Créer manifest.json selon le [diagnostic existant](search-console-observations.md),
   avec provenance supplied-google-api, description, retrieved_at, http_status,
   empreintes SHA-256 des fichiers conservés et change:null en l’absence de pièce
   de changement réel. Les empreintes lient les fichiers, elles n’authentifient
   ni Google ni l’accès à la propriété. Ne pas reformater après calcul des empreintes.
5. Fournir seulement le chemin local de ce dossier et du plan. Le parcours de
   revue demande ensuite les décisions nécessaires, liées aux pièces exactes.
   L’outil ne fabrique pas l’accord du responsable ou une revue humaine.

L’API décrit la version indexée, pas un test live. La date de récupération,
lastCrawlTime et toute capture technique sont distinctes. Le dernier crawl ne date
pas chaque champ ; une réponse récente peut décrire un état ancien. Les canonical
rapportées ne sont pas une observation du HTML ou du DOM actuel. Les données de
compte restent locales et restreintes ; les exemples distribués sont fictifs.

## English

This procedure prepares a local trial; it establishes no account access, actual
inspection or Edikka objective. Performance CSV, screenshot and native API JSON
are distinct evidence types.

Before acquisition, retain the exact property, selected URLs, selection rationale,
per-URL objective and its source in a restricted local folder. Disclose prior
knowledge and its origin. Use the actual plan date; a one-URL trial is not site
coverage. In the official index.inspect page linked above, the account holder can
use “Try it”, enter inspectionUrl/siteUrl and optional languageCode, and handle
Google authorization personally. The read-only scope suffices for this method.
Never send credentials, tokens, cookies or authorization headers here. Retain
access failures without bypassing them.

Save request.json and response.json without rewriting their values, together with
actual HTTP status, acquisition timestamp/timezone and method. Disclose a copy
from the panel as such, not authenticated network bytes. API errors remain failed
attempts, never proof of non-indexing. Create manifest.json under the existing
diagnostic contract: supplied-google-api provenance, description, retrieved_at,
http_status, byte SHA-256 hashes, and change:null unless actual change evidence
exists. Hashes do not authenticate the provider or account. Supply the local
folder/plan paths; subsequent review must contain genuinely supplied decisions.

Inspection is not live. Retrieval time, lastCrawlTime and technical-capture times
are distinct; lastCrawlTime does not date every field. Canonical values reported
by Google do not observe current source or DOM. Account data remains restricted;
distributed exercises are synthetic.

## Parcours local / Local workflow

`adapters/inspection_intake.py` version1 importe les dossiers du diagnostic1 et
produit des demandes de revue vides. Le plan est une cible captures sous le
[contrat TS08](inspection-evidence.md), sans inspection_records/inspection_reviews.
La date observed_at est renseignée à l’import puis lors de la nouvelle évaluation ;
intent.declared_at et toutes les dates fournies restent intactes. La revue préalable
inspection_plan_review doit réellement précéder l’acquisition. L’import ne la crée pas.

```sh
python3 adapters/inspection_intake.py prepare /chemin/plan.json \
  --inspection /chemin/inspection-originale --output /chemin/intake-neuf
# Copier review-request.json ailleurs et renseigner les revues effectivement fournies.
python3 adapters/inspection_intake.py build /chemin/intake-neuf \
  --reviews /chemin/revues-fournies.json --assessor 'Évaluateur réel' \
  --output /chemin/rapport-neuf
python3 adapters/replay.py /chemin/rapport-neuf --output /chemin/rejeu-neuf
python3 tsep.py html /chemin/rapport-neuf/report.json --lang fr \
  --output /chemin/rapport-neuf-fr.html
```

English: prepare imports exact diagnostic1 folders and blank evidence-bound review
requests; it invents no plan review or decision. The input plan is a captures target
under the TS08 contract without inspection_records/inspection_reviews. Assessment
time is recorded at import/new build; supplied intent/acquisition/review dates are
never moved. Copy and complete only genuinely supplied reviews. Build creates a
new restricted (or explicitly synthetic) bundle; use exact tools for replay. Keep
the intake folder, original native files, supplied reviews and entire output bundle.
