# 双语 README 生成说明

上传流程中的"创建介绍"步骤会基于本技能的模板自动生成中英双语 README。

## 模板位置
- `references/readme-template.md` — 占位符模板

## 占位符一览
| 占位符 | 含义 | 来源 |
|---|---|---|
| `{{REPO_NAME}}` | 仓库名 | --repo 参数或交互输入 |
| `{{ZH_TAGLINE}}` / `{{EN_TAGLINE}}` | 中英文一句话简介 | 交互输入的 zh_desc / en_desc |
| `{{ZH_WHAT}}` / `{{EN_WHAT}}` | 详细介绍段 | 同上，支持多句 |
| `{{ZH_USAGE}}` / `{{EN_USAGE}}` | 使用说明 | 自动推断或用户补充 |
| `{{ZH_FEATURES}}` / `{{EN_FEATURES}}` | 要点列表 | 自动扫描文件或用户补充 |
| `{{ZH_INSTALL}}` / `{{EN_INSTALL}}` | 安装命令 | 按项目类型推断 |
| `{{ZH_TREE}}` / `{{EN_TREE}}` | 目录树 | 自动生成 |
| `{{LINKS}}` | 相关链接 | 用户输入或留空 |
| `{{LICENSE_NOTE}}` | 许可证说明 | 默认 MIT |

## 生成时机
1. 脚本检测目标目录下无 `README.md`，或用户传入 `--force-readme` 时触发
2. 交互式会依次询问：中文简介、英文简介、是否追加自定义段落
3. 非交互式可用参数：
```powershell
python scripts/github_upload.py ./myapp --repo myapp --zh-desc "一句话中文简介" --en-desc "One-line English intro" --force-readme
```

## 自定义
- 直接编辑 `references/readme-template.md` 改版式
- 或在目标项目里放好自己的 `README.md`，脚本会跳过覆盖（除非加 --force-readme）
