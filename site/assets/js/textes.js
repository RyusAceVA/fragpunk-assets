import { $, h, loadJSON, boot, media, RAW, GITHUB } from './common.js';

boot();

const TSV_PATH = 'farlands/textes/_tous_les_textes_du_jeu.tsv';
const PAGE = 100;
const params = new URLSearchParams(location.search);
const ui = {
  q: $('#q'), table: $('#table'), field: $('#field'), scope: $('#scope'), count: $('#count'),
  rows: $('#rows'), more: $('#more'), status: $('#status'),
};

let corpus = null; // { labels, rows: [table, en, fr, key] }
let full = null;
let shown = PAGE;
let results = [];

$('#tsv-link').href = GITHUB + TSV_PATH;
ui.q.value = params.get('q') || params.get('k') || '';
if (params.get('k')) ui.field.value = 'key';

function setStatus(msg) { ui.status.textContent = msg || ''; ui.status.hidden = !msg; }

/** Lecteur TSV (format écrit par le module csv de Python : champs entre guillemets si besoin). */
function parseTSV(text) {
  if (text.charCodeAt(0) === 0xfeff) text = text.slice(1);
  const rows = [];
  let row = []; let field = ''; let i = 0; let quoted = false;
  const n = text.length;
  while (i < n) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"') {
        if (text[i + 1] === '"') { field += '"'; i += 2; continue; }
        quoted = false; i++; continue;
      }
      field += ch; i++; continue;
    }
    if (ch === '"' && field === '') { quoted = true; i++; continue; }
    if (ch === '\t') { row.push(field); field = ''; i++; continue; }
    if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i++;
      row.push(field); rows.push(row); row = []; field = ''; i++; continue;
    }
    field += ch; i++;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  return rows;
}

async function loadFull() {
  if (full) return full;
  setStatus('Chargement du fichier complet (10 Mo)…');
  let res = await fetch(media(TSV_PATH)).catch(() => null);
  if (!res || !res.ok) res = await fetch(RAW + TSV_PATH);
  const rows = parseTSV(await res.text());
  const head = rows.shift();
  const ti = head.indexOf('table'); const ki = head.indexOf('cle');
  const ei = head.indexOf('anglais'); const fi = head.indexOf('francais');
  full = rows.filter((r) => r.length >= 4).map((r) => [(r[ti] || '').slice(0, 8), r[ei], r[fi], (r[ki] || '').slice(0, 8)]);
  setStatus('');
  return full;
}

function fillTables(rows) {
  const counts = new Map();
  rows.forEach((r) => counts.set(r[0], (counts.get(r[0]) || 0) + 1));
  const current = ui.table.value || params.get('t') || '';
  ui.table.innerHTML = '';
  ui.table.append(h('option', { value: '' }, 'Toutes les tables'));
  const labelled = [...counts.keys()].map((t) => [t, corpus.labels[t] || (t ? `Table ${t}` : 'Sans table')]);
  labelled.sort((a, b) => a[1].localeCompare(b[1], 'fr'));
  labelled.forEach(([t, label]) => ui.table.append(h('option', { value: t }, `${label} · ${t || '—'} (${counts.get(t)})`)));
  ui.table.value = counts.has(current) ? current : '';
}

function norm(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }

function mark(text, q) {
  const el = document.createDocumentFragment();
  if (!q || !text) { el.append(text || ''); return el; }
  const nt = norm(text); const nq = norm(q);
  let from = 0; let idx = nt.indexOf(nq);
  if (idx < 0) { el.append(text); return el; }
  while (idx >= 0) {
    el.append(text.slice(from, idx), h('mark', {}, text.slice(idx, idx + q.length)));
    from = idx + q.length;
    idx = nt.indexOf(nq, from);
  }
  el.append(text.slice(from));
  return el;
}

function search() {
  const rows = ui.scope.value === 'all' ? full : corpus.rows;
  if (!rows) return;
  const q = ui.q.value.trim();
  const nq = norm(q);
  const table = ui.table.value;
  const field = ui.field.value;
  results = rows.filter((r) => {
    if (table && r[0] !== table) return false;
    if (!nq) return true;
    if (field === 'key') return r[3].toLowerCase().startsWith(nq) || r[0].toLowerCase() === nq;
    if (field === 'en') return norm(r[1]).includes(nq);
    if (field === 'fr') return norm(r[2]).includes(nq);
    return norm(r[1]).includes(nq) || norm(r[2]).includes(nq);
  });
  shown = PAGE;
  render();
  const url = new URL(location.href);
  ['q', 'k', 't'].forEach((k) => url.searchParams.delete(k));
  if (q) url.searchParams.set(field === 'key' ? 'k' : 'q', q);
  if (table) url.searchParams.set('t', table);
  history.replaceState(null, '', url);
}

function render() {
  const q = ui.field.value === 'key' ? '' : ui.q.value.trim();
  ui.rows.innerHTML = '';
  const frag = document.createDocumentFragment();
  results.slice(0, shown).forEach(([t, en, fr, key]) => {
    frag.append(h('div', { class: 'row' },
      h('div', { class: 'tb' }, h('b', {}, corpus.labels[t] || 'Autre'), `${t} · ${key}`),
      h('div', { class: 'en', lang: 'en' }, en ? mark(en, q) : h('span', { class: 'empty' }, '(vide)')),
      h('div', { class: 'fr', lang: 'fr' }, fr ? mark(fr, q) : h('span', { class: 'empty' }, '(pas de VF)'))));
  });
  ui.rows.append(frag);
  const total = (ui.scope.value === 'all' ? full : corpus.rows).length;
  ui.count.textContent = `${results.length.toLocaleString('fr-FR')} résultat${results.length > 1 ? 's' : ''} sur ${total.toLocaleString('fr-FR')} textes`;
  ui.more.hidden = results.length <= shown;
  if (!results.length) ui.rows.append(h('div', { class: 'row' }, h('div', { class: 'empty', style: 'grid-column:1/-1' },
    ui.scope.value === 'all' ? 'Aucun texte ne correspond.' : 'Aucun texte FarLands ne correspond. Essayez « Tout le fichier ».')));
}

let timer;
ui.q.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(search, 180); });
[ui.table, ui.field].forEach((el) => el.addEventListener('change', search));
ui.scope.addEventListener('change', async () => {
  if (ui.scope.value === 'all') await loadFull();
  fillTables(ui.scope.value === 'all' ? full : corpus.rows);
  search();
});
ui.more.addEventListener('click', () => { shown += PAGE; render(); });

corpus = await loadJSON('data/textes.json');
fillTables(corpus.rows);
// Lien depuis un badge source : si la clé n'est pas dans le corpus FarLands, on ouvre le fichier complet.
const k = params.get('k');
const t = params.get('t');
if ((k && !corpus.rows.some((r) => r[3].toLowerCase().startsWith(k.toLowerCase())))
  || (t && !corpus.rows.some((r) => r[0] === t))) {
  ui.scope.value = 'all';
  await loadFull();
  fillTables(full);
}
if (t) ui.table.value = t;
search();
