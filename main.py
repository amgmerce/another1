from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import requests
import srt

app = FastAPI()

# CORS (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

@app.get("/api/transcript/{video_id}")
def get_transcript(video_id: str):
    try:
        # Step 1: Get list of captions
        captions_url = f"https://www.googleapis.com/youtube/v3/captions?videoId={video_id}&part=snippet&key={YOUTUBE_API_KEY}"
        captions_response = requests.get(captions_url)
        
        if captions_response.status_code != 200:
            return JSONResponse(status_code=400, content={"success": False, "error": "Failed to get caption metadata."})
        
        captions_data = captions_response.json()
        items = captions_data.get("items", [])
        if not items:
            return JSONResponse(status_code=404, content={"success": False, "error": "No captions found for this video."})
        
        caption_id = items[0]['id']

        # Step 2: Download the actual captions
        download_url = f"https://www.googleapis.com/youtube/v3/captions/{caption_id}?tfmt=srt&key={YOUTUBE_API_KEY}"
        download_response = requests.get(download_url)

        if download_response.status_code != 200:
            return JSONResponse(status_code=400, content={"success": False, "error": "Failed to download captions."})

        srt_data = download_response.text

        # Step 3: Parse the SRT
        parsed_subs = list(srt.parse(srt_data))

        transcript = []
        for sub in parsed_subs:
            transcript.append({
                "start": sub.start.total_seconds(),
                "end
