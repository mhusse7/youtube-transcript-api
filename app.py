from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

app = Flask(__name__)

@app.route('/transcript/<video_id>', methods=['GET'])
def get_transcript(video_id):
    try:
        # Try to get English transcript first
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        transcript = None
        
        # Try manual English first
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except:
            pass
        
        # Try auto-generated English
        if not transcript:
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
            except:
                pass
        
        # Fall back to any available transcript
        if not transcript:
            try:
                transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
            except:
                # Get first available
                for t in transcript_list:
                    transcript = t
                    break
        
        if not transcript:
            return jsonify({'error': 'No transcript found', 'video_id': video_id}), 404
        
        # Fetch the transcript
        transcript_data = transcript.fetch()
        
        # Combine all text
        full_text = ' '.join([entry['text'] for entry in transcript_data])
        
        return jsonify({
            'video_id': video_id,
            'text': full_text,
            'language': transcript.language_code
        })
        
    except TranscriptsDisabled:
        return jsonify({'error': 'Transcripts disabled', 'video_id': video_id}), 404
    except NoTranscriptFound:
        return jsonify({'error': 'No transcript found', 'video_id': video_id}), 404
    except Exception as e:
        return jsonify({'error': str(e), 'video_id': video_id}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
