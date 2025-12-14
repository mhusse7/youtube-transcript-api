from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

@app.route('/transcript/<video_id>', methods=['GET'])
def get_transcript(video_id):
    try:
        # New API syntax for version 1.x
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'en-GB'])
        
        # Combine all text
        full_text = ' '.join([entry['text'] for entry in transcript])
        
        return jsonify({
            'video_id': video_id,
            'text': full_text,
            'language': 'en'
        })
        
    except Exception as e:
        error_message = str(e)
        
        # Try to get any available transcript
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for transcript in transcript_list:
                fetched = transcript.fetch()
                full_text = ' '.join([entry['text'] for entry in fetched])
                return jsonify({
                    'video_id': video_id,
                    'text': full_text,
                    'language': transcript.language_code
                })
        except:
            pass
        
        return jsonify({'error': error_message, 'video_id': video_id}), 404

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
