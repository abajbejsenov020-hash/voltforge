import { $ } from '../ui/dom.js';
export function createFeature(app) {
  function toast(t) {
    clearTimeout(app.toastTimer);
    $('#toast').textContent = t;
    $('#toast').classList.add('show');
    app.toastTimer = setTimeout(() => $('#toast').classList.remove('show'), 3500);
  }
  function detail(title, html) {
    const dialog = $('#detailDialog');
    const heading = $('#detailTitle');
    const newView = !dialog.open || heading.textContent !== title;
    heading.textContent = title;
    $('#detailBody').innerHTML = html;
    if (!dialog.open) dialog.showModal();
    if (newView) {
      dialog.scrollTop = 0;
      heading.focus({ preventScroll: true });
    }
  }
  return { toast, detail };
}
