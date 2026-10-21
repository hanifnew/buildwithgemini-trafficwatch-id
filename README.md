# TrafficWatch ID 🚗🌧️
> **Intelligent AI Commuter Assistant for Indonesian Urban Corridors**

TrafficWatch ID is an autonomous AI commuter assistant built with Google ADK and Gemini. Designed specifically for Indonesian urban centers (Jabodetabek, Bandung, Surabaya), it helps daily commuters navigate traffic disruptions, odd-even (Ganjil-Genap) municipal regulations, major infrastructure projects (MRT Fase 2A, LRT, TransJakarta), and monsoon street flooding (*genangan air* / *banjir*).

---

## ✨ Features & Capabilities

- 🧠 **Cross-Session Commuter Memory**: Remembers commuter home/work corridors (e.g. *Tebet ➜ Sudirman*), departure schedules, odd/even license plates, and weather sensitivity across sessions using **Vertex AI Memory Bank**.
- 📋 **Incident & Road Closure Tracking**: Queries and reports active road closures, construction detours, and traffic incidents stored in **Google Cloud Firestore**.
- 📰 **Live Metro Transit News**: Fetches real-time traffic and transit bulletins from Antara RSS feeds.
- 🌧️ **Weather & Flood Risk Analysis**: Assesses rainfall intensity and localized waterlogging risk along commuter routes via Open-Meteo.
- 📍 **Geocoding & Transit Waypoint Discovery**: Resolves Indonesian addresses to coordinates and locates nearby transit stations using the **Google Maps Geocoding & Places (New) REST APIs**.
- 🎨 **Visual Advisory Generation**: Creates visual alert schematics and detour infographics using **`gemini-3.1-flash-lite-image`**, saved as session artifacts and published to **Google Cloud Storage**.
- ⚡ **Secure Python Sandbox Execution**: Performs route delay calculations and travel-time comparisons inside an isolated **Agent Engine Code Sandbox**.
- 🪪 **Rich Display UI (A2UI v0.8)**: Emits structured display cards (Cards, Columns, Rows, Text with `usageHint`, and Images) rendered natively in the web chat interface.

---

## 🏗️ Architecture & Technology Stack

| Component | Google Technology / Service | Role |
| :--- | :--- | :--- |
| **Agent Core** | Google ADK (`google-adk`) + Gemini 2.5 Flash | Multi-tool orchestration & commuter reasoning |
| **Agent Runtime** | Vertex AI Agent Engine (`us-east1`) | Managed serverless agent container hosting (A2A protocol) |
| **Long-Term Memory** | Vertex AI Memory Bank | Cross-session commuter route & preference persistence |
| **Database** | Google Cloud Firestore (Native Mode) | Traffic alert storage and incident records |
| **Image Generation** | Gemini Image (`gemini-3.1-flash-lite-image`) | Traffic map schematics and detour advisory cards |
| **Asset Storage** | Google Cloud Storage (GCS) | Public hosting for generated image assets |
| **Maps Integration** | Google Maps Geocoding & Places (New) APIs | Coordinate resolution & transit hub discovery |
| **Code Sandbox** | Agent Engine Sandbox Code Executor | Isolated Python compute environment |
| **UI Protocol** | A2UI v0.8 Basic Catalog | Visual display card generation |
| **Web Frontend** | Cloud Run + FastAPI (A2A Proxy) | Web chat interface with starter chips & session reset |

---

## 📁 Repository Structure

```
.
├── app/
│   ├── agent.py               # Core ADK root_agent, tool definitions & A2UI callback
│   ├── a2ui_instruction.py    # Pre-rendered A2UI v0.8 Basic Catalog system prompt
│   ├── a2ui_utils.py          # A2UI after_model_callback data part wrapper
│   ├── fast_api_app.py        # Local FastAPI wrapper with Memory Bank service
│   └── app_utils/
│       └── services.py        # Vertex AI Memory Bank service factory
├── frontend/
│   ├── main.py                # FastAPI proxy authenticating to Agent Engine over A2A
│   ├── requirements.txt       # Frontend dependencies (fastapi, uvicorn, a2a-sdk, httpx)
│   └── static/
│       └── index.html         # Vanilla JS chat UI with built-in A2UI card renderer
├── tests/
│   └── unit/                  # Unit tests for tools and agent callbacks
├── pyproject.toml             # Python dependencies & ADK packaging configuration
└── project_brief.md           # Concise project brief & domain specifications
```

---

## 🚀 Running Locally

### 1. Prerequisites
- Python 3.11+
- `uv` package manager (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Google Cloud project with Vertex AI and Firestore enabled

### 2. Configure Environment Variables
Create a `.env` file in the project root:
```env
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=global
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
MEMORY_BANK_ID=your-agent-engine-id
```

### 3. Run the Agent Playground
```bash
uv sync
uv run adk web . --port 8080 --reload_agents --memory_service_uri=agentengine://<YOUR_MEMORY_BANK_ID>
```

### 4. Run the Web Frontend Proxy
```bash
cd frontend
pip install -r requirements.txt
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT>/locations/us-east1/reasoningEngines/<ENGINE_ID>"
export AGENT_DIRECTORY="app"
python main.py
```
Open **`http://localhost:8080`** in your browser.

---

## 🚢 Deployment

### Deploy Agent to Vertex AI Agent Runtime
```bash
agents-cli deploy \
  --project <PROJECT_ID> \
  --region us-east1 \
  --update-env-vars GOOGLE_MAPS_API_KEY=<MAPS_KEY>,MEMORY_BANK_ID=<MEMORY_BANK_ID>
```

### Deploy Frontend to Cloud Run
```bash
cd frontend
gcloud run deploy trafficwatch-id-frontend \
  --source . \
  --project <PROJECT_ID> \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME=<RESOURCE_NAME>,AGENT_DIRECTORY=app
```

---

## 📜 License
Apache-2.0
