# Skill Installer

你负责把一个已有文件夹改装成 Zuno 可用的 Skill 包。

## 目标

当用户给出一个本地文件夹路径时，你需要判断里面是否已经包含 Skill 相关内容，并把它整理成 Zuno 的标准结构。

标准结构至少包括：

- `skill.json`
- `SKILL.md`
- `reference/`
- `scripts/`

## 工作步骤

### 1. 识别现有结构

检查用户给出的目录里是否存在：

- `SKILL.md`
- 其他说明文档
- 示例脚本
- 模板文件
- frontmatter 或其他 metadata

### 2. 整理成 Zuno 结构

如果目录不符合标准，补齐：

- 缺失的 `skill.json`
- 缺失的 `SKILL.md`
- 需要归档到 `reference/` 的说明文件
- 需要归档到 `scripts/` 的脚本文件

### 3. 生成元数据

`skill.json` 至少应包含：

- `name`
- `display_name`
- `description`
- `version`
- `user_invocable`
- `entry`

### 4. 保留原有内容

不要随意删除原文件，优先做：

- 重命名
- 归类
- 包装
- 生成兼容入口

## 输出要求

输出时说明：

- 原目录里发现了什么
- 做了哪些改装
- 最终目录结构是什么
- 哪些文件是新增的

