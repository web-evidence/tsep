# Migration 0.1.0-draft.8 → 0.1.0-draft.9

## Français

La candidate ajoute TS04-A01/A02 : treize règles pour TS01, TS02, TS04, TS07 et
TS10. Les 44 identifiants, unités, sévérités et profils TSEP sont conservés.
Le format de rapport reste 2. La version normative et ses empreintes changent ;
aucun tag, DOI ou paquet antérieur n'est remplacé. Cette étape n'est pas publiée.

TS04 exige une matrice préalable par origine, un profil explicite et les preuves
de politique et de ressources, avec revue fournie là où requise. Une ancienne
mention C sans ces pièces ne migre pas en C. Voir [format et bornes](robots.md).
Sans revue ou entrée nécessaire, le résultat demeure indéterminé sauf contradiction
déjà prouvée. Il est interdit d'inventer ou antidater une intention ou une revue.

TS07-A02 utilise le même module robots. Sans `intent.robots_policy`, le profil
historique **fixe** `legacy-exact-v1` garde sa couverture limitée ; ce n'est pas une
sélection de profil favorable. Les entrées explicites choisissent leur profil avant
capture. Un 401/403 attribuable reste désormais fail malgré l'absence de robots.
Les règles TS01, TS02, TS07-A01/A03 et TS10 conservent leurs attendus. Leurs versions
sont actualisées avec l'identité globale du protocole, sans prétendre plus de rendu.

Les 254 cas antérieurs restent identiques, avec 45 nouveaux cas. Leurs sorties
TS07/TS10 historiques gardent l'empreinte de régression existante ; le nouveau cas
« refus HTTP sans robots » documente explicitement l'extension de contradiction.
Les fixtures antérieures du lecteur sont conservées. Son expérience devient une
CLI d'observation version 2 autour du module partagé ; elle n'émet pas C/NC/NA/NT.

Interpréteur 8, adaptateur de captures 9, revue/import 2. La provenance inclut les
deux nouveaux modules robots. Pour les matrices TS04, les preuves HTTP dérivées
conservent également la trace robots ; cela ne crée pas de réponse de page absente
dans TS01/TS07. Rejouer un ancien paquet avec ses anciens outils. Pour une nouvelle
évaluation, importer les captures originales dans un nouveau dossier, avec une
intention préalable existante ; ne pas renommer ni réécrire les anciens résultats.
Une demande de revue déjà préparée garde ses outils historiques ou doit être
préparée à nouveau explicitement. Aucune approbation humaine n'est générée.

## English

This candidate adds TS04-A01/A02, bringing the rule set to thirteen. Permanent
control IDs, units, severities, TSEP profiles and report format 2 remain unchanged.
Normative identity changes; no previous tag, DOI or package is replaced or relabeled.
TS04 now needs the prior matrix/profile, policy evidence and required-resource
evidence/reviews. Missing evidence never migrates an old C into a new C.

TS07-A02 shares the reader, retaining a fixed legacy-exact-v1 profile for absent
policy fields. Explicit profiles must predate capture. Attributable 401/403 denial
now survives absent robots evidence. Other rule semantics remain unchanged.
All 254 prior raw cases coexist with 45 prefrozen additions; historical TS07/TS10
output regression is retained. Interpreter 8, capture adapter 9 and review workflow
2 add shared robots provenance and required-resource review tasks. The observation
CLI version 2 wraps the shared reader without producing control statuses.

Preserve old captures, reports, review requests and pinned tools. Historical replay
requires historical tools; new assessment creates a new directory. Never fabricate
or backdate intent/review. No publication, complete four-control program, human
trial, real engine access, indexing or Edikka conformity is claimed by this version.
