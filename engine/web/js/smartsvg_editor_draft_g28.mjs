/** G2.8 — crash-safe, browser-local drafts for V21.6 brush strokes only.
 * No image bytes, ComfyUI graph or original masks are written to localStorage.
 * Drafts are untrusted input and must match the exact source fingerprint.
 */
import {encodeDocument,decodeDocument,LIMITS}
  from './smartsvg_editor_model_v216.mjs';

const PREFIX='smartsvg-v216-draft-v1:';
const TTL_MS=7*24*60*60*1000;
const MAX_ENVELOPE_BYTES=LIMITS.bytes+1000;

export function editorDraftStore(storage,meta,nodeId,now=()=>Date.now()){
  const valid=Number.isSafeInteger(nodeId)&&nodeId>=0&&
    typeof meta?.source==='string'&&/^[a-f0-9]{64}$/.test(meta.source)&&
    Number.isSafeInteger(meta.width)&&meta.width>0&&
    Number.isSafeInteger(meta.height)&&meta.height>0&&
    Number.isSafeInteger(meta.count)&&meta.count>=1&&meta.count<=32&&
    typeof now==='function'&&storage&&
    typeof storage.getItem==='function'&&typeof storage.setItem==='function'&&
    typeof storage.removeItem==='function';
  const key=PREFIX+(valid?String(nodeId)+':'+meta.source:'disabled');
  const clear=()=>{
    if(!valid)return false;
    try{storage.removeItem(key);return true;}catch{return false;}
  };
  const save=strokes=>{
    if(!valid)return false;
    if(!Array.isArray(strokes))return false;
    if(!strokes.length){clear();return true;}
    let text;
    try{text=encodeDocument(meta,strokes);}catch{return false;}
    const timestamp=now();
    if(!Number.isSafeInteger(timestamp)||timestamp<1)return false;
    const envelope=JSON.stringify({
      version:1,created_at_ms:timestamp,source:meta.source,
      width:meta.width,height:meta.height,count:meta.count,
      document:text
    });
    if(new TextEncoder().encode(envelope).length>MAX_ENVELOPE_BYTES)return false;
    try{storage.setItem(key,envelope);return true;}catch{return false;}
  };
  const load=()=>{
    if(!valid)return null;
    let payload;
    try{payload=storage.getItem(key);}catch{return null;}
    if(typeof payload!=='string'||!payload)return null;
    if(new TextEncoder().encode(payload).length>MAX_ENVELOPE_BYTES){clear();return null;}
    let data;
    try{data=JSON.parse(payload);}catch{clear();return null;}
    const current=now();
    if(!data||data.version!==1||data.source!==meta.source||
       data.width!==meta.width||data.height!==meta.height||
       data.count!==meta.count||
       !Number.isSafeInteger(data.created_at_ms)||
       !Number.isSafeInteger(current)||current<data.created_at_ms||
       current-data.created_at_ms>TTL_MS||typeof data.document!=='string'){
      clear();return null;
    }
    try{
      const strokes=decodeDocument(meta,data.document);
      if(!strokes.length){clear();return null;}
      return strokes;
    }catch{clear();return null;}
  };
  return Object.freeze({enabled:!!valid,key:valid?key:null,save,load,clear});
}
