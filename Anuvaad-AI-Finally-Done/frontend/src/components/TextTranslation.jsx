import { useState } from 'react';
import { api } from '../api';

function TextTranslation() {
  const [text, setText] = useState('');
  const [fromLang, setFromLang] = useState('English');
  const [toLang, setToLang] = useState('Hindi');
  const [loading, setLoading] = useState(false);
  const [translation, setTranslation] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const languages = ['English', 'Hindi', 'Spanish', 'French', 'German', 'Italian', 'Portuguese', 'Japanese', 'Korean', 'Chinese'];

  const handleTranslate = async () => {
    if (!text.trim()) {
      setError('Please enter some text to translate');
      return;
    }
    if (fromLang === toLang) {
      setError('Source and target languages must be different');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);
    setTranslation('');

    try {
      const result = await api.textTranslation(text, fromLang, toLang);
      setTranslation(result.translated_text);
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to translate');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tool-content">
      <h3>🌐 Text Translation</h3>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type or paste text here..."
        rows={5}
      />
      <div className="language-selectors">
        <div>
          <label>From:</label>
          <select value={fromLang} onChange={(e) => setFromLang(e.target.value)}>
            {languages.map(lang => (
              <option key={lang} value={lang}>{lang}</option>
            ))}
          </select>
        </div>
        <div>
          <label>To:</label>
          <select value={toLang} onChange={(e) => setToLang(e.target.value)}>
            {languages.map(lang => (
              <option key={lang} value={lang}>{lang}</option>
            ))}
          </select>
        </div>
      </div>
      <button onClick={handleTranslate} disabled={loading} className="primary-btn">
        {loading ? 'Translating...' : '🔄 Translate'}
      </button>
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">✅ Translated from {fromLang} to {toLang}</div>}
      {translation && (
        <div className="result-box">
          <h4>📝 Translation:</h4>
          <textarea value={translation} readOnly rows={5} />
        </div>
      )}
    </div>
  );
}

export default TextTranslation;
