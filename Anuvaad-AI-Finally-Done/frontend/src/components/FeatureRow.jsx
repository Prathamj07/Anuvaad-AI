import { useRef } from 'react';
import FeatureCard from './FeatureCard';
import './FeatureRow.css';

function FeatureRow({ title, features, onCardClick }) {
  const rowRef = useRef(null);

  const scroll = (direction) => {
    if (rowRef.current) {
      const scrollAmount = 300;
      rowRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className="feature-row">
      <h2 className="row-title">{title}</h2>
      <div className="row-container">
        <button className="scroll-btn scroll-left" onClick={() => scroll('left')}>
          ‹
        </button>
        <div className="cards-container" ref={rowRef}>
          {features.map((feature, idx) => (
            <FeatureCard 
              key={idx} 
              feature={feature} 
              onClick={() => onCardClick(feature)}
            />
          ))}
        </div>
        <button className="scroll-btn scroll-right" onClick={() => scroll('right')}>
          ›
        </button>
      </div>
    </div>
  );
}

export default FeatureRow;
