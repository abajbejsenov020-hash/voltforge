import { Box3, Mesh, MeshBasicMaterial, PlaneGeometry, Vector3 } from 'three';
import { createContactTexture } from './render-lighting.js';

/** Small ground occlusion patches remain visible in both rendering modes. */
export function createVehicleContactShadow(scene) {
  const texture = createContactTexture();
  const geometry = new PlaneGeometry(1, 1).rotateX(-Math.PI / 2);
  const patch = () => {
    const mesh = new Mesh(
      geometry,
      new MeshBasicMaterial({
        color: 0x17222b,
        map: texture,
        transparent: true,
        depthWrite: false,
      }),
    );
    mesh.position.y = -0.001;
    mesh.visible = false;
    scene.add(mesh);
    return mesh;
  };
  const body = patch();
  const wheels = [
    { name: 'FrontWheel', patch: patch(), footprint: new Vector3(), size: new Vector3() },
    { name: 'RearWheel', patch: patch(), footprint: new Vector3(), size: new Vector3() },
  ];
  const center = new Vector3();
  const size = new Vector3();
  const world = new Vector3();
  const wheelBounds = new Box3();

  function updateWheels() {
    for (const wheel of wheels) {
      if (!wheel.node) continue;
      wheel.node.localToWorld(world.copy(wheel.footprint));
      const lift = Math.max(0, world.y);
      const spread = 1 + lift * 1.2;
      wheel.patch.position.x = world.x;
      wheel.patch.position.z = world.z;
      wheel.patch.scale.set(
        wheel.size.x * 0.83 * spread,
        1,
        Math.max(wheel.size.z * 2, wheel.size.x * 0.48) * spread,
      );
      wheel.patch.material.opacity = 0.55 * Math.exp(-lift * 6);
    }
  }

  return {
    fit(bounds, model) {
      bounds.getCenter(center);
      bounds.getSize(size);
      body.visible = !bounds.isEmpty();
      body.position.x = center.x;
      body.position.z = center.z;
      body.scale.set(size.x * 1.31, 1, size.z * 1.24);
      body.material.opacity = 0.4;
      for (const wheel of wheels) {
        const node =
          model.getObjectByName(wheel.name) ||
          model.children.find((child) => child.userData.groundContact === wheel.name);
        const hasWheel = node && !wheelBounds.setFromObject(node).isEmpty();
        wheel.node = hasWheel ? node : null;
        wheel.patch.visible = Boolean(hasWheel);
        if (!hasWheel) continue;
        wheelBounds.getSize(wheel.size);
        wheelBounds.getCenter(center);
        center.y = wheelBounds.min.y;
        wheel.footprint.copy(node.worldToLocal(center));
      }
      updateWheels();
    },
    updateWheels,
    hide() {
      body.visible = false;
      for (const wheel of wheels) {
        wheel.patch.visible = false;
        wheel.node = null;
      }
    },
    dispose() {
      for (const mesh of [body, ...wheels.map((wheel) => wheel.patch)]) {
        scene.remove(mesh);
        mesh.material.dispose();
      }
      geometry.dispose();
      texture.dispose();
    },
  };
}
