# OpenClaw Utility Skills

[中文说明](#中文说明) | [English](#english)

---

## 中文说明

这是一组可复用的 OpenClaw / AgentSkills，小而专注，主要解决两个常见工作流：

1. 用 Codex / ChatGPT OAuth 生成图片；
2. 用 PicGo 把本地图片上传到图床，再写入 Markdown / Obsidian。

适合 AI Agent 写笔记、生成架构图海报、整理 Obsidian 文档、发布带图 Markdown 时使用。

## 包含的 Skills

### `codex-image`

通过已有的 Codex / ChatGPT OAuth 凭证生成图片，不需要额外配置图片生成 API Key。

适合：

- AI 生图
- 架构海报
- 技术封面图
- 笔记 / 文档里的视觉素材

> 注意：如果你要的是可维护的逻辑流程图，优先用 Mermaid / 文本图；如果你要的是好看的图片、海报、视觉资产，再用 `codex-image`。

### `picgo-md-image`

通过 PicGo GUI 的本地服务上传图片，拿到公开图片 URL，然后写入 Markdown 或 Obsidian 笔记。

适合：

- Markdown 图片链接
- Obsidian 发布流程
- 分享文档前把本地图片路径替换成公网 URL
- 让 AI 生成的图片可以稳定展示在 README / 公开笔记里

## 安装

把需要的 skill 复制到你的 Agent skills 目录，例如：

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -R skills/codex-image ~/.openclaw/workspace/skills/
cp -R skills/picgo-md-image ~/.openclaw/workspace/skills/
```

如果你的 Agent 运行时使用其他 skills 路径，请按实际情况调整。

## 使用方法

### 用 Codex OAuth 生成图片

```bash
python3 skills/codex-image/scripts/codex_image.py \
  --size 1024x1536 \
  --quality high \
  --out ./architecture.png \
  "A polished technical architecture poster, modern style"
```

认证来源按顺序尝试：

1. `OPENAI_API_KEY`
2. `CODEX_AUTH_FILE`
3. `~/.codex/auth.json`
4. 可选的 OpenClaw Codex OAuth profile

不要提交 auth 文件、API Key、token 或本地私有配置。

### 用 PicGo 上传图片并获取 Markdown URL

先启动 PicGo GUI，并确保本地服务已开启，默认地址通常是：

```text
http://127.0.0.1:36677
```

然后运行：

```bash
python3 skills/picgo-md-image/scripts/picgo_upload.py ./architecture.png
```

脚本会输出公开图片 URL：

```text
https://pic.example.com/architecture.png
```

写入 Markdown：

```md
![Architecture diagram](https://pic.example.com/architecture.png)
```

## 推荐的笔记发布流程

当你要发布一篇带图的 Markdown / Obsidian 笔记时，推荐按这个顺序：

1. 写入或更新笔记正文；
2. 如果需要好看的视觉图，用 `codex-image` 生成；
3. 用 `picgo-md-image` 上传图片；
4. 把返回的公网 URL 写入 Markdown；
5. 如果 vault 有目录索引 / TOC，先更新索引；
6. 最后再生成或刷新公开分享链接。

这样可以避免分享出去的笔记里出现本地图片路径失效的问题。

## 安全检查

发布前请确认：

- 不要提交 token、API Key、OAuth 文件、PicGo 配置、cookie 或密码；
- 不要在未确认的情况下把隐私图片、内部截图、公司文档上传到公开图床；
- 不要硬编码本机用户名、机器路径、个人域名、聊天 ID 或组织内部信息；
- `codex-image` 使用的 ChatGPT / Codex backend endpoint 属于非官方接口，可能随时变化。

---

## English

Two small, reusable AgentSkills for image-generation and Markdown image-publishing workflows.

## Included skills

### `codex-image`

Generate images through Codex/ChatGPT OAuth credentials, without configuring a separate image API key.

Good for:

- AI image generation
- architecture posters
- technical cover images
- visual assets for notes and docs

### `picgo-md-image`

Upload local images through the PicGo GUI local server and embed the returned public URL into Markdown or Obsidian notes.

Good for:

- Markdown image links
- Obsidian publishing workflows
- replacing local image paths before sharing docs
- making generated images usable in public notes/READMEs

## Install

Copy the skills you want into your agent skills directory, for example:

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -R skills/codex-image ~/.openclaw/workspace/skills/
cp -R skills/picgo-md-image ~/.openclaw/workspace/skills/
```

Adapt the target directory if your agent runtime uses a different skills path.

## Usage

### Generate an image with Codex OAuth

```bash
python3 skills/codex-image/scripts/codex_image.py \
  --size 1024x1536 \
  --quality high \
  --out ./architecture.png \
  "A polished technical architecture poster, modern style"
```

Authentication is resolved from:

1. `OPENAI_API_KEY`
2. `CODEX_AUTH_FILE`
3. `~/.codex/auth.json`
4. Optional OpenClaw Codex OAuth profile

Do not commit auth files, API keys, tokens, or local configuration.

### Upload an image with PicGo and get a Markdown URL

Start PicGo GUI and make sure the local server is enabled, usually at:

```text
http://127.0.0.1:36677
```

Then run:

```bash
python3 skills/picgo-md-image/scripts/picgo_upload.py ./architecture.png
```

The script prints a public URL:

```text
https://pic.example.com/architecture.png
```

Use it in Markdown:

```md
![Architecture diagram](https://pic.example.com/architecture.png)
```

## Recommended note publishing workflow

When generating an image for a Markdown/Obsidian note:

1. Write or update the note body.
2. Generate images with `codex-image` if a polished visual asset is needed.
3. Upload images with `picgo-md-image`.
4. Reference the returned public URLs in Markdown.
5. Update the index/table-of-contents note if your vault uses one.
6. Generate or refresh the public share link only after image URLs are in place.

This avoids broken shared notes caused by local image embeds.

## Security checklist before publishing

- Do not commit tokens, API keys, OAuth files, PicGo configs, cookies, or passwords.
- Do not upload private or sensitive images to public image hosts without confirmation.
- Do not hard-code local usernames, machine paths, personal domains, chat IDs, or organization-specific secrets.
- Treat the ChatGPT/Codex backend endpoint used by `codex-image` as unofficial and subject to change.

## License

MIT
