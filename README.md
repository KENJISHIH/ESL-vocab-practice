# ESL Vocabulary Practice

給孩子用的 ESL 每週單字練習網站，純前端、部署在 GitHub Pages。

🔗 **線上使用**：https://kenjishih.github.io/ESL-vocab-practice/
📋 **更新日誌**：[CHANGELOG.md](CHANGELOG.md)

## 功能

- **⭐ 每日模式**：依日期自動算出今天該背的兩個字（老師規定每天兩個），首頁顯示今日進度卡與連續完成天數
- **🔁 複習錯過的字**：答錯過又還沒練熟的字自動收進來，答對 3 次自動畢業
- **熟練度追蹤**：每個字的對錯次數會記在瀏覽器裡，單字列表標示 ✅ 熟了 / 🔁 要複習 / 📖 練習中
- **四種練習模式**：單字列表（Study）、字卡（Cards）、選擇題（Quiz，雙向出題）、拼字（Spell，帶提示與多空格）
- **Reading / Science 類別切換**，可只練某一類
- **Achernar 真人發音**：預錄音檔，無音檔時自動退回瀏覽器語音
- **中文釋義開關**：一鍵展開／收合該週所有單字的中文意思（預設收合）
- **Avatar Shop 換裝**：練習賺金幣，幫角色換服裝、帽子、鞋子、配件、寵物、背景
- **週次／考試範圍下拉**：單週、期中考、期末考、複習範圍快選
- **可加到 iPhone 主畫面像 App**（PWA，全螢幕，離線也能開）

## 技術

- 單檔 SPA：原生 HTML + vanilla JS（不依賴框架／打包工具）
- 資料驅動：`vocab_manifest.js` 登記週次、考試範圍與每日進度計畫（`DAILY_PLAN`），各週單字存在 `*_data.js`
- 學習進度：存在瀏覽器 `localStorage`（`esl_user_profile`），換裝置不會同步
- 發音：`audio/*.m4a`（Gemini TTS Achernar 語音預先產生）
- 離線：`sw.js`（程式與單字走 network-first，音檔與圖片走 cache-first）
- 部署：GitHub Pages

## 每學期要改的設定

`vocab_manifest.js` 的 `DAILY_PLAN`：

| 欄位 | 說明 |
|---|---|
| `semester` | 目前學期代號，需與 `VOCAB_MANIFEST` 一致 |
| `startDate` | 該學期 W1 Day1，**必須是星期一** |
| `skipDates` | 不上課的平日（國定假日、連假、段考週…），**沒填會讓每日進度超前** |

## 本機啟動

```bash
python3 -m http.server 8000
# 瀏覽器開 http://localhost:8000
```

## 擴充新學期單字

OCR 流程與工具說明見 [`tools/README.md`](tools/README.md)。
