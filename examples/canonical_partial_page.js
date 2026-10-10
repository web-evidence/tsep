// SYNTHETIC family laboratory. A real browser visit, never a simulated DOM.
(() => {
  const errors = [];
  const sha = async bytes => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)),
    value => value.toString(16).padStart(2, '0')).join('');
  window.addEventListener('error', event => errors.push(String(event.message)));
  window.addEventListener('unhandledrejection', event => errors.push(String(event.reason)));
  window.addEventListener('load', async () => {
    try {
      const sitemapURL = __SITEMAP__;
      let auxiliary = null;
      if (sitemapURL !== null) {
        const response = await fetch(sitemapURL, {cache:'no-store', credentials:'omit', redirect:'error'});
        const bytes = await response.arrayBuffer();
        auxiliary = {url:response.url, status:response.status, body_sha256:await sha(bytes)};
        if (!response.ok) throw new Error('Sitemap HTTP '+response.status);
        document.getElementById('lab-sitemap').textContent = auxiliary.body_sha256;
      }
      document.getElementById('lab-state').textContent = 'load-state';
      const started = new Date().toISOString();
      const tree = __CAPTURE_EXPRESSION__;
      const payload = JSON.stringify({kind:'canonical-family-page',version:'1',context:__CONTEXT__,
        task_id:__TASK__,navigation_id:__NAVIGATION__,url:document.URL,user_agent:navigator.userAgent,
        script_sha256:__SCRIPT_SHA__,capture_started_at:started,captured_at:new Date().toISOString(),
        errors,tree,auxiliary});
      const body = JSON.stringify({payload,sha256:await sha(new TextEncoder().encode(payload))});
      const response = await fetch(__ENDPOINT__, {method:'POST',credentials:'omit',
        headers:{'Content-Type':'application/json'},body});
      const answer = await response.json();
      if (!response.ok) throw new Error(answer.error || 'Capture refused');
      document.getElementById('lab-receipt').textContent = 'received:'+answer.receipt;
    } catch (error) { document.getElementById('lab-receipt').textContent = 'error:'+String(error); }
  }, {once:true});
})();
