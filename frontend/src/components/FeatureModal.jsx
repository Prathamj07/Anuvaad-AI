import './Modal.css';

function FeatureModal({ feature, onClose }) {
  if (!feature) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content feature-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>&times;</button>
        
        {feature.image && (
          <div className="feature-modal-image">
            <img src={feature.image} alt={feature.title} />
          </div>
        )}
        
        <div className="feature-modal-header">
          <span className="feature-icon">{feature.icon}</span>
          <h2>{feature.title}</h2>
        </div>
        
        <div className="feature-modal-body">
          <p>{feature.description}</p>
          
          {feature.details && (
            <div className="feature-details">
              <h3>Key Features:</h3>
              <ul>
                {feature.details.map((detail, idx) => (
                  <li key={idx}>{detail}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
        
        <div className="feature-modal-footer">
          <button className="btn-get-started" onClick={() => {
            if (feature.action) feature.action();
            onClose();
          }}>
            Get Started
          </button>
        </div>
      </div>
    </div>
  );
}

export default FeatureModal;
