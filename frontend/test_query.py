import google.auth
import google.auth.transport.requests
import httpx
import json
import uuid

RESOURCE = "projects/411799846904/locations/us-east1/reasoningEngines/2841185325173178368"
LOCATION = "us-east1"
AGENT_DIRECTORY = "app"
A2A_BASE = f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"

creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
creds.refresh(google.auth.transport.requests.Request())
client = httpx.Client(headers={"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"}, timeout=120)

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "message/send",
    "params": {
        "message": {
            "messageId": str(uuid.uuid4()),
            "role": "user",
            "parts": [{"text": "Halo TrafficWatch, saya komuter dari Tebet ke Sudirman naik mobil plat ganjil. Cek aturan Ganjil-Genap dan rute terbaik hari ini."}]
        }
    }
}
resp = client.post(A2A_BASE, json=payload)
print("Status:", resp.status_code)
print("Response:", json.dumps(resp.json(), indent=2)[:1000])
