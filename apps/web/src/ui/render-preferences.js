const STORAGE_KEY = 'voltmodd-render-preferences';
const REDUCED_MOTION_QUERY = '(prefers-reduced-motion: reduce)';

export function reducedMotionEnabled() {
  return (
    document.documentElement.dataset.reduceMotion === 'true' ||
    window.matchMedia(REDUCED_MOTION_QUERY).matches
  );
}

export function bindRenderPreferences(onChange) {
  const settings = document.querySelector('#graphicsSettings');
  const summary = settings.querySelector('summary');
  const quality = document.querySelector('#renderQuality');
  const motion = document.querySelector('#reduceMotion');
  let saved;
  try {
    saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
  } catch {
    // Graphics controls are also usable when storage is unavailable.
  }
  quality.value = saved?.quality === 'efficient' ? 'efficient' : 'high';
  motion.checked = saved?.reduceMotion === true;

  function apply() {
    const preferences = { quality: quality.value, reduceMotion: motion.checked };
    document.documentElement.dataset.reduceMotion = String(preferences.reduceMotion);
    onChange(preferences);
    return preferences;
  }
  function save() {
    const preferences = apply();
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
    } catch {
      // The current session keeps the chosen graphics settings.
    }
  }
  quality.addEventListener('change', save);
  motion.addEventListener('change', save);
  settings.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || !settings.open) return;
    event.preventDefault();
    settings.open = false;
    summary.focus();
  });
  settings.addEventListener('focusout', (event) => {
    if (event.relatedTarget && !settings.contains(event.relatedTarget)) settings.open = false;
  });
  apply();
}
