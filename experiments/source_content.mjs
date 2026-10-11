// Bounded static content tree, observation only. Apache-2.0.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {scope as networkGuard} from './source_tree_network_guard.mjs';
import {parse} from 'parse5';

if (!/^v24\./.test(process.version)) throw Error('This experiment requires Node 24');
const raw = fs.readFileSync(new URL('./source.bin', import.meta.url));
if (raw.length > 8*1024*1024) throw Error('Source byte bound exceeded');
const source = new TextDecoder('utf-8', {fatal:true, ignoreBOM:true}).decode(raw);
const bounds = {source_bytes:8*1024*1024,tree_nodes:20000,tree_depth:128,parse_errors:1000};
const readings = {};
for (const mode of ['enabled', 'disabled']) {
  const nodes = [], errors = [];
  let documentMode = null;
  try {
    const tree = parse(source, {scriptingEnabled:mode === 'enabled',sourceCodeLocationInfo:true,
      onParseError:e => {if (errors.length >= bounds.parse_errors) throw Error('Parse error bound exceeded'); errors.push(e);}});
    documentMode = tree.mode;
    const stack = [{node:tree,parent:null,edge:'root',index:0,depth:0}];
    while (stack.length) {
      const {node,parent,edge,index,depth} = stack.pop();
      if (nodes.length >= bounds.tree_nodes || depth > bounds.tree_depth) throw Error('Tree node/depth bound exceeded');
      const element = typeof node.tagName === 'string';
      const kind = element ? 'element' : ({'#document':'document','#document-fragment':'fragment',
        '#documentType':'doctype','#text':'text','#comment':'comment'})[node.nodeName];
      if (!kind) throw Error('Unknown parser node kind');
      // Element provenance is its start tag, never a claim that a recovered node
      // occupied a unique source interval. Text spans may include intervening
      // markup after parser recovery; retain raw span and parsed value separately.
      const loc = element ? node.sourceCodeLocation?.startTag : node.sourceCodeLocation;
      const span = loc ? [loc.startOffset,loc.endOffset] : null;
      const children = node.childNodes ?? [];
      const id = nodes.length;
      nodes.push({id,parent,edge,index,kind,name:node.tagName ?? node.nodeName,
        namespace:node.namespaceURI ?? null,
        attributes:(node.attrs ?? []).map(a => ({name:a.name,namespace:a.namespace ?? null,prefix:a.prefix ?? null,value:a.value})),
        data:kind === 'text' ? node.value : kind === 'comment' ? node.data : null,
        child_count:children.length,template_content:Boolean(node.content),
        source_span_utf16:span,raw_source:span ? source.slice(...span) : null});
      if (node.content) stack.push({node:node.content,parent:id,edge:'template-content',index:0,depth:depth+1});
      for (let i=children.length-1;i>=0;i--) stack.push({node:children[i],parent:id,edge:'child',index:i,depth:depth+1});
    }
    readings[mode] = {complete:true,document_mode:documentMode,nodes,parse_errors:errors};
  } catch (error) {
    // Never retain an apparently useful prefix after a traversal or parser limit.
    readings[mode] = {complete:false,reason:String(error.message),document_mode:documentMode,nodes:[],parse_errors:errors};
  }
}
const result = {kind:'unapplied-source-content-tree',experiment_version:'1',normative_effect:'none',
  parser:{name:'parse5',version:'8.0.1',dependency:'entities@8.0.0'},
  runtime:{node:process.version,v8:process.versions.v8},
  parser_input_utf8_sha256:crypto.createHash('sha256').update(raw).digest('hex'),
  readings,bounds,networkGuard,
  scope:'Static HTML tree in two scripting hypotheses; source JavaScript never executed. Templates retained as separate fragments; shadow attachment, child frame documents, CSS visibility, discovery, consumer reading and semantic sufficiency not established. Complete means bounded traversal completed, not valid HTML or a TS44 outcome.'};
const output = JSON.stringify(result);
if (Buffer.byteLength(output) > 32*1024*1024) throw Error('Source result byte bound exceeded');
process.stdout.write(output+'\n');
