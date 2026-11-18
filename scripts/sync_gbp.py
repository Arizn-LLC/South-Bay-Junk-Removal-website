"""Refresh the public reviews and post from the owner's Google Business Profile."""
import json
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def read(request):
    with urlopen(request, timeout=30) as response:
        return json.load(response)

def entries(location, resource, key, token):
    params = {}
    while True:
        url = f"https://mybusiness.googleapis.com/v4/{location}/{resource}?" + urlencode(params)
        page = read(Request(url, headers={"Authorization": "Bearer " + token}))
        yield from page.get(key, [])
        if not page.get("nextPageToken"):
            break
        params["pageToken"] = page["nextPageToken"]

def created(item):
    return datetime.fromisoformat(item["createTime"].replace("Z", "+00:00"))

def main():
    location = os.environ["GBP_LOCATION"]
    if not re.fullmatch(r"accounts/\d+/locations/\d+", location):
        raise ValueError("Expected accounts/ACCOUNT_ID/locations/LOCATION_ID")
    auth = {"grant_type": "refresh_token"}
    for key in ("client_id", "client_secret", "refresh_token"):
        auth[key] = os.environ["GBP_" + key.upper()]
    token = read(Request("https://oauth2.googleapis.com/token", data=urlencode(auth).encode()))["access_token"]
    reviews = sorted((r for r in entries(location, "reviews", "reviews", token)
                      if r.get("starRating") == "FIVE"), key=created, reverse=True)[:10]
    post = max((p for p in entries(location, "localPosts", "localPosts", token)
                if p.get("state") == "LIVE"), key=created, default=None)
    feed = {"reviews": [{"name": r.get("reviewer", {}).get("displayName") or "Google user",
                         "date": r["createTime"], "text": r.get("comment", ""),
                         "photo": r.get("reviewer", {}).get("profilePhotoUrl", "")} for r in reviews],
            "post": {"text": post.get("summary", ""), "url": post.get("searchUrl", ""),
                     "image": next((m.get("googleUrl") or m.get("sourceUrl") for m in post.get("media", [])
                                    if m.get("mediaFormat") == "PHOTO"), None)} if post else None}
    target = Path("gbp-feed.json")
    temp = target.with_suffix(".tmp")
    temp.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n")
    temp.replace(target)

if __name__ == "__main__":
    main()
