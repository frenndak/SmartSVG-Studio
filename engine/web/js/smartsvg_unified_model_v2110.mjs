/** V21.10 bounded, portable brush JSON; no filesystem or ComfyUI dependencies. */
import {validateMeta as validateNative, nativeUrl, fitView, clampView, nativeZoom, sourceAt, centerOn} from './smartsvg_native_model_v219.mjs';
export {nativeUrl,fitView,clampView,nativeZoom,sourceAt,centerOn};
export const LIMITS=Object.freeze({strokes:400,points:1500,total:12000,bytes:350000});
const sha=/^[0-9a-f]{64}$/;
const finite=(n,a,b)=>typeof n==='number'&&Number.isFinite(n)&&n>=a&&n<=b;
const lengthBytes=text=>new TextEncoder().encode(text).length;
export function validateUnified(output){
  const m=Array.isArray(output?.smartsvg_unified)?output.smartsvg_unified[0]:null;
  if(!m||m.version!==1||!sha.test(m.source||'')||typeof m.quality!=='string'||m.quality.length>32)return null;
  return validateNative({smartsvg_native:[m]})?m:null;
}
export function validateStrokes(m,raw){
  if(!m||!sha.test(m.source||'')||!Number.isSafeInteger(m.count)||m.count<1||m.count>32||
     !Array.isArray(raw)||raw.length>LIMITS.strokes)throw Error('Retouches invalides / maximum 400 traits');
  let seen=0;
  return raw.map(s=>{
    if(!s||!Number.isSafeInteger(s.object)||s.object<0||s.object>=m.count||
       !['add','erase'].includes(s.mode)||!finite(s.radius,.0005,.2)||
       !Array.isArray(s.points)||!s.points.length||s.points.length>LIMITS.points)
      throw Error('Trait ou masque hors limites');
    seen+=s.points.length;if(seen>LIMITS.total)throw Error('Maximum 12 000 points');
    return {object:s.object,mode:s.mode,radius:s.radius,points:s.points.map(p=>{
      if(!Array.isArray(p)||p.length!==2||!finite(p[0],0,1)||!finite(p[1],0,1))throw Error('Coordonnées de pinceau invalides');
      return [Math.round(p[0]*1e5)/1e5,Math.round(p[1]*1e5)/1e5];
    })};
  });
}
export function serialize(m,strokes){
  if(!validateUnified({smartsvg_unified:[m]}))throw Error('Session d’édition expirée');
  const text=JSON.stringify({version:1,width:m.width,height:m.height,count:m.count,
    source:m.source,strokes:validateStrokes(m,strokes)});
  if(lengthBytes(text)>LIMITS.bytes)throw Error('Retouches > 350 Ko');
  return text;
}
export function deserialize(m,text){
  if(!text?.trim())return [];
  if(typeof text!=='string'||lengthBytes(text)>LIMITS.bytes)throw Error('Retouches trop volumineuses');
  let doc;try{doc=JSON.parse(text);}catch{throw Error('JSON de retouches invalide');}
  if(!doc||Object.keys(doc).sort().join('|')!==['count','height','source','strokes','version','width'].join('|')||
     doc.version!==1||doc.width!==m.width||doc.height!==m.height||doc.count!==m.count||doc.source!==m.source)
    throw Error('Image ou segmentation différente : retouches incompatibles');
  return validateStrokes(m,doc.strokes);
}
export function positionUV(view,px,py,w,h,clamped=false){
  if(!view||!finite(view.scale,.001,20)||![px,py].every(Number.isFinite))return null;
  let x=(px-view.x)/(view.scale*w),y=(py-view.y)/(view.scale*h);
  if(!clamped&&(x<0||x>1||y<0||y>1))return null;
  x=Math.max(0,Math.min(1,x));y=Math.max(0,Math.min(1,y));
  return [Math.round(x*1e5)/1e5,Math.round(y*1e5)/1e5];
}
