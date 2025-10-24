import os
import tempfile
try:
    from moviepy import VideoFileClip, CompositeVideoClip, AudioFileClip
except ImportError:
    from moviepy.editor import VideoFileClip, CompositeVideoClip, AudioFileClip
import ffmpeg
from typing import Optional, Dict

class VideoProcessor:
    """Handles video processing operations"""
    
    def __init__(self):
        """Initialize video processor"""
        pass
    
    def get_video_info(self, video_path: str) -> Optional[Dict]:
        """
        Get basic information about the video file
        """
        try:
            with VideoFileClip(video_path) as video:
                return {
                    'duration': video.duration,
                    'fps': video.fps,
                    'width': video.w,
                    'height': video.h,
                    'has_audio': video.audio is not None
                }
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
    
    def extract_audio(self, video_path: str) -> Optional[str]:
        """
        Extract audio track from video file
        """
        try:
            output_path = tempfile.mktemp(suffix='.wav')
            
            # Use moviepy to extract audio
            with VideoFileClip(video_path) as video:
                if video.audio is None:
                    print("No audio track found in video")
                    return None
                
                # Extract audio and save as WAV
                video.audio.write_audiofile(
                    output_path,
                    logger=None  # Suppress output
                )
            
            return output_path
            
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return None
    
    def create_dubbed_video(self, original_video_path: str, dubbed_audio_path: str) -> Optional[str]:
        """
        Create final dubbed video by combining original video with new audio
        """
        try:
            output_path = tempfile.mktemp(suffix='.mp4')
            
            # Load original video (without audio)
            with VideoFileClip(original_video_path) as original_video:
                # Load dubbed audio
                with AudioFileClip(dubbed_audio_path) as dubbed_audio:
                    
                    # Get video duration
                    video_duration = original_video.duration
                    audio_duration = dubbed_audio.duration
                    
                    # Ensure audio matches video duration exactly
                    if abs(audio_duration - video_duration) > 0.1:  # 100ms tolerance
                        # Adjust audio duration to match video
                        if audio_duration > video_duration:
                            dubbed_audio = dubbed_audio.subclip(0, video_duration)
                        else:
                            # Extend audio with silence if needed
                            from moviepy.audio.AudioClip import AudioClip
                            silence_duration = video_duration - audio_duration
                            silence = AudioClip(
                                make_frame=lambda t: 0,
                                duration=silence_duration
                            ).set_fps(dubbed_audio.fps)
                            dubbed_audio = dubbed_audio.concatenate_audioclips([dubbed_audio, silence])
                    
                    # Remove original audio and add dubbed audio
                    final_video = original_video.without_audio().set_audio(dubbed_audio)
                    
                    # Write final video
                    final_video.write_videofile(
                        output_path,
                        codec='libx264',
                        audio_codec='aac',
                        temp_audiofile='temp-audio.m4a',
                        remove_temp=True,
                        logger=None
                    )
            
            return output_path
            
        except Exception as e:
            print(f"Error creating dubbed video: {e}")
            return None
    
    def create_side_by_side_comparison(self, original_path: str, dubbed_path: str) -> Optional[str]:
        """
        Create a side-by-side comparison video
        """
        try:
            output_path = tempfile.mktemp(suffix='.mp4')
            
            with VideoFileClip(original_path) as original, VideoFileClip(dubbed_path) as dubbed:
                # Resize videos to half width
                original_resized = original.resize(width=original.w // 2)
                dubbed_resized = dubbed.resize(width=dubbed.w // 2)
                
                # Position videos side by side
                original_positioned = original_resized.set_position(('left', 'center'))
                dubbed_positioned = dubbed_resized.set_position(('right', 'center'))
                
                # Composite videos
                comparison = CompositeVideoClip([
                    original_positioned,
                    dubbed_positioned
                ], size=(original.w, original.h))
                
                # Write comparison video
                comparison.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    logger=None
                )
            
            return output_path
            
        except Exception as e:
            print(f"Error creating comparison video: {e}")
            return None
    
    def extract_video_frames_at_timestamps(self, video_path: str, timestamps: list) -> list:
        """
        Extract video frames at specific timestamps for analysis
        """
        try:
            frames = []
            
            with VideoFileClip(video_path) as video:
                for timestamp in timestamps:
                    try:
                        # Extract frame at timestamp
                        frame = video.get_frame(timestamp)
                        frames.append({
                            'timestamp': timestamp,
                            'frame': frame
                        })
                    except:
                        continue
            
            return frames
            
        except Exception as e:
            print(f"Error extracting frames: {e}")
            return []
    
    def optimize_video_for_web(self, video_path: str) -> Optional[str]:
        """
        Optimize video for web playback
        """
        try:
            output_path = tempfile.mktemp(suffix='.mp4')
            
            # Use ffmpeg for optimization
            (
                ffmpeg
                .input(video_path)
                .output(
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    preset='fast',
                    crf=23,
                    movflags='faststart'  # Enable streaming
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            return output_path
            
        except Exception as e:
            print(f"Error optimizing video: {e}")
            return video_path
    
    def validate_video_format(self, video_path: str) -> bool:
        """
        Validate if video format is supported
        """
        try:
            with VideoFileClip(video_path) as video:
                # Basic validation - check if video can be loaded
                return video.duration > 0 and video.fps > 0
        except:
            return False
    
    def get_video_metadata(self, video_path: str) -> Dict:
        """
        Get comprehensive video metadata
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            metadata = {
                'format': probe['format']['format_name'],
                'duration': float(probe['format']['duration']),
                'size': int(probe['format']['size']),
                'bitrate': int(probe['format']['bit_rate'])
            }
            
            if video_stream:
                metadata.update({
                    'video_codec': video_stream['codec_name'],
                    'width': int(video_stream['width']),
                    'height': int(video_stream['height']),
                    'fps': eval(video_stream['r_frame_rate'])
                })
            
            if audio_stream:
                metadata.update({
                    'audio_codec': audio_stream['codec_name'],
                    'sample_rate': int(audio_stream['sample_rate']),
                    'channels': int(audio_stream['channels'])
                })
            
            return metadata
            
        except Exception as e:
            print(f"Error getting metadata: {e}")
            return {}
