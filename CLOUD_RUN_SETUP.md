# Deploy Telegram Bot to Google Cloud Run

## Free Tier Limits
- 2 million requests per month
- 200,000 GB-seconds of CPU time
- 1 GB of network egress per month

---

## Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., `telegram-glm-bot`)
4. Click "Create"

---

## Step 2: Enable APIs

1. In Cloud Console, search for "Cloud Run API"
2. Click "Enable"

3. Search for "Cloud Build API"
4. Click "Enable" (needed to build Docker images)

---

## Step 3: Install Google Cloud SDK

### Windows:
1. Download: https://cloud.google.com/sdk/docs/install
2. Run the installer
3. After install, open PowerShell and authenticate:

```powershell
gcloud init
```

Follow the prompts to:
- Select your Google account
- Choose the project you created
- Choose a region (recommend: `us-central1`)

---

## Step 4: Set Up Environment Variables

Create your env variables (replace with actual values):

```powershell
$env:GLM_API_KEY = "your_glm_api_key_here"
$env:TELEGRAM_BOT_TOKEN = "your_telegram_bot_token_here"
```

---

## Step 5: Deploy to Cloud Run

From the `telegram-glm-bot` directory, run:

```powershell
# Submit the build (builds Docker image in Google's infrastructure)
gcloud builds submit --tag gcr.io/PROJECT_ID/telegram-glm-bot

# Deploy to Cloud Run (replace PROJECT_ID with your actual project ID)
gcloud run deploy telegram-glm-bot `
  --image gcr.io/PROJECT_ID/telegram-glm-bot `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars "GLM_API_KEY=$env:GLM_API_KEY,TELEGRAM_BOT_TOKEN=$env:TELEGRAM_BOT_TOKEN"
```

> Note: Replace `PROJECT_ID` with your actual Google Cloud project ID (shown in console)

---

## Step 6: Verify Deployment

1. Go to: https://console.cloud.google.com/run
2. Click on your service
3. Click "Logs" tab to see the bot running
4. Open Telegram and send a message to your bot

---

## Updating the Bot

After making changes to the code:

```powershell
# Rebuild and redeploy
gcloud builds submit --tag gcr.io/PROJECT_ID/telegram-glm-bot
gcloud run deploy telegram-glm-bot --image gcr.io/PROJECT_ID/telegram-glm-bot --platform managed --region us-central1
```

---

## Monitoring

- **View Logs**: Cloud Console → Cloud Run → your service → Logs
- **View Usage**: Cloud Console → Cloud Run → your service → Metrics

---

## Troubleshooting

### Bot not responding?
- Check logs in Cloud Console
- Verify environment variables are set correctly
- Make sure TELEGRAM_BOT_TOKEN is valid

### Build fails?
- Ensure Cloud Build API is enabled
- Check Dockerfile syntax

### Service keeps restarting?
- Check logs for Python errors
- Verify API keys are correct

---

## Stopping the Service (to avoid charges)

```powershell
gcloud run services delete telegram-glm-bot --region us-central1
```

Or simply delete the Google Cloud project if you don't need it anymore.
