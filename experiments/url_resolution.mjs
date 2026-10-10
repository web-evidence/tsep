// Finite offline URL observation; not a browser or a TSEP decision.
import {scope as networkGuard} from './source_tree_network_guard.mjs';
import fs from 'node:fs';
import crypto from 'node:crypto';
if (!/^v24\./.test(process.version)) throw Error('Only explicitly qualified Node 24 supported');
const bytes=fs.readFileSync(new URL('./requests.json',import.meta.url));
if(bytes.length>4*1024*1024)throw Error('URL input byte bound exceeded');
const requests=JSON.parse(bytes.toString('utf8'));
if(!Array.isArray(requests)||requests.length>50000)throw Error('URL request count bound exceeded');
const results=requests.map(request=>{
  if(!request || Object.keys(request).sort().join(',')!=='base,url' ||
     typeof request.url!=='string' || !(request.base===null||typeof request.base==='string') ||
     Buffer.byteLength(request.url)>65536 || (request.base!==null&&Buffer.byteLength(request.base)>65536))
    throw Error('Malformed/bounded URL request');
  try{
    const url=request.base===null?new URL(request.url):new URL(request.url,request.base);
    const result={ok:true,href:url.href,protocol:url.protocol,origin:url.origin};
    url.hash='';result.without_fragment=url.href;
    return result;
  }catch(error){
    if(!(error instanceof TypeError))throw error;
    return {ok:false,error:'invalid-url'};
  }
});
const output=JSON.stringify({kind:'unapplied-url-resolution',version:'1',normative_effect:'none',
  request_sha256:crypto.createHash('sha256').update(bytes).digest('hex'),
  runtime:{node:process.version,v8:process.versions.v8,ada:process.versions.ada,icu:process.versions.icu,unicode:process.versions.unicode},
  results,networkGuard});
if(Buffer.byteLength(output)>16*1024*1024)throw Error('URL output byte bound exceeded');
process.stdout.write(output+'\n');
