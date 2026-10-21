# Project Brief: TrafficWatch ID (Smart Indonesian Commuter Assistant)

## 1. Project Overview
**TrafficWatch ID** is an intelligent AI commuter assistant designed for Indonesian urban centers (Jabodetabek, Bandung, Surabaya). It helps daily commuters navigate traffic disruptions, odd-even (Ganjil-Genap) municipal regulations, infrastructure projects (MRT Fase 2A, LRT, TransJakarta), and monsoon street flooding (*genangan air* / *banjir*).

---

## 2. Key Capabilities & Features
- **Cross-Session Commuter Memory**: Automatically remembers user routes (e.g., *Tebet ➜ Sudirman*), usual departure windows, vehicle odd/even license plates, and rain sensitivity across conversations.
- **Incident & Closure Management**: Reads and reports structured traffic closures, construction detours, and road incidents stored in Firestore.
- **Real-Time News Monitoring**: Fetches live Indonesian metro transit news bulletins from Antara RSS feeds.
- **Weather & Flood Risk Detection**: Evaluates real-time precipitation and localized waterlogging risk along commuter corridors via Open-Meteo.
- **Geocoding & Transit Waypoint Discovery**: Resolves Indonesian addresses to coordinates and locates nearby transit hubs using Google Maps Geocoding and Places (New) REST APIs.
- **Visual Alert Generation**: Generates contextual traffic advisory cards and infographics using `gemini-3.1-flash-lite-image`, saving session artifacts and publishing them to Cloud Storage.
- **Secure Route Code Execution**: Performs commute math, detour delay calculations, and time-window estimations inside a remote Agent Engine Python Sandbox.
- **Rich Card UI (A2UI v0.8)**: Emits structured display cards with headings, lists, badges, and image components.

---

## 3. Architecture & Google Stack

| Component | Technology / Service | Role |
| :--- | :--- | :--- |
| **Agent Framework** | Google ADK (`google-adk`) + Gemini 2.5 Flash | Core reasoning and multi-tool orchestration |
| **Agent Runtime** | Vertex AI Agent Engine (`us-east1`) | Managed serverless agent container hosting (A2A protocol) |
| **Long-Term Memory** | Vertex AI Memory Bank | Cross-session user preferences and commute profile persistence |
| **Database** | Google Cloud Firestore (Native Mode) | Traffic alert storage and incident records |
| **Image Generation** | Gemini Image Generation (`gemini-3.1-flash-lite-image`) | Traffic map schematics and detour infographics |
| **Asset Storage** | Google Cloud Storage (GCS) | Public hosting for generated image assets |
| **Maps Integration** | Google Maps Geocoding & Places (New) API | Location coordinates and nearby station discovery |
| **Code Sandbox** | Agent Engine Sandbox Code Executor | Isolated Python compute environment |
| **Rich Display UI** | A2UI v0.8 Basic Catalog | Visual card generation for chat interface |
| **Frontend Web App** | FastAPI A2A Proxy + Vanilla HTML/CSS Chat UI | Lightweight web interface deployed to Cloud Run |

---

## 4. Deployed Endpoints
- **Agent Engine Runtime ID**: `projects/411799846904/locations/us-east1/reasoningEngines/2841185325173178368`
- **Memory Bank ID**: `1671656796940402688`
- **Live Frontend (Cloud Run)**: `https://trafficwatch-id-frontend-411799846904.us-east1.run.app`
- **GitHub Repository**: `https://github.com/hanifnew/buildwithgemini-trafficwatch-id`
