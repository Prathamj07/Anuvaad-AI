import streamlit as st
import tempfile
import os
from pathlib import Path
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

st.set_page_config(
    page_title="Anuvaad AI - Professional Video Dubbing",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    [data-testid="stHeader"] {
        display: none !important;
    }
    
    [data-testid="stToolbar"] {
        display: none !important;
    }
    
    html, body, [data-testid="stAppViewContainer"], .main {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: #0f172a;
    }
    
    .main {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .block-container {
        padding: 0 2rem !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    
    section[data-testid="stVerticalBlock"] > div {
        padding: 0 !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 5px solid !important;
        border-image: linear-gradient(135deg, #60a5fa, #a78bfa, #ec4899) 1 !important;
        border-radius: 24px !important;
        padding: 2.5rem !important;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95)) !important;
        box-shadow: 
            0 0 80px rgba(96, 165, 250, 0.9),
            0 0 150px rgba(167, 139, 250, 0.7),
            0 25px 80px rgba(0, 0, 0, 0.8),
            inset 0 0 60px rgba(96, 165, 250, 0.15) !important;
        position: relative !important;
        outline: 5px solid transparent !important;
        outline-offset: -5px !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]::before {
        content: '' !important;
        position: absolute !important;
        inset: -5px !important;
        border-radius: 24px !important;
        padding: 5px !important;
        background: linear-gradient(135deg, #60a5fa, #a78bfa, #ec4899) !important;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0) !important;
        -webkit-mask-composite: xor !important;
        mask-composite: exclude !important;
        pointer-events: none !important;
    }
    
    .header {
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(10px);
        padding: 1.5rem 4rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0;
    }
    
    .logo {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }
    
    .hero {
        text-align: center;
        padding: 5rem 2rem 3rem 2rem;
        background: rgba(96, 165, 250, 0.05);
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        margin: 0;
    }
    
    .hero h1 {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        line-height: 1.2;
    }
    
    .hero p {
        font-size: 1.5rem;
        color: #cbd5e1;
        font-weight: 300;
        max-width: 800px;
        margin: 0 auto 2rem auto;
    }
    
    .badge {
        display: inline-block;
        background: rgba(96, 165, 250, 0.2);
        color: #60a5fa;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid rgba(96, 165, 250, 0.3);
    }
    
    .content-section {
        padding: 3rem 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    @media (max-width: 768px) {
        .content-section {
            padding: 2rem 1rem;
        }
        
        .header {
            padding: 1.5rem 2rem;
        }
        
        .block-container {
            padding: 0 1rem !important;
        }
    }
    
    .card {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2.5rem;
        border: 1px solid rgba(148, 163, 184, 0.1);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
    }
    
    .feature-button-wrapper {
        margin-top: auto;
        padding-top: 1rem;
        display: flex;
        justify-content: center;
    }
    
    .feature-button-wrapper .stButton {
        width: 100%;
        max-width: 400px;
    }
    
    .feature-column {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    .feature-content-wrapper {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%) !important;
        border: 3px solid #60a5fa !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2), 0 0 0 3px #60a5fa !important;
        transition: all 0.3s ease;
        min-height: 450px !important;
        display: flex !important;
        flex-direction: column !important;
        outline: 3px solid #60a5fa !important;
        outline-offset: -3px !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #93c5fd !important;
        outline-color: #93c5fd !important;
        box-shadow: 0 12px 40px rgba(59, 130, 246, 0.3), 0 0 0 3px #93c5fd !important;
        transform: translateY(-2px);
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        display: flex !important;
        flex-direction: column !important;
        height: 100% !important;
    }
    
    [data-testid="stTooltipIcon"] {
        color: #60a5fa !important;
        opacity: 1 !important;
    }
    
    [data-testid="stTooltipIcon"] svg {
        fill: #60a5fa !important;
        width: 18px !important;
        height: 18px !important;
    }
    
    .stButton {
        display: flex;
        justify-content: center;
        margin-top: auto !important;
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-box {
        background: rgba(96, 165, 250, 0.1);
        border: 1px solid rgba(96, 165, 250, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .feature-box:hover {
        background: rgba(96, 165, 250, 0.15);
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(96, 165, 250, 0.2);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-size: 0.9rem;
        color: #94a3b8;
        line-height: 1.5;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        display: block;
        margin-bottom: 0.3rem;
    }
    
    .stat-label {
        font-size: 0.85rem;
        opacity: 0.9;
        font-weight: 500;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(59, 130, 246, 0.6);
    }
    
    .stSelectbox label {
        font-weight: 700 !important;
        color: #ffffff !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.8rem !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .stSelectbox > div > div {
        background: rgba(30, 41, 59, 0.95) !important;
        border: 2px solid rgba(96, 165, 250, 0.5) !important;
        color: #ffffff !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background: rgba(30, 41, 59, 0.95) !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(30, 41, 59, 0.95) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }
    
    .stSelectbox svg {
        fill: #60a5fa !important;
        width: 24px !important;
        height: 24px !important;
    }
    
    .stSelectbox [aria-expanded="true"] svg {
        fill: #a78bfa !important;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
    }
    
    .upload-zone {
        border: 2px dashed rgba(96, 165, 250, 0.4);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: rgba(96, 165, 250, 0.05);
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        border-color: rgba(96, 165, 250, 0.6);
        background: rgba(96, 165, 250, 0.1);
    }
    
    .info-box {
        background: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: #cbd5e1;
        margin: 1rem 0;
    }
    
    .success-box {
        background: rgba(34, 197, 94, 0.1);
        border-left: 4px solid #22c55e;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: #86efac;
        margin: 1rem 0;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        border-top: 1px solid rgba(148, 163, 184, 0.1);
        margin-top: 3rem;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #f1f5f9 !important;
    }
    
    h5 {
        color: #e0e7ff !important;
        font-weight: 700 !important;
        margin-bottom: 0.8rem !important;
    }
    
    p {
        color: #cbd5e1;
    }
    
    .stVideo {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

def render_text_to_speech(elevenlabs_client):
    st.markdown("### 🗣️ Text to Speech")
    
    text_input = st.text_area(
        "Enter text to convert to speech",
        placeholder="Type or paste your text here...",
        height=150,
        key="tts_input"
    )
    
    voice_id = st.selectbox(
        "Select Voice",
        ["Rachel", "Adam", "Antoni", "Arnold", "Bella", "Domi", "Elli", "Josh", "Sam"],
        key="tts_voice"
    )
    
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
    
    if st.button("🎵 Generate Speech", key="tts_btn", use_container_width=True):
        if not text_input.strip():
            st.error("Please enter some text first")
        else:
            try:
                with st.spinner("Generating speech..."):
                    audio_generator = elevenlabs_client.text_to_speech.convert(
                        text=text_input,
                        voice_id=voice_map[voice_id],
                        model_id="eleven_multilingual_v2",
                        output_format="mp3_44100_128"
                    )
                    
                    audio_bytes = b''.join(audio_generator)
                    
                    st.audio(audio_bytes, format='audio/mpeg')
                    
                    st.download_button(
                        label="📥 Download Audio",
                        data=audio_bytes,
                        file_name=f"tts_{int(time.time())}.mp3",
                        mime="audio/mpeg",
                        key="tts_download"
                    )
                    
                    st.success("✅ Speech generated successfully!")
            except Exception as e:
                st.error(f"❌ Failed to generate speech: {str(e)}")

def render_speech_to_text():
    st.markdown("### 🎤 Speech to Text")
    
    uploaded_audio = st.file_uploader(
        "Upload audio file",
        type=['wav', 'mp3', 'ogg', 'flac', 'm4a'],
        key="stt_upload"
    )
    
    if uploaded_audio:
        st.audio(uploaded_audio)
    else:
        st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
    
    if st.button("📝 Transcribe", key="stt_btn", use_container_width=True, disabled=uploaded_audio is None):
        if uploaded_audio:
            try:
                with st.spinner("Transcribing audio..."):
                    file_extension = uploaded_audio.name.split('.')[-1].lower()
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_input:
                        tmp_input.write(uploaded_audio.read())
                        input_path = tmp_input.name
                    
                    wav_path = tempfile.mktemp(suffix='.wav')
                    
                    try:
                        audio = AudioSegment.from_file(input_path, format=file_extension)
                        audio.export(wav_path, format='wav')
                    except Exception as e:
                        os.unlink(input_path)
                        raise Exception(f"Failed to convert audio: {str(e)}")
                    
                    recognizer = sr.Recognizer()
                    
                    try:
                        with sr.AudioFile(wav_path) as source:
                            audio_data = recognizer.record(source)
                            text = recognizer.recognize_google(audio_data)
                    finally:
                        os.unlink(input_path)
                        if os.path.exists(wav_path):
                            os.unlink(wav_path)
                    
                    st.markdown("##### 📄 Transcription:")
                    st.text_area("Result", value=text, height=150, key="stt_result")
                    
                    st.success("✅ Transcription completed!")
            except sr.UnknownValueError:
                st.error("❌ Could not understand audio. Please try with clearer audio.")
            except Exception as e:
                st.error(f"❌ Transcription failed: {str(e)}")

def render_text_translation(gemini_client):
    st.markdown("### 🌐 Text Translation")
    
    source_text = st.text_area(
        "Enter text to translate",
        placeholder="Type or paste text here...",
        height=120,
        key="trans_input"
    )
    
    trans_col1, trans_col2 = st.columns(2)
    
    with trans_col1:
        from_lang = st.selectbox(
            "From",
            ["English", "Hindi", "Spanish", "French", "German", "Italian", "Portuguese", "Japanese", "Korean", "Chinese"],
            key="trans_from"
        )
    
    with trans_col2:
        to_lang = st.selectbox(
            "To",
            ["Hindi", "English", "Spanish", "French", "German", "Italian", "Portuguese", "Japanese", "Korean", "Chinese"],
            key="trans_to"
        )
    
    if st.button("🔄 Translate", key="trans_btn", use_container_width=True):
        if not source_text.strip():
            st.error("Please enter some text to translate")
        elif from_lang == to_lang:
            st.error("Source and target languages must be different")
        else:
            try:
                with st.spinner("Translating..."):
                    prompt = f"Translate the following text from {from_lang} to {to_lang}. Only provide the translation, no explanations:\n\n{source_text}"
                    
                    response = gemini_client.models.generate_content(
                        model="gemini-2.0-flash-exp",
                        contents=prompt
                    )
                    translated_text = response.text
                    
                    st.markdown("##### 📝 Translation:")
                    st.text_area("Result", value=translated_text, height=120, key="trans_result")
                    
                    st.success(f"✅ Translated from {from_lang} to {to_lang}")
            except Exception as e:
                st.error(f"❌ Translation failed: {str(e)}")

def render_youtube_summarizer(youtube_summarizer):
    youtube_url = st.text_input(
        "Enter YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        key="youtube_url"
    )
    
    word_count = st.slider(
        "Summary word count",
        min_value=50,
        max_value=500,
        value=200,
        step=50,
        key="summary_words"
    )
    
    st.markdown('<div class="feature-button-wrapper">', unsafe_allow_html=True)
    if st.button("📝 Summarize Video", key="youtube_btn", use_container_width=True):
        if not youtube_url.strip():
            st.error("Please enter a YouTube URL")
        else:
            try:
                with st.spinner("Processing... This may take a few minutes"):
                    status = st.empty()
                    
                    status.info("⬇️ Downloading video...")
                    time.sleep(0.5)
                    
                    status.info("🎤 Transcribing audio...")
                    time.sleep(0.5)
                    
                    status.info("📄 Generating summary...")
                    
                    result = youtube_summarizer.process_youtube_video(youtube_url, word_count)
                    
                    if result:
                        status.empty()
                        
                        st.markdown(f"##### 📹 Video: {result['title']}")
                        st.markdown("##### 📝 Summary:")
                        st.text_area("Summary", value=result['summary'], height=200, key="youtube_summary")
                        
                        st.success("✅ Summary generated successfully!")
                    else:
                        st.error("❌ Failed to process video. Please check the URL and try again.")
                        
            except Exception as e:
                st.error(f"❌ Processing failed: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

def render_word_to_story(story_generator):
    words_input = st.text_input(
        "Enter words (comma-separated)",
        placeholder="adventure, forest, mystery, courage",
        key="story_words"
    )
    
    theme = st.text_input(
        "Story theme",
        placeholder="Fantasy adventure, Mystery thriller, etc.",
        key="story_theme"
    )
    
    story_col1, story_col2 = st.columns(2)
    
    with story_col1:
        word_count = st.slider(
            "Story word count",
            min_value=100,
            max_value=1000,
            value=300,
            step=50,
            key="story_word_count"
        )
    
    with story_col2:
        language = st.selectbox(
            "Language",
            ["English", "Hindi"],
            key="story_language"
        )
    
    st.markdown('<div class="feature-button-wrapper">', unsafe_allow_html=True)
    if st.button("✨ Generate Story", key="story_btn", use_container_width=True):
        if not words_input.strip():
            st.error("Please enter some words")
        elif not theme.strip():
            st.error("Please enter a theme")
        else:
            try:
                with st.spinner("Creating your story... This may take a moment"):
                    words_list = [word.strip() for word in words_input.split(',')]
                    
                    status = st.empty()
                    status.info("✍️ Writing story...")
                    time.sleep(0.5)
                    
                    status.info("🎙️ Generating emotional narration...")
                    
                    result = story_generator.create_story_with_audio(
                        words=words_list,
                        theme=theme,
                        word_count=word_count,
                        language=language.lower()
                    )
                    
                    if result and result['story']:
                        status.empty()
                        
                        st.markdown("##### 📝 Your Story:")
                        st.text_area("Story", value=result['story'], height=300, key="generated_story")
                        
                        if result['audio_bytes']:
                            st.markdown("##### 🎧 Audio Narration:")
                            st.audio(result['audio_bytes'], format='audio/mpeg')
                            
                            st.download_button(
                                label="📥 Download Audio",
                                data=result['audio_bytes'],
                                file_name=f"story_{int(time.time())}.mp3",
                                mime="audio/mpeg",
                                key="story_audio_download"
                            )
                            st.success("✅ Story created successfully with audio narration!")
                        else:
                            st.warning("⚠️ Story created, but audio generation failed. This may be due to API limitations.")
                            st.info("💡 You can still read the story above. Audio narration will be available when API access is restored.")
                    else:
                        st.error("❌ Failed to generate story. Please try again.")
                        
            except Exception as e:
                st.error(f"❌ Story generation failed: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

def render_video_dubbing(video_processor, dubbing_service):
    input_video_path = None
    video_uploaded = False
    source_lang = "en"
    target_lang = "hi"
    
    uploaded_file = st.file_uploader(
        "Choose your video file",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help="Supported formats: MP4, AVI, MOV, MKV | Max size: 100MB",
        key="video_dubbing_uploader"
    )
    
    if uploaded_file is not None:
        if not validate_video_file(uploaded_file):
            st.error("❌ Invalid video file or file too large (max 100MB)")
        else:
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            video_uploaded = True
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(uploaded_file.read())
                input_video_path = tmp_file.name
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**🌍 Source Language**")
                source_lang = st.selectbox(
                    "From",
                    ["en", "hi", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"],
                    format_func=lambda x: {
                        "en": "🇬🇧 English", "hi": "🇮🇳 Hindi", "es": "🇪🇸 Spanish", 
                        "fr": "🇫🇷 French", "de": "🇩🇪 German", "it": "🇮🇹 Italian",
                        "pt": "🇵🇹 Portuguese", "ja": "🇯🇵 Japanese", 
                        "ko": "🇰🇷 Korean", "zh": "🇨🇳 Chinese"
                    }.get(x, x),
                    label_visibility="collapsed",
                    key="dubbing_source_lang"
                )
            
            with col2:
                st.markdown("**🎯 Target Language**")
                target_lang = st.selectbox(
                    "To",
                    ["hi", "en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"],
                    format_func=lambda x: {
                        "en": "🇬🇧 English", "hi": "🇮🇳 Hindi", "es": "🇪🇸 Spanish", 
                        "fr": "🇫🇷 French", "de": "🇩🇪 German", "it": "🇮🇹 Italian",
                        "pt": "🇵🇹 Portuguese", "ja": "🇯🇵 Japanese", 
                        "ko": "🇰🇷 Korean", "zh": "🇨🇳 Chinese"
                    }.get(x, x),
                    label_visibility="collapsed",
                    key="dubbing_target_lang"
                )
    else:
        st.info("📤 Upload a video file to start dubbing")
    
    st.markdown('<div class="feature-button-wrapper">', unsafe_allow_html=True)
    if st.button("🎬 Dub Video", use_container_width=True, key="dub_video_btn", disabled=not video_uploaded):
        if video_uploaded and input_video_path:
            process_video_with_elevenlabs(
                input_video_path, 
                source_lang, 
                target_lang,
                video_processor,
                dubbing_service
            )
    st.markdown('</div>', unsafe_allow_html=True)

def render_article_to_podcast(article_podcast):
    article_text = st.text_area(
        "Enter news article or text",
        placeholder="Paste your news article or any text here...",
        height=200,
        key="article_input"
    )
    
    script_word_count = st.slider(
        "Podcast script length (words)",
        min_value=100,
        max_value=500,
        value=300,
        step=50,
        key="podcast_script_length"
    )
    
    st.markdown('<div class="feature-button-wrapper">', unsafe_allow_html=True)
    if st.button("🎧 Generate Podcast", key="podcast_btn", use_container_width=True):
        if not article_text.strip():
            st.error("Please enter an article or text")
        else:
            try:
                with st.spinner("Creating your podcast... This may take a moment"):
                    status = st.empty()
                    
                    def progress_callback(message, percent):
                        status.info(f"{message}")
                    
                    audio_bytes = article_podcast.create_podcast_from_article(
                        article_text=article_text,
                        script_word_count=script_word_count,
                        progress_callback=progress_callback
                    )
                    
                    if audio_bytes:
                        status.empty()
                        
                        st.markdown("##### 🎧 Your Podcast:")
                        st.audio(audio_bytes, format='audio/mpeg')
                        
                        st.download_button(
                            label="📥 Download Podcast",
                            data=audio_bytes,
                            file_name=f"podcast_{int(time.time())}.mp3",
                            mime="audio/mpeg",
                            key="podcast_download"
                        )
                        
                        st.success("✅ Podcast created successfully!")
                        st.info("💡 This podcast features a conversational format with a Host and an Expert discussing your article.")
                    else:
                        st.error("❌ Failed to generate podcast. Please try again.")
                        
            except Exception as e:
                st.error(f"❌ Podcast generation failed: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

@st.cache_resource
def initialize_services():
    try:
        elevenlabs_api_key = os.environ.get('ELEVENLABS_API_KEY')
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
        
        if not elevenlabs_api_key:
            st.error("🔑 API key environment variable not set")
            return None, None, None, None, None, None, None
        
        if not gemini_api_key:
            st.error("🔑 GEMINI_API_KEY environment variable not set")
            return None, None, None, None, None, None, None
        
        video_processor = VideoProcessor()
        dubbing_service = ElevenLabsDubbing(api_key=elevenlabs_api_key)
        elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
        gemini_client = genai.Client(api_key=gemini_api_key)
        youtube_summarizer = YouTubeSummarizer(gemini_api_key=gemini_api_key)
        story_generator = StoryGenerator(gemini_api_key=gemini_api_key, elevenlabs_api_key=elevenlabs_api_key)
        article_podcast = ArticleToPodcast(gemini_api_key=gemini_api_key, elevenlabs_api_key=elevenlabs_api_key)
        
        return video_processor, dubbing_service, elevenlabs_client, gemini_client, youtube_summarizer, story_generator, article_podcast
    except Exception as e:
        st.error(f"❌ Failed to initialize services: {str(e)}")
        return None, None, None, None, None, None, None

def main():
    st.markdown("""
        <div class="header">
            <span class="logo">🌐 Anuvaad AI</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="hero">
            <h1>Transform Content<br>Across Languages</h1>
            <p>AI-powered video dubbing, text-to-speech, speech-to-text, and translation</p>
            <span class="badge">✨ Powered by Advanced AI Technology</span>
        </div>
    """, unsafe_allow_html=True)
    
    services = initialize_services()
    if None in services:
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.error("⚠️ Failed to initialize application services. Please check API keys.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    video_processor, dubbing_service, elevenlabs_client, gemini_client, youtube_summarizer, story_generator, article_podcast = services
    
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    
    st.markdown('<h2 style="text-align: center; margin: 1rem 0 2rem 0;">Main Features</h2>', unsafe_allow_html=True)
    
    row1_col1, row1_col2 = st.columns(2, gap="large")
    
    with row1_col1:
        with st.container(border=True):
            st.markdown('<h3 style="text-align: center; margin: 0 0 1rem 0;">🎬 Video Dubbing</h3>', unsafe_allow_html=True)
            render_video_dubbing(video_processor, dubbing_service)
    
    with row1_col2:
        with st.container(border=True):
            st.markdown('<h3 style="text-align: center; margin: 0 0 1rem 0;">📺 YouTube Summarizer</h3>', unsafe_allow_html=True)
            render_youtube_summarizer(youtube_summarizer)
    
    row2_col1, row2_col2 = st.columns(2, gap="large")
    
    with row2_col1:
        with st.container(border=True):
            st.markdown('<h3 style="text-align: center; margin: 0 0 1rem 0;">📖 Word to Story</h3>', unsafe_allow_html=True)
            render_word_to_story(story_generator)
    
    with row2_col2:
        with st.container(border=True):
            st.markdown('<h3 style="text-align: center; margin: 0 0 1rem 0;">🎙️ Article to Podcast</h3>', unsafe_allow_html=True)
            render_article_to_podcast(article_podcast)
    
    st.markdown("---")
    st.markdown('<h2 style="text-align: center; margin: 2rem 0;">Additional Tools</h2>', unsafe_allow_html=True)
    
    btn_col1, btn_col2, btn_col3 = st.columns(3, gap="medium")
    
    with btn_col1:
        if st.button("🗣️ Text to Speech", key="tts_feature_btn", use_container_width=True):
            st.session_state.active_feature = "tts"
    
    with btn_col2:
        if st.button("🎤 Speech to Text", key="stt_feature_btn", use_container_width=True):
            st.session_state.active_feature = "stt"
    
    with btn_col3:
        if st.button("🌐 Text Translation", key="trans_feature_btn", use_container_width=True):
            st.session_state.active_feature = "trans"
    
    if "active_feature" not in st.session_state:
        st.session_state.active_feature = None
    
    if st.session_state.active_feature == "tts":
        render_text_to_speech(elevenlabs_client)
    elif st.session_state.active_feature == "stt":
        render_speech_to_text()
    elif st.session_state.active_feature == "trans":
        render_text_translation(gemini_client)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="footer">
            <p>© 2025 Anuvaad AI - Advanced AI Technology</p>
            <p style="font-size: 0.85rem; margin-top: 0.5rem;">Breaking language barriers with artificial intelligence</p>
        </div>
    """, unsafe_allow_html=True)

def process_video_with_elevenlabs(input_path, source_lang, target_lang, video_proc, dub_svc):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🔄 Processing</div>', unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.markdown("**📤 Uploading video...**")
        progress_bar.progress(10)
        time.sleep(0.5)
        
        status_text.markdown("**🗣️ Transcribing speech...**")
        progress_bar.progress(25)
        time.sleep(0.5)
        
        status_text.markdown(f"**🌐 Translating {source_lang.upper()} → {target_lang.upper()}...**")
        progress_bar.progress(40)
        
        status_text.markdown("**🎙️ Generating AI voice...**")
        progress_bar.progress(50)
        
        def progress_callback(message, percent):
            status_text.markdown(f"**{message}**")
            progress_bar.progress(percent)
        
        dubbed_video_path = dub_svc.dub_video_complete(
            input_path,
            source_lang,
            target_lang,
            progress_callback=progress_callback
        )
        
        if not dubbed_video_path:
            st.error("❌ Failed to dub video. Please check your API configuration.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        progress_bar.progress(100)
        status_text.markdown("**✅ Dubbing completed!**")
        time.sleep(0.5)
        
        st.balloons()
        st.success("🎉 Your video is ready!")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📹 Original")
            st.video(input_path)
        
        with col2:
            st.markdown("##### 🎬 Dubbed")
            st.video(dubbed_video_path)
        
        st.markdown("---")
        
        with open(dubbed_video_path, 'rb') as f:
            st.download_button(
                label="📥 Download Dubbed Video",
                data=f.read(),
                file_name=f"anuvaad_ai_{source_lang}_to_{target_lang}_{int(time.time())}.mp4",
                mime="video/mp4",
                type="primary",
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"❌ Processing failed: {str(e)}")
        progress_bar.progress(0)
        status_text.markdown("**❌ Processing failed**")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
