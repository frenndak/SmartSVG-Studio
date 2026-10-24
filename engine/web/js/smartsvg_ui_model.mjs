/** Presentation only: no filesystem paths or content are trusted HTML. */
export function normalizePayload(output) {
  const raw = Array.isArray(output?.smartsvg) ? output.smartsvg[0] : null;
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
  const items = Array.isArray(raw.objets) ? raw.objets : [];
  return {
    objets_total: finiteCount(raw.objets_total),
    planches_total: finiteCount(raw.planches_total),
    alertes_total: finiteCount(raw.alertes_total),
    provenance: safeText(raw.provenance, 160),
    chemin_sortie: safeText(raw.chemin_sortie, 420),
    objets: items.slice(0, 32).filter(x => x && typeof x === "object").map((item, i) => ({
      numero: finiteCount(item.numero) || i + 1,
      etat: item.etat === "RISQUE_ELEVE" ? "RISQUE_ELEVE" : "A_VERIFIER",
      largeur_mm: Number.isFinite(item.largeur_mm) && item.largeur_mm > 0 ? item.largeur_mm : null,
      nombre_alertes: finiteCount(item.nombre_alertes),
      alertes: Array.isArray(item.alertes) ? item.alertes.slice(0, 6).map(v => safeText(v, 120)) : [],
    })),
    action_requise: safeText(raw.action_requise, 220),
  };
}
function safeText(value, max) { return typeof value === "string" ? value.slice(0, max) : ""; }
function finiteCount(value) { return Number.isSafeInteger(value) && value >= 0 ? Math.min(value, 100000) : 0; }

// Only browser-served ComfyUI output references are eligible for image previews.
export function normalizePreviews(output) {
  const entries = Array.isArray(output?.smartsvg_previews) ? output.smartsvg_previews : [];
  return entries.slice(0, 7).filter(it => it && it.type === "output" &&
    it.subfolder === "SmartSVG_Studio_Previews" &&
    typeof it.filename === "string" && /^qa_[a-z0-9_]{2,35}\.png$/.test(it.filename));
}
export function previewUrl(reference, base) {
  if (!normalizePreviews({smartsvg_previews:[reference]}).length) return null;
  const url = new URL("/view", base);
  url.searchParams.set("filename", reference.filename);
  url.searchParams.set("subfolder", reference.subfolder);
  url.searchParams.set("type", "output");
  return url.toString();
}
