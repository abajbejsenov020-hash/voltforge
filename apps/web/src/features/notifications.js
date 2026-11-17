import { $ } from '../ui/dom.js';
export function createFeature(app) {
  function toast(t) {
    clearTimeout(app.toastTimer);
    $('#toast').textContent = t;
    $('#toast').classList.add('show');
    app.toastTimer = setTimeout(() => $('#toast').classList.remove('show'), 3500);
  }
  function detail(title, html) {
    $('#detailTitle').textContent = title;
    $('#detailBody').innerHTML = html;
    if (!$('#detailDialog').open) $('#detailDialog').showModal();
  }
  return { toast, detail };
}
