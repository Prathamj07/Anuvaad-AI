import axios from 'axios';

const API_BASE_URL = '/api';

export const api = {
  textToSpeech: async (text, voice) => {
    const response = await axios.post(`${API_BASE_URL}/text-to-speech`, {
      text,
      voice
    });
    return response.data;
  },

  speechToText: async (audioFile) => {
    const formData = new FormData();
    formData.append('audio', audioFile);
    const response = await axios.post(`${API_BASE_URL}/speech-to-text`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  textTranslation: async (text, fromLang, toLang) => {
    const response = await axios.post(`${API_BASE_URL}/text-translation`, {
      text,
      from_lang: fromLang,
      to_lang: toLang
    });
    return response.data;
  },

  youtubeSummary: async (url, wordCount) => {
    const response = await axios.post(`${API_BASE_URL}/youtube-summary`, {
      url,
      word_count: wordCount
    });
    return response.data;
  },

  wordToStory: async (words, theme, wordCount, language) => {
    const response = await axios.post(`${API_BASE_URL}/word-to-story`, {
      words,
      theme,
      word_count: wordCount,
      language
    });
    return response.data;
  },

  articleToPodcast: async (articleText, scriptWordCount) => {
    const response = await axios.post(`${API_BASE_URL}/article-to-podcast`, {
      article_text: articleText,
      script_word_count: scriptWordCount
    });
    return response.data;
  },

  startVideoDubbing: async (videoFile, sourceLang, targetLang) => {
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('source_lang', sourceLang);
    formData.append('target_lang', targetLang);
    const response = await axios.post(`${API_BASE_URL}/video-dubbing/start`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  getDubbingStatus: async (dubbingId) => {
    const response = await axios.get(`${API_BASE_URL}/video-dubbing/status/${dubbingId}`);
    return response.data;
  },

  downloadDubbedVideo: async (dubbingId, targetLang) => {
    const response = await axios.get(`${API_BASE_URL}/video-dubbing/download/${dubbingId}`, {
      params: { target_lang: targetLang },
      responseType: 'blob'
    });
    return response.data;
  }
};
