# Agent Skills

[简体中文](README.md)

Reusable workflows for multiple agents. Each skill lives at `skills/<skill-name>/SKILL.md` and may include scripts. This repository stores general instructions and code; audio, transcripts, show notes, account details, and personal local paths stay in private workspaces.

## Included skills

| Skill | Purpose |
| --- | --- |
| [podcast-editing](skills/podcast-editing/SKILL.md) | Edit an episode's audio, adjust pauses and loudness, and map chapter timestamps using episode-specific instructions. |
| [xiaoyuzhou-podcast-upload](skills/xiaoyuzhou-podcast-upload/SKILL.md) | Check a final audio file and show notes, upload an episode to Xiaoyuzhou, and verify its status. |

## Local use

Open an agent in a workspace with access to the episode files and invoke the relevant skill. Provide the episode's audio, transcript, or final-audio directory. Times in `podcast-editing` are command examples; actual cuts require episode evidence and user confirmation. Finding new files never authorizes automatic publication by `xiaoyuzhou-podcast-upload`.

Codex, Cursor, and Antigravity can load directories from `skills/` according to their current discovery rules. Claude Code can install the relevant skill directory under `.claude/skills/`. Check the current agent version and local permissions for installation details.

Before adding or updating a skill, follow the [publishing and privacy checklist](PUBLISHING.md) for both current files and Git history, then update both READMEs. [AGENTS.md](AGENTS.md) and [CLAUDE.md](CLAUDE.md) provide agent entry points.

Uploading an episode requires access to the local files and Xiaoyuzhou Creator Center. A newly created episode may still be transcoding or under review.
