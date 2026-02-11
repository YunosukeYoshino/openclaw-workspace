const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'reflect-ai-screenshot.png', fullPage: true });
  await browser.close();
  console.log('Screenshot saved to reflect-ai-screenshot.png');
})();
