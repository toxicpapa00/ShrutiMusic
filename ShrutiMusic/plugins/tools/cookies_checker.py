

import os
import time
import tempfile
import asyncio
from datetime import datetime, timezone
from http import cookiejar
from typing import Tuple, Dict, Optional

import requests
from pyrogram import filters
from pyrogram.types import Message

from ShrutiMusic import app

YOUTUBE_SUBS_URL = "https://www.youtube.com/feed/subscriptions"
YOUTUBE_WATCH_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

def parse_raw_cookie_string(s: str) -> Dict[str, str]:
    cookies = {}
    for part in s.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies

def load_cookies_from_netscape(path: str) -> requests.cookies.RequestsCookieJar:
    mj = cookiejar.MozillaCookieJar()
    # ignore missing expiry / discard
    mj.load(path, ignore_discard=True, ignore_expires=True)
    jar = requests.cookies.RequestsCookieJar()
    for c in mj:
        jar.set(c.name, c.value, domain=c.domain, path=c.path, expires=c.expires)
    return jar

def extract_cookie_metadata_from_jar(jar: requests.cookies.RequestsCookieJar) -> Dict[str, Optional[int]]:
    meta = {}
    # requests cookiejar stores objects with attributes on underlying cookie
    for c in jar:
        # c is a Cookie object-like from requests
        try:
            meta[c.name] = getattr(c, "expires", None)
        except Exception:
            meta[c.name] = None
    return meta

def format_expiry(ts: Optional[int]) -> str:
    if not ts:
        return "no-expiry/unknown"
    try:
        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return str(ts)

def analyze_responses(subs_resp: requests.Response, watch_resp: requests.Response, jar: requests.cookies.RequestsCookieJar) -> str:
    diagnostics = []
    # subscriptions check
    subs_final = subs_resp.url
    diagnostics.append(f"Subscriptions final URL: {subs_final} (HTTP {subs_resp.status_code})")
    if "signin" in subs_final or "accounts.google.com" in subs_final or "service=login" in subs_final:
        subs_status = "NOT LOGGED IN / SIGNIN REDIRECT"
    else:
        subs_status = "APPEARS LOGGED IN"
    diagnostics.append(f"Subscriptions check: {subs_status}")

    # watch page check
    watch_final = watch_resp.url
    diagnostics.append(f"Watch final URL: {watch_final} (HTTP {watch_resp.status_code})")

    body = watch_resp.text.lower()
    # heuristics
    ok_tokens = ["ytinitialplayerresponse", '"playabilitystatus"', '"playabilityStatus"'.lower()]
    blocked_tokens = ["sign in", "accounts.google.com", "service=login"]
    playability_ok = any(tok in body for tok in ok_tokens)
    sign_in_found = any(tok in watch_final.lower() or tok in body for tok in blocked_tokens)

    if sign_in_found:
        watch_status = "WATCH PAGE REDIRECTS / SIGNIN"
    elif playability_ok:
        watch_status = "WATCH PAGE OK — player data present"
    else:
        watch_status = "WATCH PAGE UNCERTAIN"

    diagnostics.append(f"Watch check: {watch_status}")

    # cookie-based heuristics for "will download"
    cookie_names = [c.name for c in jar]
    auth_like = [n for n in cookie_names if n.lower() in ("sid","hsid","sapisid","ssid","apisid","sidc","authuser")]
    diagnostics.append(f"Auth-like cookies present: {', '.join(auth_like) if auth_like else 'none'}")

    # final decision on download possibility
    if subs_status.startswith("APPEARS LOGGED IN") and "OK" in watch_status:
        download_guess = "LIKELY — downloads (yt-dlp) should work"
    elif subs_status.startswith("APPEARS LOGGED IN") and "UNCERTAIN" in watch_status:
        download_guess = "POSSIBLE but uncertain — try yt-dlp with this cookie file"
    else:
        download_guess = "UNLIKELY — cookies appear signed-out / redirected"

    diagnostics.append(f"Download guess: {download_guess}")

    return "\n".join(diagnostics)

def check_cookies_with_requests(jar: requests.cookies.RequestsCookieJar, timeout: int = 20) -> Tuple[bool, Dict[str, Optional[int]], str]:
    """
    Returns (success_flag, cookie_meta, diagnostics_text)
    success_flag: True if cookies look valid (heuristic)
    cookie_meta: {name: expires_timestamp_or_None}
    diagnostics_text: multiline string with details
    """
    s = requests.Session()
    s.cookies = jar
    s.headers.update({"User-Agent": USER_AGENT})

    try:
        subs_resp = s.get(YOUTUBE_SUBS_URL, timeout=timeout, allow_redirects=True)
    except requests.RequestException as e:
        return False, extract_cookie_metadata_from_jar(jar), f"Network error checking subscriptions: {e}"

    try:
        watch_resp = s.get(YOUTUBE_WATCH_URL, timeout=timeout, allow_redirects=True)
    except requests.RequestException as e:
        return False, extract_cookie_metadata_from_jar(jar), f"Network error checking watch page: {e}"

    diagnostics = analyze_responses(subs_resp, watch_resp, jar)

    # decide success boolean
    subs_final = subs_resp.url.lower()
    if "signin" in subs_final or "accounts.google.com" in subs_final:
        success = False
    else:
        # if watch page contains player data, treat as success
        watch_body = watch_resp.text.lower()
        if ("ytinitialplayerresponse" in watch_body) or ('"playabilitystatus"' in watch_body):
            success = True
        else:
            # fallback on presence of common auth cookies
            cookie_meta = extract_cookie_metadata_from_jar(jar)
            auth_cookies = [n for n in cookie_meta.keys() if n.lower() in ("sid","hsid","sapisid","ssid","apisauth","apnea")]
            success = bool(auth_cookies)

    return success, extract_cookie_metadata_from_jar(jar), diagnostics

async def do_check(file_path: Optional[str], raw_text: Optional[str]) -> Tuple[bool, Dict[str, Optional[int]], str]:
    """
    Either file_path (path to saved cookie file) OR raw_text (cookie header text) is provided.
    This runs in a thread to avoid blocking the event loop.
    """
    def blocking_work():
        # build requests cookie jar
        jar = requests.cookies.RequestsCookieJar()
        if file_path:
            # try netscape format first; fallback to raw string parse
            try:
                jar = load_cookies_from_netscape(file_path)
            except Exception:
                # attempt to parse raw text inside file as cookie header
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                        content = fh.read()
                    parsed = parse_raw_cookie_string(content)
                    jar.update(parsed)
                except Exception as e:
                    raise RuntimeError(f"Failed to load cookie file: {e}")
        else:
            parsed = parse_raw_cookie_string(raw_text or "")
            jar.update(parsed)

        success, meta, diagnostics = check_cookies_with_requests(jar)
        return success, meta, diagnostics

    return await asyncio.to_thread(blocking_work)

# Handler: user replies to a message (with document or text) and sends /check
@app.on_message(filters.command("check") & filters.reply)
async def check_cookies_plugin(client, message: Message):
    reply = message.reply_to_message
    if not reply:
        await message.reply_text("❗️ Use /check as a *reply* to the message that contains the cookie file or raw cookie text.")
        return

    status_msg = await message.reply_text("🔎 Checking cookies... please wait (this may take a few seconds)")

    file_path = None
    raw_text = None
    try:
        # If replied message has a document (file), download it
        if reply.document:
            # limit size to something reasonable (e.g., 2MB)
            if reply.document.file_size and reply.document.file_size > 5 * 1024 * 1024:
                await status_msg.edit_text("❗️ Cookie file too large (>5MB). Please provide a small cookies.txt or raw cookie file.")
                return
            tmpdir = tempfile.gettempdir()
            local_name = os.path.join(tmpdir, f"shruti_cookies_{int(time.time())}.txt")
            await client.download_media(reply.document, file_name=local_name)
            file_path = local_name
        else:
            # maybe the user put raw cookie text in the replied message
            raw_text = reply.text or reply.caption or ""
            if not raw_text.strip():
                await status_msg.edit_text("❗️ Replied message has no file and no cookie text. Please attach cookies file or paste cookie header.")
                return

        # run check
        success, meta, diagnostics = await do_check(file_path=file_path, raw_text=raw_text)

        # Build response
        cookie_lines = []
        if meta:
            for name, expires in meta.items():
                cookie_lines.append(f"- `{name}` — {format_expiry(expires)}")
        else:
            cookie_lines.append("No cookies parsed.")

        result_text = (
            "✅ *Cookie Check Result*\n\n"
            f"*Validity:* {'VALID / LOGGED IN' if success else 'EXPIRED / NOT LOGGED IN'}\n\n"
            f"*Cookies found:*\n" + ("\n".join(cookie_lines)) + "\n\n"
            f"*Download likelihood:* "
            + ("LIKELY — yt-dlp should work." if success else "UNLIKELY — probably will not work.") + "\n\n"
            f"*Diagnostics:*\n```\n{diagnostics[:1500]}\n```\n\n"
            "_Note: This is heuristic. YouTube uses JS and complex auth; for foolproof checks use a headless browser or try yt-dlp directly with the cookie file._"
        )

        await status_msg.edit_text(result_text, disable_web_page_preview=True)
    except Exception as e:
        await status_msg.edit_text(f"❌ Error while checking cookies: {e}")
    finally:
        # cleanup temp file if created
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
