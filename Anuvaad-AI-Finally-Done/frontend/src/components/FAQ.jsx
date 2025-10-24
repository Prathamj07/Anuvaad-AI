import { useState } from 'react';
import './FAQ.css';

function FAQ() {
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      question: 'What is Anuvaad AI?',
      answer: 'Anuvaad AI is a professional AI-powered platform that helps you translate and dub videos, summarize YouTube content, generate creative stories, and perform various text and audio transformations. We use advanced AI technology from ElevenLabs and Google Gemini to deliver high-quality, natural-sounding results across 50+ languages.'
    },
    {
      question: 'How does the video dubbing feature work?',
      answer: 'Our video dubbing feature uses AI to extract audio from your video, translate it to your chosen language, generate natural-sounding dubbed audio with the same emotional tone, and synchronize it perfectly with your video. The entire process is automated and typically takes just a few minutes, delivering professional-quality dubbed videos ready for global audiences.'
    },
    {
      question: 'Which languages are supported?',
      answer: 'Anuvaad AI supports 50+ languages including English, Spanish, French, German, Hindi, Mandarin, Japanese, Korean, Arabic, Portuguese, Italian, Russian, and many more. Our AI ensures natural translations while preserving context, tone, and cultural nuances.'
    },
    {
      question: 'What file formats are supported?',
      answer: 'For video dubbing, we support common formats like MP4, AVI, MOV, and MKV. Audio files can be WAV, MP3, or M4A. Our YouTube Summarizer works with any YouTube video URL. All processed files are returned in widely compatible formats for easy use.'
    },
    {
      question: 'How accurate is the translation?',
      answer: 'Our translations use Google Gemini AI, which provides highly accurate, context-aware translations. The AI understands idioms, cultural references, and maintains the original meaning while adapting to the target language naturally. For critical content, we recommend reviewing translations, but our accuracy rate is excellent for most use cases.'
    },
    {
      question: 'Is there a limit on video length or file size?',
      answer: 'File size and video length limits depend on your subscription plan. Free users can process videos up to 10 minutes and 100MB. Premium users enjoy extended limits with videos up to 2 hours and 1GB file sizes. Check your account dashboard for specific limits.'
    },
    {
      question: 'Can I use Anuvaad AI for commercial purposes?',
      answer: 'Yes! Anuvaad AI can be used for commercial projects including marketing videos, educational content, podcasts, YouTube videos, and business presentations. All content you create with our platform is yours to use commercially. Please review our Terms of Service for complete licensing details.'
    },
    {
      question: 'How do I get started?',
      answer: 'Getting started is easy! Simply sign up for a free account, choose the feature you want to use (video dubbing, YouTube summarizer, etc.), upload your content or provide a URL, select your target language, and let our AI do the work. Your processed content will be ready for download in minutes.'
    }
  ];

  const toggleFAQ = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section id="faq" className="faq-section">
      <h2 className="faq-title">Frequently Asked Questions</h2>
      <div className="faq-container">
        {faqs.map((faq, index) => (
          <div key={index} className="faq-item">
            <button 
              className={`faq-question ${openIndex === index ? 'active' : ''}`}
              onClick={() => toggleFAQ(index)}
            >
              <span>{faq.question}</span>
              <span className="faq-icon">{openIndex === index ? '×' : '+'}</span>
            </button>
            <div className={`faq-answer ${openIndex === index ? 'open' : ''}`}>
              <p>{faq.answer}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default FAQ;
