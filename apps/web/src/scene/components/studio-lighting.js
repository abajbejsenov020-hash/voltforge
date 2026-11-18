import * as THREE from 'three';
import { createContactTexture, createReflectionMap } from '../render-lighting.js';

const KEY_POSITION = new THREE.Vector3(3.2, 5.2, 3.8);

/** One set of softboxes and one shadow map for the shared component renderer. */
export function createComponentStudio(renderer, scene) {
  const key = new THREE.DirectionalLight(0xffefdc, 2.25);
  const fill = new THREE.DirectionalLight(0xe0ebff, 0.8);
  fill.position.set(-3.5, 3, 2.2);
  const edge = new THREE.DirectionalLight(0xf1f6ff, 1.65);
  edge.position.set(0.5, 2.8, -4);
  scene.add(new THREE.HemisphereLight(0xf0f4ff, 0x78808d, 0.75), key, fill, edge);

  renderer.shadowMap.type = THREE.PCFShadowMap;
  key.shadow.mapSize.set(512, 512);
  key.shadow.radius = 3;
  key.shadow.bias = -0.00015;
  key.shadow.normalBias = 0.003;
  key.shadow.autoUpdate = false;

  const ground = new THREE.PlaneGeometry(1, 1);
  ground.rotateX(-Math.PI / 2);
  const projected = new THREE.Mesh(
    ground,
    new THREE.ShadowMaterial({ color: 0x26313e, opacity: 0.19, depthWrite: false }),
  );
  projected.receiveShadow = true;
  projected.renderOrder = 1;
  const contactTexture = createContactTexture();
  const contact = new THREE.Mesh(
    ground,
    new THREE.MeshBasicMaterial({
      color: 0x28303d,
      map: contactTexture,
      transparent: true,
      opacity: 0.28,
      depthWrite: false,
    }),
  );
  scene.add(contact, projected);

  let reflection;
  return {
    setQuality(quality) {
      const high = quality === 'high';
      key.castShadow = projected.visible = renderer.shadowMap.enabled = high;
      if (!reflection) {
        reflection = createReflectionMap(renderer);
        scene.environment = reflection.texture;
      }
      scene.environmentIntensity = high ? 0.92 : 0.72;
      key.shadow.needsUpdate = high;
    },
    fit(size, radius) {
      contact.position.y = -size.y / 2 - radius * 0.015;
      contact.scale.set(Math.max(size.x * 1.85, radius), 1, Math.max(size.z * 1.85, radius));
      projected.position.y = contact.position.y - 0.001;
      projected.scale.set(radius * 5.5, 1, radius * 5.5);
      key.position.copy(KEY_POSITION).multiplyScalar(radius);
      const shadowCamera = key.shadow.camera;
      const extent = radius * 1.75;
      shadowCamera.left = shadowCamera.bottom = -extent;
      shadowCamera.right = shadowCamera.top = extent;
      shadowCamera.near = radius;
      shadowCamera.far = radius * 12;
      shadowCamera.updateProjectionMatrix();
      key.shadow.needsUpdate = true;
    },
    resetContext() {
      key.shadow.dispose();
      key.shadow.map = null;
      reflection?.dispose();
      reflection = undefined;
      scene.environment = null;
    },
  };
}
