// SYNTHETIC laboratory: one actual navigation and one declared load-state export.
(() => {
  const failures = [];
  window.addEventListener('error', event => failures.push(String(event.message)));
  window.addEventListener('unhandledrejection', event => failures.push(String(event.reason)));
  window.addEventListener('load', async () => {
    const receipt = document.getElementById('lab-receipt');
    try {
      const mutation = __MUTATION__;
      if (mutation === 'noindex') {
        const meta = document.createElement('meta'); meta.name='robots'; meta.content='noindex';
        document.head.appendChild(meta);
      } else if (mutation === 'canonical') {
        document.getElementById('primary-canonical').href = document.URL + '/other';
      } else if (mutation === 'links') {
        document.getElementById('family-link').href = document.URL + '?variant=1';
      } else if (mutation === 'node-limit') {
        for (let i=0; i<1200; i++) document.body.appendChild(document.createElement('span'));
      }
      document.getElementById('lab-state').textContent = 'load-state';
      const started = new Date().toISOString();
      const tree = __CAPTURE_EXPRESSION__;
      const captured = new Date().toISOString();
      const payload = JSON.stringify({kind:'same-navigation-page',version:'1',context:__CONTEXT__,
        task_id:__TASK__,navigation_id:__NAVIGATION__,url:document.URL,user_agent:navigator.userAgent,
        script_sha256:__SCRIPT_SHA__,capture_started_at:started,captured_at:captured,errors:failures,tree});
      const bytes = new TextEncoder().encode(payload);
      const digest = await crypto.subtle.digest('SHA-256',bytes);
      const sha256 = Array.from(new Uint8Array(digest), b=>b.toString(16).padStart(2,'0')).join('');
      const response = await fetch(__ENDPOINT__, {method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({payload,sha256})});
      const answer = await response.json();
      if (!response.ok) throw new Error(answer.error || 'Capture refused');
      receipt.textContent='received:'+answer.receipt;
    } catch (error) { receipt.textContent='error:'+String(error); }
  }, {once:true});
})();
