import * as THREE from 'three';

const sunDirection = new THREE.Vector3(0.12, 0.023, -1).normalize();

const positionShader = /* glsl */ `
  varying vec3 vLocal;
  varying vec3 vWorld;
  void main() {
    vLocal = position;
    vWorld = (modelMatrix * vec4(position, 1.0)).xyz;
    gl_Position = projectionMatrix * viewMatrix * vec4(vWorld, 1.0);
  }
`;

const noiseShader = /* glsl */ `
  float hash(vec2 point) {
    return fract(sin(dot(point, vec2(127.1, 311.7))) * 43758.5453);
  }
  float grain(vec2 point) {
    vec2 cell = floor(point);
    vec2 blend = fract(point);
    blend = blend * blend * (3.0 - 2.0 * blend);
    return mix(mix(hash(cell), hash(cell + vec2(1.0, 0.0)), blend.x),
               mix(hash(cell + vec2(0.0, 1.0)), hash(cell + vec2(1.0, 1.0)), blend.x), blend.y);
  }
`;

function palette(colors) {
  return Object.fromEntries(
    Object.entries(colors).map(([name, color]) => [name, { value: new THREE.Color(color) }]),
  );
}

export function addCoastalHorizon(root, shore) {
  const sky = new THREE.Mesh(
    new THREE.SphereGeometry(115, 36, 20),
    new THREE.ShaderMaterial({
      side: THREE.BackSide,
      depthWrite: false,
      toneMapped: false,
      uniforms: {
        ...palette({
          horizon: 0xf4a99e,
          peach: 0xffac78,
          dusk: 0x86629f,
          zenith: 0x364e85,
          mist: 0xb3adcc,
          cloud: 0x74517f,
        }),
        sunDirection: { value: sunDirection },
      },
      vertexShader: positionShader,
      fragmentShader: /* glsl */ `
        varying vec3 vLocal;
        uniform vec3 horizon, peach, dusk, zenith, mist, cloud, sunDirection;
        ${noiseShader}
        void main() {
          vec3 direction = normalize(vLocal);
          float height = direction.y;
          float light = max(0.0, dot(direction, sunDirection));
          vec3 color = mix(horizon, peach, pow(light, 12.0));
          color = mix(color, mist, 1.0 - smoothstep(-0.14, 0.0, height));
          color = mix(color, dusk, smoothstep(0.015, 0.235, height));
          color = mix(color, zenith, smoothstep(0.22, 0.73, height));
          vec2 clouds = vec2(atan(direction.x, -direction.z) * 8.0, height * 26.0);
          float wisps = grain(clouds) * 0.60 + grain(clouds * 2.2 + 4.0) * 0.27
                        + grain(clouds * 5.1 - 2.0) * 0.13;
          float bank = smoothstep(0.06, 0.17, height) * (1.0 - smoothstep(0.22, 0.51, height));
          color = mix(color, mix(cloud, peach, pow(light, 17.0) * 0.36),
                      bank * smoothstep(0.42, 0.67, wisps) * 0.61);
          color = mix(color, vec3(1.0, 0.55, 0.29), pow(light, 80.0) * 0.34);
          float sun = smoothstep(0.99964, 0.99974, light);
          gl_FragColor = vec4(mix(color, vec3(1.0, 0.88, 0.61), sun), 1.0);
          #include <colorspace_fragment>
        }
      `,
    }),
  );
  sky.name = 'Coastal sky and sunset';
  sky.renderOrder = -10;
  root.add(sky);

  const sea = new THREE.Mesh(
    new THREE.PlaneGeometry(218, 112).rotateX(-Math.PI / 2).translate(0, -0.55, shore - 56),
    new THREE.ShaderMaterial({
      toneMapped: false,
      uniforms: {
        ...palette({
          shallow: 0x5cbab8,
          deep: 0x387d97,
          horizon: 0xc3a6b7,
          glint: 0xffbaa4,
          foam: 0xe0ede4,
        }),
        shore: { value: shore },
        sunSlope: { value: sunDirection.x / -sunDirection.z },
      },
      vertexShader: positionShader,
      fragmentShader: /* glsl */ `
        varying vec3 vLocal;
        varying vec3 vWorld;
        uniform vec3 shallow, deep, horizon, glint, foam;
        uniform float shore, sunSlope;
        ${noiseShader}
        void main() {
          vec2 point = vLocal.xz;
          float offshore = shore - point.y;
          float distanceToEye = length(vWorld - cameraPosition);
          float haze = smoothstep(9.0, 102.0, distanceToEye);
          float bend = sin(point.x * 2.8) * 0.52 + grain(point * vec2(3.0, 0.7));
          float wave = sin(point.y * 11.6 + bend) * 0.57
                     + sin(point.y * 8.9 + point.x * 3.3) * 0.26
                     + sin(point.y * 43.0 + point.x * 8.0) * 0.17;
          float rippleWidth = max(fwidth(point.x), fwidth(point.y));
          float detail = (1.0 - smoothstep(9.0, 44.0, distanceToEye))
                         * (1.0 - smoothstep(0.025, 0.26, rippleWidth));
          float swell = grain(point * vec2(0.4, 1.6)) * 0.68
                      + grain(point * vec2(0.95, 3.4)) * 0.32;
          float broadDetail = (1.0 - haze) * (1.0 - smoothstep(0.25, 1.2, rippleWidth));
          vec3 color = mix(shallow, deep, smoothstep(0.0, 22.0, offshore));
          color *= 0.97 + (swell - 0.4) * 0.21 * broadDetail + wave * 0.10 * detail;
          float ray = abs(point.x - sunSlope * -point.y);
          float reflection = exp(-ray / (0.78 + offshore * 0.09));
          float glimmer = smoothstep(0.18, 0.73, wave + grain(point * vec2(4.3, 8.0)) * 0.32);
          color = mix(color, glint, reflection * (0.075 + 0.19 * swell * broadDetail
                                                           + 0.43 * glimmer * detail));
          float front = 0.65 + sin(point.x * 1.05) * 0.085 + grain(point * 1.8) * 0.10;
          float edge = 1.0 - smoothstep(0.012, 0.093, abs(offshore - front));
          color = mix(color, foam, edge * (0.44 + glimmer * 0.29));
          gl_FragColor = vec4(mix(color, horizon, haze * 0.95), 1.0);
          #include <colorspace_fragment>
        }
      `,
    }),
  );
  sea.name = 'Turquoise coastal water';
  root.add(sea);
}
