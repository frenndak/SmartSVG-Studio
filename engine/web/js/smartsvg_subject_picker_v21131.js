/** V21.13.1: subject thumbnails are optional advisory UI, never SVG manufacture. */
import {app} from '../../scripts/app.js';
const NAME='SmartSVGChooseSubjectV21131';
const elt=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);return n;};
function picker(node){
 const root=elt('div');root.style.cssText='padding:8px;color:#e7edf5;background:#1c2731;border-radius:10px;font:12px system-ui;max-height:225px;overflow:auto;';
 const title=elt('strong','Choisir un personnage');const hint=elt('p','Exécuter une fois, cliquer une vignette puis relancer. Le clic ne découpe rien.');
 const layout=elt('div');layout.style.cssText='display:grid;grid-template-columns:repeat(4,1fr);gap:5px;';
 root.append(title,hint,layout);
 return {root,update(data){
   layout.replaceChildren();
   const entry=data?.smartsvg_subjects_v21131?.[0];
   if(!entry||!Array.isArray(entry.sujets)){hint.textContent='Aucun aperçu disponible. Utiliser le numéro de sujet.';return;}
   hint.textContent='Cliquer pour choisir, puis relancer le workflow. Aucun export automatique.';
   for(const item of entry.sujets.slice(0,32)){
     if(!Number.isInteger(item.numero)||item.numero<1||item.numero>32||typeof item.image_data!=='string'||!item.image_data.startsWith('data:image/png;base64,'))continue;
     const b=elt('button');b.type='button';b.style.cssText='cursor:pointer;background:#253544;color:white;border:1px solid #5c758b;padding:3px;border-radius:5px;';
     const im=elt('img');im.src=item.image_data;im.width=72;im.height=72;im.alt='Sujet '+item.numero;
     const label=elt('span','#'+item.numero);b.append(im,label);
     if(item.numero===entry.selection)b.style.borderColor='#73ccba';
     b.addEventListener('click',()=>{
       const widget=node.widgets?.find(w=>w.name==='numero_sujet');
       if(!widget){hint.textContent='Champ numéro_sujet introuvable ; choisir manuellement.';return;}
       widget.value=item.numero;
       hint.textContent='Sujet '+item.numero+' sélectionné. Relancer le workflow pour fabriquer.';
       node.setDirtyCanvas?.(true,true);
       node.graph?.setDirtyCanvas?.(true,true);
     });layout.append(b);
   }
 }};
}
app.registerExtension({name:'smartsvg.studio.subjectpicker.v21131',nodeCreated(node){
 if((node?.comfyClass||node?.type)!==NAME||node._ss21131Picker||typeof node.addDOMWidget!=='function')return;
 try{
  const ui=picker(node);
  node.addDOMWidget('smartsvg_subject_picker_v21131','smartsvg_picker',ui.root,{serialize:false,hideOnZoom:true,getMinHeight:()=>160,getMaxHeight:()=>250});
  node._ss21131Picker=ui;
  const prev=node.onExecuted;
  node.onExecuted=function(out){prev?.apply(this,arguments);try{ui.update(out);}catch(err){console.warn('SmartSVG subject picker',err);}};
  node.size=[Math.max(node.size?.[0]||300,395),Math.max(node.size?.[1]||200,400)];
 }catch(err){console.warn('Optional SmartSVG picker disabled',err);}
}});
