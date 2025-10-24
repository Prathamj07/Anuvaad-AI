from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import tempfile
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install it with: pip install python-dotenv")
import time
from video_processor import VideoProcessor
from elevenlabs_dubbing import ElevenLabsDubbing
from utils import format_time, validate_video_file
import speech_recognition as sr
from elevenlabs import ElevenLabs
from google import genai
from pydub import AudioSegment
from youtube_summarizer import YouTubeSummarizer
from story_generator import StoryGenerator
from article_to_podcast import ArticleToPodcast
import base64
from werkzeug.utils import secure_filename
import io
from models import db, bcrypt, User, UserHistory
from datetime import timedelta

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anuvaad_ai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

elevenlabs_api_key = os.environ.get('ELEVENLABS_API_KEY')
gemini_api_key = os.environ.get('GEMINI_API_KEY')

video_processor = VideoProcessor()
dubbing_service = ElevenLabsDubbing(api_key=elevenlabs_api_key) if elevenlabs_api_key else None
elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key) if elevenlabs_api_key else None
gemini_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None
youtube_summarizer = YouTubeSummarizer(gemini_api_key=gemini_api_key) if gemini_api_key else None
story_generator = StoryGenerator(gemini_api_key=gemini_api_key, elevenlabs_api_key=elevenlabs_api_key) if gemini_api_key and elevenlabs_api_key else None
article_podcast = ArticleToPodcast(gemini_api_key=gemini_api_key, elevenlabs_api_key=elevenlabs_api_key) if gemini_api_key and elevenlabs_api_key else None

dubbing_projects = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Backend is running'})

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not name or not email or not password:
            return jsonify({'error': 'Name, email, and password are required'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(name=name, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET', 'POST'])
@jwt_required()
def user_history():
    try:
        user_id = int(get_jwt_identity())
        
        if request.method == 'POST':
            data = request.json
            feature_type = data.get('feature_type')
            feature_data = data.get('feature_data')
            
            history_entry = UserHistory(
                user_id=user_id,
                feature_type=feature_type,
                feature_data=feature_data
            )
            
            db.session.add(history_entry)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'History saved',
                'history': history_entry.to_dict()
            }), 201
        
        else:
            history = UserHistory.query.filter_by(user_id=user_id).order_by(UserHistory.created_at.desc()).limit(50).all()
            
            return jsonify({
                'success': True,
                'history': [h.to_dict() for h in history]
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text')
        voice = data.get('voice', 'Rachel')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        voice_map = {
            "Rachel": "21m00Tcm4TlvDq8ikWAM",
            "Adam": "pNInz6obpgDQGcFmaJgB",
            "Antoni": "ErXwobaYiN019PkySvjV",
            "Arnold": "VR6AewLTigWG4xSOukaG",
            "Bella": "EXAVITQu4vr4xnSDxMaL",
            "Domi": "AZnzlk1XvdvUeBnXmlld",
            "Elli": "MF3mGyEYCl7XYWbV9V6O",
            "Josh": "TxGEqnHWrfWFTfGW9XjX",
            "Sam": "yoZ06aMxZJJ28mfd3POQ"
        }
        
        audio_generator = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=voice_map.get(voice, voice_map['Rachel']),
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        audio_bytes = b''.join(audio_generator)
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return jsonify({
            'success': True,
            'audio': audio_base64,
            'filename': f'tts_{int(time.time())}.mp3'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Audio file is required'}), 400
        
        audio_file = request.files['audio']
        file_extension = audio_file.filename.split('.')[-1].lower()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_input:
            audio_file.save(tmp_input.name)
            input_path = tmp_input.name
        
        wav_path = tempfile.mktemp(suffix='.wav')
        
        try:
            audio = AudioSegment.from_file(input_path, format=file_extension)
            audio.export(wav_path, format='wav')
        except Exception as e:
            os.unlink(input_path)
            return jsonify({'error': f'Failed to convert audio: {str(e)}'}), 500
        
        recognizer = sr.Recognizer()
        
        try:
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
        finally:
            os.unlink(input_path)
            if os.path.exists(wav_path):
                os.unlink(wav_path)
        
        return jsonify({
            'success': True,
            'text': text
        })
    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand audio'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/text-translation', methods=['POST'])
def text_translation():
    try:
        data = request.json
        text = data.get('text')
        from_lang = data.get('from_lang')
        to_lang = data.get('to_lang')
        
        if not text or not from_lang or not to_lang:
            return jsonify({'error': 'Text, from_lang, and to_lang are required'}), 400
        
        if from_lang == to_lang:
            return jsonify({'error': 'Source and target languages must be different'}), 400
        
        prompt = f"Translate the following text from {from_lang} to {to_lang}. Only provide the translation, no explanations:\n\n{text}"
        
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        translated_text = response.text
        
        return jsonify({
            'success': True,
            'translated_text': translated_text,
            'from_lang': from_lang,
            'to_lang': to_lang
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/youtube-summary', methods=['POST'])
def youtube_summary():
    try:
        data = request.json
        youtube_url = data.get('url')
        word_count = data.get('word_count', 200)
        
        if not youtube_url:
            return jsonify({'error': 'YouTube URL is required'}), 400
        
        result = youtube_summarizer.process_youtube_video(youtube_url, word_count)
        
        if result:
            return jsonify({
                'success': True,
                'title': result['title'],
                'summary': result['summary']
            })
        else:
            return jsonify({'error': 'Failed to process video'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/word-to-story', methods=['POST'])
def word_to_story():
    try:
        data = request.json
        words = data.get('words')
        theme = data.get('theme')
        word_count = data.get('word_count', 300)
        language = data.get('language', 'english')
        
        if not words or not theme:
            return jsonify({'error': 'Words and theme are required'}), 400
        
        words_list = [word.strip() for word in words.split(',')]
        
        result = story_generator.create_story_with_audio(
            words=words_list,
            theme=theme,
            word_count=word_count,
            language=language.lower()
        )
        
        if result and result['story']:
            response_data = {
                'success': True,
                'story': result['story']
            }
            
            if result['audio_bytes']:
                audio_base64 = base64.b64encode(result['audio_bytes']).decode('utf-8')
                response_data['audio'] = audio_base64
                response_data['filename'] = f'story_{int(time.time())}.mp3'
            
            return jsonify(response_data)
        else:
            return jsonify({'error': 'Failed to generate story'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/article-to-podcast', methods=['POST'])
def article_to_podcast():
    try:
        data = request.json
        article_text = data.get('article_text')
        script_word_count = data.get('script_word_count', 300)
        
        if not article_text:
            return jsonify({'error': 'Article text is required'}), 400
        
        audio_bytes = article_podcast.create_podcast_from_article(
            article_text=article_text,
            script_word_count=script_word_count,
            progress_callback=None
        )
        
        if audio_bytes:
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            return jsonify({
                'success': True,
                'audio': audio_base64,
                'filename': f'podcast_{int(time.time())}.mp3'
            })
        else:
            return jsonify({'error': 'Failed to generate podcast'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/video-dubbing/start', methods=['POST'])
def start_video_dubbing():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'Video file is required'}), 400
        
        video_file = request.files['video']
        source_lang = request.form.get('source_lang', 'en')
        target_lang = request.form.get('target_lang', 'hi')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            video_file.save(tmp_file.name)
            input_video_path = tmp_file.name
        
        dubbing_id = dubbing_service.create_dubbing_project(
            video_path=input_video_path,
            source_lang=source_lang,
            target_lang=target_lang,
            project_name=f"Dubbing_{int(time.time())}"
        )
        
        if dubbing_id:
            dubbing_projects[dubbing_id] = {
                'source_lang': source_lang,
                'target_lang': target_lang,
                'status': 'processing'
            }
            
            return jsonify({
                'success': True,
                'dubbing_id': dubbing_id
            })
        else:
            os.unlink(input_video_path)
            return jsonify({'error': 'Failed to start dubbing'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/video-dubbing/status/<dubbing_id>', methods=['GET'])
def get_dubbing_status(dubbing_id):
    try:
        status_result = dubbing_service.get_dubbing_status(dubbing_id)
        
        return jsonify({
            'success': True,
            'status': status_result['status'],
            'dubbing_id': dubbing_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/video-dubbing/download/<dubbing_id>', methods=['GET'])
def download_dubbed_video(dubbing_id):
    try:
        target_lang = request.args.get('target_lang', 'hi')
        
        dubbed_video_path = dubbing_service.download_dubbed_video(dubbing_id, target_lang)
        
        if dubbed_video_path and os.path.exists(dubbed_video_path):
            return send_file(
                dubbed_video_path,
                as_attachment=True,
                download_name=f'dubbed_video_{int(time.time())}.mp4',
                mimetype='video/mp4'
            )
        else:
            return jsonify({'error': 'Failed to download dubbed video'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/attached_assets/<path:filename>')
def serve_attached_assets(filename):
    try:
        return send_file(os.path.join('attached_assets', filename))
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
