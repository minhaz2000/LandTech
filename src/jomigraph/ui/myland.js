/* Geography home + "check my land" wizard. Relies on globals from app.js/extras.js (currentLang, currentRole, toBanglaDigits). */
(function () {
  const M = {
    bn: { title: "জমিগ্রাফ এআই", sub: "আপনার এলাকার জমির রেকর্ড মিলিয়ে দেখুন (কাল্পনিক ডেমো ডেটা)", where: "কোন এলাকা দেখবেন?", all: "সারা বাংলাদেশ",
      div: "বিভাগ", dis: "জেলা", upa: "উপজেলা", pick: "সব", red: "লাল", yellow: "হলুদ", green: "সবুজ", redD: "অসঙ্গতি", yellowD: "দেখা দরকার", greenD: "সঙ্গতিপূর্ণ",
      mine: "আমার", total: "টি জমি", empty: "এই এলাকায় এখনো কোনো ডেমো রেকর্ড নেই। নিজের জমির তথ্য দিয়ে যাচাই করুন।", mapT: "মৌজা ম্যাপ (৩ডি)", mapD: "রঙিন প্লট ঘুরিয়ে দেখুন",
      verT: "কেনার আগে যাচাই", verD: "দাগ নম্বর বা নাম লিখে খুঁজুন", myT: "আমার জমি যাচাই", myD: "নিজের জমি ও দলিলের তথ্য দিন, সাথে সাথে ফল", note: "ডেমো, কাল্পনিক তথ্য। আইনি সিদ্ধান্ত বা মালিকানার সনদ নয়।",
      steps: ["এলাকা ও দাগ", "জমির মালিক", "দলিল", "ফল"], next: "পরের ধাপ →", back: "← পেছনে", check: "যাচাই করুন", s1: "জমি কোথায়?", s1d: "এলাকা বেছে দাগের তথ্য লিখুন। না জানলে ফাঁকা রাখুন।",
      mouza: "মৌজার নাম", mouzaH: "খতিয়ান বা দলিলে মৌজার যে নাম আছে", dag: "দাগ নম্বর", dagH: "জমির সিরিয়াল নম্বর, যেমন ১০১", kh: "খতিয়ান নম্বর (ঐচ্ছিক)", sd: "জরিপের তারিখ", sdH: "যে জরিপের খতিয়ান থেকে শুরু করছেন (CS, SA, RS, BS) তার সাল বা তারিখ",
      s2: "জরিপে কার নামে কত শতক?", s2d: "খতিয়ানে যাদের নাম আছে তাদের লিখুন। মোট জমি এখান থেকেই হিসাব হবে।", hn: "মালিকের নাম", ha: "জমি (শতক)", haH: "যেমন ৫ বা ২.৫", addH: "+ আরেকজন মালিক", rm: "মুছুন",
      s3: "এই জমির দলিল (বিক্রি বা দান)", s3d: "দলিল না থাকলে সরাসরি যাচাই করুন। তারিখ অনুযায়ী নিজেই সাজিয়ে নেওয়া হবে।", sel: "বিক্রেতা", buy: "ক্রেতা", da: "কত শতক", dd: "দলিলের তারিখ", dn: "দলিল নম্বর (ঐচ্ছিক)",
      mutT: "নামজারির তথ্য দিন (ঐচ্ছিক)", ma: "নামজারিতে কত শতক", md: "নামজারির তারিখ", addD: "+ আরেকটি দলিল", baseline: "এই জরিপের পর থেকে সব দলিল এখানে দিয়েছি",
      exOk: "সঠিক উদাহরণ", exBad: "সমস্যাযুক্ত উদাহরণ", required: "লাল ঘরগুলো পূরণ করুন", loading: "যাচাই চলছে...", passed: "টি নিয়ম মিলেছে", nextStep: "পরের ধাপ",
      ok: "দেওয়া তথ্যে কোনো অসঙ্গতি পাওয়া যায়নি", rv: "আরও যাচাই দরকার", bad: "দেওয়া তথ্যে অসঙ্গতি পাওয়া গেছে", bal: "দলিল অনুযায়ী কাগজের হিসাব", balD: "শুধু আপনার দেওয়া সংখ্যার যোগ-বিয়োগ। মালিকানার সনদ নয়।",
      save: "এই ব্রাউজারে সংরক্ষণ করুন", saved: "সংরক্ষিত হয়েছে। হোমে এলাকা অনুযায়ী দেখতে পাবেন।", edit: "তথ্য বদলান", fresh: "নতুন যাচাই", home: "হোমে যান", neg: "দলিলের হিসাবে বেশি", unit: "শতক", err: "সার্ভার থেকে উত্তর আসেনি" },
    en: { title: "JomiGraph AI", sub: "Cross-check land records in your area (fictional demo data)", where: "Which area?", all: "All Bangladesh",
      div: "Division", dis: "District", upa: "Upazila", pick: "All", red: "Red", yellow: "Yellow", green: "Green", redD: "Contradiction", yellowD: "Needs review", greenD: "Consistent",
      mine: "Mine", total: " parcels", empty: "No demo records here yet. Check your own land details instead.", mapT: "Mouza map (3D)", mapD: "Rotate the coloured plots",
      verT: "Check before you buy", verD: "Search by dag number or name", myT: "Check my land", myD: "Enter your plot and deeds, get a result right away", note: "Demo, fictional data. Not a legal ruling or proof of ownership.",
      steps: ["Place and dag", "Holders", "Deeds", "Result"], next: "Next →", back: "← Back", check: "Check now", s1: "Where is the land?", s1d: "Pick the area and enter the dag details. Leave blank what you do not know.",
      mouza: "Mouza name", mouzaH: "The mouza name as written on the khatian or deed", dag: "Dag number", dagH: "The plot serial number, e.g. 101", kh: "Khatian number (optional)", sd: "Survey date", sdH: "Date of the survey record you start from (CS, SA, RS, BS)",
      s2: "Who held how much in the survey?", s2d: "List the names on the khatian. The total area is added up from these.", hn: "Holder name", ha: "Area (shatak)", haH: "e.g. 5 or 2.5", addH: "+ Add another holder", rm: "Remove",
      s3: "Deeds for this plot (sale or gift)", s3d: "No deeds? Go straight to the check. They are sorted by date for you.", sel: "Seller", buy: "Buyer", da: "Area (shatak)", dd: "Deed date", dn: "Deed number (optional)",
      mutT: "Add mutation details (optional)", ma: "Mutation area (shatak)", md: "Mutation date", addD: "+ Add another deed", baseline: "I have entered every deed made after this survey",
      exOk: "Good example", exBad: "Problem example", required: "Fill in the red fields", loading: "Checking...", passed: " rules matched", nextStep: "Next step",
      ok: "No contradiction found in the details you gave", rv: "More checking needed", bad: "Contradiction found in the details you gave", bal: "Paper balance from the deeds", balD: "Plain addition and subtraction of your numbers. Not proof of ownership.",
      save: "Save in this browser", saved: "Saved. You will see it on the home screen under its area.", edit: "Edit details", fresh: "New check", home: "Go home", neg: "More than the deeds allow", unit: "shatak", err: "No answer from the server" }
  };
  const m = () => M[currentLang] || M.bn, esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const num = (n) => (currentLang === "bn" ? toBanglaDigits(n) : String(n)), root = () => document.getElementById("app-root");
  const CL = { CONTRADICTION: "red", REVIEW: "yellow", CONSISTENT: "green" };
  const jget = (u) => fetch(u).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); });
  const ls = { get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch (e) { return d; } }, set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} } };
  let tree = null; const getTree = async () => (tree = tree || (await jget("/geo/tree")));
  const geo = () => ls.get("jg_geo", { division: "", district: "", upazila: "" });
  const nm = (o) => (currentLang === "bn" ? o.bn : o.en);
  const mine = () => ls.get("jg_my_lands", []);

  /* ---------- geography selects ---------- */
  function geoSelects(t, g, onChange) {
    const dv = t.divisions.find((d) => d.en === g.division), ds = dv && dv.districts.find((d) => d.en === g.district);
    const sel = (id, label, opts, val) => `<label class="x-field"><span>${label}</span><select id="${id}"><option value="">${m().pick}</option>${opts.map((o) => `<option value="${esc(o.en)}"${o.en === val ? " selected" : ""}>${esc(nm(o))}</option>`).join("")}</select></label>`;
    return `<div class="x-geo">${sel("g-div", m().div, t.divisions, g.division)}${sel("g-dis", m().dis, dv ? dv.districts : [], g.district)}${sel("g-upa", m().upa, ds ? ds.upazilas : [], g.upazila)}</div>`;
  }
  function wireGeo(g, onChange) {
    const set = (k) => (e) => { const n = { ...g, [k]: e.target.value }; if (k === "division") { n.district = ""; n.upazila = ""; } if (k === "district") n.upazila = ""; onChange(n); };
    ["division", "district", "upazila"].forEach((k, i) => document.getElementById(["g-div", "g-dis", "g-upa"][i]).addEventListener("change", set(k)));
  }

  /* ---------- home ---------- */
  window.renderHomeGeo = async function () {
    root().innerHTML = `<div class="x-wrap"><div class="x-skel"></div><div class="x-skel"></div></div>`;
    const t = await getTree(); let g = geo(), cur = "";
    const draw = async () => {
      const q = new URLSearchParams({ lang: currentLang, ...(g.division && { division: g.division }), ...(g.district && { district: g.district }), ...(g.upazila && { upazila: g.upazila }) });
      const r = await jget("/geo/parcels?" + q);
      const mm = mine().filter((x) => (!g.division || x.place.division === g.division) && (!g.district || x.place.district === g.district) && (!g.upazila || x.place.upazila === g.upazila));
      const grp = { red: [], yellow: [], green: [] };
      r.parcels.forEach((p) => grp[CL[p.status_code]].push({ label: p.label, href: "#/parcel/" + encodeURIComponent(p.id) }));
      mm.forEach((x) => grp[CL[x.result.status_code]].push({ label: x.label, href: "#/my-land/saved/" + x.id, mine: true }));
      cur = cur || (grp.red.length ? "red" : grp.yellow.length ? "yellow" : "green");
      const total = grp.red.length + grp.yellow.length + grp.green.length, s = m();
      root().innerHTML = `<div class="x-wrap x-fade"><div class="x-hero"><h1>${s.title}</h1><p>${s.sub}</p></div>
        <div class="x-card"><h2 class="x-h2">📍 ${s.where}</h2>${geoSelects(t, g)}
          <p class="x-note">${g.division ? "" : s.all + " · "}${num(total)}${s.total}</p></div>
        <div class="x-grid">${["red", "yellow", "green"].map((c) => `<button type="button" class="x-stat ${c}${cur === c ? " on" : ""}" data-c="${c}"><b>${num(grp[c].length)}</b><span>${s[c]} · ${s[c + "D"]}</span></button>`).join("")}</div>
        <div class="x-list">${total ? grp[cur].map((i) => `<a class="x-item" href="${i.href}"><span>${esc(i.label)}${i.mine ? ` <em class="x-tag">${s.mine}</em>` : ""}</span><i class="x-dot ${cur}"></i></a>`).join("") : `<p class="x-empty">${s.empty}</p>`}</div>
        <div class="x-actions3"><a class="x-big" href="#/my-land">📝<strong>${s.myT}</strong><small>${s.myD}</small></a><a class="x-big" href="#/map">🗺️<strong>${s.mapT}</strong><small>${s.mapD}</small></a><a class="x-big" href="#/verify">🔍<strong>${s.verT}</strong><small>${s.verD}</small></a></div>
        <p class="x-note">${s.note}</p></div>`;
      wireGeo(g, (n) => { g = n; ls.set("jg_geo", g); cur = ""; draw(); });
      document.querySelectorAll(".x-stat").forEach((b) => b.addEventListener("click", () => { cur = b.dataset.c; draw(); }));
    };
    draw();
  };

  /* ---------- wizard ---------- */
  const blankDeed = () => ({ seller: "", buyer: "", area: "", date: "", deed_no: "", mut: false, mutation_area: "", mutation_date: "" });
  let W = null; const fresh = () => (W = { step: 0, place: { ...geo() }, mouza: "", dag_no: "", khatian_no: "", survey_date: "", holders: [{ name: "", area: "" }], deeds: [], baseline_complete: true, bad: false, err: "", result: null });
  const example = (good) => { Object.assign(W, { mouza: currentLang === "bn" ? "উদাহরণ মৌজা" : "Example Mouza", dag_no: "101", khatian_no: "1001", survey_date: "2000-01-10", holders: [{ name: currentLang === "bn" ? "রহিম" : "Rahim", area: "10" }],
    deeds: [{ ...blankDeed(), seller: currentLang === "bn" ? "রহিম" : "Rahim", buyer: currentLang === "bn" ? "করিম" : "Karim", area: good ? "4" : "15", date: "2012-05-10", deed_no: "D-2012-77" }], bad: false }); };
  const fld = (label, hint, id, val, extra = "", cls = "") => `<label class="x-field ${cls}"><span>${label}</span><input id="${id}" value="${esc(val)}" ${extra}>${hint ? `<small>${hint}</small>` : ""}</label>`;

  async function wizard() {
    if (!W) fresh(); const s = m(), t = await getTree();
    const bar = `<div class="x-steps">${s.steps.map((x, i) => `<div class="x-step${i === W.step ? " on" : i < W.step ? " done" : ""}"><i>${num(i + 1)}</i><span>${x}</span></div>`).join("")}</div>`;
    let body = "", nav = "";
    if (W.step === 0) {
      body = `<h2 class="x-h2">${s.s1}</h2><p class="x-note">${s.s1d}</p>${geoSelects(t, W.place)}
        ${fld(s.mouza, s.mouzaH, "f-mouza", W.mouza, "", W.bad && !W.mouza.trim() ? "bad" : "")}
        <div class="x-two">${fld(s.dag, s.dagH, "f-dag", W.dag_no, 'inputmode="numeric"', W.bad && !W.dag_no.trim() ? "bad" : "")}${fld(s.kh, "", "f-kh", W.khatian_no, 'inputmode="numeric"')}</div>
        ${fld(s.sd, s.sdH, "f-sd", W.survey_date, 'type="date"', W.bad && !W.survey_date ? "bad" : "")}
        <div class="x-chips"><button type="button" class="x-chip" id="ex-ok">✨ ${s.exOk}</button><button type="button" class="x-chip" id="ex-bad">⚠️ ${s.exBad}</button></div>`;
      nav = `<span></span><button class="btn-primary x-btn" id="n-next">${s.next}</button>`;
    } else if (W.step === 1) {
      body = `<h2 class="x-h2">${s.s2}</h2><p class="x-note">${s.s2d}</p>` + W.holders.map((h, i) => `<div class="x-row"><div class="x-two">${fld(s.hn, "", "h-n" + i, h.name, "", W.bad && !h.name.trim() ? "bad" : "")}${fld(s.ha, s.haH, "h-a" + i, h.area, 'inputmode="decimal"', W.bad && !h.area.trim() ? "bad" : "")}</div>${W.holders.length > 1 ? `<button type="button" class="x-link" data-rm-h="${i}">${s.rm}</button>` : ""}</div>`).join("") + `<button type="button" class="x-chip" id="add-h">${s.addH}</button>`;
      nav = `<button class="x-btn x-ghost" id="n-back">${s.back}</button><button class="btn-primary x-btn" id="n-next">${s.next}</button>`;
    } else if (W.step === 2) {
      const names = W.holders.map((h) => h.name.trim()).filter(Boolean);
      body = `<h2 class="x-h2">${s.s3}</h2><p class="x-note">${s.s3d}</p><datalist id="dl">${[...new Set([...names, ...W.deeds.flatMap((d) => [d.seller, d.buyer]).filter(Boolean)])].map((n) => `<option value="${esc(n)}">`).join("")}</datalist>` +
        W.deeds.map((d, i) => `<div class="x-row"><div class="x-two">${fld(s.sel, "", "d-s" + i, d.seller, 'list="dl"', W.bad && !d.seller.trim() ? "bad" : "")}${fld(s.buy, "", "d-b" + i, d.buyer, 'list="dl"', W.bad && !d.buyer.trim() ? "bad" : "")}</div>
          <div class="x-two">${fld(s.da, s.haH, "d-a" + i, d.area, 'inputmode="decimal"', W.bad && !d.area.trim() ? "bad" : "")}${fld(s.dd, "", "d-d" + i, d.date, 'type="date"', W.bad && !d.date ? "bad" : "")}</div>
          ${fld(s.dn, "", "d-n" + i, d.deed_no)}
          <label class="x-check"><input type="checkbox" id="d-m${i}"${d.mut ? " checked" : ""}> ${s.mutT}</label>
          ${d.mut ? `<div class="x-two">${fld(s.ma, "", "d-ma" + i, d.mutation_area, 'inputmode="decimal"')}${fld(s.md, "", "d-md" + i, d.mutation_date, 'type="date"')}</div>` : ""}
          <button type="button" class="x-link" data-rm-d="${i}">${s.rm}</button></div>`).join("") +
        `<button type="button" class="x-chip" id="add-d">${s.addD}</button><label class="x-check"><input type="checkbox" id="f-base"${W.baseline_complete ? " checked" : ""}> ${s.baseline}</label>${W.err ? `<div class="x-err">${esc(W.err)}</div>` : ""}`;
      nav = `<button class="x-btn x-ghost" id="n-back">${s.back}</button><button class="btn-primary x-btn" id="n-go">${s.check}</button>`;
    } else { body = resultHTML(W.result); nav = ""; }
    root().innerHTML = `<div class="x-wrap x-fade"><div class="x-hero"><h1>📝 ${s.myT}</h1><p>${s.myD}</p></div>${bar}<div class="x-card">${body}</div>${nav ? `<div class="x-nav2">${nav}</div>` : ""}<p class="x-note">${s.note}</p></div>`;
    wire();
  }

  function pull() { // copy input values into W
    const v = (id) => document.getElementById(id)?.value ?? "";
    if (W.step === 0) { W.mouza = v("f-mouza"); W.dag_no = v("f-dag"); W.khatian_no = v("f-kh"); W.survey_date = v("f-sd"); }
    if (W.step === 1) W.holders.forEach((h, i) => { h.name = v("h-n" + i); h.area = v("h-a" + i); });
    if (W.step === 2) { W.baseline_complete = document.getElementById("f-base")?.checked ?? true; W.deeds.forEach((d, i) => { d.seller = v("d-s" + i); d.buyer = v("d-b" + i); d.area = v("d-a" + i); d.date = v("d-d" + i); d.deed_no = v("d-n" + i); d.mut = document.getElementById("d-m" + i)?.checked; d.mutation_area = v("d-ma" + i); d.mutation_date = v("d-md" + i); }); }
  }
  const stepOK = () => (W.step === 0 ? W.mouza.trim() && W.dag_no.trim() && W.survey_date : W.step === 1 ? W.holders.every((h) => h.name.trim() && h.area.trim()) : W.deeds.every((d) => d.seller.trim() && d.buyer.trim() && d.area.trim() && d.date));

  function wire() {
    const $ = (id) => document.getElementById(id), re = () => wizard();
    if (W.step === 0) { getTree().then((t) => { const g = W.place; document.getElementById("g-div") && wireGeo(g, (n) => { pull(); W.place = n; ls.set("jg_geo", n); re(); }); }); $("ex-ok").onclick = () => { example(true); re(); }; $("ex-bad").onclick = () => { example(false); re(); }; }
    $("n-next")?.addEventListener("click", () => { pull(); if (!stepOK()) { W.bad = true; return re(); } W.bad = false; W.step++; re(); window.scrollTo({ top: 0, behavior: "smooth" }); });
    $("n-back")?.addEventListener("click", () => { pull(); W.step--; W.bad = false; re(); });
    $("add-h")?.addEventListener("click", () => { pull(); W.holders.push({ name: "", area: "" }); re(); });
    document.querySelectorAll("[data-rm-h]").forEach((b) => b.addEventListener("click", () => { pull(); W.holders.splice(+b.dataset.rmH, 1); re(); }));
    $("add-d")?.addEventListener("click", () => { pull(); W.deeds.push(blankDeed()); re(); });
    document.querySelectorAll("[data-rm-d]").forEach((b) => b.addEventListener("click", () => { pull(); W.deeds.splice(+b.dataset.rmD, 1); re(); }));
    W.deeds.forEach((d, i) => $("d-m" + i)?.addEventListener("change", () => { pull(); re(); }));
    $("n-go")?.addEventListener("click", async () => {
      pull(); if (!stepOK()) { W.bad = true; return re(); } W.bad = false; W.err = "";
      $("n-go").disabled = true; $("n-go").textContent = m().loading;
      const body = { ...W.place, mouza: W.mouza, dag_no: W.dag_no, khatian_no: W.khatian_no || null, survey_date: W.survey_date, holders: W.holders, baseline_complete: W.baseline_complete, lang: currentLang,
        deeds: W.deeds.map((d) => ({ seller: d.seller, buyer: d.buyer, area: d.area, date: d.date, deed_no: d.deed_no || null, mutation_area: d.mut ? d.mutation_area || null : null, mutation_date: d.mut ? d.mutation_date || null : null })) };
      try {
        const r = await fetch("/check-my-land", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }), j = await r.json();
        if (!r.ok) { W.err = typeof j.detail === "string" ? j.detail : (j.detail || []).map((x) => x.msg).join("; "); return re(); }
        W.result = j; W.step = 3; re(); window.scrollTo({ top: 0, behavior: "smooth" });
      } catch (e) { W.err = m().err; re(); }
    });
    $("r-save")?.addEventListener("click", () => {
      const id = "u" + Date.now().toString(36), label = `${W.mouza} ${currentLang === "bn" ? "দাগ" : "Dag"} ${W.dag_no}`;
      const all = mine(); all.unshift({ id, label, place: { ...W.place }, result: W.result, input: { mouza: W.mouza, dag_no: W.dag_no } }); ls.set("jg_my_lands", all.slice(0, 50));
      $("r-save").outerHTML = `<p class="x-ok">${m().saved}</p>`;
    });
    $("r-edit")?.addEventListener("click", () => { W.step = 2; re(); });
    $("r-new")?.addEventListener("click", () => { fresh(); re(); });
  }

  function resultHTML(r) {
    const s = m(), c = CL[r.status_code], head = { green: s.ok, yellow: s.rv, red: s.bad }[c], icon = { green: "✅", yellow: "⚠️", red: "⛔" }[c], steps = [...new Set(r.alerts.map((a) => a.recommended_next_step))];
    return `<div class="x-verdict ${c}"><h2>${icon} ${head}</h2><p>${num(r.checks_passed)}/${num(r.checks_total)}${s.passed}</p>${r.alerts.map((a) => `<p>• ${esc(a.message)}</p>`).join("")}${steps.length ? `<p><strong>${s.nextStep}:</strong> ${steps.map(esc).join("; ")}</p>` : ""}</div>
      <h3 class="x-h2">${s.bal}</h3><p class="x-note">${s.balD}</p><div class="x-bal">${r.paper_balance.map((b) => `<div class="${b.negative ? "neg" : ""}"><span>${esc(b.name)}</span><b>${num(b.area)} ${s.unit}</b>${b.negative ? `<small>${s.neg}</small>` : ""}</div>`).join("")}</div>
      <p class="x-note">${esc(r.disclaimer)}</p><div class="x-nav2 wrap">${W && W.result === r ? `<button class="btn-primary x-btn" id="r-save">💾 ${s.save}</button><button class="x-btn x-ghost" id="r-edit">${s.edit}</button><button class="x-btn x-ghost" id="r-new">${s.fresh}</button>` : ""}<a class="x-btn x-ghost" href="#/">${s.home}</a></div>`;
  }

  window.myLandRoute = function (hash) {
    if (hash === "#/my-land") { if (!W || W.step === 3 && !W.result) fresh(); wizard(); return true; }
    if (hash.startsWith("#/my-land/saved/")) {
      const x = mine().find((i) => i.id === hash.split("/").pop()), s = m();
      root().innerHTML = x ? `<div class="x-wrap x-fade"><div class="x-hero"><h1>📝 ${esc(x.label)}</h1><p>${s.myT}</p></div><div class="x-card">${resultHTML(x.result)}</div></div>` : `<div class="x-wrap"><p class="x-empty">404</p></div>`;
      return true;
    }
    return false;
  };
})();
