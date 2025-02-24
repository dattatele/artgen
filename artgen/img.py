import traceback
import requests
from duckduckgo_search import DDGS
from io import BytesIO
from PIL import Image

def fetch_image_object(query):
    """
    Dynamically fetch an image for the given query using DuckDuckGo search.
    Returns a PIL Image object loaded from an in-memory byte stream.
    """
    try:
        results = DDGS().images(
            keywords=query,
            region="wt-wt",
            safesearch="moderate",
            max_results=1
        )
        if results:
            image_url = results[0]["image"]
            # Mimic a browser with a User-Agent header to avoid 403 errors.
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/114.0.0.0 Safari/537.36"
                )
            }
            response = requests.get(image_url, headers=headers)
            response.raise_for_status()
            image_data = response.content
            image = Image.open(BytesIO(image_data))
            return image
    except Exception as e:
        print("Error fetching image:", e)
        traceback.print_exc()
    return None
