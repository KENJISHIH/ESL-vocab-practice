# ESL Vocabulary Practice

給孩子用的 ESL 每週單字練習網站，純前端、部署在 GitHub Pages。

🔗 **線上使用**：https://kenjishih.github.io/ESL-vocab-practice/
📋 **更新日誌**：[CHANGELOG.md](CHANGELOG.md)

## 功能

- **四種練習模式**：單字列表（Study）、字卡（Cards）、選擇題（Quiz）、拼字（Spell）
- **Reading / Science 類別切換**，可只練某一類
- **Achernar 真人發音**：預錄音檔，無音檔時自動退回瀏覽器語音
- **中文釋義開關**：一鍵展開／收合該週所有單字的中文意思（預設收合）
- **Avatar Shop 換裝**：練習賺金幣，幫角色換服裝、帽子、鞋子、配件、寵物、背景
- **週次／考試範圍下拉**：單週、期中考、期末考、複習範圍快選
- **可加到 iPhone 主畫面像 App**（PWA，全螢幕）

## 技術

- 單檔 SPA：原生 HTML + vanilla JS（不依賴框架／打包工具）
- 資料驅動：`vocab_manifest.js` 登記週次與範圍，各週單字存在 `*_data.js`
- 發音：`audio/*.m4a`（Gemini TTS Achernar 語音預先產生）
- 部署：GitHub Pages

## 本機啟動

```bash
python3 -m http.server 8000
# 瀏覽器開 http://localhost:8000
```

## 擴充新學期單字

OCR 流程與工具說明見 [`tools/README.md`](tools/README.md)。
