import React, {useState} from 'react';
import { Link } from "react-router-dom";
import "./Methodology.css";
import csusmLogo from './csusm-logo.png';
import qualcommLogo from './qualcomm-ai-hub-logo.png';

function Methodology() {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };
    return (
        <div className="methodology-page">
            {/* Header */}
            <div className="header">
                <div className="mobile-menu-icon" onClick={toggleMobileMenu}>
                {isMobileMenuOpen ? '✕' : '☰'}
                </div>
                <Link to="/" className="logo">Qual Bench AI</Link>
                <div className={`nav-links ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
                <Link to="/model-comparison" onClick={() => setIsMobileMenuOpen(false)}>Model Comparisons</Link>
                <Link to="/detailed-comparison" onClick={() => setIsMobileMenuOpen(false)}>Detailed Comparison</Link>
                <Link to="/methodology" onClick={() => setIsMobileMenuOpen(false)}><u>Methodology</u></Link>
                <Link to="/explore-now" onClick={() => setIsMobileMenuOpen(false)}>Explore Models</Link>
                </div>
                <div className="desktop-spacer"></div>
            </div>

            {/* Main Content */}
            <div className="methodology-content">
                <h2>Benchmarking Methodology</h2>

                <p>The dataset used in this project is <strong>COCO 2017</strong>, which includes 5,000 diverse and annotated images suitable for object detection tasks.</p>

                <p>To evaluate models fairly and consistently, we prepared three specialized datasets:</p>
                <ul>
                    <li><strong>DETR</strong></li>
                    <li><strong>YOLO Regular</strong></li>
                    <li><strong>YOLO Quantized</strong></li>
                </ul>

                <div className="methodology-image-section">
                    <img src="/images/image-ji.jpg" alt="Sample dataset image" />
                    <p><em>Back-end specialists Lucas Gomes and Kabire Akbari tuning the automation script of the compiling jobs.</em></p>
                </div>

                <h3>Preprocessing Steps</h3>
                <ul>
                    <li>DETR images: resized to <strong>480×480</strong> and cast to <code>float32</code>.</li>
                    <li>YOLO Regular images: resized to <strong>640×640</strong> and cast to <code>float32</code>.</li>
                    <li>YOLO Quantized images: resized to <strong>640×640</strong> and converted to <code>uint8</code>.</li>
                </ul>

                <p>Normalization approaches:</p>
                <ul>
                    <li><strong>YOLO Regular</strong>: divide by <code>255.0</code>.</li>
                    <li><strong>DETR</strong>: divide by <code>255.0</code>, subtract mean, divide by std. deviation.</li>
                    <li><strong>YOLO Quantized</strong>: only datatype conversion (no normalization).</li>
                </ul>

                <p>A <code>.csv</code> file was also created to track original image dimensions for accurate bounding box rescaling.</p>

                <h3>Inference & Profiling</h3>
                <p>Inference jobs were processed sequentially per model and device type, with profiling for:</p>
                <ul>
                    <li>Inference time</li>
                    <li>Memory usage</li>
                    <li>Hardware utilization (CPU, GPU, NPU)</li>
                </ul>

                <div className="methodology-image-section">
                    <img src="/images/Output Scrawl2.gif" alt="Visualization of automated submission of profiling jobs durring pre-processing" />
                    <p><em>Visualization of automated submission of profiling jobs durring pre-processing</em></p>
                </div>

                <h3>Model Output Handling</h3>
                <ul>
                    <li><strong>DETR</strong> had two output types:
                        <ul>
                            <li><em>Raw logits + bounding boxes</em>: required softmax, fallback to second-best if class was 0.</li>
                            <li><em>Pre-processed output</em>: used by DETR and all YOLO models.</li>
                        </ul>
                    </li>
                    <li><strong>YOLO Models</strong>: only used the pre-processed format.</li>
                </ul>

                <h3>Post-processing</h3>
                <p>YOLO models used Non-Maximum Suppression (NMS) with an IOU threshold of <strong>0.6</strong>.</p>
                <p>Final bounding boxes were rescaled to original image dimensions and saved to <code>results.json</code>.</p>

                <div className="methodology-image-section">
                    <img src="/images/image-lucas-kabire.jpg" alt="Example annotated image" />
                    <p><em>Database specialist Ji Guo making improvements on the MySQL Database.</em></p>
                </div>

                <h3>Evaluation</h3>
                <ul>
                    <li>Used the <strong>COCO Evaluation Toolkit</strong> to compare predictions to ground truth.</li>
                    <li>Metrics were stored in the project database for future reporting and visualization.</li>
                </ul>

                <div className="methodology-image-section">
                    <img src="/images/Coco2017img.jpg" alt="Example annotated image" />
                </div>


            </div>

            {/* Footer */}
            <div className="footer_group">
                <div className="footer-content_group">
                    <hr className="footer-line_group" />
                    <div className="footer-logos_group">
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
