/** V21.9 inspection non destructive: source/mask loaded at native pixel resolution.
 * Only the visible viewport is rasterized to a bounded canvas. No mask writes.
 */
import {app} from '../../scripts/app.js';
import {api} from '../../scripts/api.js';
import {validateMeta,nativeUrl,fitView,clampView,nativeZoom,sourceAt,centerOn} from './smartsvg_native_model_v219.mjs';
const CLASS='SmartSVGNativeInspectorV219';
const EXT='smartsvg.studio.v219.native_inspection';
const create=(tag,txt)=>{const e=document.createElement(tag);if(txt!=null)e.textContent=String(txt);return e;};
function button(text,fn){const e=create('button',text);e.type='button';e.addEventListener('click',fn);return e;}
function stylesheet(){
  if(document.getElementById('smartsvg219-css'))return;
  const el=create('style');el.id='smartsvg219-css';el.textContent=`
  .ss219-node {padding:9px;border:1px solid #576879;border-radius:9px;background:#1e2630;color:#eee;font:12px system-ui}
  .ss219-node button,.ss219-modal button,.ss219-modal select{color:#fff;background:#344054;border:1px solid #7a8fa5;border-radius:6px;padding:7px;cursor:pointer}
  .ss219-modal{position:fixed;inset:0;z-index:2147482001;background:#000d;display:flex;align-items:center;justify-content:center;padding:10px;box-sizing:border-box}
  .ss219-panel{background:#1e2733;color:#fff;border:1px solid #62758a;border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:10px;width:min(1140px,96vw);max-height:96vh;box-sizing:border-box;overflow:auto;font:13px system-ui}
  .ss219-tools,.ss219-spots{display:flex;align-items:center;flex-wrap:wrap;gap:8px}
  .ss219-viewport{width:100%;height:min(64vh,650px);min-height:220px;position:relative;touch-action:none;overflow:hidden;background:repeating-conic-gradient(#ddd 0% 25%,#bbb 0% 50%) 50%/20px 20px;cursor:grab;outline-offset:2px;border:1px solid #758595;box-sizing:border-box}
  .ss219-viewport canvas{width:100%;height:100%;display:block}
  .ss219-note{color:#c5d6e9;font-size:12px}
  .ss219-modal :focus-visible{outline:2px solid #9dd8ff;outline-offset:2px}
  `;document.head.appendChild(el);
}
function imgLoad(ref){return new Promise((resolve,reject)=>{
  const url=nativeUrl(ref,window.location.href,api.apiURL('/view'));
  if(!url){reject(Error('Référence de fichier invalide'));return;}
  const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error('Aperçu natif indisponible / purgé'));
  im.src=url;
});}
async function showInspector(node,meta,generation){
  stylesheet();
  const image=await imgLoad(meta.image);
  // If another run completed while this native PNG was loading, cancel it.
  if(node._smartsvg219Generation!==generation)return;
  if(image.naturalWidth!==meta.width || image.naturalHeight!==meta.height)throw Error('Dimensions de la source native incohérentes');
  const root=create('div');root.className='ss219-modal';
  const panel=create('div');panel.className='ss219-panel';panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');panel.setAttribute('aria-label','Inspection Cricut native');
  const heading=create('strong',`SmartSVG V21.9 — inspection à ${meta.width} × ${meta.height} pixels`);
  const tools=create('div');tools.className='ss219-tools';
  const chooser=create('select');chooser.setAttribute('aria-label','Choisir un sujet');
  meta.objects.forEach((o,i)=>{const option=create('option',`Sujet ${i+1} · ${o.etat}`);option.value=String(i);chooser.append(option);});
  const note=create('span','Chargement du masque…');note.className='ss219-note';
  const zoomInfo=create('strong','');
  const coords=create('span','Position source : —');coords.className='ss219-note';
  const viewport=create('div');viewport.className='ss219-viewport';viewport.tabIndex=0;
  viewport.setAttribute('role','application');viewport.setAttribute('aria-label','Inspection native : molette et déplacement à la souris');
  const canvas=create('canvas');viewport.append(canvas);
  const ctx=canvas.getContext('2d');if(!ctx)throw Error('Canvas 2D indisponible');
  const scratch=create('canvas'),scratchCtx=scratch.getContext('2d',{willReadFrequently:true});
  if(!scratchCtx)throw Error('Canvas masque indisponible');
  let mask=null, current=0, view=null,disposed=false,loading=0,pan=null,framePending=false;
  const viewportSize=()=>{const b=viewport.getBoundingClientRect();return {w:Math.max(1,b.width),h:Math.max(1,b.height)};};
  const local=e=>{const r=viewport.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top];};
  function resize(){
    const {w,h}=viewportSize();const dpr=Math.min(1.5,Math.max(1,window.devicePixelRatio||1));
    canvas.width=Math.max(1,Math.min(1800,Math.round(w*dpr)));canvas.height=Math.max(1,Math.min(1200,Math.round(h*dpr)));
    scratch.width=canvas.width;scratch.height=canvas.height;
    view=view?clampView(view,meta.width,meta.height,w,h):fitView(meta.width,meta.height,w,h);
    schedule();
  }
  function draw(){
    if(disposed)return;
    framePending=false;
    const {w,h}=viewportSize(),rx=canvas.width/w,ry=canvas.height/h;
    ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.imageSmoothingEnabled=view.scale<1;
    ctx.setTransform(rx*view.scale,0,0,ry*view.scale,rx*view.x,ry*view.y);
    ctx.drawImage(image,0,0,meta.width,meta.height);
    ctx.setTransform(1,0,0,1,0,0);
    if(mask){
      scratchCtx.setTransform(1,0,0,1,0,0);scratchCtx.clearRect(0,0,scratch.width,scratch.height);
      scratchCtx.imageSmoothingEnabled=view.scale<1;
      scratchCtx.setTransform(rx*view.scale,0,0,ry*view.scale,rx*view.x,ry*view.y);
      scratchCtx.drawImage(mask,0,0,meta.width,meta.height);
      scratchCtx.setTransform(1,0,0,1,0,0);
      const data=scratchCtx.getImageData(0,0,scratch.width,scratch.height);
      const px=data.data,ww=scratch.width,hh=scratch.height;
      const active=new Uint8Array(ww*hh);
      for(let k=0;k<active.length;k++)active[k]=(px[k*4+3] && px[k*4]>=128)?1:0;
      for(let y=0;y<hh;y++)for(let x=0;x<ww;x++){
        const k=y*ww+x,p=k*4,inside=active[k];
        const edge= (x>0&&inside!==active[k-1]) || (x<ww-1&&inside!==active[k+1]) ||
                    (y>0&&inside!==active[k-ww]) || (y<hh-1&&inside!==active[k+ww]);
        px[p]=edge?30:235;px[p+1]=edge?255:45;px[p+2]=edge?255:175;
        px[p+3]=edge?235:inside?72:0;
      }
      scratchCtx.putImageData(data,0,0);
      ctx.drawImage(scratch,0,0);
    }
    // Mark localized findings, but never imply these are cutting toolpaths.
    ctx.lineWidth=2;ctx.font='bold 11px system-ui';
    for(const [index,spot] of meta.objects[current].points.entries()){
      const x=(spot.x+.5)*view.scale+view.x,y=(spot.y+.5)*view.scale+view.y;
      if(x<0||y<0||x>w||y>h)continue;
      ctx.strokeStyle='#ffe48b';ctx.beginPath();ctx.arc(x*rx,y*ry,9,0,2*Math.PI);ctx.stroke();
      ctx.fillStyle='#101820';ctx.fillRect(x*rx+10,y*ry-9,16,16);
      ctx.fillStyle='#ffe48b';ctx.fillText(String(index+1),x*rx+13,y*ry+3);
    }
    zoomInfo.textContent=`${Math.round(view.scale*100)} % · ${view.scale>=1?'pixels natifs visibles':'vue réduite : inspecter à 100 %'}`;
  }
  function schedule(){if(disposed||framePending)return;framePending=true;requestAnimationFrame(draw);}
  function zoom(factor,center){const {w,h}=viewportSize();view=nativeZoom(view,view.scale*factor,center?.[0]??w/2,center?.[1]??h/2,meta.width,meta.height,w,h);schedule();}
  function exact(){const {w,h}=viewportSize();view=nativeZoom(view,1,w/2,h/2,meta.width,meta.height,w,h);schedule();}
  function fit(){const {w,h}=viewportSize();view=fitView(meta.width,meta.height,w,h);schedule();}
  const plus=button('+ Zoom',()=>zoom(1.4)),minus=button('− Zoom',()=>zoom(1/1.4));
  const one=button('100 % natif',exact),fitButton=button('Adapter',fit);
  tools.append(create('span','Sujet'),chooser,minus,plus,one,fitButton,zoomInfo,coords);
  const spots=create('div');spots.className='ss219-spots';
  const footer=create('div','Lecture seule : pour corriger une zone, utiliser l’éditeur de masques V21.6 puis relancer le workflow. Les fichiers Cricut ne sont jamais modifiés par cet inspecteur.');footer.className='ss219-note';
  let observer;
  const close=()=>{if(disposed)return;disposed=true;loading++;observer?.disconnect?.();root.remove();
    if(node._smartsvg219Close===close)node._smartsvg219Close=null;
    node._smartsvg219Open=false;
    if(node._smartsvg219Button)node._smartsvg219Button.disabled=!node._smartsvg219Meta;
    node._smartsvg219Button?.focus?.();
  };
  node._smartsvg219Close=close;
  const closeBtn=button('Fermer',close);
  function updateSpots(){
    spots.replaceChildren();
    const points=meta.objects[current].points;
    if(!points.length)spots.append(create('span','Aucun point d’alerte localisé : inspecter visuellement la silhouette complète.'));
    points.forEach((spot,i)=>spots.append(button(`${i+1}. ${spot.type}`,()=>{
      const {w,h}=viewportSize();view=nativeZoom(view,2,w/2,h/2,meta.width,meta.height,w,h);
      view=centerOn(view,spot.x,spot.y,meta.width,meta.height,w,h);note.textContent=spot.detail;schedule();
    })));
  }
  async function loadMask(index){
    const token=++loading;mask=null;current=index;note.textContent='Chargement du masque natif…';updateSpots();schedule();
    try{
      const im=await imgLoad(meta.masks[index]);
      if(disposed||token!==loading)return;
      if(im.naturalWidth!==meta.width||im.naturalHeight!==meta.height)throw Error('Dimensions du masque incohérentes');
      mask=im;note.textContent=`Sujet ${index+1} : contours à la résolution source, ${meta.objects[index].alertes.length} alerte(s) géométriques`;schedule();
    }catch(e){if(!disposed&&token===loading){note.textContent=e.message;schedule();}}
  }
  chooser.addEventListener('change',()=>void loadMask(Number(chooser.value)));
  viewport.addEventListener('wheel',e=>{if(disposed)return;zoom(Math.exp(-Math.max(-250,Math.min(250,e.deltaY||0))/500),local(e));e.preventDefault?.();},{passive:false});
  viewport.addEventListener('pointerdown',e=>{if(e.button!==0 && e.button!==1)return;pan={pointer:e.pointerId,x:e.clientX,y:e.clientY};viewport.setPointerCapture?.(e.pointerId);e.preventDefault?.();});
  viewport.addEventListener('pointermove',e=>{
    const [x,y]=local(e);const source=sourceAt(view,x,y,meta.width,meta.height);
    coords.textContent=source?`Pixel source : ${source[0]}, ${source[1]}`:'Hors image';
    if(!pan||e.pointerId!==pan.pointer)return;
    const {w,h}=viewportSize();view=clampView({...view,x:view.x+e.clientX-pan.x,y:view.y+e.clientY-pan.y},meta.width,meta.height,w,h);
    pan.x=e.clientX;pan.y=e.clientY;schedule();e.preventDefault?.();
  });
  for(const name of ['pointerup','pointercancel','lostpointercapture'])viewport.addEventListener(name,e=>{if(pan&&pan.pointer===e.pointerId)pan=null;});
  const keydown=e=>{if(disposed)return;if(e.key==='Escape'){e.preventDefault();close();}};
  root.addEventListener('keydown',keydown);
  root.addEventListener('pointerdown',e=>{if(e.target===root)close();});
  panel.append(heading,tools,viewport,spots,note,footer,closeBtn);root.append(panel);document.body.append(root);
  observer=typeof ResizeObserver==='function'?new ResizeObserver(resize):null;observer?.observe(viewport);
  resize();updateSpots();void loadMask(0);chooser.focus?.();
}
app.registerExtension({name:EXT,nodeCreated(node){
  if((node?.comfyClass||node?.type)!==CLASS || node._smartsvg219Hook || typeof node.addDOMWidget!=='function')return;
  stylesheet();node._smartsvg219Hook=true;node._smartsvg219Generation=0;
  const block=create('div');block.className='ss219-node';
  const note=create('div','Exécuter le nœud pour obtenir les contours natifs.');
  const trigger=button('Inspecter contours 100 %',()=>{
    if(node._smartsvg219Open||!node._smartsvg219Meta)return;
    node._smartsvg219Open=true;trigger.disabled=true;
    const generation=node._smartsvg219Generation;
    void showInspector(node,node._smartsvg219Meta,generation).catch(e=>{
      if(node._smartsvg219Generation!==generation)return;
      node._smartsvg219Open=false;trigger.disabled=!node._smartsvg219Meta;note.textContent='Aperçu : '+e.message;
    });
  });
  trigger.disabled=true;node._smartsvg219Button=trigger;
  block.append(note,trigger);
  node.addDOMWidget('smartsvg_native_v219','smartsvg_native',block,{serialize:false});
  const original=node.onExecuted;
  node.onExecuted=function(output){original?.apply(this,arguments);
    // A new execution invalidates both open overlays and pending image loads.
    node._smartsvg219Generation++;
    node._smartsvg219Close?.();
    node._smartsvg219Open=false;
    const meta=validateMeta(output);node._smartsvg219Meta=meta;
    trigger.disabled=!meta||!!node._smartsvg219Open;
    note.textContent=meta?`${meta.count} sujet(s) · ${meta.width} × ${meta.height} px natifs · vérifier avant Print Then Cut`:
      'Pas de copie native : se reporter au rapport JSON. Masques de fabrication inchangés.';
    node.setDirtyCanvas?.(true,true);
  };
  const oldRemoved=node.onRemoved;
  node.onRemoved=function(){node._smartsvg219Generation++;node._smartsvg219Close?.();
    node._smartsvg219Meta=null;return oldRemoved?.apply(this,arguments);};
  node.size=[Math.max(node.size?.[0]||340,340),Math.max(node.size?.[1]||240,280)];
}});
