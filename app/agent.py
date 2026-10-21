# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo
from google.cloud import firestore

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types


MODEL = "gemini-3.7-flash"
PROJECT_ID = "qwiklabs-gcp-03-e50049ae2385"
COLLECTION_NAME = "traffic_alerts"

# Initialize Firestore client with hardcoded project ID
db = firestore.Client(project=PROJECT_ID)


def list_traffic_alerts(status_filter: Optional[str] = "active") -> List[Dict[str, Any]]:
    """List traffic alerts and road closure reports from the database.

    Args:
        status_filter: Filter by alert status ('active', 'resolved', or None for all).

    Returns:
        A list of traffic alert dictionaries.
    """
    col_ref = db.collection(COLLECTION_NAME)
    if status_filter:
        query = col_ref.where(filter=firestore.FieldFilter("status", "==", status_filter))
        docs = query.stream()
    else:
        docs = col_ref.stream()

    alerts = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        alerts.append(data)
    return alerts


def get_traffic_alert_details(alert_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific traffic alert.

    Args:
        alert_id: The unique identifier of the traffic alert (e.g. 'alert-jkt-001').

    Returns:
        Dictionary containing alert details, or an error message if not found.
    """
    doc_ref = db.collection(COLLECTION_NAME).document(alert_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Traffic alert '{alert_id}' not found."}
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def report_traffic_alert(
    title: str,
    location: str,
    alert_type: str,
    severity: str,
    description: str,
    alternate_routes: Optional[List[str]] = None,
    affected_transit: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Report or record a new traffic incident, road closure, or hazard.

    Args:
        title: Short headline of the incident or road closure.
        location: Street, intersection, or area affected (e.g., 'Jl. Sudirman').
        alert_type: Type of incident (e.g., 'construction', 'weather', 'accident', 'regulation').
        severity: Severity level ('low', 'medium', 'high', 'critical').
        description: Detailed explanation of the disruption and expected impact.
        alternate_routes: Suggested alternative roads or detours.
        affected_transit: Public transit lines affected (e.g., MRT, TransJakarta).

    Returns:
        Confirmation dictionary with the created alert ID and timestamp.
    """
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    doc_id = f"alert-{int(datetime.datetime.now().timestamp())}"
    alert_data = {
        "id": doc_id,
        "title": title,
        "location": location,
        "type": alert_type,
        "severity": severity,
        "status": "active",
        "description": description,
        "alternate_routes": alternate_routes or [],
        "affected_transit": affected_transit or [],
        "created_at": now,
    }
    db.collection(COLLECTION_NAME).document(doc_id).set(alert_data)
    return {"status": "success", "alert_id": doc_id, "data": alert_data}


def update_traffic_alert_status(alert_id: str, new_status: str) -> Dict[str, Any]:
    """Update the status of an existing traffic alert (e.g., mark as 'resolved' or 'active').

    Args:
        alert_id: The ID of the alert to update.
        new_status: The new status ('active', 'resolved', 'monitoring').

    Returns:
        Confirmation dictionary.
    """
    doc_ref = db.collection(COLLECTION_NAME).document(alert_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Traffic alert '{alert_id}' not found."}
    doc_ref.update({"status": new_status})
    return {"status": "success", "alert_id": alert_id, "new_status": new_status}


def fetch_traffic_rss_alerts(
    query: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, str]]:
    """Fetch recent Indonesian metro traffic, transit, and infrastructure news from RSS feeds.

    Args:
        query: Optional keyword to filter articles (e.g. 'macet', 'banjir', 'penutupan', 'transjakarta', 'mrt').
        limit: Maximum number of articles to return (default: 10).

    Returns:
        A list of articles with title, link, description, and published date.
    """
    import re
    import urllib.request
    import xml.etree.ElementTree as ET

    feed_url = "https://www.antaranews.com/rss/metro.xml"
    req = urllib.request.Request(feed_url, headers={"User-Agent": "Mozilla/5.0 (compatible; TrafficWatchID/1.0)"})

    results = []
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
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

                results.append({
                    "title": title,
                    "link": link,
                    "summary": clean_desc,
                    "published": pub_date,
                })
                if len(results) >= limit:
                    break
    except Exception as e:
        return [{"error": f"Failed to fetch RSS alerts: {str(e)}"}]

    return results


def get_route_weather_and_flood_risk(location_name: str = "Jakarta") -> Dict[str, Any]:
    """Check current weather, rainfall, and potential flood/puddle risk for a commute area or city.

    Uses the Open-Meteo free public API (no API key required). Heavy rainfall in Indonesian urban areas
    (e.g., Jakarta, Bandung, Surabaya) directly causes street flooding (genangan air) and massive traffic delays.

    Args:
        location_name: Name of the city or district (e.g., 'Jakarta', 'Jakarta Selatan', 'Bekasi', 'Tangerang').

    Returns:
        Dictionary containing temperature, precipitation (mm), rain intensity, weather description, and flood risk level.
    """
    import json
    import urllib.parse
    import urllib.request

    try:
        # 1. Geocode location name with Jabodetabek district fallback
        clean_name = location_name.strip()
        # Fallback coordinates for common Greater Jakarta districts
        known_locations = {
            "jakarta selatan": (-6.2615, 106.8106, "Jakarta Selatan (South Jakarta)"),
            "jakarta pusat": (-6.1865, 106.8341, "Jakarta Pusat (Central Jakarta)"),
            "jakarta barat": (-6.1683, 106.7589, "Jakarta Barat (West Jakarta)"),
            "jakarta timur": (-6.2250, 106.9004, "Jakarta Timur (East Jakarta)"),
            "jakarta utara": (-6.1384, 106.8640, "Jakarta Utara (North Jakarta)"),
            "kemang": (-6.2738, 106.8169, "Kemang, Jakarta Selatan"),
            "sudirman": (-6.2198, 106.8224, "Sudirman Corridor, Jakarta"),
            "thamrin": (-6.1950, 106.8230, "Thamrin Corridor, Jakarta"),
            "kuningan": (-6.2297, 106.8294, "HR Rasuna Said / Kuningan, Jakarta"),
        }
        lower_name = clean_name.lower()
        if lower_name in known_locations:
            lat, lon, resolved_name = known_locations[lower_name]
        else:
            encoded_name = urllib.parse.quote(clean_name)
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_name}&count=1&language=en&format=json"
            req_geo = urllib.request.Request(geo_url, headers={"User-Agent": "TrafficWatchID/1.0"})
            with urllib.request.urlopen(req_geo, timeout=6) as resp:
                geo_res = json.loads(resp.read())

            if not geo_res.get("results"):
                return {"error": f"Location '{location_name}' could not be resolved."}

            top_hit = geo_res["results"][0]
            lat = top_hit["latitude"]
            lon = top_hit["longitude"]
            resolved_name = f"{top_hit.get('name', clean_name)}, {top_hit.get('admin1', '')} ({top_hit.get('country_code', '')})"

        # 2. Get current precipitation and weather
        w_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,precipitation,rain,showers,weather_code&timezone=auto"
        )
        req_w = urllib.request.Request(w_url, headers={"User-Agent": "TrafficWatchID/1.0"})
        with urllib.request.urlopen(req_w, timeout=6) as resp:
            w_res = json.loads(resp.read())

        current = w_res.get("current", {})
        rain = current.get("rain", 0.0)
        precip = current.get("precipitation", 0.0)
        temp = current.get("temperature_2m")
        w_code = current.get("weather_code", 0)

        # Interpret flood / waterlogging risk for urban roads
        if precip >= 15.0 or rain >= 15.0:
            flood_risk = "HIGH - Heavy downpour detected. High risk of severe waterlogging / banjir on arterial roads."
        elif precip >= 5.0 or rain >= 5.0:
            flood_risk = "MODERATE - Moderate rainfall. Puddle formation and slow traffic expected, riders exercise caution."
        elif precip > 0.0 or rain > 0.0:
            flood_risk = "LOW - Light rain or drizzle. Wet roads and minor delays."
        else:
            flood_risk = "MINIMAL - Dry conditions reported. No rain-related disruptions."

        return {
            "query_location": location_name,
            "resolved_location": resolved_name,
            "latitude": lat,
            "longitude": lon,
            "temperature_celsius": temp,
            "precipitation_mm": precip,
            "rain_mm": rain,
            "flood_risk_level": flood_risk,
            "observation_time": current.get("time"),
        }
    except Exception as e:
        return {"error": f"Failed to retrieve weather data: {str(e)}"}


import os
from google.cloud import storage
import google.genai as genai
from google.adk.tools import ToolContext

BUCKET_NAME = "trafficwatch-id-assets-qwiklabs-gcp-03-e50049ae2385"


def geocode_address(address: str) -> Dict[str, Any]:
    """Turn an address or landmark into geographic coordinates using the Google Maps Geocoding API.

    Args:
        address: The street address, intersection, or landmark name (e.g. 'Bundaran HI, Jakarta').

    Returns:
        Dictionary containing formatted address, latitude, longitude, and place_id.
    """
    import json
    import urllib.parse
    import urllib.request

    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY is not configured in the environment."}

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TrafficWatchID/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("status") != "OK" or not data.get("results"):
            return {"error": f"Geocoding failed for '{address}': {data.get('status')}"}

        result = data["results"][0]
        location = result["geometry"]["location"]
        return {
            "query": address,
            "formatted_address": result.get("formatted_address"),
            "latitude": location.get("lat"),
            "longitude": location.get("lng"),
            "place_id": result.get("place_id"),
        }
    except Exception as e:
        return {"error": f"Failed to call Geocoding API: {str(e)}"}


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "transit_station",
    radius_meters: float = 1500.0,
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    """Find nearby places (such as transit stations, police posts, gas stations) using Google Maps Places API (New).

    Args:
        latitude: Latitude of the center location.
        longitude: Longitude of the center location.
        place_type: Type of place to search for (e.g., 'transit_station', 'subway_station', 'bus_station', 'gas_station', 'police').
        radius_meters: Search radius in meters (default: 1500.0).
        max_results: Maximum number of places to return (default: 5).

    Returns:
        List of place dictionaries with name, formatted_address, and location coordinates.
    """
    import json
    import urllib.request

    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return [{"error": "GOOGLE_MAPS_API_KEY is not configured in the environment."}]

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": min(max_results, 10),
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "radius": float(radius_meters),
            }
        },
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        places = []
        for p in data.get("places", []):
            display_name = p.get("displayName", {}).get("text", "Unknown")
            address = p.get("formattedAddress", "")
            loc = p.get("location", {})
            places.append({
                "name": display_name,
                "address": address,
                "latitude": loc.get("latitude"),
                "longitude": loc.get("longitude"),
            })
        return places
    except Exception as e:
        return [{"error": f"Failed to call Places API: {str(e)}"}]


def generate_traffic_alert_image(
    prompt: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generate a visual traffic infographic, detour advisory, or road disruption map schematic using Gemini Image generation.

    The generated image is saved as an artifact in the session and uploaded to public Cloud Storage for web viewing.

    Args:
        prompt: Description of the visual alert or advisory card to generate (e.g. 'Stylized morning traffic map schematic showing MRT detour at Bundaran HI Jakarta with caution signs').
        tool_context: ADK ToolContext used to save session artifacts.

    Returns:
        Dictionary containing public GCS URL, artifact status, and image details.
    """
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        image_bytes = None
        mime_type = "image/jpeg"
        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break

        if not image_bytes:
            return {"error": "No image was returned by gemini-3.1-flash-lite-image model."}

        # 1. Save artifact to ADK session context
        ext = "png" if "png" in mime_type else "jpg"
        timestamp = int(datetime.datetime.now().timestamp())
        filename = f"traffic_alert_{timestamp}.{ext}"
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "filename": filename,
            "public_image_url": public_url,
            "mime_type": mime_type,
            "prompt_used": prompt,
        }
    except Exception as e:
        return {"error": f"Failed to generate and upload image: {str(e)}"}


import base64


def generate_traffic_alert_video(
    prompt: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generate a short video clip for traffic updates, corridor advisories, or weather road conditions using Google's Omni model (gemini-omni-flash-preview).

    The generated video is saved as an artifact in the session and uploaded to public Cloud Storage for web viewing.

    Args:
        prompt: Description of the short video clip to generate (e.g. 'A short 3-second cinematic video clip showing busy Jakarta evening traffic in the rain with motorcycle headlights and wet asphalt reflections').
        tool_context: ADK ToolContext used to save session artifacts.

    Returns:
        Dictionary containing public GCS URL, artifact status, and video details.
    """
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        output_video = getattr(interaction, "output_video", None)
        if not output_video or not getattr(output_video, "data", None):
            return {"error": "No video was returned by gemini-omni-flash-preview model."}

        video_bytes = base64.b64decode(output_video.data)
        mime_type = getattr(output_video, "mime_type", "video/mp4") or "video/mp4"

        # 1. Save artifact to ADK session context
        timestamp = int(datetime.datetime.now().timestamp())
        filename = f"traffic_video_{timestamp}.mp4"
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload video bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "filename": filename,
            "public_video_url": public_url,
            "mime_type": mime_type,
            "prompt_used": prompt,
        }
    except Exception as e:
        return {"error": f"Failed to generate and upload video: {str(e)}"}


from google.adk.code_executors import AgentEngineSandboxCodeExecutor

AGENT_ENGINE_RESOURCE_NAME = (
    "projects/411799846904/locations/us-east1/reasoningEngines/1671656796940402688"
)

sandbox_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=AGENT_ENGINE_RESOURCE_NAME
)

async def generate_memories_callback(callback_context: CallbackContext):
    """Save salient commuter preferences and facts across sessions."""
    await callback_context.add_session_to_memory()
    return None


from .a2ui_instruction import INSTRUCTION
from .a2ui_utils import a2ui_callback

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=INSTRUCTION,
    code_executor=sandbox_executor,
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    tools=[
        PreloadMemoryTool(),
        list_traffic_alerts,
        get_traffic_alert_details,
        report_traffic_alert,
        update_traffic_alert_status,
        fetch_traffic_rss_alerts,
        get_route_weather_and_flood_risk,
        geocode_address,
        find_nearby_places,
        generate_traffic_alert_image,
        generate_traffic_alert_video,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)




