# JEV 决策模型 API 系统

本项目基于 **Liquid AI** 决策模型架构（`LiquidAI/d1-omni-600M`）搭建的 **JEV 决策中台 API**。系统包含 **API Key 开通与配额管理**、**全链路 Token 消耗精细统计**，并提供基于 **Vue 3 + Tailwind CSS + DaisyUI + Vue Router + Pinia** 的现代化管理控制台与交互式决策 Studio。

---

## 🌟 核心特性

### 1. 多模型协同决策引擎 (Liquid AI & MiniCPM5-2B-Jev)
- **支持模型矩阵**：
  - `LiquidAI/d1-omni-600M`：专为高吞吐超低延迟场景设计（600M 参数，单步前向推理 15~35ms），适合网关护栏、实时客服工单流转。
  - `MiniCPM5-2B-Jev`：面壁智能 MiniCPM 5 架构 2B 参数量决策增强微调大模型（2.4B 参数，深度语义泛化 30~65ms），支持复杂行业长文本决策、深层风险研判。
- **三大约束决策原语**：
  - `choice`：多项分类选择，输出类别概率分布与置信度最高项。
  - `noul`：二元判断（Yes / No），返回判定布尔值与校准概率。
  - `score`：量规有序打分，在指定量表（如 1~5 分）内进行强度评级。
- **双模态支持引擎**：
  - **原生引擎**：支持通过 Hugging Face `transformers` 加载模型权重（支持 Apple Silicon `mps`、NVIDIA `cuda` 与 `cpu`）。
  - **高精度校准仿真引擎**：无权重或离线环境下自动平滑启动，百分百兼容真实输出结构与 Token 计量。

### 2. API Key 鉴权与配额管理
- **密码学安全**：生成 `jev-live-<hex>` 格式密钥，数据库仅存储 SHA-256 哈希值与部分脱敏前缀（如 `jev-live-b7e...70ae`）。
- **细粒度配额控制**：支持为不同客户端设置专属 Token 配额上限（Quota）、速率限制（RPM）及有效期限。
- **动态拦截**：请求时实时校验 Token 余量，超额自动触发 HTTP 429 配额保护。

### 3. 全链路 Token 消耗计量与审计
- **精细算力拆分**：
  - `prompt_tokens`：输入文本上下文与各问题 Schema（指导指令与标准描述）编码代币。
  - `decision_tokens`：评估各个决策分类头与打分投影层的计算单元代币。
  - `total_tokens`：总消耗代币。
- **全景仪表盘**：近 7 天趋势可视化、任务原语占比、密钥消耗排行、每次调用的请求流水审计日志。

### 4. 现代化前端架构
- **技术栈**：Vue 3 (Composition API / `<script setup>`) + TypeScript + Vite + Tailwind CSS + DaisyUI
- **页面路由**：
  - `/`：控制台概览（KPI 卡片、7天趋势图、原语分布、密钥排行）
  - `/playground`：决策 Studio（预置场景模版、动态 Schema 编辑器、实时概率条形图、cURL 导出）
  - `/api-keys`：API Key 密钥管理（生成新凭证、一次性明文展示、配额进度条、启停与删除）
  - `/analytics`：Token 消耗审计（多维度分类、按 Key 筛选、详细流水表）
  - `/docs`：开发者文档与 Python / cURL / TypeScript 代码示例
- **设计体验**：支持主题切换（dark, light, synthwave, corporate, dim）、模型在线状态实时检测。

---

## 🛠️ 项目结构

```text
jev/
├── backend/                  # Python 后端工程 (由 uv 统一管理)
│   ├── app/
│   │   ├── api/              # API 路由与依赖注入
│   │   │   ├── deps.py       # API Key 鉴权与 DB Session
│   │   │   └── v1/
│   │   │       ├── router.py # v1 主路由
│   │   │       ├── decision.py # 模型推理与 Token 扣减
│   │   │       ├── keys.py   # API Key CRUD
│   │   │       ├── analytics.py # 消耗统计与日志
│   │   │       └── model.py  # 模型运行状态控制
│   │   ├── core/
│   │   │   ├── config.py     # 环境变量与应用配置
│   │   │   └── security.py   # 密钥生成与 SHA-256 哈希
│   │   ├── db/
│   │   │   ├── base.py       # SQLAlchemy DeclarativeBase
│   │   │   ├── session.py    # 异步数据库引擎与默认种子数据
│   │   │   └── models.py     # APIKey, TokenUsageLog 模型
│   │   ├── schemas/          # Pydantic v2 数据模型
│   │   └── services/
│   │       ├── model_engine.py  # Liquid AI d1-omni-600M 推理引擎
│   │       ├── tokenizer.py     # Token 计量算法
│   │       ├── key_service.py   # Key 业务逻辑
│   │       └── analytics_service.py # 统计聚合计算
│   ├── pyproject.toml        # uv 项目与依赖配置
│   └── uv.lock
│
├── frontend/                 # Vue 3 前端工程
│   ├── src/
│   │   ├── api/              # Axios 接口层
│   │   ├── components/       # 业务组件 (StatCard, ProbabilitiesBar, TokenProgressBar...)
│   │   ├── layouts/          # AppLayout.vue (侧边栏 + 顶栏 + 抽屉)
│   │   ├── router/           # vue-router 路由配置
│   │   ├── stores/           # Pinia 状态管理 (keyStore, decisionStore, analyticsStore...)
│   │   ├── types/            # TypeScript 类型定义
│   │   └── views/            # 5 大功能页面视图
│   ├── tailwind.config.js    # Tailwind 与 DaisyUI 配置
│   └── vite.config.ts        # Vite 与代理配置
└── README.md
```

---

## 🚀 启动与运行指南

### 1. 后端启动 (使用 uv)

进入 `backend` 目录，通过 `uv` 运行服务（支持虚拟环境与依赖无缝管理）：

```bash
cd backend

# 安装/同步依赖
uv sync

# 配置环境变量 (账密与服务配置)
cp .env.example .env

# 启动 FastAPI 后端服务
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

后端服务就绪后：
- 决策中台管理登录：`http://127.0.0.1:8000/login`
  - **默认账号**：`admin`
  - **默认密码**：`admin123`
  - **凭据配置位置**：后端 `backend/.env`（支持 `ADMIN_USERNAME` 与 `ADMIN_PASSWORD`）
- 前端控制台主页（需先登录）：`http://127.0.0.1:8000/`
- 健康检查：`http://127.0.0.1:8000/api/health`
- Swagger API 文档：`http://127.0.0.1:8000/docs`
- 系统初始化时已自动植入默认开发者主密钥：`jev-live-demo-master-key-2026`（额度 1,000,000 Tokens）。

### 2. 前端构建与开发

进入 `frontend` 目录：

```bash
cd frontend

# 安装依赖
pnpm install

# 生产环境打包（直接自动编译输出到 backend/static/ 静态目录）
pnpm build

# 开发调试服务器（支持热重载与 /api 代理）
pnpm dev
```

> **一体化部署说明**：执行 `pnpm build` 后，产物直接生成到 `backend/static/`，后端 FastAPI 会自动挂载并提供 SPA 路由托管（支持 Vue Router History 模式）。访问 `http://127.0.0.1:8000/` 即可直接使用完整前端页面。

---

## 💻 API 调用示例

### 决策评估接口 (`POST /api/v1/decision/predict`)

#### cURL 示例
```bash
curl -X POST http://127.0.0.1:8000/api/v1/decision/predict \
  -H "Authorization: Bearer jev-live-demo-master-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "系统生产环境数据库出现高负载锁死，支付核心接口受到影响！",
    "questions": {
      "intent": {
        "type": "choice",
        "instructions": "判断故障分类",
        "criteria": {
          "database": "数据库及存储层故障",
          "network": "网络与网关异常",
          "code": "业务代码逻辑错误"
        }
      },
      "is_critical": {
        "type": "noul",
        "instructions": "是否属于重大紧急事件",
        "criteria": "核心交易流程受阻"
      },
      "urgency_score": {
        "type": "score",
        "instructions": "应急响应等级打分 (1-5)",
        "scale": 5
      }
    }
  }'
```

#### Python 示例
```python
import requests

API_URL = "http://127.0.0.1:8000/api/v1/decision/predict"
API_KEY = "jev-live-demo-master-key-2026"

payload = {
    "input": "企业希望在下季度采购 JEV 决策模型 API，请提供报价单与私有化部署测试包。",
    "questions": {
        "stage": {
            "type": "choice",
            "instructions": "评估销售线索阶段",
            "criteria": {
                "procurement_ready": "准备采购签约",
                "solution_eval": "方案评估阶段",
                "inquiry": "早期泛咨询"
            }
        },
        "is_enterprise": {
            "type": "noul",
            "instructions": "是否具备企业级采购特征"
        },
        "intent_score": {
            "type": "score",
            "instructions": "意向评分 (1-5)",
            "scale": 5
        }
    }
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

resp = requests.post(API_URL, json=payload, headers=headers)
data = resp.json()

print("决策结果:", data["answers"])
print(f"Token 消耗: {data['usage']['total_tokens']} tokens (Prompt: {data['usage']['prompt_tokens']}, Decision: {data['usage']['decision_tokens']})")
print(f"推理延迟: {data['latency_ms']} ms")
```

---

## 🔒 生产部署建议
- 可在 `.env` 中指定 `DATABASE_URL`（如 PostgreSQL）替代默认 SQLite。
- 若需下载并运行真实 `LiquidAI/d1-omni-600M` 权重（约 1.2GB），服务器需联网访问 Hugging Face 并确保具备相应算力支持（MPS 或 CUDA）。
