import { $, h, img, loadJSON, boot, reveal, openLightbox } from './common.js';

boot();

const gallery = await loadJSON('data/galerie.json');
// Ratio des vignettes par section (les images d'icônes restent entières, sans recadrage)
const LAYOUT = {
  ecrans: { min: 300 }, mondes: { min: 300 }, zones: { min: 220 }, hub: { min: 260, ratio: '2000 / 1340' },
  coursier: { min: 200, contain: true, ratio: '1' }, tenues: { min: 130, ratio: '200 / 310' },
  tutoriel: { min: 420, ratio: '2436 / 816' }, commandes: { min: 240, ratio: '760 / 252' },
  emballage: { min: 260 }, vehicules: { min: 240, contain: true, ratio: '408 / 164' },
  garage: { min: 150, contain: true, ratio: '1' }, armes: { min: 150, contain: true, ratio: '1' },
  plans: { min: 130, contain: true, ratio: '1' }, etoiles: { min: 120, contain: true, ratio: '256 / 332' },
  carte: { min: 72, contain: true, ratio: '1' }, evac: { min: 240, contain: true, ratio: '1' },
};

gallery.forEach((g) => {
  if (!g.items.length) return;
  const lay = LAYOUT[g.id] || {};
  $('#gal-nav').append(h('a', { class: 'filter', href: `#${g.id}` }, `${g.title} (${g.items.length})`));
  const items = g.items.map((it) => ({ thumb: img(it.thumb), file: it.file, caption: `${g.title} · ${it.name}` }));
  const grid = h('div', { class: 'gal-grid' + (lay.contain ? ' contain' : ''), style: `--min:${lay.min || 240}px;--ratio:${lay.ratio || '16 / 9'}` });
  items.forEach((it, i) => grid.append(h('button', { type: 'button', title: it.caption, onclick: () => openLightbox(items, i) },
    h('img', { src: it.thumb, alt: it.caption, loading: 'lazy', decoding: 'async' }),
    h('span', { class: 'nm' }, g.items[i].name))));
  $('#gallery').append(h('section', { class: 'gal-section reveal', id: g.id },
    h('h2', { class: 'sub-title' }, g.title, h('span', { class: 'dim', style: 'font-size:18px;font-style:normal' }, ` ${g.items.length}`)), grid));
});
reveal();
if (location.hash) document.getElementById(location.hash.slice(1))?.scrollIntoView();
