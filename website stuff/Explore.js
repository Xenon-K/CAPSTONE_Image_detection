import React from 'react';
import { Link } from 'react-router-dom';
import './Explore.css';
import csusmLogo from './csusm-logo.png';
import qualcommLogo from './qualcomm-ai-hub-logo.png';

const modules = [
  { title: "Module 1", url: "https://example.com/1" },
  { title: "Module 2", url: "https://example.com/2" },
  { title: "Module 3", url: "https://example.com/3" },
  { title: "Module 4", url: "https://example.com/4" },
  { title: "Module 5", url: "https://example.com/5" },
  { title: "Module 6", url: "https://example.com/6" },
  { title: "Module 7", url: "https://example.com/7" },
  { title: "Module 8", url: "https://example.com/8" },
  { title: "Module 9", url: "https://example.com/9" },
  { title: "Module 10", url: "https://example.com/10" },
  { title: "Module 11", url: "https://example.com/11" },
  { title: "Module 12", url: "https://example.com/12" },
  { title: "Module 13", url: "https://example.com/13" },
  { title: "Module 14", url: "https://example.com/14" },
  { title: "Module 15", url: "https://example.com/15" },
  { title: "Module 16", url: "https://example.com/16" },
];

function Explore() {
  return (
    <div className="explore-page">
      {/* Header */}
      <div className="header">
        <Link to="/" className="logo">Qual Bench AI</Link>
        <div className="nav-links">
          <Link to="/model-comparison">Model Comparisons</Link>
          <Link to="/detailed-comparison">Detailed Comparison</Link>
          <Link to="/methodology">Methodology</Link>
        </div>
        <Link to="/explore-now" className="cta-button">Explore Now</Link>
      </div>

      {/* Main Grid Section */}
      <div className="explore-content">
        <h2>Explore AI Modules</h2>
        <div className="module-grid">
          {modules.map((mod, index) => (
            <a key={index} href={mod.url} target="_blank" rel="noopener noreferrer" className="module-card">
              {mod.title}
            </a>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="footer">
        <div className="footer-content">
          <div className="footer-nav">
            <Link to="/model-comparison">Model Comparisons</Link>
            <Link to="/methodology">Methodology</Link>
            <Link to="/explore-now">Explore Now</Link>
          </div>
          <hr className="footer-line" />
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

export default Explore;
