from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

@app.route('/transcript/<video_id>', methods=['GET'])
def get_transcript(video_id):
    try:
        # New API syntax for version 1.x
        ytt_api = YouTubeTranscriptApi()
        
        # Step 1: List transcripts
        try:
            transcript_list = ytt_api.list(video_id)
        except Exception as e:
            return jsonify({'error': f'List error: {str(e)}', 'video_id': video_id}), 500
        
        # Step 2: Find English transcript
        selected_transcript = None
        language = 'unknown'
        
        try:
            for t in transcript_list:
                try:
                    lang_code = str(getattr(t, 'language_code', ''))
                except:
                    lang_code = ''
                if lang_code.startswith('en'):
                    selected_transcript = t
                    language = lang_code
                    break
            
            # If no English, use first available
            if not selected_transcript:
                for t in transcript_list:
                    selected_transcript = t
                    try:
                        language = str(getattr(t, 'language_code', 'unknown'))
                    except:
                        language = 'unknown'
                    break
        except Exception as e:
            return jsonify({'error': f'Select error: {str(e)}', 'video_id': video_id}), 500
        
        if not selected_transcript:
            return jsonify({'error': 'No transcript found', 'video_id': video_id}), 404
        
        # Step 3: Fetch transcript
        try:
            fetched = ytt_api.fetch(selected_transcript)
        except Exception as e:
            return jsonify({'error': f'Fetch error: {str(e)}', 'video_id': video_id}), 500
        
        # Step 4: Convert to text
        try:
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
        except Exception as e:
            return jsonify({'error': f'Text error: {str(e)}', 'video_id': video_id}), 500
        
        # Step 5: Return result
        return jsonify({
            'video_id': str(video_id),
            'text': str(full_text),
            'language': str(language)
        })
        
    except Exception as e:
        return jsonify({'error': f'General error: {str(e)}', 'video_id': str(video_id)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
