// Instrumented SYNTHETIC laboratory. One callback, not API authentication.
(() => {
  async function capture() {
    const receipt = document.getElementById('lab-receipt');
    try {
      const captureStarted = new Date().toISOString();
      const tree = __CAPTURE_EXPRESSION__;
      const capturedAt = new Date().toISOString();
      const payload = JSON.stringify({kind:'laboratory-page-inventory',version:'1',
        script_sha256:__SCRIPT_SHA__,context:__CONTEXT__,url:document.URL,
        state:__TRIGGER__,user_agent:navigator.userAgent,
        errors:JSON.parse(document.getElementById('lab-errors').textContent),
        capture_started_at:captureStarted,captured_at:capturedAt,tree});
      const digest = await crypto.subtle.digest('SHA-256',new TextEncoder().encode(payload));
      const sha256 = Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
      const response = await fetch(__ENDPOINT__,{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({payload,sha256})});
      if (!response.ok) throw new Error('Receipt HTTP '+response.status);
      receipt.textContent = 'received:'+(await response.json()).receipt;
    } catch (error) { receipt.textContent = 'error:'+String(error); }
  }
  if (__TRIGGER__ === 'during-parsing') capture();
  else window.addEventListener('load',capture,{once:true});
})();
