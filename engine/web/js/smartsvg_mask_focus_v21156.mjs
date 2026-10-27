/** G2.6 focus requests: ephemeral only, pinned to source and masks. */
const SHA=/^[a-f0-9]{64}$/;
const integer=(x,lower=0)=>Number.isInteger(x)&&x>=lower;
export function validatedFocus(raw,meta){
  if(!raw||raw.version!==1||!meta||!SHA.test(String(raw.source_sha256||''))||
    raw.source_sha256!==meta.source||!integer(raw.subject,1)||raw.subject>meta.count||
    raw.width_px!==meta.width||raw.height_px!==meta.height||
    !Array.isArray(raw.bbox_source_px)||raw.bbox_source_px.length!==4)return null;
  const b=raw.bbox_source_px;
  if(!b.every(v=>integer(v))||b[2]<=b[0]||b[3]<=b[1]||
    b[2]>meta.width||b[3]>meta.height)return null;
  return Object.freeze({subject:raw.subject,box:Object.freeze([...b]),
    source_sha256:raw.source_sha256});
}
export function centerFocusView(box,sourceWidth,sourceHeight,imageWidth,imageHeight,frameWidth,frameHeight,limit=8){
  if(!Array.isArray(box)||box.length!==4||
    ![sourceWidth,sourceHeight,imageWidth,imageHeight,frameWidth,frameHeight,limit].every(n=>Number.isFinite(n)&&n>0)||
    box.some(n=>!Number.isFinite(n))||box[2]<=box[0]||box[3]<=box[1])throw new Error('Zone à examiner invalide');
  const width=(box[2]-box[0])*imageWidth/sourceWidth;
  const height=(box[3]-box[1])*imageHeight/sourceHeight;
  const scale=Math.max(.1,Math.min(limit,frameWidth/Math.max(1,width*2),frameHeight/Math.max(1,height*2)));
  const centerX=(box[0]+box[2])*imageWidth/(2*sourceWidth);
  const centerY=(box[1]+box[3])*imageHeight/(2*sourceHeight);
  return {scale,x:frameWidth/2-centerX*scale,y:frameHeight/2-centerY*scale};
}
