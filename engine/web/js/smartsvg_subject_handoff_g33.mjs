/** G3.3b: bounded, voluntary transfer of G2.6 subject inspections across
 * same-origin ComfyUI tabs. No storage, no inference, no mutation of masks.
 */
export const SUBJECT_HANDOFF_CHANNEL='smartsvg:subjects:atelier:g33b:v1';
export const SUBJECT_HANDOFF_KIND='smartsvg:subjects:g33b';
const SHA=/^[a-f0-9]{64}$/;
const PREVIEW=/^data:image\/png;base64,[A-Za-z0-9+/]+={0,2}$/;
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
     if(typeof item.image_data!=='string'||item.image_data.length>700000||
        !PREVIEW.test(item.image_data))return null;
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
 return {kind:SUBJECT_HANDOFF_KIND,version:1,source_sha256:sha,
   width_px:width,height_px:height,count,selection:body.selection,
   sujets:items,modifications_automatiques:false,decoupe_certifiee:false};
}
