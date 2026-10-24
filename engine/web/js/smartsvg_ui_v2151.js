/** SmartSVG V21.5.1 audited UI: embedded result dashboard for ComfyUI nodes.
 * No arbitrary filesystem access, no HTML injection, no automatic cut approval.
 * Older ComfyUI UIs without addDOMWidget simply show the existing Python text result.
 */
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { normalizePayload, normalizePreviews, previewUrl } from "./smartsvg_ui_model_v2151.mjs";

const EXT_NAME = "smartsvg.studio.v2151.dashboard";
const NODE_IDS = new Set(["SmartSVGExpressV2151", "SmartSVGExpressV21152"]);

function addStyles() {
  if (document.getElementById("smartsvg-v2151-style")) return;
  const style = document.createElement("style");
  style.id = "smartsvg-v2151-style";
  style.textContent = `
  .smartsvg2151 {font:12px/1.45 system-ui,sans-serif;background:#191b22;color:#f0f1f4;min-width:290px;
    border:1px solid #373d4b;border-radius:12px;padding:11px;box-sizing:border-box;overflow:auto}
  .smartsvg2151 * {box-sizing:border-box}
  .smartsvg2151 .header {font-weight:700;font-size:14px;margin-bottom:7px;display:flex;justify-content:space-between;gap:8px}
  .smartsvg2151 .small {font-size:11px;color:#b9c1d1}
  .smartsvg2151 .pipeline {display:flex;flex-wrap:wrap;gap:4px;margin:6px 0 10px}
  .smartsvg2151 .phase {border-radius:6px;background:#313544;padding:4px 6px;font-size:10px}
  .smartsvg2151 .phase.pending {background:#403527;color:#ffe2aa}
  .smartsvg2151 .numbers {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin-bottom:10px}
  .smartsvg2151 .count {background:#262b35;border-radius:8px;padding:7px 4px;text-align:center}
  .smartsvg2151 .count strong {display:block;font-size:18px}
  .smartsvg2151 .toolbar {display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
  .smartsvg2151 button {background:#343a49;color:#fff;border:1px solid #535d73;border-radius:6px;
    padding:5px 8px;cursor:pointer;font-size:11px}
  .smartsvg2151 button:focus-visible {outline:2px solid #b4c8fe;outline-offset:2px}
  .smartsvg2151 button.active {background:#315782;border-color:#7badff}
  .smartsvg2151 .preview {width:100%;max-height:170px;object-fit:contain;background:#fff;border-radius:6px}
  .smartsvg2151 .cards {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:5px;max-height:135px;overflow:auto}
  .smartsvg2151 .card {background:#262b35;border-radius:6px;padding:6px;font-size:11px;min-width:0}
  .smartsvg2151 .card.warn {border-left:3px solid #e7a954}
  .smartsvg2151 .card.danger {border-left:3px solid #e07870}
  .smartsvg2151 .foot {margin-top:8px;font-size:11px;color:#f9dca4}
  `;
  document.head.appendChild(style);
}
function elem(tag, className, text) {
  const e = document.createElement(tag);
  if (className) e.className = className;
  if (text != null) e.textContent = String(text);
  return e;
}
function button(text, click) {
  const b = elem("button", "", text);
  b.type = "button";
  b.addEventListener("click", click);
  return b;
}
function dashboard(node) {
  addStyles();
  const root = elem("div", "smartsvg2151");
  root.setAttribute("role", "region");
  root.setAttribute("aria-label", "Tableau de bord SmartSVG, résultats et vérifications");
  const header = elem("div", "header", "SmartSVG · Atelier Cricut");
  const help = elem("span", "small", "V21.15.2");
  header.appendChild(help);
  const stage = elem("div", "pipeline");
  for (const [text, pending] of [["1 Importer",false],["2 Analyser",false],["3 Exporter",false],["4 Vérifier",true]]) {
    stage.appendChild(elem("span", pending ? "phase pending" : "phase", text));
  }
  const subtitle = elem("div", "small", "Lancer le workflow pour consulter les objets et les aperçus.");
  const numbers = elem("div", "numbers");
  const counts = {};
  for (const [key,label] of [["objets_total","Objets"],["planches_total","Planches"],["alertes_total","Alertes"]]) {
    const block = elem("div", "count");
    counts[key] = elem("strong", "", "—");
    block.append(counts[key],elem("span","small",label));
    numbers.appendChild(block);
  }
  const toolbar = elem("div", "toolbar");
  const preview = elem("img", "preview");
  preview.alt = "Fiche de contrôle SmartSVG provenant du traitement local";
  preview.hidden = true;
  const cards = elem("div", "cards");
  const footer = elem("div", "foot", "Découpe non certifiée : contrôler la taille dans Cricut Design Space.");
  root.append(header,stage,subtitle,numbers,toolbar,preview,cards,footer);

  function update(output) {
    const report = normalizePayload(output);
    if (!report) {
      // Failures or new execution without a report must not leave a previous
      // successful result on screen with a stale "looks safe" indicator.
      subtitle.textContent = "Aucun resultat verifiable pour cette execution.";
      for (const key of Object.keys(counts)) counts[key].textContent = "—";
      cards.replaceChildren();toolbar.replaceChildren();
      preview.hidden = true;preview.removeAttribute("src");
      footer.textContent = "Resultat non valide. Relancer le workflow avant toute decoupe.";
      node.setDirtyCanvas?.(true,true);
      return;
    }
    subtitle.textContent = (report.etat_prevol === "BLOCKED" ? "⛔ COUPE BLOQUÉE — " : "⚠️ NON CERTIFIÉ — ") + (report.provenance || "Rapport SmartSVG reçu");
    for (const key of Object.keys(counts)) counts[key].textContent = String(report[key]);
    cards.replaceChildren();
    for (const item of report.objets) {
      const card = elem("div",item.etat === "RISQUE_ELEVE" ? "card danger" : "card warn");
      card.append(elem("strong", "", `Objet ${item.numero} · ${item.largeur_mm ?? "?"} mm`),
                  elem("div", "small", `${item.nombre_alertes} alerte(s) · ${item.etat}`));
      if (item.alertes.length) card.appendChild(elem("div", "small", item.alertes.join(" ; ")));
      cards.appendChild(card);
    }
    toolbar.replaceChildren();
    const images = normalizePreviews(output);
    const show = index => {
      const url = previewUrl(images[index], window.location.href, api.apiURL('/view'));
      if (!url) return;
      preview.src = url;
      preview.hidden = false;
      preview.onload = () => { preview.alt = "Apercu charge depuis les exports SmartSVG"; };
      preview.onerror = () => { preview.hidden = true;preview.alt = "Apercu indisponible"; };
      for (let i=0;i<toolbar.children.length;i++) {
        if (toolbar.children[i].dataset.previewIndex) {
          toolbar.children[i].classList.toggle("active", Number(toolbar.children[i].dataset.previewIndex)===index+1);
        }
      }
    };
    images.forEach((ref,index) => {
      const b=button(index===0 ? "Aperçu global" : `Objet ${index}`,()=>show(index));
      b.dataset.previewIndex=String(index+1);
      toolbar.appendChild(b);
    });
    if (report.chemin_sortie) {
      toolbar.appendChild(button("Copier dossier",() => {
        // User gesture only. Never attempt to open local file paths from the browser.
        if (navigator.clipboard?.writeText) {
          void navigator.clipboard.writeText(report.chemin_sortie).catch(() => {
            footer.textContent = "Copie refusee par le navigateur; consulter le rapport texte.";
          });
        } else footer.textContent = "Copie non disponible dans ce navigateur.";
      }));
    }
    if (images.length) show(0);
    else { preview.hidden = true; preview.removeAttribute("src"); }
    footer.textContent = report.action_requise || "Validation manuelle dans Cricut Design Space nécessaire.";
    node.setDirtyCanvas?.(true,true);
  }
  return {root,update};
}

app.registerExtension({
  name: EXT_NAME,
  nodeCreated(node) {
    if (!NODE_IDS.has(node?.comfyClass || node?.type)) return;
    if (node._smartsvgV2151Dashboard) return;
    if (typeof node.addDOMWidget !== "function") return; // graceful old frontend fallback
    try {
      const ui=dashboard(node);
      const widget=node.addDOMWidget("smartsvg_ui_v2151","smartsvg_dashboard",ui.root,{
        serialize:false, hideOnZoom:true, getMinHeight:()=>330,getMaxHeight:()=>470,
      });
      if (widget) {
        // Both fields are necessary to avoid altering saved widgets_values & API prompts.
        widget.serialize=false;
        widget.options={...(widget.options || {}),serialize:false};
      }
      node._smartsvgV2151Dashboard=ui;
      node.size=[Math.max(node.size?.[0] || 400,400),Math.max(node.size?.[1] || 400,530)];
      const original=node.onExecuted;
      node.onExecuted=function (output) {
        original?.apply(this,arguments);
        try { ui.update(output); } catch (e) { console.warn("SmartSVG panel unable to render",e); }
      };
    } catch (e) { console.warn("SmartSVG UI disabled; Python node remains operational",e); }
  },
});
