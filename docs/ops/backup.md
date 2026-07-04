
# 簡述

利用 Railway cron service 執行 `pg_dump` 匯出壓縮的資料庫檔案，再經驗證與加密後上傳至 Cloudflare r2 備份。

# 準備加密金鑰
採用非對稱加密，以公鑰加密匯出的檔案，就不需要在雲端存放解密金鑰。首先用以下指令生成密鑰對：

```bash
age-keygen -o tsfdb-backup-key-1.txt
age-keygen -o tsfdb-backup-key-2.txt
```

公鑰是輸出檔中 `# public key: age1...` 那一行，將它們以**空白隔開**填入`AGE_RECIPIENTS`，確保任一把私鑰皆可解密。建議將私鑰分開保存，以免遺失後無法解密資料。


# 設定 Cloudflare R2
Cloudflare R2 的免費方案提供 10 GB 儲存容量，而且也不收取 Egress 費用。雖然啟用服務需要綁定信用卡，但實際上用量都在額度內。

1. 註冊 [Cloudflare](https://www.cloudflare.com/) 帳號，進入[個人頁面](https://dash.cloudflare.com/)
2. 從側欄依序點選**儲存空間和資料庫**、**R2物件儲存**、**啟用 R2**，接著填寫信用卡付款資訊
3. 啟用 R2 後，從側欄進入**R2物件儲存**，點選**建立貯體**
  - 貯體名稱：tsfdb-backups
  - 位置：亞太地區
  - 預設儲存體類別：標準（用於每月至少存取一次的物件）
4. 在**R2物件儲存**最下方的**帳戶詳細資訊**，點選API令牌**{}管理**，再點選**建立Account API權杖**
  - 權杖名稱：railway-psql-backups-to-r2
  - 權限：物件讀取和寫入
  - 指定貯體：僅套用至特定貯體（`tsfdb-backups`）
  - TTL：永久
5. 抄下權杖值、存取金鑰識別碼、秘密存取金鑰、針對 S3 用戶端使用管轄區域特定端點
6. 在**R2物件儲存**的**設定**，點選**物件生命週期規則**右側的**+**符號新增規則
  - 規則名稱：tsfdb-olr
  - 規則範圍：`daily/`
  - 生命週期動作：`在此之後刪除上傳的物件: 90 天`


# 設定 Railway
1. 進入 Project 點選 **+ Add** 新增 **GitHub Repository**，再選取 *Settings** 調整設置：
  - Root Directory：`/backup`
  - Regions & Replicas：Southeast Asia (Singapore, Singapore)
  - Builder：Dockerfile
  - Dockerfile Path：Dockerfile
  - Cron Schedule：Daily， `0 19 * * *`（19:00 UTC = 03:00 台北）
2. 點選**Variables**填入環境變項，
  - `DATABASE_URL`：Add Reference：`${{Postgres.DATABASE_URL}}`
  - `AGE_RECIPIENTS`：用空白隔開的兩把 age 公鑰
  - `R2_BUCKET`：`tsfdb-backups`
  - `R2_ENDPOINT`：針對 S3 用戶端使用管轄區域特定端點，`https://<account_id>.r2.cloudflarestorage.com`
  - `R2_ACCESS_KEY_ID`：R2 API token 的存取金鑰識別碼
  - `R2_SECRET_ACCESS_KEY`：R2 API token 的秘密存取金鑰
  - `MIN_DUMP_BYTES`：dump 大小下限（bytes）


# 手動測試
1. 手動觸發一次 deploy，log 應依序出現：
   `dumping... verifying... encrypting... uploading... backup ok: tsfdb-<日期>.dump.age (<大小> bytes, dump <大小> bytes)`
2. 到 R2 確認 `daily/` 下有該檔案且大小合理
3. 依 log 中 dump 的實際大小，把 `MIN_DUMP_BYTES` 調到約其一半


# 還原流程

```bash
# 1. 下載（rclone 的 R2 連線環境變數同 backup.sh，或用 rclone config 互動設定）
rclone copy r2:tsfdb-backups/daily/tsfdb-<日期>.dump.age .

# 2. 解密（任一把私鑰皆可）
age -d -i tsfdb-backup-key-1.txt -o db.dump tsfdb-<日期>.dump.age

# 3. 還原
pg_restore --clean --if-exists --no-owner --no-privileges \
           -d "$DATABASE_URL" db.dump
```

（`--no-owner --no-privileges`：managed PG 的角色名稱不一定相同；
roles 由 Railway 管理，不需 `pg_dumpall`。）
