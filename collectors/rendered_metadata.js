(() => {
  // Observation-only v2. No writes, network, reparsing, or TSEP decisions.
  const limits = {nodes:1024, depth:64, tree_utf8_bytes:524288,
    serialization_utf8_bytes:262144, cooperative_ms:2000, invocation_timeout_ms:5000};
  const started = Date.now();
  const htmlNS = "http://www.w3.org/1999/xhtml";
  const size = s => {
    let bytes = 0;
    for (const c of s) { const p = c.codePointAt(0); bytes += p < 128 ? 1 : p < 2048 ? 2 : p < 65536 ? 3 : 4; }
    return bytes;
  };
  const output = {format:"rendered-metadata-tree", version:"2", limits,
    document_url:null, base_uri:null, ready_state:null,
    execution_context:"not-attested", scripting:"enabled-by-laboratory-plan",
    closed_shadow_coverage:"unknown", frame_documents:"not-collected",
    template_fragments:"not-collected", origin_attribution:"unknown",
    serialization:null, nodes:[], reported_node_count:0, traversal_complete:false, stop_reason:null,
    api_errors:[], elapsed_ms:null};
  const pending = [{node:document, parent:null, edge:"root", index:0, depth:0}];
  let bytes = 2;
  const requireString = (value, name) => {
    if (typeof value !== "string") throw new Error("Unavailable DOM API: " + name);
    return value;
  };
  const requireNamespace = (value, name) => {
    if (value !== null && typeof value !== "string") throw new Error("Unavailable DOM API: " + name);
    return value;
  };
  try {
    output.document_url = requireString(document.URL, "document.URL");
    output.ready_state = requireString(document.readyState, "document.readyState");
    output.base_uri = requireString(document.baseURI, "document.baseURI");
    const raw = requireString(document.documentElement.outerHTML, "outerHTML");
    output.serialization = size(raw) <= limits.serialization_utf8_bytes
      ? {available:true, html:raw} : {available:false, reason:"serialization-byte-limit"};
    while (pending.length) {
      if (Date.now() - started > limits.cooperative_ms) { output.stop_reason="time-limit"; break; }
      if (output.nodes.length >= limits.nodes) { output.stop_reason="node-limit"; break; }
      const item = pending.pop(), node = item.node;
      if (item.depth > limits.depth) { output.stop_reason="depth-limit"; break; }
      const type = node.nodeType, element = type === 1;
      const children = Array.from(node.childNodes);
      const shadow = element ? node.shadowRoot : null;
      if (element && shadow === undefined) throw new Error("Unavailable DOM API: shadowRoot");
      const record = {id:output.nodes.length, parent:item.parent, edge:item.edge,
        index:item.index, type, name:element ? node.localName : node.nodeName,
        namespace:element ? requireNamespace(node.namespaceURI, "namespaceURI") : null,
        attributes:element ? Array.from(node.attributes).map(a => ({
          name:requireString(a.name, "attribute.name"), local_name:requireString(a.localName, "attribute.localName"),
          namespace:requireNamespace(a.namespaceURI, "attribute.namespaceURI"), value:requireString(a.value, "attribute.value")})) : [],
        data:type === 3 || type === 8 ? node.nodeValue : null,
        child_count:children.length, shadow:element ? (shadow ? "open" : "unexposed-or-absent") : "not-element",
        resolved_href:element && node.namespaceURI === htmlNS &&
          (node.localName === "link" || node.localName === "base") ? requireString(node.href, "href") : null};
      const next = size(JSON.stringify(record)) + 1;
      if (bytes + next > limits.tree_utf8_bytes) { output.stop_reason="tree-byte-limit"; break; }
      bytes += next; output.nodes.push(record);
      // Shadow is a distinct edge after light-DOM children. Never enter frames/templates.
      if (shadow) pending.push({node:shadow,parent:record.id,edge:"shadow",index:0,depth:item.depth+1});
      for (let i=children.length-1; i>=0; i--) pending.push({
        node:children[i],parent:record.id,edge:"child",index:i,depth:item.depth+1});
    }
    output.traversal_complete = output.stop_reason === null && pending.length === 0;
  } catch (error) {
    output.stop_reason="api-error"; output.api_errors.push(String(error));
  }
  output.elapsed_ms = Math.max(0, Date.now()-started);
  output.reported_node_count = output.nodes.length;
  return output;
})()
