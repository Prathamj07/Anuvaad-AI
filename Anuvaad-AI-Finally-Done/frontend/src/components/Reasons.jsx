import './Reasons.css';

function Reasons() {
  const reasons = [
    {
      icon: '🌍',
      title: 'Break Language Barriers',
      description: 'Reach global audiences by translating and dubbing your content into 50+ languages with AI-powered precision and natural-sounding voices.'
    },
    {
      icon: '⚡',
      title: 'Lightning-Fast Processing',
      description: 'Get your dubbed videos and translations in minutes, not days. Our AI technology processes content at incredible speeds without compromising quality.'
    },
    {
      icon: '🎯',
      title: 'Professional Quality Output',
      description: 'Experience studio-quality results with natural voice synthesis, perfect lip-sync, and emotional tone preservation in every translation.'
    },
    {
      icon: '💡',
      title: 'All-in-One Creative Suite',
      description: 'Access video dubbing, YouTube summarization, story generation, and more - all the tools you need for content creation in one place.'
    }
  ];

  return (
    <section className="reasons-section">
      <h2 className="reasons-title">More reasons to use Anuvaad AI</h2>
      <div className="reasons-grid">
        {reasons.map((reason, idx) => (
          <div key={idx} className="reason-card">
            <div className="reason-icon-wrapper">
              <span className="reason-icon">{reason.icon}</span>
            </div>
            <h3>{reason.title}</h3>
            <p>{reason.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Reasons;
