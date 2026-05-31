# Deploy FloTrack on Vercel

## Step 1 — Push latest code to GitHub

```bash
git add .
git commit -m "Fix Vercel deployment"
git push origin main
```

## Step 2 — Vercel project settings

In [vercel.com](https://vercel.com) → your project → **Settings**:

| Setting | Value |
|---------|--------|
| **Framework Preset** | Other |
| **Root Directory** | *(leave empty)* |
| **Build Command** | `python scripts/prepare_vercel.py` |
| **Output Directory** | *(leave empty — do NOT set to `public` or `frontend`)* |
| **Install Command** | *(leave empty)* |

## Step 3 — Environment variables

**Settings → Environment Variables** (add for Production, Preview, Development):

| Name | Example |
|------|---------|
| `MONGO_URI` | `mongodb+srv://user:pass@cluster.mongodb.net/?appName=FloTrack1` |
| `JWT_SECRET` | long random string (32+ characters) |
| `DATABASE_NAME` | `flotrack_db` |
| `JWT_ALGORITHM` | `HS256` |
| `JWT_EXPIRE_MINUTES` | `10080` |
| `CORS_ORIGINS` | `https://flotrack-swart.vercel.app` |

Use your **exact** Vercel URL in `CORS_ORIGINS` (from the Vercel dashboard).

## Step 4 — MongoDB Atlas

1. **Network Access** → Add IP Address → **Allow Access from Anywhere** (`0.0.0.0/0`)
2. Confirm database user password is correct in `MONGO_URI`

## Step 5 — Redeploy

1. **Deployments** tab → latest deployment → **⋯** → **Redeploy**
2. Wait until status is **Ready** (green)

## Step 6 — Open the correct URLs

| URL | What you should see |
|-----|---------------------|
| `https://YOUR-PROJECT.vercel.app/login.html` | Login page |
| `https://YOUR-PROJECT.vercel.app/` | Redirects to login |
| `https://YOUR-PROJECT.vercel.app/api/health` | `{"status":"ok",...}` |

## If you still see "404: NOT_FOUND"

That Vercel error means **no successful deployment** is linked to that URL.

1. Open **Deployments** — is the latest build **Ready** or **Error**?
2. If **Error**, open **Build Logs** and fix the error shown there.
3. Confirm you are opening the URL from the **Ready** deployment (not an old failed one).
4. Try the deployment-specific URL, e.g. `flotrack-xxxxx.vercel.app` from the deployment card.

## If the page loads but login fails

- Check **Runtime Logs** in Vercel for API errors
- Verify `MONGO_URI` and `JWT_SECRET` are set
- Test API: visit `/api/health` — `database` should say `"connected"`
