# Deploy Telegram Bot to Koyeb

Koyeb is a EU-based serverless platform with a generous free tier.

## Free Tier
- 512 MB RAM
- 0.1 vCPU
- Always-on (no sleep)
- 3.6 GB storage
- Paris & other EU regions

---

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (name it `telegram-glm-bot`)
3. Don't initialize with README (we already have files)

4. In your project folder, run:

```powershell
cd C:\Users\dench\telegram-glm-bot

git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/telegram-glm-bot.git
git push -u origin main
```

---

## Step 2: Create Koyeb Account

1. Go to https://www.koyeb.com
2. Sign up (GitHub login works well)
3. Verify your email

---

## Step 3: Deploy Your Bot

### Option A: Deploy from GitHub (Recommended)

1. Go to https://app.koyeb.com/apps
2. Click **"Create App"**
3. Select **"GitHub"** as the source
4. Authorize Koyeb to access your GitHub
5. Select your `telegram-glm-bot` repository
6. Configure:
   - **Name**: `telegram-glm-bot`
   - **Region**: `par` (Paris) or closest to you
   - **Instance type**: **Nano** (free tier)
   - **Type**: **Worker** (not a web service)

7. Add Environment Variables:
   ```
   GLM_API_KEY = your_glm_api_key_here
   TELEGRAM_BOT_TOKEN = your_telegram_bot_token_here
   ```

8. Click **"Deploy"**

### Option B: Deploy via CLI

```bash
# Install Koyeb CLI
npm install -g @koyeb/cli

# Authenticate
koyeb login

# Deploy
koyeb app init telegram-glm-bot
cd telegram-glm-bot
koyeb service create
```

---

## Step 4: Verify Deployment

1. Go to https://app.koyeb.com/apps
2. Click on your app
3. Check the **Logs** tab - you should see "Bot is running..."
4. Open Telegram and test your bot

---

## Updating Your Bot

After making code changes:

```powershell
git add .
git commit -m "Your commit message"
git push
```

Koyeb will auto-deploy when it detects changes to your main branch.

---

## Monitoring

- **Logs**: App → Logs tab
- **Metrics**: App → Metrics tab
- **Deployments**: App → Deployments tab

---

## Troubleshooting

### Bot not responding?
- Check Logs tab in Koyeb dashboard
- Verify environment variables are set correctly
- Make sure both API keys are valid

### Build fails?
- Check that `requirements.txt` is present
- Verify `bot.py` has no syntax errors

### Service keeps restarting?
- Check logs for Python errors
- Verify API keys are correct and valid

---

## Free Tier Limits

Your bot should stay well within free limits:
- CPU: A Telegram bot uses very little CPU
- RAM: Python bot uses ~50-100 MB
- Storage: Container is small

You'll only need to upgrade if you add many users or complex features.

---

## Stopping the Service

To stop the bot and avoid charges:
1. Go to https://app.koyeb.com/apps
2. Select your app
3. Click **"Delete"**
