/** SmartSVG V21.10: one native-resolution canvas for inspection, edits and QA.
 * Base PNGs are read-only temporary ComfyUI /view files. Edited MASK is produced
 * by Python after saving normalized, fingerprint-bound strokes and rerunning.
 */
import {app} from '../../scripts/app.js';
import {api} from '../../scripts/api.js';
import {validateUnified,nativeUrl,fitView,clampView,nativeZoom,sourceAt,centerOn,
        LIMITS,serialize,deserialize,positionUV} from './smartsvg_unified_model_v2110.mjs';
const CLASSES=new Set(['SmartSVGUnifiedEditorV2110','SmartSVGUnifiedEditorV21112']),EXT='smartsvg.studio.v2110.unified';
const E=(tag,txt,cls)=>{const e=document.createElement(tag);if(txt!==undefined)e.textContent=String(txt);if(cls)e.className=cls;return e;};
const B=(txt,fn)=>{const e=E('button',txt);e.type='button';e.addEventListener('click',fn);return e;};
function style(){
 if(document.getElementById('smartsvg2110-css'))return;
 const e=E('style');e.id='smartsvg2110-css';e.textContent=`
 .ss2110-node{background:#1d2832;color:#e8f1fc;border:1px solid #617387;padding:9px;border-radius:9px;font:12px system-ui}
 .ss2110-node button,.ss2110-panel button,.ss2110-panel select{border:1px solid #74869a;border-radius:6px;background:#304254;color:#fff;padding:7px;font:12px system-ui;cursor:pointer}
 .ss2110-panel button:disabled{opacity:.45;cursor:not-allowed}
 .ss2110-panel button.active{background:#125a83;border-color:#7dd6ff}
 .ss2110-modal{position:fixed;inset:0;background:#000d;z-index:2147482002;display:flex;align-items:center;justify-content:center;padding:10px;box-sizing:border-box}
 .ss2110-panel{width:min(1170px,97vw);max-height:97vh;overflow:auto;box-sizing:border-box;display:flex;flex-direction:column;gap:9px;background:#1d2731;color:#f2f6fd;border:1px solid #74899d;border-radius:12px;padding:13px;font:13px system-ui}
 .ss2110-row{display:flex;gap:7px;align-items:center;flex-wrap:wrap}.ss2110-row label{display:flex;gap:5px;align-items:center}
 .ss2110-viewport{height:clamp(210px,59vh,660px);width:100%;border:1px solid #6e8496;box-sizing:border-box;touch-action:none;overflow:hidden;position:relative;cursor:crosshair;background:repeating-conic-gradient(#eee 0% 25%,#c4c4c4 0% 50%) 50%/20px 20px}
 .ss2110-viewport canvas{display:block;width:100%;height:100%}.ss2110-note{font:12px system-ui;color:#ccdeef}
 .ss2110-modal :focus-visible{outline:2px solid #b1e6ff;outline-offset:2px}
 @media(max-height:620px){.ss2110-viewport{height:44vh;min-height:170px}}
 `;document.head.append(e);
}
function fetchImage(ref){return new Promise((resolve,reject)=>{
  const url=nativeUrl(ref,window.location.href,api.apiURL('/view'));
  if(!url){reject(Error('Référence image non autorisée'));return;}
  const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error('Aperçu natif introuvable (purge ou réseau)'));im.src=url;
});}
function clone(items){return items.map(s=>({...s,points:s.points.map(p=>[...p])}));}
async function open(node,m,generation){
 const field=(node.widgets||[]).find(w=>w.name==='retouches_json');
 if(!field)throw Error('Widget retouches_json introuvable');
 let history=deserialize(m,String(field.value||''));
 const draft=node._ss2110Draft;
 const draftRecovered=!!(draft?.source===m.source && draft?.text);
 if(draftRecovered)history=deserialize(m,draft.text);
 else if(draft)node._ss2110Draft=null;
 const source=await fetchImage(m.image);
 if(node._ss2110Generation!==generation)return;
 if(source.naturalWidth!==m.width||source.naturalHeight!==m.height)throw Error('Dimensions source incohérentes');
 style();
 const root=E('div',undefined,'ss2110-modal'),panel=E('div',undefined,'ss2110-panel');
 panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');panel.setAttribute('aria-label','Éditeur natif SmartSVG');
 const title=E('strong',`SmartSVG V21.10 · ${m.width} × ${m.height} px natifs · ${m.count} sujet(s)`);
 const tools=E('div',undefined,'ss2110-row'),nav=E('div',undefined,'ss2110-row');
 const choose=E('select');choose.setAttribute('aria-label','Sujet');
 m.objects.forEach((o,i)=>{const p=E('option',`Sujet ${i+1} · ${o.etat}`);p.value=String(i);choose.append(p);});
 let current=0,mode='add',radius=.015,undo=history,redo=[],active=null,pan=null,space=false;
 let mask=null,loading=0,closed=false,scheduled=false,observer=null,dirtyRevision=draftRecovered?1:0;
 // Cache the expensive mask-edge raster until viewport or committed strokes change.
 // Active brush feedback draws on top without reading every canvas pixel per move.
 let maskCacheKey=null;
 const rlabel=E('span','1,5 %'),range=E('input');range.type='range';range.min='.002';range.max='.1';range.step='.001';range.value=String(radius);
 range.setAttribute('aria-label','Taille du pinceau');
 range.addEventListener('input',()=>{radius=Number(range.value);rlabel.textContent=(radius*100).toFixed(1).replace('.',',')+' %';});
 const add=B('+ Ajouter',()=>setMode('add')),erase=B('− Retirer',()=>setMode('erase')),move=B('✋ Déplacer',()=>setMode('pan'));
 const back=B('↶ Annuler',()=>{if(undo.length){redo.push(undo.pop());dirtyRevision++;refresh();schedule();}});
 const forward=B('↷ Rétablir',()=>{if(redo.length){undo.push(redo.pop());dirtyRevision++;refresh();schedule();}});
 const zoomLabel=E('strong',''),coordinates=E('span','Position : —','ss2110-note');
 const viewport=E('div',undefined,'ss2110-viewport');viewport.tabIndex=0;
 viewport.setAttribute('role','application');viewport.setAttribute('aria-label','Pinceau ou déplacement ; molette pour zoomer');
 const screen=E('canvas');viewport.append(screen);const ctx=screen.getContext('2d');
 const maskCanvas=E('canvas'),maskCtx=maskCanvas.getContext('2d',{willReadFrequently:true});
 if(!ctx||!maskCtx)throw Error('Canvas 2D non disponible');
 const status=E('div','Chargement du masque…','ss2110-note'),quality=E('div',undefined,'ss2110-note');
 const alerts=E('div',undefined,'ss2110-row'),footer=E('div',`Le diagnostic correspond à la dernière exécution. Après une retouche, enregistrer et relancer. ${m.real_size?'Largeur contrôlée : '+m.qa_width_mm+' mm (à relier à Express).':'Ancien nœud : seuils de 40 mm hypothétiques.'} Les pixels finaux sont calculés côté Python.`,'ss2110-note');
 const location=()=>{const r=viewport.getBoundingClientRect();return {w:Math.max(1,r.width),h:Math.max(1,r.height)};};
 const local=e=>{const b=viewport.getBoundingClientRect();return [e.clientX-b.left,e.clientY-b.top];};
 let view=null;
 function refresh(){
   for(const [b,kind] of [[add,'add'],[erase,'erase'],[move,'pan']])b.classList.toggle('active',mode===kind);
   back.disabled=!undo.length;forward.disabled=!redo.length;
   viewport.style.cursor=mode==='pan'||space||pan?'grab':mask?'crosshair':'not-allowed';
   quality.textContent=`${undo.length} trait(s) · ${redo.length} annulé(s) · diagnostic ${m.quality} · ${dirtyRevision?'retouches non validées : relancer après sauvegarde':'inspection de la dernière exécution'}`;
 }
 function setMode(v){mode=v;refresh();}
 function fit(){const {w,h}=location();view=fitView(m.width,m.height,w,h);schedule();}
 function exact(){const {w,h}=location();view=nativeZoom(view,1,w/2,h/2,m.width,m.height,w,h);schedule();}
 function zoom(factor,pt){const {w,h}=location();view=nativeZoom(view,view.scale*factor,pt?.[0]??w/2,pt?.[1]??h/2,m.width,m.height,w,h);schedule();}
 function paint(target,s,feedback=false){
   // Strokes are replayed on the mask layer, not the source image. The backend
   // remains authoritative for exact pixel morphology and anti-aliasing.
   const r=Math.max(1,Math.round(s.radius*Math.min(m.width,m.height)));
   target.fillStyle=feedback?(s.mode==='add'?'rgb(0,235,174)':'rgb(255,126,66)'):
     (s.mode==='add'?'rgb(255,255,255)':'rgb(0,0,0)');
   target.strokeStyle=target.fillStyle;target.lineWidth=2*r;target.lineCap='round';target.lineJoin='round';
   target.beginPath();s.points.forEach(([u,v],i)=>{const x=u*(m.width-1),y=v*(m.height-1);if(!i)target.moveTo(x,y);else target.lineTo(x,y);});
   if(s.points.length>1)target.stroke();
   for(const [u,v] of s.points){target.beginPath();target.arc(u*(m.width-1),v*(m.height-1),r,0,Math.PI*2);target.fill();}
 }
 function render(){
   scheduled=false;if(closed||!view)return;
   const {w,h}=location(),rx=screen.width/w,ry=screen.height/h;
   ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,screen.width,screen.height);
   ctx.imageSmoothingEnabled=view.scale<1;ctx.setTransform(rx*view.scale,0,0,ry*view.scale,rx*view.x,ry*view.y);
   ctx.drawImage(source,0,0,m.width,m.height);ctx.setTransform(1,0,0,1,0,0);
   if(mask){
     const key=`${current}/${dirtyRevision}/${view.scale}/${view.x}/${view.y}/${screen.width}/${screen.height}`;
     if(maskCacheKey!==key){
       maskCtx.setTransform(1,0,0,1,0,0);maskCtx.clearRect(0,0,maskCanvas.width,maskCanvas.height);
       maskCtx.imageSmoothingEnabled=view.scale<1;
       maskCtx.setTransform(rx*view.scale,0,0,ry*view.scale,rx*view.x,ry*view.y);
       maskCtx.drawImage(mask,0,0,m.width,m.height);
       for(const s of undo)if(s.object===current)paint(maskCtx,s);
       maskCtx.setTransform(1,0,0,1,0,0);
       const data=maskCtx.getImageData(0,0,maskCanvas.width,maskCanvas.height),px=data.data;
       const ww=maskCanvas.width,hh=maskCanvas.height,selected=new Uint8Array(ww*hh);
       for(let k=0;k<selected.length;k++)selected[k]=px[k*4+3]&&px[k*4]>=128?1:0;
       for(let y=0;y<hh;y++)for(let x=0;x<ww;x++){
         const k=y*ww+x,j=k*4,on=selected[k];
         const edge=(x>0&&on!==selected[k-1])||(x<ww-1&&on!==selected[k+1])||
                    (y>0&&on!==selected[k-ww])||(y<hh-1&&on!==selected[k+ww]);
         px[j]=edge?15:234;px[j+1]=edge?250:40;px[j+2]=edge?255:179;px[j+3]=edge?240:on?88:0;
       }
       maskCtx.putImageData(data,0,0);maskCacheKey=key;
     }
     ctx.drawImage(maskCanvas,0,0);
     if(active&&active.object===current){
       ctx.save();ctx.setTransform(rx*view.scale,0,0,ry*view.scale,rx*view.x,ry*view.y);
       ctx.globalAlpha=.72;
       // This is live guidance only. Exact alpha is recalculated in Python.
       paint(ctx,active,true);ctx.restore();
     }
   }
   ctx.font='bold 11px system-ui';
   for(const [i,p] of m.objects[current].points.entries()){
     const x=(p.x+.5)*view.scale+view.x,y=(p.y+.5)*view.scale+view.y;
     if(x<0||y<0||x>w||y>h)continue;
     ctx.strokeStyle='#ffe476';ctx.lineWidth=2;ctx.beginPath();ctx.arc(x*rx,y*ry,9,0,2*Math.PI);ctx.stroke();
     ctx.fillStyle='#242424';ctx.fillRect(x*rx+9,y*ry-11,19,18);
     ctx.fillStyle='#ffe476';ctx.fillText(String(i+1),x*rx+13,y*ry+3);
   }
   zoomLabel.textContent=`Zoom ${Math.round(view.scale*100)} % ${view.scale>=1?'· pixels natifs':'· vue réduite'}`;
 }
 function schedule(){if(closed||scheduled)return;scheduled=true;requestAnimationFrame(render);}
 function resize(){const {w,h}=location(),dpr=Math.min(1.5,Math.max(1,window.devicePixelRatio||1));
   screen.width=Math.min(1600,Math.max(1,Math.round(w*dpr)));screen.height=Math.min(1100,Math.max(1,Math.round(h*dpr)));
   maskCanvas.width=screen.width;maskCanvas.height=screen.height;maskCacheKey=null;
   view=view?clampView(view,m.width,m.height,w,h):fitView(m.width,m.height,w,h);schedule();
 }
 function updateAlerts(){
   alerts.replaceChildren();const points=m.objects[current].points;
   if(!points.length)alerts.append(E('span','Aucune alerte localisée ; vérifier néanmoins la silhouette complète.'));
   points.forEach((spot,i)=>alerts.append(B(`${i+1}. ${spot.type}`,()=>{
      const {w,h}=location();view=nativeZoom(view,2,w/2,h/2,m.width,m.height,w,h);
      view=centerOn(view,spot.x,spot.y,m.width,m.height,w,h);
      status.textContent=spot.detail+(dirtyRevision?' · alerte antérieure aux retouches':'');schedule();
   })));
 }
 async function loadMask(index){
   const token=++loading;mask=null;maskCacheKey=null;current=index;status.textContent='Chargement du masque natif…';updateAlerts();schedule();
   try{const im=await fetchImage(m.masks[index]);if(closed||token!==loading)return;
     if(im.naturalWidth!==m.width||im.naturalHeight!==m.height)throw Error('Taille de masque incorrecte');
     mask=im;maskCacheKey=null;status.textContent=`Sujet ${index+1} : source native, ${m.objects[index].alertes.length} alerte(s)`;refresh();schedule();
   }catch(e){if(!closed&&token===loading){status.textContent=e.message;refresh();schedule();}}
 }
 const minus=B('− Zoom',()=>zoom(1/1.4)),plus=B('+ Zoom',()=>zoom(1.4)),real=B('100 % natif',exact),adapt=B('Adapter',fit);
 tools.append(E('span','Sujet'),choose,add,erase,move,E('span','Pinceau'),range,rlabel,back,forward);
 nav.append(minus,plus,real,adapt,zoomLabel,coordinates);
 const save=B('Enregistrer les retouches',()=>{
   const before=field.value;
   try{if(active)throw Error('Terminer le tracé en cours');
     if(!mask)throw Error('Masque natif indisponible : impossible de confirmer les retouches');
     const json=serialize(m,undo);field.value=json;field.callback?.(json);
     node._ss2110Draft=null;
     app.graph?.change?.();node.setDirtyCanvas?.(true,true);close();
   }catch(e){field.value=before;status.textContent=e.message;}
 });
 const captureDraft=()=>{
   if(closed||!dirtyRevision)return;
   try{node._ss2110Draft={source:m.source,text:serialize(m,undo)};}
   catch(e){node._ss2110DraftError=String(e.message||e);}
 };
 node._ss2110CaptureDraft=captureDraft;
 const close=()=>{
   if(closed)return;closed=true;loading++;observer?.disconnect?.();root.remove();
   if(node._ss2110CaptureDraft===captureDraft)node._ss2110CaptureDraft=null;
   root.removeEventListener?.('keydown',onKey);
   if(node._ss2110Close===close)node._ss2110Close=null;
   node._ss2110Open=false;node._ss2110Button.disabled=!node._ss2110Meta;node._ss2110Button.focus?.();
 };
 // Escape/backdrop require a second deliberate action when edits are unsaved.
 const askClose=()=>{
   if(dirtyRevision&&typeof window.confirm==='function'&&!window.confirm('Abandonner les retouches non enregistrées ?'))return;
   if(dirtyRevision&&typeof window.confirm!=='function'){status.textContent='Retouches non enregistrées : utiliser le bouton Fermer sans sauvegarder.';return;}
   node._ss2110Draft=null;
   close();
 };
 const end=B('Fermer sans sauvegarder',()=>{node._ss2110Draft=null;close();}),actions=E('div',undefined,'ss2110-row');actions.append(save,end);
 const hint=E('div','Molette : zoom · Espace + glisser ou Déplacer : navigation · Ctrl+Z : annuler · Ctrl+Maj+Z : rétablir · Escape : fermer. Les alertes seront recalculées après relance.','ss2110-note');
 const onKey=e=>{
   if(e.key==='Escape'){e.preventDefault();askClose();return;}
   if(['INPUT','TEXTAREA','SELECT'].includes(e.target?.tagName?.toUpperCase?.()))return;
   if(e.code==='Space'){space=true;refresh();e.preventDefault();}
   if((e.ctrlKey||e.metaKey)&&e.key?.toLowerCase()==='z'){e.preventDefault();e.shiftKey?forward.click():back.click();}
   if((e.ctrlKey||e.metaKey)&&e.key?.toLowerCase()==='y'){e.preventDefault();forward.click();}
 };
 root.addEventListener('keydown',onKey);
 root.addEventListener('keyup',e=>{if(e.code==='Space'){space=false;refresh();}});
 root.addEventListener('pointerdown',e=>{if(e.target===root)askClose();});
 choose.addEventListener('change',()=>{active=null;void loadMask(Number(choose.value));});
 viewport.addEventListener('wheel',e=>{zoom(Math.exp(-Math.max(-250,Math.min(250,e.deltaY||0))/500),local(e));e.preventDefault?.();},{passive:false});
 viewport.addEventListener('pointerdown',e=>{
   if(!mask||e.button!==0&&e.button!==1)return;
   if(mode==='pan'||space||e.button===1){pan={id:e.pointerId,x:e.clientX,y:e.clientY};viewport.setPointerCapture?.(e.pointerId);e.preventDefault?.();return;}
   if(undo.length>=LIMITS.strokes){status.textContent='400 traits maximum';return;}
   const [x,y]=local(e),p=positionUV(view,x,y,m.width,m.height);if(!p)return;
   active={pointerId:e.pointerId,object:current,mode,radius,points:[p]};viewport.setPointerCapture?.(e.pointerId);schedule();e.preventDefault?.();
 });
 viewport.addEventListener('pointermove',e=>{
   const [x,y]=local(e),pixel=sourceAt(view,x,y,m.width,m.height);
   coordinates.textContent=pixel?`Source : ${pixel[0]}, ${pixel[1]} px`:'Hors image';
   if(pan&&e.pointerId===pan.id){const f=location();view=clampView({...view,x:view.x+e.clientX-pan.x,y:view.y+e.clientY-pan.y},m.width,m.height,f.w,f.h);pan.x=e.clientX;pan.y=e.clientY;schedule();return;}
   if(!active||e.pointerId!==active.pointerId)return;
   const p=positionUV(view,x,y,m.width,m.height,true);if(!p)return;
   const last=active.points.at(-1),distance=Math.hypot((p[0]-last[0])*m.width*view.scale,(p[1]-last[1])*m.height*view.scale);
   if(distance>=1.2&&active.points.length<LIMITS.points){active.points.push(p);schedule();}
   else if(distance>=1.2&&active.points.length===LIMITS.points)status.textContent='Trait limité à 1 500 points ; relâcher puis reprendre le tracé';
 });
 function finish(e){
   if(pan&&e.pointerId===pan.id){pan=null;refresh();return;}
   if(!active||e.pointerId!==active.pointerId)return;
   const stroke=active;active=null;
   if(undo.reduce((n,s)=>n+s.points.length,0)+stroke.points.length>LIMITS.total)status.textContent='Maximum 12 000 points ; tracer moins de détails';
   else{undo.push(stroke);redo=[];dirtyRevision++;refresh();}
   schedule();
 }
 viewport.addEventListener('pointerup',finish);
 for(const name of ['pointercancel','lostpointercapture'])viewport.addEventListener(name,e=>{
   if(pan?.id===e.pointerId)pan=null;
   if(active?.pointerId===e.pointerId)active=null;refresh();schedule();
 });
 panel.append(title,tools,nav,viewport,alerts,status,quality,actions,footer,hint);root.append(panel);document.body.append(root);
 observer=typeof ResizeObserver==='function'?new ResizeObserver(resize):null;observer?.observe(viewport);
 resize();updateAlerts();refresh();void loadMask(0);choose.focus?.();
 node._ss2110Close=close;
}
app.registerExtension({name:EXT,nodeCreated(node){
 if(!CLASSES.has(node?.comfyClass||node?.type)||node._ss2110Hook||typeof node.addDOMWidget!=='function')return;
 style();node._ss2110Hook=true;node._ss2110Generation=0;
 const region=E('div',undefined,'ss2110-node'),note=E('div','Exécuter le nœud pour inspecter et modifier à la résolution native.');
 const button=B('Inspecter + corriger les contours',()=>{
   if(node._ss2110Open||!node._ss2110Meta)return;
   node._ss2110Open=true;button.disabled=true;const id=node._ss2110Generation;
   void open(node,node._ss2110Meta,id).catch(e=>{
     if(node._ss2110Generation!==id)return;
     node._ss2110Open=false;button.disabled=!node._ss2110Meta;note.textContent='Éditeur : '+e.message;
   });
 });button.disabled=true;node._ss2110Button=button;
 region.append(button,note);
 const widget=node.addDOMWidget('smartsvg_unified_v2110','smartsvg_unified',region,{serialize:false,hideOnZoom:true});
 if(widget){widget.serialize=false;widget.options={...(widget.options||{}),serialize:false};}
 node.size=[Math.max(node.size?.[0]||340,340),Math.max(node.size?.[1]||240,290)];
 const old=node.onExecuted;
 node.onExecuted=function(output){old?.apply(this,arguments);
   node._ss2110CaptureDraft?.();
   node._ss2110Generation++;node._ss2110Close?.();node._ss2110Open=false;
   const meta=validateUnified(output);node._ss2110Meta=meta;button.disabled=!meta;
   const draftKept=!!(node._ss2110Draft && meta && node._ss2110Draft.source===meta.source);
   if(node._ss2110Draft&&!draftKept)node._ss2110Draft=null;
   note.textContent=meta?`${meta.count} sujet(s) · ${meta.width} × ${meta.height} px · inspection + retouche au même endroit${draftKept?' · BROUILLON non sauvegardé récupérable':''}`:
     'Aucun aperçu disponible ; consulter le rapport du nœud.';
   node.setDirtyCanvas?.(true,true);
 };
 const removed=node.onRemoved;
 node.onRemoved=function(){node._ss2110Generation++;node._ss2110Close?.();node._ss2110Draft=null;node._ss2110Meta=null;return removed?.apply(this,arguments);};
}});
