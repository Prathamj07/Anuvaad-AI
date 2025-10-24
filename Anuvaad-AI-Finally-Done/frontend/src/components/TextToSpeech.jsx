import { useState } from 'react';
import { api } from '../api';

function TextToSpeech() {
  const [text, setText] = useState('');
  const [voice, setVoice] = useState('Rachel');
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const voices = ['Rachel', 'Adam', 'Antoni', 'Arnold', 'Bella', 'Domi', 'Elli', 'Josh', 'Sam'];

  const handleGenerate = async () => {
    if (!text.trim()) {
      setError('Please enter some text first');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);
    setAudioUrl(null);

    try {
      const result = await api.textToSpeech(text, voice);
      const audioBlob = new Blob(
        [Uint8Array.from(atob(result.audio), c => c.charCodeAt(0))],
        { type: 'audio/mpeg' }
      );
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate speech');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tool-content">
      <h3>🗣️ Text to Speech</h3>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type or paste your text here..."
        rows={6}
      />
      <select value={voice} onChange={(e) => setVoice(e.target.value)}>
        {voices.map(v => (
          <option key={v} value={v}>{v}</option>
        ))}
      </select>
      <button onClick={handleGenerate} disabled={loading} className="primary-btn">
        {loading ? 'Generating...' : '🎵 Generate Speech'}
      </button>
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">✅ Speech generated successfully!</div>}
      {audioUrl && (
        <div className="audio-player">
          <audio controls src={audioUrl} />
          <a href={audioUrl} download="speech.mp3" className="download-btn">📥 Download Audio</a>
        </div>
      )}
    </div>
  );
}

export default TextToSpeech;
