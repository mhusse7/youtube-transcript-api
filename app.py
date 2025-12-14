from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

@app.route('/transcript/<video_id>', methods=['GET'])
def get_transcript(video_id):
    try:
        # New API syntax for version 1.x
        ytt_api = YouTubeTranscriptApi()
        
        # Step 1: List transcripts
        transcript_list = ytt_api.list(video_id)
        
        # Step 2: Find English transcript and fetch directly
        fetched = None
        language = 'unknown'
        
        for t in transcript_list:
            try:
                lang_code = str(getattr(t, 'language_code', ''))
            except:
                lang_code = ''
            
            if lang_code.startswith('en'):
                # Fetch using the transcript's own fetch method
                fetched = t.fetch()
                language = lang_code
                break
        
        # If no English, use first available
        if not fetched:
            for t in transcript_list:
                try:
                    fetched = t.fetch()
                    language = str(getattr(t, 'language_code', 'unknown'))
                    break
                except:
                    continue
        
        if not fetched:
            return jsonify({'error': 'No transcript found', 'video_id': video_id}), 404
        
        # Step 3: Convert to text
        text_parts = []
        for entry in fetched:
            try:
                if hasattr(entry, 'text'):
                    text_parts.append(str(entry.text))
                elif isinstance(entry, dict) and 'text' in entry:
                    text_parts.append(str(entry['text']))
                else:
                    text_parts.append(str(entry))
            except:
                continue
        
        full_text = ' '.join(text_parts)
        
        return jsonify({
            'video_id': str(video_id),
            'text': str(full_text),
            'language': str(language)
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'video_id': str(video_id)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
