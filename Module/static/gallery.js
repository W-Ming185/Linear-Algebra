(() => {
  const byId = id => document.getElementById(id);
  const gallery = byId('characterGallery');
  if (!gallery) return;
  const looks = [
    {file:'member-gym-power.png', name:'GYM POWER', title:'กล้ามแน่น เชคต้องถึง 🔥', alt:'ภาพ AI คนเดิมเวอร์ชันกล้ามโต ใส่เสื้อกล้ามแดง ถือโปรตีนเชคในยิม', cheer:'กล้ามพร้อม เชคพร้อม! 💪'},
    {file:'member-shake-champ.png', name:'SHAKE CHAMP', title:'แชมป์ยกเชค ไม่ยกเว้นวันพัก 💪', alt:'ภาพ AI คนเดิมกล้ามโต ใส่ชุดกีฬาแดงขาว ชูขวดโปรตีนเชค', cheer:'อีกหนึ่งเชคเพื่อแชมป์! 🏆'},
    {file:'member-banana-king.png', name:'BANANA KING', title:'ราชาโปรตีน ขี่กล้วยมาปั่น 🍌', alt:'ภาพ AI ตลก คนเดิมกล้ามยักษ์สวมมงกุฎกับผ้าคลุมแดง ขี่กล้วยยักษ์ถือเชค', cheer:'กล้วยยังยอม กล้ามไม่ยอม! 🍌'},
    {file:'member-shake-idol.png', name:'SHAKE IDOL', title:'ร้องไม่เน้น เน้นโปรตีน 🎤', alt:'ภาพ AI ตลกจากรูปในรถ เป็นนักร้องถือขวดเชคแทนไมค์ เสยผมบนเวที มีแฟนคลับกรี๊ด', cheer:'กรี๊ดได้ แต่อย่าลืมเชค! 🎤'},
    {file:'member-space-bulk.png', name:'SPACE BULK', title:'ตัวหลับ แต่กล้ามไปดาวอังคาร 🚀', alt:'ภาพ AI หลุดโลก คนเดิมหลับกล้ามโตบนยานขวดโปรตีนเชค มีวัวนักบินอวกาศกับดาวสตรอว์เบอร์รี', cheer:'นอนหนึ่งงีบ โปรตีนข้ามกาแล็กซี! 🐄🚀'},
    {file:'member-protein-chef.png', name:'PROTEIN CHEF', title:'โยนแพนเค้กที เป็ดมีตกใจ 🥞', alt:'ภาพ AI ตลก คนเดิมเป็นเชฟกล้ามโต โยนแพนเค้กสูงเป็นหอคอย มีเป็ดจิ๋วสองตัวช่วยถือโปรตีนเชค', cheer:'เชฟบอกปั่นเชค ไม่ใช่ปั่นครัว! 🥞🐥'}
  ];
  const card = byId('characterCard');
  const portrait = byId('characterImage');
  const status = byId('galleryStatus');
  const dialog = byId('portraitDialog');
  const buttons = [...gallery.querySelectorAll('[data-look]')];
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let current = 0, requested = 0, requestId = 0, power = 0, burstTimer;
  let touchStart = null, suppressClickUntil = 0;
  const source = index => '/static/assets/' + looks[index].file;

  function updateDialog() {
    byId('portraitDialogTitle').textContent = looks[current].name;
    byId('fullPortrait').src = source(current);
    byId('fullPortrait').alt = looks[current].alt;
  }

  function chooseLook(index) {
    requested = (index + looks.length) % looks.length;
    const next = requested;
    const token = ++requestId;
    if (next === current) { gallery.removeAttribute('aria-busy'); status.textContent = looks[current].cheer; return; }
    gallery.setAttribute('aria-busy', 'true');
    status.textContent = 'กำลังเปลี่ยนลุค…';
    const image = new Image();
    image.onload = () => {
      if (token !== requestId) return;
      current = next;
      portrait.src = source(current);
      portrait.alt = looks[current].alt;
      byId('characterTag').textContent = looks[current].name;
      byId('characterTitle').textContent = looks[current].title;
      byId('galleryIndex').textContent = String(current + 1).padStart(2, '0');
      buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === current)));
      card.classList.toggle('is-comedy', current >= 2);
      gallery.removeAttribute('aria-busy');
      status.textContent = looks[current].cheer;
      if (dialog.open) updateDialog();
    };
    image.onerror = () => {
      if (token !== requestId) return;
      requested = current;
      gallery.removeAttribute('aria-busy');
      status.textContent = 'โหลดรูปไม่สำเร็จ ลองเลือกลุคอีกครั้ง';
    };
    image.src = source(next);
  }

  function updatePower() {
    byId('powerValue').textContent = power + '%';
    byId('powerFill').style.width = power + '%';
    byId('powerMeter').setAttribute('aria-valuenow', String(power));
    card.style.setProperty('--fire-power', String(1 + power / 300));
    card.classList.toggle('is-max-power', power === 100);
  }

  function boost() {
    if (Date.now() < suppressClickUntil) return;
    power = Math.min(100, power + 20);
    updatePower();
    byId('powerPop').textContent = power === 100 ? 'MAX POWER 🔥' : '+20 POWER';
    status.textContent = power === 100 ? 'ไฟลุกเต็มพลัง! ' + looks[current].cheer : `พลังไฟ ${power}% · ${looks[current].cheer}`;
    clearTimeout(burstTimer);
    card.classList.remove('is-boosting');
    // Restart a short burst on each click; no looping camera shake or flashing.
    void card.offsetWidth;
    card.classList.add('is-boosting');
    burstTimer = setTimeout(() => card.classList.remove('is-boosting'), 650);
  }

  buttons.forEach(button => button.addEventListener('click', () => chooseLook(Number(button.dataset.look))));
  byId('previousLook').addEventListener('click', () => chooseLook(requested - 1));
  byId('nextLook').addEventListener('click', () => chooseLook(requested + 1));
  byId('boostCharacter').addEventListener('click', boost);
  byId('resetPower').addEventListener('click', () => {
    power = 0; updatePower(); clearTimeout(burstTimer);
    card.classList.remove('is-boosting');
    status.textContent = 'เริ่มใหม่! กดรูปเพื่อเติมพลังไฟ';
  });
  gallery.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault(); chooseLook(requested + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  card.addEventListener('pointermove', event => {
    if (event.pointerType !== 'mouse' || reducedMotion.matches) return;
    const rect = card.getBoundingClientRect();
    card.style.setProperty('--tilt-x', `${-(event.clientY - rect.top - rect.height / 2) / rect.height * 8}deg`);
    card.style.setProperty('--tilt-y', `${(event.clientX - rect.left - rect.width / 2) / rect.width * 8}deg`);
  });
  function resetTilt() { card.style.setProperty('--tilt-x', '0deg'); card.style.setProperty('--tilt-y', '0deg'); }
  card.addEventListener('pointerleave', resetTilt);
  reducedMotion.addEventListener('change', resetTilt);
  card.addEventListener('pointerdown', event => {
    if (event.pointerType === 'touch') touchStart = {x:event.clientX, y:event.clientY};
  });
  card.addEventListener('pointercancel', () => { touchStart = null; });
  card.addEventListener('pointerup', event => {
    if (!touchStart) return;
    const dx = event.clientX - touchStart.x, dy = event.clientY - touchStart.y;
    touchStart = null;
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) {
      suppressClickUntil = Date.now() + 450;
      chooseLook(requested + (dx < 0 ? 1 : -1));
    }
  });

  byId('openPortrait').addEventListener('click', () => { updateDialog(); dialog.showModal(); });
  byId('closePortrait').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => byId('openPortrait').focus());
})();
