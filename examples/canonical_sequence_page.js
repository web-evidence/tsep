// SYNTHETIC sequence. One planned capture per state; no retries or API authentication.
(() => {
  const states = __STATES__;
  const actions = __ACTIONS__;
  const button = document.getElementById('advance');
  const receiptDisplay = document.getElementById('lab-receipt');
  const failures = [];
  const error = value => {
    failures.push(String(value));
    document.getElementById('lab-errors').textContent = JSON.stringify(failures);
  };
  window.addEventListener('error', e => error(e.message));
  window.addEventListener('unhandledrejection', e => error(e.reason));
  let index = -1, previousReceipt = null;
  document.getElementById('lab-agent').textContent = navigator.userAgent;
  document.getElementById('lab-url').textContent = document.URL;
  async function capture(next) {
    button.disabled = true;
    receiptDisplay.textContent = 'pending';
    document.getElementById('lab-state').textContent = states[next].id;
    index = next;
    try {
      if (next > 0) actions[next - 1]();
      const captureStarted = new Date().toISOString();
      const tree = __CAPTURE_EXPRESSION__;
      const capturedAt = new Date().toISOString();
      const payload = JSON.stringify({kind:'laboratory-page-inventory',version:'1',
        script_sha256:__SCRIPT_SHA__,context:__CONTEXT__,url:document.URL,state:states[next].id,
        sequence_index:next,action:states[next].action,previous_receipt:previousReceipt,
        user_agent:navigator.userAgent,errors:failures.slice(),
        capture_started_at:captureStarted,captured_at:capturedAt,tree});
      const bytes = await crypto.subtle.digest('SHA-256',new TextEncoder().encode(payload));
      const sha256 = Array.from(new Uint8Array(bytes), b=>b.toString(16).padStart(2,'0')).join('');
      const response = await fetch(__ENDPOINT__,{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({payload,sha256})});
      if (!response.ok) throw new Error('Receipt HTTP '+response.status);
      const received = (await response.json()).receipt;
      if (typeof received !== 'string' || !/^[0-9a-f]{64}$/.test(received)) throw new Error('Invalid receipt');
      previousReceipt = received;
      receiptDisplay.textContent = 'received:'+received;
      button.textContent = next === states.length-1 ? 'Séquence terminée' : 'Exécuter l’action '+(next+1);
      button.disabled = next === states.length-1;
    } catch (failure) {
      error(failure); receiptDisplay.textContent = 'error:'+String(failure);
      button.textContent = 'Séquence arrêtée'; // Fail closed: no next action and no retry.
    }
  }
  button.addEventListener('click',()=>{if (!button.disabled && index+1<states.length) capture(index+1);});
  window.addEventListener('load',()=>capture(0),{once:true});
})();
