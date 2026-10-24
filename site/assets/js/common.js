// Fonctions partagées par toutes les pages du site FarLands Leaks.

export const REPO = 'RyusAceVA/fragpunk-assets';
const LOCAL = location.protocol === 'file:' || ['localhost', '127.0.0.1', ''].includes(location.hostname);

// Les fichiers lourds (vidéos, modèles 3D, PNG d'origine) restent dans le dépôt et passent par
// jsDelivr, comme sur FragTracker : raw.githubusercontent n'est pas un CDN et sature sous la charge.
// En local (serveur lancé à la racine du dépôt), on lit directement les fichiers.
export const MEDIA = LOCAL ? new URL('../', location.href).href : `https://cdn.jsdelivr.net/gh/${REPO}@main/`;
export const RAW = `https://raw.githubusercontent.com/${REPO}/main/`;
export const GITHUB = `https://github.com/${REPO}/blob/main/`;
export const media = (path) => MEDIA + path;
export const img = (name) => `img/${name}.webp`;

/** Repasse sur raw.githubusercontent si le CDN échoue. */
export function withFallback(el, path) {
  el.addEventListener('error', function retry() {
    el.removeEventListener('error', retry);
    if (!el.src.startsWith(RAW)) el.src = RAW + path;
  });
  return el;
}

export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

export function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k === 'html') el.innerHTML = v;
    else if (k === 'style' && typeof v === 'object') Object.assign(el.style, v);
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? '' : v);
  }
  for (const c of children.flat()) {
    if (c == null || c === false) continue;
    el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return el;
}

export async function loadJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path} : ${res.status}`);
  return res.json();
}

/* ---------- Langue des textes du jeu ---------- */

const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* stockage indisponible */ } },
};

export function getLang() { return document.documentElement.dataset.lang || 'fr'; }

function setLang(lang) {
  document.documentElement.dataset.lang = lang;
  store.set('fl-lang', lang);
  $$('.lang-toggle button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.lang === lang)));
  document.dispatchEvent(new CustomEvent('langchange', { detail: lang }));
}

/**
 * Rend un texte du jeu { en, fr, zh?, s } avec ses deux versions (le bouton FR/EN choisit
 * laquelle est visible) et un badge qui renvoie à sa ligne dans l'explorateur de textes.
 */
export function gt(t, { tag = 'span', cls = '', src = true } = {}) {
  const el = h(tag, { class: ('gq ' + cls).trim() });
  if (!t) return el;
  if (t.zh && !t.en) {
    el.append(h('span', {}, ph(t.fr || t.zh)));
    el.append(h('span', { class: 't-zh', lang: 'zh' }, 'VO chinoise : ' + t.zh));
  } else {
    el.append(h('span', { class: 't-en', lang: 'en' }, ph(t.en)));
    const fr = h('span', { class: 't-fr', lang: t.fr ? 'fr' : 'en', title: t.fr ? 'VO : ' + t.en : null }, ph(t.fr || t.en));
    if (!t.fr) fr.append(h('span', { class: 'nofr' }, 'VO, pas de VF'));
    el.append(fr);
  }
  if (src && t.s) el.append(srcBadge(t.s));
  return el;
}

/** Les {1}, {2}… du jeu sont des variables remplies en partie (nom d'objet, touche, nombre). */
const ph = (s) => (s || '').replace(/\{\d\}/g, '[…]');

export function srcBadge(s) {
  const [table, key] = s.split(':');
  return h('a', {
    class: 'src', href: `textes.html?k=${encodeURIComponent(key || table)}`,
    title: `Source : _tous_les_textes_du_jeu.tsv, table ${table}${key ? ', clé ' + key + '…' : ''}`,
  }, key ? key.slice(0, 6) : table);
}

/** Texte brut d'un texte du jeu dans la langue choisie. */
export function txt(t) {
  if (!t) return '';
  if (t.zh && !t.en) return ph(t.fr || t.zh);
  return ph(getLang() === 'en' ? t.en : (t.fr || t.en));
}

/* ---------- Titres glitch ---------- */

export function glitchify(root = document) {
  $$('[data-glitch]:not(.glitch)', root).forEach((el) => {
    const text = el.dataset.glitch || el.textContent.trim();
    el.classList.add('glitch');
    el.setAttribute('aria-label', text);
    el.textContent = '';
    ['g0', 'g1', 'g2'].forEach((c, i) => el.append(h('span', { class: c, 'aria-hidden': i ? 'true' : null }, text)));
  });
}

/* ---------- Navigation ---------- */

function initNav() {
  const nav = $('.nav');
  if (!nav) return;
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 10);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
  const burger = $('.burger');
  const links = $('.nav-links');
  if (burger && links) {
    burger.addEventListener('click', () => {
      const open = links.classList.toggle('open');
      burger.setAttribute('aria-expanded', String(open));
    });
    links.addEventListener('click', (e) => {
      if (e.target.closest('a')) { links.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); }
    });
  }
  const page = location.pathname.split('/').pop() || 'index.html';
  $$('.nav-links a').forEach((a) => {
    if (a.getAttribute('href') === page) a.classList.add('active');
  });
}

/* ---------- Apparition au défilement ---------- */

export function reveal(root = document) {
  const els = $$('.reveal:not(.in)', root);
  if (!('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('in')); return; }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
  }, { rootMargin: '0px 0px -8% 0px' });
  els.forEach((e) => io.observe(e));
}

/* ---------- Modale (images, vidéos, documents) ---------- */

const ICONS = {
  x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>',
  l: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m15 18-6-6 6-6"/></svg>',
  r: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 18 6-6-6-6"/></svg>',
};

let modal; let state = null; let lastFocus = null;

function ensureModal() {
  if (modal) return modal;
  modal = h('div', { class: 'modal', role: 'dialog', 'aria-modal': 'true', 'aria-label': 'Aperçu' },
    h('div', { class: 'backdrop', onclick: closeModal }),
    h('div', { class: 'box' }, h('div', { class: 'inner' })),
    h('button', { class: 'round-btn close', 'aria-label': 'Fermer', html: ICONS.x, onclick: closeModal }),
    h('button', { class: 'round-btn prev', 'aria-label': 'Précédent', html: ICONS.l, onclick: () => step(-1) }),
    h('button', { class: 'round-btn next', 'aria-label': 'Suivant', html: ICONS.r, onclick: () => step(1) }),
  );
  document.body.append(modal);
  document.addEventListener('keydown', (e) => {
    if (!modal.classList.contains('open')) return;
    if (e.key === 'Escape') closeModal();
    if (e.key === 'ArrowRight') step(1);
    if (e.key === 'ArrowLeft') step(-1);
  });
  return modal;
}

function openShell(kind) {
  ensureModal();
  lastFocus = document.activeElement;
  modal.className = 'modal open ' + kind;
  document.body.style.overflow = 'hidden';
  requestAnimationFrame(() => modal.classList.add('show'));
  $('.close', modal).focus();
  return $('.inner', modal);
}

export function closeModal() {
  if (!modal) return;
  $$('video', modal).forEach((v) => v.pause());
  modal.classList.remove('show', 'open');
  $('.inner', modal).innerHTML = '';
  document.body.style.overflow = '';
  state = null;
  if (lastFocus) lastFocus.focus();
}

function step(d) {
  if (!state || state.items.length < 2) return;
  state.index = (state.index + d + state.items.length) % state.items.length;
  state.render();
}

/**
 * Visionneuse d'images. items : [{ thumb, file, caption }]. La vignette WebP s'affiche tout de suite,
 * puis l'image d'origine (PNG du dépôt) la remplace une fois chargée.
 */
export function openLightbox(items, index = 0) {
  const inner = openShell('lightbox');
  state = { items, index, render() {
    const it = this.items[this.index];
    inner.innerHTML = '';
    const im = h('img', { src: it.thumb, alt: it.caption || '' });
    inner.append(im);
    if (it.file) {
      const full = new Image();
      full.onload = () => { if (state && state.items[state.index] === it) im.src = full.src; };
      full.onerror = () => { if (!full.src.startsWith(RAW)) full.src = RAW + it.file; };
      full.src = media(it.file);
    }
    const cap = h('div', { class: 'caption' }, it.caption || '');
    if (it.file) {
      cap.append(' · ', h('a', { href: GITHUB + it.file, target: '_blank', rel: 'noopener' }, it.file.split('/').pop()));
    }
    if (this.items.length > 1) cap.append(h('span', { class: 'dim' }, `  ${this.index + 1} / ${this.items.length}`));
    inner.append(cap);
    $('.prev', modal).hidden = $('.next', modal).hidden = this.items.length < 2;
  } };
  state.render();
}

/** Lecteur vidéo. v : { file, poster, id, desc } */
export function openVideo(list, index = 0) {
  const inner = openShell('video');
  state = { items: list, index, render() {
    const v = this.items[this.index];
    inner.innerHTML = '';
    const video = h('video', { controls: true, autoplay: true, playsinline: true, preload: 'auto', poster: img(v.poster) });
    withFallback(video, v.file);
    video.src = media(v.file);
    inner.append(video, h('div', { class: 'caption' }, v.desc, ' · ',
      h('a', { href: GITHUB + v.file, target: '_blank', rel: 'noopener' }, v.id + '.mp4'),
      this.items.length > 1 ? h('span', { class: 'dim' }, `  ${this.index + 1} / ${this.items.length}`) : ''));
    $('.prev', modal).hidden = $('.next', modal).hidden = this.items.length < 2;
  } };
  state.render();
}

/** Lecteur de document (lore). */
export function openDoc(title, body) {
  const inner = openShell('doc-modal');
  state = null;
  $('.prev', modal).hidden = $('.next', modal).hidden = true;
  inner.append(h('span', { class: 'skew' }, h('span', {}, 'Document du jeu')), h('h2', {}, title));
  const meta = h('p', { class: 'dim' }, 'Texte d\'origine du jeu. ');
  meta.append(srcBadge(body.s));
  inner.append(meta, gt(body, { tag: 'div', cls: 'doc-text', src: false }));
}

/* ---------- Démarrage ---------- */

export function boot() {
  const saved = store.get('fl-lang');
  document.documentElement.dataset.lang = saved === 'en' ? 'en' : 'fr';
  $$('.lang-toggle button').forEach((b) => {
    b.setAttribute('aria-pressed', String(b.dataset.lang === getLang()));
    b.addEventListener('click', () => setLang(b.dataset.lang));
  });
  initNav();
  glitchify();
  reveal();
  const y = $('#year');
  if (y) y.textContent = new Date().getFullYear();
}
