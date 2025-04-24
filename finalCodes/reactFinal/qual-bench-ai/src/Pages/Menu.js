import React, { useState } from "react";
import { Link } from "react-router-dom";
import exampleImage from "./example.png";
import "./Menu.css";
import csusmLogo from './csusm-logo.png';
import qualcommLogo from './qualcomm-ai-hub-logo.png';

function Menu() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <div>
      {/* Header */}
      <div className="header">
        <div className="mobile-menu-icon" onClick={toggleMobileMenu}>
          {isMobileMenuOpen ? '✕' : '☰'}
        </div>
        <Link to="/" className="logo">Qual Bench AI</Link>
        <div className={`nav-links ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
          <Link to="/model-comparison" onClick={() => setIsMobileMenuOpen(false)}>Model Comparisons</Link>
          <Link to="/detailed-comparison" onClick={() => setIsMobileMenuOpen(false)}>Detailed Comparison</Link>
          <Link to="/methodology" onClick={() => setIsMobileMenuOpen(false)}>Methodology</Link>
          <Link to="/explore-now" onClick={() => setIsMobileMenuOpen(false)}>Explore Models</Link>
        </div>
        {/* Empty div to balance logo on desktop */}
        <div className="desktop-spacer"></div>
      </div>

      {/* Main Section */}
      <div className="main-section">
        <div className="text-content">
          <h2>Compare AI Models with Interactive Graphs</h2>
          <p>
            Explore our platform’s ability to visually compare AI models using comprehensive graphs. Select models and metrics to gain insights into performance differences, enhancing your decision-making process.
          </p>
          <div className="metrics">
            <p>Mean Average Precision (MAP)</p>
            <p>Inference Time Comparison</p>
            <p>Estimated Peak Memory Usage</p>
            <p>Compute Units</p>
          </div>
        </div>
        <div className="image-content">
          <img src={exampleImage} alt="AI Model Comparison Graphs" />
        </div>
      </div>

      {/* Footer */}
      <div className="footer">
        <div className="footer-content">
          <div className="footer-nav">
          </div>
          <hr className="footer-line" /> {/* Added white line */}
          <div className="footer-logos">
            <a href="https://www.csusm.edu/" target="_blank" rel="noopener noreferrer">
              <img src={csusmLogo} alt="CSUSM Logo" className="footer-logo" />
            </a>
            <a href="https://aihub.qualcomm.com/" target="_blank" rel="noopener noreferrer">
              <img src={qualcommLogo} alt="Qualcomm AI Hub Logo" className="footer-logo" />
            </a>
          </div>
          <p>© 2025 Qual Bench AI. All rights reserved. Terms & Conditions Privacy & Policy</p>
        </div>
      </div>
    </div>
  );
}

export default Menu;