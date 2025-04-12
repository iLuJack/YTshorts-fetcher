# K-Pop Shorts Processor

本專案旨在整理與分析 K-Pop 團體的 YouTube Shorts 資料，並從中篩選出具有挑戰性質的影片（Challenge Shorts）。

---

## 📚 目錄

1. [📁 專案結構說明](#-專案結構說明)
2. [🔧 `utils/`](#-utils)
3. [📂 資料夾說明](#-資料夾說明)
4. [📜 主程式腳本](#-主程式腳本)
5. [📚 重要參考資料](#-重要參考資料)

---

## 📁 專案結構說明

```bash
.
├── data-original
│   ├── kpop-group.csv        # Original K-pop group dataset
│   └── kpop-idol.csv         # List of K-pop idols with group affiliations
├── data-processed
│   ├── kpop-challenge-shorts.json      # Challenge videos output
│   ├── kpop-group-updated.csv          # Updated group information
│   ├── kpop-non-challenge-shorts.json  # Non-challenge videos output
│   ├── kpop_shorts_data.json           # Raw fetched shorts data
│   └── kpop_shorts_data_hashtag_processed.json # Processed shorts with hashtags
├── utils
│   ├── dataset-comparer.py    # Validation tool for group data completeness
│   ├── handle-to-id.py        # Converts YouTube handles to Channel IDs
│   └── hashtag-processor.py   # Extracts hashtags from titles into dedicated field
├── shorts-fetcher.py          # Main script to fetch K-pop shorts from YouTube
└── shorts-challenge-spliter.py # Categorizes shorts into challenge/non-challenge
```

## 🔧 `utils/`

- **`handle-to-id.py`**  
  將頻道的 `@handle`（如 `@bigbang`）轉換成實際的 YouTube `Channel ID`。

- **`dataset-comparer.py`**  
  確保已完整抓取所有指定的 K-Pop 團體資料，用於比對與確認缺漏。

- **`hashtag-processor.py`**  
  解析影片標題中的 Hashtag，並合併進 `hashtags` 欄位中，避免遺漏標題中的重要標籤。

---

## 📂 data 資料夾說明

- **`data-original/`**  
  包含原始資料，例如 K-Pop 團體與成員的對應關係（CSV 格式）。

- **`data-processed/`**  
  儲存處理後的結果資料，例如已整合 Hashtag 與分類的 Shorts 影片資訊。

---

## 📜 主程式腳本

- **`shorts-fetcher.py`**  
  從 YouTube 擷取指定 K-Pop 團體自 2020/1/1 後上傳的 Shorts 影片，包括觀看數、按讚數、留言數、Hashtag、上傳時間等資訊。

- **`shorts-challenger-spliter.py`**  
  將 Shorts 影片依據 Hashtag 進行分類，篩選出 Challenge Shorts。  
  定義為：若影片同時包含本團體（或成員）與其他團體（或成員）的 Hashtag，即視為 Challenge 類型影片。

---

## 📚 重要參考資料

- [如何從 YouTube API 抓取 Shorts - Stack Overflow 討論](https://stackoverflow.com/questions/71192605/how-do-i-get-youtube-shorts-from-youtube-api-data-v3)
- [YouTube 官方 API 文件](https://developers.google.com/youtube/v3/docs/)
