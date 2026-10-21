#!/usr/bin/env node

import { chromium } from 'playwright';
import { execSync } from 'child_process';
import path from 'path';
import fs from 'fs';

const TARGET_URL = 'http://localhost:8080';
const OUTPUT_FILE = path.resolve(process.cwd(), 'trafficwatch_demo.webm');
const TMP_DIR = path.resolve(process.cwd(), '.video_tmp');

if (!fs.existsSync(TMP_DIR)) {
  fs.mkdirSync(TMP_DIR, { recursive: true });
}

async function run() {
  console.log('--- Launching Comprehensive Full-Feature Showcase Demo Recording ---');
  
  const browser = await chromium.launch({
    executablePath: '/usr/bin/google-chrome',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--window-size=1280,800'],
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    recordVideo: {
      dir: TMP_DIR,
      size: { width: 1280, height: 800 },
    },
  });

  const page = await context.newPage();
  console.log(`Navigating to ${TARGET_URL}...`);
  await page.goto(TARGET_URL, { waitUntil: 'networkidle' });
  await page.waitForTimeout(4000);

  // 1. Showcase Running News Ticker Bar & Ganjil-Genap Pill
  console.log('[Showcase 1/5] Highlighting live running text news marquee and Ganjil-Genap indicator...');
  await page.hover('.ticker-track-container');
  await page.waitForTimeout(3000);

  // 2. Showcase Commuter Profile Modal with Memory Bank Sync
  console.log('[Showcase 2/5] Opening Commuter Profile Modal...');
  await page.click('#profile-btn');
  await page.waitForTimeout(2000);

  console.log('Customizing commuter profile...');
  await page.fill('#prof-name', 'Hanif (Komuter Jakarta)');
  await page.waitForTimeout(1000);
  await page.selectOption('#prof-plate', 'Mobil Plat GANJIL (Angka Akhir 1, 3, 5, 7, 9)');
  await page.waitForTimeout(1000);
  await page.fill('#prof-route', 'Tebet ke SCBD / Sudirman via Casablanca');
  await page.waitForTimeout(1000);
  await page.selectOption('#prof-pref', 'Hindari Jalur Banjir/Genangan Air');
  await page.waitForTimeout(1500);

  console.log('Saving profile to Vertex AI Memory Bank...');
  await page.click('#modal-save-btn');
  await page.waitForTimeout(22000); // Wait for agent to store to Memory Bank

  // 3. 1-Click Commuter Daily Route Check (A2UI Card Evaluation)
  console.log('[Showcase 3/5] Testing 1-Click "Cek Rute Harian Saya" quick chip...');
  const dailyChip = page.locator('.chip:has-text("Cek Rute Harian Saya")');
  await dailyChip.click();
  await page.waitForTimeout(26000); // Wait for A2UI route card & Ganjil-Genap evaluation

  // 4. Multimodal Detour Infographic Image Generation (Gemini Image + GCS)
  console.log('[Showcase 4/5] Requesting Detour Infographic Map Generation (Gemini Image)...');
  await page.fill('#input', 'Tolong buatkan gambar peta rute skematik infografis pengalihan arus di Bundaran HI untuk panduan komuter.');
  await page.click('.btn-submit');
  await page.waitForTimeout(28000); // Wait for Gemini Image generation & GCS upload

  // 5. Weather & Flood Risk Real-Time Check (Open-Meteo)
  console.log('[Showcase 5/5] Checking Weather & Flood Risk along Jakarta corridors...');
  await page.fill('#input', 'Pantau cuaca terkini dan potensi titik genangan air / banjir di jalur komuter Jakarta Selatan');
  await page.click('.btn-submit');
  await page.waitForTimeout(22000); // Wait for Open-Meteo tool response

  console.log('Finalizing full demo recording...');
  await page.waitForTimeout(5000);

  const video = page.video();
  await page.close();
  await context.close();
  await browser.close();

  const savedVideoPath = await video.path();
  console.log('Raw video saved to:', savedVideoPath);

  // Speedup 1.3x for smooth ~1.5 - 2 min playback
  const spedPath = path.join(TMP_DIR, 'sped.webm');
  execSync(`ffmpeg -y -i "${savedVideoPath}" -filter_complex "[0:v]setpts=0.75*PTS[v]" -map "[v]" "${spedPath}"`);
  fs.copyFileSync(spedPath, OUTPUT_FILE);
  console.log('Final demo video successfully generated at:', OUTPUT_FILE);
}

run().catch((err) => {
  console.error('Recording failed:', err);
  process.exit(1);
});
