#!/usr/bin/env node
/**
 * Terabox Downloader — One-command installer & launcher.
 *
 *   npx terabox-downloader          → Start bot (setup on first run)
 *   npx terabox-downloader setup    → Configure .env interactively
 *   npx terabox-downloader start    → Run bot
 *   npx terabox-downloader update   → Git pull + restart
 */

const { execSync, spawn } = require('child_process');
const { existsSync, writeFileSync, readFileSync } = require('fs');
const { join } = require('path');
const readline = require('readline');

const REPO = 'https://github.com/mocasus/terabox-downloader';
const DIR = join(process.env.HOME || '/tmp', '.terabox-downloader');
const ENV_FILE = join(DIR, '.env');

const CYAN = '\x1b[36m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const RED = '\x1b[31m';
const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';

function banner() {
  console.log(`
${CYAN}${BOLD}╔══════════════════════════════════╗
║   📦 TERABOX DOWNLOADER BOT     ║
║   Telegram + KlikQRIS           ║
╚══════════════════════════════════╝${RESET}
`);
}

function sh(cmd, opts = {}) {
  try {
    return execSync(cmd, { stdio: opts.silent ? 'pipe' : 'inherit', ...opts }).toString().trim();
  } catch (e) {
    if (!opts.ignore) throw e;
    return '';
  }
}

function prompt(query) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(resolve => rl.question(query, ans => { rl.close(); resolve(ans.trim()); }));
}

async function setup() {
  banner();
  console.log(`${YELLOW}🔧 Setup Wizard — isi .env untuk pertama kali${RESET}\n`);

  if (!existsSync(DIR)) {
    console.log(`${CYAN}📥 Cloning repo...${RESET}`);
    sh(`git clone ${REPO} ${DIR}`, { silent: true });
  }

  const token = await prompt('🤖 Bot Token (dari @BotFather): ');
  const adminIds = await prompt('👑 Admin Telegram ID (pisah koma kalo banyak): ');
  const vipPrice = await prompt('💰 Harga VIP (default: 10000): ') || '10000';
  const vipDays = await prompt('⏳ Durasi VIP hari (default: 7): ') || '7';
  const apiKey = await prompt('🔑 KlikQRIS API Key: ');
  const merchantId = await prompt('🏪 KlikQRIS Merchant ID: ');
  const sandbox = await prompt('🧪 Sandbox mode? (y/N): ');

  const env = [
    `BOT_TOKEN=${token}`,
    `ADMIN_IDS=${adminIds}`,
    `VIP_PRICE=${vipPrice}`,
    `VIP_DURATION_DAYS=${vipDays}`,
    `KLIKQRIS_API_KEY=${apiKey}`,
    `KLIKQRIS_MERCHANT_ID=${merchantId}`,
    `KLIKQRIS_SANDBOX=${sandbox.toLowerCase() === 'y' ? 'true' : 'false'}`,
    `WEBHOOK_HOST=http://localhost:8000`,
    `VIP_ENABLED=true`,
    `VIP_TRIAL_ENABLED=true`,
    `VIP_TRIAL_DOWNLOADS=3`,
    `MAX_FILE_SIZE_MB=500`,
    `DOWNLOAD_DIR=./downloads`,
  ].join('\n');

  writeFileSync(ENV_FILE, env);
  console.log(`\n${GREEN}✅ .env tersimpan di ${ENV_FILE}${RESET}`);

  // Install Python deps
  console.log(`\n${CYAN}📦 Install Python dependencies...${RESET}`);
  if (!existsSync(join(DIR, 'venv'))) {
    sh(`python3 -m venv ${join(DIR, 'venv')}`, { silent: true });
  }
  const pip = join(DIR, 'venv/bin/pip');
  sh(`${pip} install -q -r ${join(DIR, 'requirements.txt')}`, { silent: true });

  console.log(`\n${GREEN}${BOLD}✅ Setup selesai!${RESET}`);
  console.log(`\nJalankan: ${CYAN}npx terabox-downloader start${RESET}\n`);
}

function start() {
  if (!existsSync(ENV_FILE)) {
    console.log(`${RED}❌ .env belum ada. Jalankan setup dulu:${RESET}`);
    console.log(`${CYAN}  npx terabox-downloader setup${RESET}\n`);
    process.exit(1);
  }

  banner();
  const python = join(DIR, 'venv/bin/python3');
  if (!existsSync(python)) {
    console.log(`${RED}❌ venv belum ada. Jalankan setup dulu.${RESET}\n`);
    process.exit(1);
  }

  console.log(`${GREEN}🚀 Starting bot...${RESET}\n`);
  const child = spawn(python, ['bot.py'], {
    cwd: DIR,
    stdio: 'inherit',
    env: { ...process.env },
  });

  child.on('exit', code => {
    console.log(`\n${YELLOW}Bot stopped (exit ${code})${RESET}`);
    process.exit(code);
  });

  process.on('SIGINT', () => child.kill());
  process.on('SIGTERM', () => child.kill());
}

function update() {
  console.log(`${CYAN}🔄 Updating...${RESET}`);
  sh(`cd ${DIR} && git pull`, { silent: true });
  const pip = join(DIR, 'venv/bin/pip');
  sh(`${pip} install -q -r ${join(DIR, 'requirements.txt')}`, { silent: true });
  console.log(`${GREEN}✅ Updated! Jalankan: npx terabox-downloader start${RESET}`);
}

// ── Main ──
const cmd = process.argv[2] || 'start';

if (!existsSync(DIR)) {
  console.log(`${YELLOW}📥 First run — cloning repo...${RESET}`);
  sh(`git clone ${REPO} ${DIR}`, { silent: true });
}

switch (cmd) {
  case 'setup':
    setup().catch(e => { console.error(e); process.exit(1); });
    break;
  case 'start':
    start();
    break;
  case 'update':
    update();
    break;
  default:
    console.log(`Usage: npx terabox-downloader [setup|start|update]`);
    process.exit(0);
}
