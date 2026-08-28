# GitHub PAT 配置说明

本技能可记忆你的 GitHub Personal Access Token（PAT），下次上传无需重复输入。

## 保存位置

- 默认路径：`%USERPROFILE%\.codex\skills\github-upload\.github-pat`
- 文件内容仅一行：你的 PAT 明文（前后会自动去除空白）
- 权限：脚本会在 Windows 上自动执行 `icacls` 仅保留当前用户可读；Linux/macOS 设为 `600`

## 三种填写方式

### 方式 A：上传时交互保存（推荐）
首次运行上传脚本时按提示粘贴 PAT，脚本会询问：
```
是否保存此 PAT 供下次免输入？ [Y/n]:
```
选 Y 即写入上述文件。

### 方式 B：手动写入
```powershell
# PowerShell（Windows）
Set-Content -Path "$env:USERPROFILE\.codex\skills\github-upload\.github-pat" -Value "ghp_xxxxxxxxxxxxxxxxxxxx" -NoNewline
icacls "$env:USERPROFILE\.codex\skills\github-upload\.github-pat" /inheritance:r /grant:r "$env:USERNAME:(R,W)"

# Bash（macOS/Linux）
echo -n "ghp_xxxxxxxxxxxxxxxxxxxx" > ~/.codex/skills/github-upload/.github-pat
chmod 600 ~/.codex/skills/github-upload/.github-pat
```

### 方式 C：环境变量（单次生效，不落盘）
```powershell
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
python "%USERPROFILE%\.codex\skills\github-upload\scripts\github_upload.py" "D:/我的项目" --repo "my-project"
```

## 如何获取 PAT

1. 打开 https://github.com/settings/tokens
2. **Classic**：Generate new token (classic) → 勾选 `repo`（含私有仓库读写）→ 生成后复制 `ghp_...`
3. **Fine-grained**：Generate new token → 选定仓库或 All repositories → Repository permissions 勾选 Contents: Read and write、Metadata: Read

## 更换 / 删除

```powershell
# 更换：直接覆盖文件或传入 --token
python "%USERPROFILE%\.codex\skills\github-upload\scripts\github_upload.py" --token "ghp_新token" --push-only

# 删除记忆
Remove-Item "$env:USERPROFILE\.codex\skills\github-upload\.github-pat" -Force
```

## 安全提示

- PAT 等同密码，请勿提交到仓库、勿截图明文
- 脚本在日志中会对 PAT 做脱敏（仅显示前 4 位）
- 如 PAT 泄露，立即到 GitHub Settings → Tokens 页面 Revoke
