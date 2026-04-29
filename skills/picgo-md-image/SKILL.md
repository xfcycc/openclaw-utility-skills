---
name: picgo-md-image
description: Upload local images through the PicGo GUI local server, get public image URLs, and embed them into Markdown or Obsidian notes. Use when the user mentions PicGo, image hosting, image URL, Markdown images, Obsidian image embeds, or replacing local image paths with public URLs.
---

# PicGo Markdown Image

Upload local images through the **PicGo GUI local HTTP server**, receive public image URLs, and write those URLs into Markdown or Obsidian notes.

## Use when

- The user asks to upload an image with PicGo.
- The user wants an image URL for Markdown, README, docs, or Obsidian.
- A note should not contain local image paths.
- A publishing workflow requires images to be hosted before sharing.

Example Markdown output:

```md
![Architecture diagram](https://pic.example.com/image.png)
```

Example Obsidian callout:

```md
> [!example] Architecture diagram
> ![Architecture diagram](https://pic.example.com/image.png)
```

## Do not use when

- The image should remain private.
- The user wants to send the image directly through a chat app. Use that chat/channel's file or image sending tool instead.
- The user has not agreed to upload potentially sensitive images to a public or semi-public image host.

## Prerequisites

PicGo GUI local server must be running. Default endpoint:

```text
http://127.0.0.1:36677
```

You can override it with:

```bash
export PICGO_SERVER="http://127.0.0.1:36677"
```

Never read, print, or commit PicGo config secrets such as OSS keys, tokens, access keys, or passwords.

## Quick start

```bash
python3 {SKILL_DIR}/scripts/picgo_upload.py /absolute/path/to/image.png
```

The script prints one URL per line, for example:

```text
https://pic.example.com/20260428230308390.png
```

Then write the URL into Markdown:

```md
![Image description](https://pic.example.com/20260428230308390.png)
```

## Underlying PicGo API

```bash
curl -sS -X POST http://127.0.0.1:36677/upload \
  -H 'Content-Type: application/json' \
  -d '{"list":["/absolute/path/to/image.png"]}'
```

Typical response:

```json
{
  "success": true,
  "result": ["https://pic.example.com/image.png"]
}
```

## Recommended publishing workflow

When creating a published note or document:

1. Write or update the Markdown content.
2. Upload local images through PicGo.
3. Replace local paths with public image URLs.
4. Update any index or table-of-contents note if needed.
5. Generate or refresh the final share link only after the Markdown references public URLs.

## Safety notes

- Image host URLs are usually public or semi-public.
- Confirm before uploading sensitive screenshots, personal photos, internal documents, or private architecture diagrams.
- This skill only handles image hosting and Markdown references; it does not send chat messages or upload files to collaboration platforms.
