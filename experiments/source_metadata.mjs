// Metadata inventory extension 1 with namespace ancestry; no decision. Apache-2.0.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {scope as networkGuard} from './source_tree_network_guard.mjs';
import {parse} from 'parse5';

if (!/^v24\./.test(process.version)) throw Error('This experiment requires Node 24');
const raw = fs.readFileSync(new URL('./source.bin', import.meta.url));
if (raw.length > 8*1024*1024) throw Error('Source byte bound exceeded');
// The supervisor consumed at most one BOM. Never consume a second one here.
const source = new TextDecoder('utf-8', {fatal:true, ignoreBOM:true}).decode(raw);
const HTML = 'http://www.w3.org/1999/xhtml';
const groups = ['robots','canonical','anchors','bases'];
const empty = () => Object.fromEntries(groups.map(g => [g, []]));
const lower = s => s.replace(/[A-Z]/g, c => c.toLowerCase());
const readings = {};

for (const mode of ['enabled', 'disabled']) {
  const inventory = empty(), templateSignals = [], containers = [], declarations = [], metadata = [], errors = [], order = [];
  let nodes = 0, recordCount = 0, documentMode = null;
  try {
    const tree = parse(source, {scriptingEnabled:mode === 'enabled', sourceCodeLocationInfo:true,
      onParseError:e => {if (errors.length >= 1000) throw Error('Parse error bound exceeded'); errors.push(e);}});
    documentMode = tree.mode;
    const stack = [{node:tree, ancestors:[], ancestorNamespaces:[], context:'other', templateIndices:[]}];
    while (stack.length) {
      const {node, ancestors, ancestorNamespaces, templateIndices, context:priorContext} = stack.pop();
      if (++nodes > 200000 || ancestors.length > 256) throw Error('Tree node/depth bound exceeded');
      const tag = node.tagName, isHTML = node.namespaceURI === HTML;
      const context = isHTML && (tag === 'head' || tag === 'body') ? tag : priorContext;
      const attrs = Object.fromEntries((node.attrs ?? []).map(a => [a.name, a.value]));
      const record = group => {
        if (++recordCount > 50000) throw Error('Inventory record bound exceeded');
        const loc = node.sourceCodeLocation?.startTag ?? (['meta','link','base'].includes(tag) ? node.sourceCodeLocation : null);
        const span = loc ? [loc.startOffset, loc.endOffset] : null;
        return {group, tag, namespace:node.namespaceURI, context:templateIndices.length ? 'template' : context,
          attributes:attrs, ancestors, ancestor_namespaces:ancestorNamespaces, template_indices:templateIndices,
          source_span_utf16:span, raw_tag:span ? source.slice(...span) : null};
      };
      if (tag === 'meta') metadata.push(record('metadata'));
      let group;
      if (isHTML && tag === 'meta' && ['robots','googlebot'].includes(lower(attrs.name ?? ''))) group = 'robots';
      if (isHTML && tag === 'link' && lower(attrs.rel ?? '').split(/[\t\n\f\r ]+/).includes('canonical')) group = 'canonical';
      if (isHTML && tag === 'a' && Object.hasOwn(attrs, 'href')) group = 'anchors';
      if (isHTML && tag === 'base') group = 'bases';
      if (group) {
        const destination = templateIndices.length ? templateSignals : inventory[group];
        order.push({group:templateIndices.length ? 'template' : group, index:destination.length});
        destination.push(record(group));
      }
      if (isHTML && tag === 'meta' && (Object.hasOwn(attrs,'charset') || lower(attrs['http-equiv'] ?? '') === 'content-type'))
        declarations.push(record('encoding'));
      let childTemplates = templateIndices;
      if (isHTML && tag === 'template') {
        const entry = record('templates');
        const value = attrs.shadowrootmode ?? null;
        const normalized = value === null ? null : lower(value);
        entry.template_index = containers.length;
        entry.parent = {tag:node.parentNode?.tagName ?? node.parentNode?.nodeName ?? null,
          namespace:node.parentNode?.namespaceURI ?? null};
        entry.shadow_declaration = {value, value_state:value === null ? 'absent' :
          ['open','closed'].includes(normalized) ? normalized : 'invalid', attachment:'not-assessed'};
        childTemplates = [...templateIndices, containers.length];
        containers.push(entry);
      }
      const path = [...ancestors, tag ?? node.nodeName];
      const namespacePath = [...ancestorNamespaces, node.namespaceURI ?? null];
      for (let i = (node.childNodes ?? []).length - 1; i >= 0; i--)
        stack.push({node:node.childNodes[i], ancestors:path, ancestorNamespaces:namespacePath, context, templateIndices});
      if (node.content)
        stack.push({node:node.content, ancestors:[...path,'#template-content'], ancestorNamespaces:[...namespacePath,null], context, templateIndices:childTemplates});
    }
    readings[mode] = {complete:true, inventory, template_signals:templateSignals, template_containers:containers,
      metadata, encoding_declarations:declarations, inventory_order:order, parse_errors:errors, tree_nodes:nodes, document_mode:documentMode};
  } catch (error) {
    readings[mode] = {complete:false, reason:String(error.message), inventory:empty(), template_signals:[],
      template_containers:[], metadata:[], encoding_declarations:[], inventory_order:[], parse_errors:errors, tree_nodes:nodes, document_mode:documentMode};
  }
}
const ready = Object.values(readings).every(r => r.complete);
const compare = getter => !ready ? 'unavailable' :
  JSON.stringify(getter(readings.enabled)) === JSON.stringify(getter(readings.disabled)) ? 'identical' : 'different';
const result = {kind:'unapplied-http-source-tree', experiment_version:'1', metadata_extension:'1', normative_effect:'none',
  parser:{name:'parse5',version:'8.0.1',dependency:'entities@8.0.0'}, runtime:{node:process.version,v8:process.versions.v8},
  parser_input_utf8_sha256:crypto.createHash('sha256').update(raw).digest('hex'),
  source_offset_unit:'UTF-16 code units in exact decoded parser input, zero-based, exclusive end; body byte spans added by supervisor.',
  readings, comparisons:Object.fromEntries(groups.map(g => [g, compare(r => r.inventory[g])])),
  supplementary_comparisons:Object.fromEntries(['template_containers','template_signals','encoding_declarations','metadata'].map(g => [g,compare(r => r[g])])),
  networkGuard, bounds:{source_bytes:8*1024*1024,tree_nodes:200000,tree_depth:256,records:50000,parse_errors:1000},
  scope:'Static whole-document hypotheses, no scripts executed. Template declarations and nesting retained; shadow attachment never asserted, including closed mode. Encoding meta retained without changing the certain declared HTTP decoding. Complete is bounded inventory completion, not HTML validity. No SEO decision, URL resolution, browser or Google observation.'};
const output = JSON.stringify(result);
if (Buffer.byteLength(output) > 32*1024*1024) throw Error('Source result byte bound exceeded');
process.stdout.write(output+'\n');
