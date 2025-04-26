from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from fastapi.responses import JSONResponse

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# YouTube API key inserted directly
YOUTUBE_API_KEY = "AIzaSyBYOYmj8-Urp_19ofjXCErvBB2NkEcKAwY"

@app.get("/api/transcript/{video_id}")
def get_transcript(video_id: str):
    try:
        captions_url = (
            f"https://www.googleapis.com/youtube/v3/captions?videoId={video_id}&key={YOUTUBE_API_KEY}&part=snippet"
        )
        captions_response = requests.get(captions_url)

        if captions_response.status_code != 200:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": f"Failed to fetch captions. Status code: {captions_response.status_code}"}
            )

        captions_data = captions_response.json()
        return {"success": True, "captions": captions_data}

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )

@app.get("/")
def root():
    return {"message": "YouTube Transcript Scraper API is running."}
