// Static parsing only. No source script execution or TSEP decision. Apache-2.0.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {scope as networkGuard} from './source_tree_network_guard.mjs';
import {parse} from 'parse5';

if (!/^v24\./.test(process.version)) throw Error('This experiment requires Node 24');
const raw=fs.readFileSync(new URL('./source.bin',import.meta.url));
if (raw.length>8*1024*1024) throw Error('Source byte bound exceeded');
const source=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(raw);
const HTML='http://www.w3.org/1999/xhtml';
const groups=['robots','canonical','anchors','bases'];
const empty=()=>Object.fromEntries(groups.map(g=>[g,[]]));
const lower=s=>s.replace(/[A-Z]/g,c=>c.toLowerCase());
const readings={};

for (const mode of ['enabled','disabled']) {
  const inventory=empty(), templates=[], errors=[], order=[];
  let nodes=0, signalCount=0;
  try {
    const tree=parse(source,{scriptingEnabled:mode==='enabled',sourceCodeLocationInfo:true,
      onParseError:e=>{ if(errors.length>=1000) throw Error('Parse error bound exceeded'); errors.push(e); }});
    const stack=[{node:tree,ancestors:[],context:'other',template:false}];
    while(stack.length) {
      const state=stack.pop(), {node,ancestors,template}=state;
      let context=state.context;
      if(++nodes>200000 || ancestors.length>256) throw Error('Tree node/depth bound exceeded');
      const tag=node.tagName, isHTML=node.namespaceURI===HTML;
      if(isHTML && (tag==='head'||tag==='body')) context=tag;
      const attrs=Object.fromEntries((node.attrs??[]).map(a=>[a.name,a.value]));
      let group;
      if(isHTML && tag==='meta' && ['robots','googlebot'].includes(lower(attrs.name??''))) group='robots';
      if(isHTML && tag==='link' && lower(attrs.rel??'').split(/[\t\n\f\r ]+/).includes('canonical')) group='canonical';
      if(isHTML && tag==='a' && Object.hasOwn(attrs,'href')) group='anchors';
      if(isHTML && tag==='base') group='bases';
      if(group) {
        if(++signalCount>50000) throw Error('Signal bound exceeded');
        const loc=node.sourceCodeLocation?.startTag??null;
        // Void nodes carry their token location directly, not a startTag property.
        const tokenLoc=loc??(['meta','link','base'].includes(tag)?node.sourceCodeLocation:null);
        const span=tokenLoc?[tokenLoc.startOffset,tokenLoc.endOffset]:null;
        const record={group,tag,namespace:HTML,context:template?'template':context,attributes:attrs,
          ancestors,source_span_utf16:span,raw_tag:span?source.slice(...span):null};
        const destination=template?templates:inventory[group];
        order.push({group:template?'template':group,index:destination.length});
        destination.push(record);
      }
      const path=[...ancestors,tag??node.nodeName];
      for(let i=(node.childNodes??[]).length-1;i>=0;i--)
        stack.push({node:node.childNodes[i],ancestors:path,context,template});
      if(node.content) stack.push({node:node.content,ancestors:[...path,'#template-content'],context,template:true});
    }
    readings[mode]={complete:true,inventory,template_signals:templates,inventory_order:order,parse_errors:errors,
      tree_nodes:nodes,has_reported_parse_errors:errors.length>0};
  } catch(error) {
    readings[mode]={complete:false,reason:String(error.message),inventory:empty(),template_signals:[],inventory_order:[],
      parse_errors:errors,tree_nodes:nodes,has_reported_parse_errors:errors.length>0};
  }
}
const ready=Object.values(readings).every(r=>r.complete);
const comparisons=Object.fromEntries(groups.map(g=>[g,!ready?'unavailable':
  JSON.stringify(readings.enabled.inventory[g])===JSON.stringify(readings.disabled.inventory[g])?'identical':'different']));
const result={kind:'unapplied-static-source-tree',experiment_version:'1',normative_effect:'none',
  parser:{name:'parse5',version:'8.0.1',dependency:'entities@8.0.0'},runtime:{node:process.version,v8:process.versions.v8},
  source_utf8_sha256:crypto.createHash('sha256').update(raw).digest('hex'),source_bytes:raw.length,
  source_offset_unit:'UTF-16 code units, zero-based, exclusive end on exact input string',
  decoding:'Explicit UTF-8, fatal invalid bytes, leading U+FEFF retained; no HTTP charset detection or newline normalization by adapter.',
  readings,comparisons,networkGuard,
  bounds:{source_bytes:8*1024*1024,tree_nodes:200000,tree_depth:256,signals:50000,parse_errors:1000},
  scope:'Static parser tree, two whole-document scripting hypotheses. Scripts never executed. Tree construction may recover markup; errors retained. Complete means this bounded inventory finished, not valid HTML. Template signals are separate. No URL resolution, robots/canonical policy decision, measured DOM, Google observation or TSEP result. Equal empty inventories are not success.'};
const output=JSON.stringify(result);
if(Buffer.byteLength(output)>32*1024*1024) throw Error('Source result byte bound exceeded');
process.stdout.write(output+'\n');
