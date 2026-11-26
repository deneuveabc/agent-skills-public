# Agent Skills

[English](README.en.md)

供多种 Agent 使用的可复用工作流。每个 Skill 位于 `skills/<skill-name>/SKILL.md`，可以包含脚本。仓库只保存通用说明和代码；音频、逐字稿、shownote、账号信息及个人本机路径留在各自的私有工作区。

## 已收录

| Skill | 用途 |
| --- | --- |
| [podcast-editing](skills/podcast-editing/SKILL.md) | 依据本期要求剪辑播客音频、处理停顿与响度，并映射章节时间轴。 |
| [xiaoyuzhou-podcast-upload](skills/xiaoyuzhou-podcast-upload/SKILL.md) | 核对本地成片和 shownote，上传小宇宙单集并确认后台状态。 |

## 本地使用

在能访问本期文件的工作区调用相应 Skill，并提供本期音频、逐字稿或成片所在目录。`podcast-editing` 中的示例时间仅演示命令用法，实际剪点由本期材料和用户确认决定。`xiaoyuzhou-podcast-upload` 不会因为发现新文件就自动发布。

Codex、Cursor 和 Antigravity 可根据各自当前版本的发现规则加载 `skills/` 中的目录；Claude Code 可将相应 Skill 目录安装在 `.claude/skills/`。安装方式与权限以运行环境为准。

新增或更新 Skill 时，先按 [发布与脱敏检查](PUBLISHING.md) 检查当前文件和 Git 历史，再同步维护中英文 README。仓库中的 [AGENTS.md](AGENTS.md) 及 [CLAUDE.md](CLAUDE.md) 为不同 Agent 提供入口。

上传小宇宙单集需要访问本地文件和创作者中心。后台创建成功后，单集仍可能处于转码或审核阶段。

## 许可

本仓库的说明与脚本采用 [MIT License](LICENSE)。使用、修改和再发布时请保留版权及许可声明。
