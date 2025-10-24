import { useState } from 'react';
import { api } from '../api';

function SpeechToText() {
  const [audioFile, setAudioFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleFileChange = (e) => {
    setAudioFile(e.target.files[0]);
    setTranscription('');
    setError(null);
    setSuccess(false);
  };

  const handleTranscribe = async () => {
    if (!audioFile) {
      setError('Please upload an audio file first');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);
    setTranscription('');

    try {
      const result = await api.speechToText(audioFile);
      setTranscription(result.text);
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to transcribe audio');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tool-content">
      <h3>🎤 Speech to Text</h3>
      <input
        type="file"
        accept=".wav,.mp3,.ogg,.flac,.m4a"
        onChange={handleFileChange}
        className="file-input"
      />
      {audioFile && (
        <audio controls src={URL.createObjectURL(audioFile)} style={{ width: '100%', margin: '10px 0' }} />
      )}
      <button onClick={handleTranscribe} disabled={loading || !audioFile} className="primary-btn">
        {loading ? 'Transcribing...' : '📝 Transcribe'}
      </button>
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">✅ Transcription completed!</div>}
      {transcription && (
        <div className="result-box">
          <h4>📄 Transcription:</h4>
          <textarea value={transcription} readOnly rows={6} />
        </div>
      )}
    </div>
  );
}

export default SpeechToText;
