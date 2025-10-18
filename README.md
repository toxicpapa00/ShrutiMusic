# ðŸŽµ Shruti Music Bot

> A clean, fast and stable Telegram music bot built for playing highâ€‘quality audio in group voice chats. This README is styled for clarity and quick setup â€” copy it into your repository as `README.md`.

---

## ðŸ“Œ Table of contents

- [About](#about)
- [Highlights](#highlights)
- [Badges](#badges)
- [Quick Links](#quick-links)
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Deployment (Recommended)](#deployment-recommended)
  - [VPS (systemd / screen)](#vps-systemd--screen)
  - [Heroku](#heroku)
  - [Render (Free)](#render-free)
- [Commands](#commands)
- [Troubleshooting & Tips](#troubleshooting--tips)
- [Contributing & Credits](#contributing--credits)
- [License](#license)

---

## âœ… About

**Shruti Music Bot** is a Telegram music bot designed to stream audio into group voice chats using a fast API backend. It prioritizes reliability, low latency, and ease-of-deployment for both beginners and advanced users.

This repository uses a modern API-based approach (no cookie scraping) to deliver consistent, low-latency results.

---

## âœ¨ Highlights

- API-first architecture â€” no cookie handling required
- 1â€“3 second search/stream response times (dependent on API and hosting)
- Supports YouTube, Spotify, SoundCloud and local files
- Playlist management, admin controls and multi-language support
- Production-ready deployment instructions for VPS, Heroku and Render

---

## ðŸ“› Badges

```
[![Support Channel](https://img.shields.io/badge/Support%20Channel-FF0000?style=for-the-badge&logo=telegram&logoColor=white&labelColor=000000)]()
[![Support Group](https://img.shields.io/badge/Support%20Group-00FF00?style=for-the-badge&logo=telegram&logoColor=black&labelColor=FF0000)]()
[![Owner](https://img.shields.io/badge/Owner-FFFF00?style=for-the-badge&logo=telegram&logoColor=black&labelColor=8A2BE2)]()
```

Replace the `()` links above with your actual URLs. Badges are optional but help with visual polish.

---

## ðŸ”— Quick links

- Support Channel: `https://t.me/ShrutiBots`
- Support Group: `https://t.me/ShrutiBotSupport`
- Owner: `https://t.me/WTF_WhyMeeh`
- API Panel (required): `https://panel.thequickearn.xyz/signup?ref=NGBM6HYNQKU`
- GitHub (forks/stars): `https://github.com/NoxxOP/ShrutiMusic`

---

## ðŸ§© Requirements

- Python 3.10+ (recommended)
- FFmpeg (system package)
- MongoDB (Atlas or local)
- A Telegram Bot Token (from @BotFather)
- API_ID and API_HASH (from https://my.telegram.org)
- `API_KEY` from the QuickEarn panel (mandatory)

---

## âš™ï¸ Configuration

Create a `.env` file (or edit `.env.example`) and set the following environment variables:

```env
API_ID=123456
API_HASH=abcdef1234567890abcdef
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
MONGO_DB_URI=mongodb+srv://user:pass@cluster0.mongodb.net/dbname
OWNER_ID=123456789
OWNER_USERNAME=yourusername
BOT_USERNAME=shrutibot
STRING_SESSION=your_string_session
GIT_TOKEN= (if using private repo auto-update)
LOG_GROUP_ID=-1001234567890
SUPPORT_GROUP=https://t.me/ShrutiBotSupport
SUPPORT_CHANNEL=https://t.me/ShrutiBots
API_KEY=your_quickearn_api_key  # REQUIRED
START_IMG_URL=https://example.com/image.jpg
```

> **Note:** `COOKIE_URL` and cookie-based methods are deprecated for this repo. Prefer `API_KEY`.

---

## ðŸš€ Deployment (recommended)

### VPS (systemd or screen)

1. Update & install dependencies:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip ffmpeg git screen curl
```

2. Clone & prepare:

```bash
git clone https://github.com/NoxxOP/ShrutiMusic.git
cd ShrutiMusic
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env  # edit .env accordingly
```

3. Run inside `screen` for 24Ã—7 uptime:

```bash
screen -S shruti
python3 -m ShrutiMusic
# Detach: Ctrl+A, D
# Reattach: screen -r shruti
```

*Optional:* Create a `systemd` service for auto-start on reboot (recommended for production).

---

### Heroku

1. Click **Deploy** button (if present) or push branch to Heroku Git
2. Set required config vars in the app dashboard (same keys as `.env`)
3. Scale worker to 1 in the `Resources` tab

**Pro Tip:** Keep worker dyno sleeping disabled for consistent uptime.

---

### Render (Free)

1. Create a new web service -> Connect GitHub repo
2. Provide build & start commands, and config vars
3. Deploy

---

## ðŸ”¥ Essential commands

Use these commands in group chats where the bot is present and has proper permissions:

| Command | Description |
|---|---|
| `/play` | Play music from YouTube or search by name |
| `/play [song name/URL]` | Play specific song |
| `/pause` | Pause the current stream |
| `/resume` | Resume playback |
| `/skip` | Skip current track |
| `/stop` | Stop playback and clear queue |
| `/playlist` | Show the current queue |
| `/song [song name]` | Download a track as audio |
| `/settings` | Open bot settings (admins) |

---

## ðŸ›  Troubleshooting & Tips

- **Bot not responding:** Ensure `python3 -m ShrutiMusic` process is running and bot token correct.
- **No sound in VC:** Verify FFmpeg is installed and accessible in PATH.
- **Cannot join voice chat:** Make the bot an admin with voice permissions in the group.
- **API / Invalid API_KEY:** Double-check the `API_KEY` from the QuickEarn panel.
- **Session generation:** Use `@Sessionbbbot` to create `STRING_SESSION` safely.

---

## ðŸ¤ Contributing & credits

- **Main Developer:** [NoxxOP](https://github.com/NoxxOP)
- If you contributed, add your name to the `CONTRIBUTORS` section in the repo.

Contributions are welcome â€” open pull requests for bug fixes, docs, or new features.

---

## ðŸ“„ License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

## ðŸ§¾ Last notes

- Keep your `API_KEY` secret. Do not commit `.env` to Git.
- If you want a translated Hindi or bilingual README, tell me and I will provide a polished Hindi version.

---

*Enjoy streaming â€” Shruti Music Bot* ðŸŽ§
