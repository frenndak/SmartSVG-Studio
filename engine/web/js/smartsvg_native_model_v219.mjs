/** V21.9 native masks; no URL, report, file path or dimensions trusted by default. */
export const FOLDER='SmartSVG_Studio_Native_V219';
const FILE=/^ni_([a-f0-9]{24})_(image|mask\d{2})\.png$/;
const finite=n=>typeof n==='number'&&Number.isFinite(n);
const inBounds=(n,low,high)=>Number.isSafeInteger(n)&&n>=low&&n<=high;
function ref(value,token,suffix){return value?.type==='output' && value?.subfolder===FOLDER &&
  typeof value.filename==='string' && value.filename===`ni_${token}_${suffix}.png` && FILE.test(value.filename);}
export function validateMeta(output){
  const m=Array.isArray(output?.smartsvg_native)?output.smartsvg_native[0]:null;
  if(!m || m.version!==1 || !inBounds(m.width,1,5000000)||!inBounds(m.height,1,5000000)||
    m.width*m.height>5000000 || !inBounds(m.count,1,32) || !Array.isArray(m.masks) || m.masks.length!==m.count ||
    !Array.isArray(m.objects) || m.objects.length!==m.count || typeof m.image?.filename!=='string')return null;
  const match=m.image.filename.match(FILE);
  if(!match||match[2]!=='image')return null;
  const token=match[1];
  if(!ref(m.image,token,'image') || !m.masks.every((r,i)=>ref(r,token,`mask${String(i).padStart(2,'0')}`)))return null;
  for(let i=0;i<m.count;i++){
    const item=m.objects[i];
    if(!item || item.objet!==i+1 || !Array.isArray(item.points) || item.points.length>8 ||
      !Array.isArray(item.alertes) || item.alertes.length>16 ||
      !item.alertes.every(x=>typeof x==='string'&&x.length<=100))return null;
    for(const pt of item.points){
      if(!pt || !inBounds(pt.x,0,m.width-1) || !inBounds(pt.y,0,m.height-1) ||
        typeof pt.type!=='string' || pt.type.length>50 || typeof pt.detail!=='string' || pt.detail.length>200) return null;
    }
  }
  return m;
}
export function nativeUrl(reference,base,route){
  if(!reference||typeof reference.filename!=='string'||!FILE.test(reference.filename)||
     reference.subfolder!==FOLDER||reference.type!=='output'||typeof route!=='string'||!route)return null;
  const u=new URL(route,base);
  u.searchParams.set('filename',reference.filename);u.searchParams.set('subfolder',FOLDER);u.searchParams.set('type','output');
  return u.toString();
}
export function clampView(view,iw,ih,fw,fh){
  if(![iw,ih,fw,fh].every(n=>finite(n)&&n>0)||!view||![view.scale,view.x,view.y].every(finite))throw Error('Coordonnées non valides');
  const scale=Math.max(.02,Math.min(16,view.scale));
  const axis=(p,w,b)=>w<=b?(b-w)/2:Math.max(b-w,Math.min(0,p));
  return {scale,x:axis(view.x,iw*scale,fw),y:axis(view.y,ih*scale,fh)};
}
export function fitView(iw,ih,fw,fh){
  const scale=Math.min(1,fw/iw,fh/ih);
  return clampView({scale,x:(fw-iw*scale)/2,y:(fh-ih*scale)/2},iw,ih,fw,fh);
}
export function nativeZoom(view,desired,ax,ay,iw,ih,fw,fh){
  if(![desired,ax,ay].every(finite)||view.scale<=0)throw Error('Zoom non valide');
  const scale=Math.min(16,Math.max(.02,desired)),r=scale/view.scale;
  return clampView({scale,x:ax-(ax-view.x)*r,y:ay-(ay-view.y)*r},iw,ih,fw,fh);
}
export function sourceAt(view,px,py,iw,ih){
  if(![px,py].every(finite))return null;
  const x=(px-view.x)/view.scale,y=(py-view.y)/view.scale;
  if(x<0||y<0||x>=iw||y>=ih)return null;
  return [Math.floor(x),Math.floor(y)];
}
export function centerOn(view,x,y,iw,ih,fw,fh){
  if(![x,y].every(finite)||x<0||y<0||x>=iw||y>=ih)throw Error('Point en dehors de la source');
  return clampView({...view,x:fw/2-(x+.5)*view.scale,y:fh/2-(y+.5)*view.scale},iw,ih,fw,fh);
}
