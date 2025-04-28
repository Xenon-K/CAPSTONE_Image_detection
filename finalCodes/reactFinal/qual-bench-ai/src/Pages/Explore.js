import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Explore.css';
import csusmLogo from './csusm-logo.png';
import qualcommLogo from './qualcomm-ai-hub-logo.png';

const API_BASE_URL = 'https://qualbenchai-backend-production.up.railway.app'; // Replace with your actual Railway backend URL

const modules = [
  {
    title: "Conditional-DETR-ResNet50",
    url: "https://aihub.qualcomm.com/models/conditional_detr_resnet50?domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/Conditional-DETR-ResNet50.jpg"
  },
  {
    title: "DETR-ResNet101",
    url: "https://aihub.qualcomm.com/models/detr_resnet101?domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/DETR-ResNet101.jpg"
  },
  {
    title: "DETR-ResNet101-DC5",
    url: "https://aihub.qualcomm.com/models/detr_resnet101_dc5?domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/DETR-ResNet101-DC5.jpg"
  },
  {
    title: "DETR-ResNet50-DC5",
    url: "https://aihub.qualcomm.com/models/detr_resnet50_dc5?domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/DETR-ResNet50-DC5.jpg"
  },
  {
    title: "DETR-ResNet50",
    url: "https://aihub.qualcomm.com/models/detr_resnet50?domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/DETR-ResNet50.jpg"
  },
  {
    title: "Yolo-v3",
    url: "https://aihub.qualcomm.com/models/yolov3?domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/yolo3.jpg"
  },
  {
    title: "Yolo-v6",
    url: "https://aihub.qualcomm.com/models/yolov6?domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/yolo6.jpg"
  },
  {
    title: "Yolo-v7",
    url: "https://aihub.qualcomm.com/models/yolov7?domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/yolo5-7.jpg"
  },
  {
    title: "Yolo-v8",
    url: "https://aihub.qualcomm.com/models/yolov8_det?searchTerm=yolo&domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/yolo8-10-11.jpg"
  },
  {
    title: "Yolo-v10",
    url: "https://aihub.qualcomm.com/models/yolov10_det?searchTerm=yolo&domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/yolo8-10-11.jpg"
  },
  {
    title: "Yolo-v11",
    url: "https://aihub.qualcomm.com/models/yolov11_det?searchTerm=yolo&domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/yolo8-10-11.jpg"
  },
  {
    title: "Yolo-v7-Quantized",
    url: "https://aihub.qualcomm.com/models/yolov7_quantized?searchTerm=yolo&domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/yolo5-7.jpg"
  },
  {
    title: "Yolo-v8-Quantized",
    url: "https://aihub.qualcomm.com/models/yolov8_det_quantized?searchTerm=yolo&domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/yolo8-10-11.jpg"
  },
  {
    title: "Yolo-v11-Quantized",
    url: "https://aihub.qualcomm.com/models/yolov11_det_quantized?searchTerm=yolo&domain=Computer+Vision&useCase=Object+Detection",
    image: "/images/yolo8-10-11.jpg"
  }
];

const deviceImages = {
  'SA8255 (Proxy)': '/images/SA8255.png',
  'SA8650 (Proxy)': '/images/SA8650.png',
  'QCS8550 (Proxy)': '/images/QCS8550.jpg',
  'QCS9075 (Proxy)': '/images/QCS9075.jpg',
  'Google Pixel 5 (Family)': '/images/Google_Pixel 5_(Family).png',
  'Samsung Galaxy S21 (Family)': '/images/Samsung_Galaxy_S21_(Family).jpg',
  'Samsung Galaxy S23 (Family)': '/images/Samsung_Galaxy_S23_(Family).png',
  'Samsung Galaxy S24 (Family)': '/images/Samsung_Galaxy_S24_(Family).png',
  'Samsung Galaxy Tab S8': '/images/Tab8.jpg',
  'Snapdragon 8 Elite QRD': '/images/8QRD.jpg',
  // ... Add more device image mappings as needed ...
};

const DEFAULT_DEVICE_IMAGE = '/images/SA8255.png'; // Define default image
const DEFAULT_DEVICE_NAME = 'SA8255 (Proxy)'; // Default device name

function Explore() {
  const [selectedModel, setSelectedModel] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [devices, setDevices] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredModules, setFilteredModules] = useState(modules);
  const [error, setError] = useState(null); // Add error state

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/devices`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setDevices(data);
        if (data.length > 0) {
          setSelectedDevice(data[0].device_id);
        }
      } catch (err) {
        console.error("Failed to fetch devices:", err);
        setError('Failed to fetch devices. Please check your network connection and backend server.'); // Set error
      }
    };
    fetchDevices();
  }, []);

  useEffect(() => {
    const fetchModelMetrics = async () => {
      if (selectedModel && selectedDevice) {
        try {
          const response = await fetch(`${API_BASE_URL}/api/modeldata?device_id=${selectedDevice}&model=${selectedModel.title}`);
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          setMetrics(data.data[selectedModel.title]);
        } catch (err) {
          console.error("Failed to fetch model metrics:", err);
          setError('Failed to fetch model metrics. Please check your network connection and backend server.'); // Set error
        }
      }
    }
    fetchModelMetrics();
  }, [selectedModel, selectedDevice]);

  /*
  useEffect(() => {
    fetch('http://172.25.133.11:5000/api/devices')
      .then(res => res.json())
      .then(data => {
        setDevices(data);
        if (data.length > 0) {
          setSelectedDevice(data[0].device_id);
        }
      })
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    if (selectedModel && selectedDevice) {
      fetch(`http://172.25.133.11:5000/api/modeldata?device_id=${selectedDevice}&model=${selectedModel.title}`)
        .then(res => res.json())
        .then(data => {
          setMetrics(data.data[selectedModel.title]);
        })
        .catch(err => console.error(err));
    }
  }, [selectedModel, selectedDevice]);
  */
 
  useEffect(() => {
    const filtered = modules.filter(module =>
      module.title.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredModules(filtered);
  }, [searchQuery]);

  const openModal = (model) => {
    setSelectedModel(model);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setSelectedModel(null); // Clear selected model when closing
    setIsModalOpen(false);
    setMetrics(null); // Clear metrics when closing
    setError(null); //clear error
  };

  const handleDeviceChange = (e) => {
    setSelectedDevice(e.target.value);
  };

  const handleTryOnAIHub = () => {
    if (selectedModel && selectedModel.url) {
      window.open(selectedModel.url, '_blank'); // Open in a new tab
    }
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  return (
    <div>
      <div className="explore-page">
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
            <Link to="/explore-now" onClick={() => setIsMobileMenuOpen(false)}><u>Explore Models</u></Link>
          </div>
          <div className="desktop-spacer"></div>
        </div>

        {/* Main Grid Section */}
        <div className="explore-content">
          <h2>Explore AI Models</h2>
          <div className="explore-header">
            <input
              type="text"
              className="search-box"
              placeholder="Search models..."
              value={searchQuery}
              onChange={handleSearchChange}
            />
          </div>
          <div className="module-grid">
            {filteredModules.map((mod, index) => (
              <div
                key={index}
                onClick={() => openModal(mod)}
                className="module-card"
                style={{ backgroundImage: `url(${mod.image})` }}
              >
                <div className="module-overlay">{mod.title}</div>
              </div>
            ))}
          </div>
          {error && <p className="error-message">{error}</p>}
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <span className="close" onClick={closeModal}>&times;</span>
            <h2>{selectedModel.title}</h2>
            <select className="device-dropdown" value={selectedDevice} onChange={handleDeviceChange}>
              {devices.map(device => (
                <option key={device.device_id} value={device.device_id}>
                  {device.device_name} ({device.operating_system})
                </option>
              ))}
            </select>
            {metrics && (
              <div className="metrics-display">
                <div className="device-info">
                  {/* Use default image if no match found */}
                  <img
                    src={
                      deviceImages[devices.find(device => String(device.device_id) === selectedDevice)?.device_name] ||
                      DEFAULT_DEVICE_IMAGE
                    }
                    alt={devices.find(device => String(device.device_id) === selectedDevice)?.device_name || 'Device'}
                    className="device-image"
                  />
                  <div className="device-details">
                    <h3>{devices.find(device => String(device.device_id) === selectedDevice)?.device_name || DEFAULT_DEVICE_NAME}</h3>
                    <p>{metrics.device_description}</p>
                  </div>

                </div>
                <div className="metrics-values">
                  <div className="metric-box">
                    <span className="metric-value">{metrics.mAP === 0 ? 'N/A' : metrics.mAP}</span>
                    <span className="metric-label">mAP</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-value">{metrics.AP_small === 0 ? 'N/A' : metrics.AP_small}</span>
                    <span className="metric-label">AP Small</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-value">{metrics.AP_medium === 0 ? 'N/A' : metrics.AP_medium}</span>
                    <span className="metric-label">AP Medium</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-value">{metrics.AP_large === 0 ? 'N/A' : metrics.AP_large}</span>
                    <span className="metric-label">AP Large</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-value">{metrics.inference_time === 0 ? 'N/A' : `${metrics.inference_time} ms`}</span>
                    <span className="metric-label">Inference Time</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-value">{metrics.memory_usage === 0 ? 'N/A' : `${metrics.memory_usage} MB`}</span>
                    <span className="metric-label">Peak Memory Usage</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-value">{metrics.min_memory === 0 ? 'N/A' : `${metrics.min_memory} MB`}</span>
                    <span className="metric-label">Min Memory Usage</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-value">{metrics.compute_units_npu === 0 ? 'N/A' : `${metrics.compute_units_npu} NPU`}</span>
                    <span className="metric-label">Layers</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-value">{metrics.compute_units_cpu === 0 ? 'N/A' : `${metrics.compute_units_cpu} CPU`}</span>
                    <span className="metric-label">Compute Units</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-value">{metrics.compute_units_gpu === 0 ? 'N/A' : `${metrics.compute_units_gpu} GPU`}</span>
                    <span className="metric-label">Pipeline Stages</span>
                  </div>
                </div>
                <button className="see-more-metrics" onClick={handleTryOnAIHub}>Try on AI Hub</button>
              </div>
            )}
            {error && <p className="error-message">{error}</p>}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="footer_group">
        <div className="footer-content_group">
          <hr className="footer-line_group" />
          <div className="footer-logos_group">
            <a href="https://www.csusm.edu/" target="_blank" rel="noopener noreferrer">
              <img src={csusmLogo} alt="CSUSM Logo" className="footer-logo_group" />
            </a>
            <a href="https://aihub.qualcomm.com/" target="_blank" rel="noopener noreferrer">
              <img src={qualcommLogo} alt="Qualcomm AI Hub Logo" className="footer-logo_group" />
            </a>
          </div>
          <p>© 2025 Qual Bench AI. All rights reserved. Terms & Conditions Privacy & Policy</p>
        </div>
      </div>
    </div>
  );
}

export default Explore;
