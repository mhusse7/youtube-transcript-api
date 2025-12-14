from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

@app.route('/transcript/<video_id>', methods=['GET'])
def get_transcript(video_id):
    try:
        # New API syntax for version 1.x
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        # Try to find English transcript
        transcript = None
        for t in transcript_list:
            if t.language_code.startswith('en'):
                transcript = t
                break
        
        # If no English, use first available
        if not transcript:
            for t in transcript_list:
                transcript = t
                break
        
        if not transcript:
            return jsonify({'error': 'No transcript found', 'video_id': video_id}), 404
        
        # Fetch the transcript
        fetched = ytt_api.fetch(transcript)
        
        # Convert to plain text - handle the new object format
        text_parts = []
        for entry in fetched:
            # Try different ways to get text
            if hasattr(entry, 'text'):
                text_parts.append(str(entry.text))
            elif isinstance(entry, dict) and 'text' in entry:
                text_parts.append(entry['text'])
            else:
                text_parts.append(str(entry))
        
        full_text = ' '.join(text_parts)
        
        return jsonify({
            'video_id': video_id,
            'text': full_text,
            'language': transcript.language_code
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'video_id': video_id}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
