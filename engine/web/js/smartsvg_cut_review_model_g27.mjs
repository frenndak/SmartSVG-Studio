/** G2.7: local, non-executing inspection of an SVG containing cut paths.
 * This is an indicative preview and a sanitizing subset builder, NOT a
 * Cricut Design Space import check or a physical cut qualification.
 */
export const MAX_SVG_BYTES=768*1024;
export const MAX_CUT_PATHS=64;
const NS='http://www.w3.org/2000/svg';
const NUM=String.raw`[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?`;
const D_ALLOWED=/^[0-9eE.+,\-\sMmLlHhVvCcSsQqTtAaZz]+$/;
const TAGS=new Set(['svg','g','path','title','desc']);
const ATTRS={
  svg:new Set(['xmlns','width','height','viewBox','version']),
  g:new Set(['id']),
  path:new Set(['id','d','fill','stroke','stroke-width']),
  title:new Set([]),desc:new Set([]),
};

export class CutReviewError extends Error {
  constructor(code){super(code);this.name='CutReviewError';this.code=code;}
}
function fail(code){throw new CutReviewError(code);}
function dimension(value){
  if(typeof value!=='string'||!/^(?:[0-9]+(?:\.[0-9]{1,4})?)mm$/.test(value))fail('DIMENSION_MM_REQUIRED');
  const mm=Number(value.slice(0,-2));
  if(!Number.isFinite(mm)||mm<1||mm>300)fail('INVALID_DIMENSION');
  return mm;
}
function box(value){
  if(typeof value!=='string')fail('INVALID_VIEWBOX');
  const parts=value.trim().split(/[\s,]+/);
  if(parts.length!==4||parts.some(p=>!new RegExp('^'+NUM+'$').test(p)))
    fail('INVALID_VIEWBOX');
  const data=parts.map(Number);
  if(data.some(v=>!Number.isFinite(v)||Math.abs(v)>100000)||
     data[2]<=0||data[3]<=0||data[2]>100000||data[3]>100000)
    fail('INVALID_VIEWBOX');
  return data;
}
function cutPath(d){
  if(typeof d!=='string'||!d||d.length>150000||!D_ALLOWED.test(d))
    fail('UNSUPPORTED_PATH');
  const trimmed=d.trim();
  if(!/^[Mm]/.test(trimmed)||!/[Zz]\s*$/.test(trimmed)||
     !/[LlHhVvCcSsQqTtAa]/.test(trimmed))
    fail('OPEN_OR_EMPTY_CONTOUR');
  const nums=trimmed.match(new RegExp(NUM,'g'))||[];
  if(nums.length>50000||nums.some(n=>!Number.isFinite(Number(n))||Math.abs(Number(n))>1e6))
    fail('INVALID_PATH_COORDINATE');
  return trimmed;
}
function safeId(id){
  return typeof id==='string'&&/^[A-Za-z][A-Za-z0-9_.-]{0,63}$/.test(id);
}

/** parseXml injection only for deterministic tests: real UI uses DOMParser. */
export function inspectCutSvg(source,{parseXml}={}){
  if(typeof source!=='string'||new TextEncoder().encode(source).length>MAX_SVG_BYTES)
    fail('SVG_TOO_LARGE');
  const clean=source.replace(/^\uFEFF/,'').trim();
  // Refuse declarations, entities and processing instructions before DOMParser.
  const xml=clean.replace(/^<\?xml\s+version=(?:"1\.0"|'1\.0')(?:\s+encoding=(?:"UTF-8"|'UTF-8'))?\s*\?>\s*/i,'');
  if(/<!|<\?|&(?:#|[a-z])/i.test(xml))fail('ACTIVE_OR_COMPLEX_XML');
  if(!xml.startsWith('<svg')&&!xml.startsWith('<svg '))fail('SVG_ROOT_REQUIRED');
  let document;
  try{
    document=(parseXml?parseXml(xml):new DOMParser().parseFromString(xml,'image/svg+xml'));
  }catch{fail('SVG_PARSE_FAILED');}
  const root=document?.documentElement;
  if(!root||root.localName!=='svg'||root.namespaceURI!==NS)
    fail('SVG_PARSE_FAILED');
  const descendants=Array.from(root.getElementsByTagName('*'));
  if(descendants.length>MAX_CUT_PATHS*4+10)fail('SVG_TOO_COMPLEX');
  const nodes=[root,...descendants];
  const paths=[],ids=new Set();
  for(const node of nodes){
    if(node.namespaceURI!==NS||!TAGS.has(node.localName))fail('UNSUPPORTED_SVG_ELEMENT');
    if(node.localName==='title'||node.localName==='desc'){
      if(Array.from(node.children||[]).length)fail('UNSUPPORTED_SVG_ELEMENT');
    }
    for(const attr of Array.from(node.attributes||[])){
      const a=attr.name;
      if(!ATTRS[node.localName].has(a)||
         (attr.namespaceURI&&!(node===root&&a==='xmlns'&&
                                 attr.namespaceURI==='http://www.w3.org/2000/xmlns/')))
        fail('UNSUPPORTED_SVG_ATTRIBUTE');
      if(a==='id'&&!safeId(attr.value))fail('INVALID_SVG_ID');
    }
    if(node.localName==='path'){
      const d=cutPath(node.getAttribute('d'));
      const id=node.getAttribute('id')||'contour-'+(paths.length+1);
      if(ids.has(id))fail('DUPLICATE_SVG_ID');
      ids.add(id);
      paths.push({index:paths.length+1,id,d});
      if(paths.length>MAX_CUT_PATHS)fail('TOO_MANY_PATHS');
    }
  }
  if(!paths.length)fail('NO_CUT_PATHS');
  const width_mm=dimension(root.getAttribute('width'));
  const height_mm=dimension(root.getAttribute('height'));
  const viewBox=box(root.getAttribute('viewBox'));
  const physicalRatio=width_mm/height_mm,coordinateRatio=viewBox[2]/viewBox[3];
  if(Math.abs(physicalRatio-coordinateRatio)/physicalRatio>0.02)
    fail('SVG_RATIO_CONFLICT');
  return Object.freeze({
    width_mm,height_mm,viewBox:Object.freeze(viewBox),
    paths:Object.freeze(paths.map(p=>Object.freeze(p))),
    verified:false,source:'local_manual_svg'
  });
}
export function selectedSvg(review,indices){
  if(!review||!Array.isArray(review.paths)||!Array.isArray(indices))fail('INVALID_SELECTION');
  if(!indices.length||indices.length>MAX_CUT_PATHS||
     new Set(indices).size!==indices.length||
     indices.some(i=>!Number.isInteger(i)||i<1||i>review.paths.length))
    fail('INVALID_SELECTION');
  // Validate again: this public serializer may be called without inspectCutSvg.
  const width_mm=dimension(String(review.width_mm)+'mm'),
        height_mm=dimension(String(review.height_mm)+'mm');
  const vb=box(review.viewBox?.join(' '));
  if(Math.abs(width_mm/height_mm-vb[2]/vb[3])/(width_mm/height_mm)>0.02)
    fail('SVG_RATIO_CONFLICT');
  const selected=indices.map(i=>review.paths[i-1]);
  const paths=selected.map((p,i)=>'  <path id="contour-'+(i+1)+
    '" d="'+cutPath(p.d)+'" fill="none" stroke="#000000"/>').join('\n');
  return '<?xml version="1.0" encoding="UTF-8"?>\n'+
    '<svg xmlns="'+NS+'" width="'+width_mm+'mm" height="'+height_mm+
    'mm" viewBox="'+vb.join(' ')+'">\n'+paths+'\n</svg>\n';
}
export const REVIEW_MESSAGES=Object.freeze({
  SVG_TOO_LARGE:'SVG trop volumineux (768 Ko maximum).',
  ACTIVE_OR_COMPLEX_XML:'SVG contenant des déclarations, entités ou instructions non prises en charge.',
  SVG_ROOT_REQUIRED:'Le fichier ne commence pas par un document SVG.',
  SVG_PARSE_FAILED:'SVG invalide : impossible de lire sa structure XML.',
  SVG_TOO_COMPLEX:'SVG trop complexe pour cet aperçu.',
  UNSUPPORTED_SVG_ELEMENT:'SVG avec image, texte, définition ou autre élément non pris en charge.',
  UNSUPPORTED_SVG_ATTRIBUTE:'SVG avec styles, transformations ou attributs non pris en charge.',
  INVALID_SVG_ID:'Identifiant d’objet SVG non valide.',
  DUPLICATE_SVG_ID:'Le SVG contient des identifiants d’objets en double.',
  UNSUPPORTED_PATH:'Tracé SVG non pris en charge ou non conforme.',
  OPEN_OR_EMPTY_CONTOUR:'Au moins un contour n’est pas fermé ou ne contient pas de segment.',
  INVALID_PATH_COORDINATE:'Coordonnée de tracé invalide.',
  NO_CUT_PATHS:'Aucun chemin de découpe SVG trouvé.',
  TOO_MANY_PATHS:'Plus de 64 chemins : regrouper les objets avant le contrôle.',
  DIMENSION_MM_REQUIRED:'Dimensions en millimètres explicites obligatoires.',
  INVALID_DIMENSION:'Dimensions physiques invalides (1 à 300 mm).',
  INVALID_VIEWBOX:'viewBox absent ou invalide.',
  SVG_RATIO_CONFLICT:'Le rapport de dimensions SVG et les millimètres ne correspondent pas.',
  INVALID_SELECTION:'Sélection de contours invalide.',
});
