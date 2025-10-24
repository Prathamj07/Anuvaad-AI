import os
import tempfile
import subprocess
from typing import Optional, Dict, Callable
from elevenlabs import ElevenLabs, VoiceSettings
from google import genai

class ArticleToPodcast:
    """Handles conversion of articles to multi-speaker podcast audio"""
    
    def __init__(self, gemini_api_key: str, elevenlabs_api_key: str):
        """Initialize article to podcast service with Gemini and ElevenLabs APIs"""
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
        
        # Voice mapping for different speakers
        self.host_voice_id = "pNInz6obpgDQGcFmaJgB"    # Adam - Host voice
        self.expert_voice_id = "XB0fDUnXU5powFXDhCwa"  
    
    def generate_podcast_script(self, article_text: str, word_count: int = 300) -> Optional[str]:
        """
        Generate a podcast script from article text using Gemini
        Returns: Formatted script with Host: and Expert: labels
        """
        try:
            prompt = f"""
Summarize the following article into a detailed podcast script (~{word_count} words) as a conversation:
- Include a "Host" and an "Expert".
- Each line should start with "Host:" or "Expert:".
- Make it engaging, explanatory, and conversational.
- The Host should introduce the topic and ask questions.
- The Expert should provide insights and explanations.
- Make it sound natural and informative.

Article:
---
{article_text}
---

Generate the podcast script:
"""
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                # Fallback script
                return self._generate_fallback_script(article_text)
                
        except Exception as e:
            print(f"Error generating podcast script: {e}")
            return self._generate_fallback_script(article_text)
    
    def _generate_fallback_script(self, article_text: str) -> str:
        """Generate a simple fallback script if AI generation fails"""
        words = article_text.split()[:100]
        summary = ' '.join(words)
        
        return f"""Host: Welcome to our podcast. Today, we're discussing an important article.
Expert: {summary}
Host: That's very interesting. Can you tell us more about this?
Expert: Certainly. This article highlights several key points that deserve attention.
Host: Thank you for sharing these insights with us today.
Expert: My pleasure. It's important to stay informed about these developments."""
    
    def generate_speaker_audio(self, text: str, voice_id: str, output_file: str) -> bool:
        """
        Generate audio for a single speaker line using ElevenLabs
        Returns: True if successful, False otherwise
        """
        try:
            audio_generator = self.elevenlabs_client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75
                )
            )
            
            with open(output_file, 'wb') as f:
                for chunk in audio_generator:
                    f.write(chunk)
            
            return True
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            return False
    
    def merge_audio_files(self, audio_files: list, output_file: str) -> bool:
        """
        Merge multiple audio files into a single file using FFmpeg
        Returns: True if successful, False otherwise
        """
        try:
            # Create a temporary file list for FFmpeg
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                for audio_file in audio_files:
                    f.write(f"file '{audio_file}'\n")
                file_list_path = f.name
            
            # Use FFmpeg to concatenate audio files
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", file_list_path, "-c", "copy", output_file
            ], check=True, capture_output=True)
            
            # Clean up the file list
            os.unlink(file_list_path)
            return True
            
        except Exception as e:
            print(f"Error merging audio files: {e}")
            return False
    
    def create_podcast_from_article(self, article_text: str, script_word_count: int = 300, 
                                   progress_callback: Optional[Callable] = None) -> Optional[bytes]:
        """
        Complete workflow to convert article to podcast audio
        Returns: Audio bytes if successful, None otherwise
        """
        try:
            # Step 1: Generate script
            if progress_callback:
                progress_callback("Generating podcast script...", 20)
            
            script = self.generate_podcast_script(article_text, script_word_count)
            if not script:
                return None
            
            # Step 2: Parse script and generate audio for each line
            if progress_callback:
                progress_callback("Generating audio for speakers...", 40)
            
            lines = script.strip().split('\n')
            audio_files = []
            temp_files = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                speaker, text, voice_id = "", "", ""
                
                if line.lower().startswith("host:"):
                    speaker, text, voice_id = "Host", line[5:].strip(), self.host_voice_id
                elif line.lower().startswith("expert:"):
                    speaker, text, voice_id = "Expert", line[7:].strip(), self.expert_voice_id
                else:
                    continue
                
                if not text:
                    continue
                
                # Generate audio file
                temp_audio = tempfile.mktemp(suffix=f'_speaker_{i}.mp3')
                temp_files.append(temp_audio)
                
                if self.generate_speaker_audio(text, voice_id, temp_audio):
                    audio_files.append(temp_audio)
                
                # Update progress
                if progress_callback:
                    progress = 40 + int((i / len(lines)) * 40)
                    progress_callback(f"Processing speaker {i+1}/{len(lines)}...", progress)
            
            if not audio_files:
                return None
            
            # Step 3: Merge audio files
            if progress_callback:
                progress_callback("Merging audio segments...", 85)
            
            final_output = tempfile.mktemp(suffix='_podcast.mp3')
            temp_files.append(final_output)
            
            if not self.merge_audio_files(audio_files, final_output):
                return None
            
            # Step 4: Read the final audio file
            if progress_callback:
                progress_callback("Finalizing podcast...", 95)
            
            with open(final_output, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass
            
            if progress_callback:
                progress_callback("Complete!", 100)
            
            return audio_bytes
            
        except Exception as e:
            print(f"Error creating podcast: {e}")
            return None
