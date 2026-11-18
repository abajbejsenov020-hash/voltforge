import { buildComponentModel } from './model-builder.js';
import { createComponentStudio } from './studio-lighting.js';
import * as THREE from 'three';
import { CATALOG } from '@voltforge/shared/catalog';
import { COMPONENT_REFERENCES } from '@voltforge/shared/appearances';

/* On-demand component previews. One shared WebGL renderer serves visible tiles.
   Procedural shapes are appearance references, not supplier CAD or fitment data. */
export const PartPreviews = (() => {
  const safe = (s) =>
    String(s ?? '').replace(
      /[&<>"']/g,
      (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c],
    );
  function describe(p) {
    const ref = COMPONENT_REFERENCES[p.id];
    if (!ref)
      return {
        family: 'unverified',
        label: p.template
          ? 'Choose an exact product'
          : p.request
            ? 'Exact replacement needed'
            : 'Product appearance not verified',
        reference: null,
        model: null,
      };
    return {
      family: ref.model?.type || 'photo-only',
      label:
        ref.kind === 'user-reference' ? 'Your product reference' : 'Manufacturer product photo',
      reference: ref.image,
      source: ref.source,
      imageSource: ref.imageSource,
      variantNote: ref.variantNote || '',
      model: ref.model || null,
    };
  }
  function markup(p, large = false) {
    const info = describe(p);
    if (!info.reference)
      return (
        '<div class="component-preview component-needs-part"><div class="component-unverified"><strong>Exact part needed</strong><span>' +
        safe(
          p.template
            ? 'Custom specification'
            : p.request
              ? 'Supplier replacement request'
              : 'Product reference unavailable',
        ) +
        '</span></div><span class="component-fidelity">' +
        safe(info.label) +
        '</span></div>'
      );
    return (
      '<div class="component-preview ' +
      (large ? 'component-preview-large' : '') +
      '" data-preview-part="' +
      safe(p.id) +
      '"><div class="component-photo-pane component-reference"><img class="component-real-photo" src="' +
      safe(info.reference) +
      '" width="900" height="900" loading="lazy" alt="' +
      safe(p.brand + ' ' + p.name) +
      ' product reference photograph"></div>' +
      (info.model
        ? '<div class="component-model-pane" hidden>' +
          modelMarkup(p, large) +
          '</div><div class="component-view-switch" aria-label="Appearance view"><button type="button" data-part-view="photo" aria-pressed="true">Photo</button><button type="button" data-part-view="model" aria-pressed="false">3D' +
          (large ? ' approximation' : '') +
          '</button></div>'
        : '') +
      '<span class="component-real-note">' +
      safe(info.label) +
      '</span></div>'
    );
  }
  function modelMarkup(p, large = false) {
    const info = describe(p);
    return (
      '<div class="component-visual ' +
      (large ? 'component-large' : '') +
      '"><canvas data-component="' +
      safe(p.id) +
      '" width="' +
      (large ? 900 : 240) +
      '" height="' +
      (large ? 540 : 200) +
      '" tabindex="0" role="group" aria-label="3D ' +
      safe(p.brand + ' ' + p.name) +
      '. Drag or use arrow keys to rotate; plus and minus to zoom."></canvas><span class="component-fallback" hidden>3D preview unavailable</span><span class="component-hint" aria-hidden="true">' +
      (large ? 'Drag to rotate · + / − to zoom' : '3D · drag to rotate') +
      '</span>' +
      (large
        ? '<div class="component-tools"><button type="button" data-component-action="out" aria-label="Zoom component out">−</button><button type="button" data-component-action="in" aria-label="Zoom component in">+</button><button type="button" data-component-action="reset">Reset view</button></div>'
        : '') +
      '</div><span class="component-fidelity">' +
      'Photo-guided 3D approximation' +
      '</span>'
    );
  }
  function createModel(p, T) {
    return buildComponentModel(p, T, describe);
  }
  let renderer,
    scene,
    studio,
    camera,
    activeModel,
    lastId,
    quality = 'high',
    appliedQuality,
    failed = false;
  const observers = new WeakMap();
  const states = new WeakMap(),
    mounted = new WeakSet();
  const previewMargin = 120;
  function init() {
    if (failed || typeof THREE === 'undefined') return false;
    if (renderer) return true;
    try {
      renderer = new THREE.WebGLRenderer({
        alpha: false,
        antialias: true,
        preserveDrawingBuffer: true,
      });
      renderer.setPixelRatio(1);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.toneMapping = THREE.NeutralToneMapping;
      renderer.setClearColor(0xe9ecf0, 1);
      scene = new THREE.Scene();
      studio = createComponentStudio(renderer, scene);
      camera = new THREE.PerspectiveCamera(32, 1, 0.01, 40);
      renderer.domElement.addEventListener('webglcontextlost', (e) => {
        e.preventDefault();
        failed = true;
      });
      renderer.domElement.addEventListener('webglcontextrestored', () => {
        studio.resetContext();
        appliedQuality = undefined;
        failed = false;
        refreshVisible();
      });
      return true;
    } catch (error) {
      failed = true;
      console.warn('Component 3D previews unavailable', error);
      return false;
    }
  }
  // Component motion happens only in response to direct input.
  function setRenderPreferences({ quality: preference } = {}) {
    const next = preference === 'efficient' ? 'efficient' : 'high';
    if (quality === next) return;
    quality = next;
    refreshVisible();
  }
  function refreshVisible() {
    if (typeof document === 'undefined') return;
    for (const canvas of document.querySelectorAll('canvas[data-component]')) {
      const rect = canvas.getBoundingClientRect();
      if (
        rect.width &&
        rect.height &&
        rect.bottom > -previewMargin &&
        rect.top < window.innerHeight + previewMargin
      )
        draw(canvas);
    }
  }
  function draw(canvas) {
    if (!canvas.isConnected) return;
    const fallback = canvas.parentElement.querySelector('.component-fallback');
    if (!init()) {
      if (fallback) fallback.hidden = false;
      return;
    }
    const p = CATALOG.find((x) => x.id === canvas.dataset.component);
    if (!p) return;
    try {
      if (quality !== appliedQuality) {
        studio.setQuality(quality);
        appliedQuality = quality;
      }
      if (lastId !== p.id) {
        if (activeModel) {
          scene.remove(activeModel.root);
          activeModel.dispose();
        }
        activeModel = null;
        lastId = undefined;
        activeModel = createModel(p, THREE);
        scene.add(activeModel.root);
        const bounds = new THREE.Box3().setFromObject(activeModel.root),
          center = bounds.getCenter(new THREE.Vector3()),
          size = bounds.getSize(new THREE.Vector3());
        activeModel.root.position.sub(center);
        activeModel.radius = Math.max(size.x, size.y, size.z) * 0.5;
        activeModel.root.traverse((object) => {
          if (!object.isMesh) return;
          object.castShadow = true;
          object.receiveShadow = true;
        });
        studio.fit(size, activeModel.radius);
        lastId = p.id;
      }
      const state = states.get(canvas) || { yaw: 0.48, pitch: 0.32, zoom: 1 },
        w = canvas.width,
        h = canvas.height;
      const scale = quality === 'efficient' ? 0.65 : 1;
      const frameWidth = Math.max(1, Math.round(w * scale));
      const frameHeight = Math.max(1, Math.round(h * scale));
      if (renderer.domElement.width !== frameWidth || renderer.domElement.height !== frameHeight)
        renderer.setSize(frameWidth, frameHeight, false);
      camera.aspect = frameWidth / frameHeight;
      camera.updateProjectionMatrix();
      const radius = activeModel.radius || 0.8,
        dist = ((radius / Math.sin((32 * Math.PI) / 360)) * 1.32) / state.zoom;
      camera.position.set(
        Math.sin(state.yaw) * Math.cos(state.pitch) * dist,
        Math.sin(state.pitch) * dist,
        Math.cos(state.yaw) * Math.cos(state.pitch) * dist,
      );
      camera.lookAt(0, 0, 0);
      renderer.render(scene, camera);
      const c = canvas.getContext('2d');
      if (!c) throw new Error('Canvas 2D is unavailable');
      c.drawImage(renderer.domElement, 0, 0, w, h);
      canvas.dataset.renderQuality = quality;
      canvas.dataset.renderResolution = `${frameWidth}×${frameHeight}`;
      if (fallback) fallback.hidden = true;
    } catch (error) {
      if (fallback) fallback.hidden = false;
      console.warn('Component preview failed', error);
    }
  }
  function mount(container) {
    observers.get(container)?.disconnect();
    const canvases = [...container.querySelectorAll('canvas[data-component]')];
    for (const canvas of canvases) {
      if (!mounted.has(canvas)) {
        mounted.add(canvas);
        const state = { yaw: 0.48, pitch: 0.32, zoom: 1 };
        states.set(canvas, state);
        let drag = null;
        canvas.addEventListener('pointerdown', (e) => {
          if (e.button !== undefined && e.button !== 0) return;
          drag = [e.clientX, e.clientY];
          canvas.setPointerCapture?.(e.pointerId);
        });
        canvas.addEventListener('pointermove', (e) => {
          if (!drag) return;
          state.yaw -= (e.clientX - drag[0]) * 0.014;
          state.pitch = Math.max(
            -1.25,
            Math.min(1.25, state.pitch + (e.clientY - drag[1]) * 0.012),
          );
          drag = [e.clientX, e.clientY];
          draw(canvas);
        });
        for (const event of ['pointerup', 'pointercancel', 'lostpointercapture'])
          canvas.addEventListener(event, () => (drag = null));
        canvas.addEventListener('keydown', (e) => {
          if (
            !['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', '+', '=', '-', '0'].includes(e.key)
          )
            return;
          e.preventDefault();
          if (e.key === 'ArrowLeft') state.yaw -= 0.18;
          if (e.key === 'ArrowRight') state.yaw += 0.18;
          if (e.key === 'ArrowUp') state.pitch = Math.min(1.25, state.pitch + 0.15);
          if (e.key === 'ArrowDown') state.pitch = Math.max(-1.25, state.pitch - 0.15);
          if (['+', '='].includes(e.key)) state.zoom = Math.min(2, state.zoom + 0.1);
          if (e.key === '-') state.zoom = Math.max(0.65, state.zoom - 0.1);
          if (e.key === '0') Object.assign(state, { yaw: 0.48, pitch: 0.32, zoom: 1 });
          draw(canvas);
        });
      }
    }
    for (const button of container.querySelectorAll('[data-part-view]'))
      button.onclick = () => {
        const pane = button.closest('.component-preview'),
          mode = button.dataset.partView;
        pane.querySelector('.component-photo-pane').hidden = mode !== 'photo';
        pane.querySelector('.component-model-pane').hidden = mode !== 'model';
        pane
          .querySelectorAll('[data-part-view]')
          .forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.partView === mode)));
        if (mode === 'model') draw(pane.querySelector('canvas'));
      };
    for (const button of container.querySelectorAll('[data-component-action]'))
      button.onclick = () => {
        const canvas = button.closest('.component-visual').querySelector('canvas'),
          state = states.get(canvas);
        if (!state) return;
        if (button.dataset.componentAction === 'in') state.zoom = Math.min(2, state.zoom + 0.15);
        if (button.dataset.componentAction === 'out')
          state.zoom = Math.max(0.65, state.zoom - 0.15);
        if (button.dataset.componentAction === 'reset')
          Object.assign(state, { yaw: 0.48, pitch: 0.32, zoom: 1 });
        draw(canvas);
      };
    if (typeof IntersectionObserver === 'undefined') {
      for (const canvas of canvases) draw(canvas);
    } else {
      const observer = new IntersectionObserver(
        (entries) => {
          for (const entry of entries)
            if (entry.isIntersecting && entry.target.dataset.renderQuality !== quality)
              draw(entry.target);
        },
        { rootMargin: `${previewMargin}px` },
      );
      observers.set(container, observer);
      for (const canvas of canvases) observer.observe(canvas);
    }
  }
  return { describe, markup, createModel, mount, setRenderPreferences };
})();
