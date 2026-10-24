/** V21.11.2: lightweight non-serialized result panel for the guided Cricut export.
 * This is advisory only. It cannot make a raster or a cutout valid.
 */
import {app} from '../../scripts/app.js';

const IDS=new Set(['SmartSVGAutoExpressV21112','SmartSVGAutoExpressV21122']);
const e=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);return n;};
function view(){
  const root=e('div');
  root.style.cssText='background:#1c2730;color:#edf3f9;border:1px solid #64788b;border-radius:9px;padding:11px;font:12px system-ui;min-width:310px;';
  const title=e('strong','SmartSVG · Mon sticker Cricut');
  const status=e('div','Importer → Détourer → Vérifier → Exporter');
  status.style.cssText='margin-top:8px;line-height:1.6;white-space:normal;';
  const next=e('div','Exécuter le nœud pour obtenir un résultat précontrôlé.');
  next.style.cssText='margin-top:6px;line-height:1.5;color:#d4e6f4;white-space:normal;';
  const warning=e('div','Design Space et découpe physique non encore vérifiés.');
  warning.style.cssText='margin-top:6px;color:#e5cf9f;';
  root.append(title,status,next,warning);
  return {root,update(output){
    const item=output?.smartsvg_steps_v21112?.[0];
    if(!item||typeof item!=='object'){
      status.textContent='Aucun nouveau résultat valide.';
      next.textContent='Consulter la console ComfyUI et le rapport du nœud. Ne pas utiliser un ancien aperçu comme preuve de succès.';
      return;
    }
    const count=Number.isSafeInteger(item.sujets)&&item.sujets>=0?item.sujets:0;
    const cards=Number.isSafeInteger(item.cartes)&&item.cartes>=0?item.cartes:0;
    if(item.statut==='CONTROLE_LOCAL_OK_VERIFICATION_VISUELLE'){
      status.textContent=`${count} silhouette(s) précontrôlée(s) localement · inspection visuelle requise`;
    }else if(item.statut==='CARTE_RECTANGULAIRE'){
      status.textContent=`${cards} carte(s) rectangulaire(s) · pas un détourage de personnage`;
    }else{
      status.textContent='Correction ou vérification nécessaire avant la découpe';
    }
    next.textContent=typeof item.action==='string'?item.action:'Consulter le rapport JSON.';
  }};
}
app.registerExtension({name:'smartsvg.studio.v21112.steps',nodeCreated(node){
  if(!IDS.has(node?.comfyClass||node?.type)||node._ss21112Guide||typeof node.addDOMWidget!=='function')return;
  const pane=view();
  try{
    const widget=node.addDOMWidget('smartsvg_steps_v21112','smartsvg_guide',pane.root,
      {serialize:false,hideOnZoom:true,getMinHeight:()=>135,getMaxHeight:()=>170});
    if(widget){widget.serialize=false;widget.options={...(widget.options||{}),serialize:false};}
    node._ss21112Guide=pane;
    const previous=node.onExecuted;
    node.onExecuted=function(output){previous?.apply(this,arguments);try{pane.update(output);}catch(err){console.warn('SmartSVG Guide',err);}};
    node.size=[Math.max(node.size?.[0]||350,370),Math.max(node.size?.[1]||300,460)];
  }catch(err){console.warn('SmartSVG guided panel disabled, Python node remains available',err);}
}});
