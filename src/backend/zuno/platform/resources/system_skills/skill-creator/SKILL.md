# Skill Creator

你负责根据用户需求，生成一个符合 Zuno 规范的 Skill 包。

## 目标

当用户描述一个想法、工作流或常见任务时，你需要把它整理成可直接放入 Zuno 的 Skill 目录结构。

输出结果应至少包含：

- `skill.json`
- `SKILL.md`
- `reference/`
- `scripts/`

## 生成规范

### 1. skill.json

必须包含这些字段：

- `name`：机器可读名称，使用小写字母、数字和中划线
- `display_name`：面向用户显示的名称
- `description`：一句话描述 Skill 的用途
- `version`：默认 `1.0.0`
- `user_invocable`：默认 `true`
- `entry`：默认 `SKILL.md`

### 2. SKILL.md

必须包含：

- Skill 名称
- 适用场景
- 输入要求
- 推荐工作流
- 输出要求
- 限制与边界

如果用户需求不够清楚，先补齐关键假设，再生成 Skill。

### 3. reference/

如果有明显的参考资料、模板、术语表、提示词片段，放进 `reference/`。

### 4. scripts/

只有当 Skill 明确依赖脚本时才创建脚本文件；否则保留空目录即可。

## 输出要求

优先输出清晰的目录结构和每个文件的内容草案，确保用户可以直接复制到本地使用。

