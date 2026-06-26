# Zuno 设置窗口与 RAG 评测接力说明

## 这份文档是干什么的

这是一份给下一轮对话直接接力用的交接说明，避免重新摸索上下文。

适用场景：

- 新开一个对话继续做 Zuno 设置窗口测试
- 用 Chrome / 浏览器插件继续做前端验收
- 继续推进 RAG / GraphRAG 自动化评测

## 当前已经落下来的文档

### 1. RAG / GraphRAG 评测任务文档

已保存：

```text
docs/prototypes/superpowers-legacy/specs/2026-05-27-zuno-rag-graphrag-eval-task.md
```

用途：

- 定义小样本调参 -> 大样本正式评测两阶段方案
- 固定五个核心指标
- 把 GraphRAG 作为正式候选模式纳入评测
- 明确 LangSmith 只负责 trace，不直接负责召回率计算

### 2. 既有设计文档

可继续参考：

```text
docs/prototypes/superpowers-legacy/specs/2026-05-26-zuno-rag-evaluation-langsmith-design.md
docs/prototypes/superpowers-legacy/specs/2026-05-26-zuno-rag-graphrag-knowledge-config-design.md
```

## 当前前端改动进度

### 已经完成的方向

设置页的目标已经从“整页替换”转为：

- 左下角 `设置` 入口触发
- 主内容区上方弹出一个设置窗口
- 背景半透明 + 虚化
- 窗口内左栏切换栏目，右侧显示具体设置页
- 支持关闭

### 当前判断

网页 Chrome 中表现正常或接近正常。  
Codex 内置浏览器里表现异常，不适合作为这项任务的主验收环境。

### 对 Codex 内置浏览器的结论

当前已确认：

- 同一前端页面在普通 Chrome 可正常显示
- Codex 内置浏览器存在异常表现
- 不应再把 Codex 内置浏览器当作主验收标准

后续前端视觉与交互验收，优先使用：

- 普通 Chrome
- 或能驱动真实 Chrome 的浏览器插件 / 自动化链路

## 当前代码状态的重点

### 1. 设置窗口相关代码已分散在这几处

```text
src/frontend/src/pages/workspace/workspace.vue
src/frontend/src/pages/workspace/workspace.scss
src/frontend/src/pages/workspace/components/WorkspaceSettingsShell.vue
src/frontend/src/pages/workspace/components/SettingsUiModeSwitch.vue
src/frontend/src/utils/settings-preferences.ts
```

### 2. 默认设置界面模式

当前逻辑是：

- 默认 `traditional`
- 仍保留 `chat-flow`

### 3. 路由模式

已修正：

- 只有真正 `file://` 桌面打包环境才使用 `hash`
- 本地 `http://127.0.0.1:8090` 应走 `history`

相关文件：

```text
src/frontend/src/router/index.ts
```

## 当前最适合继续推进的事情

### A. 设置窗口前端验收

优先目标：

1. 左下角点击 `设置`
2. 弹出设置窗口
3. 背景虚化
4. 左栏切换 `智能体 / 模型 / 知识库 / MCP / 工具 / Skill / 数据看板 / 个人资料 / 对话记录`
5. 右侧对应内容正常切换
6. 点击右上角关闭
7. 点击遮罩空白关闭
8. 侧边栏宽度变化时，设置窗口仍保持正常布局

### B. RAG / GraphRAG 评测继续推进

优先顺序：

1. 基于 `mixed_tuning_v2` 生成 30 - 50 条小样本评测问题
2. 配置第一轮 profile 对比
3. 先选最优参数
4. 再扩到大样本正式评测

## 小样本资料位置

```text
F:\resume project\03_rag_eval_dataset\prepared\mixed_tuning_v2
```

## 下一轮对话最适合使用的方式

如果下一轮要专门做前端设置窗口测试，建议：

- 新开一个对话
- 明确要求使用 Chrome / 真实浏览器能力做验证
- 不再把 Codex 内置浏览器当作主标准

## 给下一轮对话的建议提示词

下面这段可以直接复制到新对话里：

```text
请接着处理 Zuno 的设置窗口测试与收尾，不要重新从头分析。

先阅读这几份文件：
1. F:\\resume project\\02_projects\\Zuno\\docs\\superpowers\\plans\\2026-05-27-zuno-settings-rag-test-handoff.md
2. F:\\resume project\\02_projects\\Zuno\\docs\\superpowers\\specs\\2026-05-27-zuno-rag-graphrag-eval-task.md
3. F:\\resume project\\02_projects\\Zuno\\docs\\superpowers\\specs\\2026-05-26-zuno-rag-graphrag-knowledge-config-design.md

当前前提：
- 普通 Chrome 中页面表现正常或更接近正确
- Codex 内置浏览器表现异常，不作为主验收标准
- 现在要优先用真实 Chrome / Chrome 插件能力继续验证设置窗口

本轮任务目标：
1. 用真实 Chrome 验证 Zuno 左下角“设置”入口弹出的设置窗口
2. 检查背景虚化、弹窗关闭、左栏栏目切换、右侧页面切换是否正常
3. 检查侧边栏宽度变化时，设置窗口布局是否仍正常
4. 如果发现问题，直接修改前端并重新验证
5. 最后给出一份简短验收结果

重点页面：
- http://127.0.0.1:8090/workspace

重点要求：
- 不要再把“整页设置中心”当目标
- 目标是“工作台里的设置弹窗”
- 如果需要自动化，请优先使用真实浏览器能力而不是 Codex 内置浏览器
```

## 如果下一轮改做 RAG 评测

可用这段提示词：

```text
请接着推进 Zuno 的 RAG / GraphRAG 自动化评测，不要重新从头规划。

先阅读：
1. F:\\resume project\\02_projects\\Zuno\\docs\\superpowers\\plans\\2026-05-27-zuno-settings-rag-test-handoff.md
2. F:\\resume project\\02_projects\\Zuno\\docs\\superpowers\\specs\\2026-05-27-zuno-rag-graphrag-eval-task.md
3. F:\\resume project\\02_projects\\Zuno\\docs\\superpowers\\specs\\2026-05-26-zuno-rag-evaluation-langsmith-design.md

本轮目标：
1. 基于 F:\\resume project\\03_rag_eval_dataset\\prepared\\mixed_tuning_v2 生成一版 30-50 条小样本评测问题
2. 设计第一轮 profile 对比配置
3. 覆盖纯 RAG、RAG + Rerank、RAG + GraphRAG
4. 指标固定为 Recall@K、Context Precision@K、MRR@K、NDCG@K、Citation Accuracy
5. 单独标记 graph_relation 类型问题，用于判断 GraphRAG 是否真的更优

最后输出：
- 问题集草稿路径
- profile 配置草稿
- 下一步运行命令或脚本建议
```
