# 乡村文旅研学解决方案生成器 - 开发会话记录

> 会话时间：2025年某日
> 用户：fanpu（转业空军上校/工程师）
> 项目：绿野有机教育体验农场 - 乡村文旅研学解决方案生成器

---

## 项目目标

为乡村一键生成完整的文旅研学解决方案，包括：
- 研学解决方案 PDF（1份）
- 研学宣传海报 PNG（多张）
- 品牌视觉（含 slogan/logo/文创小样）
- 不少于 5 个研学课程教案 PDF
- 不少于 2 个夏/冬令营研学手册 PDF

**村庄测试数据**：湖南省怀化市会同县炮团乡（无图片/视频）

---

## 技术方案

### 模型选型
- **主模型**：Qwen2.5-72B-Instruct（阿里云百炼 DashScope）
- **图片理解**：Qwen2-VL
- **海报生成**：FLUX.1-dev（Replicate）
- **Logo/文创**：Wanx2.1

### 项目结构
```
village_study_tour/
├── config.py              # API Key 配置
├── main.py                # FastAPI Web 服务入口
├── requirements.txt       # 依赖清单
├── output_coordinator.py  # 完整流程编排器
├── models/
│   ├── input_schema.py    # 村庄输入模型
│   └── output_schema.py    # 输出结构模型
├── agents/
│   ├── solution_agent.py      # 研学解决方案生成
│   ├── lesson_plan_agent.py   # 5份教案生成
│   └── camp_manual_agent.py   # 夏/冬令营手册生成
├── multimodal/
│   └── image_analyzer.py      # Qwen-VL 图片特征提取
├── rag/
│   └── village_knowledge.py   # 村庄知识库+RAG
├── generators/
│   ├── pdf_solution.py        # 解决方案 PDF
│   ├── pdf_lesson_plan.py      # 教案 PDF
│   ├── pdf_camp_manual.py      # 营地手册 PDF
│   ├── poster_generator.py     # 海报概念生成
│   └── brand_generator.py      # 品牌视觉（Slogan/Logo/文创）
└── tests/
    └── test_pipeline.py        # Mock 全流程测试
```

---

## 完成状态

### 已创建的文件

| 文件 | 状态 |
|------|------|
| `config.py` | ✅ 完成 |
| `models/input_schema.py` | ✅ 完成 |
| `models/output_schema.py` | ✅ 完成 |
| `agents/solution_agent.py` | ✅ 完成 |
| `agents/lesson_plan_agent.py` | ✅ 完成 |
| `agents/camp_manual_agent.py` | ✅ 完成 |
| `multimodal/image_analyzer.py` | ❌ 未完成（shell 引号嵌套问题） |
| `rag/village_knowledge.py` | ❌ 未完成（shell 引号嵌套问题） |
| `generators/pdf_solution.py` | ✅ 完成 |
| `generators/pdf_lesson_plan.py` | ✅ 完成 |
| `generators/pdf_camp_manual.py` | ✅ 完成 |
| `generators/poster_generator.py` | ✅ 完成 |
| `generators/brand_generator.py` | ✅ 完成 |
| `main.py` | ✅ 完成 |
| `output_coordinator.py` | ✅ 完成 |
| `tests/test_pipeline.py` | ✅ 完成 |
| `requirements.txt` | ✅ 完成 |

### Mock 测试结果
- 炮团乡研学解决方案 ✅（标题"炮团乡研学旅行解决方案"，主题"乡土文化探索营"）
- 5份教案 ✅（稻作文化/侗族大歌/竹编手工艺/乡村美食工坊/山林自然探索）
- 夏令营（7天）/ 冬令营（5天）手册 ✅
- 3张海报概念 ✅
- 3条品牌标语 ✅
- PDF/HTML 文件生成（WeasyPrint 未安装时 fallback 为 HTML）✅

---

## 待完成工作

### 立即可做
1. 安装 WeasyPrint：`pip install weasyprint`
2. 补全 `multimodal/image_analyzer.py`
3. 补全 `rag/village_knowledge.py`

### 配置 API Key 后
1. 在 `config.py` 中填入真实的 `DASHSCOPE_API_KEY`（阿里云百炼）和 `REPLICATE_API_KEY`
2. 运行 `python main.py` 启动 FastAPI 服务
3. 访问 http://localhost:8000/docs 测试 `/generate` 接口
4. 调用真实 API 生成炮团乡完整研学方案

### 产品化
1. 开发 Gradio 前端界面
2. 加入异步任务队列（Celery）
3. 添加图片上传和视频上传接口

---

## 关键教训

1. **write_file 工具优先**：复杂的 Python 代码块不要通过 shell 传递，用 write_file 工具直接写入可避免所有引号嵌套问题
2. **Mock 测试先行**：先用模拟数据跑通全流程，确认链路无误后再配真实 API
3. **输出架构**：全部先生成结构化 JSON → 再渲染为 HTML/WeasyPrint PDF，Agent 和渲染器解耦

---

## NotebookLM 技术调研

### NotebookLM 使用什么底层模型？
- 核心：Google Gemini 系列，特别是 **Gemini 1.5 Pro**（超长上下文，支持 100 万 token）
- Audio Overview 功能：使用 **Veo2**（视频生成）+ **Lyria**（音乐生成）
- 实时数据查询：结合 Google Search 提供的能力

### 国产替代方案
- **文心一言**（百度）：文档理解、对话、生成
- **通义千问**（阿里）：长文本理解、多模态
- **讯飞星火**（科大讯飞）：语音+文档综合处理
- **Kimi**（月之暗面）：超长上下文（20 万 token），文档理解
- **智谱 GLM**（智谱华章）：长文本+多模态
- **腾讯混元**：文档处理+对话

---

## 输出文件位置

真实 API 运行后输出到：`C:\Users\fanpu\village_study_tour\output\炮团乡\`

---

*会话结束，待晚上继续开发*
