// Bounded static script inventory. No JavaScript execution. Apache-2.0.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {scope as networkGuard} from './source_tree_network_guard.mjs';
import {parse} from 'parse5';

if (!/^v24\./.test(process.version)) throw Error('Node 24 required');
const raw = fs.readFileSync(new URL('./source.bin', import.meta.url));
const bounds = {source_bytes:8388608, tree_nodes:20000, tree_depth:128,
  parse_errors:1000, scripts:512, context_elements:512, payload_parts:20000, payload_bytes:8388608};
if (raw.length > bounds.source_bytes) throw Error('Source bound exceeded');
const source = new TextDecoder('utf-8', {fatal:true,ignoreBOM:true}).decode(raw);
const HTML = 'http://www.w3.org/1999/xhtml';
const location = loc => loc ? {source_span_utf16:[loc.startOffset,loc.endOffset],
  raw_source:source.slice(loc.startOffset,loc.endOffset)} : null;
const readings = {};
for (const mode of ['enabled','disabled']) {
  const scripts = [], contextElements = [], errors = [];
  let documentMode = null, visited = 0, parts = 0, payloadBytes = 0;
  try {
    const tree = parse(source, {scriptingEnabled:mode === 'enabled',sourceCodeLocationInfo:true,
      onParseError:e => {if (errors.length >= bounds.parse_errors) throw Error('Parse error bound exceeded'); errors.push(e);}});
    documentMode = tree.mode;
    const stack = [{node:tree,depth:0,ancestors:[],templates:[],owners:[]}];
    while (stack.length) {
      const {node,depth,ancestors,templates,owners} = stack.pop();
      if (visited >= bounds.tree_nodes || depth > bounds.tree_depth) throw Error('Tree node/depth bound exceeded');
      const nodeId = visited++;
      let nextAncestors = ancestors, nextOwners = owners;
      if (node.tagName) {
        const tag = node.tagName, ns = node.namespaceURI;
        nextAncestors = [...ancestors,{node_id:nodeId,name:tag,namespace:ns}];
        const isScript = tag === 'script';
        const isContext = ns === HTML && (tag === 'base' || tag === 'meta');
        if (isScript || isContext) {
          const rows = isScript ? scripts : contextElements;
          if (rows.length >= (isScript ? bounds.scripts : bounds.context_elements)) throw Error('Element population bound exceeded');
          const record = {node_id:nodeId,name:tag,namespace:ns,ancestors,template_path:templates,
            attributes:(node.attrs ?? []).map(a => ({name:a.name,namespace:a.namespace ?? null,prefix:a.prefix ?? null,value:a.value})),
            start_tag:location(node.sourceCodeLocation?.startTag),end_tag:location(node.sourceCodeLocation?.endTag)};
          if (isScript) {record.payload_parts=[]; record.payload=''; nextOwners=[...owners,record];}
          rows.push(record);
        }
      }
      if (node.nodeName === '#text') {
        for (const owner of owners) {
          if (++parts > bounds.payload_parts) throw Error('Payload part bound exceeded');
          payloadBytes += Buffer.byteLength(node.value);
          if (payloadBytes > bounds.payload_bytes) throw Error('Payload byte bound exceeded');
          owner.payload_parts.push({node_id:nodeId,data:node.value,location:location(node.sourceCodeLocation)});
        }
      }
      // Template contents are inventoried, but never part of a parent's textContent.
      if (node.content) stack.push({node:node.content,depth:depth+1,ancestors:nextAncestors,
        templates:[...templates,nodeId],owners:[]});
      const children = node.childNodes ?? [];
      for (let i=children.length-1;i>=0;i--) stack.push({node:children[i],depth:depth+1,
        ancestors:nextAncestors,templates,owners:nextOwners});
    }
    for (const script of scripts) script.payload = script.payload_parts.map(p => p.data).join('');
    readings[mode] = {complete:true,document_mode:documentMode,visited_nodes:visited,
      scripts,context_elements:contextElements,parse_errors:errors};
  } catch(error) {
    readings[mode] = {complete:false,reason:String(error.message),document_mode:documentMode,
      visited_nodes:visited,scripts:[],context_elements:[],parse_errors:errors};
  }
}
const result = {kind:'unapplied-source-scripts',version:'1',normative_effect:'none',
  parser:{name:'parse5',version:'8.0.1',dependency:'entities@8.0.0'},
  runtime:{node:process.version,v8:process.versions.v8},bounds,networkGuard,
  parser_input_utf8_sha256:crypto.createHash('sha256').update(raw).digest('hex'),readings};
const output = JSON.stringify(result);
if (Buffer.byteLength(output) > 32*1024*1024) throw Error('Output bound exceeded');
process.stdout.write(output+'\n');
