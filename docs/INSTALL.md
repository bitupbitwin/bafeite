# 安装与使用手册

本手册面向第一次使用本工具的用户，按步骤操作即可在自己的电脑上跑起来，并用手机访问。

> ⚠️ 本工具仅基于历史价格、成交量和技术指标进行统计分析，不构成任何投资建议。

---

## 目录

1. [环境要求](#1-环境要求)
2. [获取代码](#2-获取代码)
3. [安装并启动后端](#3-安装并启动后端)
4. [安装并启动前端](#4-安装并启动前端)
5. [手机访问](#5-手机访问)
6. [Docker 一键部署（可选）](#6-docker-一键部署可选)
7. [页面使用说明](#7-页面使用说明)
8. [回测验证模型](#8-回测验证模型)
9. [常见问题排查](#9-常见问题排查)

---

## 1. 环境要求

| 软件 | 版本要求 | 下载地址 |
| --- | --- | --- |
| Python | 3.10 及以上（推荐 3.11） | https://www.python.org/downloads/ |
| Node.js | 18 及以上（推荐 20/22 LTS） | https://nodejs.org/ |
| 浏览器 | Chrome / Edge / Safari 较新版本 | — |

安装完成后，打开终端（Windows 用「命令提示符」或 PowerShell，macOS 用「终端」），确认版本：

```bash
python --version    # Windows 如无效可试 py --version
node --version
npm --version
```

> **Windows 安装 Python 时务必勾选 "Add Python to PATH"**，否则终端找不到 `python` 命令。

获取真实行情需要电脑能访问互联网（AKShare 从公开行情站点取数）。

---

## 2. 获取代码

方式一：用 git 克隆

```bash
git clone <本仓库地址>
cd bafeite
```

方式二：在 GitHub 页面点 **Code → Download ZIP**，解压后用终端进入解压目录。

项目包含两个子目录：`backend/`（Python 后端）和 `frontend/`（网页前端），**需要分别启动，两个终端窗口同时开着**。

---

## 3. 安装并启动后端

打开**第一个终端窗口**：

```bash
cd backend

# (推荐) 创建独立虚拟环境, 避免污染系统 Python
python -m venv .venv

# 激活虚拟环境
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (命令提示符):
.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# 安装依赖(国内网络慢可加镜像参数, 见下方提示)
pip install -r requirements.txt

# 启动后端
uvicorn main:app --host 0.0.0.0 --port 8000
```

看到类似下面的输出说明启动成功：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

验证：浏览器打开 http://localhost:8000/docs ，能看到 Swagger 接口文档页面即为正常。

> **国内 pip 加速**：
> ```bash
> pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
> ```

> **无法联网取行情？** 可用演示模式启动（数据为程序生成，仅用于体验界面，页面会显示黄色警示条）：
> ```bash
> # macOS / Linux
> USE_MOCK_DATA=1 uvicorn main:app --host 0.0.0.0 --port 8000
> # Windows PowerShell
> $env:USE_MOCK_DATA="1"; uvicorn main:app --host 0.0.0.0 --port 8000
> ```

---

## 4. 安装并启动前端

打开**第二个终端窗口**（保持后端窗口运行不要关）：

```bash
cd frontend

# 安装依赖(国内网络慢可先执行: npm config set registry https://registry.npmmirror.com)
npm install

# 启动开发服务器
npm run dev
```

看到类似输出说明启动成功：

```
  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

浏览器打开 **http://localhost:5173** 即可使用。前端已自动把 `/api` 请求代理到后端 8000 端口，无需额外配置。

---

## 5. 手机访问

1. 确保手机和电脑连接**同一个 Wi-Fi**。
2. 查看前端启动输出中的 `Network:` 地址（如 `http://192.168.1.8:5173`），或手动查电脑局域网 IP：
   - Windows：终端执行 `ipconfig`，看「IPv4 地址」
   - macOS：终端执行 `ipconfig getifaddr en0`
3. 手机浏览器输入该地址，例如 `http://192.168.1.8:5173`。

打不开时检查：电脑防火墙是否放行了 5173 端口；手机和电脑是否真的在同一网段。

---

## 6. Docker 一键部署（可选）

已安装 Docker Desktop（或 docker + docker compose）的用户，在项目根目录执行：

```bash
docker compose up --build
```

- 前端：http://localhost:8080
- 后端接口文档：http://localhost:8000/docs

无法联网取行情时，把 `docker-compose.yml` 中的 `USE_MOCK_DATA` 改为 `"1"` 再启动。

停止：按 `Ctrl+C`，或执行 `docker compose down`。

---

## 7. 页面使用说明

### 7.1 首页

1. **输入股票名称或代码**：如 `普冉股份`、`688766`、`长川科技`、`300604`，输入后会弹出候选列表，点选目标股票。
2. **选择分析周期**：最近 7 / 15 个交易日、最近 1 / 2 / 3 个月。
   - 注意：模型至少需要 20 个交易日数据，选 7 天或 15 天时只做简单趋势判断，结论可靠性较低。
3. 点击红色的 **开始分析** 按钮。

### 7.2 结果页

从上到下依次为：

| 区块 | 内容 |
| --- | --- |
| 预测卡片 | 股票名称代码、当前价、今日涨跌幅、当前状态徽章、明日涨/跌概率条、预计涨跌幅区间、支撑位、压力位、模型评分 |
| K线与成交量 | 蜡烛图 + MA5/MA10/MA20 均线 + 成交量柱（红涨绿跌），可拖动下方滑块或双指缩放查看 |
| 模型解释 | 逐条说明模型为什么给出这个判断 |

**当前状态**共六种：

- 🔴 **上涨阶段** — 短期趋势强，注意冲高回落
- 🟠 **健康回调** — 涨后缩量回调 3%~8%，属正常整理
- ⚪ **横盘整理** — 窄幅缩量震荡，等待方向选择
- 🩷 **突破阶段** — 放量突破近期高点，注意假突破
- 🟢 **风险阶段** — 出现放量下跌/长上影/破均线等出货信号
- 🔵 **震荡观察** — 不属于以上任何典型形态

**如何读概率**：上涨概率 = 50% + 评分 × 0.35（限 10%~90%），它是规则评分的线性映射，**不是真实统计概率**，只表示模型看多/看空的倾向强弱。

点击左上角「← 返回重新选择」或页面标题可回到首页。

### 7.3 接口直接调用（进阶）

不用网页也可以直接调接口，完整说明见 [docs/API.md](API.md)：

```bash
# 搜索
curl "http://localhost:8000/api/stocks/search?keyword=普冉"

# 分析
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "688766", "period_days": 30}'
```

---

## 8. 回测验证模型

在相信任何概率数字之前，先用回测接口看模型在这只股票上的历史表现：

```bash
curl -X POST http://localhost:8000/api/backtest \
  -H "Content-Type: application/json" \
  -d '{"code": "688766", "window_days": 30, "test_days": 60}'
```

返回中重点看：

- `accuracy`：方向预测准确率（%）。长期接近或低于 50% 说明模型对这只股票基本无效。
- `worst_cases`：预测方向错误且实际波动最大的案例，了解最坏情况。

---

## 9. 常见问题排查

| 现象 | 原因与解决办法 |
| --- | --- |
| `pip install` 报错或极慢 | 使用国内镜像：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`；确认 Python ≥ 3.10 |
| 安装 akshare 失败 | 先升级构建工具：`pip install -U pip setuptools wheel` 后重试；仍失败可先用 `USE_MOCK_DATA=1` 演示模式体验，再单独排查 |
| `uvicorn: command not found` | 虚拟环境未激活，或用 `python -m uvicorn main:app --port 8000` 代替 |
| 页面报「无法从 AKShare 获取…」(502) | 电脑无法访问行情站点：检查网络/代理；确认股票代码正确；上游接口偶尔抽风可稍后重试；或用演示模式 |
| 搜索无结果 | 首次搜索需要从 AKShare 拉全量股票列表，可能等几秒；仅支持 A 股，港股美股暂不支持 |
| 前端打开报错 / 一直转圈 | 确认后端终端窗口仍在运行且无报错；浏览器按 F12 看 Network 里 `/api` 请求的错误信息 |
| 端口被占用（8000 或 5173） | 换端口启动：后端 `uvicorn main:app --port 8001`，同时把 `frontend/vite.config.ts` 中代理 target 改为对应端口 |
| 手机打不开页面 | 电脑防火墙放行 5173 端口；确认手机电脑同一 Wi-Fi；用 `Network:` 显示的 IP 而不是 localhost |
| 页面顶部出现黄色「演示数据」警示 | 后端是用 `USE_MOCK_DATA=1` 启动的，数据为程序生成；去掉该环境变量重启后端即可使用真实行情 |
| 数据不是最新的 | AKShare 日线数据在收盘后更新，盘中看到的是上一交易日为止的数据 |

仍解决不了时，把后端终端窗口里的报错信息完整复制下来提 issue。
