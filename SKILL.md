---
name: github-upload
description: 将本地文件夹/zip 一键上传到 GitHub，自动生成中英双语 README、LICENSE 并支持 PAT 记忆，下次无需重复输入。说"上传 GitHub/Github推送/推GitHub"时触发。
---

# GitHub Upload

将任意本地项目/文件夹/压缩包一键打包并推送到 GitHub，自动生成中英双语介绍、并可记忆 PAT 供下次免输入上传。

## 触发
- "上传到 GitHub" / "推到 GitHub" / "发布到 GitHub" / "github push"
- 用户指定本地路径 + 目标仓库名时自动进入上传流程

## 快速开始

```powershell
# 最简：交互式（会引导填路径、仓库名、介绍）
python "%USERPROFILE%\.codex\skills\github-upload\scripts\github_upload.py"

# 指定路径和仓库
python "%USERPROFILE%\.codex\skills\github-upload\scripts\github_upload.py" "D:/我的项目" --repo "my-project"

# 指定仓库全名（用户名/仓库名）
python "%USERPROFILE%\.codex\skills\github-upload\scripts\github_upload.py" "D:/我的项目" --repo "yourname/my-project" --visibility public

# 已有配置文件时一键推送
python "%USERPROFILE%\.codex\skills\github-upload\scripts\github_upload.py" --push-only
```

## 工作流程

1. 解析来源：文件夹原样推送 / zip 先解压（若 zip 内仅含一级目录则自动提升）
2. 询问或读取配置：仓库名、是否新建仓库、中文简介、英文简介、可见性
3. **创建介绍**（新增能力）：基于 `references/readme-template.md` 模板 + 用户提供的简介，自动生成中英双语 `README.md`（含安装/目录/链接段）、`LICENSE`、`.gitignore`；详见 `references/readme-guide.md`
4. 本地 git 初始化、首次提交
5. 读取已记忆的 PAT（见下）或提示输入，新建远端仓库并 `git push -u origin main`
6. 输出仓库地址

## PAT 记忆（新增能力）

- 首次上传时脚本会询问是否保存 GitHub PAT（Personal Access Token，classic 需 `repo` 权限，fine-grained 需 Repository 读写）
- 保存位置：`%USERPROFILE%/.codex/skills/github-upload/.github-pat`（仅本机可读，权限自动设为当前用户私有）
- 也可手动写入，见 `references/token-setup.md`
- 下次调用时自动读取，无需再次输入；如需更换，删除该文件或传入 `--token <新PAT>`
- 永不在日志/README 中明文回显 PAT

## 更多说明

- 详细介绍与 PAT 填写位置见 `references/token-setup.md`
- 双语 README 模板与字段说明见 `references/readme-template.md` 与 `references/readme-guide.md`
- 失败时按提示检查 token 权限、仓库名是否已存在、网络代理
