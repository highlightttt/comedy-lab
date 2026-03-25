// Comedy Lab Feedback System v4
// Saves to localStorage + syncs to GitHub repo file via commit API
// Falls back to local-only if GitHub unavailable
(function() {
  const PAGE = document.title || location.pathname;
  const FB_KEY = 'comedy-fb-' + PAGE.replace(/[^a-z0-9]/gi, '-');
  const PENDING_KEY = 'comedy-fb-pending';
  
  function loadFB() { try { return JSON.parse(localStorage.getItem(FB_KEY)) || {}; } catch(e) { return {}; } }
  function saveFB(d) { localStorage.setItem(FB_KEY, JSON.stringify(d)); updateBar(d); }
  
  function loadPending() { try { return JSON.parse(localStorage.getItem(PENDING_KEY)) || []; } catch(e) { return []; } }
  function savePending(arr) { localStorage.setItem(PENDING_KEY, JSON.stringify(arr)); }
  
  function addPending(entry) {
    const arr = loadPending();
    arr.push(entry);
    savePending(arr);
  }

  function updateBar(d) {
    const bar = document.getElementById('fbBar');
    const count = document.getElementById('fbCount');
    if (!bar || !count) return;
    const c = Object.keys(d).length;
    count.textContent = c;
    bar.classList.toggle('visible', c > 0);
  }

  function createModal() {
    if (document.getElementById('fb-modal')) return;
    const modal = document.createElement('div');
    modal.id = 'fb-modal';
    modal.innerHTML = `
      <div class="fb-modal-backdrop" onclick="window._fbCloseModal()"></div>
      <div class="fb-modal-box">
        <div class="fb-modal-header">
          <span class="fb-modal-vote-icon"></span>
          <span class="fb-modal-title">Why?</span>
          <button class="fb-modal-close" onclick="window._fbCloseModal()">✕</button>
        </div>
        <div class="fb-modal-joke"></div>
        <textarea class="fb-modal-input" placeholder="What made this funny / not funny? What inspired you? (optional)" rows="3"></textarea>
        <div class="fb-modal-actions">
          <button class="fb-modal-skip" onclick="window._fbSubmitModal('')">Skip</button>
          <button class="fb-modal-submit" onclick="window._fbSubmitModal(document.querySelector('.fb-modal-input').value)">Save</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    const style = document.createElement('style');
    style.textContent = `
      #fb-modal{display:none;position:fixed;inset:0;z-index:10000}
      #fb-modal.open{display:flex;align-items:center;justify-content:center}
      .fb-modal-backdrop{position:absolute;inset:0;background:rgba(0,0,0,0.7);backdrop-filter:blur(4px)}
      .fb-modal-box{position:relative;background:#141414;border:1px solid #2a2a2a;border-radius:16px;padding:1.5rem;width:90%;max-width:480px;font-family:'Space Grotesk','Noto Sans SC',sans-serif}
      .fb-modal-header{display:flex;align-items:center;gap:10px;margin-bottom:1rem}
      .fb-modal-vote-icon{font-size:1.5rem}
      .fb-modal-title{flex:1;font-size:1rem;font-weight:600;color:#eaeaea}
      .fb-modal-close{background:none;border:none;color:#777;font-size:1.2rem;cursor:pointer;padding:4px 8px}
      .fb-modal-close:hover{color:#eaeaea}
      .fb-modal-joke{font-size:0.82rem;color:#999;line-height:1.5;margin-bottom:1rem;padding:0.8rem;background:#0e0e0e;border-radius:8px;border:1px solid #1e1e1e;max-height:80px;overflow-y:auto}
      .fb-modal-input{width:100%;background:#0e0e0e;border:1px solid #2a2a2a;border-radius:10px;padding:0.8rem;color:#eaeaea;font-size:0.85rem;font-family:inherit;resize:none;outline:none;transition:border-color 0.2s}
      .fb-modal-input:focus{border-color:#ff6b35}
      .fb-modal-input::placeholder{color:#555}
      .fb-modal-actions{display:flex;gap:8px;margin-top:1rem;justify-content:flex-end}
      .fb-modal-skip{background:none;border:1px solid #2a2a2a;border-radius:8px;padding:8px 16px;color:#777;font-size:0.8rem;cursor:pointer;font-family:inherit}
      .fb-modal-skip:hover{border-color:#444;color:#aaa}
      .fb-modal-submit{background:#ff6b35;border:none;border-radius:8px;padding:8px 20px;color:#000;font-weight:600;font-size:0.8rem;cursor:pointer;font-family:inherit}
      .fb-modal-submit:hover{opacity:0.85}
      .fb-modal-saved{text-align:center;padding:2rem;font-size:0.9rem}
      .fb-modal-saved.ok{color:#30d158}
    `;
    document.body.appendChild(style);
  }

  let pendingVote = null;

  window._fbCloseModal = function() {
    document.getElementById('fb-modal')?.classList.remove('open');
    pendingVote = null;
  };

  window._fbSubmitModal = function(comment) {
    if (!pendingVote) return;
    const entry = {
      vote: pendingVote.vote,
      text: pendingVote.text,
      comment: comment.trim(),
      page: PAGE,
      jid: pendingVote.jid,
      time: new Date().toISOString()
    };

    // Save locally
    const data = loadFB();
    data[pendingVote.jid] = entry;
    saveFB(data);

    // Queue for server sync
    addPending(entry);

    // Try local server
    fetch('/vote', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(entry)
    }).catch(() => {});

    // Update button visual
    const wrap = document.querySelector(`.fb-wrap[data-jid="${pendingVote.jid}"]`);
    if (wrap) {
      wrap.querySelectorAll('.fb-btn').forEach(b => b.classList.remove('active-up', 'active-down'));
      const activeBtn = wrap.querySelector(`[data-vote="${pendingVote.vote}"]`);
      if (activeBtn) activeBtn.classList.add(pendingVote.vote === 'up' ? 'active-up' : 'active-down');
    }

    // Show confirmation
    const box = document.querySelector('.fb-modal-box');
    box.innerHTML = `<div class="fb-modal-saved ok">✅ Saved!</div>`;
    setTimeout(() => window._fbCloseModal(), 800);
    pendingVote = null;
  };

  window.vote = function(btn) {
    if (btn.closest('a.ref-card')) { event.preventDefault(); event.stopPropagation(); }
    createModal();
    const wrap = btn.closest('.fb-wrap');
    const jid = wrap.dataset.jid;
    const v = btn.dataset.vote;
    const data = loadFB();

    if (data[jid] && data[jid].vote === v) {
      delete data[jid];
      wrap.querySelectorAll('.fb-btn').forEach(b => b.classList.remove('active-up', 'active-down'));
      saveFB(data);
      return;
    }

    const parent = wrap.closest('li') || wrap.closest('.ref-card') || wrap.closest('a') || wrap.closest('.joke');
    let text = '';
    if (parent) text = parent.textContent.replace(/👍|👎|Skip|Save|Why\?/g, '').trim().substring(0, 200);

    pendingVote = { jid, vote: v, text };
    const modal = document.getElementById('fb-modal');
    const box = modal.querySelector('.fb-modal-box');
    box.innerHTML = `
      <div class="fb-modal-header">
        <span class="fb-modal-vote-icon">${v === 'up' ? '👍' : '👎'}</span>
        <span class="fb-modal-title">Why?</span>
        <button class="fb-modal-close" onclick="window._fbCloseModal()">✕</button>
      </div>
      <div class="fb-modal-joke">${text.replace(/</g,'&lt;')}</div>
      <textarea class="fb-modal-input" placeholder="What made this funny / not funny? What inspired you? (optional)" rows="3"></textarea>
      <div class="fb-modal-actions">
        <button class="fb-modal-skip" onclick="window._fbSubmitModal('')">Skip</button>
        <button class="fb-modal-submit" onclick="window._fbSubmitModal(document.querySelector('.fb-modal-input').value)">Save</button>
      </div>
    `;
    modal.classList.add('open');
    setTimeout(() => modal.querySelector('.fb-modal-input')?.focus(), 100);
  };

  // Sync pending feedback to server when page loads (catches mobile feedback next time on desktop)  
  window._syncPending = function() {
    const pending = loadPending();
    if (!pending.length) return;
    fetch('/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({page: PAGE, feedback: Object.fromEntries(pending.map(p => [p.jid, p]))})
    }).then(r => { if (r.ok) savePending([]); }).catch(() => {});
  };

  window.exportFeedback = function() {
    const data = loadFB();
    navigator.clipboard.writeText(JSON.stringify({page: PAGE, feedback: data}, null, 2)).then(() => {
      const btn = document.querySelector('.fb-bar button');
      if (btn) { btn.textContent = '✅ Copied!'; setTimeout(() => btn.textContent = '📋 Copy Feedback', 2000); }
    });
  };

  document.addEventListener('DOMContentLoaded', () => {
    const data = loadFB();
    updateBar(data);
    Object.entries(data).forEach(([jid, info]) => {
      const wrap = document.querySelector(`.fb-wrap[data-jid="${jid}"]`);
      if (wrap) {
        const btn = wrap.querySelector(`[data-vote="${info.vote}"]`);
        if (btn) btn.classList.add(info.vote === 'up' ? 'active-up' : 'active-down');
      }
    });
    window._syncPending();
  });
})();
