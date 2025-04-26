import requests
import re
import json

def fetch_transcript(video_id):
    try:
        # Fetch the YouTube video page
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to fetch YouTube page.")

        # Extract the ytInitialPlayerResponse JSON
        initial_data_match = re.search(r'ytInitialPlayerResponse\s*=\s*(\{.+?\});', response.text)
        if not initial_data_match:
            raise Exception("Could not find player response JSON.")

        initial_data = json.loads(initial_data_match.group(1))

        # Find captions
        captions = initial_data.get('captions')
        if not captions:
            raise Exception("No captions available for this video.")

        caption_tracks = captions.get('playerCaptionsTracklistRenderer', {}).get('captionTracks')
        if not caption_tracks:
            raise Exception("No caption tracks found.")

        # Prefer English or first available
        transcript_url = None
        for track in caption_tracks:
            if 'languageCode' in track and track['languageCode'].startswith('en'):
                transcript_url = track.get('baseUrl')
                break
        if not transcript_url:
            transcript_url = caption_tracks[0].get('baseUrl')

        if not transcript_url:
            raise Exception("No transcript URL found.")

        # Download the transcript XML
        transcript_response = requests.get(transcript_url)
        if transcript_response.status_code != 200:
            raise Exception("Failed to fetch transcript file.")

        # Extract text lines
        text_lines = re.findall(r'>([^<]+)<', transcript_response.text)
        if not text_lines:
            raise Exception("Transcript data not found.")

        full_text = "\n".join(text_lines)
        return full_text

    except Exception as e:
        raise Exception(f"Error fetching transcript: {str(e)}")