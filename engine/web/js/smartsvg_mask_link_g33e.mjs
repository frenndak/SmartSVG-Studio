/** G3.3e-a — strictly read-only correspondence between a G2.6 ordinal and
 * the exact G2.4 float32 slice in a pinned .smartsvg archive.
 *
 * mask_id is G2.4's position-based archive ID. It is not a semantic subject
 * identity. subject_id is present ONLY when a validated G1.2 Subject record
 * already supplies it. SHA-256 binds bytes, not meaning across edits.
 */
import {validProjectLock,matchesProjectLock} from './smartsvg_subject_project_gate_g33d.mjs';
const SHA=/^[a-f0-9]{64}$/;
const ID=/^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/;
export const MASK_CATALOG_VERSION=1;
const positive=n=>Number.isSafeInteger(n)&&n>0;

/** Normalize an untrusted cross-tab catalog, never accepting partial identity. */
export function normalizeMaskCatalog(catalog,report){
 if(!catalog||typeof catalog!=='object'||!validProjectLock(report)||
    catalog.version!==MASK_CATALOG_VERSION||
    catalog.project_name!==report.project_name||
    catalog.project_sha256!==report.project_sha256||
    catalog.source_sha256!==report.source_sha256||
    !SHA.test(String(catalog.source_sha256||''))||
    !positive(report.count)||report.count>32||
    !positive(report.width_px)||!positive(report.height_px)||
    catalog.count!==report.count||
    catalog.width_px!==report.width_px||
    catalog.height_px!==report.height_px||
    !ID.test(String(catalog.source_id||''))||
    !Array.isArray(catalog.items)||catalog.items.length!==report.count)
   return null;
 const seenHashes=new Set(),seenSubjects=new Set(),items=[];
 for(let i=0;i<catalog.items.length;i++){
   const item=catalog.items[i],maskId='base-mask-'+String(i).padStart(2,'0');
   if(!item||item.mask_index!==i||item.mask_id!==maskId||
      (item.subject_proof_status!==undefined&&
       !['verified','unbound','ambiguous','legacy_subject_record'].includes(item.subject_proof_status))||
      (item.subject_proof_status==='verified'&&
       !/^subject-[a-f0-9]{32}$/.test(String(item.subject_id||'')))||
      !SHA.test(String(item.mask_sha256_float32||''))||
      seenHashes.has(item.mask_sha256_float32)||item.has_foreground!==true||
      item.subject_ambiguous!==false||
      (item.subject_id!==null&&!ID.test(String(item.subject_id||'')))||
      !Array.isArray(item.accessory_ids)||item.accessory_ids.length>32||
      item.accessory_ids.some(id=>!ID.test(String(id||'')))||
      new Set(item.accessory_ids).size!==item.accessory_ids.length)return null;
   if(item.subject_id!==null){
     if(seenSubjects.has(item.subject_id)||item.accessory_ids.includes(item.subject_id))return null;
     seenSubjects.add(item.subject_id);
   }else if(item.accessory_ids.length)return null;
   seenHashes.add(item.mask_sha256_float32);
   items.push({mask_index:i,mask_id:maskId,
     mask_sha256_float32:item.mask_sha256_float32,
     has_foreground:true,subject_id:item.subject_id,
     accessory_ids:[...item.accessory_ids],subject_ambiguous:false,
     ...(item.subject_proof_status!==undefined
       ?{subject_proof_status:item.subject_proof_status}:{})});
 }
 // An accessory relationship is only meaningful when its subject exists.
 for(const item of items){
   if(item.accessory_ids.some(id=>!seenSubjects.has(id)))return null;
 }
 return {version:MASK_CATALOG_VERSION,project_name:report.project_name,
   project_sha256:report.project_sha256,source_sha256:report.source_sha256,
   source_id:catalog.source_id,width_px:report.width_px,
   height_px:report.height_px,count:report.count,items};
}

/** Derive a transport-safe catalog from server-validated G2.4 metadata.
 * Returns null on any ambiguity; old project inspection without the new
 * mask_identity property remains a valid *legacy pin* without a catalog.
 */
export function makeVerifiedMaskCatalog(project,report){
 if(!matchesProjectLock(report,project,report))return null;
 const evidence=project?.base_masks?.mask_identity;
 if(!evidence||evidence.version!==1||
    evidence.identity_kind!=='snapshot_position_plus_float32_digest'||
    evidence.subject_proof_schema_valid===false||
    !Array.isArray(evidence.bindings)||
    evidence.bindings.some(item=>
      ['invalid','missing','mismatch'].includes(item?.subject_proof_status)))return null;
 return normalizeMaskCatalog({
   version:1,project_name:project.name,project_sha256:project.sha256,
   source_sha256:report.source_sha256,
   source_id:evidence.source_id,width_px:report.width_px,
   height_px:report.height_px,count:report.count,items:evidence.bindings,
 },report);
}

export function maskForSubject(catalog,subject){
 if(!Number.isSafeInteger(subject)||subject<1||!catalog||
    !Array.isArray(catalog.items)||subject>catalog.items.length)return null;
 const entry=catalog.items[subject-1];
 return entry?.mask_index===subject-1?entry:null;
}
