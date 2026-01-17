from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)

# -----------------------
# CONFIG
# -----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Note: In production, Overpass limits requests. 
# For a real app, you would want to cache these results in a database.
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# -----------------------
# ROUTES
# -----------------------

@app.route("/")
def index():
    # Looks for map_page.html in the same folder as this script
    return send_from_directory(BASE_DIR, "map_page.html")

@app.route("/nearby-hospitals", methods=["GET"])
def nearby_hospitals():
    """
    Proxy endpoint to fetch hospitals from Python.
    (The HTML above fetches directly from JS, but this exists if you want to switch logic to backend)
    """
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Latitude and longitude required"}), 400

    # Optimized Query: timeout added, search radius 5km
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="hospital"](around:5000,{lat},{lon});
      way["amenity"="hospital"](around:5000,{lat},{lon});
      relation["amenity"="hospital"](around:5000,{lat},{lon});
    );
    out center tags;
    """

    try:
        res = requests.post(OVERPASS_URL, data=query, timeout=30)
        res.raise_for_status() # Check for HTTP errors
        data = res.json()
    except Exception as e:
        return jsonify({"error": "Failed to fetch data", "details": str(e)}), 500

    hospitals = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        
        # Geometry fallback
        center_lat = el.get("lat") or el.get("center", {}).get("lat")
        center_lon = el.get("lon") or el.get("center", {}).get("lon")

        if center_lat and center_lon:
            hospitals.append({
                "id": el.get("id"),
                "name": tags.get("name", "Unnamed Facility"),
                "lat": center_lat,
                "lon": center_lon,
                "emergency": tags.get("emergency", "no"),
                "type": "hospital"
            })

    return jsonify({"count": len(hospitals), "results": hospitals})

# -----------------------
# ENTRY POINT
# -----------------------
if __name__ == "__main__":
    print("🚑 Server running at http://127.0.0.1:5050")
    app.run(
        host="127.0.0.1",
        port=5050,
        debug=True 
    )