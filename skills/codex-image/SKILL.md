---
name: codex-image
description: Generate images with Codex/ChatGPT OAuth instead of a separate image API key. Use when the user asks to generate images, draw, create AI artwork, produce architecture posters, or create visual assets through Codex/ChatGPT authentication.
---

# Codex Image

Generate images through the ChatGPT/Codex backend using an existing Codex OAuth login. This is useful when your agent environment already has `codex login` credentials and you do not want to configure a separate image-generation API key.

## Quick start

```bash
python3 {SKILL_DIR}/scripts/codex_image.py \
  --size 1024x1024 \
  --quality medium \
  --out ./output.png \
  "A clean product architecture poster, modern technical style"
```

`{SKILL_DIR}` means the directory containing this skill. If your agent does not expand it automatically, replace it with the actual path to this skill.

## Authentication

The script tries credentials in this order:

1. `OPENAI_API_KEY`, if set.
2. `CODEX_AUTH_FILE`, if set.
3. `~/.codex/auth.json`, usually created by `codex login`.
4. Optional OpenClaw Codex OAuth profile at `~/.openclaw/agents/main/agent/auth-profiles.json`.

Do not commit any auth files, tokens, API keys, or local config files.

## Options

- `--prompt` or positional prompt: image description.
- `--out`: output file path. Defaults to `~/.codex/generated_images/manual/...`.
- `--size`: common values include `1024x1024`, `1024x1536`, `1536x1024`, `1792x1024`, `1024x1792`.
- `--quality`: `low`, `medium`, or `high`.
- `--model`: defaults to a Codex-compatible chat model. If a `gpt-image-*` model is supplied, the script falls back to a chat model because image generation is invoked as a tool.
- `--timeout`: request timeout in seconds.

## Workflow guidance

- Use this skill for **visual images**: posters, illustrations, cover images, polished architecture diagrams, and other presentation-ready graphics.
- For maintainable logical diagrams, prefer Mermaid, Markdown tables, or plain text diagrams instead.
- If the generated image will be embedded in Markdown/Obsidian or published online, upload it to an image host first and reference the public URL.

## Safety notes

- This script uses locally available credentials; never print or share tokens.
- Generated images may contain imperfect text. For precise technical labels, consider generating a mostly visual image and adding final labels manually or with a deterministic renderer.
- The backend endpoint is unofficial and may change.
