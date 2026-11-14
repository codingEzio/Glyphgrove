# Glyphgrove

Glyphgrove 是实验性字体，组合等宽英文、像素中文、Nerd 图标和 Noto 3D Emoji。GlyphgrovePixel 提供正常体与斜体可变字体；`web/` 包含 Web 字体。

安装 `requirements.txt` 中的 Python 依赖，然后运行：

```sh
python tool/build.py --inputs inputs --recipe recipe.json --output build
```

构建会校验输入并生成可变 TTF。素材来源见 `INPUTS.md`，Web 用法见 `web/README.zh-Hans.md`。使用 `python tool/package_web.py --output Local/web-package --zip` 可生成 Web 包，输出目录须为新路径。

GlyphgroveDeparture 是使用 DeparturePixelZh Compact、Nerd 图标和 3D Emoji 的实验字体，粗体和斜体为合成样式。构建参数见 `python tool/build_departure.py --help`，依赖的其他项目输入未包含在此仓库中。

Web Emoji 使用 sbix，仅在 macOS Chrome 验证；其他平台可能回退至系统 Emoji。中文宽度不完全等于两个英文字格，终端对齐可能不同。组件说明见 `tool/THIRD-PARTY-NOTICES.md` 和 `licenses/`；工具代码许可见 `tool/CODE-LICENSE-MIT.txt`。
