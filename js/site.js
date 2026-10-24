'use strict';
// Navigation remains native, including hashes and browser Back/Forward.
const links = [...document.querySelectorAll('#sidebar nav > a')];
const sections = links.map(link => document.querySelector(link.hash));
function updateNavigation() {
  const visible = sections.filter(section => section.getBoundingClientRect().top <= window.innerHeight * .35);
  let current = visible.at(-1) || sections[0];
  if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 8) current = sections.at(-1);
  for (const link of links) {
    if (link.hash === '#' + current.id) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }
}
let scheduled = false;
addEventListener('scroll', () => {
  if (!scheduled) requestAnimationFrame(() => { updateNavigation(); scheduled = false; });
  scheduled = true;
}, {passive: true});
addEventListener('resize', updateNavigation);
updateNavigation();

const viewer = document.querySelector('#media-viewer');
const content = document.querySelector('#media-content');
const status = document.querySelector('#media-status');
let opener;
let generation = 0;
if (typeof viewer.showModal === 'function') {
  document.addEventListener('click', event => {
    const link = event.target.closest('a[data-media]');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    opener = link;
    const current = ++generation;
    const caption = link.dataset.caption || link.closest('figure')?.querySelector('figcaption')?.textContent || link.getAttribute('aria-label') || 'Image';
    document.querySelector('#media-caption').textContent = caption;
    document.querySelector('#media-original').href = link.href;
    const sourcePreview = link.querySelector('img');
    if (sourcePreview) {
      const preview = sourcePreview.cloneNode();
      preview.removeAttribute('loading');
      content.replaceChildren(preview);
    } else {
      content.replaceChildren();
    }
    status.textContent = 'Loading original…';
    viewer.showModal();
    document.body.classList.add('viewer-open');
    const original = new Image();
    original.alt = caption;
    original.onload = () => {
      if (current !== generation) return;
      content.replaceChildren(original);
      status.textContent = '';
    };
    original.onerror = () => {
      if (current === generation) status.textContent = 'The original could not load. Use the link below to open it, or close and try again.';
    };
    original.src = link.href;
  });
  document.querySelector('#close-viewer').addEventListener('click', () => viewer.close());
  viewer.addEventListener('click', event => {
    if (event.target !== viewer) return;
    const rect = viewer.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) viewer.close();
  });
  viewer.addEventListener('close', () => {
    generation++;
    content.replaceChildren();
    document.body.classList.remove('viewer-open');
    opener?.focus({preventScroll: true});
  });
}
