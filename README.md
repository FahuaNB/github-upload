# github-upload

> 一键将本地文件夹/zip 推送到 GitHub 的 Codex 技能 · 自动生成中英双语 README 并可记忆 PAT
> One-click push local folders/zips to GitHub with bilingual README and PAT persistence

---

## 中文介绍

### 是什么
`github-upload` 将本地文件夹或 `.zip` 一键推送到 GitHub，自动生成中英双语 `README.md` / `LICENSE` / `.gitignore`，并可记忆 GitHub PAT（Personal Access Token），下次无需重复输入。

### 触发
- “上传到 GitHub” / “推到 GitHub” / “发布到 GitHub” / “github push”

### 快速开始
```powershell
# 交互式（引导填路径、仓库名、简介）
python "%USERPROFILE%\.codex\skills\github-upload\scripts\github_upload.py"

# 指定路径和仓库
python "%USERPROFILE%\.codex\skills\github-upload\scripts\github_upload.py" "D:/我的项目" --repo "FahuaNB/my-project" --visibility public
```

### 安装
> 快捷安装脚本已移除，请手动复制技能文件夹。

```powershell
Copy-Item -Path ".\github-upload" -Destination "$env:USERPROFILE\.codex\skills\github-upload" -Recurse -Force
# 重启 Codex 后生效
```

### PAT 记忆
- 首次推送时会询问是否保存 PAT，下次自动读取
- 保存位置：`%USERPROFILE%\.codex\skills\github-upload\.github-pat`（仅本机可读）
- 详见 `references/token-setup.md`

### 双语介绍生成
- 模板：`references/readme-template.md`
- 说明：`references/readme-guide.md`

### 目录结构
```
push-github-upload/
├── .gitignore
├── LICENSE
├── README.md
├── references
│   ├── readme-guide.md
│   ├── readme-template.md
│   └── token-setup.md
├── scripts
│   └── github_upload.py
└── SKILL.md
```

---

## English

### What is this
`github-upload` pushes local folders or `.zip` to GitHub, auto-generates bilingual `README.md` / `LICENSE`, and persists your GitHub PAT for next use.

### Trigger
- "push to GitHub" / "upload to GitHub"

### Quick Start
```powershell
python "%USERPROFILE%\.codex\skills\github-upload\scripts\github_upload.py" "D:/my-project" --repo "FahuaNB/my-project"
```

### Install
> Quick-install scripts have been removed. Copy the skill folder manually.

```powershell
Copy-Item -Path ".\github-upload" -Destination "$env:USERPROFILE%\.codex\skills\github-upload" -Recurse -Force
```

### PAT Persistence
- Saved to `%USERPROFILE%\.codex\skills\github-upload\.github-pat` (private)
- See `references/token-setup.md`

### Structure
```
push-github-upload/
├── .gitignore
├── LICENSE
├── README.md
├── references
│   ├── readme-guide.md
│   ├── readme-template.md
│   └── token-setup.md
├── scripts
│   └── github_upload.py
└── SKILL.md
```

---

## License
MIT
