#!/usr/bin/env python3
"""基于 Codex auth.json 认证的图片生成工具。

通过 ChatGPT 后端 Responses API + image_generation 工具出图，
使用 ~/.codex/auth.json 中的 OAuth access_token 认证。
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import uuid
import ssl
from pathlib import Path
from typing import Any, NoReturn
from urllib import error, request

try:
    import tomllib
except ModuleNotFoundError as exc:
    raise SystemExit("需要 Python 3.11+") from exc


# ── 常量 ──────────────────────────────────────────────────────────────────────
DEFAULT_MODEL = "gpt-5.4"
DEFAULT_SIZE = "1024x1024"
DEFAULT_QUALITY = "medium"
DEFAULT_FORMAT = "png"
DEFAULT_TIMEOUT = 600

# ChatGPT OAuth 认证
OPENAI_AUTH_TOKEN_URL = "https://auth.openai.com/oauth/token"
CHATGPT_BASE_URL = "https://chatgpt.com/backend-api/codex"
OPENAI_DEFAULT_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"

SIZE_PATTERN = re.compile(r"^\s*(\d+)\s*[xX×]\s*(\d+)\s*$")


# ── 工具函数 ──────────────────────────────────────────────────────────────────
def log(msg: str) -> None:
    print(f"[codex-image] {msg}", file=sys.stderr)


def fail(msg: str) -> NoReturn:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def random_suffix(n: int = 8) -> str:
    return uuid.uuid4().hex[:n]


# ── JWT 解析 ──────────────────────────────────────────────────────────────────
def decode_jwt_payload(token: str) -> dict[str, Any]:
    """解析 JWT payload（不验证签名）"""
    parts = token.split(".")
    if len(parts) != 3:
        return {}
    b = parts[1]
    b += "=" * (4 - len(b) % 4) if len(b) % 4 else ""
    try:
        return json.loads(base64.urlsafe_b64decode(b))
    except (ValueError, json.JSONDecodeError):
        return {}


def is_token_expired(token: str, margin: int = 60) -> bool:
    """检查 JWT 是否过期（含安全边际）"""
    exp = decode_jwt_payload(token).get("exp")
    return not isinstance(exp, (int, float)) or time.time() >= (exp - margin)


# ── 认证 ─────────────────────────────────────────────────────────────────────
def refresh_tokens(auth_path: Path, auth_data: dict[str, Any]) -> str:
    """用 refresh_token 刷新 access_token，回写 auth.json"""
    tokens = auth_data.get("tokens", {})
    rt = tokens.get("refresh_token")
    if not rt:
        fail("refresh_token 缺失，请重新运行 codex login")

    client_id = decode_jwt_payload(tokens.get("access_token", "")).get(
        "client_id", OPENAI_DEFAULT_CLIENT_ID
    )
    url = os.environ.get("CODEX_REFRESH_TOKEN_URL_OVERRIDE", OPENAI_AUTH_TOKEN_URL)
    body = json.dumps(
        {"grant_type": "refresh_token", "refresh_token": rt, "client_id": client_id}
    ).encode()

    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    log(f"正在刷新 OAuth token …")
    try:
        with request.urlopen(req, timeout=30, context=ssl._create_unverified_context()) as resp:
            result = json.loads(resp.read())
    except (error.HTTPError, error.URLError) as exc:
        fail(f"刷新 token 失败: {exc}")

    new_at = result.get("access_token")
    if not new_at:
        fail("刷新 token 失败: 响应中无 access_token")

    # 回写
    tokens["access_token"] = new_at
    for k in ("refresh_token", "id_token"):
        if result.get(k):
            tokens[k] = result[k]
    auth_data["tokens"] = tokens

    import datetime
    auth_data["last_refresh"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        auth_path.write_text(json.dumps(auth_data, indent=2, ensure_ascii=False), encoding="utf-8")
        log("token 刷新成功，已更新 auth.json")
    except OSError as exc:
        log(f"警告: 无法写回 auth.json: {exc}")
    return new_at



def load_openclaw_codex_auth() -> str | None:
    """从 OpenClaw auth-profiles.json 读取 openai-codex OAuth access token。"""
    auth_path = Path(os.environ.get(
        "OPENCLAW_CODEX_AUTH_PROFILES",
        "~/.openclaw/agents/main/agent/auth-profiles.json",
    )).expanduser()
    if not auth_path.exists():
        return None
    try:
        data = json.loads(auth_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    profiles = data.get("profiles") or {}
    last_good = (data.get("lastGood") or {}).get("openai-codex")
    candidates = []
    if last_good and isinstance(profiles.get(last_good), dict):
        candidates.append(profiles[last_good])
    candidates.extend(
        p for p in profiles.values()
        if isinstance(p, dict) and p.get("provider") == "openai-codex"
    )
    for prof in candidates:
        at = prof.get("access")
        if isinstance(at, str) and at.strip():
            # OpenClaw 自己负责刷新；若这里已过期，提示用户重新授权/让 OpenClaw 刷新。
            if is_token_expired(at, margin=30):
                log("OpenClaw openai-codex access token 看起来已过期；请先触发一次 Codex 模型调用或重新授权。")
            return at.strip()
    return None

def load_auth() -> str:
    """从 ~/.codex/auth.json 加载认证凭证，返回可用的 Bearer token"""
    # 环境变量优先
    env_key = os.environ.get("OPENAI_API_KEY")
    if env_key:
        return env_key

    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    auth_path = Path(os.environ.get("CODEX_AUTH_FILE", codex_home / "auth.json")).expanduser()
    if not auth_path.exists():
        openclaw_token = load_openclaw_codex_auth()
        if openclaw_token:
            return openclaw_token
        fail(f"找不到认证文件: {auth_path}，也没有找到 OpenClaw openai-codex OAuth profile\n请先运行 codex login 或完成 OpenClaw Codex 授权")

    try:
        data = json.loads(auth_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        openclaw_token = load_openclaw_codex_auth()
        if openclaw_token:
            return openclaw_token
        fail(f"读取 auth.json 失败: {exc}")

    # API Key 模式
    api_key = data.get("OPENAI_API_KEY")
    if isinstance(api_key, str) and api_key.strip():
        return api_key.strip()

    # ChatGPT OAuth 模式
    if data.get("auth_mode") == "chatgpt":
        tokens = data.get("tokens", {})
        at = tokens.get("access_token")
        if not at:
            fail("access_token 缺失，请重新运行 codex login")
        if is_token_expired(at):
            log("access_token 已过期，自动刷新…")
            at = refresh_tokens(auth_path, data)
        return at

    openclaw_token = load_openclaw_codex_auth()
    if openclaw_token:
        return openclaw_token

    fail("auth.json 中无可用凭证，也没有找到 OpenClaw openai-codex OAuth profile；请运行 codex login 或完成 OpenClaw Codex 授权")


# ── 输出路径 ──────────────────────────────────────────────────────────────────
def resolve_output(out: str | None, name: str | None, fmt: str) -> Path:
    """确定输出文件路径"""
    ext = f".{fmt}"
    if out:
        p = Path(out).expanduser()
        return p.with_suffix(ext) if not p.suffix else p

    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    base = codex_home / "generated_images" / "manual"
    base.mkdir(parents=True, exist_ok=True)
    prefix = name or "generated"
    return base / f"{prefix}-{random_suffix()}{ext}"


# ── HTTP ──────────────────────────────────────────────────────────────────────
def post_streaming(url: str, token: str, payload: dict[str, Any], timeout: int) -> list[dict]:
    """发送 JSON 请求，解析 SSE 流式响应"""
    log(f"POST {url} (streaming)")
    body = json.dumps(payload).encode()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    req = request.Request(url, data=body, headers=headers, method="POST")
    events: list[dict] = []
    try:
        with request.urlopen(req, timeout=timeout, context=ssl._create_unverified_context()) as resp:
            log(f"status={resp.status}")
            buf = ""
            for chunk in iter(lambda: resp.read(4096), b""):
                buf += chunk.decode("utf-8", errors="replace")
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if not line or line.startswith(":"):
                        continue
                    if line == "data: [DONE]":
                        break
                    if line.startswith("data: "):
                        try:
                            events.append(json.loads(line[6:]))
                        except json.JSONDecodeError:
                            pass
    except error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        fail(f"请求失败: status={exc.code}\n{body_text}")
    except error.URLError as exc:
        fail(f"请求失败: {exc}")

    log(f"流式响应完成，共 {len(events)} 个事件")
    return events


def extract_image(events: list[dict]) -> str:
    """从 SSE 事件中提取 base64 图片数据"""
    for ev in events:
        # response.image_generation_call.done 事件
        if ev.get("type") == "response.image_generation_call.done":
            r = ev.get("result")
            if r:
                return str(r)
        # item / output_item 中的结果
        for key in ("item", "output_item"):
            item = ev.get(key, {})
            if item.get("type") == "image_generation_call" and item.get("result"):
                return str(item["result"])
        # 完成事件中的 response.output
        resp = ev.get("response", {})
        if isinstance(resp, dict):
            for o in resp.get("output") or []:
                if o.get("type") == "image_generation_call" and o.get("result"):
                    return str(o["result"])

    # 调试信息
    tail = events[-3:] if len(events) > 3 else events
    fail(f"未找到生成的图片:\n{json.dumps(tail, ensure_ascii=False, indent=2)[:2000]}")


# ── 主流程 ────────────────────────────────────────────────────────────────────
def generate(args: argparse.Namespace) -> int:
    token = load_auth()
    prompt = args.prompt.strip()
    if not prompt:
        fail("prompt 不能为空")

    size = args.size or DEFAULT_SIZE
    quality = args.quality or DEFAULT_QUALITY
    model = args.model or DEFAULT_MODEL
    fmt = args.format or DEFAULT_FORMAT
    out_path = resolve_output(args.out, args.name, fmt)

    # 如果指定了 gpt-image-* 模型，自动替换为对话模型
    if model.startswith("gpt-image"):
        model = DEFAULT_MODEL

    # 尺寸约束提示
    dim = SIZE_PATTERN.match(size)
    if dim:
        w, h = int(dim.group(1)), int(dim.group(2))
        orient = "square" if w == h else ("landscape" if w > h else "portrait")
        prompt += f"\n\nFinal output: {w}x{h} pixel {orient} canvas."

    base_url = os.environ.get("OPENAI_BASE_URL", CHATGPT_BASE_URL).rstrip("/")
    # 构建 URL
    if "backend-api/codex" in base_url:
        api_url = f"{base_url}/responses"
    elif base_url.endswith("/v1"):
        api_url = f"{base_url}/responses"
    else:
        api_url = f"{base_url}/v1/responses"

    tool: dict[str, Any] = {"type": "image_generation", "size": size, "quality": quality}
    payload = {
        "model": model,
        "instructions": "Generate the requested image using the image_generation tool.",
        "input": [{"role": "user", "content": prompt}],
        "tools": [tool],
        "store": False,
        "stream": True,
    }

    log(f"model={model} size={size} quality={quality} → {out_path}")

    if args.dry_run:
        print(json.dumps({"url": api_url, "payload": payload, "output": str(out_path)}, indent=2, ensure_ascii=False))
        return 0

    events = post_streaming(api_url, token, payload, DEFAULT_TIMEOUT)
    img_b64 = extract_image(events)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(base64.b64decode(img_b64))
    log(f"已保存: {out_path}")
    print(str(out_path))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="基于 Codex auth.json 的图片生成工具")
    p.add_argument("prompt", help="图片描述")
    p.add_argument("--model", help=f"模型名称 (默认: {DEFAULT_MODEL})")
    p.add_argument("--size", help=f"图片尺寸 (默认: {DEFAULT_SIZE})")
    p.add_argument("--quality", choices=("low", "medium", "high"), help="图片质量")
    p.add_argument("--format", choices=("png", "jpeg", "webp"), help="输出格式")
    p.add_argument("--out", help="输出文件路径")
    p.add_argument("--name", help="输出文件名前缀")
    p.add_argument("--dry-run", action="store_true", help="仅预览请求，不调用 API")
    return generate(p.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
