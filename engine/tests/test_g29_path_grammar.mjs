import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectSvgPathGrammar} from '../web/js/smartsvg_svg_path_grammar_g29.mjs';
import {inspectCutSvg,selectedSvg,CutReviewError}
  from '../web/js/smartsvg_cut_review_model_g27.mjs';

const NS='http://www.w3.org/2000/svg';
const svg=(d,w='40mm',vb='0 0 40 20')=>'<svg xmlns="'+NS+
  '" width="'+w+'" height="20mm" viewBox="'+vb+
  '"><path id="sujet" d="'+d+'"/></svg>';
function parseSvg(src){
  const parseAttributes=raw=>[...raw.matchAll(/([\w:-]+)="([^"]*)"/g)]
    .map(m=>({name:m[1],value:m[2],namespaceURI:m[1]==='xmlns'?
      'http://www.w3.org/2000/xmlns/':null}));
  const rootAttrs=parseAttributes(src.match(/<svg\s+([^>]+)>/)?.[1]||'');
  const body=[...src.matchAll(/<path\s+([^>]+)\/>/g)].map(match=>{
    const attributes=parseAttributes(match[1]);
    return {namespaceURI:NS,localName:'path',attributes,
      getAttribute:k=>attributes.find(a=>a.name===k)?.value??null};
  });
  return {documentElement:{namespaceURI:NS,localName:'svg',
    attributes:rootAttrs,getElementsByTagName:()=>body,
    getAttribute:k=>rootAttrs.find(a=>a.name===k)?.value??null}};
}
const inspect=s=>inspectCutSvg(s,{parseXml:parseSvg});

test('real closed polygon, relative commands, smooth curves and arcs parse',()=>{
  const cases=[
    ['M1 1L10 1L10 10Z',false,1],
    ['M1,1 h9 v9 z',false,1],
    ['M1 1 C1 4 4 9 10 1 Z',true,1],
    ['M1 1 Q5 10 10 1 L10 10Z',true,1],
    ['M1 1 A5 4 0 0 1 10 10L1 10Z',true,1],
    ['M1 1L10 1L10 10ZM20 2L30 2L30 12Z',false,2],
  ];
  for(const [path,needsReview,subpaths] of cases){
    const r=inspectSvgPathGrammar(path);
    assert.equal(r.subpaths,subpaths,path);
    assert.equal(r.needsReview,needsReview,path);
    assert.ok(r.segments>=1);
  }
});

test('rejects false closure, missing parameters, empty, degenerate or open paths',()=>{
  const bad=[
    'M1 1L10 1L10 10Z L1 5Z',
    'M1 1L10 1L10 10ZM20 2L30 2',
    'M1 1L10 1L10Z',
    'M1 1L10 1L10 10',
    'M1 1L10 1L10 10ZL2 2Z',
    'M0 0L10 0Z',
    'M0 0L10 0L10 0Z',
    'M0 0L1 1L2 2Z',
    'M0 0C0 0 0 0 0 0Z',
    'M1 1C1 1 5 5 10 10Z', // Bezier controls all on one diagonal
    'M1 1Q5 5 10 10Z',  // quadratic curve is actually a line
    'M0 0L10 0L10 10ZM3 3C3 3 3 3 3 3Z',
    'M0 0A4 4 0 2 0 5 5Z',
    'M0 0A4 4 0 0 3 5 5Z',
    'M0 0C1 1 2 2Z',
    'M0 0 Q1 1 2 Z',
    'M0 0L10 0M10 10L0 10Z',
    'M0 0L1e999 2Z',
    'M0 0L10 0L10 10Z ;',
    'M0 0L10 0L10 10Z0',
  ];
  for(const d of bad)assert.throws(()=>inspectSvgPathGrammar(d),undefined,d);
});

test('rejects a path outside artboard instead of silently exporting clipped image',()=>{
  assert.throws(()=>inspect(svg('M30 1L50 1L50 10Z')),e=>
    e instanceof CutReviewError&&e.code==='PATH_OUTSIDE_VIEWBOX');
  assert.throws(()=>inspect(svg('M1 1L10 1L10 10Z','40px')),CutReviewError);
  assert.equal(inspect(svg('M1 1L10 1L10 10Z')).paths.length,1);
});

test('selected SVG also validates path grammar independently of inspector',()=>{
  const review=inspect(svg('M1 1L10 1L10 10Z'));
  const exported=selectedSvg(review,[1]);
  assert.match(exported,/width="40mm"/);
  assert.match(exported,/d="M1 1L10 1L10 10Z"/);
  const poisoned={...review,paths:[{d:'M1 1L10 1ZL20 20Z'}]};
  assert.throws(()=>selectedSvg(poisoned,[1]),CutReviewError);
  const clipped={...review,paths:[{d:'M30 1L50 1L50 10Z'}]};
  assert.throws(()=>selectedSvg(clipped,[1]),e=>
    e instanceof CutReviewError&&e.code==='PATH_OUTSIDE_VIEWBOX');
});

test('inspection remains a candidate review, not a physical cut proof',()=>{
  const out=inspect(svg('M1 1C1 4 4 9 10 1Z'));
  assert.equal(out.verified,false);
  assert.equal(out.source,'local_manual_svg');
});
