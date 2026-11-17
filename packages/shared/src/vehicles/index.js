// Name index only: no stock specification, fitment or CAD claims are inferred.
const VEHICLE_INDEX = [];
function vehicleFamily(brand, type, models, aliases = []) {
  for (const model of models) {
    const name = brand + ' ' + model;
    VEHICLE_INDEX.push({
      id: type + ':' + name.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
      brand,
      model,
      name,
      type,
      aliases: aliases.map((a) => a + ' ' + model),
    });
  }
}
vehicleFamily(
  'KuKirin',
  'scooter',
  [
    'G2',
    'G2 VMP',
    'G2 Pro',
    'G2 Pro VMP',
    'G2 Pro ABE',
    'G2 Max',
    'G2 Master',
    'G2 Ultra',
    'G3',
    'G3 Pro',
    'G4',
    'G4 Max',
    'G4 Ultra',
    'M4',
    'M4 Pro',
    'M4 Max',
    'S1 Max',
    'S3 Pro',
    'A1',
    'C1 Pro',
    'T3',
    'T4',
  ],
  ['Kugoo Kirin', 'KugooKirin', 'Ku Kirin', 'Kirin', 'Kugoo'],
);
vehicleFamily('KuKirin', 'bike', ['X1'], ['Kugoo Kirin', 'KugooKirin']);
vehicleFamily('Kugoo', 'scooter', [
  'M2 Pro',
  'S1',
  'S1 Pro',
  'S3',
  'S3 Pro',
  'G-Booster',
  'G-Max',
  'G1',
  'G2 Pro',
]);
vehicleFamily('Ausom', 'scooter', [
  'Leopard',
  'Gallop',
  'L1',
  'L2',
  'L2 Max',
  'L2 Max Dual Motor',
  'DT1',
  'DT1 Pro',
  'DT2 Pro',
  'F1 Max',
  'Gosoul 2',
  'Gosoul 2 Pro',
  'Gosoul 2 Pro Dual Motor',
  'K20 Pro',
  'K20 Pro Dual Motor',
  'Laluz 2 Pro Dual Motor',
  'SR1',
]);
vehicleFamily(
  'Dualtron',
  'scooter',
  [
    'Thunder',
    'Thunder 2',
    'Thunder 3',
    'Ultra',
    'Ultra 2',
    'Victor',
    'Victor Luxury',
    'Victor Luxury Plus',
    'Eagle Pro',
    'Achilleus',
    'Storm',
    'Storm Limited',
    'X',
    'X2',
    'X Limited',
    'Spider',
    'Spider 2',
    'Mini',
    'Mini Special',
    'Popular',
    'City',
    'Togo',
    'Forever',
  ],
  ['MiniMotors Dualtron', 'Minimotors'],
);
vehicleFamily(
  'Segway Ninebot',
  'scooter',
  [
    'Max G30',
    'Max G30D',
    'Max G30LP',
    'Max G2',
    'Max G3',
    'F2',
    'F2 Pro',
    'F2 Plus',
    'F3',
    'F3 Pro',
    'E2',
    'E2 Plus',
    'E2 Pro',
    'ES1',
    'ES2',
    'ES4',
    'P65',
    'P100S',
    'GT1',
    'GT2',
    'GT3',
    'ZT3 Pro',
  ],
  ['Ninebot', 'Segway'],
);
vehicleFamily(
  'Xiaomi',
  'scooter',
  [
    'M365',
    'M365 Pro',
    'Pro 2',
    'Essential',
    '1S',
    'Mi 3',
    '4',
    '4 Lite',
    '4 Pro',
    '4 Ultra',
    '5',
    '5 Pro',
    '5 Max',
  ],
  ['Mi', 'Xiaomi Electric Scooter'],
);
vehicleFamily(
  'Kaabo',
  'scooter',
  [
    'Mantis 8',
    'Mantis 10',
    'Mantis 10 Pro',
    'Mantis King GT',
    'Mantis X',
    'Wolf Warrior 11',
    'Wolf Warrior X',
    'Wolf King',
    'Wolf King GT',
    'Wolf King GTR',
  ],
  ['Kaboo'],
);
vehicleFamily(
  'NAMI',
  'scooter',
  ['Burn-E', 'Burn-E 2', 'Burn-E 2 Max', 'Klima', 'Klima Max', 'Stellar', 'Super Stellar'],
  ['Nami Electric'],
);
vehicleFamily(
  'Vsett',
  'scooter',
  ['8', '8+', '9', '9+', '10+', '10 Apex', '11+', '11+ Super 72'],
  ['V Set'],
);
vehicleFamily('Zero', 'scooter', ['8', '9', '10', '10X', '11X']);
vehicleFamily('Inokim', 'scooter', ['Light 2', 'Quick 4', 'OX', 'OXO']);
vehicleFamily('Apollo', 'scooter', [
  'Air',
  'Go',
  'City',
  'City Pro',
  'Explore',
  'Ghost',
  'Phantom',
  'Pro',
]);
vehicleFamily('InMotion', 'scooter', ['S1', 'S1F', 'Climber', 'RS', 'RS Lite'], ['In Motion']);
vehicleFamily('NIU', 'scooter', [
  'KQi1 Pro',
  'KQi2 Pro',
  'KQi3 Sport',
  'KQi3 Pro',
  'KQi3 Max',
  'KQi Air',
  'KQi 300P',
  'KQi 300X',
]);
vehicleFamily('Yume', 'scooter', ['Y10', 'X11', 'Hawk', 'Hawk Pro', 'Raptor', 'Osprey']);
vehicleFamily('Teverun', 'scooter', [
  'Fighter Mini',
  'Fighter 10',
  'Fighter 11',
  'Fighter Supreme',
  'Blade Mini',
  'Blade GT',
]);
vehicleFamily('RoadRunner', 'scooter', ['RS5', 'RS5 Max', 'RS5 Pro', 'RX7']);
vehicleFamily('EMOVE', 'scooter', [
  'Touring',
  'Cruiser',
  'Cruiser S',
  'RoadRunner',
  'RoadRunner Pro',
]);
vehicleFamily('Varla', 'scooter', ['Pegasus', 'Eagle One', 'Eagle One Pro', 'Eagle One V2.0']);
vehicleFamily('Hiley', 'scooter', ['Tiger 8', 'Tiger 9', 'Tiger 10', 'Tiger 10 Pro']);
vehicleFamily('Joyor', 'scooter', ['S5', 'S8', 'S10-S', 'Y8-S']);
vehicleFamily('iScooter', 'scooter', ['i9', 'i10', 'iX3', 'iX4', 'iX5', 'iX6']);
vehicleFamily('iENYRID', 'scooter', ['M4 Pro S+', 'M4 Pro S+ Max', 'ES1', 'ES10']);
vehicleFamily('Bogist', 'scooter', ['C1 Pro', 'M5 Pro']);
vehicleFamily(
  'Sur-Ron',
  'bike',
  ['Light Bee', 'Light Bee X', 'Ultra Bee', 'Storm Bee'],
  ['Surron', 'Sur Ron'],
);
vehicleFamily(
  'Talaria',
  'bike',
  ['Sting', 'Sting R MX4', 'Sting Pro MX5', 'XXX', 'X3'],
  ['Talaria Moto'],
);
vehicleFamily('Engwe', 'bike', [
  'EP-2 Pro',
  'Engine Pro',
  'Engine Pro 2.0',
  'M20',
  'X20',
  'X24',
  'X26',
  'L20',
  'L20 2.0',
  'P275 Pro',
  'MapFour N1 Air',
]);
vehicleFamily('Fiido', 'bike', [
  'D4S',
  'D11',
  'D21',
  'M1 Pro',
  'M21',
  'T1',
  'T2',
  'Titan',
  'C11',
  'C21',
  'Air',
]);
vehicleFamily('Aventon', 'bike', [
  'Aventure',
  'Aventure.2',
  'Level',
  'Level.2',
  'Pace 500',
  'Pace 500.3',
  'Soltera',
  'Sinch',
  'Abound',
  'Ramblas',
]);
vehicleFamily(
  'Rad Power',
  'bike',
  [
    'RadRunner',
    'RadRunner 2',
    'RadRunner Plus',
    'RadRover 6 Plus',
    'RadCity 5 Plus',
    'RadExpand 5',
    'RadWagon 4',
  ],
  ['Rad Power Bikes', 'RadPower'],
);
vehicleFamily('Trek', 'bike', [
  'Marlin',
  'Marlin+',
  'Powerfly',
  'Rail',
  'Allant+',
  'Verve+',
  'FX+',
]);
vehicleFamily('Giant', 'bike', [
  'Talon',
  'Talon E+',
  'Explore E+',
  'Trance X E+',
  'Reign E+',
  'Fathom E+',
]);
vehicleFamily('Specialized', 'bike', [
  'Rockhopper',
  'Turbo Levo',
  'Turbo Kenevo',
  'Turbo Vado',
  'Turbo Como',
  'Turbo Tero',
]);
vehicleFamily('Cube', 'bike', [
  'Reaction Hybrid',
  'Stereo Hybrid',
  'Kathmandu Hybrid',
  'Touring Hybrid',
]);
vehicleFamily('Cannondale', 'bike', ['Moterra Neo', 'Trail Neo', 'Adventure Neo', 'Tesoro Neo']);
vehicleFamily('Haibike', 'bike', ['AllMtn', 'HardNine', 'HardSeven', 'Trekking']);
vehicleFamily('Himiway', 'bike', ['Cruiser', 'Zebra', 'Cobra', 'Big Dog']);
vehicleFamily('Lectric', 'bike', ['XP 2.0', 'XP 3.0', 'XP Lite', 'XPedition', 'XPeak']);
vehicleFamily('Super73', 'bike', ['S2', 'R', 'RX', 'ZX', 'Z Miami'], ['Super 73']);
const CYRILLIC = {
  а: 'a',
  б: 'b',
  в: 'v',
  г: 'g',
  д: 'd',
  е: 'e',
  ё: 'e',
  ж: 'zh',
  з: 'z',
  и: 'i',
  й: 'i',
  к: 'k',
  л: 'l',
  м: 'm',
  н: 'n',
  о: 'o',
  п: 'p',
  р: 'r',
  с: 's',
  т: 't',
  у: 'u',
  ф: 'f',
  х: 'h',
  ц: 'ts',
  ч: 'ch',
  ш: 'sh',
  щ: 'sh',
  ы: 'y',
  э: 'e',
  ю: 'yu',
  я: 'ya',
  ь: '',
  ъ: '',
};
function normalizeVehicleName(value) {
  return String(value ?? '')
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[а-яё]/g, (c) => CYRILLIC[c])
    .replace(/\+/g, ' plus ')
    .replace(/kugookirin/g, 'kukirin')
    .replace(
      /\b(?:kugo\s*kirin|kugoo\s*kirin|kugookirin|ku\s*kirin|kukrin|kukirn|kukurin|kirin)\b/g,
      'kukirin',
    )
    .replace(/\b(?:segway\s*ninebot|segway|nine\s*bot)\b/g, 'ninebot')
    .replace(/\bmini\s*motors\b/g, 'minimotors')
    .replace(/\bsur\s*-?\s*ron\b/g, 'surron')
    .replace(/(\d)(max|master|ultra|pro|plus|gt|gtr)\b/g, '$1 $2')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
    .replace(/\s+/g, ' ');
}
function editDistance(a, b) {
  const row = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    let prev = row[0];
    row[0] = i;
    for (let j = 1; j <= b.length; j++) {
      const old = row[j];
      row[j] = Math.min(row[j] + 1, row[j - 1] + 1, prev + (a[i - 1] === b[j - 1] ? 0 : 1));
      prev = old;
    }
  }
  return row[b.length];
}
function finderQuery(value) {
  return normalizeVehicleName(value)
    .replace(/\b(?:electric|scooter|escooter|ebike|bike|20[12]\d)\b/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}
function vehicleMatchScore(query, record) {
  const q = finderQuery(query);
  if (!q) return 1;
  const qc = q.replace(/ /g, ''),
    aliases = [record.name, record.model, ...(record.aliases || [])].map(normalizeVehicleName);
  let best = 0;
  for (const a of aliases) {
    const ac = a.replace(/ /g, '');
    if (a === q || ac === qc) {
      best = Math.max(best, 120);
      continue;
    }
    if (a.startsWith(q) || ac.startsWith(qc)) {
      best = Math.max(best, 95 - Math.min(15, a.length - q.length));
      continue;
    }
    if (a.includes(q) || ac.includes(qc)) {
      best = Math.max(best, 76);
      continue;
    }
    const words = a.split(' '),
      qt = q.split(' ');
    let score = 0,
      ok = true;
    for (const token of qt) {
      let value = 0;
      for (const word of words) {
        if (word === token) value = Math.max(value, 10);
        else if (word.startsWith(token)) value = Math.max(value, 7);
        else if (
          token.length >= 4 &&
          word.length >= 4 &&
          !/\d/.test(token + word) &&
          editDistance(token, word) <= (token.length >= 7 ? 2 : 1)
        )
          value = Math.max(value, 4);
      }
      if (!value) {
        ok = false;
        break;
      }
      score += value;
    }
    if (ok) best = Math.max(best, 45 + score / qt.length);
  }
  return best;
}
function vehicleCandidates(saved = []) {
  const list = [...VEHICLE_INDEX];
  const seen = new Set(list.map((v) => normalizeVehicleName(v.name)));
  for (const v of saved) {
    const name = v.vehicle?.trim();
    if (name && !seen.has(normalizeVehicleName(name))) {
      seen.add(normalizeVehicleName(name));
      list.push({
        id: 'saved:' + v.id,
        name,
        model: name,
        brand: 'My vehicles',
        type: v.type,
        aliases: [],
        custom: true,
      });
    }
  }
  return list;
}
function findVehicles(query, { type = 'scooter', brand = '', saved = [] } = {}) {
  const q = finderQuery(query);
  return vehicleCandidates(saved)
    .filter((v) => (!brand || v.brand === brand) && (q || brand || v.type === type))
    .map((v) => ({ ...v, score: vehicleMatchScore(query, v) }))
    .filter((v) => v.score > 0)
    .sort(
      (a, b) =>
        b.score - a.score + (a.type === type ? -0.1 : 0) + (b.type === type ? 0.1 : 0) ||
        a.name.localeCompare(b.name, undefined, { numeric: true }),
    );
}
function canonicalVehicleName(name) {
  const key = normalizeVehicleName(name).replace(/ /g, '');
  return (
    VEHICLE_INDEX.find((v) =>
      [v.name, ...v.aliases].some((a) => normalizeVehicleName(a).replace(/ /g, '') === key),
    )?.name || String(name).trim()
  );
}
// E-moto name library. Regional names remain distinct; no specifications are inferred.
vehicleFamily('Sur-Ron', 'bike', ['Light Bee S', 'Hyper Bee'], ['Surron', 'Sur Ron']);
vehicleFamily(
  'Talaria',
  'bike',
  [
    'Sting MX3',
    'Sting Pro',
    'Komodo',
    'Komodo MX',
    'Komodo L3E',
    'XXX MX',
    'XXX L1E',
    'Sting Pro L1E',
    'Junior ET01',
  ],
  ['Talaria Moto'],
);
vehicleFamily(
  'Arctic Leopard',
  'bike',
  [
    'XF Pro',
    'XF Pro MX',
    'XF Pro Super',
    'XE Pro R',
    'XE Pro S',
    'XE Pro S Super',
    'XE Pro S Enduro',
    'XE L1E',
    'E-XE 880 Super',
    'E-XE 880 Enduro',
    'E-XE 800 Enduro',
    'E-XE L3E',
    'E-16Z',
    'E-20Y',
    'E-ZPRO',
  ],
  ['ArcticLeopard', 'Arctic', 'Spirit Leopard'],
);
vehicleFamily(
  'Stark',
  'bike',
  ['Varg', 'Varg MX', 'Varg MX 1.2', 'Varg EX', 'Varg SM', 'Varg SM Skoll', 'Varg Factory Edition'],
  ['Stark Future'],
);
vehicleFamily(
  'E Ride Pro',
  'bike',
  ['S', 'SS', 'SS 2.0', 'SS 3.0', '4.0', 'SR', 'Mini R'],
  ['Eride Pro', 'E-Ride Pro', 'E Ride', 'Eride'],
);
vehicleFamily(
  'Altis',
  'bike',
  ['Sigma', 'Sigma MX', 'Delta', 'Delta x DBK', 'Omega'],
  ['Altis Powersports'],
);
// Common abbreviations are search aliases, not additional vehicle records.
const EMOTO_ALIASES = {
  'Sur-Ron Light Bee X': ['Surron LBX', 'Sur Ron LBX', 'Surron Lightbee X'],
  'Sur-Ron Light Bee S': ['Surron LBS'],
  'Sur-Ron Ultra Bee': ['Surron UB', 'Surron Ultrabee'],
  'Sur-Ron Storm Bee': ['Surron Stormbee'],
  'Talaria Sting MX3': ['Talaria MX3'],
  'Talaria Sting R MX4': ['Talaria MX4', 'Talaria Sting R'],
  'Talaria Sting Pro MX5': ['Talaria MX5', 'Talaria Sting MX5'],
  'Talaria XXX': ['Talaria X3 Concept'],
  'Arctic Leopard E-XE 880 Enduro': [
    'Arctic Leopard EXE 880',
    'Arctic Leopard EXE880',
    'Arctic Leopard EXE 880 Enduro',
  ],
  'Arctic Leopard E-XE 800 Enduro': ['Arctic Leopard EXE 800', 'Arctic Leopard EXE800'],
  'E Ride Pro SR': ['E Ride Pro Pro SR'],
  'E Ride Pro S': ['E Ride Pro Pro S'],
  'E Ride Pro SS 3.0': ['Eride 3.0', 'Eride Pro 3.0'],
  'Stark Varg SM Skoll': ['Stark Varg SM Sköll'],
};
for (const record of VEHICLE_INDEX) record.aliases.push(...(EMOTO_ALIASES[record.name] || []));
const EMOTO_SOURCES = {
  'Sur-Ron': 'https://sur-ron.com/',
  Talaria: 'https://talaria.cn/',
  'Arctic Leopard': 'https://arctic-leopard.com/en-us/cheetah_9/107.html',
  Stark: 'https://starkfuture.com/',
  'E Ride Pro': 'https://www.eridepro.com/pages/user-manual',
  Altis: 'https://www.altispowersports.com/',
};

// Keep the original array surface available to older app extensions.
const VEHICLES = {
  scooter: VEHICLE_INDEX.filter((v) => v.type === 'scooter').map((v) => v.name),
  bike: VEHICLE_INDEX.filter((v) => v.type === 'bike').map((v) => v.name),
};

export {
  VEHICLE_INDEX,
  VEHICLES,
  normalizeVehicleName,
  findVehicles,
  canonicalVehicleName,
  vehicleCandidates,
  vehicleMatchScore,
  EMOTO_SOURCES,
};
