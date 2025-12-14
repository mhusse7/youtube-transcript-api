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
        selected_transcript = None
        language = 'unknown'
        
        for t in transcript_list:
            lang_code = str(t.language_code) if hasattr(t, 'language_code') else ''
            if lang_code.startswith('en'):
                selected_transcript = t
                language = lang_code
                break
        
        # If no English, use first available
        if not selected_transcript:
            for t in transcript_list:
                selected_transcript = t
                language = str(t.language_code) if hasattr(t, 'language_code') else 'unknown'
                break
        
        if not selected_transcript:
            return jsonify({'error': 'No transcript found', 'video_id': video_id}), 404
        
        # Fetch the transcript
        fetched = ytt_api.fetch(selected_transcript)
        
        # Convert to plain text
        text_parts = []
        for entry in fetched:
            if hasattr(entry, 'text'):
                text_parts.append(str(entry.text))
            elif isinstance(entry, dict) and 'text' in entry:
                text_parts.append(str(entry['text']))
            else:
                text_parts.append(str(entry))
        
        full_text = ' '.join(text_parts)
        
        return jsonify({
            'video_id': video_id,
            'text': full_text,
            'language': language
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'video_id': video_id}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
