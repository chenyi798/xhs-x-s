# xhs-sign

小红书 Web 端 `x-s` / `x-s-common` 本地生成示例。

> 仅用于学习、研究和协议分析。请遵守小红书用户协议、robots 规则和当地法律法规，不要用于批量抓取、绕过风控、账号滥用或商业化采集。仓库不包含也不提供 Cookie、账号、代理或任何登录态获取方式。

## 文件说明

```text
.
├── xhs_sign_bundle.js              # 核心签名 bundle，导出 x-s / x-s-common 生成函数
├── homefeed_xs_xscommon_test.py    # Python 调用示例
```

## 环境要求

- Node.js 18+
- Python 3.9+，仅运行 Python 示例时需要
- Python 依赖：`requests`

安装 Python 示例依赖：

```bash
pip install requests
```

本项目的 Node.js 部分只使用内置模块，不需要 `npm install`。


运行 Python 示例：

```bash
python homefeed_xs_xscommon_test.py
```

运行前请在 `homefeed_xs_xscommon_test.py` 中自行填写合法来源的 `COOKIE`，格式如下：

```python
COOKIE = (
    "a1=; "
    "web_session=; "
)
```

把实际值填到等号后面，例如 `a1=你的a1; `、`web_session=你的web_session; `。

## Node.js API

### `buildX3(options)`

生成 `x-s`，返回值里包含中间参数和最终 `xs`。

```js
const { buildX3 } = require('./xhs_sign_bundle');

const result = buildX3({
  url: '/api/sns/web/v1/homefeed',
  payload: {
    cursor_score: '',
    num: 18,
    refresh_type: 1,
  },
  a1: '',
  loadts: '',
  random32: 0x7fffffff,
  nowMs: String(Date.now()),
  ctr: 544,
});

console.log(result.xs);
```

常用参数：

- `url`：接口 path，例如 `/api/sns/web/v1/homefeed`
- `payload`：请求体对象，内部会使用 `JSON.stringify(payload)`
- `a1`：Cookie 中的 `a1`
- `loadts`：Cookie 中的 `loadts`，没有时可为空字符串
- `random32`：32 位随机数或固定测试值
- `nowMs`：当前毫秒时间戳，字符串或数字均可
- `ctr`：计数值，示例中为 `544`

### `buildXsCommon(options)`

生成 `x-s-common`。

```js
const { buildXsCommon } = require('./xhs_sign_bundle');

const now = String(Date.now());
const common = buildXsCommon({
  a1: '',
  b1: '',
  b1b1: '1',
  dsllt: now,
  dsl: now,
  platform: 'Windows',
  signCount: 0,
});

console.log(common.xSCommon);
```

返回结构：

```js
{
  payload: { /* x-s-common 原始 payload */ },
  xSCommon: '...'
}
```

## Python 调用方式

Python 示例通过 `subprocess.run(["node", "-e", js])` 调用本地 Node.js 签名函数，再把结果放入请求头：

```python
built = build_headers()

headers = {
    "x-s": built["xs"],
    "x-s-common": built["xsc"],
    "cookie": COOKIE,
}
```

如果你要接入自己的 Python 项目，建议保留这种边界：签名逻辑在 `xhs_sign_bundle.js`，业务请求逻辑在 Python 中。

## 注意事项

- `x-s` 对 `url + JSON.stringify(payload)` 敏感，请确保签名时的 `payload` 和实际发送的 body 完全一致。
- Python 发送 JSON 时建议使用 `json.dumps(payload, ensure_ascii=False, separators=(",", ":"))`，避免空格差异导致签名不一致。
- `x-s-common` 不带 `XYS_` 前缀；`x-s` 带 `XYS_` 前缀。
- 平台算法可能更新，生成逻辑不保证长期有效。

## 免责声明

本项目只用于安全研究、学习和本地签名算法验证。使用者应自行承担使用风险，并确保所有请求都有合法授权。作者不对任何违规使用、账号风险、数据滥用或由此产生的后果负责。
