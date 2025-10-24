import './FeatureCard.css';

function FeatureCard({ feature, onClick }) {
  return (
    <div className="feature-card-netflix" onClick={onClick}>
      <div className="card-image" style={{
        backgroundImage: feature.image ? `url(${feature.image})` : 'none',
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}>
        {!feature.image && <span className="card-icon">{feature.icon}</span>}
      </div>
      <div className="card-overlay">
        <h3>{feature.title}</h3>
        <p>{feature.shortDesc}</p>
      </div>
    </div>
  );
}

export default FeatureCard;
