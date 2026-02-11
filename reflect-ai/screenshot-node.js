import htmlToImage from 'node-html-to-image';

const url = 'http://localhost:3000';

htmlToImage(url, {
  puppeteerArgs: {
    '--no-sandbox': true,
    '--disable-setuid-sandbox': true,
  },
  puppeteer: {
    headless: true,
  },
}).then(data => {
  data.toFile('./reflect-ai-screenshot.png');
  console.log('Screenshot saved');
}).catch(error => {
  console.error('Error:', error);
});
