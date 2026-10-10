// Authored API doubles, NOT browser observations or HTML parsing qualification.
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const script=new URL('../collectors/rendered_links.js',import.meta.url);
const code=fs.readFileSync(script,'utf8'), HTML='http://www.w3.org/1999/xhtml';
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const element=(tag='div')=>({nodeType:1,localName:tag,namespaceURI:HTML,shadowRoot:null,
  attributes:[],hasAttribute(name){return this.attributes.some(a=>a.name===name);},
  baseURI:'https://example.test/p',href:'',firstChild:null,nextSibling:null});
const doc=()=>({nodeType:9,URL:'https://example.test/p',baseURI:'https://example.test/p',
  characterSet:'UTF-8',contentType:'text/html',readyState:'complete',firstChild:null});
const attr=(name,value)=>({name,localName:name,namespaceURI:null,value});
const run=(document)=>vm.runInNewContext(code,{document},{timeout:5000});
const rows=[];
function check(id,fn){try{fn();rows.push({id,ok:true});}catch(e){rows.push({id,ok:false,error:String(e)});}}
check('missing-document-api',()=>{const d=doc();delete d.baseURI;const r=run(d);assert.equal(r.stop_reason,'unavailable-api');assert.equal(r.traversal_complete,false);});
check('getter-throws',()=>{const d=doc();d.firstChild=element('a');Object.defineProperty(d.firstChild,'href',{get(){throw Error('fixture getter failure');}});const r=run(d);assert.equal(r.stop_reason,'api-error');assert.equal(r.records.length,0);});
check('unpaired-surrogate-preserved-for-downstream-refusal',()=>{const d=doc();d.firstChild=element('a');d.firstChild.attributes=[attr('href','\ud800')];const r=run(d);assert.equal(r.records[0].attributes[0].value,'\ud800');assert.equal(r.traversal_complete,true);});
check('invalid-property-is-not-parsed-or-repaired',()=>{const d=doc();d.firstChild=element('a');d.firstChild.href='http://[bad';d.firstChild.attributes=[attr('href','http://[bad')];const r=run(d);assert.equal(r.records[0].href_property,'http://[bad');assert.equal(r.traversal_complete,true);});
check('repeated-node',()=>{const d=doc();d.firstChild=element();d.firstChild.nextSibling=d.firstChild;const r=run(d);assert.equal(r.stop_reason,'repeated-node');});
check('depth-bound',()=>{const d=doc();let parent=d;for(let i=0;i<130;i++){parent.firstChild=element();parent=parent.firstChild;}const r=run(d);assert.equal(r.stop_reason,'depth-limit');});
check('record-count-bound',()=>{const d=doc();d.firstChild=element('a');let last=d.firstChild;for(let i=0;i<8193;i++){last.nextSibling=element('a');last=last.nextSibling;}const r=run(d);assert.equal(r.stop_reason,'record-limit');assert.equal(r.records.length,8192);});
check('string-bound',()=>{const d=doc();d.firstChild=element('a');d.firstChild.href='é'.repeat(131073);const r=run(d);assert.equal(r.stop_reason,'string-limit');assert.equal(r.records.length,0);});
check('attribute-bound',()=>{const d=doc();d.firstChild=element('a');d.firstChild.attributes=Array.from({length:257},(_,i)=>attr('x'+i,''));assert.equal(run(d).stop_reason,'attribute-limit');});
check('record-byte-bound',()=>{const d=doc();d.firstChild=element('a');d.firstChild.attributes=[attr('x','x'.repeat(200000)),attr('y','y'.repeat(200000))];assert.equal(run(d).stop_reason,'record-byte-limit');});
check('frames-templates-and-slots-not-entered',()=>{const d=doc();d.firstChild=element('iframe');d.firstChild.contentDocument={get firstChild(){throw Error('entered frame');}};d.firstChild.nextSibling=element('template');d.firstChild.nextSibling.content={get firstChild(){throw Error('entered template');}};d.firstChild.nextSibling.nextSibling=element('slot');d.firstChild.nextSibling.nextSibling.assignedNodes=()=>{throw Error('expanded slot');};const r=run(d);assert.equal(r.traversal_complete,true);assert.equal(r.records.length,2);});
check('base-change-not-hidden',()=>{const d=doc();d.firstChild=element('a');Object.defineProperty(d.firstChild,'href',{get(){d.baseURI='https://example.test/changed/';return 'unchanged-property';}});const r=run(d);assert.notEqual(r.document_before.base_uri,r.document_after.base_uri);});
console.log(JSON.stringify({kind:'rendered-links-authored-api-guards',synthetic:true,normative_effect:'none',
  scope:'Handwritten API doubles test collector guards, not browser semantics. Authored after implementation.',
  node:process.version,v8:process.versions.v8,script_sha256:sha(code),check_sha256:sha(fs.readFileSync(new URL(import.meta.url))),
  matched:rows.filter(r=>r.ok).length,total:rows.length,rows},null,2));
process.exitCode=rows.every(r=>r.ok)?0:1;
