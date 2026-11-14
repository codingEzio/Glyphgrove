#!/usr/bin/env python3
"""Package the checked-in GlyphgrovePixel Web fonts and notices."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import zipfile

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FILES = ('Base-Regular.woff2', 'Base-Italic.woff2', 'Nerd.woff2', 'Emoji3D.woff2', 'RysaMixWebPixelCJK.woff2')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path, help='new package directory')
    parser.add_argument('--zip', action='store_true', help='also create a ZIP alongside the directory')
    args = parser.parse_args()
    dest = args.output.expanduser().absolute()
    archive = dest.with_name(dest.name + '.zip')
    if dest.exists() or dest.is_symlink() or (args.zip and archive.exists()):
        raise ValueError('Choose a new output directory and ZIP name')
    recipe = json.loads((ROOT / 'recipe.json').read_text())
    for name, digest in recipe['inputSha256'].items():
        if sha(ROOT / 'inputs' / name) != digest:
            raise ValueError('Pinned input changed: ' + name)
    web = ROOT / 'web'
    css = (web / 'fonts.css').read_text()
    paths = set(re.findall(r'url\(["\']?([^"\')]+)', css))
    if paths != {'fonts/' + name for name in FILES}:
        raise ValueError('Unexpected Web font references')
    for name in FILES:
        if TTFont(web / 'fonts' / name, lazy=True).flavor != 'woff2':
            raise ValueError('Invalid WOFF2: ' + name)
    nerd = TTFont(web / 'fonts/Nerd.woff2')
    nerd_source = TTFont(ROOT / 'inputs/SymbolsNerdFontMono-Regular.ttf')
    aliases = {int(cp, 16) for cp in recipe['symbolAliases']}
    if set(nerd.getBestCmap()) != set(nerd_source.getBestCmap()) | aliases:
        raise ValueError('Nerd icon coverage changed')
    emoji = TTFont(web / 'fonts/Emoji3D.woff2')
    source = TTFont(ROOT / 'inputs/Noto3D-64.ttf')
    if emoji.getBestCmap() != source.getBestCmap() or emoji.getTableData('GSUB') != source.getTableData('GSUB'):
        raise ValueError('Emoji coverage or sequence shaping changed')
    if sum(x.graphicType == 'png ' for x in emoji['sbix'].strikes[28].glyphs.values()) != 3994:
        raise ValueError('Emoji bitmap repertoire changed')
    dest.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.glyphgrove-web-', dir=dest.parent))
    try:
        for file in ('fonts.css', 'example.html', 'README.md', 'README.zh-Hans.md', 'README.zh-Hant.md', 'NOTICE.md'):
            shutil.copyfile(web / file, stage / file)
        shutil.copytree(web / 'fonts', stage / 'fonts')
        shutil.copytree(web / 'licenses', stage / 'licenses')
        entries = {p.relative_to(stage).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size}
                   for p in sorted(stage.rglob('*')) if p.is_file()}
        manifest = {'schemaVersion': 1, 'family': 'GlyphgrovePixel', 'scope': 'public web font package',
                    'sourceRecipeSha256': sha(ROOT / 'recipe.json'), 'fonts': {n: entries['fonts/' + n] for n in FILES},
                    'nerdCmapCount': len(nerd.getBestCmap()), 'emojiBitmapCount': 3994,
                    'files': entries}
        (stage / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        stage.rename(dest)
        if args.zip:
            with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as out:
                for path in sorted(dest.rglob('*')):
                    if path.is_file():
                        out.write(path, path.relative_to(dest))
            with zipfile.ZipFile(archive) as out:
                for path in dest.rglob('*'):
                    if path.is_file() and hashlib.sha256(out.read(path.relative_to(dest).as_posix())).hexdigest() != sha(path):
                        raise ValueError('ZIP verification failed: ' + str(path))
        print(json.dumps({'directory': str(dest), 'zip': str(archive) if args.zip else None,
                          'zipBytes': archive.stat().st_size if args.zip else None,
                          'fontBytes': sum(x['bytes'] for x in manifest['fonts'].values()),
                          'nerdCmapCount': manifest['nerdCmapCount'], 'emojiBitmapCount': 3994}))
    finally:
        if stage.exists():
            shutil.rmtree(stage)


if __name__ == '__main__':
    main()
