# Pinned inputs

All inputs are included for offline builds; hashes and geometry are recorded in `recipe.json`.

- Rysana Mono 1.0.0 upright and italic: https://github.com/rysana-os/type/releases/download/v1.0.0/rysana-type.zip — OFL 1.1, reserved name Rysana.
- Cubic 11: https://github.com/ACh-K/Cubic-11 — OFL 1.1, reserved names Cubic and 俐方體; exact bundled input hash is in the recipe.
- Symbols Nerd Font Mono 3.5.1: https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.5.1 — multiple component licenses; preserve notices and review before redistribution.
- Noto 3D Emoji `v2026-09-24-unicode18_0`: https://github.com/googlefonts/noto-emoji — OFL 1.1. The included file is the pre-extracted original 55 PPEM / 64 px strike, derived from upstream `3D/fonts/Noto-3D-128.ttf` (upstream SHA-256 `6f4312a7c02d0c9de88095ee65e320ffe9316d2d8d56e4c515e7181fca5ed439`). The build resamples to 28 PPEM and 64 colors.
- Build dependencies: fontTools 4.60.1, Brotli 1.1.0 and Pillow 12.0.0. Install separately from Python package indexes; offline builds require preinstalled dependencies. Python and HarfBuzz are not included.

## GlyphgroveDeparture experiment

- The text input is the verified `DeparturePixelZh Compact` 0.1.1 output from the sibling X-DeparturePixelZh project, built using its pinned X-DeparturePixelZhBuilder recipe. Input and per-codepoint source coverage SHA-256 are pinned in `departure-recipe.json`. It is an intermediate derived input, not the raw upstream font. The original sources and notices belong to the Departure project.
- `skia-pathops` 0.8.0.post2 (BSD-3-Clause, https://github.com/fonttools/skia-pathops) is needed to create the experimental bold text outlines; it is installed separately with `requirements.txt`. It is not bundled in the font packages. Source text advances remain unchanged; italic and bold are synthetic static styles, not original Departure Mono styles.
