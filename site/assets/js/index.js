import {
  $, $$, h, gt, txt, img, loadJSON, boot, reveal, openLightbox, openVideo, openDoc, glitchify, srcBadge,
} from './common.js';

boot();

const FACTION_FR = {
  kepler: 'Kepler', scavengers: 'Charognards', mariana: 'Mariana', chelae: 'Chelae', orcs: 'Orques',
  dragon: 'Gang du Dragon Fou', aesir: 'Aesir', boiler: 'Gang du Fourneau', kemet: 'Kemet',
  wild: 'Faune sauvage', neutral: 'Neutre', orbs: 'Orbes de gel',
};

const VIDEO_TITLES = {
  CT_Ch00_Vid_01_720: 'Le crash', CT_Ch00_Vid_02_720: 'La traversée de la neige',
  CT_Ch00_Vid_03_720: 'La forêt rouge', CT_Ch00_Vid_04_720: 'Le colis retrouvé',
  CT_Ch00_Vid_05_720: 'La rencontre', CT_Ch00_Vid_06_CN_720: "L'embuscade",
  CT_Boss_Vid_115056_720: 'Le niveau de boss', HL_Packup_AnimationVideo1: "La chaîne d'emballage",
  HL_Evacuate_Video: "L'évacuation",
};

const MECHANICS = [
  { t: 'Commandes et livraison', lead: "Tout part d'une commande : récupérer la marchandise, l'emballer, la porter jusqu'au client ou au casier à colis, dans les délais. L'état de la cargaison à l'arrivée fixe la paie.", q: ['tuto_100', 'hud_load'] },
  { t: 'Perfection', lead: "Presque tous les objets ont un taux de Perfection, qui baisse avec les coups et l'environnement. Il fixe le prix de revente et la paie des livraisons. À 0, un équipement ne sert plus à rien. Les résistances du sac protègent son contenu.", q: ['perf_intro', 'perf_effect', 'perf_restore'], el: ['Froid', 'Explosion', 'Physique', 'Foudre', 'Corrosion', 'Radiation', 'Chaleur'] },
  { t: 'Magnétisme', lead: "La jauge qui fait tout : roulade, escalade, sprint, aspiration des objets, pousser et tirer, parade. Elle se recharge à l'arrêt, avec des objets ou à une borne de recharge.", q: ['mag_intro', 'mag_adv', 'mag_recover'] },
  { t: 'Charge et équilibre', lead: "Plus vous portez, plus vous ralentissez : d'abord plus lent, puis sans sprint, puis vous titubez, et à pleine charge vous ne bougez plus. Les coups et les pentes vous déséquilibrent.", q: ['load', 'balance', 'tuto_slope'] },
  { t: 'Sac et emplacements assurés', lead: "Sans sac, impossible de ramasser quoi que ce soit. On le pose pour se battre et on le reprend après. À la mort, tout tombe sur place, sauf ce qui se trouve dans les emplacements d'assurance.", q: ['backpack_need', 'tuto_backpack', 'tuto_death'] },
  { t: 'Survie', lead: "La santé baisse si l'on ne mange pas, il faut aussi boire, et la météo use. S'accroupir dans les buissons aide à passer inaperçu des monstres.", q: ['health', 'tuto_crouch'] },
  { t: 'Avant-postes et évacuation', lead: "Les avant-postes, petits, moyens ou grands, promettent plus de monstres et plus de butin. Pour garder ce que vous portez, il faut rejoindre vivant un point d'évacuation.", q: ['extract', 'outpost_s', 'outpost_l'] },
  { t: 'PvPvE et escouade', lead: "On part en équipe et on relève ses coéquipiers à terre. D'autres joueurs rôdent : des quêtes demandent d'en éliminer (« Kill 3 enemy players with Rusty Revolver »).", q: ['revive', 'nolancers'] },
  { t: 'Déplacements', lead: "Escalade des parois, glissades, tyroliennes verticales et horizontales, pont énergétique portable, et des véhicules pour les longues distances.", q: ['energy_bridge', 'tuto_climb'] },
];

const KIT = [
  ['Uniforme de nouvelle recrue', 'kit_uniform'], ['Casque de coursier', 'kit_helmet'], ['Gants de coursier', 'kit_gloves'],
  ['Jambières de coursier', 'kit_legs'], ['Bottes de coursier', 'kit_boots'], ["Carton d'expédition", 'kit_box'],
  ['La boisson du salon', 'kit_drink'],
];

const MAPS = [
  ...['01', '02', '03', '04'].flatMap((z) => ['dessus', 'perspective'].map((v) => ['HL_Lobby', z, v])),
  ...['01', '02'].flatMap((z) => ['dessus', 'perspective', 'sol'].map((v) => ['HL_Chapter00', z, v])),
];

const [data, gallery, models] = await Promise.all([
  loadJSON('data/farlands.json'), loadJSON('data/galerie.json'), loadJSON('data/modeles.json'),
]);
const Q = data.quotes;
const gal = Object.fromEntries(gallery.map((g) => [g.id, g]));
const fmt = (n) => n.toLocaleString('fr-FR');

function lazyImg(name, alt = '', cls) {
  return h('img', { src: img(name), alt, loading: 'lazy', decoding: 'async', class: cls });
}

/** Grille d'images cliquables ouvrant la visionneuse. items : [{ thumb, file, caption }] */
function imageGrid(container, items) {
  items.forEach((it, i) => {
    const im = h('img', { src: it.thumb, alt: it.caption || '', loading: 'lazy', decoding: 'async' });
    im.addEventListener('click', () => openLightbox(items, i));
    container.append(im);
  });
}

function thumbButtons(container, items) {
  items.forEach((it, i) => container.append(h('button', {
    type: 'button', title: it.caption, onclick: () => openLightbox(items, i),
  }, h('img', { src: it.thumb, alt: it.caption || '', loading: 'lazy', decoding: 'async' }))));
}

const galItems = (id, filter = () => true) => gal[id].items.filter(filter)
  .map((it) => ({ thumb: img(it.thumb), file: it.file, caption: it.name }));

// Citations placées dans le HTML
$$('[data-q]').forEach((el) => { el.append(gt(Q[el.dataset.q])); });

// Images agrandissables placées dans le HTML
$$('[data-zoom]').forEach((el) => el.addEventListener('click', () => openLightbox([{
  thumb: img(el.dataset.zoom), file: el.dataset.file, caption: el.dataset.caption,
}])));

/* ---------- Compte à rebours ---------- */
(function countdown() {
  const target = new Date('2026-11-05T00:00:00+01:00').getTime();
  const box = $('#countdown');
  const tick = () => {
    const diff = target - Date.now();
    if (diff <= 0) {
      box.innerHTML = '';
      box.append(h('div', { class: 'cd-label' }, 'Accès anticipé', h('b', {}, 'Disponible depuis le 5 novembre 2026')));
      return;
    }
    const s = Math.floor(diff / 1000);
    const parts = { d: Math.floor(s / 86400), h: Math.floor(s / 3600) % 24, m: Math.floor(s / 60) % 60, s: s % 60 };
    for (const [k, v] of Object.entries(parts)) $(`[data-cd="${k}"]`, box).textContent = String(v).padStart(2, '0');
    setTimeout(tick, 1000);
  };
  tick();
}());

/* ---------- Le mode ---------- */
const c = data.counts;
[[76823, 'fichiers ajoutés'], [c.images, 'images'], [c.videos, 'cinématiques'], [c.models, 'modèles 3D'], [c.texts, 'textes du jeu']]
  .forEach(([n, l]) => $('#stats').append(h('div', { class: 'stat' }, h('b', {}, fmt(n)), h('span', {}, l))));

[
  ['Préinscriptions et pré-lancement', ['ev_prereg', 'ev_prehype', 'ev_team', 'ev_squad']],
  ['Twitch Drops et passe de combat', ['ev_twitch', 'ev_bp']],
  ['Défi FarLands', ['challenge', 'challenge_search', 'challenge_kill']],
].forEach(([title, ids]) => {
  const card = h('div', { class: 'card card-pad' }, h('h3', {}, title));
  const list = h('div', { class: 'quotes-stack', style: 'gap:8px;margin-top:10px' });
  ids.forEach((id) => list.append(gt(Q[id], { tag: 'p', cls: 'muted' })));
  card.append(list, h('div', { class: 'bar', style: 'position:absolute;left:0;bottom:0' }));
  $('#events').append(card);
});

/* ---------- Histoire ---------- */
const videos = data.videos;
const vidIndex = (id) => videos.findIndex((v) => v.id === id);
data.story.forEach((s, i) => {
  const lines = h('div', { class: 'lines' });
  s.q.forEach((id) => lines.append(gt(Q[id], { tag: 'p' })));
  const body = h('div', { class: 'tl-body' }, h('div', {}, h('h3', {}, s.title), lines));
  if (s.video) {
    const v = videos[vidIndex(s.video)];
    body.append(h('div', { class: 'tl-video', role: 'button', tabindex: '0', 'aria-label': `Lire la cinématique ${v.id}`,
      onclick: () => openVideo(videos, vidIndex(s.video)),
      onkeydown: (e) => { if (e.key === 'Enter') openVideo(videos, vidIndex(s.video)); } },
    lazyImg(v.poster, v.desc), h('div', { class: 'play' }, h('i')), h('span', { class: 'dur' }, `${Math.round(v.duration)} s`)));
  } else {
    body.style.gridTemplateColumns = '1fr';
  }
  $('#timeline').append(h('div', { class: 'tl-item reveal' }, h('div', { class: 'tl-num' }, String(i + 1)), body));
});

const zoneById = Object.fromEntries(data.zones.map((z) => [z.id, z]));
data.chapters.forEach((ch, i) => {
  const z = zoneById[ch.zone];
  const quests = h('div', { class: 'chips', style: 'margin:12px 0 16px' });
  ch.quests.forEach((q) => quests.append(h('span', { class: 'chip' }, gt(q, { src: false }))));
  const lines = h('div', { class: 'quotes-stack', style: 'gap:8px' });
  ch.lines.forEach((l) => lines.append(gt(l, { tag: 'p', cls: 'muted' })));
  $('#chapters').append(h('div', { class: 'card reveal' },
    h('div', { class: 'media color', style: 'aspect-ratio:16/7' }, lazyImg(z.img, '')),
    h('div', { class: 'card-pad' },
      h('span', { class: 'skew' }, h('span', {}, `Chapitre ${i + 1}`)),
      h('h3', { style: 'margin-top:10px' }, gt(z.name, { src: false })),
      h('p', { class: 'muted' }, ch.zone === 'fringe'
        ? "Harmony Town, abandonnée par Kepler après le second Smash-Up, est coupée en deux entre les restes de la garnison de Kepler et les Charognards du Roi des charognards."
        : "À Akhet, un éclat de Kemet, des Mariana et des Chelae ennemis jurés ont échoué dans le même port, entre les Orques et le Gang du Dragon Fou."),
      h('p', { class: 'dim', style: 'margin:12px 0 0;font-size:14px;text-transform:uppercase;letter-spacing:.08em' }, 'Quêtes'), quests, lines),
    h('div', { class: 'bar' })));
});

/* ---------- Cinématiques ---------- */
videos.forEach((v, i) => {
  $('#videos').append(h('div', { class: 'card vid-card reveal', role: 'button', tabindex: '0',
    onclick: () => openVideo(videos, i), onkeydown: (e) => { if (e.key === 'Enter') openVideo(videos, i); } },
  h('div', { class: 'media' }, lazyImg(v.poster, v.desc), h('div', { class: 'play' }, h('i')),
    h('span', { class: 'dur' }, v.duration < 10 ? `${v.duration} s` : `${Math.round(v.duration)} s`)),
  h('div', { class: 'card-pad' }, h('h3', {}, VIDEO_TITLES[v.id] || v.id), h('p', {}, v.desc), h('code', {}, v.id + '.mp4')),
  h('div', { class: 'bar' })));
});

/* ---------- Hub 9 ---------- */
data.merchants.forEach((m) => {
  const ava = h('div', { class: 'ava' });
  if (m.img || m.id === 'journey') ava.append(lazyImg(m.img || 'journey', m.name));
  else ava.textContent = m.name[0];
  const lines = h('div', {});
  m.lines.forEach((l) => lines.append(gt(l, { tag: 'p' })));
  $('#merchants').append(h('div', { class: 'card merchant reveal' }, ava,
    h('div', {}, h('h3', {}, m.name), h('div', { class: 'role' }, h('span', { class: 'skew' }, h('span', {}, txt(m.role)))), lines)));
});
document.addEventListener('langchange', () => {
  $$('#merchants .role .skew span').forEach((s, i) => { s.textContent = txt(data.merchants[i].role); });
});

data.facilities.forEach((f) => {
  $('#facilities').append(h('div', { class: 'card card-pad reveal facility' },
    h('h3', {}, gt(f.name, { src: false })), gt(f.desc, { tag: 'p' }), h('div', { class: 'bar', style: 'position:absolute;left:0;bottom:0' })));
});
imageGrid($('#hub-screens'), galItems('hub'));
$$('#hub-screens img').forEach((i) => { i.style.aspectRatio = '3/2'; });

data.stars.forEach((s) => $('#stars').append(h('div', { class: 'star' }, lazyImg(s.img, ''), gt(s.name, { src: false }))));
data.perks.forEach((p) => $('#perks').append(h('div', { class: 'icon-row' }, lazyImg(p.icon, ''), gt(p.text))));
data.rarities.forEach((r) => $('#rarities').append(h('span', { class: 'rarity ' + r.id }, h('span', {}, gt(r.name, { src: false })))));

/* ---------- Gameplay ---------- */
MECHANICS.forEach((m, i) => {
  const card = h('div', { class: 'card mech reveal' },
    h('div', { class: 'num' }, String(i + 1).padStart(2, '0')), h('h3', {}, m.t), h('p', { class: 'lead' }, m.lead));
  m.q.forEach((id) => card.append(gt(Q[id], { tag: 'p' })));
  if (m.el) card.append(h('div', { class: 'elements' }, m.el.map((e) => h('span', { class: 'el' }, e))));
  card.append(h('div', { class: 'bar', style: 'position:absolute;left:0;bottom:0' }));
  $('#mechanics').append(card);
});
const tutoItems = [1, 2, 3].map((i) => ({
  thumb: img(`tuto-${i}`), file: `farlands/images/AtlasTexture/HappyLand/HL_Tutorial/HL_Tutorial_Guide${i}.png`,
  caption: `Image du tutoriel ${i} (interface en chinois)`,
}));
tutoItems.forEach((it, i) => $('#tuto-imgs').append(h('figure', { class: 'banner-img zoomable', style: 'margin:0;aspect-ratio:2436/816', onclick: () => openLightbox(tutoItems, i) },
  h('img', { src: it.thumb, alt: it.caption, loading: 'lazy' }), h('figcaption', {}, it.caption))));

/* ---------- Commandes ---------- */
data.orders.forEach((o) => {
  const card = h('div', { class: 'card order reveal' }, h('h3', {}, gt(o.en, { src: false })),
    h('div', { class: 'en' }, `VO chinoise : ${o.name.zh}`));
  card.append(o.desc ? gt(o.desc, { tag: 'p' }) : h('p', { class: 'muted', style: 'margin:0' }, 'La commande standard.'), h('div', { class: 'bar', style: 'position:absolute;left:0;bottom:0' }));
  $('#orders').append(card);
});
$('#extra-orders').append(h('span', { class: 'dim', style: 'align-self:center;margin-right:4px' }, 'Autres types :'));
data.extra_orders.forEach((t) => $('#extra-orders').append(h('span', { class: 'chip' }, gt(t))));

data.customers.forEach((cu) => {
  $('#customers tbody').append(h('tr', {},
    h('td', { style: 'font-weight:700' }, cu.name.fr, h('span', { class: 't-zh' }, cu.name.zh)),
    h('td', {}, cu.desc ? gt(cu.desc) : h('span', { class: 'dim' }, 'Pas de description dans les fichiers ', srcBadge(cu.name.s)))));
});
data.market.forEach((m) => $('#market').append(h('div', { class: 'icon-row' }, lazyImg(m.icon, ''), gt(m.name))));

const packItems = [
  { thumb: img('packup-result'), file: 'farlands/images/AtlasTexture/HappyLand/HL_Packup/HL_Packup_Result.png', caption: "Écran de fin d'emballage" },
  { thumb: img('packup-bg'), file: 'farlands/images/AtlasTexture/HappyLand/HL_Packup/HL_Packup_AnimationBg.png', caption: "Fond de l'animation d'emballage" },
];
packItems.forEach((it, i) => $('#packup').append(h('figure', { class: 'banner-img zoomable', style: 'margin:0;aspect-ratio:16/9', onclick: () => openLightbox(packItems, i) },
  h('img', { src: it.thumb, alt: it.caption, loading: 'lazy' }), h('figcaption', {}, it.caption))));
const pv = vidIndex('HL_Packup_AnimationVideo1');
$('#packup').append(h('div', { class: 'tl-video', style: 'grid-column:span 2', role: 'button', tabindex: '0', onclick: () => openVideo(videos, pv) },
  lazyImg(videos[pv].poster, ''), h('div', { class: 'play' }, h('i')), h('span', { class: 'dur' }, '21 s')));

/* ---------- Survie ---------- */
data.weather.forEach((w) => {
  const box = h('div', { class: 'wx reveal' + (w.desc ? ' danger' : '') }, h('h4', {}, gt(w.name, { src: false })));
  box.append(w.desc ? gt(w.desc, { tag: 'p' }) : h('p', { class: 'dim', style: 'margin:0;font-size:15px' }, gt(w.name)));
  $('#weather').append(box);
});
$('#train-cats').append(...data.training_cats.flatMap((t, i) => [i ? ', ' : '', gt(t, { src: false })]));
data.training.forEach((t) => {
  $('#training').append(h('div', { class: 'card train reveal' }, lazyImg(t.icon, ''),
    h('div', {}, h('h4', {}, gt(t.name, { src: false })), t.desc ? gt(t.desc, { tag: 'p' }) : h('p', { class: 'dim', style: 'margin:0;font-size:15px' }, "Pas encore de description dans les fichiers."))));
});

/* ---------- Véhicules ---------- */
data.vehicles.forEach((v) => {
  $('#vehicles').append(h('div', { class: 'card veh reveal' },
    h('div', { class: 'media flat' }, lazyImg(v.img, '')),
    h('div', { class: 'card-pad' }, h('h3', {}, gt(v.name, { src: false })),
      h('p', {}, gt(v.name)), h('code', {}, v.code + (v.sure ? '' : ' · image probable'))),
    h('div', { class: 'bar' })));
});
data.vehicle_stats.forEach((s) => $('#veh-stats').append(h('span', { class: 'chip' }, gt(s, { src: false }))));
data.vehicle_parts.forEach((p) => $('#veh-parts').append(h('div', { class: 'icon-row' }, lazyImg(p.icon, ''), gt(p.name))));
const garageItems = [
  { thumb: img('garage-craft'), file: 'farlands/images/AtlasTexture/HappyLand/HL_Vehicle/HL_MachineM_13.png', caption: 'Atelier de véhicules' },
  { thumb: img('garage-new'), file: 'farlands/images/AtlasTexture/HappyLand/HL_Vehicle/Veh_New/VehNew_08.png', caption: 'Garage' },
];
garageItems.forEach((it, i) => $('#garage').append(h('figure', { class: 'banner-img zoomable', style: 'margin:0;aspect-ratio:16/9', onclick: () => openLightbox(garageItems, i) },
  h('img', { src: it.thumb, alt: it.caption, loading: 'lazy' }), h('figcaption', {}, it.caption))));

/* ---------- Monde ---------- */
data.zones.forEach((z) => {
  $('#zones').append(h('div', { class: 'card zone reveal' },
    h('div', { class: 'media' }, lazyImg(z.img, '')),
    h('div', { class: 'tag' }, h('span', { class: 'skew solid' }, h('span', {}, z.tag))),
    h('div', { class: 'card-pad' }, h('h3', {}, gt(z.name, { src: false })),
      z.desc ? gt(z.desc, { tag: 'p' }) : h('p', { class: 'muted' }, z.id === 'dunes'
        ? "Une carte désertique : des quêtes demandent d'y livrer des commandes et d'en évacuer."
        : "L'arène du Roi des charognards, avec son niveau de boss et sa cinématique.")),
    h('div', { class: 'bar' })));
});

const locFilter = { zone: 'all', faction: 'all', open: false };
const LOC_PREVIEW = 12;
function renderLocations() {
  const box = $('#locations');
  box.innerHTML = '';
  const list = data.locations
    .filter((l) => (locFilter.zone === 'all' || l.zone === locFilter.zone) && (locFilter.faction === 'all' || l.faction === locFilter.faction));
  const more = $('#loc-more');
  more.hidden = locFilter.open || list.length <= LOC_PREVIEW;
  more.textContent = `Afficher les ${list.length - LOC_PREVIEW} autres lieux`;
  (locFilter.open ? list : list.slice(0, LOC_PREVIEW))
    .forEach((l) => {
      const f = data.factions.find((x) => x.id === l.faction);
      box.append(h('div', { class: 'card loc', style: { '--fc': f ? f.color : '' } },
        h('div', { class: 'meta' }, h('span', {}, txt(zoneById[l.zone].name)), '·', h('span', {}, FACTION_FR[l.faction])),
        h('h4', {}, gt(l.name, { src: false })), gt(l.desc, { tag: 'p' })));
    });
}
function filterButtons(key, options) {
  options.forEach(([val, label]) => {
    const b = h('button', { class: 'filter', type: 'button', 'aria-pressed': String(locFilter[key] === val) }, label);
    b.dataset.key = key; b.dataset.val = val;
    b.addEventListener('click', () => {
      locFilter[key] = val;
      $$(`.filter[data-key="${key}"]`).forEach((x) => x.setAttribute('aria-pressed', String(x.dataset.val === val)));
      renderLocations();
    });
    $('#loc-filters').append(b);
  });
}
filterButtons('zone', [['all', 'Toutes les zones'], ['fringe', 'Secteur périphérique'], ['seaside', 'Port côtier']]);
$('#loc-filters').append(h('span', { style: 'width:12px' }));
filterButtons('faction', [['all', 'Toutes factions'], ...['kepler', 'scavengers', 'mariana', 'chelae', 'orcs', 'dragon', 'neutral'].map((f) => [f, FACTION_FR[f]])]);
$('#loc-more').addEventListener('click', () => { locFilter.open = true; renderLocations(); });
renderLocations();
document.addEventListener('langchange', renderLocations);

const mapItems = MAPS.map(([m, z, v]) => ({
  thumb: img(`maps/${m}/apercu_zone${z}_${v}`), file: `farlands/maps/${m}/apercu_zone${z}_${v}.png`,
  caption: `${m === 'HL_Lobby' ? 'Hub (lobby)' : 'Chapitre 0'} · zone ${z} · vue ${v}`,
}));
imageGrid($('#maps'), mapItems);
$$('#maps img').forEach((i) => { i.style.aspectRatio = '16/10'; });

/* ---------- Factions ---------- */
data.factions.forEach((f) => {
  const card = h('div', { class: 'card faction reveal', style: { '--fc': f.color } },
    h('h3', {}, FACTION_FR[f.id]), gt(f.desc, { tag: 'p' }));
  if (f.overview) card.append(h('div', { class: 'over' }, gt(f.overview, { tag: 'p' })));
  $('#faction-list').append(card);
});

/* ---------- Bestiaire ---------- */
const bossVid = vidIndex('CT_Boss_Vid_115056_720');
$('#boss').append(
  h('div', { class: 'media', style: 'cursor:pointer', onclick: () => openVideo(videos, bossVid) },
    lazyImg('load/HL_Loading_BossLevel_325325', 'Écran de chargement du niveau de boss : une forteresse de ferraille.'),
    h('div', { class: 'play' }, h('i'))),
  h('div', { class: 'card-pad' },
    h('span', { class: 'skew solid' }, h('span', {}, 'Boss')),
    h('h3', { style: 'margin-top:12px' }, gt(data.scavenger_king.name, { src: false })),
    gt(data.scavenger_king.desc, { tag: 'p' }),
    h('p', { class: 'dim', style: 'margin-top:14px;font-size:16px' }, "Son niveau (une forteresse de ferraille) a sa propre cinématique : cliquer sur l'image pour la voir.")));

data.monster_types.forEach((t) => $('#monster-types').append(h('span', { class: 'chip' }, gt(t, { src: false }))));
data.monster_groups.forEach((g) => {
  const f = data.factions.find((x) => x.id === g.faction);
  const ul = h('ul', {});
  g.names.forEach((n) => ul.append(h('li', {}, gt(n, { src: false }))));
  $('#monsters').append(h('div', { class: 'card mgroup reveal', style: { '--fc': f ? f.color : '#00ffff' } },
    h('h4', {}, FACTION_FR[g.faction] + ` (${g.names.length})`), ul));
});
models.items.filter((m) => m.group === 'monstres').slice(0, 16).forEach((m) => {
  $('#monster-models').append(h('a', { href: `modeles.html?m=${encodeURIComponent(m.id)}`, title: m.id }, lazyImg(m.thumb, m.id)));
});

/* ---------- PNJ ---------- */
data.npc_names.forEach((n) => $('#npc-names').append(h('span', { class: 'chip' }, gt(n, { src: false }))));
imageGrid($('#npc-banners'), galItems('commandes', (it) => it.name.startsWith('Merge_NPC')));
data.npc_lines.forEach((l) => $('#npc-lines').append(gt(l, { tag: 'p' })));

/* ---------- Équipement ---------- */
KIT.forEach(([title, id]) => $('#kit').append(h('div', { class: 'card' }, h('div', { class: 'card-pad' }, h('h4', {}, title), gt(Q[id], { tag: 'p' })))));
thumbButtons($('#suits'), [
  ...galItems('coursier', (it) => /_1[0-3]$/.test(it.name)),
  ...galItems('tenues'),
]);
data.sets_featured.forEach((s) => $('#sets').append(h('span', { class: 'chip' }, gt(s, { src: false }))));
$('#sets').append(h('span', { class: 'chip', style: 'border-style:dashed' }, h('a', { href: 'textes.html?t=C3BA5F4E' }, `voir les ${data.sets.length} →`)));
data.set_bonus.forEach((b) => $('#set-bonus').append(gt(b, { tag: 'p', cls: 'chip' })));
thumbButtons($('#blueprints'), galItems('plans'));
thumbButtons($('#weapons'), galItems('armes'));

/* ---------- Lore ---------- */
data.docs.forEach((d) => {
  const preview = (d.body.fr || d.body.en).replace(/^#.*\n/, '').slice(0, 260);
  $('#docs').append(h('button', { class: 'card doc reveal', type: 'button', onclick: () => openDoc(d.title, d.body) },
    h('h3', {}, d.title), h('p', {}, preview + '…'), h('span', { class: 'read' }, 'Lire le document →'),
    h('div', { class: 'bar', style: 'position:absolute;left:0;bottom:0' })));
});

glitchify();
reveal();
if (location.hash) {
  const target = document.getElementById(location.hash.slice(1));
  if (target) setTimeout(() => target.scrollIntoView(), 50);
}
