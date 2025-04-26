from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from fastapi.responses import JSONResponse

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # <- we will load your API key as an ENV variable

@app.get("/api/transcript/{video_id}")
def get_transcript(video_id: str):
    try:
        captions_url = f"https://www.googleapis.com/youtube/v3/captions?videoId={video_id}&part=snippet&key={YOUTUBE_API_KEY}"
        captions_response = requests.get(captions_url)

        if captions_response.status_code != 200:
            return JSONResponse(status_code=400, content={"success": False, "error": "Failed to fetch captions info."})

        captions_data = captions_response.json()
        items = captions_data.get("items", [])

        if not items:
            return JSONResponse(status_code=404, content={"success": False, "error": "No captions found."})

        caption_id = items[0]["id"]

        caption_download_url = f"https://www.googleapis.com/youtube/v3/captions/{caption_id}?tfmt=sbv&key={YOUTUBE_API_KEY}"
        caption_response = requests.get(caption_download_url)

        if caption_response.status_code != 200:
            return JSONResponse(status_code=400, content={"success": False, "error": "Failed to download caption text."})

        return {"success": True, "transcript": caption_response.text}

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/")
def root():
    return {"message": "YouTube API Transcript Server is running."}
