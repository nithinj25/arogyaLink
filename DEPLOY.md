# ArogyaLink — Deployment Guide

## Prerequisites
- `gcloud` CLI authenticated (`gcloud auth login`)
- `firebase` CLI installed (`npm i -g firebase-tools && firebase login`)
- Project ID: `solution-challenge-cb95c`

---

## 1. Backend → Google Cloud Run

### One-time setup
```bash
gcloud config set project solution-challenge-cb95c
gcloud services enable run.googleapis.com containerregistry.googleapis.com
```

### Build & deploy
```bash
cd arogyalink-backend

# Build and push image
gcloud builds submit --tag gcr.io/solution-challenge-cb95c/arogyalink-backend

# Deploy to Cloud Run (asia-south1 = Mumbai)
gcloud run deploy arogyalink-backend \
  --image gcr.io/solution-challenge-cb95c/arogyalink-backend \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --set-env-vars "ENV=production,FIREBASE_PROJECT_ID=solution-challenge-cb95c,FIREBASE_DATABASE_URL=https://solution-challenge-cb95c-default-rtdb.firebaseio.com,GEMMA_MODEL=gemini-2.0-flash" \
  --set-secrets "GEMMA_API_KEY=gemma-api-key:latest,TWILIO_ACCOUNT_SID=twilio-sid:latest,TWILIO_AUTH_TOKEN=twilio-token:latest,TWILIO_PHONE_NUMBER=twilio-number:latest,GOOGLE_APPLICATION_CREDENTIALS=firebase-sa:latest"
```

> After deploy, copy the Cloud Run URL (e.g. `https://arogyalink-backend-xxxx-el.a.run.app`)

### Update Twilio webhook
Go to Twilio Console → Phone Numbers → your number → Voice:
- Set **A Call Comes In** → Webhook → `https://<CLOUD_RUN_URL>/language`

### Upload Firebase service account as a secret (first time)
```bash
gcloud secrets create firebase-sa --data-file=firebase-service-account.json
```
For other secrets:
```bash
echo -n "your-value" | gcloud secrets create gemma-api-key --data-file=-
echo -n "your-value" | gcloud secrets create twilio-sid --data-file=-
echo -n "your-value" | gcloud secrets create twilio-token --data-file=-
echo -n "your-value" | gcloud secrets create twilio-number --data-file=-
```

---

## 2. Frontend → Firebase Hosting

### Fill in your production .env
Edit `arogyalink-frontend/.env.production`:
- Set `VITE_API_URL` to your Cloud Run URL above
- Fill in Firebase Web SDK config from Firebase Console

### Build & deploy
```bash
cd arogyalink-frontend

# Build with production env
cp .env.production .env
npm run build

# Deploy to Firebase Hosting
firebase deploy --only hosting
```

Live at: **https://solution-challenge-cb95c.web.app**

---

## 3. Quick re-deploy (after code changes)

Backend:
```bash
cd arogyalink-backend
gcloud builds submit --tag gcr.io/solution-challenge-cb95c/arogyalink-backend
gcloud run deploy arogyalink-backend --image gcr.io/solution-challenge-cb95c/arogyalink-backend --region asia-south1
```

Frontend:
```bash
cd arogyalink-frontend && npm run build && firebase deploy --only hosting
```

---

## 4. Flutter App (APK for demo)

```bash
cd arogyalink-mobile
# Edit lib/core/services/api_service.dart — set defaultValue to your Cloud Run URL
flutter build apk --release
# APK at: build/app/outputs/flutter-apk/app-release.apk
```

---

## Live URLs after deploy
| Service | URL |
|---------|-----|
| Frontend (Web) | https://solution-challenge-cb95c.web.app |
| Backend API | https://arogyalink-backend-xxxx-el.a.run.app |
| API Health | https://arogyalink-backend-xxxx-el.a.run.app/health |
| API Docs | https://arogyalink-backend-xxxx-el.a.run.app/docs |
