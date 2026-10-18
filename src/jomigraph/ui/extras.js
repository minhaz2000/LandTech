/* Home risk summary, 3D mouza map, pre-purchase check. Uses globals from app.js (currentLang, currentRole). */
(function () {
  const X = {
    bn: { title: "জমিগ্রাফ এআই", sub: "কাল্পনিক ডেটায় জমির রেকর্ড মিলিয়ে দেখার ডেমো", red: "লাল", yellow: "হলুদ", green: "সবুজ",
      redD: "অসঙ্গতি আছে", yellowD: "দেখা দরকার", greenD: "সঙ্গতিপূর্ণ", map: "মৌজা ম্যাপ (৩ডি)", mapD: "রঙিন প্লট ঘুরিয়ে দেখুন, ক্লিকে জমির পেজ",
      verify: "কেনার আগে যাচাই", verifyD: "দাগ নম্বর বা মালিকের নাম লিখুন", list: "জমির তালিকা", home: "হোম", plots: "টি জমি",
      ph: "দাগ নম্বর, খতিয়ান বা নাম", go: "যাচাই", none: "এই তথ্যে কোনো জমি পাওয়া যায়নি।", open: "পূর্ণ ইতিহাস দেখুন →",
      vg: "রেকর্ডে কোনো অসঙ্গতি পাওয়া যায়নি", vy: "কেনার আগে আরও যাচাই দরকার", vr: "রেকর্ডে অসঙ্গতি পাওয়া গেছে", next: "পরের ধাপ",
      note: "ডেমো, কাল্পনিক তথ্য। এটি আইনি সিদ্ধান্ত বা মালিকানার সনদ নয়।", drag: "ঘোরাতে টানুন, জুম করতে স্ক্রল বা পিঞ্চ করুন", loading: "লোড হচ্ছে...",
      disclaimer_map: "কাল্পনিক ডেমো মৌজা নকশা — বাস্তব ভৌগোলিক সীমানা নয়", lineage: "বংশপরম্পরা সংযোগ",
      area_label: "জমির পরিমাণ:", open_details: "ক্লিক করে বিস্তারিত দেখুন →", shatak: "শতক",
      status_contradiction: "অসঙ্গতি পাওয়া গেছে", status_review: "পর্যালোচনা প্রয়োজন", status_consistent: "সঙ্গতিপূর্ণ" },
    en: { title: "JomiGraph AI", sub: "Demo that cross-checks land records on fictional data", red: "Red", yellow: "Yellow", green: "Green",
      redD: "Contradiction found", yellowD: "Needs review", greenD: "Consistent", map: "Mouza map (3D)", mapD: "Rotate coloured plots, click for the parcel page",
      verify: "Check before you buy", verifyD: "Enter a dag number or holder name", list: "Parcel list", home: "Home", plots: " parcels",
      ph: "Dag number, khatian or name", go: "Check", none: "No parcel matched.", open: "See full history →",
      vg: "No contradiction found in the records", vy: "More checking needed before buying", vr: "Contradiction found in the records", next: "Next step",
      note: "Demo, fictional data. Not a legal ruling or proof of ownership.", drag: "Drag to rotate, scroll or pinch to zoom", loading: "Loading...",
      disclaimer_map: "Fictional demo cadastral layout — Not real geographic boundaries", lineage: "Lineage View",
      area_label: "Recorded Area:", open_details: "Click for full history →", shatak: "decimals",
      status_contradiction: "Contradiction Found", status_review: "Review Required", status_consistent: "Consistent" }
  };
  const S = () => X[currentLang] || X.bn;
  const COL = { CONTRADICTION: "red", REVIEW: "yellow", CONSISTENT: "green" };
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const num = (n) => (currentLang === "bn" ? toBanglaDigits(n) : String(n));
  const root = () => document.getElementById("app-root");
  const getJSON = (u) => fetch(u).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); });
  let stopMap = null;

  window.extraChrome = function (hash) {
    if (stopMap) { stopMap(); stopMap = null; }
    let nav = document.getElementById("x-nav");
    if (!currentRole) { nav && nav.remove(); return; }
    if (!nav) { nav = document.createElement("nav"); nav.id = "x-nav"; nav.className = "x-nav"; document.body.appendChild(nav); }
    const s = S(), it = [
      ["#/", "🏠", s.home],
      ["#/map", "🗺️", s.map.split(" ")[0] + " " + (currentLang === "bn" ? "ম্যাপ" : "")],
      ["#/verify", "🔍", s.verify],
      ["#/verify-deed", "📜", (currentLang === "bn" ? "দলিল যাচাই" : "Verify Deed")],
      ["#/ussd", "📱", (currentLang === "bn" ? "ইউএসএসডি" : "USSD")],
      ["#/my-land", "📝", currentLang === "bn" ? "আমার জমি" : "My land"],
      ["#/parcels", "📋", s.list]
    ];
    nav.innerHTML = it.map(([h, i, l]) => `<a href="${h}" class="${hash === h ? "on" : ""}"><span>${i}</span>${l.trim()}</a>`).join("");
  };

  window.extraRoute = function (hash) {
    if (window.myLandRoute && window.myLandRoute(hash)) return true;
    if (hash === "#/" || hash === "") { if (window.renderHomeGeo) window.renderHomeGeo(); else home(); return true; }
    if (hash === "#/map") { mapScreen(); return true; }
    if (hash === "#/verify") { verifyScreen(); return true; }
    if (hash.startsWith("#/verify-deed")) { verifyDeedScreen(hash); return true; }
    if (hash === "#/ussd") { ussdSimulatorScreen(); return true; }
    return false;
  };

  async function home() {
    const s = S(); root().innerHTML = `<div class="x-wrap"><p>${s.loading}</p></div>`;
    const parcels = await getJSON(`/parcels?lang=${currentLang}&role=${currentRole}`);
    const g = { red: [], yellow: [], green: [] };
    parcels.forEach((p) => g[COL[p.status_code] || "green"].push(p));
    root().innerHTML = `<div class="x-wrap">
      <div class="x-hero"><h1>${s.title}</h1><p>${s.sub}</p></div>
      <div class="x-grid">${["red", "yellow", "green"].map((c) => `<button type="button" class="x-stat ${c}" data-c="${c}"><b>${num(g[c].length)}</b><span>${s[c]} · ${s[c + "D"]}</span></button>`).join("")}</div>
      <div id="x-list"></div>
      <div class="x-actions">
        <a class="x-big" href="#/map">🗺️ <strong>${s.map}</strong><small>${s.mapD}</small></a>
        <a class="x-big" href="#/verify">🔍 <strong>${s.verify}</strong><small>${s.verifyD}</small></a>
        <a class="x-big" href="#/verify-deed">📜 <strong>${currentLang === "bn" ? "দলিল যাচাই ও কিউআর" : "Verify Deed & QR"}</strong><small>${currentLang === "bn" ? "ডিজিটাল ফিঙ্গারপ্রিন্ট ও কিউআর যাচাই" : "Cryptographic hash check & QR"}</small></a>
        <a class="x-big" href="#/ussd">📱 <strong>${currentLang === "bn" ? "ফিচার-ফোন (USSD)" : "USSD Simulator"}</strong><small>${currentLang === "bn" ? "*123*45# ডায়াল সিমুলেটর" : "*123*45# dial simulator"}</small></a>
      </div>
      <p class="x-note">${s.note}</p></div>`;
    const show = (c) => {
      document.querySelectorAll(".x-stat").forEach((b) => b.classList.toggle("on", b.dataset.c === c));
      document.getElementById("x-list").innerHTML = `<div class="x-list">${g[c].map((p) => `<a class="x-item" href="#/parcel/${encodeURIComponent(p.id)}"><span>${esc(p.label)}</span><i class="x-dot ${c}"></i></a>`).join("")}</div>`;
    };
    document.querySelectorAll(".x-stat").forEach((b) => b.addEventListener("click", () => show(b.dataset.c)));
    show(g.red.length ? "red" : g.yellow.length ? "yellow" : "green");
  }

  async function verifyScreen() {
    const s = S();
    root().innerHTML = `<div class="x-wrap"><div class="x-hero"><h1>🔍 ${s.verify}</h1><p>${s.verifyD}</p></div>
      <div class="x-search"><input id="x-q" placeholder="${s.ph}" autocomplete="off" inputmode="search"><button id="x-go" class="btn-primary" type="button">${s.go}</button></div><div id="x-out"></div></div>`;
    const out = document.getElementById("x-out"), q = document.getElementById("x-q");
    async function show(id, chips) {
      const d = await getJSON(`/parcel/${encodeURIComponent(id)}?lang=${currentLang}&role=citizen`);
      const c = COL[d.overall_status_code] || "green";
      const head = { green: s.vg, yellow: s.vy, red: s.vr }[c], icon = { green: "✅", yellow: "⚠️", red: "⛔" }[c];
      const steps = [...new Set(d.alerts.map((a) => a.recommended_next_step))];
      out.innerHTML = `<div class="x-verdict ${c}"><h2>${icon} ${head}</h2><div>${esc(d.mouza)} · ${num(d.dag_no)}</div>
        ${d.alerts.map((a) => `<p>${esc(a.message)}</p>`).join("")}
        ${steps.length ? `<p><strong>${s.next}:</strong> ${steps.map(esc).join("; ")}</p>` : ""}
        <p><a href="#/parcel/${encodeURIComponent(id)}">${s.open}</a></p>
        ${chips.length > 1 ? `<div class="x-chips">${chips.map((r) => `<button type="button" class="x-chip" data-id="${esc(r.id)}">${esc(r.label)}</button>`).join("")}</div>` : ""}
        <p class="x-note">${s.note}</p></div>`;
      out.querySelectorAll(".x-chip").forEach((b) => b.addEventListener("click", () => show(b.dataset.id, chips)));
    }
    async function run() {
      const v = q.value.trim(); if (v.length < 2) return;
      const r = await getJSON(`/search?q=${encodeURIComponent(v)}&lang=${currentLang}`);
      if (!r.length) { out.innerHTML = `<p>${s.none}</p>`; return; }
      show(r[0].id, r.slice(0, 8));
    }
    document.getElementById("x-go").addEventListener("click", run);
    q.addEventListener("keydown", (e) => { if (e.key === "Enter") run(); });
  }

  /* -------------------------------------------------------------
   * Enhanced 3D Mouza Cadastral Map (Tasks 3, 4, 5)
   * ------------------------------------------------------------- */

  // Procedural canvas textures (zero external downloads)
  function createFieldCanvasTexture(baseColorHex, isFurrow) {
    const cv = document.createElement("canvas");
    cv.width = 256; cv.height = 256;
    const ctx = cv.getContext("2d");
    ctx.fillStyle = baseColorHex;
    ctx.fillRect(0, 0, 256, 256);

    // Subtle crop rows or soil striations
    ctx.strokeStyle = "rgba(0, 0, 0, 0.08)";
    ctx.lineWidth = isFurrow ? 5 : 3;
    for (let y = 8; y < 256; y += 16) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(256, y);
      ctx.stroke();
    }
    // Subtle organic grass/stipple flecks
    ctx.fillStyle = "rgba(255, 255, 255, 0.12)";
    for (let i = 0; i < 240; i++) {
      const rx = (i * 47) % 256, ry = (i * 83) % 256;
      ctx.fillRect(rx, ry, 2, 2);
    }
    const tex = new THREE.CanvasTexture(cv);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    tex.repeat.set(1.5, 1.5);
    return tex;
  }

  // Deterministic irregular polygon shape for village cadastral plots
  function createIrregularPolygonShape(P, seed) {
    const s = new THREE.Shape();
    const hash = (n) => {
      let v = ((seed * 1103515245 + n * 12345) & 0x7fffffff) / 0x7fffffff;
      return (v - 0.5) * 0.45; // Subtle organic variation
    };
    const hw = (P * 0.95) / 2, hd = (P * 0.95) / 2;
    const pts = [
      [-hw + hash(1), -hd + hash(2)],
      [hw + hash(3), -hd + hash(4)],
      [hw + hash(5), hd + hash(6)],
      [-hw + hash(7), hd + hash(8)]
    ];
    s.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) s.lineTo(pts[i][0], pts[i][1]);
    s.closePath();
    return { shape: s, pts };
  }

  async function mapScreen() {
    const s = S();
    root().innerHTML = `<div class="x-wrap">
      <div class="x-hero">
        <h1>🗺️ ${s.map}</h1>
        <p>${s.mapD}</p>
      </div>
      <div class="x-map-banner" role="note">
        <span>ℹ️</span> <strong>${s.disclaimer_map}</strong>
      </div>
      <div class="x-legend">
        <span><i style="background:#22c55e"></i>${s.green}</span>
        <span><i style="background:#f59e0b"></i>${s.yellow}</span>
        <span><i style="background:#ef4444"></i>${s.red}</span>
        <button type="button" id="x-lineage-btn" class="x-lineage-btn"><span>🔗</span> ${s.lineage}</button>
        <span style="color:#64748b; font-size: 0.82rem; margin-left: auto;">${s.drag}</span>
      </div>
      <div class="x-map-box" id="x-map">
        <div class="x-card-tip" id="x-card"></div>
      </div>
    </div>`;

    const parcels = await getJSON(`/parcels?lang=${currentLang}&role=${currentRole}`);
    const box = document.getElementById("x-map");
    const cardTip = document.getElementById("x-card");
    const lineageBtn = document.getElementById("x-lineage-btn");
    if (!box || typeof THREE === "undefined") return;

    // Layout: Group by mouza, arranged cleanly in blocks
    const by = {};
    parcels.forEach((p) => {
      const m = p.label.split(/ (?:দাগ|Dag) /)[0];
      (by[m] = by[m] || []).push(p);
    });

    const P = 3.6, G = 1.0, spots = [], labels = [];
    let bx = 0, bz = 0, rowH = 0, inRow = 0;

    Object.keys(by).forEach((m) => {
      const n = by[m].length;
      const cols = Math.ceil(Math.sqrt(n));
      const rows = Math.ceil(n / cols);
      const w = cols * (P + G), h = rows * (P + G);
      if (inRow === (innerWidth < 600 ? 2 : 3)) {
        bx = 0; bz += rowH + 6; rowH = 0; inRow = 0;
      }
      by[m].forEach((p, i) => {
        spots.push({
          p,
          x: bx + (i % cols) * (P + G),
          z: bz + Math.floor(i / cols) * (P + G),
          mouza: m,
          index: i
        });
      });
      labels.push({ m, x: bx + w / 2 - G / 2, z: bz - 2.5 });
      bx += w + 6;
      rowH = Math.max(rowH, h);
      inRow++;
    });

    const maxX = Math.max(...spots.map((o) => o.x)) + P;
    const maxZ = Math.max(...spots.map((o) => o.z)) + P;
    const cx = maxX / 2, cz = maxZ / 2;
    const span = Math.max(maxX, maxZ);

    // Scene & Renderer Setup with ACESFilmic Tone Mapping
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xd8eee0);
    scene.fog = new THREE.Fog(0xd8eee0, span * 1.5, span * 3.8);

    const cam = new THREE.PerspectiveCamera(42, 1, 0.1, 500);
    cam.position.set(cx + span * 0.35, span * (innerWidth < 600 ? 1.45 : 0.95), cz + span * (innerWidth < 600 ? 1.1 : 0.95));
    cam.fov = innerWidth < 600 ? 58 : 42;
    cam.updateProjectionMatrix();

    const ren = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    ren.setPixelRatio(Math.min(devicePixelRatio, 2));
    ren.shadowMap.enabled = true;
    ren.shadowMap.type = THREE.PCFSoftShadowMap;
    ren.toneMapping = THREE.ACESFilmicToneMapping;
    ren.toneMappingExposure = 1.05;
    box.appendChild(ren.domElement);

    const ctl = new THREE.OrbitControls(cam, ren.domElement);
    ctl.target.set(cx, 0.2, cz);
    ctl.enableDamping = true;
    ctl.dampingFactor = 0.08;
    ctl.maxPolarAngle = Math.PI * 0.46;
    ctl.minDistance = 7;
    ctl.maxDistance = span * 3.2;

    // Atmospheric Lighting: Warm Late-Afternoon Sun + Sky/Ground Hemisphere
    const hemi = new THREE.HemisphereLight(0xe0f2fe, 0x86efac, 0.85);
    scene.add(hemi);

    const sun = new THREE.DirectionalLight(0xfff8e7, 1.1);
    sun.position.set(cx + span * 0.8, span * 1.3, cz - span * 0.5);
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024);
    Object.assign(sun.shadow.camera, {
      left: -span * 1.1, right: span * 1.1,
      top: span * 1.1, bottom: -span * 1.1,
      near: 1, far: span * 4
    });
    sun.target.position.set(cx, 0, cz);
    scene.add(sun, sun.target);

    // Shared Procedural Textures & Materials
    const texGreen = createFieldCanvasTexture("#22c55e", true);
    const texYellow = createFieldCanvasTexture("#f59e0b", true);
    const texRed = createFieldCanvasTexture("#ef4444", true);

    const groundTex = createFieldCanvasTexture("#d6ebd9", false);
    groundTex.repeat.set(span * 0.4, span * 0.4);

    const groundMat = new THREE.MeshStandardMaterial({
      color: 0xcde5d3,
      map: groundTex,
      roughness: 0.9,
      metalness: 0.02
    });
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(span * 6, span * 6), groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.position.set(cx, -0.02, cz);
    ground.receiveShadow = true;
    scene.add(ground);

    // Earthen Boundary (আইল) Material
    const ailMat = new THREE.LineBasicMaterial({ color: 0x785135, linewidth: 2 });
    const ailBaseMat = new THREE.MeshStandardMaterial({ color: 0x8d5b36, roughness: 0.9 });

    // Status Material Config
    const STATUS_CFG = {
      green: { col: 0x22c55e, emissive: 0x052e16, tex: texGreen },
      yellow: { col: 0xf59e0b, emissive: 0x451a03, tex: texYellow },
      red: { col: 0xef4444, emissive: 0x7f1d1d, tex: texRed }
    };

    const meshes = [];
    const parcelMapById = {};

    // 1. Natural Irregular Plot Meshes
    spots.forEach(({ p, x, z, mouza, index }) => {
      const c = COL[p.status_code] || "green";
      const cfg = STATUS_CFG[c];
      const seed = (p.id.split("").reduce((acc, ch) => acc + ch.charCodeAt(0), 0) + index * 17) % 10000;
      const { shape, pts } = createIrregularPolygonShape(P, seed);

      // Low, predominantly flat extruded parcel plot
      const extrudeGeom = new THREE.ExtrudeGeometry(shape, {
        depth: 0.14,
        bevelEnabled: true,
        bevelSegments: 1,
        steps: 1,
        bevelSize: 0.03,
        bevelThickness: 0.03
      });
      extrudeGeom.rotateX(-Math.PI / 2);

      const mat = new THREE.MeshStandardMaterial({
        color: cfg.col,
        map: cfg.tex,
        roughness: 0.65,
        metalness: 0.05,
        emissive: cfg.emissive,
        emissiveIntensity: c === "red" ? 0.35 : 0.15
      });

      const m = new THREE.Mesh(extrudeGeom, mat);
      m.position.set(x, 0.02, z);
      m.castShadow = true;
      m.receiveShadow = true;

      // Raised earthen boundary perimeter (মাটির আইল)
      const lineGeom = new THREE.BufferGeometry().setFromPoints(
        pts.concat([pts[0]]).map(([px, pz]) => new THREE.Vector3(px, 0.18, pz))
      );
      const ailLine = new THREE.Line(lineGeom, ailMat);
      m.add(ailLine);

      // Dag number badge indicator
      const dagCv = document.createElement("canvas");
      dagCv.width = 128; dagCv.height = 64;
      const dg = dagCv.getContext("2d");
      dg.fillStyle = "rgba(255, 255, 255, 0.9)";
      dg.beginPath();
      dg.roundRect ? dg.roundRect(4, 4, 120, 56, 12) : dg.rect(4, 4, 120, 56);
      dg.fill();
      dg.fillStyle = c === "red" ? "#dc2626" : c === "yellow" ? "#d97706" : "#15803d";
      dg.font = "bold 26px sans-serif";
      dg.textAlign = "center";
      dg.textBaseline = "middle";
      const dagNo = p.label.split(/ (?:দাগ|Dag) /)[1] || p.id.replace("PARCEL_", "");
      dg.fillText(dagNo, 64, 32);

      const dagSprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(dagCv) }));
      dagSprite.scale.set(1.4, 0.7, 1);
      dagSprite.position.set(0, 0.6, 0);
      m.add(dagSprite);

      m.userData = { p, c, y0: m.position.y, origEmissive: cfg.emissive };
      scene.add(m);
      meshes.push(m);
      parcelMapById[p.id] = m;
    });

    // 2. Rural Landscape Elements: Village Canal / Pond (পুকুর / খাল)
    const pondShape = new THREE.Shape();
    pondShape.moveTo(-4, -1);
    pondShape.quadraticCurveTo(-1, -5, 5, -2);
    pondShape.quadraticCurveTo(8, 2, 4, 6);
    pondShape.quadraticCurveTo(-2, 7, -4, -1);
    const pondGeom = new THREE.ShapeGeometry(pondShape);
    pondGeom.rotateX(-Math.PI / 2);
    const pondMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      roughness: 0.12,
      metalness: 0.25,
      opacity: 0.85,
      transparent: true
    });
    const pond = new THREE.Mesh(pondGeom, pondMat);
    pond.position.set(cx - span * 0.45, 0.01, cz + span * 0.35);
    scene.add(pond);

    // 3. Winding Village Earthen Paths (মাটির রাস্তা)
    const pathMat = new THREE.MeshStandardMaterial({ color: 0xd4b996, roughness: 0.95 });
    for (let r = 0; r < 4; r++) {
      const pathW = maxX + 10;
      const pathGeom = new THREE.PlaneGeometry(pathW, 0.9);
      const path = new THREE.Mesh(pathGeom, pathMat);
      path.rotation.x = -Math.PI / 2;
      path.position.set(cx, 0.005, (r * (maxZ / 3)) + 1);
      path.receiveShadow = true;
      scene.add(path);
    }

    // 4. Rural Bangladeshi Homesteads (চৌচালা / টিনশেড ঘর)
    const houseWallMat = new THREE.MeshStandardMaterial({ color: 0xd7c4b7, roughness: 0.85 });
    const houseRoofMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.45, metalness: 0.35 }); // Tin roof
    const thatchRoofMat = new THREE.MeshStandardMaterial({ color: 0xb45309, roughness: 0.9 }); // Thatch

    for (let h = 0; h < 6; h++) {
      const hx = ((h * 61 + 13) % 100) / 100 * (maxX + 10) - 5;
      const hz = ((h * 41 + 29) % 100) / 100 * (maxZ + 10) - 5;
      if (spots.some((o) => Math.hypot(o.x - hx, o.z - hz) < P)) continue;

      const houseGroup = new THREE.Group();
      const wall = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.8, 1.1), houseWallMat);
      wall.position.y = 0.4;
      wall.castShadow = true;
      wall.receiveShadow = true;
      houseGroup.add(wall);

      // Pitched tin/thatch roof
      const roof = new THREE.Mesh(new THREE.ConeGeometry(1.15, 0.65, 4), (h % 2 === 0 ? houseRoofMat : thatchRoofMat));
      roof.position.y = 1.05;
      roof.rotation.y = Math.PI / 4;
      roof.castShadow = true;
      houseGroup.add(roof);

      houseGroup.position.set(hx, 0, hz);
      scene.add(houseGroup);
    }

    // 5. Diverse Trees: Coconut / Supari Palms & Rounded Mango / Banyan Trees
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x6b4423, roughness: 0.9 });
    const palmFrondMat = new THREE.MeshStandardMaterial({ color: 0x15803d, roughness: 0.6 });
    const banyanFoliageMat = new THREE.MeshStandardMaterial({ color: 0x166534, roughness: 0.75 });

    for (let i = 0; i < 48; i++) {
      const tx = (((i * 89 + 7) % 100) / 100) * (maxX + 14) - 7;
      const tz = (((i * 47 + 23) % 100) / 100) * (maxZ + 14) - 7;
      if (spots.some((o) => Math.hypot(o.x - tx, o.z - tz) < P * 0.95)) continue;

      const treeGroup = new THREE.Group();
      if (i % 2 === 0) {
        // Coconut palm: Tall slender trunk + palm crown
        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.12, 2.4, 5), trunkMat);
        trunk.position.y = 1.2;
        trunk.castShadow = true;
        treeGroup.add(trunk);

        const frond = new THREE.Mesh(new THREE.ConeGeometry(1.0, 0.45, 6), palmFrondMat);
        frond.position.y = 2.45;
        frond.castShadow = true;
        treeGroup.add(frond);
      } else {
        // Mango / Banyan tree: Shorter trunk + rounded lush canopy
        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.18, 1.2, 6), trunkMat);
        trunk.position.y = 0.6;
        trunk.castShadow = true;
        treeGroup.add(trunk);

        const canopy = new THREE.Mesh(new THREE.DodecahedronGeometry(0.85, 1), banyanFoliageMat);
        canopy.position.y = 1.8;
        canopy.castShadow = true;
        treeGroup.add(canopy);
      }
      treeGroup.position.set(tx, 0, tz);
      scene.add(treeGroup);
    }

    // 6. Mouza Name Labels (Clean 2D Billboard Sprites)
    labels.forEach((l) => {
      const cv = document.createElement("canvas");
      cv.width = 512; cv.height = 128;
      const g = cv.getContext("2d");
      g.fillStyle = "rgba(255, 255, 255, 0.94)";
      g.beginPath();
      g.roundRect ? g.roundRect(8, 20, 496, 88, 44) : g.rect(8, 20, 496, 88);
      g.fill();
      g.fillStyle = "#14532d";
      g.font = "bold 46px sans-serif";
      g.textAlign = "center";
      g.textBaseline = "middle";
      g.fillText(l.m, 256, 64);

      const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(cv) }));
      sp.scale.set(7.5, 1.85, 1);
      sp.position.set(l.x, 3.2, l.z);
      scene.add(sp);
    });

    // 7. 3D Parcel Lineage Visualization Curves (Subdivisions & Lineage)
    const lineageGroup = new THREE.Group();
    lineageGroup.visible = false;
    scene.add(lineageGroup);

    function createLineageArc(startMesh, endMesh, arcColor) {
      if (!startMesh || !endMesh) return;
      const v0 = new THREE.Vector3(startMesh.position.x, 0.3, startMesh.position.z);
      const v2 = new THREE.Vector3(endMesh.position.x, 0.3, endMesh.position.z);
      const midX = (v0.x + v2.x) / 2;
      const midZ = (v0.z + v2.z) / 2;
      const dist = v0.distanceTo(v2);
      const v1 = new THREE.Vector3(midX, Math.min(dist * 0.45, 4.2), midZ);

      const curve = new THREE.QuadraticBezierCurve3(v0, v1, v2);
      const tubeGeom = new THREE.TubeGeometry(curve, 24, 0.08, 6, false);
      const tubeMat = new THREE.MeshStandardMaterial({
        color: arcColor,
        roughness: 0.3,
        emissive: arcColor,
        emissiveIntensity: 0.45
      });
      const tube = new THREE.Mesh(tubeGeom, tubeMat);
      lineageGroup.add(tube);
    }

    // Connect parent PARCEL_PLANTED_R4 to its children R4_A & R4_B
    const parentR4 = parcelMapById["PARCEL_PLANTED_R4"];
    const childR4A = parcelMapById["PARCEL_PLANTED_R4_A"];
    const childR4B = parcelMapById["PARCEL_PLANTED_R4_B"];
    if (parentR4 && childR4A) createLineageArc(parentR4, childR4A, 0x3b82f6);
    if (parentR4 && childR4B) createLineageArc(parentR4, childR4B, 0x8b5cf6);

    // Connect sequential family story parcels (PARCEL_STORY_01 to 02, etc.)
    for (let st = 1; st < 5; st++) {
      const fromP = parcelMapById[`PARCEL_STORY_0${st}`];
      const toP = parcelMapById[`PARCEL_STORY_0${st + 1}`];
      if (fromP && toP) createLineageArc(fromP, toP, 0x10b981);
    }

    let lineageActive = false;
    if (lineageBtn) {
      lineageBtn.addEventListener("click", () => {
        lineageActive = !lineageActive;
        lineageGroup.visible = lineageActive;
        lineageBtn.classList.toggle("on", lineageActive);
      });
    }

    // 8. Pointer, Raycasting & Rich Interactive Card
    const ray = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let hover = null;
    let down = null;
    let isFlying = false;

    const setM = (e) => {
      const r = ren.domElement.getBoundingClientRect();
      mouse.set(
        ((e.clientX - r.left) / r.width) * 2 - 1,
        -((e.clientY - r.top) / r.height) * 2 + 1
      );
      ray.setFromCamera(mouse, cam);
      return ray.intersectObjects(meshes)[0];
    };

    function showCardTip(mesh, clientX, clientY) {
      if (!mesh || !mesh.userData || !mesh.userData.p) {
        cardTip.style.display = "none";
        return;
      }
      const p = mesh.userData.p;
      const c = mesh.userData.c;
      const r = box.getBoundingClientRect();

      const statusLabels = {
        red: s.status_contradiction,
        yellow: s.status_review,
        green: s.status_consistent
      };
      const badgeClasses = {
        red: "badge-contradiction",
        yellow: "badge-review",
        green: "badge-consistent"
      };

      cardTip.innerHTML = `
        <strong>${esc(p.label)}</strong>
        <span class="badge ${badgeClasses[c] || 'badge-consistent'}">${statusLabels[c] || c}</span>
        <div style="font-size:0.8rem; color:#475569; margin: 4px 0;">
          ${s.area_label} <b>${num(p.recorded_area || "10.0")} ${s.shatak}</b>
        </div>
        <a class="x-prompt" data-id="${esc(p.id)}">${s.open_details}</a>
      `;

      cardTip.style.display = "block";
      const cardX = Math.min(clientX - r.left + 12, box.clientWidth - 280);
      const cardY = Math.min(clientY - r.top - 20, box.clientHeight - 140);
      cardTip.style.left = Math.max(cardX, 10) + "px";
      cardTip.style.top = Math.max(cardY, 10) + "px";

      const promptLink = cardTip.querySelector(".x-prompt");
      if (promptLink) {
        promptLink.onclick = (ev) => {
          ev.stopPropagation();
          flyToAndNavigate(mesh);
        };
      }
    }

    ren.domElement.addEventListener("pointermove", (e) => {
      if (isFlying) return;
      const h = setM(e);
      const newHover = h ? h.object : null;

      if (newHover !== hover) {
        if (hover) {
          hover.position.y = hover.userData.y0;
          hover.material.emissiveIntensity = hover.userData.c === "red" ? 0.35 : 0.15;
        }
        hover = newHover;
        if (hover) {
          // Slight hover lift and emissive glow
          hover.position.y = hover.userData.y0 + 0.12;
          hover.material.emissiveIntensity = 0.55;
        }
      }

      ren.domElement.style.cursor = hover ? "pointer" : "grab";
      if (hover) {
        showCardTip(hover, e.clientX, e.clientY);
      } else {
        cardTip.style.display = "none";
      }
    });

    ren.domElement.addEventListener("pointerdown", (e) => {
      down = [e.clientX, e.clientY];
    });

    ren.domElement.addEventListener("pointerup", (e) => {
      if (isFlying) return;
      if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 7) return;
      const h = setM(e);
      if (h) {
        const mesh = h.object;
        showCardTip(mesh, e.clientX, e.clientY);
        flyToAndNavigate(mesh);
      }
    });

    // 9. Camera Fly-To & Page Transition
    function flyToAndNavigate(mesh) {
      if (!mesh || !mesh.userData || !mesh.userData.p) return;
      const targetId = mesh.userData.p.id;

      const isReduced = document.body.classList.contains("reduce-motion") ||
        (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);

      if (isReduced) {
        location.hash = "#/parcel/" + encodeURIComponent(targetId);
        return;
      }

      isFlying = true;
      cardTip.style.display = "none";

      const startCam = cam.position.clone();
      const startTarget = ctl.target.clone();
      const endTarget = new THREE.Vector3(mesh.position.x, 0.2, mesh.position.z);
      const endCam = new THREE.Vector3(mesh.position.x + 3.2, 3.8, mesh.position.z + 4.2);

      const flyStart = performance.now();
      const flyDuration = 550;

      function flyLoop(now) {
        const progress = Math.min(1, (now - flyStart) / flyDuration);
        const ease = 1 - Math.pow(1 - progress, 3); // Cubic ease-out

        cam.position.lerpVectors(startCam, endCam, ease);
        ctl.target.lerpVectors(startTarget, endTarget, ease);
        ctl.update();

        if (progress < 1) {
          requestAnimationFrame(flyLoop);
        } else {
          isFlying = false;
          location.hash = "#/parcel/" + encodeURIComponent(targetId);
        }
      }
      requestAnimationFrame(flyLoop);
    }

    // 10. Resize & Render Loop
    const resize = () => {
      const w = box.clientWidth, h = box.clientHeight;
      ren.setSize(w, h);
      cam.aspect = w / h;
      cam.updateProjectionMatrix();
    };
    resize();
    window.addEventListener("resize", resize);

    let raf, t0 = 0;
    const loop = (t) => {
      raf = requestAnimationFrame(loop);
      if (!isFlying) {
        ctl.update();
      }
      ren.render(scene, cam);
    };
    requestAnimationFrame((t) => { t0 = t; loop(t); });

    // Clean disposal on route teardown
    stopMap = () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      ctl.dispose();
      meshes.forEach((m) => {
        if (m.geometry) m.geometry.dispose();
        if (m.material) {
          if (Array.isArray(m.material)) m.material.forEach((mat) => mat.dispose());
          else m.material.dispose();
        }
      });
      [texGreen, texYellow, texRed, groundTex].forEach((t) => t && t.dispose());
      ren.dispose();
    };
  }

  /* -------------------------------------------------------------
   * Deed Copy & Fingerprint Verification Screen (F13 / R12)
   * ------------------------------------------------------------- */
  async function verifyDeedScreen(hash) {
    const s = S();
    const params = {};
    const qIdx = hash.indexOf("?");
    if (qIdx !== -1) {
      hash.slice(qIdx + 1).split("&").forEach(pair => {
        const [k, v] = pair.split("=");
        if (k) params[decodeURIComponent(k)] = decodeURIComponent(v || "");
      });
    }

    const initialDeedNo = params.deed_no || "";
    const initialParcelId = params.parcel_id || "";
    const initialDate = params.date || params.registration_date || "";
    const initialSeller = params.seller || "";
    const initialBuyer = params.buyer || "";
    const initialArea = params.area || "";
    const initialHash = params.hash || params.claimed_hash || "";

    const title = t("verify_screen_title");
    const desc = t("verify_screen_desc");
    const notice = t("verify_disclaimer_notice");

    root().innerHTML = `
      <div class="x-wrap verify-deed-container">
        <div class="x-hero">
          <h1>📜 ${esc(title)}</h1>
          <p>${esc(desc)}</p>
          <div class="verify-disclaimer-pill" role="note" style="margin-top: 0.5rem; background: #fef3c7; color: #92400e; padding: 0.5rem 0.85rem; border-radius: 6px; font-size: 0.85rem; border: 1px solid #fde68a;">
            ⚖️ ${esc(notice)}
          </div>
        </div>

        <div class="verify-form-card" style="background: var(--surface-bg, #fff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 8px; padding: 1.5rem; margin-top: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
          <form id="verify-deed-form">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem;">
              <div>
                <label for="vd-deed-no" style="font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 0.25rem;">${t("verify_deed_no_label")}</label>
                <input id="vd-deed-no" name="deed_no" value="${esc(initialDeedNo)}" required style="width: 100%; padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 4px;" placeholder="e.g. 4021" />
              </div>
              <div>
                <label for="vd-reg-date" style="font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 0.25rem;">${t("verify_reg_date_label")}</label>
                <input id="vd-reg-date" name="registration_date" value="${esc(initialDate)}" required style="width: 100%; padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 4px;" placeholder="YYYY-MM-DD" />
              </div>
              <div>
                <label for="vd-parcel-id" style="font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 0.25rem;">${t("verify_parcel_id_label")}</label>
                <input id="vd-parcel-id" name="parcel_id" value="${esc(initialParcelId)}" required style="width: 100%; padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 4px;" placeholder="e.g. PARCEL_STORY_01" />
              </div>
              <div>
                <label for="vd-area" style="font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 0.25rem;">${t("verify_area_label")}</label>
                <input id="vd-area" name="area" value="${esc(initialArea)}" required style="width: 100%; padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 4px;" placeholder="e.g. 10 or 5/2" />
              </div>
              <div>
                <label for="vd-seller" style="font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 0.25rem;">${t("verify_seller_label")}</label>
                <input id="vd-seller" name="seller" value="${esc(initialSeller)}" required style="width: 100%; padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 4px;" placeholder="e.g. Abdul Latif" />
              </div>
              <div>
                <label for="vd-buyer" style="font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 0.25rem;">${t("verify_buyer_label")}</label>
                <input id="vd-buyer" name="buyer" value="${esc(initialBuyer)}" required style="width: 100%; padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 4px;" placeholder="e.g. Abdul Karim" />
              </div>
            </div>

            <div style="margin-top: 1rem;">
              <label for="vd-claimed-hash" style="font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 0.25rem;">${t("verify_claimed_hash_label")}</label>
              <input id="vd-claimed-hash" name="claimed_hash" value="${esc(initialHash)}" style="width: 100%; padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 4px; font-family: monospace; font-size: 0.85rem;" placeholder="64-character hex SHA-256 fingerprint (optional)" />
            </div>

            <div style="margin-top: 1.25rem; display: flex; gap: 0.75rem;">
              <button id="vd-submit-btn" type="submit" class="btn-primary" style="padding: 0.6rem 1.25rem; font-weight: 600; cursor: pointer;">🔍 ${t("verify_btn_submit")}</button>
            </div>
          </form>
        </div>

        <div id="verify-result-container" style="margin-top: 1.5rem;" aria-live="polite"></div>
      </div>
    `;

    const form = document.getElementById("verify-deed-form");
    const resBox = document.getElementById("verify-result-container");

    async function executeVerification() {
      const deed_no = document.getElementById("vd-deed-no").value.trim();
      const registration_date = document.getElementById("vd-reg-date").value.trim();
      const parcel_id = document.getElementById("vd-parcel-id").value.trim();
      const seller = document.getElementById("vd-seller").value.trim();
      const buyer = document.getElementById("vd-buyer").value.trim();
      const area = document.getElementById("vd-area").value.trim();
      const claimed_hash = document.getElementById("vd-claimed-hash").value.trim() || null;

      if (!deed_no || !registration_date || !parcel_id || !seller || !buyer || !area) {
        resBox.innerHTML = `<p style="color: #dc2626;">${t("error_empty_fields")}</p>`;
        return;
      }

      resBox.innerHTML = `<p>${t("verify_loading")}</p>`;

      try {
        const payload = {
          deed_no,
          registration_date,
          parcel_id,
          seller,
          buyer,
          area,
          claimed_hash,
          lang: currentLang,
          role: currentRole || "reviewer"
        };

        const res = await fetch("/verify-deed", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          const errMsg = err.detail || t("verify_error");
          resBox.innerHTML = `<div class="x-verdict red"><h3>⚠️ ${esc(errMsg)}</h3></div>`;
          return;
        }

        const data = await res.json();
        const sc = (data.status_code || "REVIEW").toUpperCase();
        const c = sc === "CONTRADICTION" ? "red" : (sc === "REVIEW" ? "yellow" : "green");
        const icon = sc === "CONTRADICTION" ? "⛔" : (sc === "REVIEW" ? "⚠️" : "✅");

        // Generate client-side QR Code SVG using qrcode.js
        let qrSvgHtml = "";
        if (typeof qrcode !== "undefined" && data.qr_payload) {
          try {
            const qr = qrcode(0, "M");
            qr.addData(data.qr_payload);
            qr.make();
            qrSvgHtml = qr.createSvgTag(3, 2);
          } catch (qrErr) {
            qrSvgHtml = `<p><small>QR generation error: ${esc(qrErr.message)}</small></p>`;
          }
        }

        resBox.innerHTML = `
          <div class="x-verdict ${c}" style="border: 1px solid var(--border-color); border-radius: 8px; padding: 1.5rem; background: var(--surface-bg, #fff);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;">
              <h2 style="margin: 0; font-size: 1.25rem;">${icon} ${esc(data.status)}</h2>
              ${formatStatusBadge(data.status_code)}
            </div>

            <p style="font-size: 1.05rem; font-weight: 500; margin-bottom: 0.75rem;">${esc(data.message)}</p>

            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 1rem; margin-bottom: 1rem; font-family: monospace; font-size: 0.85rem; line-height: 1.6;">
              <div><strong>${t("verify_computed_hash_label")}</strong> <span style="word-break: break-all; color: #0f172a;">${esc(data.computed_hash)}</span></div>
              ${data.recorded_hash ? `<div><strong>${t("verify_recorded_hash_label")}</strong> <span style="word-break: break-all; color: #1e293b;">${esc(data.recorded_hash)}</span></div>` : `<div><em>${currentLang === "bn" ? "রেজিস্ট্রিতে এই দলিলের কোনো ফিঙ্গারপ্রিন্ট সংরক্ষিত নেই" : "No recorded fingerprint on file in registry"}</em></div>`}
              ${data.claimed_hash ? `<div><strong>${t("verify_claimed_hash_label")}</strong> <span style="word-break: break-all; color: #475569;">${esc(data.claimed_hash)}</span></div>` : ""}
            </div>

            <div style="margin-bottom: 1rem;">
              <strong>${t("next_step_label")}</strong> <span>${esc(data.recommended_next_step)}</span>
            </div>

            ${qrSvgHtml ? `
              <div class="qr-result-box" style="margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; display: flex; align-items: center; gap: 1.25rem; flex-wrap: wrap;">
                <div style="background: #fff; padding: 6px; border: 1px solid #cbd5e1; border-radius: 6px; line-height: 0;">
                  ${qrSvgHtml}
                </div>
                <div>
                  <h4 style="margin: 0 0 0.25rem 0; font-size: 0.95rem;">${t("verify_qr_heading")}</h4>
                  <div style="font-size: 0.8rem; color: #64748b; font-family: monospace; word-break: break-all;">${esc(data.qr_payload)}</div>
                  <div style="margin-top: 0.5rem;"><small style="color: #64748b;">${currentLang === "bn" ? "এই কিউআর কোডটি অফলাইনে ক্লায়েন্ট-সাইডে তৈরি করা হয়েছে।" : "This QR code is generated client-side offline without external networks."}</small></div>
                </div>
              </div>
            ` : ""}

            <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid #e2e8f0; font-size: 0.8rem; color: #64748b;">
              ⚖️ ${esc(data.disclaimer)}
            </div>
          </div>
        `;

        const a11y = document.getElementById("a11y-status");
        if (a11y) {
          a11y.textContent = `${data.status}: ${data.message}`;
        }
      } catch (e) {
        resBox.innerHTML = `<div class="x-verdict red"><h3>⚠️ ${esc(e.message || t("verify_error"))}</h3></div>`;
      }
    }

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      executeVerification();
    });

    if (initialDeedNo && initialArea && initialSeller && initialBuyer && initialDate && initialParcelId) {
      executeVerification();
    }
  }

  async function ussdSimulatorScreen() {
    const s = S();
    let sessionId = "sim_" + Math.random().toString(36).substring(2, 9);

    root().innerHTML = `
      <div class="x-wrap ussd-wrapper">
        <div class="x-hero" style="margin-bottom: 1rem;">
          <h1>📱 ${t("ussd_simulator_title")}</h1>
          <p style="font-size: 0.95rem; color: var(--text-muted);">${t("ussd_simulator_desc")}</p>
        </div>

        <div class="ussd-phone-mockup">
          <div class="ussd-speaker"></div>

          <div class="ussd-char-counter">
            <span id="ussd-chars">0</span>/160 ${currentLang === "bn" ? "অক্ষর" : "chars"}
          </div>

          <div class="ussd-screen" id="ussd-screen">
            <pre class="ussd-screen-text" id="ussd-screen-text">${currentLang === "bn" ? "সংযোগ হচ্ছে..." : "Connecting..."}</pre>
          </div>

          <form id="ussd-form" class="ussd-input-group">
            <input type="text" id="ussd-input" class="ussd-input" placeholder="${t("ussd_dial_placeholder")}" autocomplete="off" />
            <div class="ussd-btn-row">
              <button type="submit" id="ussd-send-btn" class="btn-primary">${t("ussd_send_btn")}</button>
              <button type="button" id="ussd-cancel-btn" class="btn-secondary">${t("ussd_cancel_btn")}</button>
              <button type="button" id="ussd-reset-btn" class="btn-secondary">${t("ussd_reset_btn")}</button>
            </div>
          </form>

          <div class="ussd-keypad-grid">
            ${["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"].map(k => `
              <button type="button" class="ussd-key" data-key="${k}">${k}</button>
            `).join("")}
          </div>
        </div>

        <p class="x-note" style="margin-top: 1.5rem;">${s.note}</p>
      </div>
    `;

    const screenText = document.getElementById("ussd-screen-text");
    const charCounter = document.getElementById("ussd-chars");
    const inputEl = document.getElementById("ussd-input");
    const form = document.getElementById("ussd-form");
    const cancelBtn = document.getElementById("ussd-cancel-btn");
    const resetBtn = document.getElementById("ussd-reset-btn");

    async function sendUSSD(text) {
      if (screenText) screenText.textContent = currentLang === "bn" ? "অপেক্ষা করুন..." : "Please wait...";
      try {
        const res = await fetch("/ussd", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: text, session_id: sessionId })
        });
        if (!res.ok) throw new Error("Network response error: " + res.status);
        const data = await res.json();
        const display = data.display_text || "";
        if (screenText) screenText.textContent = display;
        if (charCounter) charCounter.textContent = display.length;
        if (inputEl) {
          inputEl.value = "";
          inputEl.focus();
        }
      } catch (e) {
        if (screenText) screenText.textContent = currentLang === "bn" ? "সংযোগ ত্রুটি। পুনরায় চেষ্টা করুন।" : "Connection error. Please retry.";
      }
    }

    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        const val = inputEl ? inputEl.value.trim() : "";
        sendUSSD(val);
      });
    }

    if (cancelBtn) {
      cancelBtn.addEventListener("click", () => {
        sendUSSD("0");
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        sessionId = "sim_" + Math.random().toString(36).substring(2, 9);
        sendUSSD("*123*45#");
      });
    }

    document.querySelectorAll(".ussd-key").forEach(b => {
      b.addEventListener("click", () => {
        if (inputEl) {
          inputEl.value += b.dataset.key;
          inputEl.focus();
        }
      });
    });

    // Initial trigger
    sendUSSD("*123*45#");
  }
})();
