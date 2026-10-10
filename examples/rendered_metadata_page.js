// Synthetic laboratory instrumentation v1. Page world; no API authentication.
// Placeholders are replaced before source HTTP bytes are frozen.
window.addEventListener('load', async () => {
  const receipt = document.getElementById('lab-receipt');
  try {
    const captureStarted = new Date().toISOString();
    const tree = __CAPTURE_EXPRESSION__;
    const capturedAt = new Date().toISOString();
    // All mutations below occur AFTER the one synchronous traversal.
    const payload = JSON.stringify({kind:'laboratory-page-inventory',version:'1',
      script_sha256:__SCRIPT_SHA__,context:__CONTEXT__,url:document.URL,
      state:document.getElementById('lab-state').textContent,
      user_agent:navigator.userAgent,errors:JSON.parse(document.getElementById('lab-errors').textContent),
      capture_started_at:captureStarted,captured_at:capturedAt,tree});
    const digest = await crypto.subtle.digest('SHA-256',new TextEncoder().encode(payload));
    const sha256 = Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
    const response = await fetch(__ENDPOINT__,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({payload,sha256})});
    if (!response.ok) throw new Error('Receipt HTTP '+response.status);
    const result = await response.json();
    receipt.textContent = 'received:'+result.receipt;
  } catch (error) { receipt.textContent = 'error:'+String(error); }
},{once:true});
