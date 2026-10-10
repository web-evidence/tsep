// Guard documented Node network entry points during the retained offline experiment.
// This is not an OS network-isolation claim. Source scripts are never evaluated.
import {syncBuiltinESMExports} from 'node:module';
const denied=()=>{throw Error('Network/API forbidden in source parser experiment');};
const guarded=[];
for(const [name,keys] of [
  ['node:net',['connect','createConnection','createServer']],
  ['node:tls',['connect','createServer']],
  ['node:http',['request','get','createServer']],
  ['node:https',['request','get','createServer']],
  ['node:http2',['connect','createServer','createSecureServer']],
  ['node:dgram',['createSocket']],
  ['node:dns',['lookup','resolve','resolve4','resolve6','resolveAny']],
]){
  const mod=(await import(name)).default;
  for(const key of keys){if(typeof mod[key]==='function'){mod[key]=denied;guarded.push(name+'.'+key);}}
  if(mod.Socket){mod.Socket.prototype.connect=denied;guarded.push(name+'.Socket.connect');}
  if(mod.promises){for(const key of Object.keys(mod.promises)){if(typeof mod.promises[key]==='function'&&key!=='Resolver'){mod.promises[key]=denied;}}}
}
globalThis.fetch=denied;
globalThis.WebSocket=class{constructor(){denied();}};
syncBuiltinESMExports();
export const scope={guarded,scope:'Documented API guard, not OS network isolation; no source JavaScript execution.'};
