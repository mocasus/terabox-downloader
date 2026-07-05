# 📦 Terabox Downloader Bot

<p align="center">
  <img src="assets/logo.png" alt="Terabox Downloader" width="120">
</p>

> **Telegram Bot untuk download file dari Terabox — kirim link, terima file.**
> Dynamic QRIS payment via KlikQRIS. Satu command langsung jalan.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Node-18+-339933?style=flat&logo=node.js&logoColor=white" alt="Node">
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat&logo=telegram&logoColor=white" alt="Telegram">
  <img src="https://img.shields.io/badge/Payment-KlikQRIS-orange?style=flat" alt="KlikQRIS">
  <img src="https://img.shields.io/npm/v/terabox-downloader?color=red&label=npm" alt="npm">
  <img src="https://img.shields.io/github/license/mocasus/terabox-downloader" alt="License">
</p>

---

## 🚀 Quick Start

```bash
npm install -g terabox-downloader
tbd
```

Pertama kali jalan, CLI interactive wizard akan nanya:

```
🤖 Bot Token (dari @BotFather):   <paste>
👑 Admin Telegram ID:               <paste>
💰 Harga VIP (default: 10000):      <enter>
⏳ Durasi VIP (default: 7 hari):    <enter>
🔑 KlikQRIS API Key:                <paste>
🏪 KlikQRIS Merchant ID:            <paste>
🧪 Sandbox mode? (y/N):             <enter>
```

✅ Bot langsung jalan. Ga perlu clone — CLI handle semuanya.

<details>
<summary><b>📋 Semua perintah CLI</b></summary>

```bash
tbd              # Start bot (setup wizard di first run)
tbd setup        # Ulang konfigurasi .env
tbd update       # Git pull + update Python dependencies
tbd start        # Jalankan bot (skip wizard)

# Atau nama panjang:
terabox-downloader [setup|update|start]
```

</details>

<details>
<summary><b>🔄 Alternatif install</b></summary>

| Metode | Command |
|---|---|
| **npx** (tanpa install) | `npx terabox-downloader` |
| **pip** | `pip install terabox-downloader-bot` |
| **Docker** | `docker run -e BOT_TOKEN=xxx mocasus/terabox-downloader` |
| **Manual** | Clone repo → `pip install -r requirements.txt` → `python bot.py` |

</details>

> **Prasyarat:** Node.js 18+, Python 3.10+, Git.

---

## ✨ Fitur

| Fitur | Detail |
|---|---|
| 🔗 **Multi-mirror** | `terabox.com`, `teraboxapp.com`, `mirrobox.com`, `1024tera.com`, dll |
| 🔍 **Multi-strategy** | Savetube (primary) → Publicearn → Direct — auto-fallback |
| ⬇️ **Smart upload** | Auto-detect video/dokumen/audio, progress bar, file >50MB via direct link |
| 💳 **KlikQRIS** | Dynamic QR code — scan via GoPay/OVO/DANA/M-Banking, auto-callback webhook |
| 🎮 **Inline buttons** | Semua aksi bisa via tombol — ga perlu ketik command |
| 🛡️ **Admin panel** | Approve manual, tambah VIP, broadcast, stats |
| 🔒 **HMAC signature** | Verifikasi setiap webhook callback — anti fake payment |
| 🆓 **Trial mode** | Free download N kali sebelum wajib VIP |

---

## 📋 Perintah Bot

### User

| Command | Fungsi |
|---|---|
| `/start` | Register + menu utama (inline keyboard) |
| `/help` | Bantuan — download, bayar, VIP, FAQ |
| `/vip` | Info harga & beli VIP |
| `/bayar` | Buat QR code pembayaran |
| `/status` | Cek status akun & VIP |

### Admin

| Command | Fungsi |
|---|---|
| `/pending` | Lihat pembayaran menunggu |
| `/approve <id>` | Setujui pembayaran |
| `/reject <id> <alasan>` | Tolak pembayaran |
| `/vipadd <uid> <hari>` | Tambah VIP (`0` = lifetime) |
| `/viprem <uid>` | Cabut VIP |
| `/vips` | List semua VIP |
| `/stats` | Statistik user, VIP, revenue |
| `/broadcast <msg>` | Kirim pesan ke semua user |

---

## 💳 KlikQRIS — Cara Setup

1. **Daftar** di [klikqris.com](https://klikqris.com) → verifikasi
2. **Ambil API Key** dari dashboard → **Pengaturan → API Key**
3. **Isi .env**: `KLIKQRIS_API_KEY=...` + `KLIKQRIS_MERCHANT_ID=...`
4. **Set webhook URL** di dashboard KlikQRIS → `https://domain-kamu/webhook/klikqris`
5. **Test dengan sandbox**: `KLIKQRIS_SANDBOX=true` → [simulator](https://klikqris.com/public/sandbox/simulate) → ganti ke `false` setelah OK

```
User /bayar → Bot create QR via KlikQRIS → User scan & bayar
→ KlikQRIS kirim webhook "PAID" → Bot verifikasi HMAC → VIP aktif
```

---

## ⚙️ Environment Variables

<details>
<summary><b>🤖 Bot</b></summary>

| Variable | Wajib | Default |
|---|---|---|
| `BOT_TOKEN` | ✅ | — |
| `ADMIN_IDS` | ✅ | — |

</details>

<details>
<summary><b>👑 VIP</b></summary>

| Variable | Default |
|---|---|
| `VIP_ENABLED` | `true` |
| `VIP_PRICE` | `10000` |
| `VIP_DURATION_DAYS` | `7` |
| `VIP_TRIAL_ENABLED` | `true` |
| `VIP_TRIAL_DOWNLOADS` | `3` |

</details>

<details>
<summary><b>💳 KlikQRIS</b></summary>

| Variable | Default |
|---|---|
| `KLIKQRIS_API_KEY` | — |
| `KLIKQRIS_MERCHANT_ID` | — |
| `KLIKQRIS_SANDBOX` | `false` |
| `KLIKQRIS_BASE_URL` | `https://klikqris.com` |

</details>

<details>
<summary><b>🌐 Webhook</b></summary>

| Variable | Default |
|---|---|
| `WEBHOOK_HOST` | `http://localhost:8000` |
| `WEBHOOK_PORT` | `8000` |

</details>

<details>
<summary><b>⬇️ Download</b></summary>

| Variable | Default |
|---|---|
| `MAX_FILE_SIZE_MB` | `500` |
| `DOWNLOAD_DIR` | `./downloads` |

</details>

---

## 🏗️ Arsitektur

```
terabox-downloader/
├── bot.py                    🚀 Entry point
├── config.py                 ⚙️ Config loader
├── cli.js                    💻 npm CLI installer
│
├── database/
│   ├── models.py             🗃️ SQLite (users, payments, VIP)
│   └── migrations.py         🔄 Auto-migrate
│
├── terabox/
│   ├── resolver.py           🔍 Multi-strategy engine
│   ├── downloader.py         ⬇️ Async download + upload
│   ├── utils.py              🛠️ URL parser, formatter
│   └── strategies/
│       ├── savetube.py       🥇 Primary (no cookie)
│       ├── publicearn.py     🥈 Fallback (stub)
│       └── direct.py         🥉 Direct extraction (stub)
│
├── payments/
│   ├── klikqris.py           💳 KlikQRIS API client
│   ├── webhook_server.py     🌐 Webhook receiver
│   └── handler.py            🎯 Payment flow handlers
│
└── admin/
    ├── handlers.py           🛡️ Admin commands
    └── stats.py              📊 Statistics
```

| Layer | Teknologi |
|---|---|
| Bahasa | Python 3.10+ |
| Bot | python-telegram-bot v20 |
| DB | SQLite (WAL mode) |
| HTTP | aiohttp |
| CLI | Node.js (npm wrapper) |
| Payment | KlikQRIS API |

---

## 📄 License

MIT — [mocasus](https://github.com/mocasus)

---

**[⬆ Back to top](#-terabox-downloader-bot)**
