from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from fastapi.responses import JSONResponse

app = FastAPI()

# Allow all CORS (for Bolt frontend convenience)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your actual YouTube API Key (directly inserted, per your request)
YOUTUBE_API_KEY = "AIzaSyBYOYmj8-Urp_19ofjXCErvBB2NkEcKAwY"

@app.get("/api/transcript/{video_id}")
def get_transcript(video_id: str):
    try:
        # Step 1: Fetch caption list from YouTube API
        captions_list_url = f"https://www.googleapis.com/youtube/v3/captions?videoId={video_id}&part=snippet&key={YOUTUBE_API_KEY}"
        captions_list_response = requests.get(captions_list_url)

        if captions_list_response.status_code != 200:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Failed to fetch captions list."}
            )

        captions_list_data = captions_list_response.json()
        items = captions_list_data.get("items", [])

        if not items:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "No captions available for this video."}
            )

        # Pick the first English caption track available
        caption_id = None
        for item in items:
            snippet = item.get("snippet", {})
            if snippet.get("language") == "en":
                caption_id = item.get("id")
                break

        if not caption_id:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "No English captions found for this video."}
            )

        # Step 2: Download captions (JSON format with timestamps)
        caption_download_url = f"https://www.googleapis.com/youtube/v3/captions/{caption_id}?key={YOUTUBE_API_KEY}&tfmt=srv3"
        caption_response = requests.get(caption_download_url)

        if caption_response.status_code != 200:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Failed to download captions."}
            )

        captions_json = caption_response.json()

        return {"success": True, "transcript": captions_json}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/")
def root():
    return {"message": "YouTube Transcript API is running with JSON timestamps."}
