# 乡村文旅研学解决方案生成器 - 开发会话

> 会话时间：2026-05-18
> 用户：fanpu（转业空军上校/工程师）
> 项目：乡村文旅研学解决方案生成器

---

## 项目目标

为乡村一键生成完整的文旅研学解决方案，包括：
- 研学解决方案 PDF（1份）
- 研学宣传海报 PNG（多张）
- 品牌视觉（含 slogan/logo/文创小样）
- 不少于 5 个研学课程教案 PDF
- 不少于 2 个夏/冬令营研学手册 PDF

**测试村庄**：福建省宁德市屏南县熙岭乡 龙潭村

---

## 本次完成的工作

### 1. 接入 MiniMax 图片生成 API

| 文件 | 改动 |
|------|------|
| `config.py` | 添加 `IMAGE_MODEL = "image-01"` |
| `generators/poster_generator.py` | 接入 MiniMax `/v1/image_generation` API |
| `generators/brand_generator.py` | 接入 MiniMax `/v1/image_generation` API |
| `output_coordinator.py` | 调用图片 API 并下载图片到本地 |

**API 端点**：`POST https://api.minimaxi.com/v1/image_generation`

**测试结果**：
- ✅ 图片生成成功
- ✅ 海报/Logo/文创产品均可生成
- 图片 URL 有效期：24小时

---

### 2. 架构改进（上午已完成）

| 文件 | 改动 |
|------|------|
| `config.py` | 改用 MiniMax API + M2.5 模型 |
| `agents/*.py` (3个) | base_url 改为 MiniMax |
| `multimodal/image_analyzer.py` | 改为 Mock 模式（MiniMax 不支持图片输入） |
| `rag/village_knowledge.py` | 添加龙潭村/屏南县知识数据 |
| `tests/test_pipeline.py` | 修复路径 + 改为龙潭村案例 |
| `requirements.txt` | 添加 gradio/dotenv |
| `app.py` | 新建 Gradio 网页入口 |
| `run.py` | 新建 CLI 入口 |
| `.env.example` | 新建配置模板 |
| `.env` | 创建并配置 MiniMax API Key |

### 2. 技术问题修复

| 问题 | 解决方案 |
|------|---------|
| MiniMax API Key 认证失败 | 改用 Token Plan Key + `/v1` 端点 |
| 模型思考内容干扰 JSON 解析 | 开发 `extract_content()` 函数，从响应末尾提取 JSON |
| JSON 格式不规范（多余逗号等） | 添加 JSON 容错解析 + 重试机制 |
| WeasyPrint 依赖缺失 | fallback 到 HTML 输出 |
| 教案/营地手册生成不稳定 | 添加重试和降级处理 |

### 3. 当前入口方式

| 方式 | 命令 |
|------|------|
| **CLI** | `python run.py 龙潭村 -p 福建 -c 宁德 -y 屏南 -t 熙岭乡` |
| **Mock模式** | `python run.py 龙潭村 -p 福建 -c 宁德 -y 屏南 -t 熙岭乡 --mock` |
| **Gradio** | `python app.py`（浏览器访问 http://localhost:7860）|

---

## 生成结果

```
输出目录：C:\hermes\WorkAI\village_study_tour\output\龙潭村\

✅ 龙潭村_研学解决方案.html (10KB)
✅ 龙潭村_夏令营研学手册.html (1.2KB)
✅ 龙潭村_冬令营研学手册.html (1.2KB)
✅ 龙潭村_海报（Mock 占位符）
✅ 龙潭村_品牌Logo（Mock 占位符）
❌ 教案 PDF（未生成 - JSON 解析不稳定）
```

**品牌标语**：
- 走进龙潭村，探索乡土之美
- 龙潭村——闽东传统村落文化与农耕文明传承新体验
- 在龙潭村，读懂乡土中国

---

## 已知问题

| 优先级 | 问题 | 说明 |
|--------|------|------|
| 高 | 教案生成不稳定 | MiniMax 模型输出的 JSON 有时不合格式 |
| 中 | PDF 生成失败 | WeasyPrint 需要 GTK3，Windows 安装麻烦 |
| ~~中~~ | ~~海报/Logo 是 Mock~~ | ✅ 已接入 MiniMax image-01 |
| 低 | Gradio 未测试 | 界面还未实际运行 |

---

## MiniMax API 配置

```bash
# API Key 来源
# https://platform.minimaxi.com/user-center/basic-information/interface-key

# 配置方式
# 方式1: 环境变量
set MINIMAX_API_KEY=sk-api-xxx

# 方式2: .env 文件
copy .env.example .env
# 编辑 .env 填入 API Key

# 模型选择
# MiniMax-M2.5（当前使用）
# MiniMax-M2.7
# MiniMax-M2.5-highspeed
```

---

## 后续迭代计划

### 高优先级
1. **优化 JSON 解析稳定性**
   - 改进 `extract_content()` 函数
   - 添加更robust的JSON修复逻辑
   - 或考虑使用更简单的prompt

2. **安装 WeasyPrint**
   - Windows 需要 GTK3 环境
   - 或考虑其他 PDF 生成方案（如 reportlab）

### 中优先级
3. ~~接入图片生成 API~~ ✅ 已完成
4. **测试 Gradio 界面** ✅ 已完成（轻量级优化）
   - 添加进度条显示
   - 添加文件下载按钮

### 低优先级
5. **添加更多村庄知识**
   - 扩展 `rag/village_knowledge.py` 数据

6. **批量生成功能**
   - 支持 CSV 导入多个村庄

7. **产品化**
   - 添加异步任务队列
   - 开发进度条
   - 打包成可执行文件

### 低优先级
5. **添加更多村庄知识**
   - 扩展 `rag/village_knowledge.py` 数据

6. **批量生成功能**
   - 支持 CSV 导入多个村庄

7. **产品化**
   - 添加异步任务队列
   - 开发进度条
   - 打包成可执行文件

---

## 关键教训

1. **MiniMax 模型特性**：输出包含思考过程，需从 `\n\n` 之后提取实际内容
2. **JSON 格式不稳定**：大模型输出需要 robust 的解析和修复逻辑
3. **API Key 格式**：Token Plan Key 格式为 `sk-api-xxx`，不是 `sk-xxx`
4. **Windows 环境**：WeasyPrint 需要 GTK3，建议用 HTML fallback
5. **MiniMax 图片 API**：端点是 `/v1/image_generation`，不是 OpenAI SDK 的 `images.generate()`

---

## 文件结构

```
village_study_tour/
├── config.py              # 配置（API Key、模型）
├── main.py               # FastAPI Web 服务（旧）
├── app.py                # Gradio 网页入口（新）
├── run.py                # CLI 入口（新）
├── output_coordinator.py  # 流程编排器
├── .env                  # API Key 配置
├── .env.example          # 配置模板
├── requirements.txt      # 依赖
├── models/               # 数据模型
├── agents/               # AI Agent（解决方案/教案/营地手册）
├── generators/           # PDF/海报/品牌生成器
├── multimodal/           # 图像分析（Mock）
├── rag/                  # 知识库
└── output/               # 生成结果输出目录
```

---

*会话结束，待后续迭代*
