/** G3.3b: bounded, voluntary transfer of G2.6 subject inspections across
 * same-origin ComfyUI tabs. No storage, no inference, no mutation of masks.
 */
import {validProjectLock} from './smartsvg_subject_project_gate_g33d.mjs';
import {normalizeMaskCatalog} from './smartsvg_mask_link_g33e.mjs';
export const SUBJECT_HANDOFF_CHANNEL='smartsvg:subjects:atelier:g33b:v1';
export const SUBJECT_HANDOFF_KIND='smartsvg:subjects:g33b';
const SHA=/^[a-f0-9]{64}$/;
const PREVIEW=/^data:image\/png;base64,[A-Za-z0-9+/]+={0,2}$/;

const PNG_PREFIX='data:image/png;base64,';
const PNG_SIGNATURE=[137,80,78,71,13,10,26,10];
/** Validate a bounded PNG thumbnail header, not just an image/png data URI.
 * Inspect only the first 33 decoded bytes (signature, IHDR and its CRC):
 * avoid allocating an extra 4 MiB binary string for every preview.
 * Browser decoding remains authoritative for the rest of the PNG.
 */
function validPngPreview(uri){
  if(typeof uri!=='string'||uri.length>700000||!PREVIEW.test(uri))return false;
  try{
    const header=atob(uri.slice(PNG_PREFIX.length,PNG_PREFIX.length+44));
    if(header.length!==33||
       !PNG_SIGNATURE.every((value,index)=>header.charCodeAt(index)===value)||
       header.slice(12,16)!=='IHDR')return false;
    const u32=offset=>(
      header.charCodeAt(offset)*0x1000000+
      header.charCodeAt(offset+1)*0x10000+
      header.charCodeAt(offset+2)*0x100+
      header.charCodeAt(offset+3)
    )>>>0;
    if(u32(8)!==13)return false;
    const width=u32(16),height=u32(20);
    // The actual G2.6 previews are 88 px; 512 px per side is generous.
    // 32 accepted previews then decode to at most 32 MiB of RGBA pixels.
    if(!width||!height||width>512||height>512)return false;
    const depth=header.charCodeAt(24),color=header.charCodeAt(25);
    const legalDepth={0:[1,2,4,8,16],2:[8,16],3:[1,2,4,8],
                      4:[8,16],6:[8,16]};
    if(!legalDepth[color]?.includes(depth)||
       header.charCodeAt(26)!==0||header.charCodeAt(27)!==0||
       ![0,1].includes(header.charCodeAt(28)))return false;
    let crc=0xffffffff;
    for(let i=12;i<29;i++){
      crc^=header.charCodeAt(i);
      for(let bit=0;bit<8;bit++){
        crc=(crc>>>1)^((crc&1)?0xedb88320:0);
      }
    }
    return ((crc^0xffffffff)>>>0)===u32(29);
  }catch{return false;}
}

const CODES=new Set([
 'MASQUE_VIDE','FRAGMENTS_DETACHES','MICRO_FRAGMENTS','TOUCHE_BORD_IMAGE',
 'SILHOUETTE_RECTANGULAIRE','SUJET_TRES_PETIT',
]);
export const SUBJECT_WARNING_LABELS=Object.freeze({
 MASQUE_VIDE:'Masque vide',
 FRAGMENTS_DETACHES:'Fragments détachés',
 MICRO_FRAGMENTS:'Micro-fragments à examiner',
 TOUCHE_BORD_IMAGE:'Sujet au bord de l’image',
 SILHOUETTE_RECTANGULAIRE:'Silhouette presque rectangulaire',
 SUJET_TRES_PETIT:'Sujet très petit',
});
const integer=(n,min=0,max=Number.MAX_SAFE_INTEGER)=>
 Number.isSafeInteger(n)&&n>=min&&n<=max;
const bbox=(v,width,height)=>Array.isArray(v)&&v.length===4&&
 v.every(n=>integer(n))&&v[2]>v[0]&&v[3]>v[1]&&
 v[2]<=width&&v[3]<=height;
const zone=(v,width,height)=>{
 if(!v||!['MICRO_FRAGMENT','FRAGMENT_SEPARE'].includes(v.type)||
    !bbox(v.bbox_source_px,width,height))return null;
 const tile=v.bbox_apercu_88px;
 if(!Array.isArray(tile)||tile.length!==4||!tile.every(n=>integer(n,0,88))||
    tile[2]<tile[0]||tile[3]<tile[1])return null;
 return {type:v.type,bbox_source_px:[...v.bbox_source_px],
   bbox_apercu_88px:[...tile]};
};
/** Accept raw output payload OR the message returned by this function.
 * Any invalid field fails closed rather than silently losing a subject.
 */
export function normalizeSubjectInspection(raw){
 if(!raw||typeof raw!=='object')return null;
 const body=raw.kind===SUBJECT_HANDOFF_KIND?raw:raw;
 if(raw.kind!==undefined&&raw.kind!==SUBJECT_HANDOFF_KIND)return null;
 if(raw.version!==undefined&&raw.version!==1)return null;
 const {source_sha256:sha,width_px:width,height_px:height,count,sujets}=body;
 if(!SHA.test(String(sha||''))||!integer(width,1,10000)||
    !integer(height,1,10000)||width*height>5_000_000||
    !integer(count,1,32)||!Array.isArray(sujets)||sujets.length!==count||
    !integer(body.selection,1,count))return null;
 const seen=new Set(),items=[];
 let bytes=0;
 for(const item of sujets){
   if(!item||!integer(item.numero,1,count)||seen.has(item.numero))return null;
   seen.add(item.numero);
   if(!Array.isArray(item.codes)||item.codes.length>8||
      item.codes.some(c=>!CODES.has(c)))return null;
   if(!Array.isArray(item.zones_a_examiner)||item.zones_a_examiner.length>12)return null;
   const zones=[];
   for(const rawZone of item.zones_a_examiner){
     const cleaned=zone(rawZone,width,height);
     if(!cleaned)return null;
     zones.push(cleaned);
   }
   if(!integer(item.zones_non_affichees??0,0,1000000))return null;
   let image=null;
   if(item.image_data!==undefined&&item.image_data!==null){
     if(!validPngPreview(item.image_data))return null;
     image=item.image_data;
     bytes+=image.length;
     if(bytes>4*1024*1024)return null;
   }
   items.push({
     numero:item.numero,
     image_data:image,
     codes:[...item.codes],
     zones_a_examiner:zones,
     zones_non_affichees:item.zones_non_affichees??0,
     etat:item.etat==='A_VERIFIER'?'A_VERIFIER':'INSPECTION_VISUELLE_REQUISE',
   });
 }
 items.sort((a,b)=>a.numero-b.numero);
 // Legacy G3.3b reports remain readable; executable selection is enabled
 // only when BOTH a real ComfyUI node ID and a fresh execution session exist.
 const hasBinding=body.node_id!==undefined||body.session_id!==undefined;
 const hasProject=body.project_name!==undefined||body.project_sha256!==undefined;
 const hasCatalog=body.mask_catalog!==undefined;
 const catalog=hasCatalog?normalizeMaskCatalog(body.mask_catalog,body):null;
 if(hasCatalog&&!catalog)return null;
 if(hasProject&&(!hasBinding||!validProjectLock(body)))return null;
 if(hasBinding&&(!integer(body.node_id,1)||
    typeof body.session_id!=='string'||!/^[a-f0-9]{32}$/.test(body.session_id)||
    !Number.isSafeInteger(body.expires_at_ms)||body.expires_at_ms<=0||
    Date.now()>=body.expires_at_ms))
   return null;
 return {kind:SUBJECT_HANDOFF_KIND,version:1,source_sha256:sha,
   width_px:width,height_px:height,count,selection:body.selection,
   sujets:items,modifications_automatiques:false,decoupe_certifiee:false,
   ...(hasBinding?{node_id:body.node_id,session_id:body.session_id,
     expires_at_ms:body.expires_at_ms}:{}),
   ...(hasProject?{project_name:body.project_name,
     project_sha256:body.project_sha256}:{}),
   ...(hasCatalog?{mask_catalog:catalog}:{})};
}
