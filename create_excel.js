const XLSX = require('xlsx');

// データ
const newsData = [
  ["No.", "タイトル", "ソース", "日時", "URL"],
  ["1", "AIが作業を代行してくれる「Claude Cowork」、Windows版が登場", "PC Watch", "2/12(木) 17:06", "https://news.yahoo.co.jp/articles/c9b4ef55dea56a5cb28751ec8077ef73c7b1a424"],
  ["2", "Coinbase、AIエージェント専用ウォレットインフラをリリース", "NADA NEWS", "2/12(木) 16:55", "https://news.yahoo.co.jp/articles/55f63bf61fa70ea18dfbfbc82ee1a1e77f323e21"],
  ["3", "「雲」から降りてきたAIは「パーソナル」な存在になれるのか――開催から1カ月経過した「CES 2026」を振り返る", "ITmedia PC USER", "2/12(木) 17:05", "https://news.yahoo.co.jp/articles/5ad407ec4ccebd50cf11e1a32a94f1ef7bc85034"],
  ["4", "AIで週1～7時間の業務を削減--AIが生成した成果物の修正や検証に週1～4時間", "ZDNET Japan", "2/12(木) 16:30", "https://news.yahoo.co.jp/articles/6d3b90872233cba6a04b265ad522d2426e67fd41"],
  ["5", "セーフィー、映像データとAIを組み合わせた「Safie AI Studio」を提供", "ZDNET Japan", "2/12(木) 15:51", "https://news.yahoo.co.jp/articles/1f3c617361e824e9da927d9e4d0ede7ee7e3f3c0"],
  ["6", "「高市首相vs.ウルトラマン」「悟空vs.ドラえもん」も……中国発の新動画AI「Seedance2.0」物議", "ITmedia NEWS", "2/12(木) 12:16", "https://news.yahoo.co.jp/articles/0165c53be5f2d19804bc8a157c369b4027dda786"],
  ["7", "AI要約でサイト「素通り」傾向は", "Yahoo! News", "-", "https://news.yahoo.co.jp/pickup/6569394"],
];

// ワークブックを作成
const wb = XLSX.utils.book_new();

// メインシートを作成
const ws = XLSX.utils.aoa_to_sheet(newsData);

// 列幅設定
ws['!cols'] = [
  { wch: 6 },   // No.
  { wch: 70 },  // タイトル
  { wch: 18 },  // ソース
  { wch: 14 },  // 日時
  { wch: 50 },  // URL
];

// シートをワークブックに追加
XLSX.utils.book_append_sheet(wb, ws, "AI 最新ニュース");

// サマリーシートを作成
const summaryData = [
  ["AI 最新ニュースレポート"],
  [""],
  ["作成日時:", new Date().toLocaleString('ja-JP')],
  ["ニュース数:", newsData.length - 1],
  [""],
  ["ソース:", "Yahoo! News (ITカテゴリ)"],
  [""],
  ["カテゴリ:", "AI / 人工知能 / 生成AI"],
  [""],
  ["掲載媒体一覧:"],
  ["  • PC Watch"],
  ["  • NADA NEWS"],
  ["  • ITmedia PC USER"],
  ["  • ZDNET Japan"],
  ["  • ITmedia NEWS"],
  ["  • Yahoo! News"],
];

const summaryWs = XLSX.utils.aoa_to_sheet(summaryData);
summaryWs['!cols'] = [
  { wch: 30 },
  { wch: 40 },
];

XLSX.utils.book_append_sheet(wb, summaryWs, "サマリー");

// ファイルを保存
XLSX.writeFile(wb, '/workspace/ai_news_report.xlsx');
console.log('Excelファイルを作成しました: ai_news_report.xlsx');
