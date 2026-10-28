/**
 * Smart Veterinary Clinic - Interactive Three.js 3D WebGL Engine
 * Professional 3D Hero Scene & Interactive Pet Anatomy Scanner
 */

window.Vet3D = (function () {
  'use strict';

  // --------------------------------------------------------------------------
  // 1. HERO INTERACTIVE 3D SCENE
  // --------------------------------------------------------------------------
  function initHeroScene(containerId) {
    const container = document.getElementById(containerId);
    if (!container || typeof THREE === 'undefined') return;

    const width = container.clientWidth || 450;
    const height = container.clientHeight || 420;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 8);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Group for all rotating elements
    const heroGroup = new THREE.Group();
    scene.add(heroGroup);

    // Central 3D Medical Health Cross & Crystal Core
    const coreMat = new THREE.MeshPhysicalMaterial({
      color: 0x0d9488,
      emissive: 0x115e59,
      emissiveIntensity: 0.4,
      roughness: 0.15,
      metalness: 0.85,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1
    });

    // Medical Cross geometry: vertical + horizontal bars
    const vBar = new THREE.Mesh(new THREE.BoxGeometry(0.75, 2.3, 0.6), coreMat);
    const hBar = new THREE.Mesh(new THREE.BoxGeometry(2.3, 0.75, 0.6), coreMat);
    const crossGroup = new THREE.Group();
    crossGroup.add(vBar);
    crossGroup.add(hBar);
    heroGroup.add(crossGroup);

    // Golden / Emerald Paw Center Spheres (Pads)
    const padMat = new THREE.MeshStandardMaterial({
      color: 0x2dd4bf,
      emissive: 0x0f766e,
      roughness: 0.2,
      metalness: 0.7
    });

    const mainPad = new THREE.Mesh(new THREE.SphereGeometry(0.4, 24, 24), padMat);
    mainPad.position.set(0, 0, 0.35);
    crossGroup.add(mainPad);

    const toePositions = [
      [-0.45, 0.55, 0.35],
      [-0.15, 0.75, 0.35],
      [0.15, 0.75, 0.35],
      [0.45, 0.55, 0.35]
    ];
    toePositions.forEach(pos => {
      const toe = new THREE.Mesh(new THREE.SphereGeometry(0.16, 16, 16), padMat);
      toe.position.set(pos[0], pos[1], pos[2]);
      crossGroup.add(toe);
    });

    // Orbiting Diagnostic Torus Rings
    const ringMat1 = new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true, transparent: true, opacity: 0.6 });
    const ring1 = new THREE.Mesh(new THREE.TorusGeometry(2.2, 0.03, 16, 100), ringMat1);
    ring1.rotation.x = Math.PI / 3;
    heroGroup.add(ring1);

    const ringMat2 = new THREE.MeshBasicMaterial({ color: 0x6366f1, wireframe: true, transparent: true, opacity: 0.5 });
    const ring2 = new THREE.Mesh(new THREE.TorusGeometry(2.6, 0.02, 16, 100), ringMat2);
    ring2.rotation.y = Math.PI / 4;
    ring2.rotation.x = -Math.PI / 6;
    heroGroup.add(ring2);

    // Particle Constellation Nebula (300 glowing floating dots)
    const particleCount = 280;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 10;
      positions[i + 1] = (Math.random() - 0.5) * 8;
      positions[i + 2] = (Math.random() - 0.5) * 8;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const particleMat = new THREE.PointsMaterial({
      color: 0x2dd4bf,
      size: 0.08,
      transparent: true,
      opacity: 0.8
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // Dynamic Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
    scene.add(ambientLight);

    const pointLight1 = new THREE.PointLight(0x2dd4bf, 3, 20);
    pointLight1.position.set(4, 5, 4);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0x6366f1, 2.5, 20);
    pointLight2.position.set(-4, -4, 3);
    scene.add(pointLight2);

    // Mouse Parallax Interaction
    let targetRotationX = 0;
    let targetRotationY = 0;
    let mouseX = 0;
    let mouseY = 0;

    function onMouseMove(e) {
      const rect = container.getBoundingClientRect();
      mouseX = (e.clientX - rect.left) / width - 0.5;
      mouseY = (e.clientY - rect.top) / height - 0.5;

      targetRotationY = mouseX * 1.5;
      targetRotationX = mouseY * 1.2;
    }
    container.addEventListener('mousemove', onMouseMove);

    // Click pulse burst
    container.addEventListener('click', () => {
      if (typeof anime !== 'undefined') {
        anime({
          targets: crossGroup.scale,
          x: [1, 1.35, 1],
          y: [1, 1.35, 1],
          z: [1, 1.35, 1],
          duration: 650,
          easing: 'easeOutElastic(1, .5)'
        });
        anime({
          targets: crossGroup.rotation,
          y: crossGroup.rotation.y + Math.PI * 2,
          duration: 1000,
          easing: 'easeOutQuart'
        });
      }
    });

    // Resize listener
    window.addEventListener('resize', () => {
      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight;
      if (newWidth && newHeight) {
        camera.aspect = newWidth / newHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(newWidth, newHeight);
      }
    });

    // Render loop
    let clock = new THREE.Clock();
    function animate() {
      requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // Smooth easing toward cursor target
      heroGroup.rotation.y += (targetRotationY - heroGroup.rotation.y) * 0.06;
      heroGroup.rotation.x += (targetRotationX - heroGroup.rotation.x) * 0.06;

      // Base idle rotations
      crossGroup.position.y = Math.sin(elapsedTime * 1.5) * 0.15;
      ring1.rotation.z = elapsedTime * 0.4;
      ring2.rotation.z = -elapsedTime * 0.35;
      particles.rotation.y = elapsedTime * 0.05;

      renderer.render(scene, camera);
    }
    animate();
  }

  // --------------------------------------------------------------------------
  // 2. INTERACTIVE 3D PET ANATOMY & VITALS SCANNER
  // --------------------------------------------------------------------------
  function initPetAnatomyScanner(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container || typeof THREE === 'undefined') return;

    const width = container.clientWidth || 600;
    const height = container.clientHeight || 450;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
    camera.position.set(0, 0.5, 6.5);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    const modelGroup = new THREE.Group();
    scene.add(modelGroup);

    // Anatomical Stylized Holographic Pet Wireframe & Form (Canine/Feline Archetype)
    const petMat = new THREE.MeshPhysicalMaterial({
      color: 0x0f766e,
      wireframe: true,
      transparent: true,
      opacity: 0.75,
      roughness: 0.2
    });

    const bodyMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.65, 2.2, 16), petMat);
    bodyMesh.rotation.z = Math.PI / 2;
    modelGroup.add(bodyMesh);

    const chestMesh = new THREE.Mesh(new THREE.SphereGeometry(0.85, 16, 16), petMat);
    chestMesh.position.set(-0.7, 0.1, 0);
    modelGroup.add(chestMesh);

    const headMesh = new THREE.Mesh(new THREE.SphereGeometry(0.65, 16, 16), petMat);
    headMesh.position.set(-1.4, 0.8, 0);
    modelGroup.add(headMesh);

    // Snout
    const snoutMesh = new THREE.Mesh(new THREE.ConeGeometry(0.35, 0.6, 12), petMat);
    snoutMesh.rotation.z = Math.PI / 2;
    snoutMesh.position.set(-1.9, 0.65, 0);
    modelGroup.add(snoutMesh);

    // Ears
    const ear1 = new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.5, 8), petMat);
    ear1.position.set(-1.3, 1.4, 0.35);
    ear1.rotation.z = -0.2;
    modelGroup.add(ear1);

    const ear2 = new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.5, 8), petMat);
    ear2.position.set(-1.3, 1.4, -0.35);
    ear2.rotation.z = -0.2;
    modelGroup.add(ear2);

    // Legs (Front & Hind)
    const legGeo = new THREE.CylinderGeometry(0.18, 0.14, 1.3, 12);
    const legFL = new THREE.Mesh(legGeo, petMat);
    legFL.position.set(-0.7, -1.0, 0.5);
    modelGroup.add(legFL);

    const legFR = new THREE.Mesh(legGeo, petMat);
    legFR.position.set(-0.7, -1.0, -0.5);
    modelGroup.add(legFR);

    const legHL = new THREE.Mesh(legGeo, petMat);
    legHL.position.set(0.8, -1.0, 0.5);
    modelGroup.add(legHL);

    const legHR = new THREE.Mesh(legGeo, petMat);
    legHR.position.set(0.8, -1.0, -0.5);
    modelGroup.add(legHR);

    // Tail
    const tailMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.05, 1.0, 8), petMat);
    tailMesh.rotation.z = -Math.PI / 3;
    tailMesh.position.set(1.4, 0.5, 0);
    modelGroup.add(tailMesh);

    // Rotating Hologram Scanner Grid Base
    const gridHelper = new THREE.GridHelper(5, 16, 0x2dd4bf, 0x1e293b);
    gridHelper.position.y = -1.65;
    scene.add(gridHelper);

    // ------------------------------------------------------------------------
    // Interactive 3D Telemetry Hotspots
    // ------------------------------------------------------------------------
    const hotspots = [
      {
        id: 'heart',
        name: 'Cardiovascular Node (Heart)',
        color: 0xef4444,
        position: [-0.65, 0.05, 0.65],
        vitals: `${data?.heart_rate || 96} bpm (Sinus Rhythm Normal)`,
        notes: 'Cardiac auscultation clear. Normal S1/S2 heart sounds with no murmurs.'
      },
      {
        id: 'lungs',
        name: 'Pulmonary / Respiratory (Lungs)',
        color: 0x0284c7,
        position: [-0.2, 0.25, 0.65],
        vitals: `${data?.respiratory_rate || 22} rpm (Normal Bronchial)`,
        notes: 'Bilateral lung fields clear. Good thoracic wall excursion without wheezes.'
      },
      {
        id: 'ears',
        name: 'Cranial & Otic (Ears/Temp)',
        color: 0xf59e0b,
        position: [-1.4, 1.1, 0.4],
        vitals: `${data?.temperature || 38.5} °C (Normothermic)`,
        notes: 'Otoscopic exam: Tympanic membranes intact. External canals clean.'
      },
      {
        id: 'joints',
        name: 'Orthopedic / Hip Joint',
        color: 0x8b5cf6,
        position: [0.75, 0.1, 0.6],
        vitals: 'Full Range of Motion (Mobility Grade 1)',
        notes: 'Symmetrical weight bearing on all four limbs. Negative Ortolani sign.'
      },
      {
        id: 'chip',
        name: 'RFID Microchip Sensor',
        color: 0x10b981,
        position: [-0.85, 0.85, 0],
        vitals: `RFID Tag: ${data?.microchip_id || '985141001294821'}`,
        notes: '134.2 kHz ISO standard transponder verified active.'
      }
    ];

    const hotspotMeshes = [];
    hotspots.forEach(h => {
      const hGroup = new THREE.Group();
      hGroup.position.set(h.position[0], h.position[1], h.position[2]);

      // Core Glowing Beacon
      const beacon = new THREE.Mesh(
        new THREE.SphereGeometry(0.12, 16, 16),
        new THREE.MeshBasicMaterial({ color: h.color })
      );
      hGroup.add(beacon);

      // Outer Pulsating Pulse Ring
      const pulseRing = new THREE.Mesh(
        new THREE.RingGeometry(0.16, 0.22, 24),
        new THREE.MeshBasicMaterial({ color: h.color, side: THREE.DoubleSide, transparent: true, opacity: 0.8 })
      );
      hGroup.add(pulseRing);

      hGroup.userData = h;
      modelGroup.add(hGroup);
      hotspotMeshes.push({ group: hGroup, pulse: pulseRing, data: h });
    });

    // Lights
    const amb = new THREE.AmbientLight(0xffffff, 1.0);
    scene.add(amb);

    const dir = new THREE.DirectionalLight(0x2dd4bf, 2.0);
    dir.position.set(3, 5, 4);
    scene.add(dir);

    // Raycasting for click & hover on hotspots
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const readoutCard = document.getElementById('telemetryReadoutCard');
    const readoutTitle = document.getElementById('telemetryTitle');
    const readoutVitals = document.getElementById('telemetryVitals');
    const readoutNotes = document.getElementById('telemetryNotes');

    function selectHotspot(hotspotData) {
      if (!hotspotData) return;
      if (readoutTitle) readoutTitle.innerText = hotspotData.name;
      if (readoutVitals) readoutVitals.innerText = hotspotData.vitals;
      if (readoutNotes) readoutNotes.innerText = hotspotData.notes;

      if (readoutCard && typeof anime !== 'undefined') {
        anime({
          targets: readoutCard,
          scale: [0.95, 1],
          opacity: [0.7, 1],
          duration: 350,
          easing: 'easeOutBack'
        });
      }
    }

    container.addEventListener('click', (e) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(modelGroup.children, true);

      if (intersects.length > 0) {
        let current = intersects[0].object;
        while (current && current.parent && !current.userData.id) {
          current = current.parent;
        }
        if (current && current.userData && current.userData.id) {
          selectHotspot(current.userData);

          // Smoothly rotate model toward this node
          if (typeof anime !== 'undefined') {
            anime({
              targets: modelGroup.rotation,
              y: modelGroup.rotation.y + 0.8,
              duration: 800,
              easing: 'easeOutQuart'
            });
          }
        }
      }
    });

    // Rotate dragging on container
    let isDragging = false;
    let prevMouseX = 0;

    container.addEventListener('mousedown', (e) => {
      isDragging = true;
      prevMouseX = e.clientX;
    });

    window.addEventListener('mouseup', () => { isDragging = false; });
    window.addEventListener('mousemove', (e) => {
      if (isDragging) {
        const deltaX = e.clientX - prevMouseX;
        modelGroup.rotation.y += deltaX * 0.01;
        prevMouseX = e.clientX;
      }
    });

    // Initial default hotspot select
    selectHotspot(hotspots[0]);

    // Render loop
    let clock = new THREE.Clock();
    function animate() {
      requestAnimationFrame(animate);
      const time = clock.getElapsedTime();

      // Idle turntable rotation if not dragging
      if (!isDragging) {
        modelGroup.rotation.y += 0.005;
      }

      // Animate pulsing hotspot rings
      hotspotMeshes.forEach((item, idx) => {
        const s = 1 + Math.sin(time * 3 + idx) * 0.25;
        item.pulse.scale.set(s, s, s);
        item.pulse.material.opacity = 0.5 + Math.cos(time * 3 + idx) * 0.4;
      });

      renderer.render(scene, camera);
    }
    animate();
  }

  return {
    initHeroScene: initHeroScene,
    initPetAnatomyScanner: initPetAnatomyScanner
  };
})();
