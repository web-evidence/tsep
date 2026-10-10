(() => {
  const config=__CONFIG__, results=[], errors=[];
  const status=document.getElementById("status");
  const run = async () => {
    for (const task of config.tasks) {
      status.textContent="Mesure "+task.id+" ("+(results.length+1)+"/"+config.tasks.length+")";
      const frame=document.createElement("iframe"), started_at=new Date().toISOString();
      const result=await new Promise((resolve,reject) => {
        const listener=event => {
          if (event.source!==frame.contentWindow || event.origin!==config.origin) return;
          if (event.data.kind!=="rendered-link-case" || event.data.id!==task.id) return;
          clearTimeout(timer); window.removeEventListener("message",listener);
          resolve({id:task.id,url:task.url,started_at,observed_at:event.data.observed_at,observation:event.data.observation});
        };
        const timer=setTimeout(() => {window.removeEventListener("message",listener);reject(new Error("Case timeout: "+task.id));},10000);
        window.addEventListener("message",listener);frame.src=task.url;document.getElementById("frames").append(frame);
      });
      results.push(result);frame.remove();
    }
  };
  run().catch(error => errors.push(String(error))).then(async () => {
    const data={kind:"rendered-link-browser-campaign",version:"1",token:config.token,plan_sha256:config.plan_sha256,
      controller_url:location.href,user_agent:navigator.userAgent,results,errors,complete:errors.length===0 && results.length===config.tasks.length};
    try {
      const response=await fetch(config.endpoint,{method:"POST",credentials:"omit",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
      if (!response.ok) throw new Error("Export HTTP "+response.status);
      const receipt=await response.json();document.getElementById("receipt").textContent=receipt.receipt;
      status.textContent=data.complete ? "26 observations conservées — analyse hors ligne à effectuer" : "Campagne incomplète — échec conservé";
    } catch (error) {status.textContent="Export non confirmé : "+String(error);}
  });
})()
