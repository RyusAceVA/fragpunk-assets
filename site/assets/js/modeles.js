import { $, $$, h, img, loadJSON, boot, media, RAW } from './common.js';

boot();

const { groups, items } = await loadJSON('data/modeles.json');
const mv = $('#mv');
const params = new URLSearchParams(location.search);
let group = 'all';
let current = null;

const sizeLabel = (b) => (b > 1e6 ? `${(b / 1e6).toFixed(1)} Mo` : `${Math.round(b / 1e3)} Ko`);

function select(m, push = true) {
  current = m;
  $('#m-name').textContent = m.id;
  $('#m-group span').textContent = groups[m.group];
  $('#m-size').textContent = sizeLabel(m.size);
  $('#overlay').hidden = false;
  $('#pct').textContent = '0%';
  $('#bar').style.width = '4%';
  mv.poster = img(m.thumb);
  mv.dataset.file = m.file;
  mv.src = media(m.file);
  $$('#model-list button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.id === m.id)));
  if (push) {
    const url = new URL(location.href);
    url.searchParams.set('m', m.id);
    history.replaceState(null, '', url);
  }
}

mv.addEventListener('progress', (e) => {
  const p = Math.round((e.detail?.totalProgress || 0) * 100);
  $('#pct').textContent = `${p}%`;
  $('#bar').style.width = `${Math.max(p, 4)}%`;
  if (p >= 100) $('#overlay').hidden = true;
});
mv.addEventListener('load', () => { $('#overlay').hidden = true; });
mv.addEventListener('error', () => {
  if (mv.dataset.file && !mv.src.startsWith(RAW)) { mv.src = RAW + mv.dataset.file; return; }
  $('#overlay').hidden = false;
  $('#overlay').innerHTML = '<div class="upper" style="font-weight:700;letter-spacing:.1em">Modèle 3D indisponible</div>';
});

function renderList() {
  const q = $('#m-search').value.trim().toLowerCase();
  const list = $('#model-list');
  list.innerHTML = '';
  items.filter((m) => (group === 'all' || m.group === group) && (!q || m.id.toLowerCase().includes(q))).forEach((m) => {
    const b = h('button', { type: 'button', title: `${groups[m.group]} · ${m.id}`, 'aria-pressed': String(current?.id === m.id), onclick: () => select(m) },
      h('img', { src: img(m.thumb), alt: m.id, loading: 'lazy', decoding: 'async' }), h('span', {}, m.id));
    b.dataset.id = m.id;
    list.append(b);
  });
}

const order = ['tenues', 'monstres', 'pnj', 'vehicules', 'armes', 'corps'];
[['all', `Tous (${items.length})`], ...order.map((g) => [g, `${groups[g]} (${items.filter((m) => m.group === g).length})`])].forEach(([g, label]) => {
  const b = h('button', { class: 'filter', type: 'button', 'aria-pressed': String(g === group) }, label);
  b.addEventListener('click', () => {
    group = g;
    $$('#groups .filter').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    renderList();
  });
  $('#groups').append(b);
});
$('#m-search').addEventListener('input', renderList);

const wanted = items.find((m) => m.id === params.get('m'));
if (wanted) { group = wanted.group; $$('#groups .filter')[order.indexOf(group) + 1]?.setAttribute('aria-pressed', 'true'); $$('#groups .filter')[0].setAttribute('aria-pressed', 'false'); }
renderList();
select(wanted || items.find((m) => m.id === 'HLCS3903_Female') || items[0], false);
