import { useState } from 'react';
import { api } from '../api';

function WordToStory() {
  const [words, setWords] = useState('');
  const [theme, setTheme] = useState('');
  const [wordCount, setWordCount] = useState(300);
  const [language, setLanguage] = useState('english');
  const [loading, setLoading] = useState(false);
  const [story, setStory] = useState('');
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleGenerate = async () => {
    if (!words.trim()) {
      setError('Please enter some words');
      return;
    }
    if (!theme.trim()) {
      setError('Please enter a theme');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);
    setStory('');
    setAudioUrl(null);

    try {
      const result = await api.wordToStory(words, theme, wordCount, language);
      setStory(result.story);
      
      if (result.audio) {
        const audioBlob = new Blob(
          [Uint8Array.from(atob(result.audio), c => c.charCodeAt(0))],
          { type: 'audio/mpeg' }
        );
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
      }
      
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate story');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="feature-content">
      <input
        type="text"
        value={words}
        onChange={(e) => setWords(e.target.value)}
        placeholder="adventure, forest, mystery, courage"
        className="input-field"
      />
      <input
        type="text"
        value={theme}
        onChange={(e) => setTheme(e.target.value)}
        placeholder="Fantasy adventure, Mystery thriller, etc."
        className="input-field"
      />
      <div className="dual-controls">
        <div className="slider-container">
          <label>Story word count: {wordCount}</label>
          <input
            type="range"
            min="100"
            max="1000"
            step="50"
            value={wordCount}
            onChange={(e) => setWordCount(Number(e.target.value))}
          />
        </div>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="english">English</option>
          <option value="hindi">Hindi</option>
        </select>
      </div>
      <button onClick={handleGenerate} disabled={loading} className="primary-btn">
        {loading ? 'Creating...' : '✨ Generate Story'}
      </button>
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">✅ Story generated successfully!</div>}
      {story && (
        <div className="result-box">
          <h4>📝 Your Story:</h4>
          <textarea value={story} readOnly rows={12} />
        </div>
      )}
      {audioUrl && (
        <div className="audio-player">
          <h4>🎧 Audio Narration:</h4>
          <audio controls src={audioUrl} />
          <a href={audioUrl} download="story.mp3" className="download-btn">📥 Download Audio</a>
        </div>
      )}
    </div>
  );
}

export default WordToStory;
