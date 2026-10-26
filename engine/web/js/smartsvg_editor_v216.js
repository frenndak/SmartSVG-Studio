/** SmartSVG Studio V21.6.1: deterministic mask editor with a bounded pan/zoom viewport.
 * All editing occurs in source-normalized coordinates; viewport zoom NEVER changes
 * replay resolution or the serialized V21.6 stroke JSON format.
 */
import { app } from '../../scripts/app.js';
import { api } from '../../scripts/api.js';
import { validatedFocus, centerFocusView } from './smartsvg_mask_focus_v21156.mjs';
import { normalizeMeta, previewUrl, encodeDocument, decodeDocument, LIMITS, fitView,
  constrainView, zoomView, moveView, viewToUV, strokeSpacing } from './smartsvg_editor_model_v216.mjs';

const EXT_NAME='smartsvg.studio.v216.mask_editor';
const CLASS='SmartSVGMaskEditorV216';
function el(tag,text,cls){
  const n=document.createElement(tag);
  if(text!==undefined && text!==null)n.textContent=String(text);
  if(cls)n.className=cls;
  return n;
}
function btn(text,callback){
  const n=el('button',text);n.type='button';n.addEventListener('click',callback);return n;
}
function css(){
  if(document.getElementById('smartsvg216-css'))return;
  const node=el('style');node.id='smartsvg216-css';node.textContent=`
  .ss216-summary{padding:9px;border:1px solid #4c5b69;border-radius:9px;background:#222831;color:#e5edf5;font:12px system-ui;min-width:300px}
  .ss216-summary button,.ss216-modal button,.ss216-modal select {border:1px solid #64748b;border-radius:6px;background:#354054;color:white;padding:7px;cursor:pointer;font:12px system-ui}
  .ss216-summary button:disabled,.ss216-modal button:disabled{opacity:.4;cursor:not-allowed}
  .ss216-modal{position:fixed;inset:0;z-index:2147482000;background:rgba(0,0,0,.85);display:flex;justify-content:center;align-items:center;padding:12px}
  .ss216-editor{background:#202630;color:#fff;display:flex;flex-direction:column;gap:8px;padding:14px;border:1px solid #596477;border-radius:12px;box-shadow:0 10px 30px #0008;max-height:96vh;width:min(1100px,96vw);box-sizing:border-box;overflow:auto;font:13px system-ui}
  .ss216-controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  .ss216-controls label{display:flex;gap:6px;align-items:center}
  .ss216-editor button.active{background:#245a83;border-color:#6dc7ff}
  .ss216-viewport{position:relative;flex-shrink:0;overflow:hidden;touch-action:none;user-select:none;cursor:crosshair;background:repeating-conic-gradient(#ddd 0% 25%,#bbb 0% 50%) 50%/20px 20px;border:1px solid #77818b;width:100%;height:clamp(210px,58vh,670px);box-sizing:border-box;outline-offset:2px}
  .ss216-viewport:focus-visible{outline:2px solid #a4caff}
  .ss216-viewport canvas{position:absolute;max-width:none;max-height:none;pointer-events:none;display:block;transform:none;image-rendering:auto}
  .ss216-note{font-size:12px;color:#d6dce7}
  .ss216-modal :focus-visible{outline:2px solid #a4caff;outline-offset:2px}
  @media(max-height:620px){.ss216-viewport{height:45vh;min-height:170px}}
  `;document.head.appendChild(node);
}
function safeURL(ref){return previewUrl(ref,window.location.href,api.apiURL('/view'));}
function load(ref){return new Promise((resolve,reject)=>{
  const url=safeURL(ref);
  if(!url){reject(new Error('Référence de miniature invalide'));return;}
  const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>reject(new Error('Miniature expirée ou indisponible'));
  img.src=url;
});}
function cloneStrokes(items){return items.map(s=>({...s,points:s.points.map(p=>[...p])}));}

async function openEditor(node,meta,focus=null){
  const jsonWidget=(node.widgets||[]).find(w=>w.name==='retouches_json');
  if(!jsonWidget)throw new Error('Widget retouches_json introuvable. Installer le nœud V21.6.');
  const saved=decodeDocument(meta,String(jsonWidget.value||''));
  const baseImage=await load(meta.image);
  css();
  const backdrop=el('div',null,'ss216-modal');
  const panel=el('div',null,'ss216-editor');
  panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');
  panel.setAttribute('aria-label','Éditeur de masques SmartSVG');
  const title=el('strong',`SmartSVG V21.6.1 · ${meta.count} sujet(s)`);
  const controls=el('div',null,'ss216-controls');
  const select=el('select');select.setAttribute('aria-label','Choisir le masque');
  for(let i=0;i<meta.count;i++){const o=el('option',`Sujet ${i+1}`);o.value=String(i);select.appendChild(o);}
  let current=focus?focus.subject-1:0,mode=focus?'pan':'add',radius=.015,history=cloneStrokes(saved),redo=[];
  select.value=String(current);
  let active=null,activePan=null,spaceDown=false,loadedObject=-1,maskLoadToken=0;
  let maskMessage='',revision=0,cacheRevision=-1,cacheObject=-1;
  let destroyed=false;
  const modeAdd=btn('+ Ajouter',()=>setMode('add'));
  const modeErase=btn('− Retirer',()=>setMode('erase'));
  const modePan=btn('✋ Déplacer',()=>setMode('pan'));
  const slider=el('input');slider.type='range';slider.min='0.002';slider.max='0.1';slider.step='0.001';slider.value=String(radius);
  const sliderText=el('span','1,5 %');
  const label=el('label','Pinceau');label.append(slider,sliderText);
  const undo=btn('↶ Annuler',()=>performUndo());
  const again=btn('↷ Rétablir',()=>performRedo());
  const status=el('div','', 'ss216-note');
  const coordinates=el('span','Position : —','ss216-note');
  select.addEventListener('change',()=>{current=Number(select.value);active=null;void loadMask(current);});
  slider.addEventListener('input',()=>{radius=Number(slider.value);sliderText.textContent=(radius*100).toFixed(1).replace('.',',')+' %';});
  controls.append(el('span','Sujet'),select,modeAdd,modeErase,modePan,label,undo,again);

  const toolbar=el('div',null,'ss216-controls');
  const zoomOut=btn('− Zoom',()=>changeZoom(1/1.35));
  const zoomIn=btn('+ Zoom',()=>changeZoom(1.35));
  const zoomFit=btn('Adapter',()=>resetView());
  const zoomActual=btn('100 %',()=>setZoomTo(1));
  const zoomText=el('strong','100 %');
  toolbar.append(zoomOut,zoomIn,zoomFit,zoomActual,zoomText,coordinates);

  const viewport=el('div',null,'ss216-viewport');
  viewport.tabIndex=0;
  viewport.setAttribute('role','application');
  viewport.setAttribute('aria-label','Aperçu du masque. Molette pour zoomer, mode Déplacer ou Espace pour déplacer; +, −, 0 pour le zoom.');
  const canvas=el('canvas');canvas.width=meta.preview_width;canvas.height=meta.preview_height;
  viewport.appendChild(canvas);
  const ctx=canvas.getContext('2d');
  if(!ctx)throw new Error('Canvas 2D indisponible');
  const baseLayer=el('canvas');baseLayer.width=canvas.width;baseLayer.height=canvas.height;
  const baseCtx=baseLayer.getContext('2d',{willReadFrequently:true});
  const cached=el('canvas');cached.width=canvas.width;cached.height=canvas.height;
  const cachedCtx=cached.getContext('2d');
  const live=el('canvas');live.width=canvas.width;live.height=canvas.height;
  const liveCtx=live.getContext('2d');
  if(!baseCtx||!cachedCtx||!liveCtx)throw new Error('Canvas auxiliaire indisponible');
  let view={scale:1,x:0,y:0};
  const frame=()=>{const r=viewport.getBoundingClientRect();return {width:Math.max(1,r.width),height:Math.max(1,r.height)};};
  function applyView(){
    const f=frame();view=constrainView(view,canvas.width,canvas.height,f.width,f.height);
    canvas.style.left=`${view.x}px`;canvas.style.top=`${view.y}px`;
    canvas.style.width=`${canvas.width*view.scale}px`;canvas.style.height=`${canvas.height*view.scale}px`;
    canvas.style.imageRendering=view.scale>=3?'pixelated':'auto';
    zoomText.textContent=`Zoom ${Math.round(view.scale*100)} % (aperçu ${canvas.width} × ${canvas.height})`;
  }
  function resetView(){const f=frame();view=fitView(canvas.width,canvas.height,f.width,f.height);applyView();}
  function setZoomTo(scale,anchor){
    const f=frame();view=zoomView(view,scale,anchor?.[0]??f.width/2,anchor?.[1]??f.height/2,
      canvas.width,canvas.height,f.width,f.height);applyView();
  }
  function changeZoom(factor,anchor){setZoomTo(view.scale*factor,anchor);}
  function pan(deltaX,deltaY){const f=frame();view=moveView(view,deltaX,deltaY,canvas.width,canvas.height,f.width,f.height);applyView();}
  const local=event=>{const r=viewport.getBoundingClientRect();return [event.clientX-r.left,event.clientY-r.top];};
  function position(event,clamp=false){const [x,y]=local(event);return viewToUV(view,x,y,canvas.width,canvas.height,clamp);}
  function updatePosition(event){
    const p=position(event);coordinates.textContent=p?
      `Source : ${Math.round(p[0]*(meta.width-1))}, ${Math.round(p[1]*(meta.height-1))} px`:'Position : hors image';
  }
  function setMode(next){mode=next;refreshControls();}
  function performUndo(){if(history.length){redo.push(history.pop());revision++;render();}}
  function performRedo(){if(redo.length){history.push(redo.pop());revision++;render();}}
  function refreshControls(){
    modeAdd.classList.toggle('active',mode==='add');modeErase.classList.toggle('active',mode==='erase');modePan.classList.toggle('active',mode==='pan');
    undo.disabled=!history.length;again.disabled=!redo.length;
    viewport.style.cursor=loadedObject!==current?'not-allowed':(activePan||spaceDown||mode==='pan'?'grab':'crosshair');
    status.textContent=maskMessage||`${history.length} trait(s) · sujet ${current+1}/${meta.count} · zoom sur aperçu uniquement · export pleine résolution`;
  }
  function paintStroke(draw,s){
    const r=Math.max(1,s.radius*Math.min(canvas.width,canvas.height));
    draw.save();draw.globalCompositeOperation=s.mode==='erase'?'destination-out':'source-over';
    draw.strokeStyle=s.mode==='erase'?'#000':'rgba(226,40,198,.58)';draw.fillStyle=draw.strokeStyle;
    draw.lineWidth=2*r;draw.lineCap='round';draw.lineJoin='round';
    draw.beginPath();s.points.forEach(([x,y],i)=>{const X=x*(canvas.width-1),Y=y*(canvas.height-1);if(!i)draw.moveTo(X,Y);else draw.lineTo(X,Y);});
    if(s.points.length>1)draw.stroke();
    for(const [x,y] of s.points){draw.beginPath();draw.arc(x*(canvas.width-1),y*(canvas.height-1),r,0,Math.PI*2);draw.fill();}
    draw.restore();
  }
  function render(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.drawImage(baseImage,0,0,canvas.width,canvas.height);
    if(loadedObject===current){
      if(cacheObject!==current||cacheRevision!==revision){
        cachedCtx.clearRect(0,0,canvas.width,canvas.height);
        cachedCtx.drawImage(baseLayer,0,0);
        for(const s of history)if(s.object===current)paintStroke(cachedCtx,s);
        cacheRevision=revision;cacheObject=current;
      }
      if(active&&active.object===current){
        liveCtx.clearRect(0,0,canvas.width,canvas.height);
        liveCtx.drawImage(cached,0,0);
        paintStroke(liveCtx,active);
        ctx.drawImage(live,0,0);
      }else ctx.drawImage(cached,0,0);
    }
    refreshControls();
  }
  async function loadMask(index){
    const token=++maskLoadToken;loadedObject=-1;maskMessage='Chargement du masque…';render();
    try{
      const img=await load(meta.masks[index]);
      if(token!==maskLoadToken||destroyed)return;
      baseCtx.clearRect(0,0,canvas.width,canvas.height);
      baseCtx.drawImage(img,0,0,canvas.width,canvas.height);
      const data=baseCtx.getImageData(0,0,canvas.width,canvas.height);
      for(let k=0;k<data.data.length;k+=4){
        const opacity=data.data[k]/255;
        data.data[k]=226;data.data[k+1]=40;data.data[k+2]=198;data.data[k+3]=Math.round(opacity*148);
      }
      baseCtx.putImageData(data,0,0);
      loadedObject=index;maskMessage='';cacheObject=-1;render();
    }catch(error){if(token===maskLoadToken&&!destroyed){maskMessage=error.message;render();}}
  }
  const buttons=el('div',null,'ss216-controls');
  const close=()=>{
    if(destroyed)return;destroyed=true;maskLoadToken++;
    document.removeEventListener('keydown',keyHandler,true);
    document.removeEventListener('keyup',keyUpHandler,true);
    resizeObserver?.disconnect?.();backdrop.remove();
    node._smartsvgV216ModalOpen=false;
    if(node._smartsvgV216Editor){
      node._smartsvgV216Editor.trigger.disabled=!node._smartsvgV216Meta;
      node._smartsvgV216Editor.focusTrigger.disabled=!validatedFocus(node._smartsvgV216Editor.getFocus(),node._smartsvgV216Meta);
    }
  };
  const closeButton=btn('Fermer sans enregistrer',close);
  const save=btn('Enregistrer les retouches',()=>{
    try{
      if(active)throw new Error('Terminer le coup de pinceau avant de sauvegarder');
      const value=encodeDocument(meta,history);
      jsonWidget.value=value;jsonWidget.callback?.(value);
      app.graph?.change?.();node.setDirtyCanvas?.(true,true);
      close();
    }catch(error){maskMessage=error.message;refreshControls();}
  });
  buttons.append(save,closeButton);
  const hint=el('div',focus ? 'Zone proposée : vérifier visuellement le masque et choisir explicitement Ajouter ou Retirer. Annuler/Rétablir restent disponibles ; aucune correction automatique.' : 'Molette / boutons : zoom · Déplacer ou maintenir Espace + glisser : navigation · +, −, 0 : zoom · Ctrl+Z / Ctrl+Maj+Z : annuler/rétablir. Les contours sont calculés à la résolution originale après Enregistrer puis relancer.','ss216-note');
  panel.append(title,controls,toolbar,viewport,status,buttons,hint);backdrop.appendChild(panel);
  backdrop.addEventListener('pointerdown',e=>{if(e.target===backdrop)close();});
  panel.addEventListener('pointerdown',e=>e.stopPropagation());
  document.body.appendChild(backdrop);
  resetView();
  if(focus){
    try{
      const f=frame();
      const suggested=centerFocusView(focus.box,meta.width,meta.height,canvas.width,canvas.height,f.width,f.height);
      view=constrainView(suggested,canvas.width,canvas.height,f.width,f.height);
      applyView();
      maskMessage='Zone du sujet '+focus.subject+' centrée. Vérifier le dessin puis choisir Ajouter ou Retirer. Rien n’a été modifié.';
      render();
    }catch(e){maskMessage='Cadrage impossible : '+e.message;render();}
  }
  select.focus?.();
  function keyHandler(e){
    if(destroyed)return;
    if(e.key==='Escape'){e.preventDefault();e.stopPropagation();close();return;}
    const field=['INPUT','TEXTAREA','SELECT'].includes(String(e.target?.tagName||'').toUpperCase());
    if(field)return;
    if(e.code==='Space'||e.key===' '){spaceDown=true;refreshControls();e.preventDefault();return;}
    if((e.ctrlKey||e.metaKey)&&e.key?.toLowerCase()==='z'){
      e.preventDefault();e.stopPropagation();e.shiftKey?performRedo():performUndo();return;
    }
    if((e.ctrlKey||e.metaKey)&&e.key?.toLowerCase()==='y'){
      e.preventDefault();e.stopPropagation();performRedo();return;
    }
    if(!e.ctrlKey&&!e.metaKey&&!e.altKey){
      if(e.key==='+'||e.key==='='){changeZoom(1.35);e.preventDefault();}
      else if(e.key==='-'){changeZoom(1/1.35);e.preventDefault();}
      else if(e.key==='0'){resetView();e.preventDefault();}
    }
  }
  function keyUpHandler(e){if(e.code==='Space'||e.key===' '){spaceDown=false;refreshControls();}}
  document.addEventListener('keydown',keyHandler,true);
  document.addEventListener('keyup',keyUpHandler,true);
  viewport.addEventListener('wheel',e=>{
    if(destroyed)return;
    const delta=Math.max(-240,Math.min(240,e.deltaY||0));
    const factor=Math.exp(-delta/480);
    changeZoom(factor,local(e));e.preventDefault?.();
  },{passive:false});
  viewport.addEventListener('pointerdown',e=>{
    if(loadedObject!==current||destroyed)return;
    const isPan=mode==='pan'||spaceDown||e.button===1;
    if(e.button!==0&&e.button!==1)return;
    if(isPan){
      activePan={pointerId:e.pointerId,lastX:e.clientX,lastY:e.clientY};
      viewport.setPointerCapture?.(e.pointerId);viewport.style.cursor='grabbing';e.preventDefault?.();return;
    }
    if(history.length>=LIMITS.strokes){maskMessage='400 traits au maximum : annuler ou simplifier';refreshControls();return;}
    const p=position(e);if(!p)return;
    active={pointerId:e.pointerId,object:current,mode,radius,points:[p]};
    viewport.setPointerCapture?.(e.pointerId);e.preventDefault?.();render();
  });
  viewport.addEventListener('pointermove',e=>{
    if(activePan){
      if(e.pointerId!==activePan.pointerId)return;
      pan(e.clientX-activePan.lastX,e.clientY-activePan.lastY);
      activePan.lastX=e.clientX;activePan.lastY=e.clientY;e.preventDefault?.();return;
    }
    updatePosition(e);
    if(!active||e.pointerId!==active.pointerId)return;
    const p=position(e,true);if(!p)return;
    const last=active.points[active.points.length-1];
    const distance=Math.hypot((p[0]-last[0])*canvas.width,(p[1]-last[1])*canvas.height);
    if(distance>=strokeSpacing(view.scale)&&active.points.length<LIMITS.points){active.points.push(p);render();}
    e.preventDefault?.();
  });
  function finish(e){
    if(activePan&&e.pointerId===activePan.pointerId){activePan=null;refreshControls();e.preventDefault?.();return;}
    if(!active||e.pointerId!==active.pointerId)return;
    const stroke=active;active=null;
    if(history.reduce((n,s)=>n+s.points.length,0)+stroke.points.length>LIMITS.total){
      maskMessage='12000 points maximum : annuler ou simplifier le dessin';render();return;
    }
    history.push(stroke);redo=[];revision++;maskMessage='';render();e.preventDefault?.();
  }
  viewport.addEventListener('pointerup',finish);
  viewport.addEventListener('pointercancel',e=>{
    if(active&&e.pointerId===active.pointerId)active=null;
    if(activePan&&e.pointerId===activePan.pointerId)activePan=null;
    render();
  });
  // Keep the image centered or clamped when the Comfy panel size changes.
  const resizeObserver=typeof ResizeObserver!=='undefined'?new ResizeObserver(()=>{
    if(destroyed)return;
    const f=frame();view=constrainView(view,canvas.width,canvas.height,f.width,f.height);applyView();
  }):null;
  resizeObserver?.observe?.(viewport);
  void loadMask(current);
}

app.registerExtension({
  name:EXT_NAME,
  nodeCreated(node){
    if((node?.comfyClass||node?.type)!==CLASS||node._smartsvgV216Editor||typeof node.addDOMWidget!=='function')return;
    try{
      css();const region=el('div',null,'ss216-summary');region.setAttribute('role','region');region.setAttribute('aria-label','Retouches SmartSVG');
      const note=el('div','Exécuter une première fois pour charger les masques à modifier.');
      let pendingFocus=null;
      const focusTrigger=btn('Examiner la zone signalée (aucune retouche automatique)',()=>{
        const valid=validatedFocus(pendingFocus,node._smartsvgV216Meta);
        if(!valid||node._smartsvgV216ModalOpen){focusTrigger.disabled=true;return;}
        if(typeof window.confirm==='function'&&!window.confirm('Ouvrir le sujet '+valid.subject+' ? Vérifiez que l’image et les masques sont les bons. Aucune correction automatique.'))return;
        node._smartsvgV216ModalOpen=true;trigger.disabled=true;focusTrigger.disabled=true;
        void openEditor(node,node._smartsvgV216Meta,valid).catch(e=>{
          node._smartsvgV216ModalOpen=false;trigger.disabled=!node._smartsvgV216Meta;
          focusTrigger.disabled=false;note.textContent='Zone non ouverte : '+e.message;
        });
      });
      focusTrigger.disabled=true;
      const focusListener=event=>{
        const incoming=validatedFocus(event?.detail,node._smartsvgV216Meta);
        if(!incoming)return;
        pendingFocus=event.detail;
        focusTrigger.disabled=!!node._smartsvgV216ModalOpen;
        note.textContent='Zone du sujet '+incoming.subject+' reçue pour cette image et ces masques. Confirmez avant ouverture.';
      };
      window.addEventListener('smartsvg:mask-focus:v1',focusListener);
      const trigger=btn('Ouvrir l’éditeur de masques',()=>{
        if(!node._smartsvgV216Meta||node._smartsvgV216ModalOpen)return;
        node._smartsvgV216ModalOpen=true;trigger.disabled=true;
        void openEditor(node,node._smartsvgV216Meta).catch(e=>{
          node._smartsvgV216ModalOpen=false;trigger.disabled=!node._smartsvgV216Meta;
          note.textContent='Éditeur indisponible : '+e.message;
        });
      });trigger.disabled=true;
      const reset=btn('Effacer les retouches enregistrées',()=>{
        const field=(node.widgets||[]).find(w=>w.name==='retouches_json');
        if(!field)return;
        if(typeof window.confirm==='function'&&!window.confirm('Effacer toutes les retouches de ce nœud ?'))return;
        field.value='';field.callback?.('');app.graph?.change?.();node.setDirtyCanvas?.(true,true);
        note.textContent='Retouches effacées. Relancer le workflow pour charger la nouvelle image.';
      });
      region.append(trigger,focusTrigger,reset,note);
      const w=node.addDOMWidget('smartsvg_editor_v216','smartsvg_editor',region,{
        serialize:false,hideOnZoom:true,getMinHeight:()=>85,getMaxHeight:()=>115
      });
      if(w){w.serialize=false;w.options={...(w.options||{}),serialize:false};}
      node._smartsvgV216Editor={region,trigger,note,focusTrigger,getFocus:()=>pendingFocus};
      const oldRemoval=node.onRemoved;
      node.onRemoved=function(){window.removeEventListener('smartsvg:mask-focus:v1',focusListener);oldRemoval?.apply(this,arguments);};
      const original=node.onExecuted;
      node.onExecuted=function(output){
        original?.apply(this,arguments);
        const meta=normalizeMeta(output);node._smartsvgV216Meta=meta;
        if(!validatedFocus(pendingFocus,meta))pendingFocus=null;
        focusTrigger.disabled=!pendingFocus||!!node._smartsvgV216ModalOpen;
        trigger.disabled=!meta||!!node._smartsvgV216ModalOpen;
        note.textContent=meta?`${meta.count} sujet(s) chargés · ${meta.width} × ${meta.height} px. Zoom/déplacement et retouches disponibles.`:
          'Aucun aperçu valide : consulter le résultat Python et relancer.';
        node.setDirtyCanvas?.(true,true);
      };
      node.size=[Math.max(node.size?.[0]||350,350),Math.max(node.size?.[1]||230,315)];
    }catch(e){console.warn('SmartSVG V21.6.1 mask editor disabled',e);}
  }
});
