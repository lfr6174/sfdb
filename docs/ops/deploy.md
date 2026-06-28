# 部署指南

架構：Railway（Django 後端）+ Vercel（Vue 前端）+ Cloudflare（DNS/Proxy）

(By Claude Sonnet 4.6)

---

## 事前準備

- Railway 帳號（已升級付費方案）
- Vercel 帳號
- Cloudflare 帳號（有自訂網域時才需要；現階段用平台提供的免費網域可略過）
- repo 已 push 到 GitHub

---

## 一、Railway 後端

### 1-1 建立專案與服務

1. Railway dashboard → **New Project → Deploy from GitHub repo**
2. 選 `sfdb` repo
3. Service → **Settings → Root Directory** 填 `backend`
4. Service → **Settings → Watch Paths** 填 `backend/**`（避免前端異動觸發後端 rebuild）

### 1-2 加掛 PostgreSQL

1. 同一專案 → **New → Database → PostgreSQL**
2. Railway 會自動在後端服務注入 `DATABASE_URL`，不需手動複製貼上

### 1-3 環境變數

到 **Service → Variables** 新增以下變數：

| 變數 | 值 |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.prod` |
| `SECRET_KEY` | 用 `python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"` 產生 |
| `ALLOWED_HOSTS` | 部署後取得的 Railway 網域，例如 `sfdb-api.up.railway.app` |
| `CORS_ALLOWED_ORIGINS` | 前端 Vercel 網域，例如 `https://tsfdb.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | 後端自己的網域，例如 `https://sfdb-api.up.railway.app` |
| `ADMIN_URL` | 隨機字串，例如 `myadmin-xk29/`（結尾要有 `/`） |

> `DATABASE_URL` 由 Railway PostgreSQL 外掛自動注入，不用手填。

### 1-4 部署流程

`railway.json` 的 `startCommand` 會依序自動執行：

```
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 60
```

首次部署完成後，到 Railway shell 執行一次 seed：

```bash
python manage.py seed
```

### 1-5 Railway 原生備份

Railway 付費方案的 PostgreSQL 服務內建自動備份：

1. PostgreSQL service → **Settings → Backups**
2. 開啟 **Automatic Backups**，選擇保留天數

手動備份：同頁面 → **Create Backup**

---

## 二、Vercel 前端

### 2-1 建立專案

1. Vercel dashboard → **Add New Project → Import Git Repository**
2. 選 `sfdb` repo
3. **Root Directory** 填 `frontend`
4. Framework 選 **Vite**（通常自動偵測）

### 2-2 環境變數

到 **Project → Settings → Environment Variables** 新增：

| 變數 | 環境 | 值 |
|---|---|---|
| `VITE_API_BASE_URL` | Production | `https://<railway 後端網域>/api` |
| `API_BASE_URL` | Production | `https://<railway 後端網域>/api` |

> `VITE_API_BASE_URL` 是 build-time 變數，Vercel 在 build 時注入，覆蓋 repo 裡 `.env.production` 的 placeholder。
> `API_BASE_URL` 是 runtime 變數，給 `api/render.ts` 和 `api/sitemap.ts` 的 edge functions 讀取。

### 2-3 收緊 CSP connect-src

網域確定後，把 `frontend/vercel.json` 的 CSP `connect-src` 從：

```
connect-src 'self' https:
```

改成：

```
connect-src 'self' https://<railway 後端網域>
```

---

## 三、Cloudflare（有自訂網域時）

> 現階段使用 `*.vercel.app` / `*.up.railway.app` 免費網域可略過此節。

1. Cloudflare → **Add Site** 加入自訂網域
2. 在 registrar 把 nameserver 改成 Cloudflare 提供的
3. DNS → 新增：
   - 前端：`CNAME` `@` 或 `www` → `cname.vercel-dns.com`，Proxy 開啟（橘雲）
   - 後端：`CNAME` `api` → Railway 提供的網域，Proxy 開啟
4. Vercel / Railway 各自 dashboard 加入自訂網域
5. 更新 Railway 環境變數 `ALLOWED_HOSTS`、`CORS_ALLOWED_ORIGINS`、`CSRF_TRUSTED_ORIGINS` 為正式網域
6. 更新 Vercel 環境變數 `VITE_API_BASE_URL`、`API_BASE_URL` 為正式後端網域
7. 更新 `frontend/vercel.json` CSP `connect-src`，送 PR、merge、redeploy

---

## 環境變數速查表

### Railway（後端）

| 變數 | 必填 | 說明 |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | ✅ | `config.settings.prod` |
| `SECRET_KEY` | ✅ | 50+ 字元隨機字串 |
| `ALLOWED_HOSTS` | ✅ | 後端網域（逗號分隔，不含 `https://`） |
| `CORS_ALLOWED_ORIGINS` | ✅ | 前端網域（含 `https://`，逗號分隔） |
| `CSRF_TRUSTED_ORIGINS` | ✅ | 後端網域（含 `https://`，逗號分隔） |
| `ADMIN_URL` | ✅ | 非猜得到的路徑，結尾加 `/` |
| `DATABASE_URL` | 自動注入 | Railway PostgreSQL 外掛提供 |

### Vercel（前端）

| 變數 | 必填 | 說明 |
|---|---|---|
| `VITE_API_BASE_URL` | ✅ | `https://<後端網域>/api`，build-time 注入 |
| `API_BASE_URL` | ✅ | 同上，edge function runtime 用 |
