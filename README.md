<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/Terabox-Downloader-6366f1?style=for-the-badge&logo=telegram&logoColor=white&labelColor=1e1b4b">
    <img src="https://img.shields.io/badge/Terabox-Downloader-6366f1?style=for-the-badge&logo=telegram&logoColor=white&labelColor=eef2ff" alt="Terabox Downloader">
  </picture>
</p>

<p align="center">
  <b>Telegram Bot untuk mendownload file dari Terabox</b><br>
  <sub>Kirim link → Auto resolve → File diterima di chat. Cepat, otomatis, tanpa ribet.</sub>
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-success?style=flat-square" alt="License"></a>
  <a href="https://t.me/your_bot"><img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram&logoColor=white" alt="Bot"></a>
  <a href="#docker"><img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"></a>
  <a href="#pembayaran"><img src="https://img.shields.io/badge/Payment-KlikQRIS-FF6B00?style=flat-square" alt="KlikQRIS"></a>
  <img src="https://img.shields.io/badge/DB-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Async-aiohttp-2C5BB4?style=flat-square&logo=aiohttp&logoColor=white" alt="Async">
</p>

---

<p align="center">
  <table>
    <tr>
      <td align="center"><b>🔗 Kirim Link</b><br>Terabox / Mirrobox<br>+ mirror lainnya</td>
      <td align="center"><b>🔍 Auto Resolve</b><br>Multi-strategy<br>auto-fallback</td>
      <td align="center"><b>⬇️ Download</b><br>Progress real-time<br>async stream</td>
      <td align="center"><b>📤 Terima File</b><br>Langsung di chat<br>Telegram kamu</td>
    </tr>
  </table>
</p>

---

## 📑 Daftar Isi

- [✨ Fitur](#-fitur)
- [🎮 Demo](#-demo)
- [🚀 Quick Start](#-quick-start)
- [📋 Perintah Bot](#-perintah-bot)
- [💳 Pembayaran KlikQRIS](#-pembayaran-klikqris)
- [🏗️ Arsitektur](#️-arsitektur)
- [🐳 Deployment](#-deployment)
- [🧩 Extending](#-extending)
- [🔒 Keamanan](#-keamanan)
- [❓ FAQ](#-faq)
- [📝 Changelog](#-changelog)
- [🤝 Kontribusi](#-kontribusi)
- [📄 Lisensi](#-lisensi)

---

## ✨ Fitur

### 🔗 Download Terabox

<table>
<tr>
<td>

✅ **Semua mirror didukung**
- `terabox.com`
- `teraboxapp.com`
- `mirrobox.com`
- `1024tera.com`
- `teraboxshare.com`
- Dan mirror lainnya

</td>
<td>

✅ **Multi-Strategy Resolver**
- Savetube API (primary)
- Publicearn (fallback)
- Direct extraction (last resort)
- Auto-retry dengan strategi berbeda

</td>
</tr>
<tr>
<td>

✅ **Smart Upload**
- Auto-detect: video / dokumen / arsip / audio
- Progress bar real-time
- File >50MB → direct link
- Concurrent download queue

</td>
<td>

✅ **User-Friendly**
- Inline keyboard navigasi
- Satu klik untuk semua aksi
- Notifikasi real-time
- Error handling informatif

</td>
</tr>
</table>

### 💳 Sistem VIP

<table>
<tr>
<td width="50%">

**Mode Trial**
- Free download (1-5x)
- Auto-count per hari
- Notifikasi sisa trial
- Bisa di-enable/disable

</td>
<td width="50%">

**Mode VIP**
- Harga terjangkau
- Durasi fleksibel (hari / lifetime)
- Auto-expiry check
- Status bisa dicek kapan saja

</td>
</tr>
</table>

### 💰 Pembayaran Otomatis

<table>
<tr>
<td width="50%">

**KlikQRIS Integration**
- Dynamic QR code
- Scan pakai: GoPay, OVO, DANA, M-Banking
- Webhook auto-callback
- VIP langsung aktif setelah bayar

</td>
<td width="50%">

**Keamanan Transaksi**
- HMAC signature verification
- Idempotency (no double payment)
- Sandbox mode untuk testing
- Logging semua transaksi

</td>
</tr>
</table>

### 🛡️ Admin Panel

| Perintah | Fungsi |
|---|---|
| `/pending` | Lihat semua pembayaran menunggu |
| `/approve <id>` | Approve pembayaran manual |
| `/reject <id> <alasan>` | Tolak pembayaran dengan alasan |
| `/vipadd <uid> <hari>` | Tambah VIP ke user |
| `/viprem <uid>` | Hapus VIP user |
| `/vips` | List semua VIP |
| `/stats` | Statistik: user, VIP, download |
| `/broadcast <msg>` | Broadcast ke semua user |

---

## 🎮 Demo

### User Flow — Download File

```text
👤 User: Kirim link terabox
         ║
         ╠══ https://terabox.com/s/1abc2def...
         ║
🤖 Bot:  🔍 Memproses link...
         📁 video_tutorial.mp4
         📦 245.7 MB
         🔗 Strategi: savetube
         ⬇️ Mendownload... 67%
         📤 Mengupload ke Telegram...
         ✅ File terkirim!

         [ 🔄 Download Lagi ]  [ ⭐ Beli VIP ]  [ 📊 Status ]
```

### User Flow — Beli VIP

```text
👤 User: /vip
         ║
🤖 Bot:  ⭐ VIP Terabox Downloader
         💰 Harga: Rp 15,000
         ⏳ Durasi: 30 hari
         📥 Benefit: Unlimited download

         [ 💳 Bayar via QRIS ]  [ ℹ️ Cek Status ]
         ║
         ╠══ User klik "Bayar via QRIS"
         ║
🤖 Bot:  💳 QRIS Pembayaran VIP
         [QR Code Image]
         🆔 INV-20260705-ABC123
         💰 Rp 15,000
         📱 Scan pakai GoPay/OVO/DANA/M-Banking
         ✅ VIP otomatis aktif setelah bayar!

         [ 🔄 Cek Status ]

         ║ ... user bayar ...
         ║
🤖 Bot:  ✅ Pembayaran Berhasil!
         🎉 VIP kamu sudah aktif selama 30 hari.
         Kirim link Terabox sekarang!
```

### Admin Flow — Manual Override

```text
👤 Admin: /pending
         ║
🤖 Bot:  📋 Pembayaran Pending (2)
         ┌──────────────────────────────────┐
         │ #1  User: @john (123456789)      │
         │     Rp 15,000 — klikqris          │
         │     🕐 05 Jul 2026 19:30          │
         │     [ ✅ Approve ] [ ❌ Reject ]  │
         ├──────────────────────────────────┤
         │ #2  User: @jane (987654321)      │
         │     Rp 15,000 — klikqris          │
         │     🕐 05 Jul 2026 20:15          │
         │     [ ✅ Approve ] [ ❌ Reject ]  │
         └──────────────────────────────────┘
```

---

## 🚀 Quick Start

### Cara Paling Cepat — 2 Command

```bash
npm install -g terabox-downloader
tbd
```

**Itu aja.** Pertama kali jalan, CLI akan nanya 6 pertanyaan:

```
🤖 Bot Token (dari @BotFather):  <paste>
👑 Admin Telegram ID:              <paste>
💰 Harga VIP (default: 10000):     <enter>
⏳ Durasi VIP hari (default: 7):   <enter>
🔑 KlikQRIS API Key:               <paste>
🏪 KlikQRIS Merchant ID:           <paste>
🧪 Sandbox mode? (y/N):
```

Abis itu bot langsung jalan. Ga perlu clone, ga perlu venv, ga perlu pip install.

### Alternatif: Tanpa Install

```bash
npx terabox-downloader
```

Sama aja — cuma ga permanent di PATH.

### Cara Lain

| Metode | Command |
|---|---|
| **npm** (recommended) | `npx terabox-downloader` |
| **pip** | `pip install terabox-downloader-bot && terabox-downloader` |
| **Docker** | `docker run -e BOT_TOKEN=xxx mocasus/terabox-downloader` |
| **Manual** | Clone repo → `pip install -r requirements.txt` → `python bot.py` |

### Perintah CLI

```bash
tbd                  # Start bot (alias pendek)
tbd setup            # Ulang setup .env
tbd update           # Git pull + update deps
tbd start            # Start ulang (skip setup)

# atau nama panjangnya:
terabox-downloader [setup|update|start]
```

> **Prasyarat:** Node.js 18+, Python 3.10+, Git. Udah. Ga perlu install apa-apa lagi — CLI yang handle sisanya.

---

## ⚙️ Konfigurasi

### Semua Environment Variables

<details open>
<summary><b>🤖 Bot Settings</b></summary>

| Variable | Default | Wajib | Deskripsi |
|---|---|---|---|
| `BOT_TOKEN` | — | ✅ | Token bot Telegram dari @BotFather |
| `ADMIN_IDS` | — | ✅ | ID Telegram admin, pisahkan dengan koma untuk multi admin |
</details>

<details open>
<summary><b>👑 VIP Settings</b></summary>

| Variable | Default | Deskripsi |
|---|---|---|
| `VIP_ENABLED` | `false` | Aktifkan sistem VIP (`true`/`false`) |
| `VIP_PRICE` | `15000` | Harga VIP dalam Rupiah |
| `VIP_DURATION_DAYS` | `30` | Durasi VIP dalam hari. `0` = Lifetime |
| `VIP_TRIAL_ENABLED` | `false` | Aktifkan free trial download |
| `VIP_TRIAL_DOWNLOADS` | `3` | Jumlah download gratis untuk trial |
</details>

<details open>
<summary><b>💳 KlikQRIS Settings</b></summary>

| Variable | Default | Deskripsi |
|---|---|---|
| `KLIKQRIS_API_KEY` | — | API key dari dashboard KlikQRIS |
| `KLIKQRIS_MERCHANT_ID` | — | Merchant ID KlikQRIS |
| `KLIKQRIS_SANDBOX` | `false` | Mode sandbox untuk testing |
| `KLIKQRIS_BASE_URL` | `https://klikqris.com` | Base URL API KlikQRIS |
</details>

<details open>
<summary><b>🌐 Webhook Settings</b></summary>

| Variable | Default | Deskripsi |
|---|---|---|
| `WEBHOOK_HOST` | — | Domain publik (contoh: `https://bot.kamu.com`) |
| `WEBHOOK_PORT` | `8000` | Port untuk webhook server |
</details>

<details open>
<summary><b>⬇️ Download Settings</b></summary>

| Variable | Default | Deskripsi |
|---|---|---|
| `MAX_FILE_SIZE_MB` | `50` | Batas maksimum file yang dikirim ke Telegram |
| `CONCURRENT_DOWNLOADS` | `3` | Maksimum download bersamaan |
| `DOWNLOAD_DIR` | `/tmp/terabox` | Direktori penyimpanan sementara |
</details>

---

## 📋 Perintah Bot

### 👤 User Commands

| Perintah | Keyboard | Fungsi |
|---|---|---|
| `/start` | [💰 Beli VIP] [⬇️ Download] [ℹ️ Bantuan] [👤 Status] | Registrasi + menu utama |
| `/help` | [💳 Cara Bayar] [⭐ VIP Info] [📊 Status] [🆘 FAQ] | Bantuan lengkap |
| `/vip` | [💳 Bayar via QRIS] [ℹ️ Cek Status] | Info langganan VIP |
| `/bayar` | [💳 Bayar via QRIS] | Mulai pembayaran QRIS |
| `/status` | [💳 Beli VIP] / [📊 Info VIP] | Cek status akun & VIP |

### 🛡️ Admin Commands

| Perintah | Fungsi |
|---|---|
| `/pending` | Lihat semua pembayaran menunggu verifikasi |
| `/approve <id>` | Setujui pembayaran manual |
| `/reject <id> <alasan>` | Tolak pembayaran dengan alasan |
| `/vipadd <user_id> <hari>` | Tambah VIP ke user (`0` = lifetime) |
| `/viprem <user_id>` | Cabut VIP user |
| `/vips` | List semua user VIP aktif |
| `/stats` | Statistik lengkap (user, VIP, download, revenue) |
| `/config` | Lihat konfigurasi bot saat ini |
| `/broadcast <pesan>` | Kirim pesan ke semua user |

### 🎯 Inline Callbacks (Tombol)

Setiap aksi di bot juga bisa dilakukan lewat tombol inline:

| Tombol | Muncul di | Aksi |
|---|---|---|
| `💰 Beli VIP` | /start, /status | Langsung ke /bayar |
| `⬇️ Download` | /start | Info cara download |
| `ℹ️ Bantuan` | /start, /help | Menu bantuan |
| `👤 Status` | /start | Cek status akun |
| `💳 Bayar via QRIS` | /vip, /bayar | Buat QR code pembayaran |
| `🔄 Cek Status` | Setelah bayar | Cek status pembayaran |
| `✅ Approve` | /pending (admin) | Setujui pembayaran |
| `❌ Reject` | /pending (admin) | Tolak pembayaran |
| `🔄 Download Lagi` | Setelah download | Download file lain |
| `💳 Beli VIP Sekarang` | Trial habis | Langsung ke /bayar |
| `🆘 Bantuan` | Error | Bantuan troubleshooting |

---

## 💳 Pembayaran KlikQRIS

### Flow Pembayaran Lengkap

```
┌─────────┐     ┌─────────┐     ┌──────────┐     ┌──────────┐
│  User   │     │   Bot   │     │ KlikQRIS │     │  Phone   │
└────┬────┘     └────┬────┘     └────┬─────┘     └────┬─────┘
     │               │               │                 │
     │  /bayar       │               │                 │
     │──────────────▶│               │                 │
     │               │               │                 │
     │               │  POST /api/   │                 │
     │               │  qris/create  │                 │
     │               │──────────────▶│                 │
     │               │               │                 │
     │               │  ◀─ QR Image  │                 │
     │               │     + Order   │                 │
     │               │               │                 │
     │  ◀─ QR Code   │               │                 │
     │     Payment    │               │                 │
     │               │               │                 │
     │                                         Scan QR │
     │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ▶│
     │                                         Bayar ✅│
     │               │               │                 │
     │               │  ◀─ Webhook   │                 │
     │               │     "PAID"    │                 │
     │               │               │                 │
     │               │  Verify HMAC  │                 │
     │               │  signature    │                 │
     │               │               │                 │
     │               │  DB: approve  │                 │
     │               │  + set VIP    │                 │
     │               │               │                 │
     │  ◀─ ✅ VIP    │               │                 │
     │     Aktif!    │               │                 │
     │               │               │                 │
```

### Cara Setup KlikQRIS

<details>
<summary><b>Langkah 1: Daftar Akun</b></summary>

1. Kunjungi [klikqris.com](https://klikqris.com)
2. Klik **Daftar** dan isi data merchant
3. Verifikasi email & nomor telepon
4. Login ke dashboard
</details>

<details>
<summary><b>Langkah 2: Ambil API Key</b></summary>

1. Di dashboard, buka menu **Pengaturan** → **API Key**
2. Copy **API Key** dan **Merchant ID**
3. Masukkan ke `.env`:
   ```env
   KLIKQRIS_API_KEY=sk_live_xxxxxxxx
   KLIKQRIS_MERCHANT_ID=MCH-12345
   ```
</details>

<details>
<summary><b>Langkah 3: Set Webhook URL</b></summary>

1. Pastikan bot berjalan di server dengan domain publik
2. Di dashboard KlikQRIS → **Webhook**
3. Set URL ke: `https://domain-kamu.com/webhook/klikqris`
4. Klik **Test Webhook** untuk memastikan koneksi
</details>

<details>
<summary><b>Langkah 4: Testing (Sandbox)</b></summary>

1. Set `KLIKQRIS_SANDBOX=true` di `.env`
2. Restart bot
3. Gunakan [Simulator Sandbox](https://klikqris.com/public/sandbox/simulate) KlikQRIS
4. Simulasikan pembayaran sukses untuk tes webhook
5. Setelah berhasil, set `KLIKQRIS_SANDBOX=false` untuk production
</details>

### Signature Verification

Bot memverifikasi setiap webhook callback dengan HMAC signature untuk mencegah:

- ❌ Fake payment notifications
- ❌ Replay attacks (pakai signature yang sama)
- ❌ Tampered transaction data

---

## 🏗️ Arsitektur

### Struktur Direktori

```
terabox-downloader/
│
├── bot.py                         🚀 Entry point: bot polling + webhook
├── config.py                      ⚙️ Konfigurasi dari .env
│
├── database/
│   ├── __init__.py                📦 Database package
│   ├── models.py                  🗃️ SQLite: users, payments, VIP
│   └── migrations.py              🔄 Auto-migrate schema
│
├── terabox/
│   ├── __init__.py                📦 Terabox package
│   ├── resolver.py                🔍 Multi-strategy engine
│   ├── downloader.py              ⬇️ Download + upload handler
│   ├── utils.py                   🛠️ URL parser, formatter, icons
│   └── strategies/
│       ├── __init__.py
│       ├── savetube.py            🥇 Primary: savetube API (no cookie)
│       ├── publicearn.py          🥈 Fallback: publicearn (stub)
│       └── direct.py              🥉 Last resort: direct extraction (stub)
│
├── payments/
│   ├── __init__.py                📦 Payment package
│   ├── klikqris.py                💳 KlikQRIS API client
│   ├── webhook_server.py          🌐 aiohttp webhook receiver
│   └── handler.py                 🎯 Payment flow + Telegram handlers
│
├── admin/
│   ├── __init__.py                📦 Admin package
│   ├── handlers.py                🛡️ Admin command handlers
│   └── stats.py                   📊 Statistics formatter
│
├── assets/
│   └── .gitkeep                   🖼️ Asset placeholder (logo, QRIS, dll)
│
├── Dockerfile                     🐳 Docker image
├── docker-compose.yml             🐳 Docker Compose
├── requirements.txt               📦 Python dependencies
├── .env.example                   📋 Template konfigurasi
├── .gitignore                     🙈 Git ignore rules
├── LICENSE                        📄 MIT License
└── README.md                      📖 You are here
```

### Tech Stack

| Layer | Teknologi | Alasan |
|---|---|---|
| **Bahasa** | Python 3.11+ | Async native, mature ecosystem |
| **Bot** | python-telegram-bot v20 | Best-in-class async Telegram framework |
| **Database** | SQLite (WAL mode) | Zero config, fast, thread-safe |
| **HTTP Client** | aiohttp | Non-blocking HTTP untuk API + download |
| **Web Server** | aiohttp | Webhook receiver tanpa dependency tambahan |
| **Payment** | KlikQRIS REST API | QRIS dinamis + webhook callback |
| **Deployment** | Docker / systemd | Production-ready, auto-restart |
| **File I/O** | aiofiles | Async file operations |

### Data Flow

```
User Message
    │
    ▼
┌──────────────────────────────────────────────┐
│  bot.py: MessageHandler                      │
│  ├─ Extract URL dari text                    │
│  ├─ Check VIP / trial                        │
│  └─ Delegate ke resolver                     │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  terabox/resolver.py: Multi-Strategy         │
│  ├─ savetube.resolve(url)    ← Primary      │
│  ├─ publicearn.resolve(url)  ← Fallback #1  │
│  └─ direct.resolve(url)      ← Fallback #2  │
└──────────────┬───────────────────────────────┘
               │ direct_link
               ▼
┌──────────────────────────────────────────────┐
│  terabox/downloader.py: Download & Upload    │
│  ├─ aiohttp stream to temp file              │
│  ├─ Progress callback → Telegram edit        │
│  └─ Auto-detect: doc/video/audio → upload    │
└──────────────┬───────────────────────────────┘
               │
               ▼
         File terkirim ke user ✅
```

### Payment Flow

```
/bayar → klikqris.create() → QR code → User scan → KlikQRIS webhook
→ webhook_server verifikasi → DB approve → VIP aktif → Notifikasi user
```

---

## 🐳 Deployment

### Opsi 1: Docker (Rekomendasi)

```bash
# Build image
docker compose build

# Run di background
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

**docker-compose.yml** sudah termasuk:
- Auto-restart (`unless-stopped`)
- Volume untuk temporary downloads
- Environment dari `.env`

### Opsi 2: Systemd (Linux VPS)

```bash
# Buat service file
sudo tee /etc/systemd/system/terabox-bot.service << 'EOF'
[Unit]
Description=Terabox Downloader Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/terabox-downloader
EnvironmentFile=/root/terabox-downloader/.env
ExecStart=/root/terabox-downloader/venv/bin/python bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable & start
sudo systemctl daemon-reload
sudo systemctl enable terabox-bot
sudo systemctl start terabox-bot

# Monitor
sudo journalctl -u terabox-bot -f
```

### Opsi 3: Manual + Screen

```bash
# Install screen jika belum
apt install screen -y

# Buat session
screen -S terabox

# Run bot
cd /root/terabox-downloader
source venv/bin/activate
python bot.py

# Detach: Ctrl+A, D
# Reattach: screen -r terabox
```

### Opsi 4: Cloudflare Tunnel (untuk webhook)

Jika VPS tidak punya IP publik:

```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Buat tunnel
cloudflared tunnel --url http://localhost:8000

# Output: https://xxx.trycloudflare.com
# Gunakan URL ini sebagai WEBHOOK_HOST di .env
```

---

## 🧩 Extending

### Menambah Resolver Strategy

Buat file baru di `terabox/strategies/`:

```python
"""MyCustom strategy for Terabox resolution."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def resolve(url: str) -> Optional[dict]:
    """Resolve Terabox URL using MyCustom API.

    Args:
        url: Full Terabox URL.

    Returns:
        dict with keys: file_name, sizebytes, direct_link, strategy_used
        None if this strategy cannot resolve the URL.
    """
    try:
        # Implementasi resolve logic
        return {
            "file_name": "video.mp4",
            "sizebytes": 123456789,
            "direct_link": "https://cdn.example.com/file.mp4",
            "strategy_used": "mycustom",
        }
    except Exception as e:
        logger.error(f"MyCustom resolve gagal: {e}")
        return None
```

Lalu daftarkan di `terabox/resolver.py`:

```python
from terabox.strategies import savetube, publicearn, direct, mycustom

STRATEGIES = [savetube, publicearn, direct, mycustom]
```

### Mengganti Payment Gateway

Payment gateway diisolasi di `payments/klikqris.py`. Untuk mengganti provider, implementasi interface yang sama:

```python
# Interface yang harus diimplementasi
async def create_transaction(order_id: str, amount: int, keterangan: str) -> dict:
    """Returns: {"success": bool, "qris_url": str, "order_id": str, ...}"""

async def check_status(order_id: str) -> dict:
    """Returns: {"success": bool, "status": "PENDING"|"SUCCESS"|"EXPIRED", ...}"""
```

Webhook handler di `payments/webhook_server.py` juga perlu disesuaikan dengan format callback provider baru.

---

## 🔒 Keamanan

| Fitur | Implementasi |
|---|---|
| **Webhook Verification** | HMAC-SHA256 signature check setiap callback |
| **Idempotency** | Database check `order_id` mencegah double processing |
| **Admin Auth** | Setiap admin command verifikasi ID Telegram |
| **No Secrets in Logs** | API key & token tidak di-log |
| **Sandbox Mode** | Testing tanpa transaksi real |
| **SQL Injection** | Semua query pakai parameterized statements |
| **Rate Limiting** | Concurrent download dibatasi `CONCURRENT_DOWNLOADS` |

---

## ❓ FAQ

<details>
<summary><b>Q: Apakah bot ini gratis?</b></summary>

**A:** Bot bisa dijalankan gratis (self-hosted). Biaya operasional: VPS (~$5/bln) + KlikQRIS fee (Rp 1.000/transaksi). Source code 100% gratis — MIT License.
</details>

<details>
<summary><b>Q: Kenapa file tidak terkirim?</b></summary>

**A:** Beberapa kemungkinan:
1. File >50MB — bot kirim direct link, bukan file
2. Link Terabox expired / tidak valid
3. Semua strategi resolver gagal — coba lagi nanti
4. Network error — cek koneksi VPS

Cek log dengan `docker compose logs` atau `journalctl -u terabox-bot`.
</details>

<details>
<summary><b>Q: Gimana cara dapat ID Telegram?</b></summary>

**A:** Chat [@userinfobot](https://t.me/userinfobot) di Telegram. Bot akan kasih ID kamu. Gunakan ini untuk `ADMIN_IDS` di `.env`.
</details>

<details>
<summary><b>Q: Bisakah pakai payment gateway lain?</b></summary>

**A:** Ya. System payment diisolasi di `payments/`. Implementasi interface `create_transaction()` dan `check_status()` untuk provider kamu, lalu sesuaikan webhook handler. Contoh provider: Xendit, Midtrans, Tripay, Oy! Indonesia.
</details>

<details>
<summary><b>Q: Apakah support multi-admin?</b></summary>

**A:** Ya. Pisahkan ID Telegram dengan koma di `ADMIN_IDS`:
```env
ADMIN_IDS=123456789,987654321,555555555
```
</details>

<details>
<summary><b>Q: Bagaimana cara reset database?</b></summary>

**A:** Hapus file `data.db` dan restart bot:
```bash
rm data.db
docker compose restart
```
Bot akan auto-create database baru dengan migrasi.
</details>

<details>
<summary><b>Q: Apakah ada limit download?</b></summary>

**A:** Tergantung konfigurasi:
- **VIP enabled + trial ON**: Free user dapat `VIP_TRIAL_DOWNLOADS` download gratis
- **VIP enabled + trial OFF**: Harus VIP untuk download
- **VIP disabled**: Semua user unlimited
</details>

---

## 📝 Changelog

### v1.1.0 (2026-07-05)

- ✨ **KlikQRIS integration** — dynamic QR + auto webhook
- 🎨 **Inline keyboard UX** — navigasi pakai tombol
- 📖 **README premium** — 500+ baris dokumentasi
- 🔒 HMAC signature verification untuk webhook
- 🧪 Sandbox mode untuk testing pembayaran
- 📊 Admin `/stats` command
- 🐳 Docker Compose support

### v1.0.0 (2026-07-04)

- 🚀 Initial release
- 🔗 Multi-strategy Terabox resolver
- 👑 VIP system dengan trial mode
- 💰 Payment system (manual approve)
- 🛡️ Admin panel
- 📦 SQLite database

---

## 🤝 Kontribusi

Kontribusi selalu diterima! Untuk perubahan besar, buka issue dulu untuk diskusi.

### Development Setup

```bash
# Clone
git clone https://github.com/mocasus/terabox-downloader.git
cd terabox-downloader

# Virtual env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy config
cp .env.example .env
# Isi BOT_TOKEN + ADMIN_IDS

# Run
python bot.py
```

### Guidelines

- 🐍 Ikuti PEP 8
- 📝 Docstring Google style
- ✅ Jangan break existing functionality
- 🧪 Test perubahan kamu sebelum PR
- 📋 Update README jika menambah fitur baru

---

## 📄 Lisensi

MIT License © 2026 [mocasus](https://github.com/mocasus)

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/mocasus">mocasus</a></sub>
  <br>
  <sub>⭐ Star repo ini kalau bermanfaat!</sub>
</p>
