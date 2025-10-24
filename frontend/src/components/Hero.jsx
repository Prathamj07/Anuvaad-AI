import './Hero.css';

function Hero() {
  const scrollToFeatures = () => {
    const element = document.getElementById('features');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section id="hero" className="hero-section">
      <div className="hero-overlay"></div>
      <div className="hero-content">
        <h1 className="hero-title">Welcome to Anuvaad AI</h1>
        <p className="hero-subtitle">
          Transform your content across languages with AI-powered dubbing, translation, and creative tools. 
          Experience the future of multimedia content transformation.
        </p>
        <button className="btn-hero" onClick={scrollToFeatures}>
          Get Started
        </button>
      </div>
    </section>
  );
}

export default Hero;
