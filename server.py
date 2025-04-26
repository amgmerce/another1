from flask import Flask, request, jsonify
from _transcripts import fetch_transcript

app = Flask(__name__)

@app.route('/transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('videoId')
    if not video_id:
        return jsonify({'error': 'Missing video ID'}), 400
    try:
        transcript = fetch_transcript(video_id)
        return jsonify({'transcript': transcript, 'video_id': video_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)