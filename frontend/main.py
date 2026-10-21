"""FastAPI proxy for deployed A2A agent (Agent Runtime, agents-cli 1.1.0+)."""

import os
import re
import uuid
import urllib.request
import xml.etree.ElementTree as ET
import google.auth
import google.auth.transport.requests
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

RESOURCE = os.environ.get(
    "AGENT_ENGINE_RESOURCE_NAME",
    "projects/411799846904/locations/us-east1/reasoningEngines/2841185325173178368",
)
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]

A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)
_A2UI_MIME = "application/json+a2ui"

_creds, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

def _auth_headers() -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {_creds.token}",
        "Content-Type": "application/json",
    }

app = FastAPI()

@app.exception_handler(Exception)
async def _json_errors(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={
            "parts": [{"kind": "text", "text": f"Error: {type(exc).__name__}: {exc}"}]
        },
    )

_contexts: dict[str, str] = {}

def _extract_parts(parts: list) -> list[dict]:
    out: list[dict] = []
    for p in parts:
        if not isinstance(p, dict):
            continue
        text_val = p.get("text")
        if text_val:
            out.append({"kind": "text", "text": text_val})
            continue

        data_obj = p.get("data")
        if data_obj is not None:
            if isinstance(data_obj, dict):
                inner = data_obj.get("data")
                if isinstance(inner, dict):
                    out.append({"kind": "a2ui", "data": inner})
                else:
                    out.append({"kind": "a2ui", "data": data_obj})
            else:
                out.append({"kind": "a2ui", "data": data_obj})
        elif "file" in p and isinstance(p["file"], dict):
            uri = p["file"].get("uri")
            if uri:
                out.append({"kind": "text", "text": uri})
    return out

@app.get("/api/news")
async def get_news(query: str = ""):
    """Fetch live Metro traffic & incident news."""
    feed_url = "https://www.antaranews.com/rss/metro.xml"
    req = urllib.request.Request(feed_url, headers={"User-Agent": "Mozilla/5.0 (compatible; TrafficWatchID/1.0)"})
    articles = []
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            root = ET.fromstring(resp.read())
            items = root.findall(".//item")
            for item in items:
                title_elem = item.find("title")
                link_elem = item.find("link")
                desc_elem = item.find("description")
                pub_elem = item.find("pubDate")

                title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                raw_desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
                clean_desc = re.sub(r"<[^>]+>", "", raw_desc).strip()
                pub_date = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else ""

                if query:
                    q = query.lower()
                    if q not in title.lower() and q not in clean_desc.lower():
                        continue

                articles.append({
                    "title": title,
                    "link": link,
                    "summary": clean_desc,
                    "published": pub_date,
                })
                if len(articles) >= 8:
                    break
    except Exception as e:
        return JSONResponse({"articles": [], "error": str(e)})

    return JSONResponse({"articles": articles})

@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    user_id = body.get("user_id") or "web-user"
    parts: list[dict] = []

    msg_payload = {
        "messageId": str(uuid.uuid4()),
        "role": "user",
        "parts": [{"text": message}],
    }
    if _contexts.get(user_id):
        msg_payload["contextId"] = _contexts[user_id]

    rpc_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "message/send",
        "params": {
            "message": msg_payload
        }
    }

    async with httpx.AsyncClient(headers=_auth_headers(), timeout=120) as client:
        resp = await client.post(A2A_BASE, json=rpc_payload)
        resp_data = resp.json()

        if "error" in resp_data:
            err = resp_data["error"]
            return JSONResponse({"parts": [{"kind": "text", "text": f"Error: {err.get('message')}"}]})

        result = resp_data.get("result") or {}
        if result.get("contextId"):
            _contexts[user_id] = result["contextId"]

        # 1. Check artifacts in result
        for artifact in result.get("artifacts") or []:
            parts.extend(_extract_parts(artifact.get("parts") or []))

        # 2. Check history in result if no artifacts
        if not parts:
            for history_msg in result.get("history") or []:
                if history_msg.get("role") in ("agent", "ROLE_AGENT"):
                    parts.extend(_extract_parts(history_msg.get("parts") or []))

        # 3. Check direct parts if present
        if not parts and "parts" in result:
            parts.extend(_extract_parts(result.get("parts") or []))

    if not parts:
        parts = [{"kind": "text", "text": "(The agent didn't return a reply.)"}]
    return JSONResponse({"parts": parts})

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
