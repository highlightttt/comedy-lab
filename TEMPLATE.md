# Comedy Lab HTML Template Guide

When generating daily report HTML pages, follow these rules EXACTLY:

## Feedback Buttons (CRITICAL)
Every joke MUST use this exact structure:

```html
<li>Joke text here<span class="fb-wrap" data-jid="joke-1"><button class="fb-btn" data-vote="up" onclick="vote(this)">👍</button><button class="fb-btn" data-vote="down" onclick="vote(this)">👎</button></span></li>
```

- Each joke gets a unique `data-jid` (e.g., joke-1, joke-2, etc.)
- Reference cards use `data-jid="ref-1"` etc.
- NEVER use bare `<button>👍</button>` without the wrapper

## Script Reference (CRITICAL)
Before `</body>`, include EXACTLY:
```html
<script src="feedback.js"></script>
```
Do NOT inline the feedback JavaScript. Always reference the shared file.

## Feedback Bar
Before `</body>` and before the script tag:
```html
<div class="fb-bar" id="fbBar"><span>Marked <span class="count" id="fbCount">0</span> votes</span><button onclick="exportFeedback()">📋 Copy Feedback</button></div>
```

## Required CSS for Feedback
Include these styles in the `<style>` block:
```css
.fb-wrap{display:inline-flex;gap:4px;margin-left:8px;vertical-align:middle}
.fb-btn{background:none;border:1px solid transparent;border-radius:6px;cursor:pointer;font-size:0.85rem;padding:2px 6px;opacity:0;transition:all 0.2s;line-height:1}
li:hover .fb-btn,.ref-card:hover .fb-btn{opacity:0.5}
.fb-btn:hover{opacity:0.8!important;border-color:#333}
.fb-btn.active-up{opacity:1!important;background:rgba(48,209,88,0.15);border-color:#30d158}
.fb-btn.active-down{opacity:1!important;background:rgba(255,59,48,0.15);border-color:#ff3b30}
.fb-bar{position:fixed;bottom:0;left:0;right:0;z-index:999;background:rgba(14,14,14,0.95);backdrop-filter:blur(12px);border-top:1px solid #1e1e1e;padding:10px 24px;display:flex;align-items:center;justify-content:space-between;font-size:0.8rem;color:#777;transform:translateY(100%);transition:transform 0.3s}
.fb-bar.visible{transform:translateY(0)}
.fb-bar .count{color:#30d158;font-weight:600}
.fb-bar button{background:#ff6b35;color:#000;border:none;border-radius:8px;padding:8px 20px;font-weight:600;font-size:0.8rem;cursor:pointer;font-family:inherit}
```

## Language
- All jokes in English (Jesse performs English standup)
- Commentary/labels in English
- Chinese only when a joke specifically requires Chinese context

## Example joke list item:
```html
<li>The stronger your lunch smells, the harder you work. Curry? That team ships at midnight.<span class="tag tag-hot">🔥</span><span class="fb-wrap" data-jid="joke-3"><button class="fb-btn" data-vote="up" onclick="vote(this)">👍</button><button class="fb-btn" data-vote="down" onclick="vote(this)">👎</button></span></li>
```
