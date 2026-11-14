#!/usr/bin/env python3
"""Private GlyphgroveDeparture experiment from a pinned DeparturePixelZh build."""
import argparse, copy, hashlib, json, tempfile
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.cu2quPen import Cu2QuPen
import font_mixed_support as mixed
import font_ops as ops
import pathops

ROOT = Path(__file__).resolve().parents[1]

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def font_names(font, family, style, weight, italic):
    styleps = style.replace(' ', '')
    ps = family + '-' + styleps
    names = font['name']
    for n in (1,2,3,4,5,6,8,10,16,17,25): names.removeNames(nameID=n)
    for platform, enc, lang in ((3,1,0x409),(1,0,0)):
        for n, value in {1:family,2:style,3:'0.1;private;'+ps,4:family+' '+style,5:'Version 0.1',6:ps,8:'Glyphgrove private experiment',10:'Experimental styles derived from DeparturePixelZh Compact',16:family,17:style}.items():
            names.setName(value,n,platform,enc,lang)
    font['OS/2'].usWeightClass=weight
    font['OS/2'].fsSelection=(font['OS/2'].fsSelection & ~0x61) | (0x20 if weight==700 else 0) | (1 if italic else 0) | (0x40 if weight==400 and not italic else 0)
    font['head'].macStyle=(1 if weight==700 else 0) | (2 if italic else 0)
    font['post'].italicAngle=-9.09 if italic else 0
    return ps

def styled_text(source, cmap_roles, bold, italic, cfg):
    font=copy.deepcopy(source); glyphs=source.getGlyphSet(); cmap=source.getBestCmap()
    selected={cmap[cp] for cp,role in cmap_roles.items() if role in ('departure','cubic') and cp in cmap}
    icon_names={cmap[cp] for cp,role in cmap_roles.items() if role=='nerd' and cp in cmap}
    selected-=icon_names
    original=dict(font['hmtx'].metrics)
    if bold or italic:
        for index,name in enumerate(sorted(selected)):
            obj=source['glyf'][name]
            if obj.numberOfContours==0:continue
            path=pathops.Path(); glyphs[name].draw(path.getPen())
            if not path.verbs:continue
            if bold:
                stroke=pathops.Path();stroke.addPath(path);stroke.stroke(cfg['boldStroke'],pathops.LineCap.BUTT_CAP,pathops.LineJoin.MITER_JOIN,4)
                path=pathops.op(path,stroke,pathops.PathOp.UNION)
            pen=TTGlyphPen(None); q=Cu2QuPen(pen,max_err=1,reverse_direction=False)
            path.draw(TransformPen(q,(1,0,cfg['italicShear'],1,0,0)) if italic else q)
            g=pen.glyph();g.recalcBounds(font['glyf']);font['glyf'][name]=g
            oldadv,_=original[name];font['hmtx'].metrics[name]=(oldadv,getattr(g,'xMin',0))
            if index and index%5000==0:print('styled glyphs',index,flush=True)
    if any(font['hmtx'].metrics[name][0]!=metric[0] for name,metric in original.items()):raise ValueError('Advance changed')
    return font

def main():
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--coverage',type=Path,required=True);p.add_argument('--emoji',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    cfg=json.loads((ROOT/'departure-recipe.json').read_text())
    for path,key in [(a.base,'baseSha256'),(a.coverage,'coverageSha256'),(a.emoji,'emojiSha256')]:
        if digest(path)!=cfg[key]:raise ValueError('Input hash mismatch: '+str(path))
    coverage={int(k[2:],16):v for k,v in json.loads(a.coverage.read_text()).items()};base=TTFont(a.base,recalcTimestamp=False)
    a.output.mkdir(parents=True,exist_ok=False); report={'recipe':cfg,'assets':[]}
    for style in cfg['styles']:
        print('building',style['style'],flush=True)
        text=styled_text(base,coverage,style['bold'],style['italic'],cfg)
        with tempfile.TemporaryDirectory(prefix='.work-',dir=a.output) as temp:
            font, em=mixed.with_emoji(text,a.emoji,cfg['emojiPpem'],Path(temp))
        ops.finalize_layout(font);ops.symbol_aliases(font,{'EA00':'F099'})
        for name in em['mapping'].values():
            adv,lsb=font['hmtx'].metrics[name]
            if adv:font['hmtx'].metrics[name]=(cfg['hanCell'],lsb)
        ps=font_names(font,cfg['family'],style['style'],style['weight'],style['italic']);font.recalcTimestamp=False
        path=a.output/(ps+'.ttf');font.save(path);report['assets'].append({'file':path.name,'sha256':digest(path),'bytes':path.stat().st_size,'style':style['style'],'weight':style['weight']})
        print('saved',path.name,flush=True)
    (a.output/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
