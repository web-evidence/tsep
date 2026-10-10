# Migration draft.9 → draft.10

## Français

Draft.10 intègre un lecteur DOM structuré explicitement choisi avant collecte pour
TS07-A03 et TS10-A01/A02/A04. Les 44 IDs, les 13 règles, leurs automatisations et
les résultats C/NC/NA/NT restent en place. L'interpréteur devient 9, l'adaptateur
captures 10, revue 3 ; le format rapport reste 2. Les règles FR/EN explicitent le lecteur,
la provenance des acquisitions, les limites d'API, les positions et la couverture.
[Format, priorités et cas](structured-rendering.md).

1. Conserver rapports, captures, archives et tags anciens. Aucun ancien verdict ou
   relevé expérimental n'est remplacé ; rejouer avec ses outils exacts.
2. Pour une nouvelle campagne structurée, déclarer le lecteur avant capture et
   conserver les pièces de navigation. Ne pas transformer une référence ajoutée
   a posteriori en plan préalable, ni deux visites en une seule par une empreinte.
3. Sans `dom_reader`, les anciennes entrées gardent leur lecteur fixe et leurs
   limites. Réévaluer les mêmes octets avec draft.10 produit un **nouveau rapport**.
4. Les payloads structurés ne se replient pas sur le lecteur historique. Un arbre
   incomplet ou une provenance séparée ne devient pas pass. Le candidat expérimental
   qui conservait des contradictions de préfixe garde son sens propre ; pas de
   conversion automatique de ses issues en verdict normatif.
5. Une revue manuelle TS10 doit être refaite lorsqu'elle ne désigne plus les pièces
   exactes. Une revue absente ou un HTML source hors sous-ensemble reste indéterminé.
   Les tests synthétiques et la réussite technique ne prouvent pas la conformité d'Edikka.

Les 299 cas existants restent inchangés ; 39 nouveaux cas bruts figés sont ajoutés.
Les tests vérifient aussi le rejeu hors réseau et empêchent de publier un arbre
rédigé sous un accès public via l'adaptateur. Publication et recette humaine restent
distinctes de cette intégration locale.

## English

Draft.10 adds a predeclared structured DOM reader for TS07-A03 and
TS10-A01/A02/A04. All 44 control IDs, 13 atomic rules, automation classes and
C/NC/NA/NT meanings remain. Interpreter 9, capture adapter 10, review workflow 3, report format 2.
Bilingual rules explicitly describe acquisition attribution, API/placement and
coverage limits. See the [complete method](structured-rendering.md).

Keep historical reports, captures, archives and tags with their exact tools. Choose
the new reader before collection and retain navigation evidence. Never backdate
intent or equate separate visits through a digest. Missing dom_reader retains the
fixed historical reader and limits. Reassessment under draft.10 creates a new report.
Structured payloads never fall back after refusal; incomplete/independently acquired
records do not pass. Experimental prefix contradictions retain their original
meaning, without conversion into normative outcomes. Renew manual TS10 reviews when
bound evidence changes. Missing reviews and unsupported source HTML remain unknown.

The 299 prior cases are unchanged; 39 prefrozen raw cases are added. Tests include
offline replay and refusal to label authored DOM as public evidence. Local integration
is not publication, human acceptance or an Edikka conformity assessment.

Les anciennes fiches de revue gardent leurs outils. La version 3 crée de nouvelles fiches,
avec identités des relevés structurés ; ne pas importer une ancienne réponse comme une nouvelle revue.
Old review requests retain their tools. Workflow 3 creates new requests with structured
capture identities; never relabel an old response as a fresh review.
