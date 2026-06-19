# xx

公共 TVBox 订阅收集配置，用来把多个公开订阅源合并成一个入口，减少手动切源。

## 订阅地址

```text
https://raw.githubusercontent.com/SakuraByteCore/xx/main/tvbox.json
```

## 当前来源

来源配置见 [`sources.json`](./sources.json)：

- `qist`: `https://qist.wyfc.qzz.io/jsm.json`
- `jinenge`: `https://jinenge.us.kg/app/tvbox/tvbox.json`

## 合并规则

- `sites`: 优先按 `key` 去重；同 key 但内容不同会给后加入的源加来源前缀，尽量保留两边内容。
- `lives`: 按 `name + url` 去重。
- `parses`, `rules`, `doh`: 按 `name` 去重；冲突时保留高优先级来源，低优先级来源自动改名保留。
- `hosts`, `flags`, `ads`: 按字符串集合去重。
- 相对路径会按原始订阅 URL 转换成绝对 URL，避免合并后 `./jar/...`、`./lib/...` 这类路径失效。
- 顶层 `spider` 默认使用优先级最高来源；其它来源依赖的 spider 会尽量作为站点级 `jar` 写入，兼容性取决于客户端实现。

## 更新方式

GitHub Actions 会定时运行 [`scripts/build_tvbox.py`](./scripts/build_tvbox.py)，重新抓取来源并生成：

- [`tvbox.json`](./tvbox.json): TVBox 可直接使用的订阅配置
- [`manifest.json`](./manifest.json): 本次生成的来源状态和合并统计

也可以本地手动执行：

```bash
python3 scripts/build_tvbox.py
```

## 说明

本仓库只做订阅聚合与格式整理，来源内容归原作者所有。若某来源不允许公开转载或继续聚合，请联系维护者移除。
