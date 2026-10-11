// Isolated JSON-LD processor. No source scripts, URL document loading or network.
// Apache-2.0; the unmodified bundled processor has its own retained license.
import {scope as networkGuard} from './source_tree_network_guard.mjs';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';

if(Number(process.versions.node.split('.')[0]) !== 24) throw Error('Node 24 required');
const require=createRequire(import.meta.url);
const factory=require('./jsonld.cjs');
const bytes=readFileSync(new URL('./request.json',import.meta.url));
const request=JSON.parse(bytes.toString('utf8'));
const hash=value=>createHash('sha256').update(value).digest('hex');
const results=[];
for(const doc of request.documents) {
  const row={id:doc.id,base_iri:doc.base_iri,raw_json_sha256:hash(doc.raw_json),
    contexts:doc.contexts.map(c=>({url:c.url,sha256:c.sha256})),
    status:null,expanded:null,flattened:null,notices:[],context_loads:[],error:null};
  if(doc.pre_error) {row.status=doc.pre_error.status;row.error=doc.pre_error.reason;results.push(row);continue;}
  // Each document gets a fresh context cache: another document's allowed context
  // must never satisfy a missing or changed context in this document.
  const processor=factory();
  const contexts=new Map(doc.contexts.map(c=>[c.url,c]));
  let phase='expand';let refused=false;
  const loader=async url=>{
    if(row.context_loads.length>=64) throw Error('Context load bound exceeded');
    const context=contexts.get(url);
    row.context_loads.push({phase,url,supplied:!!context,sha256:context?.sha256??null});
    if(!context) {refused=true;throw Error('Context not supplied; implicit loading refused');}
    return {contextUrl:null,documentUrl:url,document:JSON.parse(context.raw_json)};
  };
  const eventHandler=({event,next})=>{
    if(row.notices.length>=128) throw Error('Processor notice bound exceeded');
    row.notices.push({phase,code:event.code,level:event.level,message:event.message});next();
  };
  const options={base:doc.base_iri,processingMode:'json-ld-1.1',documentLoader:loader,eventHandler};
  try {
    const value=JSON.parse(doc.raw_json);
    row.expanded=await processor.expand(value,options);
    phase='flatten';
    row.flattened=await processor.flatten(value,null,options);
    row.status='observed';
  } catch(error) {
    row.status=refused?'unavailable':'processor-error';
    row.expanded=null;row.flattened=null;
    row.error={name:String(error.name??'Error'),code:error.details?.code??null,
      message:String(error.message??error).slice(0,2048),phase};
  }
  results.push(row);
}
const output={kind:'unapplied-jsonld-processing',version:'1',normative_effect:'none',
  request_sha256:hash(bytes),processor:{name:'jsonld',version:'9.0.0',member:'dist/jsonld.esm.js'},
  runtime:{node:process.version,v8:process.versions.v8},network_guard:networkGuard,documents:results};
const text=JSON.stringify(output);
if(Buffer.byteLength(text)>16*1024*1024) throw Error('Output byte bound exceeded');
process.stdout.write(text+'\n');
