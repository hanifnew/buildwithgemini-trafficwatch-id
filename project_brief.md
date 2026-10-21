# Project Brief: TrafficWatch ID (Smart Indonesian Commuter Assistant) 🚦🇮🇩

## 1. Project Overview
**TrafficWatch ID** is an autonomous AI commuter assistant designed for Indonesian urban centers (Jabodetabek, Bandung, Surabaya). It empowers daily commuters with proactive, real-time intelligence to navigate traffic disruptions, odd-even municipal regulations (*Ganjil-Genap*), major infrastructure projects (MRT Fase 2A, LRT, TransJakarta), and monsoon street flooding (*genangan air* / *banjir*).

Built with the **Google Agent Development Kit (ADK)** and powered by **Google Gemini 3.7 Flash**, TrafficWatch ID unifies cross-session memory, multimodal generative tools (schematic infographic maps and situational video generation), real-time Firestore incident reporting, live weather/flood risk scoring, and interactive card-based A2UI displays into a cohesive commuter web experience.

---

## 2. Key Capabilities & Implemented Features

1. **Cross-Session Commuter Memory (Vertex AI Memory Bank)**:
   - Uses `PreloadMemoryTool` and `generate_memories_callback` to remember commuter profiles across sessions.
   - Automatically recalls preferred corridors (e.g., *Tebet ➜ SCBD via Casablanca*), vehicle license plate odd/even compliance, commute schedules, and route preferences (e.g., *Hindari Jalur Banjir*).

2. **Interactive Commuter Onboarding & 1-Click Route Check**:
   - Built-in "Profil Saya" modal with instant sync to Vertex AI Memory Bank.
   - 1-Click *"Cek Rute Harian Saya"* action button for instantaneous commute analysis against active municipal regulations.

3. **Live Metro News Ticker & Municipal Badges**:
   - Smooth horizontal running text marquee continuously streaming real-time transit headlines from Antara News Metro RSS feed with hover-to-pause interaction.
   - Automatic background polling every 5 minutes for freshness.
   - Dynamic real-time Ganjil-Genap compliance badge (`Hari Ini: Plat GANJIL (21)` / `Plat GENAP`).

4. **Incident & Road Closure Management (Cloud Firestore)**:
   - Multi-tool operations (`list_traffic_alerts`, `get_traffic_alert_details`, `report_traffic_alert`, `update_traffic_alert_status`) connected to Firestore collection `traffic_alerts`.
   - Ingests real-time traffic police alerts from TMC Polda Metro Jaya RSS.

5. **Multimodal Infographic & Video Generation**:
   - **Gemini Image (`gemini-3.1-flash-lite-image`)**: Generates schematic detour maps and advisory infographics, saving them to session artifacts and Cloud Storage.
   - **Google Omni Model (`gemini-omni-flash-preview`)**: Generates short situational commuter video clips in global region and returns public GCS URLs.

6. **Weather & Monsoon Flood Risk Evaluation**:
   - Integrates Open-Meteo API to evaluate real-time precipitation intensity and localized waterlogging risk along commuter corridors.

7. **Geocoding & Transit Waypoint Discovery**:
   - Google Maps Geocoding & Places (New) REST APIs to resolve landmarks and find nearby transit hubs (MRT/LRT stations, bus terminals, gas stations).

8. **Secure Compute & Execution Sandbox**:
   - Remote `AgentEngineSandboxCodeExecutor` for computing travel time estimates, delay penalties, and route comparison math.

9. **Rich Structured Display UI (A2UI v0.8)**:
   - Native A2UI component renderer for cards, columns, rows, headings, badges, and images over the Agent-to-Agent (A2A) JSON-RPC protocol.

---

## 3. Architecture & Google Cloud Stack

| Component | Technology / Service | Role |
| :--- | :--- | :--- |
| **Agent Framework** | Google ADK (`google-adk`) + Gemini 3.7 Flash | Core reasoning and multi-tool orchestration |
| **Agent Runtime** | Vertex AI Agent Engine (`us-east1`) | Managed serverless agent container hosting (A2A protocol) |
| **Long-Term Memory** | Vertex AI Memory Bank | Cross-session user preferences and commute profile persistence |
| **Database** | Google Cloud Firestore (Native Mode) | Traffic alert storage and incident records |
| **Image Generation** | Gemini Image (`gemini-3.1-flash-lite-image`) | Traffic map schematics and detour infographics |
| **Video Generation** | Google Omni (`gemini-omni-flash-preview`) | Situational advisory video generation |
| **Asset Storage** | Google Cloud Storage (GCS) | Public hosting for generated image & video assets |
| **Maps Integration** | Google Maps Geocoding & Places (New) API | Location coordinates and transit hub discovery |
| **Weather & Floods** | Open-Meteo REST API | Real-time precipitation and flood vulnerability alerts |
| **Code Sandbox** | Agent Engine Sandbox Code Executor | Isolated Python compute environment |
| **Rich Display UI** | A2UI v0.8 Basic Catalog | Visual card generation for chat interface |
| **Frontend Web App** | FastAPI A2A Proxy + HTML5/CSS3 Ticker UI | Modern commuter web interface deployed to Cloud Run |

---

## 4. Deployed Endpoints & Resources

- **Agent Engine Runtime Resource**: `projects/411799846904/locations/us-east1/reasoningEngines/2841185325173178368`
- **Vertex AI Memory Bank ID**: `projects/411799846904/locations/us-east1/reasoningEngines/1671656796940402688`
- **Cloud Storage Bucket**: `trafficwatch-id-assets-qwiklabs-gcp-03-e50049ae2385`
- **Live Frontend (Cloud Run)**: `https://trafficwatch-frontend-411799846904.us-east1.run.app`
- **GitHub Repository**: `https://github.com/hanifnew/buildwithgemini-trafficwatch-id`
