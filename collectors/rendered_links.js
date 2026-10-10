(() => {
  // Experimental observations only. Never activate links or infer URL validity.
  const limits = {nodes:65536, depth:128, records:8192, record_bytes:262144,
    records_bytes:4194304, string_bytes:262144, attributes:256, cooperative_ms:2000};
  const coverage = {frames:"not-entered", templates:"not-entered", closed_shadow:"unknown",
    slots:"not-expanded", order:"physical-light-then-open-shadow", origin:"unknown",
    execution_context:"not-attested", atomicity:"not-attested"};
  const out = {format:"rendered-link-observation", version:"1", limits, coverage,
    document_before:null, document_after:null, records:[], nodes_visited:0,
    traversal_complete:false, stop_reason:null, errors:[], elapsed_ms:0};
  const start = Date.now(), HTML = "http://www.w3.org/1999/xhtml", seen = new WeakSet();
  let bytes = 2;
  const stop = reason => { out.stop_reason = reason; throw new Error(reason); };
  const size = value => {
    let n = 0;
    for (const c of value) { const p=c.codePointAt(0); n += p<128 ? 1 : p<2048 ? 2 : p<65536 ? 3 : 4; }
    return n;
  };
  const str = value => {
    if (typeof value !== "string") stop("unavailable-api");
    if (value.length > limits.string_bytes || size(value) > limits.string_bytes) stop("string-limit");
    return value;
  };
  const ns = value => value === null ? null : str(value);
  const facts = () => ({url:str(document.URL), base_uri:str(document.baseURI),
    character_set:str(document.characterSet), content_type:str(document.contentType),
    ready_state:str(document.readyState)});
  const visit = (node, path, ancestors) => {
    if (Date.now()-start > limits.cooperative_ms) stop("time-limit");
    if (path.length > limits.depth) stop("depth-limit");
    if (out.nodes_visited >= limits.nodes) stop("node-limit");
    if (seen.has(node)) stop("repeated-node");
    seen.add(node); out.nodes_visited++;
    let shadow = null, nextAncestors = ancestors;
    if (node.nodeType === 1) {
      const tag = str(node.localName), namespace = ns(node.namespaceURI);
      shadow = node.shadowRoot;
      if (shadow === undefined) stop("unavailable-api");
      const named = ["a","area","link","base","form","template","iframe","frame"].includes(tag);
      const override = namespace === HTML && ["input","button"].includes(tag) && node.hasAttribute("formaction");
      if (named || override || shadow) {
        if (out.records.length >= limits.records) stop("record-limit");
        const attributes=[];
        if (node.attributes.length > limits.attributes) stop("attribute-limit");
        for (const a of node.attributes) attributes.push({name:str(a.name), local_name:str(a.localName),
          namespace:ns(a.namespaceURI), value:str(a.value)});
        const record = {order:out.records.length, visit:out.nodes_visited, path, ancestors, tag, namespace,
          selected_reason:named ? "named-element" : override ? "form-override" : "open-shadow-host",
          attributes, node_base_uri:str(node.baseURI), shadow_root:shadow ? "open" : "unexposed-or-absent",
          href_property:namespace === HTML && ["a","area","link","base"].includes(tag) ? str(node.href) : null};
        const next = size(JSON.stringify(record))+1;
        if (next > limits.record_bytes) stop("record-byte-limit");
        if (bytes+next > limits.records_bytes) stop("records-byte-limit");
        out.records.push(record); bytes += next;
      }
      nextAncestors = ancestors.concat([{tag,namespace}]);
    }
    // Physical children only: no frame documents, template.content or slot assignment.
    let index=0;
    for (let child=node.firstChild; child; child=child.nextSibling) visit(child,path.concat([index++]),nextAncestors);
    if (shadow) visit(shadow,path.concat(["shadow"]),nextAncestors);
  };
  try {
    out.document_before=facts();
    visit(document,[],[]);
    out.document_after=facts();
    out.traversal_complete=true;
  } catch (error) {
    if (out.stop_reason === null) out.stop_reason="api-error";
    out.errors.push(String(error).slice(0,256));
  }
  out.elapsed_ms=Math.max(0,Date.now()-start);
  return out;
})()
