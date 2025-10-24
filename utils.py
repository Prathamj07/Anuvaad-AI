import os
import tempfile
from typing import Optional

def format_time(seconds: float) -> str:
    """
    Format time in seconds to MM:SS format
    """
    try:
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    except:
        return "00:00"

def validate_video_file(uploaded_file) -> bool:
    """
    Validate uploaded video file
    """
    try:
        # Check file size (max 100MB)
        if uploaded_file.size > 100 * 1024 * 1024:
            return False
        
        # Check file extension
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        return file_extension in allowed_extensions
    except:
        return False

def create_temp_file(suffix: str = '.tmp') -> str:
    """
    Create a temporary file and return its path
    """
    return tempfile.mktemp(suffix=suffix)

def cleanup_temp_file(file_path: str):
    """
    Safely delete a temporary file
    """
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
    except:
        pass

def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes
    """
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except:
        return 0.0

def validate_audio_format(audio_path: str) -> bool:
    """
    Validate audio file format
    """
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        return len(audio) > 0
    except:
        return False

def ensure_directory_exists(directory_path: str):
    """
    Ensure a directory exists, create if it doesn't
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
    except:
        pass

def get_supported_formats():
    """
    Get list of supported video and audio formats
    """
    return {
        'video': ['mp4', 'avi', 'mov', 'mkv'],
        'audio': ['wav', 'mp3', 'aac', 'm4a']
    }

def calculate_processing_time_estimate(video_duration: float) -> str:
    """
    Estimate processing time based on video duration
    """
    try:
        # Rough estimate: 3-5x the video duration for processing
        estimated_seconds = video_duration * 4
        
        if estimated_seconds < 60:
            return f"~{int(estimated_seconds)} seconds"
        elif estimated_seconds < 3600:
            minutes = int(estimated_seconds / 60)
            return f"~{minutes} minutes"
        else:
            hours = int(estimated_seconds / 3600)
            minutes = int((estimated_seconds % 3600) / 60)
            return f"~{hours}h {minutes}m"
    except:
        return "Unknown"

def validate_api_keys():
    """
    Validate that required API keys are available from environment
    """
    import os
    
    required_keys = {
        'elevenlabs': os.environ.get('ELEVENLABS_API_KEY', ''),
        'gemini': os.environ.get('GEMINI_API_KEY', '')
    }
    
    validation_results = {}
    for service, key in required_keys.items():
        validation_results[service] = bool(key and len(key) > 10)
    
    return validation_results

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    """
    try:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"
    except:
        return "Unknown"

def extract_filename_without_extension(file_path: str) -> str:
    """
    Extract filename without extension from file path
    """
    try:
        return os.path.splitext(os.path.basename(file_path))[0]
    except:
        return "unknown"

def is_valid_language_code(lang_code: str) -> bool:
    """
    Validate language code
    """
    supported_languages = ['en', 'hi']
    return lang_code in supported_languages

def create_progress_callback(progress_bar, status_text):
    """
    Create a callback function for progress updates
    """
    def update_progress(stage: str, percentage: int):
        try:
            progress_bar.progress(percentage / 100)
            status_text.text(stage)
        except:
            pass
    
    return update_progress

def safe_float_conversion(value, default: float = 0.0) -> float:
    """
    Safely convert value to float with default fallback
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int_conversion(value, default: int = 0) -> int:
    """
    Safely convert value to integer with default fallback
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def generate_unique_filename(base_name: str, extension: str) -> str:
    """
    Generate unique filename with timestamp
    """
    import time
    timestamp = int(time.time())
    return f"{base_name}_{timestamp}.{extension.lstrip('.')}"
