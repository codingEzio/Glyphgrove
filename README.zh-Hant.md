# Glyphgrove

Glyphgrove 是實驗性字型，結合等寬英文、像素中文、Nerd 圖示和 Noto 3D Emoji。GlyphgrovePixel 提供正常體與斜體可變字型；`web/` 包含 Web 字型。

安裝 `requirements.txt` 的 Python 依賴後執行：

```sh
python tool/build.py --inputs inputs --recipe recipe.json --output build
```

建置會驗證輸入並產生可變 TTF。素材來源見 `INPUTS.md`，Web 用法見 `web/README.zh-Hant.md`。執行 `python tool/package_web.py --output Local/web-package --zip` 可產生 Web 套件，輸出目錄須為新路徑。

GlyphgroveDeparture 是使用 DeparturePixelZh Compact、Nerd 圖示和 3D Emoji 的實驗字型，粗體和斜體是合成樣式。建置參數見 `python tool/build_departure.py --help`，依賴的其他專案輸入未包含在此倉庫中。

Web Emoji 使用 sbix，僅在 macOS Chrome 驗證；其他平台可能回退到系統 Emoji。中文寬度不完全等於兩個英文字格，終端機對齊可能不同。元件說明見 `tool/THIRD-PARTY-NOTICES.md` 和 `licenses/`；工具程式碼授權見 `tool/CODE-LICENSE-MIT.txt`。
