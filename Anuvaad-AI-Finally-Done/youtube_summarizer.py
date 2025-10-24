import os
import tempfile
import yt_dlp
import speech_recognition as sr
from pydub import AudioSegment
from google import genai
from typing import Optional, Dict
import time


class YouTubeSummarizer:
    """Handles YouTube video downloading, transcription, and summarization"""
    
    def __init__(self, gemini_api_key: str):
        """Initialize YouTube summarizer with Gemini API"""
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        self.recognizer = sr.Recognizer()
    
    def download_video(self, youtube_url: str) -> Optional[Dict[str, str]]:
        """
        Download YouTube video and extract audio
        Returns: {'video_path': path, 'audio_path': path, 'title': title}
        """
        try:
            video_path = tempfile.mktemp(suffix='.mp4')
            audio_path = tempfile.mktemp(suffix='.wav')
            
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': video_path,
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                title = info.get('title', 'Unknown')
            
            audio = AudioSegment.from_file(video_path)
            audio.export(audio_path, format='wav')
            
            return {
                'video_path': video_path,
                'audio_path': audio_path,
                'title': title
            }
            
        except Exception as e:
            print(f"Error downloading YouTube video: {e}")
            return None
    
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio to text using Google Speech Recognition
        """
        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None
    
    def transcribe_audio_in_chunks(self, audio_path: str, chunk_duration_ms: int = 30000) -> Optional[str]:
        """
        Transcribe long audio by splitting into chunks
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            chunks = []
            
            for i in range(0, len(audio), chunk_duration_ms):
                chunk = audio[i:i + chunk_duration_ms]
                
                chunk_path = tempfile.mktemp(suffix='.wav')
                chunk.export(chunk_path, format='wav')
                
                try:
                    with sr.AudioFile(chunk_path) as source:
                        audio_data = self.recognizer.record(source)
                        text = self.recognizer.recognize_google(audio_data)
                        chunks.append(text)
                except:
                    pass
                finally:
                    if os.path.exists(chunk_path):
                        os.unlink(chunk_path)
            
            return ' '.join(chunks) if chunks else None
            
        except Exception as e:
            print(f"Error transcribing audio in chunks: {e}")
            return None
    
    def summarize_text(self, text: str, word_count: int = 200) -> Optional[str]:
        """
        Summarize text using Gemini AI with specified word count
        """
        try:
            prompt = f"""
            Please provide a concise summary of the following text in approximately {word_count} words.
            
            Focus on the main points and key takeaways. Make the summary clear and informative.
            
            Text to summarize:
            {text}
            
            Summary (approximately {word_count} words):
            """
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return None
                
        except Exception as e:
            print(f"Summarization error: {e}")
            return None
    
    def process_youtube_video(self, youtube_url: str, word_count: int = 200) -> Optional[Dict]:
        """
        Complete pipeline: download, transcribe, and summarize YouTube video
        Returns: {'title': title, 'summary': summary}
        """
        try:
            download_result = self.download_video(youtube_url)
            if not download_result:
                return None
            
            video_path = download_result['video_path']
            audio_path = download_result['audio_path']
            title = download_result['title']
            
            transcript = self.transcribe_audio_in_chunks(audio_path)
            
            if os.path.exists(video_path):
                os.unlink(video_path)
            if os.path.exists(audio_path):
                os.unlink(audio_path)
            
            if not transcript:
                return None
            
            summary = self.summarize_text(transcript, word_count)
            
            if not summary:
                return None
            
            return {
                'title': title,
                'summary': summary,
                'transcript': transcript
            }
            
        except Exception as e:
            print(f"Error processing YouTube video: {e}")
            return None
