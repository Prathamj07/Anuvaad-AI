import './Footer.css';

function Footer() {
  const scrollToFAQ = () => {
    const element = document.getElementById('faq');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <footer id="footer" className="netflix-footer">
      <div className="footer-container">
        <div className="footer-links">
          <div className="footer-column">
            <h3>Company</h3>
            <a href="#">About Us</a>
            <a href="#">Careers</a>
            <a href="#">Press</a>
          </div>
          
          <div className="footer-column">
            <h3>Support</h3>
            <a href="#">Help Center</a>
            <a href="#">Contact Us</a>
            <a href="#" onClick={(e) => { e.preventDefault(); scrollToFAQ(); }}>FAQ</a>
          </div>
          
          <div className="footer-column">
            <h3>Legal</h3>
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Cookie Preferences</a>
          </div>
          
          <div className="footer-column">
            <h3>Follow Us</h3>
            <div className="social-links">
              <a href="#" className="social-icon">📘</a>
              <a href="#" className="social-icon">🐦</a>
              <a href="#" className="social-icon">📷</a>
              <a href="#" className="social-icon">💼</a>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; 2025 Anuvaad AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
