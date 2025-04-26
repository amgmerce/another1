from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import os
import srt

app = FastAPI()

# CORS (for frontend like Bolt app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your YouTube API Key
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

        # Get the first caption track ID
        caption_id = items[0]['id']

        # Step 2: Download the actual captions in SRT format
        download_url = f"https://www.googleapis.com/youtube/v3/captions/{caption_id}?tfmt=srt&key={YOUTUBE_API_KEY}"
        download_response = requests.get(download_url)

        if download_response.status_code != 200:
            return JSONResponse(status_code=400, content={"success": False, "error": "Failed to download captions."})

        # Step 3: Parse the SRT into text + timestamps
        subtitles = list(srt.parse(download_response.text))
        transcript = [
            {
                "text": sub.content,
                "start": sub.start.total_seconds(),
                "end": sub.end.total_seconds()
            }
            for sub in subtitles
        ]

        return {"success": True, "transcript": transcript}

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/")
def root():
    return {"message": "YouTube Transcript Scraper API is running."}
