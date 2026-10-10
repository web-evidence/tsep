(() => {
  const config=__CONFIG__;
  const parse=(url,base)=>{try{return {ok:true,href:new URL(url,base).href};}catch(e){return {ok:false,error:String(e)};}};
  const direct=()=>{const a=document.getElementById("anchor-probe");return {
    document_url:document.URL,base_uri:document.baseURI,anchor_base_uri:a.baseURI,
    raw_href:a.getAttribute("href"),href_property:a.href,
    bases:Array.from(document.querySelectorAll("base")).map(b=>({raw:b.getAttribute("href"),property:b.href})),
    parsed_against_document:parse(a.getAttribute("href"),document.URL),
    parsed_against_observed_base:parse(a.getAttribute("href"),document.baseURI)};};
  window.addEventListener("load", async()=>{
    const phases=[];
    for (const phase of ["before","after"]) {
      if(phase==="after") {__MUTATION__}
      const started_at=new Date().toISOString();
      const observation=__COLLECTOR__;
      phases.push({phase,started_at,observed_at:new Date().toISOString(),observation,direct:direct()});
    }
    const value={kind:"base-uri-diagnostic-export",version:"1",task_id:config.id,token:config.token,
      script_sha256:config.script_sha256,context:self===top?"top":"frame",user_agent:navigator.userAgent,phases};
    // The endpoint is absolute and declared by the laboratory, unaffected by base.
    try {
      const r=await fetch(config.endpoint,{method:"POST",credentials:"omit",headers:{"Content-Type":"application/json"},body:JSON.stringify(value)});
      if(!r.ok)throw Error("Export HTTP "+r.status);
      const receipt=(await r.json()).receipt;
      document.getElementById("status").textContent="Observation conservée — pas un verdict";
      document.getElementById("receipt").textContent=receipt;
      document.getElementById("facts").textContent=JSON.stringify(phases.map(p=>({phase:p.phase,direct:p.direct})),null,2);
      if(self!==top)parent.postMessage({kind:"base-uri-case-receipt",id:config.id,receipt},config.origin);
    } catch(e) {document.getElementById("status").textContent="Échec conservé : "+String(e);}
  });
})()
