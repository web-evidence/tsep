# HTML document base — dated textual capture / capture textuelle datée

- URL: https://html.spec.whatwg.org/multipage/urls-and-fetching.html#document-base-url
- Observed / consulté: 2026-10-19 UTC. Displayed update / mise à jour affichée: 2026-10-16.
- Scope / périmètre: §2.4.3, document base URL; read through the web tool.
- Capture: limited textual excerpt below, not a full-page capture. Its SHA256
  is retained in the sibling `.sha256` file.

> If document has a descendant base element that has an href attribute, then return the frozen base URL

FR : extrait limité de18 mots. La suite de l'étape désigne le premier élément
dans l'ordre de l'arbre ; sans base applicable, d'autres étapes déterminent le
repli. Cette source établit que l'URL documentaire ne suffit pas toujours à
résoudre une ressource relative. TSEP choisit prudemment NT pour une résolution
de base non qualifiée, sans prétendre implémenter tout l'algorithme HTML.

EN: limited18-word excerpt. The rest of the step selects the first element in
tree order; other steps determine fallback without an applicable base. The
source establishes that the document URL alone does not always resolve a
relative resource. TSEP conservatively chooses NT for unqualified base
resolution, without claiming to implement the full HTML algorithm.
