#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
github_upload.py — 将本地文件夹/zip 一键推送到 GitHub
- 自动生成中英双语 README / LICENSE / .gitignore
- 支持 PAT 记忆（~/.codex/skills/github-upload/.github-pat）
- 支持 gh CLI 优先，无 gh 时回退到 git+API
"""
import argparse, os, re, sys, json, shutil, subprocess, tempfile, zipfile
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).resolve().parents[1]
TOKEN_FILE = SKILL_DIR / ".github-pat"
REF_DIR = SKILL_DIR / "references"
TEMPLATE = REF_DIR / "readme-template.md"

def run(cmd, cwd=None, check=True, capture=False):
    if isinstance(cmd, str):
        import shlex
        # keep string for shell on windows
        pass
    result = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd,str), capture_output=capture, text=True, encoding="utf-8", errors="replace")
    if check and result.returncode != 0:
        msg = result.stderr if capture else ""
        raise RuntimeError(f"Command failed ({result.returncode}): {cmd}\n{msg}")
    return result

def mask_token(t):
    if not t or len(t) < 8:
        return "***"
    return t[:4] + "***" + t[-2:]

def load_token(cli_token=None):
    if cli_token:
        return cli_token.strip()
    env = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    if env.strip():
        return env.strip()
    if TOKEN_FILE.exists():
        try:
            v = TOKEN_FILE.read_text(encoding="utf-8").strip()
            if v:
                return v
        except Exception:
            pass
    return ""

def save_token(token):
    SKILL_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(token.strip(), encoding="utf-8")
    try:
        if os.name == "nt":
            user = os.environ.get("USERNAME","")
            if user:
                run(f'icacls "{TOKEN_FILE}" /inheritance:r /grant:r "{user}:(R,W)"', check=False)
        else:
            os.chmod(TOKEN_FILE, 0o600)
    except Exception:
        pass

def prompt(msg, default=""):
    suffix = f" [{default}]" if default else ""
    try:
        v = input(f"{msg}{suffix}: ").strip()
    except EOFError:
        v = ""
    return v if v else default

def tree_text(root: Path, max_depth=3):
    lines=[]
    def walk(p, prefix="", depth=0):
        if depth>max_depth: return
        items=sorted([x for x in p.iterdir() if x.name not in {".git","__pycache__",".DS_Store","node_modules",".venv"}])
        for i, it in enumerate(items):
            last=i==len(items)-1
            lines.append(f"{prefix}{'└── ' if last else '├── '}{it.name}")
            if it.is_dir():
                walk(it, prefix+("    " if last else "│   "), depth+1)
    lines.append(root.name+"/")
    walk(root)
    return "\n".join(lines)

def render_readme(repo_name, zh_desc, en_desc, proj_root: Path):
    tpl = TEMPLATE.read_text(encoding="utf-8") if TEMPLATE.exists() else "# {{REPO_NAME}}\n\n{{ZH_TAGLINE}}"
    # auto detect
    has_py = any(proj_root.rglob("*.py"))
    has_ps1 = any(proj_root.rglob("*.ps1"))
    zh_what = zh_desc or f"{repo_name} 项目。"
    en_what = en_desc or f"Project {repo_name}."
    install = 'install.cmd\n# 或\npowershell -ExecutionPolicy Bypass -File install.ps1' if has_ps1 else ('pip install -e .\n# 或\npython -m pip install -r requirements.txt' if has_py else '解压后直接使用')
    tree = tree_text(proj_root)
    mapping={
        "{{REPO_NAME}}": repo_name,
        "{{ZH_TAGLINE}}": zh_desc or repo_name,
        "{{EN_TAGLINE}}": en_desc or repo_name,
        "{{ZH_WHAT}}": zh_what,
        "{{EN_WHAT}}": en_what,
        "{{ZH_USAGE}}": "按 README 指引使用。",
        "{{EN_USAGE}}": "Follow the README.",
        "{{ZH_FEATURES}}": "- 见项目文件",
        "{{EN_FEATURES}}": "- See project files",
        "{{ZH_INSTALL}}": install,
        "{{EN_INSTALL}}": install,
        "{{ZH_TREE}}": tree,
        "{{EN_TREE}}": tree,
        "{{LINKS}}": "- GitHub: https://github.com/",
        "{{LICENSE_NOTE}}": "MIT — see LICENSE.",
    }
    out=tpl
    for k,v in mapping.items():
        out=out.replace(k, v)
    return out

def prepare_source(src: Path):
    """return Path to folder to push"""
    if src.is_file() and src.suffix.lower()==".zip":
        tmp=tempfile.mkdtemp(prefix="gh-upload-")
        tmpP=Path(tmp)
        with zipfile.ZipFile(src, 'r') as z:
            z.extractall(tmpP)
        # if single top dir, lift
        items=list(tmpP.iterdir())
        if len(items)==1 and items[0].is_dir():
            return items[0]
        return tmpP
    if src.is_dir():
        return src
    raise SystemExit(f"来源不存在: {src}")

def ensure_git_repo(proj: Path, repo_name, zh_desc, en_desc, force_readme=False):
    proj=Path(proj)
    # README
    readme = proj/"README.md"
    if not readme.exists() or force_readme:
        readme.write_text(render_readme(repo_name, zh_desc, en_desc, proj), encoding="utf-8")
        print(f"[readme] 已生成 {readme}")
    else:
        print(f"[readme] 已存在，跳过（加 --force-readme 覆盖）: {readme}")
    # LICENSE
    lic = proj/"LICENSE"
    if not lic.exists():
        year=datetime.now().year
        lic.write_text(f"MIT License\n\nCopyright (c) {year} {repo_name} contributors\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the \"Software\"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n","utf-8")
        print(f"[license] 已生成 {lic}")
    # .gitignore
    gi = proj/".gitignore"
    if not gi.exists():
        gi.write_text(".DS_Store\nThumbs.db\n*.log\n__pycache__/\n.venv/\nnode_modules/\n.env\n", encoding="utf-8")
    # git init
    if not (proj/".git").exists():
        run("git init", cwd=proj)
        run('git branch -M main', cwd=proj, check=False)
    # config if missing
    def cfg(k):
        r=run(f'git config {k}', cwd=proj, check=False, capture=True)
        return r.stdout.strip() if r.returncode==0 else ""
    if not cfg("user.name"):
        run('git config user.name "github-upload"', cwd=proj, check=False)
    if not cfg("user.email"):
        run('git config user.email "github-upload@local"', cwd=proj, check=False)
    run("git add .", cwd=proj)
    # commit if needed
    r=run("git status --porcelain", cwd=proj, capture=True, check=False)
    if r.stdout.strip():
        run('git commit -m "feat: initial commit via github-upload skill"', cwd=proj)
        print("[git] 已提交")
    else:
        print("[git] 无需提交（工作区干净）")
    return proj

def detect_gh():
    return shutil.which("gh") is not None

def create_and_push(proj: Path, repo_arg: str, token: str, visibility="public", push_only=False):
    repo_arg=repo_arg.strip()
    gh_available=detect_gh()
    # repo_arg may be "name" or "owner/name"
    owner_repo=None
    repo_name=repo_arg
    if "/" in repo_arg:
        owner_repo=repo_arg
        repo_name=repo_arg.split("/")[-1]
    else:
        # need owner
        if gh_available:
            try:
                owner=run("gh api user --jq .login", capture=True, check=False).stdout.strip()
                if owner:
                    owner_repo=f"{owner}/{repo_name}"
            except Exception:
                pass
        if not owner_repo:
            # try token api
            if token:
                try:
                    import urllib.request, json as js
                    req=urllib.request.Request("https://api.github.com/user", headers={"Authorization": f"token {token}", "Accept":"application/vnd.github.v3+json"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        data=js.loads(resp.read().decode())
                        owner=data.get("login")
                        if owner: owner_repo=f"{owner}/{repo_name}"
                except Exception as e:
                    print(f"[warn] 获取用户名失败: {e}")

    remote_url=""
    if gh_available and token:
        # use gh auth login with token via env
        env=os.environ.copy()
        env["GITHUB_TOKEN"]=token
        # create repo
        vis_flag="--public" if visibility=="public" else "--private"
        cmd=f'gh repo create "{owner_repo or repo_name}" {vis_flag} --source "{proj}" --remote origin --push'
        print(f"[gh] {cmd}")
        r=run(cmd, cwd=proj, check=False, capture=True)
        print(r.stdout)
        if r.stderr: print(r.stderr, file=sys.stderr)
        if r.returncode==0:
            print(f"[done] https://github.com/{owner_repo or repo_name}")
            return f"https://github.com/{owner_repo or repo_name}"
        else:
            print("[gh] 失败，回退到 git+API 方式")

    # fallback: create via API then git push
    if not token:
        print("未提供 PAT，无法创建远端仓库。请先配置 PAT：见 references/token-setup.md")
        print("或手动在 GitHub 新建空仓库后执行: git remote add origin <url> && git push -u origin main")
        return ""

    # create repo via REST
    try:
        import urllib.request, urllib.error, json as js
        payload=json.dumps({"name": repo_name, "private": visibility=="private"}).encode()
        req=urllib.request.Request("https://api.github.com/user/repos",
            data=payload,
            headers={"Authorization": f"token {token}", "Accept":"application/vnd.github.v3+json", "Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data=js.loads(resp.read().decode())
            html_url=data.get("html_url","")
            clone_url=data.get("clone_url","")
            print(f"[api] 已创建 {html_url}")
            remote_url=clone_url
    except Exception as e:
        # maybe already exists
        print(f"[api] 创建失败（可能已存在）: {e}")
        # try to infer remote
        if owner_repo:
            remote_url=f"https://{token}@github.com/{owner_repo}.git"
        else:
            print("请手动确认仓库是否已存在，或传入完整 owner/repo")
            return ""

    if not remote_url and owner_repo:
        remote_url=f"https://{token}@github.com/{owner_repo}.git"

    # git remote add / push
    if remote_url:
        # ensure remote origin
        r=run("git remote get-url origin", cwd=proj, check=False, capture=True)
        if r.returncode==0:
            run(f'git remote set-url origin "{remote_url}"', cwd=proj, check=False)
        else:
            run(f'git remote add origin "{remote_url}"', cwd=proj, check=False)
        run("git branch -M main", cwd=proj, check=False)
        pr=run("git push -u origin main", cwd=proj, check=False, capture=True)
        print(pr.stdout)
        if pr.stderr: print(pr.stderr)
        if pr.returncode==0:
            # clean token from remote url
            run("git remote set-url origin " + f"https://github.com/{owner_repo}.git" if owner_repo else remote_url.replace(token+"@",""), cwd=proj, check=False)
            url = f"https://github.com/{owner_repo}" if owner_repo else html_url if 'html_url' in locals() else ""
            print(f"[done] {url}")
            return url
        else:
            print("[error] git push 失败，请检查 PAT 权限与仓库名是否已占用")
    return ""

def main():
    ap=argparse.ArgumentParser(description="一键上传到 GitHub（含双语 README 生成与 PAT 记忆）")
    ap.add_argument("source", nargs="?", help="本地文件夹或 zip 路径（省略则交互输入）")
    ap.add_argument("--repo", help="目标仓库名或 owner/repo")
    ap.add_argument("--visibility", choices=["public","private"], default="public")
    ap.add_argument("--zh-desc", dest="zh_desc", default="")
    ap.add_argument("--en-desc", dest="en_desc", default="")
    ap.add_argument("--token", default="")
    ap.add_argument("--force-readme", action="store_true")
    ap.add_argument("--push-only", action="store_true", help="仅推送已在 git 的项目（需在项目目录运行）")
    ap.add_argument("--no-save-token", action="store_true")
    args=ap.parse_args()

    if args.push_only:
        proj=Path.cwd()
        repo=args.repo or prompt("目标仓库名 (owner/repo 或仅仓库名)", proj.name)
        zh=args.zh_desc
        en=args.en_desc
        ensure_git_repo(proj, repo.split("/")[-1], zh, en, args.force_readme)
        token=load_token(args.token)
        if not token:
            token=prompt("粘贴 GitHub PAT (ghp_...)")
            if token and not args.no_save_token:
                if prompt("是否保存此 PAT 供下次免输入？ [Y/n]","Y").lower() in ("y","yes",""):
                    save_token(token)
                    print(f"[token] 已保存到 {TOKEN_FILE}  ({mask_token(token)})")
        else:
            print(f"[token] 已载入记忆的 PAT {mask_token(token)}  （传入 --token 可覆盖）")
        if not token:
            print("未提供 PAT，已跳过远端创建。请手动 git push。")
            return
        create_and_push(proj, repo, token, args.visibility)
        return

    src_str=args.source or prompt("本地文件夹或 zip 路径", "")
    if not src_str:
        print("未指定来源"); sys.exit(1)
    src=Path(src_str.strip().strip('"').strip("'"))
    proj=prepare_source(src)
    print(f"[source] {src} -> {proj}")

    repo=args.repo or prompt("目标仓库名 (owner/repo 或仅仓库名)", Path(proj).name)
    if not repo:
        print("未指定仓库名"); sys.exit(1)
    repo_short=repo.split("/")[-1]

    zh=args.zh_desc or prompt("中文一句话简介（用于 README）", f"{repo_short} 项目")
    en=args.en_desc or prompt("English one-line intro", f"Project {repo_short}")

    proj=ensure_git_repo(proj, repo_short, zh, en, args.force_readme)

    token=load_token(args.token)
    if not token:
        token=prompt("粘贴 GitHub PAT (ghp_...)  — 详见 references/token-setup.md")
        if not token:
            print("未提供 PAT，已完成本地提交。请稍后手动推送或配置 PAT 后加 --push-only 重推。")
            print(f"本地项目: {proj}")
            return
        if not args.no_save_token:
            if prompt("是否保存此 PAT 供下次免输入？ [Y/n]","Y").lower() in ("y","yes",""):
                save_token(token)
                print(f"[token] 已保存到 {TOKEN_FILE}  ({mask_token(token)})")
    else:
        print(f"[token] 已载入记忆的 PAT {mask_token(token)}")

    url=create_and_push(proj, repo, token, args.visibility)
    if url:
        print(f"\n✅ 完成：{url}")
    else:
        print(f"\n本地已就绪：{proj}  — 请手动推送")

if __name__=="__main__":
    main()
