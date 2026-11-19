export const GRIP_STYLES = Object.freeze({
  ribbed: 'Ribbed rubber',
  diamond: 'Diamond texture',
  waffle: 'Waffle tread',
  ergonomic: 'Ergonomic palm rest',
  'lock-on': 'Lock-on collars',
  foam: 'Smooth foam',
});

export const GRIP_COLORS = Object.freeze({
  black: { label: 'Black', color: '#191b1d' },
  graphite: { label: 'Graphite', color: '#454b51' },
  ice: { label: 'Ice white', color: '#dbdfdc' },
  sand: { label: 'Sand', color: '#b79064' },
  amber: { label: 'Amber', color: '#e99e26' },
  orange: { label: 'KuKirin orange', color: '#f55f14' },
  red: { label: 'Race red', color: '#c72432' },
  pink: { label: 'Hot pink', color: '#db4492' },
  purple: { label: 'Violet', color: '#714ac5' },
  blue: { label: 'Cobalt', color: '#2d60c0' },
  teal: { label: 'Teal', color: '#1b9f98' },
  lime: { label: 'Lime', color: '#96ce30' },
  forest: { label: 'Forest green', color: '#365d48' },
});

export const BAR_STYLES = Object.freeze({
  flat: 'Flat bar',
  swept: 'Swept-back bar',
  'low-rise': 'Low-rise bar',
  'high-rise': 'High-rise bar',
});

export const BAR_WIDTHS = Object.freeze([
  560, 580, 600, 620, 640, 660, 680, 700, 720, 740, 760, 780, 800,
]);

export function normalizeCockpit(value) {
  const cockpit = {};
  if (typeof value?.grip === 'string' && Object.hasOwn(GRIP_STYLES, value.grip)) {
    cockpit.grip = value.grip;
    if (typeof value.color === 'string' && Object.hasOwn(GRIP_COLORS, value.color))
      cockpit.color = value.color;
  }
  if (typeof value?.bar === 'string' && Object.hasOwn(BAR_STYLES, value.bar)) {
    cockpit.bar = value.bar;
    if (BAR_WIDTHS.includes(value.width)) cockpit.width = value.width;
  }
  return cockpit;
}

export function describeCockpit(cockpit) {
  const { grip, color, bar, width } = normalizeCockpit(cockpit);
  return [
    grip && GRIP_STYLES[grip] + ' · ' + GRIP_COLORS[color || 'black'].label,
    bar && BAR_STYLES[bar] + ' · ' + (width ? width + ' mm' : 'stock width'),
  ].filter(Boolean);
}
