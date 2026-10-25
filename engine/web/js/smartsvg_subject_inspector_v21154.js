/** V21.15.5: locate suspicious components; diagnostics only, no mask mutations. */
import {app} from '../../scripts/app.js';
const CLASS='SmartSVGChooseSubjectV21154';
const LABELS=Object.freeze({
  MASQUE_VIDE:'Masque vide',
  FRAGMENTS_DETACHES:'Fragments détachés',
  MICRO_FRAGMENTS:'Petits îlots à examiner',
  TOUCHE_BORD_IMAGE:'Touche un bord de l’image',
  SILHOUETTE_RECTANGULAIRE:'Contour presque rectangulaire',
  SUJET_TRES_PETIT:'Sujet très petit',
});
const element=(tag,content)=>{
  const e=document.createElement(tag);
  if(content!==undefined)e.textContent=String(content);
  return e;
};
const validPreview=value=>typeof value==='string'&&value.length<700000&&
  /^data:image\/png;base64,[A-Za-z0-9+/]+={0,2}$/.test(value);
const validZone=zone=>{
  const coords=zone?.bbox_apercu_88px;
  const src=zone?.bbox_source_px;
  return (zone?.type==='MICRO_FRAGMENT'||zone?.type==='FRAGMENT_SEPARE')&&
    Array.isArray(coords)&&coords.length===4&&coords.every(n=>Number.isInteger(n)&&n>=0&&n<=88)&&
    coords[2]>=coords[0]&&coords[3]>=coords[1]&&
    Array.isArray(src)&&src.length===4&&src.every(n=>Number.isInteger(n)&&n>=0)&&
    src[2]>src[0]&&src[3]>src[1];
};
const makePreview=(item,zones)=>{
  const preview=element('span');
  preview.style.cssText='display:inline-block;position:relative;width:76px;height:76px;flex-shrink:0';
  const img=element('img');img.width=76;img.height=76;
  img.style.cssText='object-fit:contain;width:76px;height:76px;max-width:100%';
  img.src=item.image_data;img.alt='Aperçu du sujet '+item.numero;
  preview.append(img);
  for(const zone of zones){
    const b=zone.bbox_apercu_88px;
    const ring=element('span');
    const left=Math.max(0,Math.min(73,b[0]*76/88));
    const top=Math.max(0,Math.min(73,b[1]*76/88));
    const width=Math.min(76-left,Math.max(3,(b[2]-b[0])*76/88));
    const height=Math.min(76-top,Math.max(3,(b[3]-b[1])*76/88));
    ring.style.cssText=['position:absolute','pointer-events:none',
      'left:'+left+'px','top:'+top+'px','width:'+width+'px','height:'+height+'px',
      'outline:2px solid #ffce73','background:rgba(255,174,0,.17)','box-sizing:border-box'].join(';');
    ring.setAttribute('aria-hidden','true');
    preview.append(ring);
  }
  return preview;
};

function inspector(node){
 const root=element('section');
 root.style.cssText='padding:10px;color:#edf2f7;background:#1c2731;border:1px solid #53687a;border-radius:9px;font:13px system-ui;max-height:320px;overflow-y:auto';
 const title=element('strong','Inspection des silhouettes');
 const hint=element('p','Exécuter le nœud puis choisir une vignette. Rien n’est découpé automatiquement.');
 hint.setAttribute('role','status');hint.setAttribute('aria-live','polite');
 const summary=element('p','Aucune analyse disponible.');
 const layout=element('div');
 layout.style.cssText='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px';
 root.append(title,hint,summary,layout);
 function update(data){
   layout.replaceChildren();
   const entry=data?.smartsvg_subjects_v21154?.[0];
   if(!entry||!Array.isArray(entry.sujets)){
     summary.textContent='Aucun diagnostic disponible : utilisez la sélection numérique.';
     hint.textContent='La sélection et le calcul restent disponibles sans cet inspecteur.';
     return;
   }
   const selected=entry.selection;
   let issues=0, shown=0;
   for(const item of entry.sujets.slice(0,32)){
     if(!Number.isInteger(item.numero)||item.numero<1||item.numero>32)continue;
     const warnings=Array.isArray(item.codes)?item.codes.filter(code=>Object.hasOwn(LABELS,code)).slice(0,5):[];
     const zones=Array.isArray(item.zones_a_examiner)?item.zones_a_examiner.filter(validZone).slice(0,12):[];
     const hidden=Number.isInteger(item.zones_non_affichees)&&item.zones_non_affichees>=0?
       Math.min(item.zones_non_affichees,1000000):0;
     if(warnings.length||zones.length||hidden)issues++;
     const canSelect=validPreview(item.image_data) && !warnings.includes('MASQUE_VIDE');
     const button=element('button');button.type='button';
     button.style.cssText='background:#293a48;color:#fff;border:2px solid #607689;border-radius:7px;padding:5px;cursor:pointer;min-height:138px;display:flex;flex-direction:column;align-items:center;gap:4px;';
     const name=element('strong','Sujet '+item.numero);
     const message=warnings.length ? warnings.map(w=>LABELS[w]).join(' · ') : 'Inspection visuelle requise';
     const detail=element('span',message);
     detail.style.cssText='font-size:11px;text-align:center;';
     const locations=zones.slice(0,3).map(z=>{
       const b=z.bbox_source_px;
       return (z.type==='MICRO_FRAGMENT'?'Micro-îlot':'Fragment séparé')+' : x'+b[0]+'–'+b[2]+', y'+b[1]+'–'+b[3];
     });
     const extra=zones.length-Math.min(3,zones.length)+hidden;
     const focus=element('span',locations.join(' · ')+(extra>0?' · +'+extra+' autre(s) zone(s)':''));
     focus.style.cssText='font-size:10px;overflow-wrap:anywhere;text-align:center';
     if(canSelect)button.append(makePreview(item,zones),name,detail,focus);
     else button.append(name,element('span','Aucun aperçu exploitable'),detail,focus);
     button.setAttribute('aria-label','Sujet '+item.numero+' : '+message+'. '+(zones.length+hidden)+
       ' zone(s) localisée(s) à inspecter. '+locations.join('; ')+'. '+
       (canSelect?'Cliquer pour choisir et relancer.':'Non sélectionnable ici.'));
     button.setAttribute('aria-pressed',String(item.numero===selected));
     if(item.numero===selected)button.style.borderColor='#82d8bc';
     if(warnings.length||zones.length)button.style.borderStyle='dashed';
     if(!canSelect){button.disabled=true;button.style.opacity='.65';}
     else button.addEventListener('click',()=>{
       const widget=node.widgets?.find(w=>w.name==='numero_sujet');
       if(!widget){hint.textContent='Champ numero_sujet introuvable : choisir manuellement.';return;}
       widget.value=item.numero;
       for(const b of layout.children){
         b.setAttribute('aria-pressed',String(b===button));
         b.style.borderColor=b===button?'#82d8bc':'#607689';
       }
       hint.textContent=`Sujet ${item.numero} choisi. Relancer le workflow pour appliquer la sélection ; corriger les fragments dans l’éditeur de masques si nécessaire.`;
       node.setDirtyCanvas?.(true,true);
       node.graph?.setDirtyCanvas?.(true,true);
     });
     layout.append(button);shown++;
   }
   summary.textContent=`${shown} sujet(s) affiché(s), ${issues} à examiner. Cadres orange = fragments possibles, jamais supprimés. Aucune validation de découpe.`;
   hint.textContent='Cliquer un sujet puis relancer. Un avertissement demande inspection, pas suppression automatique.';
 }
 return {root,update};
}
app.registerExtension({name:'smartsvg.studio.subjectinspector.v21154',nodeCreated(node){
 if((node?.comfyClass||node?.type)!==CLASS||node._ss21154Inspector||typeof node.addDOMWidget!=='function')return;
 try{
   const ui=inspector(node);
   node.addDOMWidget('smartsvg_subject_inspector_v21154','smartsvg_inspector',ui.root,
     {serialize:false,hideOnZoom:true,getMinHeight:()=>200,getMaxHeight:()=>380});
   node._ss21154Inspector=ui;
   const previous=node.onExecuted;
   node.onExecuted=function(out){previous?.apply(this,arguments);try{ui.update(out);}catch(error){console.warn('SmartSVG inspection advisory',error);}};
   node.size=[Math.max(node.size?.[0]||300,430),Math.max(node.size?.[1]||200,470)];
 }catch(error){console.warn('SmartSVG subject inspector disabled',error);}
}});
