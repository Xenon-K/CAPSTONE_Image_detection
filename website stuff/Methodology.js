import React from "react";
import { Link } from "react-router-dom";
import "./Menu.css";
import csusmLogo from './csusm-logo.png';
import qualcommLogo from './qualcomm-ai-hub-logo.png';

function Methodology() {
    return (
        <div>
            {/* Header */}
            <div className="header">
                <Link to="/" className="logo">Qual Bench AI</Link>
                <div className="nav-links">
                    <Link to="/model-comparison">Model Comparisons</Link>
                    <Link to="/detailed-comparison">Detailed Comparison</Link>
                    <Link to="/methodology">Methodology</Link>
                </div>
                <a href="https://aihub.qualcomm.com/models?domain=Computer+Vision&useCase=Object+Detection" className="cta-button">
                    Explore Now
                </a>
            </div>

            {/* Main Section */}
            <div className="main-section">
                <div className="text-content">
                    <h2>Our Methodology</h2>
                    <p>
                        The leaderboard data is sourced from the Qualcomm AI Hub and other reliable open-source benchmarks. We evaluate AI models using metrics like Mean Average Precision (mAP), inference time, memory usage, and compute unit requirements.
                    </p>
                    <p>
                        All models are tested under uniform hardware and software environments to ensure consistency. Metrics are either directly extracted from official sources or calculated using a standardized benchmarking script.
                    </p>
                    <div className="metrics">
                        <p>✔ Consistent testing environments</p>
                        <p>✔ Verified benchmark sources</p>
                        <p>✔ Transparent metric definitions</p>
                        <p>✔ Publicly accessible references</p>
                    </div>
                </div>
                <div className="image-content">
                    {/* Optional: Insert relevant image if available */}
                    <img src="https://via.placeholder.com/500x300?text=Benchmark+Process" alt="Benchmark Methodology Illustration" />
                </div>
            </div>

            {/* Footer */}
            <div className="footer">
                <div className="footer-content">
                    <div className="footer-nav">
                        <Link to="/model-comparison">Model Comparisons</Link>
                        <Link to="/methodology">Methodology</Link>
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

export default Methodology;