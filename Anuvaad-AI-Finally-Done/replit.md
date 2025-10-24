# Anuvaad AI - Professional Video Dubbing

## Overview

Anuvaad AI is a professional video dubbing application that translates and dubs videos from one language to another while maintaining synchronization and audio quality. The application uses ElevenLabs for AI voice generation, Google Gemini for translation, and various audio/video processing libraries to create seamless dubbed content.

**Core Purpose**: 
- **Video Dubbing**: Transform videos into different languages by extracting audio, translating, generating dubbed audio, and synchronizing with original video timing
- **YouTube Summarizer**: Download and transcribe YouTube videos, then generate AI-powered summaries with customizable word count
- **Word to Story**: Create engaging stories from input words with themes, supporting English and Hindi with emotional audio narration
- **Additional Tools**: Text-to-speech, speech-to-text, and text translation utilities

**Technology Stack**:
- **Frontend**: React (Vite) with Netflix-style UI - modern, responsive interface with hero section, feature cards, and modal previews
- **Backend**: Flask REST API with JWT authentication
- **Database**: SQLite for user accounts and history tracking
- **Video Processing**: MoviePy, FFmpeg
- **Audio Processing**: Pydub, SpeechRecognition, Librosa (optional)
- **AI Services**: ElevenLabs (voice generation), Google Gemini (translation)
- **Language**: Python 3.x (backend), JavaScript/React (frontend)

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### 1. Frontend Architecture (React-based Netflix-style UI)

**Design Pattern**: Single-page application with component-based architecture

The application uses React with Vite for a modern, Netflix-inspired interface:
- **Styling Approach**: Custom CSS with Netflix-like design patterns
- **Hero Section**: Full-width background image with gradient overlay and call-to-action
- **Feature Cards**: Image-based cards with hover effects that open detailed modal previews
- **Layout**: Responsive design with sticky header navigation
- **Theme**: Dark theme with Netflix-style red accents (#E50914)
- **Typography**: Inter font family for modern, clean appearance
- **Authentication**: Modal-based login/signup flows with JWT token management

**Key Components**:
- `Hero.jsx` - Full-width hero section with background image
- `FeatureCard.jsx` - Individual feature cards with images
- `FeatureModal.jsx` - Detailed modal view with feature images and information
- `Header.jsx` - Sticky navigation with login/signup buttons
- `AuthContext.jsx` - Authentication state management

**Key Decision**: React was chosen for its component reusability and ability to create a polished Netflix-style UI with smooth interactions.

### 2. Backend Architecture (Modular Service Layer)

**Design Pattern**: Service-oriented architecture with single-responsibility modules

The application is organized into specialized service modules:

#### Video Processing Service (`video_processor.py`)
- **Purpose**: Handle video file operations and metadata extraction
- **Key Capabilities**:
  - Extract video information (duration, fps, dimensions, audio presence)
  - Extract audio tracks from video files using MoviePy/FFmpeg
- **Technology**: MoviePy with FFmpeg backend for cross-format compatibility

#### Audio Processing Service (`audio_processor.py`)
- **Purpose**: Separate speech from background audio and process audio segments
- **Key Capabilities**:
  - Speech/background separation using silence detection
  - Audio segment timestamp tracking
  - Optional advanced processing with Librosa (graceful degradation if unavailable)
- **Technology**: Pydub for basic processing, SpeechRecognition for transcription, Librosa for advanced features
- **Design Decision**: Librosa is optional dependency with fallback functionality to maintain compatibility

#### Translation Service (`translation_service.py`)
- **Purpose**: Translate transcribed text between languages
- **Key Capabilities**:
  - Context-aware translation optimized for video dubbing
  - Maintains emotional tone and timing considerations
  - Cultural appropriateness handling
- **Technology**: Google Gemini AI with specialized prompting
- **Design Decision**: Uses AI model for natural, context-aware translations rather than literal word-for-word translation

#### Dubbing Service (`dubbing_service.py`)
- **Purpose**: Generate AI voice audio for translated text
- **Key Capabilities**:
  - Voice selection by language and gender
  - Access to ElevenLabs voice library
  - Voice configuration management
- **Technology**: ElevenLabs API with voice settings customization
- **Design Decision**: Default voice mapping per language with extensibility for custom voice selection

#### ElevenLabs Dubbing Integration (`elevenlabs_dubbing.py`)
- **Purpose**: Use ElevenLabs' complete dubbing API for automated dubbing
- **Key Capabilities**:
  - Upload video and create dubbing projects
  - Monitor dubbing progress with polling
  - Download completed dubbed content
- **Technology**: ElevenLabs Dubbing API in "automatic" mode
- **Design Decision**: Provides alternative to manual pipeline using ElevenLabs' end-to-end dubbing service

#### Synchronization Engine (`sync_engine.py`)
- **Purpose**: Align dubbed audio timing with original video
- **Key Capabilities**:
  - Proportional timing allocation across segments
  - Audio stretching/compression for timing match
  - Segment-based synchronization
- **Technology**: Pydub for audio manipulation, optional Librosa for time-stretching
- **Design Decision**: Segment-based approach allows precise control over timing while maintaining audio quality

#### YouTube Summarizer Service (`youtube_summarizer.py`) - Added Oct 2025
- **Purpose**: Download, transcribe, and summarize YouTube videos
- **Key Capabilities**:
  - Download YouTube videos using yt-dlp
  - Extract and transcribe audio in chunks for long videos
  - Generate AI-powered summaries with configurable word count
- **Technology**: yt-dlp for downloading, SpeechRecognition for transcription, Google Gemini for summarization
- **Design Decision**: Chunk-based transcription handles long videos efficiently; summary-only output (no full transcript) keeps UI focused

#### Story Generator Service (`story_generator.py`) - Added Oct 2025
- **Purpose**: Generate creative stories from input words with emotional audio narration
- **Key Capabilities**:
  - AI story generation based on user-provided words, theme, and word count
  - Support for English and Hindi languages
  - Emotional text-to-speech with enhanced voice settings
  - Audio download functionality
- **Technology**: Google Gemini for story generation, ElevenLabs for emotional TTS
- **Design Decision**: Uses emotional voice settings (reduced stability, increased style) for engaging narration; graceful degradation when quota exceeded

### 3. Processing Pipeline Architecture

**Workflow**: Multi-stage processing pipeline with error handling at each stage

**Primary Flow**:
1. **Video Upload & Validation** → Size limits (100MB), format validation
2. **Audio Extraction** → MoviePy extracts WAV audio from video
3. **Speech Recognition** → SpeechRecognition transcribes audio to text
4. **Audio Separation** → Pydub separates speech from background (optional)
5. **Translation** → Gemini AI translates text to target language
6. **Voice Generation** → ElevenLabs generates dubbed audio
7. **Synchronization** → Sync engine aligns dubbed audio with original timing
8. **Final Assembly** → MoviePy combines dubbed audio with original video

**Alternative Flow** (ElevenLabs Direct):
1. **Video Upload** → Direct upload to ElevenLabs
2. **Dubbing Processing** → ElevenLabs handles extraction, translation, dubbing
3. **Download Result** → Retrieve completed dubbed video

**Design Decision**: Dual-pipeline approach provides flexibility—use manual pipeline for fine control or ElevenLabs automatic mode for simplicity.

### 4. Configuration & Utilities

**Utility Functions** (`utils.py`):
- Time formatting for UI display
- File validation for security
- Temporary file management
- Safe cleanup operations

**Design Decision**: Centralized utilities reduce code duplication and provide consistent error handling patterns.

### 5. Error Handling & Resilience

**Strategy**: Graceful degradation with optional dependencies

- **Optional Dependencies**: Librosa features degrade gracefully if not installed
- **API Failures**: Service modules return `None` or `Optional` types with try-except blocks
- **File Operations**: Temporary file cleanup in finally blocks
- **Validation**: Early validation prevents processing invalid inputs

### 6. State Management

**Approach**: Stateless processing with file-based intermediates

- **Session State**: Streamlit's session state for UI state management
- **Data Flow**: File paths passed between processing stages
- **Temporary Storage**: System temp directory for intermediate files
- **Cleanup**: Explicit cleanup after processing completion

**Design Decision**: File-based intermediates allow inspection, debugging, and recovery while avoiding memory constraints with large videos.

## External Dependencies

### AI & Cloud Services

**ElevenLabs API** (Primary Voice Service)
- **Purpose**: AI voice generation and complete dubbing pipeline
- **Authentication**: API key required (user-provided)
- **Services Used**:
  - Voice synthesis with customizable voice settings
  - Complete dubbing API for automated video dubbing
  - Voice library access for selection
- **Rate Limits**: Service-dependent (ElevenLabs tier-based)

**Google Gemini AI** (Translation Service)
- **Purpose**: Context-aware text translation
- **Authentication**: API key required (user-provided)
- **Service Used**: `genai.Client` for content generation
- **Model**: Uses Gemini models for translation tasks

### Media Processing Libraries

**MoviePy** (Video Processing)
- **Purpose**: Video file manipulation and audio extraction
- **Backend**: FFmpeg for codec support
- **Usage**: Video clips, audio extraction, final assembly

**FFmpeg** (Media Codec Engine)
- **Purpose**: Low-level media processing and format conversion
- **Integration**: Used via MoviePy wrapper
- **Requirement**: Must be installed on system PATH

**Pydub** (Audio Processing)
- **Purpose**: Audio manipulation and format conversion
- **Backend**: FFmpeg for audio codecs
- **Usage**: Silence detection, audio concatenation, format conversion

**SpeechRecognition** (Speech-to-Text)
- **Purpose**: Audio transcription
- **Backend**: Multiple recognizer options (Google, Sphinx, etc.)
- **Usage**: Convert speech audio to text for translation

**Librosa** (Advanced Audio Analysis) - Optional
- **Purpose**: Advanced audio processing and time-stretching
- **Installation**: Optional dependency with fallback behavior
- **Usage**: Audio time-stretching for synchronization

**Soundfile** (Audio I/O) - Optional
- **Purpose**: Audio file reading/writing for Librosa
- **Installation**: Optional dependency paired with Librosa

### Frontend Framework

**Streamlit** (Web Framework)
- **Purpose**: Rapid web application development
- **Features Used**:
  - File upload widgets
  - Progress indicators
  - Custom CSS injection
  - Video/audio playback
  - Session state management

### Python Standard Libraries

**Core Dependencies**:
- `tempfile`: Temporary file management
- `os`: File system operations
- `pathlib`: Path manipulation
- `time`: Timing and delays for API polling

### System Requirements

**FFmpeg Installation**: Required on system PATH for MoviePy and Pydub to function
**Python Version**: 3.x (type hints suggest 3.6+)
**Optional C Dependencies**: Librosa requires compiled audio processing libraries