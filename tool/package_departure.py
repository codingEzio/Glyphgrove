#!/usr/bin/env python3
"""Export the GlyphgroveDeparture experiment as private Desktop and Web kits."""
import argparse,hashlib,json,shutil,zipfile
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ranges(points):
    points=sorted(points);chunks=[];start=last=points[0]
    for cp in points[1:]:
        if cp==last+1:last=cp;continue
        chunks.append(f'U+{start:04X}' if start==last else f'U+{start:04X}-{last:04X}');start=last=cp
    chunks.append(f'U+{start:04X}' if start==last else f'U+{start:04X}-{last:04X}')
    return ','.join(chunks)
def main():
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--departure-licenses',type=Path,required=True);p.add_argument('--emoji',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--reuse-web',type=Path,help='verified previous Web font cache');a=p.parse_args();cfg=json.loads((ROOT/'departure-recipe.json').read_text());report=json.loads((a.build/'build-report.json').read_text())
    if report['recipe']!=cfg or sha(a.emoji)!=cfg['emojiSha256']:raise ValueError('Input recipe or emoji mismatch')
    for item in report['assets']:
        if sha(a.build/item['file'])!=item['sha256']:raise ValueError('Input font mismatch')
    if a.output.exists():raise ValueError('Choose a new output directory')
    desktop=a.output/'Desktop';web=a.output/'Web';desktop.mkdir(parents=True);(web/'fonts').mkdir(parents=True)
    for dest in (desktop,web):
        shutil.copytree(a.departure_licenses,dest/'licenses'/'Departure')
        shutil.copyfile(ROOT/'licenses/Noto3D-OFL.txt',dest/'licenses'/'Noto3D-OFL.txt')
        (dest/'NOTICE.md').write_text('Private GlyphgroveDeparture experiment. DeparturePixelZh Compact 0.1.1 supplies Departure Mono, Cubic 11 and Nerd Fonts symbols; full Noto 3D Emoji is merged or separately bundled. The Compact source advances remain unchanged. Italic and bold are synthesized experimental styles, not upstream original designs. All component licenses and notices under licenses/ remain applicable. Do not publish or redistribute without separate rights review.\n')
    for item in report['assets']:shutil.copyfile(a.build/item['file'],desktop/item['file'])
    text='GlyphgroveDeparture: Regular, Italic, Bold and Bold Italic. Italic and bold are synthesized experimental styles. English and Chinese advances are unchanged from DeparturePixelZh Compact; complete Nerd and Noto 3D Emoji included. Private use; do not publish.\n'
    (desktop/'README.md').write_text(text)
    emoji=TTFont(a.emoji,recalcTimestamp=False);emoji_pts=set(emoji.getBestCmap())-set(range(128))
    if a.reuse_web:
        cached=TTFont(a.reuse_web/'fonts/Emoji3D.woff2')
        for tag in ('cmap','GSUB','sbix'):
            if cached.getTableData(tag)!=emoji.getTableData(tag):raise ValueError('Emoji cache changed: '+tag)
        shutil.copyfile(a.reuse_web/'fonts/Emoji3D.woff2',web/'fonts/Emoji3D.woff2')
    else:
        emoji.flavor='woff2';emoji.save(web/'fonts/Emoji3D.woff2')
    rules=[]
    for item in report['assets']:
        font=TTFont(a.build/item['file'],recalcTimestamp=False);del font['sbix'];name=item['file'].replace('.ttf','.woff2')
        if a.reuse_web:
            cached=TTFont(a.reuse_web/'fonts'/name)
            for tag in ('glyf','cmap','hmtx','name','GSUB','GPOS'):
                if cached.getTableData(tag)!=font.getTableData(tag):raise ValueError('Web cache changed: '+name+' / '+tag)
            shutil.copyfile(a.reuse_web/'fonts'/name,web/'fonts'/name)
        else:
            font.flavor='woff2';font.save(web/'fonts'/name)
        italic='italic' if 'Italic' in item['style'] else 'normal';weight=item['weight'];
        rules.append('@font-face { font-family: "GlyphgroveDeparture"; src: url("fonts/'+name+'") format("woff2"); font-style: '+italic+'; font-weight: '+str(weight)+'; font-display: swap; }')
    for italic in ('normal','italic'):
        for weight in (400,700):
            rules.append('@font-face { font-family: "GlyphgroveDeparture"; src: url("fonts/Emoji3D.woff2") format("woff2"); font-style: '+italic+'; font-weight: '+str(weight)+'; font-display: swap; unicode-range: '+ranges(emoji_pts)+'; }')
    rules.append('@font-face { font-family: "GlyphgroveDeparture Emoji"; src: url("fonts/Emoji3D.woff2") format("woff2"); font-style: normal; font-weight: 400; font-display: swap; }')
    rules += ['.glyphgrove-departure { font-family: "GlyphgroveDeparture", monospace; font-synthesis: none; }','.glyphgrove-departure-emoji { font-family: "GlyphgroveDeparture Emoji", "Apple Color Emoji", sans-serif; font-style: normal; font-weight: 400; }']
    (web/'fonts.css').write_text('\n\n'.join(rules)+'\n')
    (web/'README.md').write_text(text+'Load fonts.css, apply class glyphgrove-departure, and wrap keycap sequences with glyphgrove-departure-emoji. Emoji uses sbix; other platforms may fall back. Keep all notices and licenses.\n')
    (web/'example.html').write_text('''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>GlyphgroveDeparture</title><link rel="stylesheet" href="fonts.css"><style>body{margin:24px;font:16px/1.5 system-ui}h1{overflow-wrap:anywhere}p{font-size:24px;overflow-wrap:anywhere}</style><h1>GlyphgroveDeparture</h1><p class="glyphgrove-departure">Regular ABC 中文 012  <span class="glyphgrove-departure-emoji">😀 👩🏽‍💻 🇹🇼 1️⃣</span></p><p class="glyphgrove-departure"><i>Italic 斜體 ABC 中文</i></p><p class="glyphgrove-departure"><b>Bold 粗體 ABC 中文</b></p><p class="glyphgrove-departure"><b><i>Bold italic 粗斜 ABC 中文</i></b></p></html>''')
    for target in (desktop,web):
        (target/'README.zh-Hans.md').write_text('GlyphgroveDeparture 私人实验版，包含正常体、斜体、粗体与粗斜体。粗体和斜体为实验性合成样式，不是上游原生字形；英文字格和汉字字格保持 DeparturePixelZh Compact 原值。包含 Nerd 图标和完整 Noto 3D Emoji。不得公开或再分发；保留 licenses/ 和 NOTICE.md。Web 使用 fonts.css 与 glyphgrove-departure 类，数字键帽等完整序列使用 glyphgrove-departure-emoji 类。Emoji 使用 sbix，非 macOS 浏览器兼容性未验证。\n')
        (target/'README.zh-Hant.md').write_text('GlyphgroveDeparture 私人實驗版，包含正常體、斜體、粗體與粗斜體。粗體和斜體為實驗性合成樣式，不是上游原生字形；英文字格和漢字字格保持 DeparturePixelZh Compact 原值。包含 Nerd 圖示和完整 Noto 3D Emoji。不得公開或再散布；保留 licenses/ 和 NOTICE.md。Web 使用 fonts.css 與 glyphgrove-departure 類別，數字鍵帽等完整序列使用 glyphgrove-departure-emoji 類別。Emoji 使用 sbix，非 macOS 瀏覽器相容性未驗證。\n')
    for target in (desktop,web):
        files={str(f.relative_to(target)):{'sha256':sha(f),'bytes':f.stat().st_size} for f in sorted(target.rglob('*')) if f.is_file()};(target/'manifest.json').write_text(json.dumps({'family':cfg['family'],'recipe':cfg,'files':files},indent=2)+'\n')
        with zipfile.ZipFile(a.output/(target.name+'.zip'),'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for f in sorted(target.rglob('*')):
                if f.is_file():z.write(f,f.relative_to(target))
        with zipfile.ZipFile(a.output/(target.name+'.zip')) as z:
            for f in target.rglob('*'):
                if f.is_file() and hashlib.sha256(z.read(str(f.relative_to(target)))).hexdigest()!=sha(f):raise ValueError('ZIP readback mismatch')
    print(json.dumps({'output':str(a.output),'desktopBytes':(a.output/'Desktop.zip').stat().st_size,'webBytes':(a.output/'Web.zip').stat().st_size}))
if __name__=='__main__':main()
