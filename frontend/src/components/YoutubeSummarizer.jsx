import { useState } from 'react';
import { api } from '../api';

function YoutubeSummarizer() {
  const [url, setUrl] = useState('');
  const [wordCount, setWordCount] = useState(200);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState('');
  const [title, setTitle] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSummarize = async () => {
    if (!url.trim()) {
      setError('Please enter a YouTube URL');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);
    setSummary('');
    setTitle('');

    try {
      const result = await api.youtubeSummary(url, wordCount);
      setTitle(result.title);
      setSummary(result.summary);
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to process video');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="feature-content">
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://www.youtube.com/watch?v=..."
        className="input-field"
      />
      <div className="slider-container">
        <label>Summary word count: {wordCount}</label>
        <input
          type="range"
          min="50"
          max="500"
          step="50"
          value={wordCount}
          onChange={(e) => setWordCount(Number(e.target.value))}
        />
      </div>
      <button onClick={handleSummarize} disabled={loading} className="primary-btn">
        {loading ? 'Processing...' : '📝 Summarize Video'}
      </button>
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">✅ Summary generated successfully!</div>}
      {title && <h4 className="video-title">📹 Video: {title}</h4>}
      {summary && (
        <div className="result-box">
          <h4>📝 Summary:</h4>
          <textarea value={summary} readOnly rows={8} />
        </div>
      )}
    </div>
  );
}

export default YoutubeSummarizer;
