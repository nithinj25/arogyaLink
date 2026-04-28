<div align="center">

# 🏥 ArogyaLink

### Emergency Healthcare Coordination for Rural India

[![Live Demo](https://img.shields.io/badge/Live%20Demo-solution--challenge--cb95c.web.app-blue?style=for-the-badge&logo=firebase)](https://solution-challenge-cb95c.web.app)
[![Backend API](https://img.shields.io/badge/Backend%20API-Cloud%20Run-4285F4?style=for-the-badge&logo=googlecloud)](https://arogyalink-backend-852047333356.asia-south1.run.app/docs)
[![Google Solution Challenge](https://img.shields.io/badge/Google%20Solution%20Challenge-2025-EA4335?style=for-the-badge&logo=google)](https://developers.google.com/community/gdsc-solution-challenge)

**One phone call. Any language. Any village. Instant emergency dispatch.**

[Live Demo](https://solution-challenge-cb95c.web.app) · [API Docs](https://arogyalink-backend-852047333356.asia-south1.run.app/docs) · [Report Bug](https://github.com/nithinj25/arogyaLink/issues)

</div>

---

## The Problem

600 million rural Indians face a life-threatening gap in emergency healthcare access. When a medical emergency strikes in a remote village, families don't know who to call, don't speak the official language, and can't navigate complex health systems. By the time help arrives, it's often too late.

**ArogyaLink bridges this gap with a single phone call.**

---

## What It Does

A villager dials one number. An AI agent answers in their language — Hindi, Kannada, Telugu, or English — asks the right questions to understand the emergency, and simultaneously dispatches the nearest ASHA worker, ambulance, and PHC doctor. No app. No internet. No literacy required.

```
Caller dials → AI triages in local language → Dispatches help → Coordinator monitors live
        ↑                    ↑                       ↑                     ↑
    Twilio IVR          Gemini AI              Firebase RTDB          Web Dashboard
```

---

## Demo

| Web Dashboard | Mobile App |
|:---:|:---:|
| ![Dashboard](https://solution-challenge-cb95c.web.app) | Flutter app with emergency button |
| Live call monitoring, family registry, case history | One-tap emergency call, register family, call history |

**Live:** https://solution-challenge-cb95c.web.app

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CALLER                               │
│              (Feature phone, 2G network)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │ Voice call
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    TWILIO IVR                               │
│         Speech recognition (STT) → TwiML response          │
└─────────────────────┬───────────────────────────────────────┘
                      │ Webhook
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              FASTAPI BACKEND (Cloud Run)                    │
│                                                             │
│   ┌─────────────┐    ┌──────────────┐   ┌──────────────┐  │
│   │Conversation │    │   Triage     │   │  Dispatch    │  │
│   │   Agent     │───▶│   Agent      │──▶│   Agent      │  │
│   │(Gemini AI)  │    │(Gemini AI)   │   │              │  │
│   └─────────────┘    └──────────────┘   └──────┬───────┘  │
│                                                 │          │
│   ┌─────────────┐    ┌──────────────┐          │          │
│   │Registration │    │  Orchestrator│          │          │
│   │   Agent     │    │              │          │          │
│   └─────────────┘    └──────────────┘          │          │
└─────────────────────────────────────────────────┼──────────┘
                      │                           │
          ┌───────────┼───────────────────────────┤
          ▼           ▼                           ▼
┌──────────────┐ ┌──────────┐            ┌──────────────┐
│  Firebase    │ │Firestore │            │ ASHA Workers │
│  Realtime DB │ │ Families │            │  PHC Doctors │
│  (Live calls)│ │  Cases   │            │  Ambulances  │
└──────────────┘ └──────────┘            └──────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              REACT WEB DASHBOARD                            │
│     Live calls · Family registry · Case history            │
│         https://solution-challenge-cb95c.web.app            │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 🗣️ Multilingual Voice IVR
- Supports **Hindi, Kannada, Telugu, English**
- Speech recognition stays in regional language
- TTS fallback to English for unsupported languages (Polly.Aditi)
- Works on **2G networks and basic feature phones**

### 🤖 Gemini-Powered AI Agents
| Agent | Role |
|-------|------|
| **Conversation Agent** | Multi-turn emergency dialogue, extracts symptom/severity/location |
| **Triage Agent** | Classifies emergency severity and required response level |
| **Location Agent** | Resolves caller location to coordinates |
| **Dispatch Agent** | Identifies nearest PHC, ASHA worker, ambulance |
| **Comms Agent** | Sends SMS/FCM alerts to responders |
| **Registration Agent** | IVR-based family registration flow |

### 👨‍👩‍👧 Family Registry
- Register families with full health profiles (members, conditions, allergies, blood group)
- When a registered number calls, AI greets by name and skips address questions
- Auto-fills location from registered address
- Member-aware triage (knows existing conditions)

### 📊 Real-Time Dashboard
- Live call monitoring via Firebase Realtime Database
- Full conversation transcript viewer
- Agent pipeline status (triage → dispatch → comms)
- Family registry CRUD
- Case history with search

### 📱 Flutter Mobile App
- Emergency call button with haptic feedback
- Family registration flow
- Call history
- Works on Android & iOS

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Voice IVR** | Twilio Voice, TwiML, Polly.Aditi TTS |
| **AI / LLM** | Google Gemini 2.0 Flash (via AI Studio) |
| **Backend** | FastAPI, Python 3.11, Uvicorn |
| **Database** | Firebase Realtime Database (live calls), Cloud Firestore (families/cases) |
| **Deployment** | Google Cloud Run, Docker |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS |
| **Hosting** | Firebase Hosting |
| **Mobile** | Flutter 3.27, Dart, go_router, google_fonts |

---

## Project Structure

```
gsc/
├── arogyalink-backend/          # FastAPI backend
│   ├── agents/
│   │   ├── conversation.py      # Gemini conversation agent
│   │   ├── triage.py            # Emergency triage
│   │   ├── dispatch.py          # Responder dispatch
│   │   ├── location.py          # Location resolution
│   │   ├── comms.py             # SMS/FCM notifications
│   │   ├── registration.py      # IVR registration agent
│   │   └── orchestrator.py      # Pipeline orchestrator
│   ├── routes/
│   │   ├── voice.py             # Twilio webhook handlers
│   │   ├── families.py          # Family registry REST API
│   │   └── cases.py             # Cases REST API
│   ├── firebase/
│   │   └── client.py            # Firebase Admin SDK
│   ├── services/
│   │   ├── gemini.py            # Gemini AI client
│   │   └── twilio_voice.py      # TwiML builders
│   ├── Dockerfile
│   ├── cloudbuild.yaml
│   └── main.py
│
├── arogyalink-frontend/         # React web dashboard
│   ├── src/
│   │   ├── components/ui/       # Button, Card, Input, Badge, Divider
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx
│   │   │   ├── Dashboard.tsx    # Live call monitoring
│   │   │   ├── FamiliesPage.tsx
│   │   │   └── CasesPage.tsx
│   │   └── lib/
│   │       ├── api.ts           # REST API client
│   │       └── firebase.ts      # Firebase Web SDK
│   ├── firebase.json
│   └── .firebaserc
│
└── arogyalink-mobile/           # Flutter mobile app
    └── lib/
        ├── features/
        │   ├── home/            # Emergency button screen
        │   ├── register/        # Family registration
        │   ├── history/         # Call history
        │   └── profile/         # Profile & settings
        ├── core/
        │   ├── theme/           # Stone palette + Playfair Display
        │   ├── models/          # Family, Case models
        │   └── services/        # API service (Dio)
        └── widgets/             # EmergencyButton, CaseCard, etc.
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Flutter 3.27+
- Twilio account with a phone number
- Google AI Studio API key (Gemini)
- Firebase project

### 1. Clone the repo
```bash
git clone https://github.com/nithinj25/arogyaLink.git
cd arogyaLink
```

### 2. Backend setup
```bash
cd arogyalink-backend
pip install -r requirements.txt

# Copy env file and fill in your values
cp .env.example .env
# Edit .env with your API keys

# Run
python main.py
```

### 3. Frontend setup
```bash
cd arogyalink-frontend
npm install

# Copy env file and fill in your Firebase config
cp .env.example .env
# Edit .env with your Firebase Web SDK config

npm run dev
```

### 4. Flutter app
```bash
cd arogyalink-mobile
flutter pub get
flutter run -d chrome   # web
flutter run             # connected device
```

### 5. Expose backend for Twilio (local dev)
```bash
ngrok http 8080
# Copy the https URL → paste into Twilio webhook as: https://xxx.ngrok.app/language
```

---

## Environment Variables

### Backend (`.env`)
```env
GEMMA_API_KEY=         # Google AI Studio API key
GEMMA_MODEL=           # gemini-2.0-flash
FIREBASE_DATABASE_URL= # https://your-project-default-rtdb.firebaseio.com
FIREBASE_PROJECT_ID=   # your-project-id
TWILIO_ACCOUNT_SID=    # ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=     # your-auth-token
TWILIO_PHONE_NUMBER=   # +1xxxxxxxxxx
APP_BASE_URL=          # your ngrok or Cloud Run URL
GOOGLE_APPLICATION_CREDENTIALS= # path to firebase-service-account.json
```

### Frontend (`.env`)
```env
VITE_API_URL=                    # Backend URL
VITE_FIREBASE_API_KEY=
VITE_FIREBASE_AUTH_DOMAIN=
VITE_FIREBASE_DATABASE_URL=
VITE_FIREBASE_PROJECT_ID=
VITE_FIREBASE_STORAGE_BUCKET=
VITE_FIREBASE_MESSAGING_SENDER_ID=
VITE_FIREBASE_APP_ID=
```

---

## Deployment

### Backend → Google Cloud Run
```bash
cd arogyalink-backend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/arogyalink-backend
gcloud run deploy arogyalink-backend \
  --image gcr.io/YOUR_PROJECT_ID/arogyalink-backend \
  --region asia-south1 \
  --allow-unauthenticated
```

### Frontend → Firebase Hosting
```bash
cd arogyalink-frontend
npm run build
npx firebase-tools deploy --only hosting
```

Full deployment guide: [DEPLOY.md](DEPLOY.md)

---

## SDG Alignment

ArogyaLink directly addresses **UN Sustainable Development Goal 3: Good Health and Well-Being** by:

- Eliminating language barriers in emergency healthcare
- Bringing AI-powered triage to zero-connectivity rural areas
- Enabling faster dispatch of ASHA workers and ambulances
- Giving district health coordinators real-time visibility into emergencies

---

## Team

Built for **Google Solution Challenge 2025** by Nithin J.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
