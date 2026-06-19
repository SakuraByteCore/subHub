# TVBox Hub

公共 TVBox 订阅聚合入口，把多个公开 TVBox 配置源合并成一个可直接使用的订阅地址，减少手动切源。

## 订阅地址

推荐使用 jsDelivr 链接，国内环境通常比 `raw.githubusercontent.com` 更稳：

```text
https://cdn.jsdelivr.net/gh/SakuraByteCore/tvbox-hub@main/tvbox.json
```

备用链接：

```text
https://fastly.jsdelivr.net/gh/SakuraByteCore/tvbox-hub@main/tvbox.json
https://gcore.jsdelivr.net/gh/SakuraByteCore/tvbox-hub@main/tvbox.json
https://raw.githubusercontent.com/SakuraByteCore/tvbox-hub/main/tvbox.json
```

## 当前内容

当前生成结果见 [`manifest.json`](./manifest.json)。截至最近一次生成：

- 站点源：206 个
- 直播源：10 个
- 解析接口：29 个
- 规则：20 条

## 当前来源

来源配置见 [`sources.json`](./sources.json)：

- `qist`: `https://qist.wyfc.qzz.io/jsm.json`
- `jinenge`: `https://jinenge.us.kg/app/tvbox/tvbox.json`

## 使用方法

1. 复制上面的推荐订阅地址。
2. 打开支持 TVBox 配置的客户端。
3. 在配置/接口/订阅地址处粘贴链接。
4. 保存并刷新。

## 合并规则

- `sites`: 优先按 `key` 去重；同 key 但内容不同会给后加入的源加来源前缀，尽量保留两边内容。
- `lives`: 按 `name + url` 去重。
- `parses`、`rules`、`doh`: 按 `name` 去重；冲突时保留高优先级来源，低优先级来源自动改名保留。
- `hosts`、`flags`、`ads`: 按字符串集合去重。
- 相对路径会按原始订阅 URL 转换成绝对 URL，避免合并后 `./jar/...`、`./lib/...` 这类路径失效。
- 顶层 `spider` 默认使用优先级最高来源；其它来源依赖的 spider 会尽量作为站点级 `jar` 写入，兼容性取决于客户端实现。

## 自动更新

GitHub Actions 会定时运行 [`scripts/build_tvbox.py`](./scripts/build_tvbox.py)，重新抓取来源并生成：

- [`tvbox.json`](./tvbox.json): TVBox 可直接使用的订阅配置
- [`manifest.json`](./manifest.json): 本次生成的来源状态和合并统计

也可以本地手动执行：

```bash
python3 scripts/build_tvbox.py
```

## 添加来源

编辑 [`sources.json`](./sources.json)，新增一条来源记录：

```json
{
  "id": "example",
  "name": "Example",
  "url": "https://example.com/tvbox.json",
  "priority": 30,
  "enabled": true,
  "note": "Optional note"
}
```

然后运行：

```bash
python3 scripts/build_tvbox.py
```

确认 `tvbox.json` 和 `manifest.json` 正常生成后提交即可。

## 说明

本仓库只做订阅聚合与格式整理，来源内容归原作者所有。若某来源不允许公开转载或继续聚合，请联系维护者移除。
