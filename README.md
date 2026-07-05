# Terabox Downloader Bot

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Telegram bot untuk auto-download file dari **Terabox** dan mirror-nya. Cukup kirim link, bot akan resolve + download + kirim file ke kamu.

## ✨ Features

-   🔗 Support semua domain Terabox & mirror (terabox.com, teraboxapp.com, mirrobox.com, nephobox.com, dll)
-   🔍 Multi-strategy resolver dengan auto-fallback
-   💎 Sistem VIP dengan pembayaran QRIS (toggle ON/OFF)
-   🎁 Free trial download (configurable)
-   📊 Admin panel lengkap (stats, pending payments, broadcast)
-   📦 Auto-detect file type & upload format
-   🔗 Direct link untuk file di atas 50 MB
-   🐳 Docker-ready

## 🚀 Quick Start

### 1. Clone

```bash
git clone https://github.com/mocasus/terabox-downloader.git
cd terabox-downloader
```

### 2. Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env dengan BOT_TOKEN dan ADMIN_IDS
```

### 3. Run

```bash
python bot.py
```

### Docker

```bash
docker compose up -d
```

## ⚙️ Configuration

| Variable | Default | Description |
|---|---|---|
| `BOT_TOKEN` | *required* | Telegram bot token dari [@BotFather](https://t.me/BotFather) |
| `ADMIN_IDS` | *required* | ID admin, comma-separated |
| `VIP_ENABLED` | false | Aktifkan sistem VIP |
| `VIP_PRICE` | 15000 | Harga VIP (Rupiah) |
| `VIP_DURATION_DAYS` | 30 | Masa aktif VIP (0 = lifetime) |
| `VIP_TRIAL_ENABLED` | false | Aktifkan free trial |
| `VIP_TRIAL_DOWNLOADS` | 3 | Jumlah download gratis |
| `MAX_FILE_SIZE_MB` | 50 | Batas upload ke Telegram |

## 📋 Commands

### User

| Command | Description |
|---|---|
| `/start` | Mulai bot |
| `/help` | Bantuan |
| `/vip` | Info langganan VIP |
| `/status` | Cek status akun |
| `/bayar` | Beli VIP |

### Admin

| Command | Description |
|---|---|
| `/pending` | List pembayaran pending |
| `/approve <id>` | Setujui pembayaran |
| `/reject <id>` | Tolak pembayaran |
| `/vipadd <uid> <hari>` | Manual add VIP |
| `/viprem <uid>` | Cabut VIP |
| `/vips` | List user VIP |
| `/stats` | Statistik bot |
| `/config` | Lihat konfigurasi |
| `/broadcast <msg>` | Broadcast ke semua user |

## 🏗️ Architecture

```
User → Telegram Bot → Terabox Resolver (multi-strategy)
                          ↓
              ┌─ savetube API (primary)
              ├─ public proxy (fallback)
              └─ ndus cookie (last resort)
                          ↓
                    Download Engine
                    ┌──────┴──────┐
               ≤50MB           >50MB
               Upload TG       Direct Link
```

## 🧩 Supported Domains

terabox.com, terabox.app, teraboxlink.com, 1024terabox.com, mirrobox.com, nephobox.com, freeterabox.com, 4funbox.com, momerybox.com, tibibox.com, teraboxapp.com, 1024tera.com, terasharefile.com, terafileshare.com, terasharelink.com, teraboxshare.com

## 📄 License

MIT — [mocasus](https://github.com/mocasus)

---

**By mmoaa**
