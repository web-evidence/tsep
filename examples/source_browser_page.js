// Synthetic browser qualification controller, Apache-2.0.
// Read whole documents in two declared sandbox configurations; never a TSEP verdict.
(async () => {
  const config = __CONFIG__;
  const results = [], errors = [];
  const status = document.getElementById('status');
  const table = document.getElementById('observations');
  const modes = config.recipe.modes;
  function snapshot(doc) {
    const signals = [], shadows = [], templates = [];
    const stack = [{node: doc, context: 'other', path: []}];
    let count = 0;
    while (stack.length) {
      const {node, path} = stack.pop();
      let context = path.lastIndexOf('#shadow-root') > path.lastIndexOf('#template-content') ? 'shadow' :
        path.includes('#template-content') ? 'template' :
        node.ownerDocument?.head?.contains(node) ? 'head' :
        node.ownerDocument?.body?.contains(node) ? 'body' : 'other';
      if (++count > 200000 || path.length > 256) throw Error('DOM traversal bound');
      const isHTML = node.namespaceURI === 'http://www.w3.org/1999/xhtml';
      const attrs = node.attributes ? Object.fromEntries(Array.from(node.attributes, a => [a.name, a.value])) : {};
      const lower = s => s.replace(/[A-Z]/g, c => c.toLowerCase());
      const robots = isHTML && node.localName === 'meta' && ['robots','googlebot'].includes(lower(attrs.name ?? ''));
      const canonical = isHTML && node.localName === 'link' && lower(attrs.rel ?? '').split(/[\t\n\f\r ]+/).includes('canonical');
      if (robots || canonical) signals.push({kind: robots ? 'robots' : 'canonical', id: attrs.id ?? null,
        context, attributes: attrs, namespace: node.namespaceURI, ancestors: path});
      const childPath = [...path, node.localName ?? node.nodeName];
      for (let i = node.childNodes.length - 1; i >= 0; i--) stack.push({node: node.childNodes[i], path: childPath});
      if (isHTML && node.localName === 'template') {
        templates.push({attributes: attrs, html: node.innerHTML});
        stack.push({node: node.content, path: [...childPath, '#template-content']});
      }
      if (node.shadowRoot) {
        shadows.push({host: node.localName, mode: node.shadowRoot.mode, html: node.shadowRoot.innerHTML});
        stack.push({node: node.shadowRoot, path: [...childPath, '#shadow-root']});
      }
    }
    return {url: doc.URL, ready_state: doc.readyState, character_set: doc.characterSet,
      content_type: doc.contentType, html: doc.documentElement.outerHTML,
      signals, templates, open_shadow_roots: shadows, tree_nodes: count};
  }
  async function observe(id, mode) {
    const frame = document.createElement('iframe');
    frame.setAttribute('sandbox', modes[mode]);
    frame.title = id + ' / ' + mode;
    const url = config.base + '/case/' + id + '/' + mode;
    const started_at = new Date().toISOString();
    const loaded = new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(Error('Frame load deadline: '+id+'/'+mode)), 10000);
      frame.addEventListener('load', () => {clearTimeout(timer); resolve();}, {once:true});
    });
    frame.src = url;
    document.getElementById('frames').append(frame);
    await loaded;
    const doc = frame.contentDocument;
    if (!doc || doc.URL !== url || doc.readyState !== 'complete') throw Error('Missing/misattributed frame document');
    const tree = snapshot(doc);
    const row = {id, mode, url, sandbox: frame.getAttribute('sandbox'), started_at,
      observed_at: new Date().toISOString(), tree};
    if (id === 'calibration') row.calibration = {
      script: doc.getElementById('script-status')?.textContent,
      noscript: doc.getElementById('noscript-status') !== null
    };
    results.push(row);
    const p = document.createElement('p');
    p.textContent = id + ' · ' + mode + ' · ' + tree.signals.length + ' signal(s) · ' + tree.open_shadow_roots.length + ' shadow';
    table.append(p); status.textContent = results.length + ' documents observés';
    return row;
  }
  try {
    for (const mode of Object.keys(modes)) {
      const row = await observe('calibration', mode);
      if (JSON.stringify(row.calibration) !== JSON.stringify(config.recipe.calibration[mode]))
        throw Error('Script/noscript calibration failed: '+mode);
    }
    for (const item of config.recipe.cases) for (const mode of Object.keys(modes)) await observe(item.id, mode);
  } catch (error) {errors.push(String(error));}
  const payload = JSON.stringify({kind:'synthetic-source-browser-observation',version:'1',token:config.token,
    plan_sha256:config.plan_sha256,user_agent:navigator.userAgent,controller_url:location.href,
    observed_at:new Date().toISOString(),results,errors,complete:errors.length === 0 && results.length === 74});
  try {
    const response = await fetch(config.base+'/capture', {method:'POST',headers:{'Content-Type':'application/json'},body:payload,credentials:'omit'});
    const answer = await response.json();
    if (!response.ok || !answer.receipt) throw Error('Capture not acknowledged');
    document.getElementById('receipt').textContent = answer.receipt;
    status.textContent = errors.length ? 'Collecte incomplète : '+errors.join('; ') : '74 documents observés et conservés — aucune conclusion SEO';
  } catch (error) {status.textContent = 'Échec de conservation : '+String(error);}
})();
