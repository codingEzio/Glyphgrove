# Glyphgrove

Glyphgrove is an experimental font family combining monospace Latin, pixel CJK, Nerd icons and Noto 3D Emoji. GlyphgrovePixel provides variable regular and italic styles; `web/` contains ready-to-use web fonts.

## Build

Install the pinned Python dependencies in `requirements.txt`, then run:

```sh
python tool/build.py --inputs inputs --recipe recipe.json --output build
```

The bundled inputs are pinned and verified by `recipe.json`. The build creates variable TTFs. See `INPUTS.md` for sources and `web/README.md` for web usage. To package the web fonts, run `python tool/package_web.py --output Local/web-package --zip` with a new output path.

## GlyphgroveDeparture

The experimental Departure family uses DeparturePixelZh Compact plus Nerd icons and 3D Emoji. Its bold and italic forms are synthesized. Run `python tool/build_departure.py --help` for required input files and `python tool/package_departure.py --help` for packaging. Its sibling-project inputs are not included here.

Web emoji uses sbix and was tested in macOS Chrome; other platforms may fall back to system emoji. Pixel CJK advances do not exactly match two Latin cells and may not align in fixed-grid terminals. Component credits and notices are in `tool/THIRD-PARTY-NOTICES.md` and `licenses/`; the tools' MIT notice is in `tool/CODE-LICENSE-MIT.txt`.
