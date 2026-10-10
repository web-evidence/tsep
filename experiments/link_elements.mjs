// Supplemental element facts; no URL resolution, activation or SEO decision.
import {scope as networkGuard} from './source_tree_network_guard.mjs';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {parse} from 'parse5';
if(!/^v24\./.test(process.version))throw Error('This observer requires Node 24');
const raw=fs.readFileSync(new URL('./source.bin',import.meta.url));
if(raw.length>8*1024*1024)throw Error('Source byte bound exceeded');
const source=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(raw);
const HTML='http://www.w3.org/1999/xhtml';
const selected=new Set(['a','area','link','base','form']);
const readings={};
for(const mode of ['enabled','disabled']){
  let nodes=0,count=0;const records=[],templates=[],errors=[];
  try{
    const tree=parse(source,{scriptingEnabled:mode==='enabled',sourceCodeLocationInfo:true,
      onParseError:e=>{if(errors.length>=1000)throw Error('Parse error bound exceeded');errors.push(e);}});
    const stack=[{node:tree,ancestors:[],namespaces:[],templateIndices:[],context:'other'}];
    while(stack.length){
      const {node,ancestors,namespaces,templateIndices,context:prior}=stack.pop();
      if(++nodes>200000||ancestors.length>256)throw Error('Tree node/depth bound exceeded');
      const tag=node.tagName,ns=node.namespaceURI??null;
      const context=ns===HTML&&['head','body'].includes(tag)?tag:prior;
      const attributes=(node.attrs??[]).map(a=>({local_name:a.name,prefix:a.prefix??null,namespace:a.namespace??null,value:a.value}));
      const record=()=>{
        if(++count>50000)throw Error('Element record bound exceeded');
        const loc=node.sourceCodeLocation?.startTag??(['area','link','base','input'].includes(tag)?node.sourceCodeLocation:null);
        const span=loc?[loc.startOffset,loc.endOffset]:null;
        return {node_index:nodes-1,tag,namespace:ns,attributes,ancestors,ancestor_namespaces:namespaces,
          context:templateIndices.length?'template':context,template_indices:templateIndices,
          source_span_utf16:span,raw_tag:span?source.slice(...span):null};
      };
      const override=ns===HTML&&['input','button'].includes(tag)&&attributes.some(a=>a.namespace===null&&a.local_name==='formaction');
      if(selected.has(tag)||override)records.push(record());
      let childTemplates=templateIndices;
      if(ns===HTML&&tag==='template'){
        const t=record();t.template_index=templates.length;templates.push(t);childTemplates=[...templateIndices,t.template_index];
      }
      const path=[...ancestors,tag??node.nodeName],namespacePath=[...namespaces,ns];
      for(let i=(node.childNodes??[]).length-1;i>=0;i--)
        stack.push({node:node.childNodes[i],ancestors:path,namespaces:namespacePath,templateIndices,context});
      if(node.content)stack.push({node:node.content,ancestors:[...path,'#template-content'],
        namespaces:[...namespacePath,null],templateIndices:childTemplates,context});
    }
    readings[mode]={complete:true,records,templates,parse_errors:errors,tree_nodes:nodes,document_mode:tree.mode};
  }catch(error){
    readings[mode]={complete:false,reason:String(error.message),records:[],templates:[],parse_errors:errors,tree_nodes:nodes,document_mode:null};
  }
}
const result={kind:'unapplied-link-elements',version:'1',normative_effect:'none',
  parser:{name:'parse5',version:'8.0.1',dependency:'entities@8.0.0'},runtime:{node:process.version,v8:process.versions.v8},
  parser_input_utf8_sha256:crypto.createHash('sha256').update(raw).digest('hex'),readings,networkGuard,
  bounds:{source_bytes:8*1024*1024,tree_nodes:200000,tree_depth:256,records:50000,parse_errors:1000},
  scope:'Named a/area/link/base/form elements in all namespaces, HTML input/button formaction and templates. Complete only for this bounded structural inventory; no interaction inventory, shadow attachment, frame documents, activated link or SEO conclusion.'};
const output=JSON.stringify(result);
if(Buffer.byteLength(output)>32*1024*1024)throw Error('Element output byte bound exceeded');
process.stdout.write(output+'\n');
