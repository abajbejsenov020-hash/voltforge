import {
  BAR_STYLES,
  BAR_WIDTHS,
  GRIP_COLORS,
  GRIP_STYLES,
  normalizeCockpit,
} from '@voltforge/shared/cockpit';

export function bindCockpitControls({ onChange, onInspect }) {
  const controls = document.querySelector('#cockpitControls');
  const grip = controls.querySelector('#gripStyle');
  const color = controls.querySelector('#gripColor');
  const bar = controls.querySelector('#barStyle');
  const width = controls.querySelector('#barWidth');
  const swatch = controls.querySelector('#gripSwatch');
  const reset = controls.querySelector('#resetCockpit');

  grip.replaceChildren(
    new Option('Stock grips', ''),
    ...Object.entries(GRIP_STYLES).map(([id, label]) => new Option(label, id)),
  );
  color.replaceChildren(
    ...Object.entries(GRIP_COLORS).map(([id, choice]) => new Option(choice.label, id)),
  );
  bar.replaceChildren(
    new Option('Stock handlebar', ''),
    ...Object.entries(BAR_STYLES).map(([id, label]) => new Option(label, id)),
  );
  width.replaceChildren(
    new Option('Stock width', ''),
    ...BAR_WIDTHS.map((mm) => new Option(mm + ' mm', mm)),
  );

  for (const field of [grip, color, bar, width])
    field.addEventListener('change', () => {
      onChange(
        normalizeCockpit({
          grip: grip.value,
          color: color.value,
          bar: bar.value,
          width: Number(width.value),
        }),
      );
    });
  reset.addEventListener('click', () => {
    onChange({});
    grip.focus();
  });
  controls.querySelector('#inspectCockpit').addEventListener('click', onInspect);

  return {
    update(configuration, visible) {
      controls.hidden = !visible;
      grip.value = configuration.grip || '';
      color.value = configuration.color || 'black';
      bar.value = configuration.bar || '';
      width.value = configuration.width || '';
      color.disabled = !configuration.grip;
      width.disabled = !configuration.bar;
      reset.disabled = !configuration.grip && !configuration.bar;
      swatch.style.backgroundColor = GRIP_COLORS[color.value].color;
    },
  };
}
