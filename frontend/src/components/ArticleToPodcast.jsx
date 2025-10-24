import { useState } from 'react';
import { api } from '../api';

function ArticleToPodcast() {
  const [articleText, setArticleText] = useState('');
  const [scriptWordCount, setScriptWordCount] = useState(300);
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleGenerate = async () => {
    if (!articleText.trim()) {
      setError('Please enter an article or text');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);
    setAudioUrl(null);

    try {
      const result = await api.articleToPodcast(articleText, scriptWordCount);
      
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
      setError(err.response?.data?.error || 'Failed to generate podcast');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="feature-content">
      <textarea
        value={articleText}
        onChange={(e) => setArticleText(e.target.value)}
        placeholder="Paste your article or text here..."
        rows={6}
        className="input-field"
      />
      <div className="slider-container">
        <label>Podcast script length: {scriptWordCount} words</label>
        <input
          type="range"
          min="100"
          max="500"
          step="50"
          value={scriptWordCount}
          onChange={(e) => setScriptWordCount(Number(e.target.value))}
        />
      </div>
      <button onClick={handleGenerate} disabled={loading} className="primary-btn">
        {loading ? 'Creating...' : '🎧 Generate Podcast'}
      </button>
      {error && <div className="error-message">{error}</div>}
      {success && (
        <>
          <div className="success-message">✅ Podcast created successfully!</div>
          <div className="info-message">💡 This podcast features a conversational format with a Host and an Expert discussing your article.</div>
        </>
      )}
      {audioUrl && (
        <div className="audio-player">
          <h4>🎧 Your Podcast:</h4>
          <audio controls src={audioUrl} />
          <a href={audioUrl} download="podcast.mp3" className="download-btn">📥 Download Podcast</a>
        </div>
      )}
    </div>
  );
}

export default ArticleToPodcast;
