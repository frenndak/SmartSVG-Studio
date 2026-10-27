/** G2.7: a local SVG contour workbench inside the existing Express project UI.
 * No server upload, no hidden ComfyUI queue and no untrusted SVG DOM insertion.
 */
import {inspectCutSvg,selectedSvg,REVIEW_MESSAGES,MAX_SVG_BYTES}
  from './smartsvg_cut_review_model_g27.mjs';

const element=(tag,text)=>{
  const e=document.createElement(tag);
  if(text!==undefined)e.textContent=String(text);
  return e;
};
const button=(title,handler)=>{
  const b=element('button',title);b.type='button';b.addEventListener('click',handler);
  return b;
};

export function createCutReviewPanel(ownerId='default'){
  const root=element('section');
  root.setAttribute('aria-label','Aperçu et choix manuel des chemins de découpe');
  root.className='details';
  const title=element('strong','5 · Contrôler les contours SVG');
  const help=element('p','Charger un SVG de contours déjà exporté. Choisir les sujets à garder puis télécharger un brouillon SVG. L’aperçu n’exécute pas de découpe et ne certifie pas Cricut.');
  help.className='fine';
  const label=element('label','SVG de contours à examiner');
  const input=element('input');input.type='file';input.accept='.svg,image/svg+xml';
  input.id='smartsvg-g27-svg-'+String(ownerId).replace(/[^a-zA-Z0-9_-]/g,'').slice(0,30);
  label.setAttribute('for',input.id);
  const status=element('p','Aucun SVG chargé.');
  status.setAttribute('role','status');status.setAttribute('aria-live','polite');
  const canvas=element('canvas');
  canvas.width=720;canvas.height=420;
  canvas.style.width='100%';canvas.style.height='auto';
  canvas.style.maxHeight='300px';canvas.style.background='#ffffff';
  canvas.style.borderRadius='6px';
  canvas.setAttribute('role','img');
  canvas.setAttribute('aria-label','Aperçu non certifié des chemins de découpe SVG');
  canvas.hidden=true;
  const selectors=element('div');
  selectors.setAttribute('role','group');
  selectors.setAttribute('aria-label','Choisir les contours individuels');
  const actions=element('div');actions.className='toolbar';
  const all=button('Tout sélectionner',()=>{if(!review)return;selected=new Set(review.paths.map(p=>p.index));paint();});
  const none=button('Tout désélectionner',()=>{selected.clear();paint();});
  const download=button('Télécharger les contours sélectionnés (brouillon)',()=>{
    if(!review||selected.size===0)return;
    try{
      const result=selectedSvg(review,[...selected].sort((a,b)=>a-b));
      const blob=new Blob([result],{type:'image/svg+xml;charset=utf-8'});
      const url=URL.createObjectURL(blob);
      try{
        const a=element('a');a.href=url;a.download='smartsvg-contours-selection-brouillon.svg';
        a.click();
        status.textContent='Brouillon téléchargé : vérifier dans Design Space les dimensions et les contours avant toute découpe.';
      }finally{
        // Allow the browser to complete its download before releasing the blob.
        setTimeout(()=>URL.revokeObjectURL(url),1500);
      }
    }catch(err){status.textContent=REVIEW_MESSAGES[err?.code]||'Export local impossible.';}
  });
  actions.append(all,none,download);
  all.disabled=none.disabled=download.disabled=true;
  root.append(title,help,label,input,status,canvas,selectors,actions);
  let review=null,selected=new Set(),paths=[],transform=null,reading=0;
  const clear=()=>{
    review=null;selected=new Set();paths=[];transform=null;
    selectors.replaceChildren();
    canvas.hidden=true;
    all.disabled=none.disabled=download.disabled=true;
  };
  const updateStatus=()=>{
    status.textContent=review?
      String(selected.size)+'/'+String(review.paths.length)+' contour(s) sélectionné(s) · '+
      String(review.width_mm)+' × '+String(review.height_mm)+
      ' mm · aperçu indicatif, aucune certification de découpe.'
      :'Aucun SVG chargé.';
  };
  function paint(){
    updateStatus();
    all.disabled=none.disabled=!review;
    download.disabled=!review||selected.size===0;
    if(!review)return;
    selectors.replaceChildren();
    for(const item of review.paths){
      const row=element('label');
      row.style.cssText='display:flex;align-items:center;gap:7px;padding:4px;min-height:32px';
      const check=element('input');check.type='checkbox';check.checked=selected.has(item.index);
      check.addEventListener('change',()=>{
        if(check.checked)selected.add(item.index);else selected.delete(item.index);
        paint();
      });
      const caption=element('span','Sujet '+item.index+' · '+item.id);
      row.append(check,caption);
      selectors.appendChild(row);
    }
    try{
      const context=canvas.getContext?.('2d');
      if(!context||typeof Path2D==='undefined')throw Error('CANVAS_UNAVAILABLE');
      const [x,y,w,h]=review.viewBox;
      const s=Math.min((canvas.width-48)/w,(canvas.height-48)/h);
      if(!Number.isFinite(s)||s<=0)throw Error('CANVAS_UNAVAILABLE');
      const offsetX=(canvas.width-w*s)/2,offsetY=(canvas.height-h*s)/2;
      context.setTransform(1,0,0,1,0,0);
      context.clearRect(0,0,canvas.width,canvas.height);
      context.fillStyle='#ffffff';context.fillRect(0,0,canvas.width,canvas.height);
      context.setTransform(s,0,0,s,offsetX-x*s,offsetY-y*s);
      context.lineJoin='round';context.lineCap='round';
      context.lineWidth=2/s;
      paths=review.paths.map(item=>new Path2D(item.d));
      for(let i=0;i<paths.length;i++){
        context.strokeStyle=selected.has(i+1)?'#0078bc':'#a1a1aa';
        context.stroke(paths[i]);
      }
      transform={scale:s,tx:offsetX-x*s,ty:offsetY-y*s};
      canvas.hidden=false;
    }catch{
      canvas.hidden=true;transform=null;
      status.textContent+=' Prévisualisation graphique indisponible ici ; la liste reste utilisable.';
    }
  }
  input.addEventListener('change',async()=>{
    const request=++reading;
    clear();
    const file=input.files?.[0];
    if(!file){status.textContent='Aucun SVG chargé.';return;}
    if(!/\.svg$/i.test(file.name)||file.size>MAX_SVG_BYTES||file.size<20){
      status.textContent='Choisir un fichier .svg de moins de 768 Ko.';return;
    }
    status.textContent='Lecture locale et vérification du SVG…';
    try{
      const text=await file.text();
      if(request!==reading)return;  // prevent a stale read replacing the new file
      review=inspectCutSvg(text);
      selected=new Set(review.paths.map(p=>p.index));
      paint();
    }catch(err){
      if(request!==reading)return;
      clear();
      status.textContent=REVIEW_MESSAGES[err?.code]||
        'Le SVG ne peut pas être inspecté : vérifier les contours et le format.';
    }
  });
  canvas.addEventListener('click',event=>{
    if(!review||!transform||canvas.hidden)return;
    const box=canvas.getBoundingClientRect();
    if(box.width<=0||box.height<=0)return;
    const x=((event.clientX-box.left)*(canvas.width/box.width)-transform.tx)/transform.scale;
    const y=((event.clientY-box.top)*(canvas.height/box.height)-transform.ty)/transform.scale;
    const ctx=canvas.getContext('2d');
    for(let i=paths.length-1;i>=0;i--){
      if(ctx.isPointInStroke?.(paths[i],x,y)||ctx.isPointInPath?.(paths[i],x,y)){
        if(selected.has(i+1))selected.delete(i+1);else selected.add(i+1);
        paint();return;
      }
    }
  });
  return root;
}
