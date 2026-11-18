import { MathUtils, MeshPhysicalMaterial, MeshStandardMaterial } from 'three';

const COATED = /powder coat|body finish|frame coating|painted|paint finish|wrap/;
const METAL = /alloy|aluminium|aluminum|anodiz|brushed|gold|gunmetal|machined|metal|steel|silver/;
const MATTE = /rubber|grip|tread|traction mat|cable|hose|saddle|seat/;
const OPTICS = /glass|optic|lens|^screen$/;
const MARKINGS = /decal|graphic|label|marking|printed|wordmark/;

function tuneFinish(material) {
  if (!material?.isMeshStandardMaterial) return material;
  const name = material.name.toLowerCase();
  // Texture maps and emissive details belong to the specific authored model.
  if (material.map || material.roughnessMap || material.metalnessMap || MARKINGS.test(name))
    return material;
  if (MATTE.test(name)) {
    material.metalness = 0;
    material.roughness = Math.max(material.roughness, 0.8);
    return material;
  }
  if (material.transparent || material.emissiveMap || material.emissive.getHex() !== 0)
    return material;
  if (COATED.test(name) || OPTICS.test(name)) {
    const paint = COATED.test(name);
    let finish = material;
    if (!material.isMeshPhysicalMaterial) {
      finish = new MeshPhysicalMaterial();
      const defines = finish.defines;
      MeshStandardMaterial.prototype.copy.call(finish, material);
      finish.defines = defines;
    }
    finish.metalness = Math.min(finish.metalness, paint ? 0.25 : 0.12);
    finish.roughness = MathUtils.clamp(
      finish.roughness * 0.84,
      paint ? 0.24 : 0.12,
      paint ? 0.58 : 0.3,
    );
    finish.clearcoat = Math.max(finish.clearcoat, paint ? 0.28 : 0.42);
    finish.clearcoatRoughness = paint ? 0.33 : 0.19;
    return finish;
  }
  if (METAL.test(name) || material.metalness >= 0.55)
    material.roughness = MathUtils.clamp(material.roughness * 0.84, 0.22, 0.58);
  return material;
}

/** Tune each unique material in a loaded model once, retaining paint names and texture ownership. */
export function refineVehicleFinishes(root) {
  const finishes = new Map();
  const resolve = (material) => {
    if (!finishes.has(material)) finishes.set(material, tuneFinish(material));
    return finishes.get(material);
  };
  root.traverse((object) => {
    if (!object.isMesh) return;
    object.material = Array.isArray(object.material)
      ? object.material.map(resolve)
      : resolve(object.material);
  });
  for (const [source, finish] of finishes) {
    if (source !== finish) source.dispose();
  }
}
