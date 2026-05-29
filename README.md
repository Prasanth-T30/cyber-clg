# FusionGuardNet — Advanced Multimodal Intrusion Detection Framework

```
+-------------------+
| Network Traffic   |
+-------------------+
          |
+-------------------+
| Packet Sniffer    |
| (Scapy/PyShark)   |
+-------------------+
          |
 ---------------------------------------------------
 |                 Fusion Layer                    |
 |-------------------------------------------------|
 | System Logs | User Behavior | Threat Feeds      |
 ---------------------------------------------------
          |
+-------------------+
| AI Detection Core |
| CNN + LSTM + RF   |
+-------------------+
          |
+-------------------+
| Alert Dashboard   |
+-------------------+
```

## Tech Stack

| Layer    | Technology                              |
|----------|-----------------------------------------|
| Frontend | React 18 · Vite · Tailwind CSS          |
| Backend  | FastAPI (Python 3.11+) · Uvicorn        |
| Database | InstantDB (real-time)                   |
| ML / DL  | TensorFlow/Keras · scikit-learn · NumPy |
| Sniffer  | Scapy (simulation mode by default)      |

## Detected Attacks

| Attack            | Model           | Method       |
|-------------------|-----------------|--------------|
| DDoS              | Random Forest   | Rule + ML    |
| Port Scanning     | LSTM            | Rule + ML    |
| Brute Force       | LSTM            | Rule + ML    |
| Malware Traffic   | CNN             | Rule + ML    |
| SQL Injection     | CNN + Regex     | Rule + ML    |

---

## Quick Start

### 1. Clone & set up backend

```bash
cd fusionguardnet/backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Copy env file
cp .env.example .env
# Edit .env with your InstantDB credentials (optional for local use)
```

### 2. Run backend

```bash
uvicorn app.main:app --reload --port 8000
```

On first start the ML models are trained on synthetic data and cached to
`app/ml/models/saved/`. Subsequent starts load from cache instantly.

API docs: http://localhost:8000/docs  
WebSocket: ws://localhost:8000/ws/alerts

### 3. Set up & run frontend

```bash
cd ../frontend
npm install
cp .env.example .env
npm run dev
```

Open: http://localhost:5173

---

## Project Structure

```
fusionguardnet/
├── backend/
│   ├── app/
│   │   ├── main.py                    ← FastAPI entry point
│   │   ├── core/
│   │   │   ├── config.py              ← Settings (pydantic-settings)
│   │   │   └── security.py           ← JWT helpers
│   │   ├── api/routes/
│   │   │   ├── alerts.py             ← GET/PATCH /alerts
│   │   │   ├── dashboard.py          ← GET /dashboard/stats
│   │   │   ├── detections.py         ← POST /detect/*
│   │   │   └── websocket.py          ← WS /ws/alerts
│   │   ├── database/
│   │   │   └── instantdb.py          ← InstantDB REST client
│   │   ├── packet_sniffer/
│   │   │   ├── sniffer.py            ← Background capture loop
│   │   │   └── packet_processor.py  ← Scapy → dict conversion
│   │   ├── ml/
│   │   │   ├── feature_extractor.py  ← Feature pipelines
│   │   │   ├── fusion_layer.py       ← Multi-modal signal fusion
│   │   │   ├── models/
│   │   │   │   ├── cnn_model.py      ← CNN (byte sequences)
│   │   │   │   ├── lstm_model.py     ← LSTM (event sequences)
│   │   │   │   └── random_forest_model.py ← RF (flow features)
│   │   │   └── detection/
│   │   │       ├── ddos_detector.py
│   │   │       ├── port_scan_detector.py
│   │   │       ├── brute_force_detector.py
│   │   │       ├── malware_detector.py
│   │   │       └── sql_injection_detector.py
│   │   └── data_sources/
│   │       ├── system_logs.py
│   │       ├── user_behavior.py
│   │       └── threat_feeds.py
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Layout/       Navbar, Sidebar
    │   │   ├── Dashboard/    KPIs + timeline chart
    │   │   ├── AlertPanel/   Real-time alert feed
    │   │   ├── NetworkMap/   Canvas IP map
    │   │   ├── ThreatStats/  Attack distribution
    │   │   └── DetectionControl/ Attack simulator
    │   ├── pages/            Home, Alerts, Analytics, Simulate, Settings
    │   ├── hooks/            useAlerts (WebSocket), useDetection
    │   ├── services/         api.js, instantdb.js
    │   └── utils/            helpers.js
    ├── package.json
    ├── vite.config.js
    └── .env.example
```

## InstantDB Setup (Optional)

1. Create a free project at https://instantdb.com
2. Copy your **App ID** → `VITE_INSTANTDB_APP_ID` in `frontend/.env`
3. Generate an **Admin Token** → `INSTANTDB_ADMIN_TOKEN` in `backend/.env`

Without InstantDB credentials the app still runs fully — alerts are stored
in-memory and streamed via WebSocket. InstantDB adds cross-session persistence.

## Live Packet Capture (Advanced)

By default the sniffer runs in simulation mode. To capture real traffic:

```env
# backend/.env
SNIFFER_SIMULATION_MODE=False
SNIFFER_INTERFACE=eth0   # or en0 on macOS
```

> **Requires root/Administrator privileges.**  
> On Linux: `sudo uvicorn app.main:app --reload`

---

Built with ❤️ — FusionGuardNet v1.0
