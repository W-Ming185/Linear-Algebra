const $ = id => document.getElementById(id);
const macros = [
  {key:'protein', label:'Protein', input:'tProtein'},
  {key:'carb', label:'Carb', input:'tCarb'},
  {key:'fat', label:'Fat', input:'tFat'},
  {key:'fiber', label:'Fiber', input:'tFiber'}
];
let DB = [], chosen = [], picked = null, revision = 0, hasResult = false;
const elInput = $('ingName'), elSuggest = $('suggest');
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
const number = n => Number(n).toLocaleString('en-US', {maximumFractionDigits:2});

function getTargets() {
  return Object.fromEntries(macros.map(m => [m.key, $(m.input).value === '' ? null : Number($(m.input).value)]));
}

// Zero targets have no percentage denominator; display their difference in grams.
function macroState(actual, target) {
  const delta = actual - target;
  const matched = Math.abs(delta) < 0.005;
  const percent = target > 0 ? actual / target * 100 : null;
  return {delta, matched, percent, width: target === 0 ? 100 : Math.min(100, Math.max(0, percent)), over: !matched && delta > 0};
}

function renderProgress(totals = null, targets = getTargets()) {
  let matchedCount = 0;
  $('macroProgress').innerHTML = macros.map(m => {
    const target = targets[m.key];
    const validTarget = target !== null && Number.isFinite(target) && target >= 0;
    const actual = totals ? Number(totals[m.key] ?? 0) : null;
    const state = totals && validTarget ? macroState(actual, target) : null;
    if (state?.matched) matchedCount++;
    let deltaText = validTarget ? 'รอคำนวณสูตร' : 'กรอก Target ก่อน';
    if (state) deltaText = state.matched ? 'ตรงเป้า ✓' : `${state.over ? 'เกินเป้า' : 'ยังขาด'} ${number(Math.abs(state.delta))} g`;
    const percentage = state ? (state.percent === null ? 'Target 0 g' : `${number(state.percent)}%`) : '—';
    const valueText = state ? `${m.label} ${number(actual)} กรัม จากเป้าหมาย ${number(target)} กรัม, ${deltaText}` : `${m.label}: ${deltaText}`;
    return `<div class="macro-row ${m.key} ${state?.over ? 'over' : ''} ${state?.matched ? 'matched' : ''}">
      <div class="macro-heading"><span class="macro-name"><i></i>${m.label}</span><span class="macro-amount"><strong>${actual === null ? '—' : number(actual)}</strong> / ${validTarget ? number(target) : '—'} g</span></div>
      <div class="bar-track" role="progressbar" aria-label="${m.label}" aria-valuemin="0" aria-valuemax="100" ${state ? `aria-valuenow="${state.width}"` : ''} aria-valuetext="${esc(valueText)}"><div class="bar-fill" style="width:${state ? state.width : 0}%"></div></div>
      <div class="macro-meta"><span class="macro-delta">${deltaText}</span><span class="macro-percent">${percentage}</span></div>
    </div>`;
  }).join('');
  if (totals) $('progressStatus').textContent = matchedCount === 4 ? 'ตรงเป้าครบทั้ง 4 สารอาหารแล้ว ✓' : `คำนวณแล้ว · ตรงเป้า ${matchedCount}/4 สารอาหาร`;
}

function clearResults(message = 'รอสูตรเชคแก้วแรกของคุณ') {
  hasResult = false;
  $('recipeTableBody').innerHTML = '<tr><td colspan="3" class="empty-state">สูตรที่ใช่กำลังรอคุณอยู่<span>ตั้ง Target เลือกวัตถุดิบ แล้วกดคำนวณสูตรเชค</span></td></tr>';
  ['totalVolume','outPrice','outCal','outMethod','outError'].forEach(id => $(id).textContent = '—');
  $('outMethod').textContent = 'รอคำนวณ';
  $('progressStatus').textContent = message;
  renderProgress();
}

function invalidateResult() {
  revision++;
  $('calcMsg').textContent = '';
  const message = hasResult || $('progressStatus').textContent.includes('เปลี่ยน') ? 'เปลี่ยนข้อมูลแล้ว · กดคำนวณสูตรอีกครั้ง' : 'รอสูตรเชคแก้วแรกของคุณ';
  clearResults(message);
}
macros.forEach(m => $(m.input).addEventListener('input', invalidateResult));

async function loadIngredients() {
  try {
    const response = await fetch('/api/ingredients');
    if (!response.ok) throw new Error('Ingredient request failed');
    DB = await response.json();
    if (elInput.value.trim()) showSuggestions();
  } catch {
    $('addMsg').textContent = 'โหลดวัตถุดิบไม่ได้ กรุณาเปิดเว็บผ่าน Flask ที่ http://127.0.0.1:5000 แล้วลองรีเฟรช';
  }
}

function hideSuggestions() { elSuggest.classList.add('hidden'); elInput.setAttribute('aria-expanded', 'false'); }
function showSuggestions() {
  const q = elInput.value.trim().toLowerCase();
  picked = null;
  if (!q) { hideSuggestions(); return; }
  const words = q.split(/\s+/);
  const hits = DB.filter(i => words.every(w => i.name.toLowerCase().includes(w))).slice(0,30);
  elSuggest.innerHTML = hits.length ? hits.map(i => `<button type="button" data-id="${i.id}" class="suggestion">${esc(i.name)}</button>`).join('') : '<div class="no-match">ไม่พบวัตถุดิบ ลองค้นหาด้วยชื่อภาษาอังกฤษ</div>';
  elSuggest.classList.remove('hidden');
  elInput.setAttribute('aria-expanded', 'true');
}
elInput.addEventListener('input', showSuggestions);
elInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') { e.preventDefault(); addIngredient(); }
  if (e.key === 'Escape') hideSuggestions();
  if (e.key === 'ArrowDown' && !elSuggest.classList.contains('hidden')) { e.preventDefault(); elSuggest.querySelector('button')?.focus(); }
});
elSuggest.addEventListener('click', e => {
  const button = e.target.closest('[data-id]');
  if (!button) return;
  picked = DB.find(i => i.id === Number(button.dataset.id));
  elInput.value = picked.name;
  hideSuggestions();
  $('addBtn').focus();
});
elSuggest.addEventListener('keydown', e => {
  if (e.key === 'Escape') { hideSuggestions(); elInput.focus(); }
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    e.preventDefault();
    const next = e.key === 'ArrowDown' ? e.target.nextElementSibling : e.target.previousElementSibling;
    next?.focus();
  }
});
document.addEventListener('click', e => { if (!elSuggest.contains(e.target) && e.target !== elInput) hideSuggestions(); });

function addIngredient() {
  $('addMsg').textContent = '';
  const query = elInput.value.trim().toLowerCase();
  if (!query) { elInput.focus(); return; }
  let item = picked || DB.find(i => i.name.toLowerCase() === query);
  if (!item) {
    const words = query.split(/\s+/);
    const hits = DB.filter(i => words.every(w => i.name.toLowerCase().includes(w)));
    if (hits.length === 1) item = hits[0];
    else { $('addMsg').textContent = hits.length ? 'พบหลายรายการ กรุณาเลือกวัตถุดิบจากรายการค้นหา' : 'ไม่พบวัตถุดิบนี้ ลองค้นหาด้วยชื่อภาษาอังกฤษ'; return; }
  }
  if (chosen.some(i => i.id === item.id)) { $('addMsg').textContent = 'เพิ่มวัตถุดิบนี้แล้ว เลือกรายการอื่นได้เลย'; return; }
  chosen.push({...item, min_g:0});
  elInput.value = ''; picked = null; hideSuggestions();
  invalidateResult(); renderInputList(); elInput.focus();
}
$('addBtn').addEventListener('click', addIngredient);

function renderInputList() {
  $('ingredientCount').textContent = `${chosen.length} รายการ`;
  $('inputTableBody').innerHTML = chosen.length ? chosen.map(i => `<tr><td>${esc(i.name)}</td><td>${number(i.protein)}</td><td>${number(i.carb)}</td><td>${number(i.fat)}</td><td>${number(i.fiber)}</td><td><input aria-label="ปริมาณขั้นต่ำ ${esc(i.name)} หน่วยกรัม" type="number" min="0" step="1" value="${i.min_g}" data-min-id="${i.id}"></td><td><button class="remove-button" data-remove-id="${i.id}" aria-label="ลบ ${esc(i.name)}">×</button></td></tr>`).join('') : '<tr><td colspan="7" class="empty-state">เริ่มจากวัตถุดิบที่คุณชอบ<span>ค้นหาแล้วกด + เพิ่ม เพื่อสร้างเชคแก้วแรก</span></td></tr>';
}
$('inputTableBody').addEventListener('click', e => {
  const button = e.target.closest('[data-remove-id]');
  if (!button) return;
  chosen = chosen.filter(i => i.id !== Number(button.dataset.removeId));
  invalidateResult(); renderInputList();
});
$('inputTableBody').addEventListener('input', e => {
  if (!e.target.matches('[data-min-id]')) return;
  const item = chosen.find(i => i.id === Number(e.target.dataset.minId));
  item.min_g = e.target.value === '' ? 0 : Number(e.target.value);
  invalidateResult();
});

async function calculateRecipe() {
  const msg = $('calcMsg'); msg.textContent = '';
  const targets = getTargets();
  if (Object.values(targets).some(v => v === null || !Number.isFinite(v) || v < 0)) { msg.textContent = 'กรุณากรอก Target ทั้ง 4 ช่อง เป็นตัวเลขตั้งแต่ 0 ขึ้นไป'; return; }
  if (!chosen.length) { msg.textContent = 'เพิ่มวัตถุดิบอย่างน้อย 1 รายการก่อนคำนวณ'; return; }
  if (chosen.some(i => !Number.isFinite(i.min_g) || i.min_g < 0 || !Number.isInteger(i.min_g))) { msg.textContent = 'ปริมาณขั้นต่ำต้องเป็นจำนวนเต็ม ตั้งแต่ 0 กรัมขึ้นไป'; return; }
  const requestRevision = revision;
  $('calcBtn').disabled = true; $('calcLabel').textContent = 'กำลังมิกซ์สูตรของคุณ…';
  clearResults('กำลังคำนวณความใกล้ Target…');
  try {
    const response = await fetch('/api/solve', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({...targets, items:chosen.map(i => ({id:i.id,min_g:i.min_g}))})});
    const data = await response.json();
    if (requestRevision !== revision) { msg.textContent = 'ข้อมูลเปลี่ยนระหว่างคำนวณ กรุณากดคำนวณอีกครั้ง'; return; }
    if (!response.ok || !data.ok) throw new Error(data.error || 'คำนวณสูตรไม่สำเร็จ');
    showResult(data, targets);
  } catch (error) {
    if (requestRevision !== revision) return;
    clearResults('ยังคำนวณไม่สำเร็จ · ลองอีกครั้ง');
    msg.textContent = error.message === 'Failed to fetch' ? 'เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ กรุณาตรวจสอบว่า Flask ทำงานอยู่' : error.message;
  } finally { $('calcBtn').disabled = false; $('calcLabel').textContent = 'คำนวณสูตรเชค'; }
}
$('calcBtn').addEventListener('click', calculateRecipe);

function showResult(data, targets) {
  hasResult = true;
  $('recipeTableBody').innerHTML = data.items.map((item,n) => `<tr><td>${String(n+1).padStart(2,'0')}</td><td>${esc(item.name)}</td><td>${number(item.grams)} g</td></tr>`).join('');
  $('totalVolume').textContent = number(data.items.reduce((sum,item) => sum + item.grams,0));
  $('outPrice').textContent = Number(data.totals.price ?? 0).toFixed(2);
  $('outCal').textContent = number(Math.round(data.totals.kcal ?? 0));
  const methodNames = {LS: 'Bounded Least Squares (LS)', NNLS: 'Non-negative Least Squares (NNLS)'};
  $('outMethod').textContent = methodNames[data.method] || data.method || 'ไม่ได้รับ Method จากเซิร์ฟเวอร์';
  $('outError').textContent = data.error ?? '—';
  renderProgress(data.totals, targets);
}
renderInputList(); clearResults(); loadIngredients();
