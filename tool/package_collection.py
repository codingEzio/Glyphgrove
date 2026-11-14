#!/usr/bin/env python3
"""Collect checked private Glyphgrove Pixel and Departure kits."""
import argparse, hashlib, json, shutil, zipfile
from pathlib import Path

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--pixel-build',required=True,type=Path);p.add_argument('--pixel-web',required=True,type=Path);p.add_argument('--departure',required=True,type=Path);p.add_argument('--licenses',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    report=json.loads((a.pixel_build/'build-report.json').read_text())
    if len(report['assets'])!=2:raise ValueError('Pixel requires regular and italic')
    for item in report['assets']:
        if sha(a.pixel_build/item['file'])!=item['sha256']:raise ValueError('Pixel build hash mismatch')
    for name in ('Desktop.zip','Web.zip'):
        with zipfile.ZipFile(a.departure/name) as z:
            if z.testzip():raise ValueError('Departure package damaged: '+name)
    with zipfile.ZipFile(a.pixel_web) as z:
        if z.testzip():raise ValueError('Pixel web package damaged')
        manifest=json.loads(z.read('manifest.json'))
        for name,entry in manifest['files'].items():
            if hashlib.sha256(z.read(name)).hexdigest()!=entry['sha256']:raise ValueError('Pixel web hash mismatch: '+name)
    if a.output.exists():raise ValueError('Choose a new output directory')
    pixel=a.output/'GlyphgrovePixel';dep=a.output/'GlyphgroveDeparture';pixel.mkdir(parents=True);dep.mkdir()
    scratch=pixel/'Desktop';scratch.mkdir();shutil.copytree(a.licenses,scratch/'licenses')
    shutil.copyfile(Path(__file__).resolve().parent/'THIRD-PARTY-NOTICES.md',scratch/'NOTICE.md')
    for item in report['assets']:shutil.copyfile(a.pixel_build/item['file'],scratch/item['file'])
    (scratch/'README.md').write_text('Private GlyphgrovePixel: Regular and Italic, full Nerd and 3D Emoji. Install the TTFs for system use. Keep licenses and NOTICE. Not for public release.\n')
    (scratch/'README.zh-Hans.md').write_text('GlyphgrovePixel 私人版：正常体、斜体，包含完整 Nerd 图标和 3D Emoji。可安装 TTF；请保留 licenses 和 NOTICE。不得公开发布。\n')
    (scratch/'README.zh-Hant.md').write_text('GlyphgrovePixel 私人版：正常體、斜體，包含完整 Nerd 圖示和 3D Emoji。可安裝 TTF；請保留 licenses 和 NOTICE。不得公開發布。\n')
    with zipfile.ZipFile(pixel/'Desktop.zip','x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in sorted(scratch.rglob('*')):
            if f.is_file():z.write(f,f.relative_to(scratch))
    with zipfile.ZipFile(pixel/'Desktop.zip') as z:
        for f in scratch.rglob('*'):
            if f.is_file() and hashlib.sha256(z.read(str(f.relative_to(scratch)))).hexdigest()!=sha(f):raise ValueError('Pixel Desktop archive mismatch')
    shutil.rmtree(scratch)
    shutil.copyfile(a.pixel_web,pixel/'Web.zip')
    for name in ('Desktop.zip','Web.zip'):shutil.copyfile(a.departure/name,dep/name)
    (a.output/'README.md').write_text('Private font kits. GlyphgrovePixel retains its chosen spacing; GlyphgroveDeparture uses DeparturePixelZh Compact spacing with experimental bold and italic. Desktop ZIPs contain installable TTF; Web ZIPs contain WOFF2, CSS, example and notices. No fonts or apps are installed or changed. Emoji Web support verified on macOS Chrome; other platforms untested. Do not publish or redistribute without rights review.\n')
    (a.output/'README.zh-Hans.md').write_text('私人字体包。GlyphgrovePixel 保留已选字距；GlyphgroveDeparture 使用 DeparturePixelZh Compact 原字距，粗体和斜体为实验性合成样式。Desktop ZIP 包含可安装的 TTF，Web ZIP 包含 WOFF2、CSS、示例和许可说明。本包不会自动安装或修改应用。Web Emoji 已在 macOS Chrome 验证，其他平台未测；不得公开或再分发。\n')
    (a.output/'README.zh-Hant.md').write_text('私人字型套件。GlyphgrovePixel 保留已選字距；GlyphgroveDeparture 使用 DeparturePixelZh Compact 原字距，粗體和斜體為實驗性合成樣式。Desktop ZIP 包含可安裝的 TTF，Web ZIP 包含 WOFF2、CSS、範例和授權說明。本套件不會自動安裝或修改 App。Web Emoji 已在 macOS Chrome 驗證，其他平台未測；不得公開或再散布。\n')
    entries={str(f.relative_to(a.output)):{'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(a.output.rglob('*')) if f.is_file()};(a.output/'manifest.json').write_text(json.dumps({'private':True,'files':entries},ensure_ascii=False,indent=2)+'\n');print(json.dumps(entries,indent=2))
if __name__=='__main__':main()
