// Stability-only browser qualification for the *demo* Atelier, not ComfyUI or Cricut.
// Synthetic content only. Requires Playwright Chromium installed in CI.
// Capture deterministic evidence, never user files or private projects.
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const BASE = process.env.SMARTSVG_TEST_URL ||
  "http://127.0.0.1:8765/smartsvg_express_atelier_preview.html";
const OUT = path.resolve(process.env.SMARTSVG_EVIDENCE_DIR || "stability-artifacts");
const SIZES = [
  [360, 740], [390, 844], [768, 1024], [1366, 768], [1920, 1080],
];
const issues = [];
const errors = [];

function intersect(a, b) {
  return Math.min(a.right, b.right) - Math.max(a.left, b.left) > 1 &&
    Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 1;
}

async function inspect(page, width, height) {
  const info = await page.evaluate(() => {
    const rect = selector => {
      const el = document.querySelector(selector);
      if (!el) return null;
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      return {
        left:r.left, right:r.right, top:r.top, bottom:r.bottom,
        width:r.width, height:r.height, visible:cs.display!=="none" &&
        cs.visibility!=="hidden" && r.width>0 && r.height>0
      };
    };
    return {
      screen: {width:window.innerWidth, height:window.innerHeight},
      bodyScrollWidth:document.body.scrollWidth,
      docScrollWidth:document.documentElement.scrollWidth,
      elements: Object.fromEntries([
        ".topbar",".hero",".workflow",".surface",".inspect",".footer-actions",
        ".real-review",".subjects-live","#navigation","#steps"
      ].map(k=>[k,rect(k)])),
      buttons: [...document.querySelectorAll("button[data-step]")]
        .map(x=>({label:x.getAttribute("aria-label"),visible:x.getBoundingClientRect().width>0}))
    };
  });
  const label = width+"x"+height;
  fs.writeFileSync(path.join(OUT, label+".json"), JSON.stringify(info,null,2));
  await page.screenshot({path:path.join(OUT,label+".png"),fullPage:true});
  if (info.docScrollWidth > info.screen.width+1) {
    issues.push(label+": débordement horizontal document "+
      info.docScrollWidth+" > "+info.screen.width);
  }
  for (const [a,b] of [
    [".workflow",".surface"],
    [".surface",".inspect"],
    [".topbar",".hero"],
  ]) {
    const r=info.elements[a],s=info.elements[b];
    if(r?.visible && s?.visible && intersect(r,s)) {
      issues.push(label+": chevauchement "+a+" ↔ "+b);
    }
  }
  if(info.buttons.length!==6)issues.push(label+": navigation étapes non complète");
}

async function main() {
  fs.mkdirSync(OUT,{recursive:true});
  const browser=await chromium.launch({headless:true});
  try{
    for(const [width,height] of SIZES){
      const page=await browser.newPage({
        viewport:{width,height},deviceScaleFactor:1,
        reducedMotion:"reduce",locale:"fr-FR"
      });
      page.on("pageerror", e=>errors.push(width+"x"+height+": "+String(e.message)));
      // Prevent outgoing requests; the standalone demo may only load its local assets.
      await page.route("**/*", route=>{
        const url=new URL(route.request().url());
        return url.hostname==="127.0.0.1"
          ? route.continue() : route.abort("blockedbyclient");
      });
      const response=await page.goto(BASE,{waitUntil:"domcontentloaded",timeout:25000});
      assert.equal(response.status(),200,"La page Atelier doit être servie localement");
      await page.locator("#steps button[data-step]").first().waitFor();
      await inspect(page,width,height);
      // Every required step should remain reachable by a real pointer event.
      for(const view of ["source","clean","subjects","retouch","cut","export"]){
        await page.locator('#steps button[data-step="'+view+'"]').click({timeout:10000});
        const selected=await page.locator('#steps button[data-step="'+view+'"]')
          .getAttribute("aria-current");
        if(selected!=="step")issues.push(width+"x"+height+": étape "+view+" non active");
      }
      await page.close();
    }
  }finally{await browser.close()}
  fs.writeFileSync(path.join(OUT,"summary.json"),
    JSON.stringify({issues,errors,viewport_count:SIZES.length,
      scope:"DOM + Chromium demo only; no ComfyUI/Windows/Cricut"},null,2));
  for(const line of [...issues,...errors])console.error("STABILITY: "+line);
  assert.equal(issues.length,0,"Le test a détecté un chevauchement ou un débordement");
  assert.equal(errors.length,0,"Le navigateur a remonté une erreur JS");
  console.log("Browser demo stability: 5 viewports PASS (not Windows/ComfyUI)");
}
main().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
