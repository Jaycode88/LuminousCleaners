from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
import requests

def _fetch_google_reviews():
    api_key = settings.GOOGLE_PLACES_API_KEY
    place_id = settings.GOOGLE_PLACE_ID
    if not api_key or not place_id:
        return {"error": "Missing Google Places API configuration.", "reviews": []}

    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": api_key,
        "fields": "name,rating,user_ratings_total,reviews,url"
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "OK":
            return {"error": data.get("error_message") or data.get("status"), "reviews": []}

        result = data.get("result", {})
        reviews = result.get("reviews", []) or []  # Google returns up to 5
        normalized = [{
            "author_name": r.get("author_name"),
            "rating": r.get("rating"),
            "text": r.get("text"),
            "relative_time": r.get("relative_time_description"),
            "profile_photo_url": r.get("profile_photo_url"),
        } for r in reviews]

        return {
            "error": None,
            "business_name": result.get("name", ""),
            "business_url": result.get("url", ""),
            "rating": result.get("rating", 0),
            "total": result.get("user_ratings_total", 0),
            "reviews": normalized,
        }
    except requests.RequestException as e:
        return {"error": str(e), "reviews": []}

def reviews_section(request):
    cache_key = "google_reviews_v1"
    payload = cache.get(cache_key)
    if not payload:
        payload = _fetch_google_reviews()
        ttl = settings.GOOGLE_REVIEWS_CACHE_SECONDS if not payload.get("error") else 60
        cache.set(cache_key, payload, ttl)

    return render(request, "reviews/reviews_section.html", payload)
