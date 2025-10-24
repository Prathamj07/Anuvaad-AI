import os
import time
import tempfile
from elevenlabs.client import ElevenLabs
from typing import Optional, Dict

class ElevenLabsDubbing:
    """Handles video dubbing using ElevenLabs Dubbing API"""
    
    def __init__(self, api_key: str):
        """Initialize ElevenLabs dubbing service"""
        self.client = ElevenLabs(api_key=api_key)
        
        # Language code mapping
        self.language_codes = {
            'en': 'en',
            'hi': 'hi',
            'es': 'es',
            'fr': 'fr',
            'de': 'de',
            'it': 'it',
            'pt': 'pt',
            'ja': 'ja',
            'ko': 'ko',
            'zh': 'zh'
        }
    
    def create_dubbing_project(self, video_path: str, source_lang: str, 
                              target_lang: str, project_name: str = "Dubbing Project") -> Optional[str]:
        """
        Upload video and create dubbing project on ElevenLabs
        Returns: dubbing_id if successful
        """
        try:
            source_code = self.language_codes.get(source_lang, 'en')
            target_code = self.language_codes.get(target_lang, 'hi')
            
            # Upload video to ElevenLabs for dubbing
            with open(video_path, 'rb') as video_file:
                response = self.client.dubbing.create(
                    target_lang=target_code,
                    file=video_file,
                    mode="automatic",
                    source_lang=source_code,
                    num_speakers=1,
                    name=project_name,
                    watermark=True
                )
            
            dubbing_id = response.dubbing_id
            print(f"Created dubbing project: {dubbing_id}")
            return dubbing_id
            
        except Exception as e:
            print(f"Error creating dubbing project: {e}")
            return None
    
    def get_dubbing_status(self, dubbing_id: str) -> Dict:
        """
        Check the status of a dubbing project
        Returns: {'status': 'dubbing'|'dubbed'|'failed', 'metadata': ...}
        """
        try:
            metadata = self.client.dubbing.get(
                dubbing_id=dubbing_id
            )
            
            return {
                'status': metadata.status,
                'metadata': metadata,
                'name': metadata.name if hasattr(metadata, 'name') else None
            }
            
        except Exception as e:
            print(f"Error getting dubbing status: {e}")
            return {'status': 'error', 'metadata': None}
    
    def wait_for_dubbing_completion(self, dubbing_id: str, 
                                   callback=None, max_wait_seconds: int = 600) -> bool:
        """
        Wait for dubbing to complete with optional progress callback
        callback: function(status, elapsed_time) called periodically
        Returns: True if successful, False otherwise
        """
        try:
            start_time = time.time()
            
            while True:
                elapsed = time.time() - start_time
                
                # Check timeout
                if elapsed > max_wait_seconds:
                    print(f"Dubbing timed out after {max_wait_seconds} seconds")
                    return False
                
                # Get status
                metadata = self.client.dubbing.get(
                    dubbing_id=dubbing_id
                )
                
                status = metadata.status
                
                # Call progress callback
                if callback:
                    callback(status, int(elapsed))
                
                # Check completion
                if status == "dubbed":
                    print("Dubbing completed successfully!")
                    return True
                elif status == "dubbing":
                    print(f"Still processing... ({int(elapsed)}s elapsed)")
                    time.sleep(5)  # Poll every 5 seconds
                else:
                    print(f"Dubbing failed with status: {status}")
                    return False
                    
        except Exception as e:
            print(f"Error waiting for dubbing: {e}")
            return False
    
    def download_dubbed_video(self, dubbing_id: str, target_lang: str) -> Optional[str]:
        """
        Download the dubbed video from ElevenLabs
        Returns: Path to downloaded video file
        """
        try:
            target_code = self.language_codes.get(target_lang, 'hi')
            
            # Get the dubbed file
            audio_stream = self.client.dubbing.audio.get(
                dubbing_id=dubbing_id,
                language_code=target_code
            )
            
            # Save to temporary file
            output_path = tempfile.mktemp(suffix='.mp4')
            
            with open(output_path, 'wb') as f:
                for chunk in audio_stream:
                    f.write(chunk)
            
            print(f"Downloaded dubbed video to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error downloading dubbed video: {e}")
            return None
    
    def dub_video_complete(self, video_path: str, source_lang: str, 
                          target_lang: str, progress_callback=None) -> Optional[str]:
        """
        Complete dubbing workflow: upload, wait, download
        Returns: Path to dubbed video or None if failed
        """
        try:
            # Step 1: Create dubbing project
            if progress_callback:
                progress_callback("Uploading video to ElevenLabs...", 10)
            
            dubbing_id = self.create_dubbing_project(
                video_path, 
                source_lang, 
                target_lang,
                project_name=f"Dub {source_lang} to {target_lang}"
            )
            
            if not dubbing_id:
                return None
            
            # Step 2: Wait for completion
            if progress_callback:
                progress_callback("Processing on ElevenLabs servers...", 30)
            
            def status_callback(status, elapsed):
                if progress_callback:
                    progress = min(30 + (elapsed // 2), 80)  # Progress from 30% to 80%
                    progress_callback(f"Dubbing in progress... ({elapsed}s)", progress)
            
            success = self.wait_for_dubbing_completion(
                dubbing_id,
                callback=status_callback,
                max_wait_seconds=600
            )
            
            if not success:
                return None
            
            # Step 3: Download result
            if progress_callback:
                progress_callback("Downloading dubbed video...", 90)
            
            dubbed_video_path = self.download_dubbed_video(dubbing_id, target_lang)
            
            if progress_callback:
                progress_callback("Complete!", 100)
            
            return dubbed_video_path
            
        except Exception as e:
            print(f"Error in complete dubbing workflow: {e}")
            return None
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return {
            'en': 'English',
            'hi': 'Hindi',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese'
        }
