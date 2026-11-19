/** Use native fullscreen when allowed, or a viewport-sized dialog on browsers that block it. */
export function bindViewerFullscreen(stage) {
  const document = stage.ownerDocument;
  const button = stage.querySelector('#sceneFullscreen');
  const dialog = document.querySelector('#viewerFullscreenDialog');
  const [expandIcon, exitIcon] = button.querySelectorAll('path');
  const originalPosition = document.createComment('Vehicle viewer position');
  let pending = false;

  function updateButton() {
    const expanded = document.fullscreenElement === stage || dialog.open;
    const label = expanded ? 'Exit full screen' : 'Full screen';
    button.setAttribute('aria-label', label);
    button.title = label;
    expandIcon.toggleAttribute('hidden', expanded);
    exitIcon.toggleAttribute('hidden', !expanded);
  }

  function restoreStage() {
    originalPosition.replaceWith(stage);
    updateButton();
    button.focus({ preventScroll: true });
  }

  async function toggle() {
    if (pending) return;
    if (dialog.open) {
      dialog.close();
      return;
    }
    pending = true;
    try {
      if (document.fullscreenElement === stage) {
        await document.exitFullscreen();
        return;
      }
      if (document.fullscreenEnabled && stage.requestFullscreen) {
        try {
          await stage.requestFullscreen();
          return;
        } catch {
          // Embedded and mobile browsers can deny native fullscreen.
        }
      }
      stage.before(originalPosition);
      dialog.append(stage);
      dialog.showModal();
      updateButton();
      button.focus({ preventScroll: true });
    } finally {
      pending = false;
    }
  }

  function exitOnEscape(event) {
    if (event.key === 'Escape' && document.fullscreenElement === stage) {
      event.preventDefault();
      void toggle();
    }
  }

  button.addEventListener('click', toggle);
  stage.addEventListener('keydown', exitOnEscape);
  document.addEventListener('fullscreenchange', updateButton);
  dialog.addEventListener('close', restoreStage);
  return () => {
    button.removeEventListener('click', toggle);
    stage.removeEventListener('keydown', exitOnEscape);
    document.removeEventListener('fullscreenchange', updateButton);
    dialog.removeEventListener('close', restoreStage);
    if (dialog.open) {
      dialog.close();
      restoreStage();
    }
  };
}
