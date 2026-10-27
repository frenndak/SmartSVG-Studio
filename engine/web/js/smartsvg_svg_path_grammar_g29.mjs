/** G2.9: a bounded SVG-path grammar check for candidate Basic Cut contours.
 * This deliberately rejects malformed commands and unclosed/degenerate loops.
 * It is NOT a computational-geometry validator or physical Cricut proof.
 */
const LEX=/[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?/y;
const SPACE=/^[\s,]*/;
const PARAMS=Object.freeze({M:2,L:2,H:1,V:1,C:6,S:4,Q:4,T:2,A:7,Z:0});
const MAX_TOKENS=50000;
const LIMIT=1e6;

export class SvgPathSyntaxError extends Error{
  constructor(code){super(code);this.name='SvgPathSyntaxError';this.code=code;}
}
const fail=code=>{throw new SvgPathSyntaxError(code);};
const isCommand=token=>typeof token==='string'&&token.length===1&&
  Object.hasOwn(PARAMS,token.toUpperCase());

function tokensOf(d){
  if(typeof d!=='string'||d.length===0||d.length>150000)fail('UNSUPPORTED_PATH');
  const out=[];
  let offset=0;
  while(offset<d.length){
    const skip=SPACE.exec(d.slice(offset))[0].length;
    offset+=skip;
    if(offset===d.length)break;
    LEX.lastIndex=offset;
    const m=LEX.exec(d);
    if(!m||m.index!==offset)fail('UNSUPPORTED_PATH');
    const text=m[0];
    if(!isCommand(text) && (!Number.isFinite(Number(text))||Math.abs(Number(text))>LIMIT))
      fail('INVALID_PATH_COORDINATE');
    out.push(text);
    if(out.length>MAX_TOKENS)fail('UNSUPPORTED_PATH');
    offset=LEX.lastIndex;
  }
  return out;
}

export function inspectSvgPathGrammar(d){
  const ts=tokensOf(d);
  if(!ts.length||ts[0]!=='M'&&ts[0]!=='m')fail('OPEN_OR_EMPTY_CONTOUR');
  let i=0,x=0,y=0,sx=0,sy=0;
  let pathOpen=false,segmentCount=0,closed=0,totalSegments=0;
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  let allMinX=Infinity,allMaxX=-Infinity,allMinY=Infinity,allMaxY=-Infinity;
  let polyArea=0,onlyLines=true,needsReview=false;
  const mark=(px,py)=>{
    minX=Math.min(minX,px);maxX=Math.max(maxX,px);
    minY=Math.min(minY,py);maxY=Math.max(maxY,py);
  };
  const addPoint=(px,py,polygon=true)=>{
    if(polygon&&onlyLines)polyArea+=x*py-px*y;
    x=px;y=py;mark(x,y);
  };
  while(i<ts.length){
    const command=ts[i++];
    if(!isCommand(command))fail('INVALID_PATH_GRAMMAR');
    const kind=command.toUpperCase(),relative=command!==kind;
    if(kind==='Z'){
      if(!pathOpen||segmentCount===0)fail('OPEN_OR_EMPTY_CONTOUR');
      if(onlyLines)polyArea+=x*sy-sx*y;
      if(!(maxX-minX>1e-7&&maxY-minY>1e-7)||
         (onlyLines&&Math.abs(polyArea)<1e-7))
        fail('DEGENERATE_CUT_PATH');
      closed++;
      allMinX=Math.min(allMinX,minX);allMaxX=Math.max(allMaxX,maxX);
      allMinY=Math.min(allMinY,minY);allMaxY=Math.max(allMaxY,maxY);
      // Every subpath requires its own non-degenerate bounds.
      minX=Infinity;maxX=-Infinity;minY=Infinity;maxY=-Infinity;
      x=sx;y=sy;pathOpen=false;segmentCount=0;onlyLines=true;polyArea=0;
      continue;
    }
    if(!pathOpen&&kind!=='M')fail('OPEN_OR_EMPTY_CONTOUR');
    if(kind==='M'&&pathOpen)fail('OPEN_OR_EMPTY_CONTOUR');
    const n=PARAMS[kind];
    let groups=0,mode=kind;
    while(i<ts.length&&!isCommand(ts[i])){
      if(i+n>ts.length||ts.slice(i,i+n).some(isCommand))
        fail('INVALID_PATH_GRAMMAR');
      const a=ts.slice(i,i+n).map(Number);
      if(a.some(v=>!Number.isFinite(v)||Math.abs(v)>LIMIT))
        fail('INVALID_PATH_COORDINATE');
      i+=n;groups++;
      if(kind==='M'&&groups===1){
        sx=relative?x+a[0]:a[0];
        sy=relative?y+a[1]:a[1];
        x=sx;y=sy;mark(x,y);
        pathOpen=true;
        continue;
      }
      // Additional pairs after M are implicit L commands.
      const type=kind==='M'?'L':mode;
      const oldX=x,oldY=y;
      if(type==='A'){
        if(a[0]<0||a[1]<0||!Number.isFinite(a[2])||
           (a[3]!==0&&a[3]!==1)||(a[4]!==0&&a[4]!==1))
          fail('INVALID_PATH_GRAMMAR');
        needsReview=true;onlyLines=false;
      } else if(!['L','H','V'].includes(type)){
        needsReview=true;onlyLines=false;
      }
      if(type==='H'){
        addPoint(relative?x+a[0]:a[0],y);
      }else if(type==='V'){
        addPoint(x,relative?y+a[0]:a[0]);
      }else{
        const j=a.length-2;
        const nx=relative?x+a[j]:a[j],ny=relative?y+a[j+1]:a[j+1];
        if(type==='C'||type==='S'||type==='Q'){
          for(let index=0;index<j;index+=2){
            mark(relative?oldX+a[index]:a[index],
                 relative?oldY+a[index+1]:a[index+1]);
          }
        }
        if(type==='A'){
          // Arcs can protrude beyond endpoints; full extrema require
          // geometric analysis. Export remains a human-review draft.
          mark(nx,ny);
        }
        addPoint(nx,ny,type==='L');
      }
      segmentCount++;totalSegments++;
      if(totalSegments>MAX_TOKENS)fail('UNSUPPORTED_PATH');
      if(!Number.isFinite(x)||!Number.isFinite(y)||
         Math.abs(x)>LIMIT||Math.abs(y)>LIMIT)fail('INVALID_PATH_COORDINATE');
    }
    if(groups===0)fail('INVALID_PATH_GRAMMAR');
  }
  if(pathOpen||closed===0)fail('OPEN_OR_EMPTY_CONTOUR');
  return Object.freeze({
    subpaths:closed,segments:totalSegments,needsReview,
    bounds:Object.freeze([allMinX,allMinY,allMaxX,allMaxY])
  });
}
