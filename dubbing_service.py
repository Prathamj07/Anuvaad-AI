import os
import tempfile
import requests
from elevenlabs.client import ElevenLabs
from elevenlabs.types.voice_settings import VoiceSettings
from typing import Optional

class DubbingService:
    """Handles AI voice generation using ElevenLabs"""
    
    def __init__(self, api_key: str):
        """Initialize dubbing service with ElevenLabs API"""
        self.client = ElevenLabs(api_key=api_key)
        
        # Default voice IDs for different languages
        self.default_voices = {
            'en': {
                'male': 'pNInz6obpgDQGcFmaJgB',  # Adam
                'female': 'EXAVITQu4vr4xnSDxMaL'  # Bella
            },
            'hi': {
                'male': 'pNInz6obpgDQGcFmaJgB',  # Use English voice - can be changed
                'female': 'EXAVITQu4vr4xnSDxMaL'  # Use English voice - can be changed
            }
        }
        
        self.current_voice_id = None
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        try:
            voices = self.client.voices.get_all()
            return [
                {
                    'voice_id': voice.voice_id,
                    'name': voice.name,
                    'category': voice.category,
                    'labels': voice.labels
                }
                for voice in voices.voices
            ]
        except Exception as e:
            print(f"Error fetching voices: {e}")
            return []
    
    def select_voice(self, language: str, gender: str = 'female') -> str:
        """Select appropriate voice for language and gender"""
        try:
            # Use default voice mapping
            voices = self.default_voices.get(language, self.default_voices['en'])
            voice_id = voices.get(gender, voices['female'])
            self.current_voice_id = voice_id
            return voice_id
        except:
            # Fallback to default English female voice
            self.current_voice_id = self.default_voices['en']['female']
            return self.current_voice_id
    
    def generate_speech(self, text: str, language: str, 
                       stability: float = 0.75, clarity: float = 0.75, 
                       style: float = 0.0, enhance: bool = True) -> Optional[str]:
        """
        Generate speech from text using ElevenLabs
        """
        try:
            # Select appropriate voice if not already set
            if not self.current_voice_id:
                self.select_voice(language)
            
            # Ensure voice_id is set
            voice_id = self.current_voice_id
            if not voice_id:
                return None
            
            # Generate speech with voice settings
            voice_settings_obj = VoiceSettings(
                stability=stability,
                similarity_boost=clarity,
                style=style,
                use_speaker_boost=enhance
            )
            
            # Use appropriate model based on language
            model = "eleven_multilingual_v2"
            
            response = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                output_format="mp3_44100_128",
                model_id=model,
                voice_settings=voice_settings_obj
            )
            
            # Save audio to temporary file
            output_path = tempfile.mktemp(suffix='.mp3')
            
            with open(output_path, 'wb') as f:
                for chunk in response:
                    f.write(chunk)
            
            return output_path
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None
    
    def generate_speech_with_timing(self, segments: list, language: str,
                                   stability: float = 0.75, clarity: float = 0.75,
                                   style: float = 0.0) -> Optional[str]:
        """
        Generate speech for multiple segments with timing information
        """
        try:
            from pydub import AudioSegment
            import math
            
            # Select voice
            if not self.current_voice_id:
                self.select_voice(language)
            
            # Ensure voice_id is set
            voice_id = self.current_voice_id
            if not voice_id:
                return None
            
            # Generate complete audio
            complete_audio = AudioSegment.empty()
            last_end_time = 0
            
            for segment in segments:
                text = segment.get('text', '').strip()
                start_time = segment.get('start', last_end_time)
                end_time = segment.get('end', start_time + 1)
                
                if not text:
                    # Add silence for empty segments
                    silence_duration = int((end_time - start_time) * 1000)
                    complete_audio += AudioSegment.silent(duration=silence_duration)
                    last_end_time = end_time
                    continue
                
                # Add silence before segment if needed
                if start_time > last_end_time:
                    silence_duration = int((start_time - last_end_time) * 1000)
                    complete_audio += AudioSegment.silent(duration=silence_duration)
                
                # Generate speech for this segment
                voice_settings_obj = VoiceSettings(
                    stability=stability,
                    similarity_boost=clarity,
                    style=style,
                    use_speaker_boost=True
                )
                
                response = self.client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=text,
                    output_format="mp3_44100_128",
                    model_id="eleven_multilingual_v2",
                    voice_settings=voice_settings_obj
                )
                
                # Save segment audio
                segment_path = tempfile.mktemp(suffix='.mp3')
                with open(segment_path, 'wb') as f:
                    for chunk in response:
                        f.write(chunk)
                
                # Load and adjust timing
                segment_audio = AudioSegment.from_mp3(segment_path)
                target_duration = int((end_time - start_time) * 1000)
                
                if len(segment_audio) != target_duration:
                    # Adjust speed to match target duration
                    speed_ratio = len(segment_audio) / target_duration
                    if speed_ratio > 1.5 or speed_ratio < 0.5:
                        # If speed change is too dramatic, just truncate or pad
                        if len(segment_audio) > target_duration:
                            segment_audio = segment_audio[:target_duration]
                        else:
                            segment_audio += AudioSegment.silent(
                                duration=target_duration - len(segment_audio)
                            )
                    else:
                        # Use speed change
                        new_sample_rate = int(segment_audio.frame_rate * speed_ratio)
                        segment_audio = segment_audio._spawn(
                            segment_audio.raw_data,
                            overrides={"frame_rate": new_sample_rate}
                        ).set_frame_rate(segment_audio.frame_rate)
                
                complete_audio += segment_audio
                last_end_time = end_time
                
                # Cleanup
                os.unlink(segment_path)
            
            # Export final audio
            output_path = tempfile.mktemp(suffix='.wav')
            complete_audio.export(output_path, format='wav')
            
            return output_path
            
        except Exception as e:
            print(f"Error generating timed speech: {e}")
            return None
    
    def clone_voice_from_sample(self, audio_path: str, voice_name: str) -> Optional[str]:
        """
        Clone a voice from an audio sample (if ElevenLabs supports it)
        """
        try:
            # This would require ElevenLabs voice cloning API
            # For now, return None as this is a premium feature
            print("Voice cloning requires premium ElevenLabs subscription")
            return None
            
        except Exception as e:
            print(f"Error cloning voice: {e}")
            return None
    
    def adjust_voice_emotion(self, text: str, emotion: str, language: str) -> Optional[str]:
        """
        Generate speech with specific emotional tone
        """
        try:
            # Modify text to convey emotion
            emotional_prompts = {
                'happy': "Say this with joy and enthusiasm: ",
                'sad': "Say this with sadness and melancholy: ",
                'excited': "Say this with high energy and excitement: ",
                'calm': "Say this in a calm and peaceful manner: ",
                'serious': "Say this seriously and professionally: "
            }
            
            prompt = emotional_prompts.get(emotion, "")
            enhanced_text = f"{prompt}{text}" if prompt else text
            
            return self.generate_speech(enhanced_text, language)
            
        except Exception as e:
            print(f"Error adjusting emotion: {e}")
            return self.generate_speech(text, language)
    
    def get_voice_info(self, voice_id: str) -> dict:
        """Get information about a specific voice"""
        try:
            voice = self.client.voices.get(voice_id)
            return {
                'voice_id': voice.voice_id,
                'name': voice.name,
                'category': voice.category,
                'description': voice.description,
                'labels': voice.labels,
                'preview_url': voice.preview_url
            }
        except Exception as e:
            print(f"Error getting voice info: {e}")
            return {}
