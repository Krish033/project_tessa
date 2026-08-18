import httpx
import urllib.parse
from typing import Dict, Any, List, Optional


async def geocode(address: str) -> Dict[str, Any]:
    """Convert location address or place name into latitude and longitude coordinates.
    
    Args:
        address: Location address or place name (e.g. 'Eiffel Tower, Paris').
    """
    if not address or not address.strip():
        return {"error": "Address is required."}

    encoded = urllib.parse.quote(address.strip())
    url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=1"
    headers = {"User-Agent": "TessaAI/1.0"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()

        data = resp.json()
        if not data:
            return {"error": f"No coordinates found for address '{address}'."}

        first = data[0]
        return {
            "address": address,
            "display_name": first.get("display_name"),
            "latitude": float(first.get("lat")),
            "longitude": float(first.get("lon"))
        }
    except Exception as e:
        return {"error": f"Geocoding failed: {str(e)}"}


async def reverse_geocode(latitude: float, longitude: float) -> Dict[str, Any]:
    """Convert latitude and longitude coordinates into a human-readable address.
    
    Args:
        latitude: Geographic latitude coordinate.
        longitude: Geographic longitude coordinate.
    """
    url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"
    headers = {"User-Agent": "TessaAI/1.0"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()

        data = resp.json()
        return {
            "latitude": latitude,
            "longitude": longitude,
            "display_name": data.get("display_name", ""),
            "address_details": data.get("address", {})
        }
    except Exception as e:
        return {"error": f"Reverse geocoding failed: {str(e)}"}


async def maps_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search map places, addresses, and points of interest.
    
    Args:
        query: Location or place search query.
        max_results: Maximum results to return (default: 5).
    """
    if not query or not query.strip():
        return []

    encoded = urllib.parse.quote(query.strip())
    url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit={max_results}"
    headers = {"User-Agent": "TessaAI/1.0"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()

        results = []
        for item in resp.json():
            results.append({
                "display_name": item.get("display_name"),
                "latitude": float(item.get("lat")),
                "longitude": float(item.get("lon")),
                "type": item.get("type"),
                "class": item.get("class")
            })

        return results
    except Exception as e:
        return [{"error": f"Maps search failed: {str(e)}"}]


async def directions(origin: str, destination: str, mode: str = "driving") -> Dict[str, Any]:
    """Calculate routing directions between origin and destination.
    
    Args:
        origin: Origin address or coordinate.
        destination: Destination address or coordinate.
        mode: Travel mode ('driving', 'walking', 'biking').
    """
    orig_geo = await geocode(origin)
    if "error" in orig_geo:
        return orig_geo

    dest_geo = await geocode(destination)
    if "error" in dest_geo:
        return dest_geo

    lon1, lat1 = orig_geo["longitude"], orig_geo["latitude"]
    lon2, lat2 = dest_geo["longitude"], dest_geo["latitude"]

    # Use OSRM public API for driving route calculation
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(osrm_url)
            resp.raise_for_status()

        data = resp.json()
        routes = data.get("routes", [])
        if routes:
            route = routes[0]
            distance_km = round(route.get("distance", 0) / 1000.0, 2)
            duration_min = round(route.get("duration", 0) / 60.0, 1)
            return {
                "origin": orig_geo["display_name"],
                "destination": dest_geo["display_name"],
                "distance_km": distance_km,
                "duration_minutes": duration_min,
                "mode": mode
            }
    except Exception:
        pass

    return {
        "origin": orig_geo["display_name"],
        "destination": dest_geo["display_name"],
        "origin_coords": {"lat": lat1, "lon": lon1},
        "destination_coords": {"lat": lat2, "lon": lon2},
        "mode": mode
    }


async def nearby_places(location: str, amenity: str = "restaurant", radius_km: float = 2.0) -> List[Dict[str, Any]]:
    """Find nearby places of interest (amenities, restaurants, fuel, etc.).
    
    Args:
        location: Target center location address.
        amenity: Amenity type ('restaurant', 'fuel', 'hospital', 'cafe', 'bank').
        radius_km: Search radius in kilometers (default: 2.0).
    """
    geo = await geocode(location)
    if "error" in geo:
        return [geo]

    lat, lon = geo["latitude"], geo["longitude"]
    search_q = f"{amenity} near {geo['display_name']}"
    return await maps_search(search_q, max_results=5)
