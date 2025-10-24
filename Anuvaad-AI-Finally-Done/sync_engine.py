import os
import tempfile
from pydub import AudioSegment
try:
    import librosa
    import soundfile as sf
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    import numpy as np
    LIBROSA_AVAILABLE = False
from typing import List, Dict, Optional

class SyncEngine:
    """Handles audio-video synchronization and timing alignment"""
    
    def __init__(self):
        """Initialize synchronization engine"""
        pass
    
    def synchronize_audio(self, dubbed_audio_path: str, original_segments: List[Dict], 
                         original_audio_path: str) -> Optional[str]:
        """
        Synchronize dubbed audio with original video timing
        """
        try:
            # Load original and dubbed audio
            original_audio = AudioSegment.from_file(original_audio_path)
            dubbed_audio = AudioSegment.from_file(dubbed_audio_path)
            
            # Create synchronized audio with same length as original
            synced_audio = AudioSegment.silent(duration=len(original_audio))
            
            # Process each segment
            for segment in original_segments:
                start_ms = int(segment['start'] * 1000)
                end_ms = int(segment['end'] * 1000)
                segment_duration = end_ms - start_ms
                
                if segment_duration <= 0:
                    continue
                
                # Extract corresponding portion from dubbed audio
                # For now, assume dubbed audio follows same segment order
                try:
                    # Calculate proportional position in dubbed audio
                    total_original_duration = sum(
                        (seg['end'] - seg['start']) for seg in original_segments
                    )
                    segment_ratio = (segment['end'] - segment['start']) / total_original_duration
                    
                    dubbed_start = int(len(dubbed_audio) * (segment['start'] / original_segments[-1]['end']))
                    dubbed_segment_length = int(len(dubbed_audio) * segment_ratio)
                    dubbed_end = dubbed_start + dubbed_segment_length
                    
                    if dubbed_end > len(dubbed_audio):
                        dubbed_end = len(dubbed_audio)
                    
                    dubbed_segment = dubbed_audio[dubbed_start:dubbed_end]
                    
                    # Adjust dubbed segment to fit original timing
                    if len(dubbed_segment) != segment_duration:
                        dubbed_segment = self._adjust_segment_timing(
                            dubbed_segment, segment_duration
                        )
                    
                    # Overlay dubbed segment onto synchronized audio
                    synced_audio = synced_audio.overlay(dubbed_segment, position=start_ms)
                    
                except Exception as e:
                    print(f"Error processing segment: {e}")
                    continue
            
            # Export synchronized audio
            output_path = tempfile.mktemp(suffix='.wav')
            synced_audio.export(output_path, format='wav')
            
            return output_path
            
        except Exception as e:
            print(f"Error in synchronization: {e}")
            return dubbed_audio_path
    
    def _adjust_segment_timing(self, audio_segment: AudioSegment, target_duration: int) -> AudioSegment:
        """
        Adjust audio segment timing to match target duration
        """
        try:
            current_duration = len(audio_segment)
            
            if current_duration == target_duration:
                return audio_segment
            
            # Calculate speed adjustment ratio
            speed_ratio = current_duration / target_duration
            
            # Limit extreme speed changes
            if speed_ratio > 2.0:
                speed_ratio = 2.0
            elif speed_ratio < 0.5:
                speed_ratio = 0.5
            
            # Apply speed change using frame rate manipulation
            new_frame_rate = int(audio_segment.frame_rate * speed_ratio)
            
            adjusted_segment = audio_segment._spawn(
                audio_segment.raw_data,
                overrides={"frame_rate": new_frame_rate}
            ).set_frame_rate(audio_segment.frame_rate)
            
            # Fine-tune length if still not matching
            if len(adjusted_segment) > target_duration:
                adjusted_segment = adjusted_segment[:target_duration]
            elif len(adjusted_segment) < target_duration:
                padding = target_duration - len(adjusted_segment)
                adjusted_segment += AudioSegment.silent(duration=padding)
            
            return adjusted_segment
            
        except Exception as e:
            print(f"Error adjusting segment timing: {e}")
            return audio_segment
    
    def align_with_video_frames(self, audio_path: str, video_fps: float, 
                               video_duration: float) -> Optional[str]:
        """
        Align audio with video frame rate for perfect synchronization
        """
        try:
            # Load audio
            audio = AudioSegment.from_file(audio_path)
            
            # Calculate target duration based on video
            target_duration_ms = int(video_duration * 1000)
            
            # Adjust audio length to match video exactly
            if len(audio) != target_duration_ms:
                if len(audio) > target_duration_ms:
                    # Truncate audio
                    audio = audio[:target_duration_ms]
                else:
                    # Pad with silence
                    padding = target_duration_ms - len(audio)
                    audio += AudioSegment.silent(duration=padding)
            
            # Ensure audio sample rate is compatible with video frame rate
            # Standard approach: use 48kHz for video compatibility
            target_sample_rate = 48000
            if audio.frame_rate != target_sample_rate:
                audio = audio.set_frame_rate(target_sample_rate)
            
            # Export aligned audio
            output_path = tempfile.mktemp(suffix='.wav')
            audio.export(output_path, format='wav')
            
            return output_path
            
        except Exception as e:
            print(f"Error aligning with video frames: {e}")
            return audio_path
    
    def detect_speech_timing(self, audio_path: str) -> List[Dict]:
        """
        Detect precise speech timing in audio
        """
        try:
            if not LIBROSA_AVAILABLE:
                # Fallback: use basic pydub detection
                from pydub.silence import detect_nonsilent
                audio = AudioSegment.from_file(audio_path)
                
                nonsilent_ranges = detect_nonsilent(
                    audio,
                    min_silence_len=100,
                    silence_thresh=audio.dBFS - 16
                )
                
                return [{
                    'start': start / 1000.0,
                    'end': end / 1000.0,
                    'duration': (end - start) / 1000.0
                } for start, end in nonsilent_ranges]
            
            # Load audio with librosa for better analysis
            y, sr = librosa.load(audio_path)
            
            # Detect onset times (beginning of sounds)
            onset_frames = librosa.onset.onset_detect(
                y=y, sr=sr, units='time', hop_length=512, backtrack=True
            )
            
            # Detect speech activity using energy-based method
            frame_length = 2048
            hop_length = 512
            
            # Calculate RMS energy
            rms = librosa.feature.rms(
                y=y, frame_length=frame_length, hop_length=hop_length
            )[0]
            
            # Convert frame indices to time
            times = librosa.frames_to_time(
                np.arange(len(rms)), sr=sr, hop_length=hop_length
            )
            
            # Detect speech segments based on energy threshold
            energy_threshold = np.mean(rms) * 0.1
            speech_segments = []
            
            in_speech = False
            segment_start = None
            
            for i, (time, energy) in enumerate(zip(times, rms)):
                if energy > energy_threshold and not in_speech:
                    # Start of speech
                    in_speech = True
                    segment_start = time
                elif energy <= energy_threshold and in_speech:
                    # End of speech
                    in_speech = False
                    if segment_start is not None:
                        speech_segments.append({
                            'start': segment_start,
                            'end': time,
                            'duration': time - segment_start
                        })
            
            # Handle case where audio ends during speech
            if in_speech and segment_start is not None:
                speech_segments.append({
                    'start': segment_start,
                    'end': times[-1],
                    'duration': times[-1] - segment_start
                })
            
            return speech_segments
            
        except Exception as e:
            print(f"Error detecting speech timing: {e}")
            return []
    
    def create_timing_map(self, original_segments: List[Dict], 
                         dubbed_segments: List[Dict]) -> List[Dict]:
        """
        Create timing mapping between original and dubbed segments
        """
        try:
            timing_map = []
            
            for i, (orig, dubbed) in enumerate(zip(original_segments, dubbed_segments)):
                timing_map.append({
                    'segment_id': i,
                    'original_start': orig.get('start', 0),
                    'original_end': orig.get('end', 0),
                    'original_duration': orig.get('end', 0) - orig.get('start', 0),
                    'dubbed_start': dubbed.get('start', 0),
                    'dubbed_end': dubbed.get('end', 0),
                    'dubbed_duration': dubbed.get('end', 0) - dubbed.get('start', 0),
                    'speed_ratio': (dubbed.get('end', 0) - dubbed.get('start', 0)) / 
                                  max(orig.get('end', 0) - orig.get('start', 0), 0.001)
                })
            
            return timing_map
            
        except Exception as e:
            print(f"Error creating timing map: {e}")
            return []
    
    def apply_dynamic_time_warping(self, original_audio_path: str, 
                                  dubbed_audio_path: str) -> Optional[str]:
        """
        Apply dynamic time warping for better synchronization
        """
        try:
            if not LIBROSA_AVAILABLE:
                # Fallback: simple duration matching
                original = AudioSegment.from_file(original_audio_path)
                dubbed = AudioSegment.from_file(dubbed_audio_path)
                
                if len(original) == len(dubbed):
                    return dubbed_audio_path
                
                # Adjust speed to match duration
                speed_ratio = len(dubbed) / len(original)
                new_frame_rate = int(dubbed.frame_rate * speed_ratio)
                adjusted = dubbed._spawn(dubbed.raw_data, overrides={"frame_rate": new_frame_rate})
                adjusted = adjusted.set_frame_rate(dubbed.frame_rate)
                
                output_path = tempfile.mktemp(suffix='.wav')
                adjusted.export(output_path, format='wav')
                return output_path
            
            # Load both audio files
            y1, sr1 = librosa.load(original_audio_path)
            y2, sr2 = librosa.load(dubbed_audio_path)
            
            # Ensure same sample rate
            if sr1 != sr2:
                y2 = librosa.resample(y2, orig_sr=sr2, target_sr=sr1)
                sr2 = sr1
            
            # Extract chroma features for alignment
            chroma1 = librosa.feature.chroma_cqt(y=y1, sr=sr1)
            chroma2 = librosa.feature.chroma_cqt(y=y2, sr=sr2)
            
            # Compute DTW alignment
            D, wp = librosa.sequence.dtw(chroma1, chroma2, subseq=True)
            
            # Apply time warping to dubbed audio
            # This is a simplified approach - full DTW implementation would be more complex
            warped_indices = wp[:, 1]
            warped_audio = y2[warped_indices * (len(y2) // len(warped_indices))]
            
            # Ensure output length matches original
            if len(warped_audio) != len(y1):
                if len(warped_audio) > len(y1):
                    warped_audio = warped_audio[:len(y1)]
                else:
                    # Pad with zeros
                    warped_audio = np.pad(warped_audio, (0, len(y1) - len(warped_audio)))
            
            # Save warped audio
            output_path = tempfile.mktemp(suffix='.wav')
            sf.write(output_path, warped_audio, sr1)
            
            return output_path
            
        except Exception as e:
            print(f"Error in dynamic time warping: {e}")
            return dubbed_audio_path
    
    def validate_synchronization(self, original_audio_path: str, 
                                dubbed_audio_path: str) -> Dict:
        """
        Validate synchronization quality between original and dubbed audio
        """
        try:
            # Load both audio files
            original = AudioSegment.from_file(original_audio_path)
            dubbed = AudioSegment.from_file(dubbed_audio_path)
            
            # Basic validation metrics
            duration_diff = abs(len(original) - len(dubbed))
            duration_match = duration_diff < 100  # Within 100ms
            
            validation_result = {
                'duration_match': duration_match,
                'duration_difference_ms': duration_diff,
                'original_duration': len(original),
                'dubbed_duration': len(dubbed),
                'sync_quality': 'Good' if duration_match else 'Needs adjustment'
            }
            
            return validation_result
            
        except Exception as e:
            print(f"Error validating synchronization: {e}")
            return {
                'duration_match': False,
                'sync_quality': 'Error',
                'error': str(e)
            }
