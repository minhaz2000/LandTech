// test_badges.js - UI unit test for formatStatusBadge in both Bangla and English
const fs = require("fs");
const path = require("path");
const assert = require("assert");

// Read app.js and extract ui_strings and formatStatusBadge
const appJsPath = path.resolve(__dirname, "../src/jomigraph/ui/app.js");
const appJsCode = fs.readFileSync(appJsPath, "utf-8");

// Extract ui_strings
const matchStrings = appJsCode.match(/const\s+ui_strings\s*=\s*(\{[\s\S]*?\n\});/);
if (!matchStrings) {
  throw new Error("Could not find ui_strings in app.js");
}
const ui_strings = JSON.parse(matchStrings[1]);

// Extract formatStatusBadge function definition
const matchFunc = appJsCode.match(/function\s+formatStatusBadge\s*\([\s\S]*?\n\}/);
if (!matchFunc) {
  throw new Error("Could not find formatStatusBadge in app.js");
}

let currentLang = "bn";
function t(key) {
  return (ui_strings[currentLang] && ui_strings[currentLang][key]) || key;
}

// Evaluate formatStatusBadge in this scope
const formatStatusBadge = new Function("currentLang", "t", `
  ${matchFunc[0]}
  return formatStatusBadge;
`)(currentLang, t);

console.log("Running badge tests in Bangla (bn)...");
currentLang = "bn";
const badgeBnFunc = (code) => {
  // redefine with current currentLang
  return new Function("t", `${matchFunc[0]}; return formatStatusBadge("${code}");`)(t);
};

// 1. CONTRADICTION in bn
const bnContra = badgeBnFunc("CONTRADICTION");
assert(bnContra.includes("badge-contradiction"), `Expected badge-contradiction, got: ${bnContra}`);
assert(bnContra.includes("অসঙ্গতি"), `Expected Bengali contradiction text, got: ${bnContra}`);
assert(!bnContra.includes("badge-consistent"), "CONTRADICTION must never render badge-consistent");

// 2. REVIEW in bn
const bnReview = badgeBnFunc("REVIEW");
assert(bnReview.includes("badge-review"), `Expected badge-review, got: ${bnReview}`);
assert(bnReview.includes("পর্যালোচনা"), `Expected Bengali review text, got: ${bnReview}`);
assert(!bnReview.includes("badge-consistent"), "REVIEW must never render badge-consistent");

// 3. CONSISTENT in bn
const bnConsistent = badgeBnFunc("CONSISTENT");
assert(bnConsistent.includes("badge-consistent"), `Expected badge-consistent, got: ${bnConsistent}`);
assert(bnConsistent.includes("সঙ্গতিপূর্ণ"), `Expected Bengali consistent text, got: ${bnConsistent}`);

// 4. UNKNOWN / Missing in bn
const bnUnknowns = [badgeBnFunc("UNKNOWN"), badgeBnFunc(""), badgeBnFunc("FOOBAR"), badgeBnFunc("undefined")];
for (const html of bnUnknowns) {
  assert(html.includes("badge-unknown"), `Expected badge-unknown, got: ${html}`);
  assert(html.includes("অজানা"), `Expected Bengali unknown text, got: ${html}`);
  assert(!html.includes("badge-consistent"), "Unknown or invalid status code must NEVER render badge-consistent");
  assert(!html.includes("badge-contradiction"), "Unknown status code must not render badge-contradiction");
}

console.log("Running badge tests in English (en)...");
currentLang = "en";

// 1. CONTRADICTION in en
const enContra = badgeBnFunc("CONTRADICTION");
assert(enContra.includes("badge-contradiction"), `Expected badge-contradiction, got: ${enContra}`);
assert(enContra.includes("Contradiction"), `Expected English contradiction text, got: ${enContra}`);
assert(!enContra.includes("badge-consistent"), "CONTRADICTION must never render badge-consistent");

// 2. REVIEW in en
const enReview = badgeBnFunc("REVIEW");
assert(enReview.includes("badge-review"), `Expected badge-review, got: ${enReview}`);
assert(enReview.includes("Needs review"), `Expected English review text, got: ${enReview}`);
assert(!enReview.includes("badge-consistent"), "REVIEW must never render badge-consistent");

// 3. CONSISTENT in en
const enConsistent = badgeBnFunc("CONSISTENT");
assert(enConsistent.includes("badge-consistent"), `Expected badge-consistent, got: ${enConsistent}`);
assert(enConsistent.includes("Consistent"), `Expected English consistent text, got: ${enConsistent}`);

// 4. UNKNOWN / Missing in en
const enUnknowns = [badgeBnFunc("UNKNOWN"), badgeBnFunc(""), badgeBnFunc("INVALID_CODE"), badgeBnFunc("null")];
for (const html of enUnknowns) {
  assert(html.includes("badge-unknown"), `Expected badge-unknown, got: ${html}`);
  assert(html.includes("Unknown"), `Expected English unknown text, got: ${html}`);
  assert(!html.includes("badge-consistent"), "Unknown or invalid status code must NEVER render badge-consistent");
}

console.log("ALL BADGE FORMATTING TESTS PASSED (8/8 cases verified in bn and en)!");
