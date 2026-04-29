# OpenClaw Utility Skills

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
