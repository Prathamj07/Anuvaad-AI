import os
from google import genai
from google.genai import types
from typing import Optional

class TranslationService:
    """Handles text translation using Gemini AI"""
    
    def __init__(self, api_key: str):
        """Initialize translation service with Gemini API"""
        self.client = genai.Client(api_key=api_key)
        
        # Language mappings
        self.language_names = {
            'en': 'English',
            'hi': 'Hindi'
        }
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Translate text from source language to target language
        """
        try:
            # Skip translation if source and target are the same
            if source_lang == target_lang:
                return text
            
            source_name = self.language_names.get(source_lang, source_lang)
            target_name = self.language_names.get(target_lang, target_lang)
            
            # Create translation prompt
            prompt = f"""
            You are a professional translator specializing in video dubbing translation.
            
            Translate the following text from {source_name} to {target_name}.
            
            Guidelines:
            - Maintain the natural flow and timing suitable for dubbing
            - Preserve emotional tone and context
            - Keep sentence structure appropriate for spoken dialogue
            - Ensure cultural appropriateness
            - Maintain roughly similar length for timing synchronization
            
            Text to translate:
            {text}
            
            Provide only the translation without any additional comments or explanations.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return None
                
        except Exception as e:
            print(f"Translation error: {e}")
            return None
    
    def translate_with_context(self, text: str, source_lang: str, target_lang: str, 
                              context: str = "") -> Optional[str]:
        """
        Translate text with additional context for better accuracy
        """
        try:
            source_name = self.language_names.get(source_lang, source_lang)
            target_name = self.language_names.get(target_lang, target_lang)
            
            context_info = f"\nContext: {context}" if context else ""
            
            prompt = f"""
            You are a professional translator for video dubbing.
            
            Translate from {source_name} to {target_name}.{context_info}
            
            Requirements:
            - Natural dubbing-appropriate translation
            - Preserve emotional tone and meaning
            - Maintain similar timing/length
            - Cultural sensitivity
            
            Text: {text}
            
            Translation:
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text.strip() if response and response.text else None
            
        except Exception as e:
            print(f"Contextual translation error: {e}")
            return None
    
    def translate_segments(self, segments: list, source_lang: str, target_lang: str) -> list:
        """
        Translate multiple text segments while preserving timing information
        """
        translated_segments = []
        
        for segment in segments:
            original_text = segment.get('text', '')
            
            if not original_text.strip():
                # Keep empty segments
                translated_segments.append(segment.copy())
                continue
            
            translated_text = self.translate_text(original_text, source_lang, target_lang)
            
            if translated_text:
                translated_segment = segment.copy()
                translated_segment['text'] = translated_text
                translated_segment['original_text'] = original_text
                translated_segments.append(translated_segment)
            else:
                # Fallback to original text if translation fails
                fallback_segment = segment.copy()
                fallback_segment['translation_failed'] = True
                translated_segments.append(fallback_segment)
        
        return translated_segments
    
    def improve_translation_for_dubbing(self, text: str, target_lang: str) -> Optional[str]:
        """
        Improve translation specifically for dubbing requirements
        """
        try:
            target_name = self.language_names.get(target_lang, target_lang)
            
            prompt = f"""
            You are a dubbing specialist. Improve this {target_name} translation for video dubbing:
            
            "{text}"
            
            Make it more natural for speaking while maintaining:
            - Original meaning and emotion
            - Similar length/timing
            - Natural speech patterns
            - Cultural appropriateness
            
            Provide only the improved translation:
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text.strip() if response and response.text else text
            
        except Exception as e:
            print(f"Translation improvement error: {e}")
            return text
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of input text
        """
        try:
            prompt = f"""
            Detect the language of this text and respond with just the language code (en for English, hi for Hindi):
            
            "{text[:200]}"  # First 200 chars
            
            Language code:
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response and response.text:
                detected = response.text.strip().lower()
                return detected if detected in ['en', 'hi'] else None
            
            return None
            
        except Exception as e:
            print(f"Language detection error: {e}")
            return None
    
    def get_translation_quality_score(self, original: str, translation: str) -> float:
        """
        Get a quality score for the translation (0-1)
        """
        try:
            prompt = f"""
            Rate the translation quality on a scale of 0-1 (where 1 is perfect).
            
            Original: "{original}"
            Translation: "{translation}"
            
            Consider accuracy, naturalness, and appropriateness for dubbing.
            Respond with only a decimal number between 0 and 1:
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response and response.text:
                try:
                    score = float(response.text.strip())
                    return max(0.0, min(1.0, score))  # Clamp between 0 and 1
                except ValueError:
                    return 0.7  # Default score
            
            return 0.7
            
        except Exception as e:
            print(f"Quality scoring error: {e}")
            return 0.7
