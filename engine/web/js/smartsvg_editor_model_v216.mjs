/** V21.6 schema and /view URL validation, intentionally browser-framework-free. */
export const LIMITS = Object.freeze({strokes:400, points:1500, total:12000, bytes:350000});
const filename = /^ed_[a-f0-9]{24}_(?:image|mask\d{2})\.png$/;
const SHA = /^[a-f0-9]{64}$/;
const between = (n,lo,hi) => typeof n === 'number' && Number.isFinite(n) && n >= lo && n <= hi;
function reference(item) {
  return item && item.type === 'output' && item.subfolder === 'SmartSVG_Studio_Editor' &&
    typeof item.filename === 'string' && filename.test(item.filename) ? item : null;
}
export function normalizeMeta(out) {
  const m = Array.isArray(out?.smartsvg_editor) ? out.smartsvg_editor[0] : null;
  if (!m || m.version !== 1 || !Number.isSafeInteger(m.width) || !Number.isSafeInteger(m.height) ||
      !Number.isSafeInteger(m.count) || m.width < 1 || m.height < 1 || m.width * m.height > 5000000 ||
      m.count < 1 || m.count > 32 || !SHA.test(m.source || '') || !reference(m.image) ||
      !Array.isArray(m.masks) || m.masks.length !== m.count || !m.masks.every(reference) ||
      !Number.isSafeInteger(m.preview_width) || !Number.isSafeInteger(m.preview_height) ||
      m.preview_width < 1 || m.preview_height < 1 || m.preview_width > 760 || m.preview_height > 760) return null;
  // Ensure a single output publication session, not a mixed set of references.
  const id = m.image.filename.match(/^ed_([a-f0-9]{24})_/)[1];
  if (m.image.filename !== `ed_${id}_image.png` ||
      !m.masks.every((r, i) => r.filename === `ed_${id}_mask${String(i).padStart(2,'0')}.png`)) return null;
  return m;
}
export function previewUrl(ref, base, apiRoute) {
  if (!reference(ref) || typeof apiRoute !== 'string' || !apiRoute) return null;
  const url = new URL(apiRoute, base);
  url.searchParams.set('filename',ref.filename);
  url.searchParams.set('subfolder','SmartSVG_Studio_Editor');
  url.searchParams.set('type','output');
  return url.toString();
}
export function encodeDocument(meta, strokes) {
  if (!normalizeMeta({smartsvg_editor:[meta]})) throw new Error('Référence de retouche invalide');
  if (!Array.isArray(strokes) || strokes.length > LIMITS.strokes) throw new Error('Maximum 400 traits');
  let count=0;
  const valid = strokes.map(s => {
    if (!s || !Number.isSafeInteger(s.object) || s.object < 0 || s.object >= meta.count ||
        !['add','erase'].includes(s.mode) || !between(s.radius,0.0005,0.2) ||
        !Array.isArray(s.points) || !s.points.length || s.points.length > LIMITS.points) throw new Error('Trait invalide');
    count += s.points.length;
    if (count > LIMITS.total) throw new Error('Maximum 12000 points');
    const points=s.points.map(p => {
      if (!Array.isArray(p) || p.length !== 2 || !between(p[0],0,1) || !between(p[1],0,1)) throw new Error('Point invalide');
      return [Math.round(p[0]*1e5)/1e5,Math.round(p[1]*1e5)/1e5];
    });
    return {object:s.object,mode:s.mode,radius:s.radius,points};
  });
  const text=JSON.stringify({version:1,width:meta.width,height:meta.height,count:meta.count,source:meta.source,strokes:valid});
  if (new TextEncoder().encode(text).length > LIMITS.bytes) throw new Error('Retouches trop volumineuses');
  return text;
}
export function decodeDocument(meta, text) {
  if (!text?.trim()) return [];
  if (typeof text !== 'string' || new TextEncoder().encode(text).length > LIMITS.bytes) throw new Error('Retouches trop volumineuses');
  let doc;
  try {doc=JSON.parse(text);} catch {throw new Error('JSON de retouches invalide');}
  if (!doc || doc.version!==1 || doc.width!==meta.width || doc.height!==meta.height ||
      doc.count!==meta.count || doc.source!==meta.source) throw new Error('La source a changé : retouches incompatibles');
  // Canonical encoder validates each stroke, coordinate and total length.
  encodeDocument(meta,doc.strokes);
  return doc.strokes;
}

/** V21.6.1: model of the image viewport in CSS pixels, independent of Comfy's graph zoom. */
export const VIEW_LIMITS = Object.freeze({minScale:0.125,maxScale:16,maxPreviewDimension:760});
const finitePositive = n => typeof n === 'number' && Number.isFinite(n) && n > 0;
export function constrainView(view, imageWidth, imageHeight, frameWidth, frameHeight) {
  if (![imageWidth,imageHeight,frameWidth,frameHeight].every(finitePositive) ||
      !view || !Number.isFinite(view.scale) || !Number.isFinite(view.x) || !Number.isFinite(view.y))
    throw new Error('Géométrie de zoom invalide');
  const scale = Math.max(VIEW_LIMITS.minScale,Math.min(VIEW_LIMITS.maxScale,view.scale));
  const w=imageWidth*scale,h=imageHeight*scale;
  const clampAxis=(position,extent,frame)=> extent<=frame ? (frame-extent)/2 : Math.min(0,Math.max(frame-extent,position));
  return {scale,x:clampAxis(view.x,w,frameWidth),y:clampAxis(view.y,h,frameHeight)};
}
export function fitView(imageWidth,imageHeight,frameWidth,frameHeight){
  if (![imageWidth,imageHeight,frameWidth,frameHeight].every(finitePositive))
    throw new Error('Géométrie de zoom invalide');
  const scale=Math.min(frameWidth/imageWidth,frameHeight/imageHeight,1.5);
  return constrainView({scale,x:(frameWidth-imageWidth*scale)/2,y:(frameHeight-imageHeight*scale)/2},
    imageWidth,imageHeight,frameWidth,frameHeight);
}
export function zoomView(view,nextScale,anchorX,anchorY,imageWidth,imageHeight,frameWidth,frameHeight){
  if (![nextScale,anchorX,anchorY].every(Number.isFinite))throw new Error('Zoom invalide');
  const scale=Math.max(VIEW_LIMITS.minScale,Math.min(VIEW_LIMITS.maxScale,nextScale));
  const factor=scale/view.scale;
  return constrainView({scale,x:anchorX-(anchorX-view.x)*factor,y:anchorY-(anchorY-view.y)*factor},
    imageWidth,imageHeight,frameWidth,frameHeight);
}
export function moveView(view,deltaX,deltaY,imageWidth,imageHeight,frameWidth,frameHeight){
  if (![deltaX,deltaY].every(Number.isFinite))throw new Error('Déplacement invalide');
  return constrainView({...view,x:view.x+deltaX,y:view.y+deltaY},
    imageWidth,imageHeight,frameWidth,frameHeight);
}
export function viewToUV(view,screenX,screenY,imageWidth,imageHeight,clamp=false){
  if (![screenX,screenY,imageWidth,imageHeight].every(Number.isFinite) || !finitePositive(imageWidth) || !finitePositive(imageHeight))return null;
  const u=(screenX-view.x)/(imageWidth*view.scale),v=(screenY-view.y)/(imageHeight*view.scale);
  if(!clamp && (u<0 || u>1 || v<0 || v>1))return null;
  return [Math.round(Math.max(0,Math.min(1,u))*1e5)/1e5,Math.round(Math.max(0,Math.min(1,v))*1e5)/1e5];
}

/** Sample fine pen motion in screen pixels when magnified, with a small lower bound. */
export function strokeSpacing(scale){
  if(!finitePositive(scale))throw new Error('Grossissement invalide');
  return Math.max(0.04, Math.min(1.2, 1.5/scale));
}
