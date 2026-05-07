# PRD — MoneyForward Clone (KITT-PFM)

## 1. Concept & Vision

**Clone 目標：** MoneyForward ME（個人向け家事簿・資産管理サービス）

> 「家計簿も資産管理も、これひとつ」
> One app to rule all your personal finances — income, expenses, assets, investments.

**KITT-PFM 的核心定位：**
- 在本地環境運行（SQLite + Python）
- 主要透過 Telegram Bot 操作，搭配 KITT 風格 Web 介面
- 不需要任何第三方 API（MoneyForward 的銀行連結、證券帳戶串接不需要了，你自己手動登打）
- 100% 掌控自己的資料

---

## 2. MoneyForward ME 完整功能清單

### 2.1 核心功能（來自官網 + App 分析）

#### A. アカウント（帳戶）管理
- 銀行帳戶登錄（普通存款、定期存款、外幣帳戶）
- 信用卡帳戶登錄
- 電子貨幣（Suica、PASMO、PayPay、LINE Pay）
- 證券帳戶（SBI, 楽天, etc.）
- ポイントカード（積分卡）
- 資産の合計表示（總資產一覽）

#### B. 自動家計簿（收入支出記錄）
- 収入/支出的自動分類
- 日付、金額、カテゴリ、商戶（店名）記錄
- 手動新增/編輯/刪除交易
- ，家賃・光熱費等的定期記録（固定支出）
- まとめて入力（批次輸入）
- レシート撮影（收據拍攝，OCR）

#### C. 家計簿分析
- 月次/年次收支報告
- カテゴリ別支出分析（圓餅圖）
- 収入と支出的推移（趨勢線圖）
- 予算対比（預算 vs 實際）
- 固定費vs変動費分析

#### D. 資産管理
- 全帳戶總資產 Overview
- 資産ポートフォリオ（資產配置比例）
- 負債（房貸、車貸、學貸）
- 純資產（資産 - 負債）

#### E. 投資資産
- 株式・投信残高
- 分配金、受取利息
- 損益状況（保有損益）
- ポートフォリオ分析

#### F. 固定費管理
- 每个月固定支出一覽（房租、房貸、保險、訂閱服務）
- 、契約更新通知
- 無駄なサブスク検出

#### G. データ連携
- 銀行API串接（MoneyForward有自己的「クラウド」）不你需要
- CSV/JSON 匯入匯出
- 他サービスからの移行（數據遷移）

### 2.2 MoneyForward 的 UI 結構（從官網分析）

```
Top Navigation:
├── ダッシュボード（Dashboard）
├── 家計簿（Bookkeeping）
│   ├── 支出（支出清單）
│   ├── 収入（收入清單）
│   ├── 分析（分析報告）
│   └── 検索（搜尋）
├── 資産（Assets）
│   ├── 概要（Overview）
│   ├── 銀行・カード（Bank & Card）
│   ├── 証券（Securities）
│   └── 負債（Debt）
├── 予算（Budget）
├── 固定費（Fixed Cost）
└── 設定（Settings）
    ├── アカウント管理
    ├── カテゴリ設定
    ├── 通知設定
    └── データ連携
```

---

## 3. KITT-PFM Clone 功能範圍（MVP）

### 第一階段：MVP（現在要實作的）

| 模組 | 功能 | 狀態 |
|------|------|------|
| **帳戶管理** | 新增/編輯/刪除帳戶（銀行、信用卡、證券、現金） | ✅ 已有 |
| **交易記帳** | 手動新增收入/支出，類別篩選 | ✅ 已有 |
| **月次報告** | 每月收支摘要（總收入、總支出、結餘） | ✅ 已有 |
| **類別管理** | 系統預設類別 + 自訂類別 | ✅ 已有 |
| **Telegram Bot** | 文字/語音記帳、回報查詢 | ✅ 已有 |
| **Web 介面** | Dashboard + Transactions + Analysis | ✅ 已有 |

### 第二階段：完整 Clone

| 模組 | 功能 |
|------|------|
| **資產總覽** | 所有帳戶餘額加總、資產配置圓餅圖 |
| **預算管理** | 每月類別預算設定，追蹤超支 |
| **固定費追蹤** | 每月固定支出（房租、房貸、保險、訂閱）追蹤與提醒 |
| **投資組合** | 證券帳戶餘額、保有損益計算 |
| **視覺化圖表** | 支出趨勢圖（折線圖）、類別佔比（圓餅圖）、資產推移（柱狀圖） |
| **匯入匯出** | CSV 匯入/匯出 |
| **搜尋功能** | 交易關鍵字搜尋 |

### 第三階段：未來功能

| 模組 | 功能 |
|------|------|
| **銀行API串接** | 如MoneyForward Me的自動取交易（需對應銀行API）- Nick 不需要 |
| **收據OCR** | 拍攝收據自動解析金額/店名/日期（Gemini Vision已可做到）✅ 必要 |
| **通知系統** | 固定費到期提醒、預算超支通知 |
| **數據遷移** | 從MoneyForward CSV匯入 |

---

## 8. 確認事項（2026-05-07）

- [x] 個人版 MoneyForward ME是正確目標
- [x] OCR 功能需要（收據拍攝自動解析）
- [x] 優先順序確認：資產總覽 → 視覺化圖表 → 預算管理 → 固定費追蹤 → 投資組合 → CSV匯入
- [x] Layout 參考 MoneyForward，換成 KITT 風格（黑底 + 紅色）

---

## 4. 技術架構

### 目前已實作

```
┌─────────────────────────────────────────────┐
│  Telegram Bot (Python)                       │
│  python-telegram-bot 22.7                    │
│  - 文字/語音記帳                             │
│  - Inline keyboard 操作                      │
└──────────────┬──────────────────────────────┘
               │ SQLite (kitt_pfm.db)
               │ /Users/nickwengsoocii/kitt-pfm/data/
┌──────────────▼──────────────────────────────┐
│  FastAPI (Python)                            │
│  Port 8765                                   │
│  - /api/summary/{year}/{month}               │
│  - /api/transactions                         │
│  - /api/accounts                             │
│  - /api/categories                           │
│  - /api/budgets                              │
└──────────────┬──────────────────────────────┘
               │ /api proxy (Astro)
               │ Port 4321
┌──────────────▼──────────────────────────────┐
│  Astro + React + Tailwind CSS                │
│  KITT Theme (黑底 + 紅色掃描線)               │
│  - Dashboard (首頁月次報告)                   │
│  - Transactions (交易清單)                    │
│  - Analysis (分析圖表)                        │
└─────────────────────────────────────────────┘
```

### 資料庫 Schema

```sql
-- 帳戶
accounts (id, name, type, balance, currency, icon, color, created_at)

-- 類別
categories (id, name, icon, color, parent_id, is_system)

-- 交易
transactions (id, account_id, date, amount, category_id,
              description, merchant, notes, is_confirmed, created_at)

-- 預算
budgets (id, category_id, amount, period)

-- 設定
settings (key, value)
```

---

## 5. UI/UX 設計方向

### KITT 主題（參考 MoneyForward 的佈局）

**色票：**
- Primary: `#FF0000` (KITT 紅)
- Background: `#0D0D0D` (近黑)
- Surface: `#1A1A1A` (卡片背景)
- Border: `#333333`
- Text Primary: `#FFFFFF`
- Text Secondary: `#999999`

**字體：**
- Primary: `JetBrains Mono` (KITT 風格)
- Fallback: `monospace`

**MoneyForward 的佈局借鑒：**
- 左側導航列（固定）
- 頂部狀態列（月份切換、總資產）
- 中央主要內容區
- 右側可選分析面板

---

## 6. MoneyForward 與 KITT-PFM 對比

| 功能 | MoneyForward ME | KITT-PFM |
|------|----------------|----------|
| 銀行API自動同步 | ✅ | ❌（手動記帳）|
|  автоматическая 分類 | ✅ | ⚠️（基本NLU分類）|
| 收據OCR | ✅ | ⚠️（需額外設定）|
| 投資組合追蹤 | ✅ | ⚠️（第二階段）|
| 固定費管理 | ✅ | ⚠️（第二階段）|
| Web + App | ✅ | ⚠️（僅Web + Telegram）|
| 資料所有權 | ❌（雲端）| ✅（本地SQLite）|
| 訂閱費用 | 付費（高級功能）| 免費 |

---

## 7. 實作順序建議

1. **鞏固 MVP** — 確認收支記帳、報告功能完整
2. **資產總覽** — 帳戶餘額總計、圖表化
3. **預算管理** — 類別預算設定與追蹤
4. **視覺化升級** — 趨勢圖、圓餅圖（用 Recharts）
5. **固定費追蹤** — 每月固定支出管理
6. **投資組合** — 證券帳戶（如果Nick有需求）
7. **CSV 匯入** — 從 MoneyForward 匯出 CSV 匯入

---

*Document generated: 2026-05-07*
*Based on: MoneyForward 官網分析 (https://moneyforward.com) + 對話記憶*
