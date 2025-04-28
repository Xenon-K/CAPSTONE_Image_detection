import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Chart from 'chart.js/auto';
import './DetailedComparison.css';
import csusmLogo from './csusm-logo.png';
import qualcommLogo from './qualcomm-ai-hub-logo.png';

const API_BASE_URL = 'https://qualbenchai-backend-production.up.railway.app'; // Replace with your actual Railway backend URL

const DetailedComparisonPage = () => {
  // State for devices, model data and selections.
  const [devices, setDevices] = useState([]);
  const [modelData, setModelData] = useState({}); // Fetched from backend for a device
  const [selectedDevice, setSelectedDevice] = useState('');
  const [selectedModels, setSelectedModels] = useState({
    model1: '',
    model2: '',
  });
  const [charts, setCharts] = useState([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  // Categories for the metrics.  Added AP metrics.
  const categories = [
    'mAP',
    'Inference Time (ms)',
    'Peak Memory Usage (MB)',
    'Min Memory Usage (MB)',
    'Compute Units (NPU)',
    'Compute Units (CPU)',
    'Compute Units (GPU)',
    'AP Small',
    'AP Medium',
    'AP Large'
  ];
  // Define if a higher value is better.
  const isBiggerBetter = [true, false, false, false, false, false, false, true, true, true];
  // Maximum values for the y-axis of each chart. Added to yAxisMax
  const yAxisMax = [1, null, null, null, null, null, null, 1, 1, 1];

    // Fetch devices from the backend on component mount.
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
            } catch (error) {
                console.error("Failed to fetch devices:", error);
                //  setError('Failed to fetch devices. Please check your network connection and backend server.'); //You can set an error message.
            }
        };
        fetchDevices();
    }, []);

    // Fetch model data for the selected device whenever selectedDevice changes.
    useEffect(() => {
        const fetchModelData = async () => {
            if (!selectedDevice) return;
            try {
                const response = await fetch(`${API_BASE_URL}/api/modeldata?device_id=${selectedDevice}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                const modelDataFromServer = data.data || {};
                setModelData(modelDataFromServer);

                const models = Object.keys(modelDataFromServer);
                if (models.length > 0) {
                    setSelectedModels(prev => ({
                        model1: models.includes(prev.model1) ? prev.model1 : models[0],
                        model2: models.includes(prev.model2) ? prev.model2 : models[0],
                    }));
                } else {
                    setSelectedModels({ model1: '', model2: '' });
                }
            } catch (error) {
                console.error("Failed to fetch model data:", error);
                //  setError('Failed to fetch model data. Please check your network connection and backend server.');
            }
        };
        fetchModelData();
    }, [selectedDevice]);

/*
// Fetch devices from the backend on component mount.
  useEffect(() => {
    fetch('http://172.25.133.11:5000/api/devices')
      .then((res) => res.json())
      .then((data) => {
        setDevices(data);
        if (data.length > 0) {
          // Use device_id from the backend.
          setSelectedDevice(data[0].device_id);
        }
      })
      .catch((err) => console.error(err));
  }, []);

  // Fetch model data for the selected device whenever selectedDevice changes.
  useEffect(() => {
    if (selectedDevice) {
      fetch(`http://172.25.133.11:5000/api/modeldata?device_id=${selectedDevice}`)
        .then((res) => res.json())
        .then((data) => {
          // Ensure data.data is not undefined before setting state
          const modelDataFromServer = data.data || {};
          setModelData(modelDataFromServer);

          const models = Object.keys(modelDataFromServer);
          if (models.length > 0) {
            setSelectedModels((prev) => ({
              model1: models.includes(prev.model1) ? prev.model1 : models[0],
              model2: models.includes(prev.model2) ? prev.model2 : models[0],
            }));
          } else {
            setSelectedModels({ model1: '', model2: '' });
          }
        })
        .catch((err) => console.error(err));
    }
  }, [selectedDevice]);
  */

  // Helper to get model metrics for the currently selected device.
  // If data is missing, return an array of zeros.  Adjusted to return 7 zeros.
// Helper to get model metrics for the currently selected device.
  // If data is missing, return an array of zeros.  Adjusted to return 7 zeros.
  const getModelMetrics = (modelName) => {
    const metrics = modelData[modelName];
    return metrics ? [
      metrics.mAP || 'N/A', // Changed to 'N/A' if 0
      metrics.inference_time || 'N/A',
      metrics.memory_usage || 'N/A',
      metrics.min_memory || 'N/A',
      metrics.compute_units_npu || 'N/A',
      metrics.compute_units_cpu || 'N/A',
      metrics.compute_units_gpu || 'N/A',
      metrics.AP_small || 'N/A', // AP Small
      metrics.AP_medium || 'N/A', // AP Medium
      metrics.AP_large || 'N/A'  // AP Large
    ] : ['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'];
  };

  // Create and initialize the charts.
  const createCharts = () => {
    const chartsContainer = document.getElementById('chartsContainer');
    chartsContainer.innerHTML = ''; // Clear any existing charts
    const chartInstances = [];

    categories.forEach((category, index) => {
      const chartDiv = document.createElement('div');
      chartDiv.className = 'chart-container';
      if (index >= 4) { // Apply 'centered-chart' class to AP Small, Medium, Large charts.
        chartDiv.classList.add('centered-chart');
      }
      chartDiv.innerHTML = `<canvas id="chart${index}"></canvas>`;
      chartsContainer.appendChild(chartDiv);

      const ctx = document.getElementById(`chart${index}`).getContext('2d');
      const chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: [selectedModels.model1, selectedModels.model2],
          datasets: [{
            label: category,
            data: [0, 0], // Data will be updated shortly.
            backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(255, 99, 132, 0.6)'],
            borderColor: ['rgb(75, 192, 192)', 'rgb(255, 99, 132)'],
            borderWidth: 1,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              ticks: {
                maxRotation: 0,
                minRotation: 0,
                font: {
                  size: 10,
                },
              },
            },
            y: {
              beginAtZero: true,
              max: yAxisMax[index],
              title: {
                display: true,
                text: category,
              },
            },
          },
        },
      });
      chartInstances.push(chartInstance);
    });
    setCharts(chartInstances);
    updateCharts(chartInstances, selectedModels);
  };

  // Update chart datasets and numerical detail rows.
  const updateCharts = (chartInstances = charts, models = selectedModels) => {
    const metrics1 = getModelMetrics(models.model1);
    const metrics2 = getModelMetrics(models.model2);

    chartInstances.forEach((chart, chartIndex) => {
      chart.data.labels = [models.model1, models.model2];
      chart.data.datasets[0].data = [metrics1[chartIndex], metrics2[chartIndex]];
      chart.update();
    });
    updateDetailRows(models, metrics1, metrics2);
    updateAverageScore(models, metrics1, metrics2);
  };

  const updateDetailRows = (models, metrics1, metrics2) => {
    categories.forEach((cat, i) => {
      const leftEl = document.getElementById(`valLeft_${i}`);
      const rightEl = document.getElementById(`valRight_${i}`);
      const diffTextEl = document.getElementById(`diffText_${i}`);

      leftEl.textContent = metrics1[i] === 'N/A' ? 'N/A' : metrics1[i];
      rightEl.textContent = metrics2[i] === 'N/A' ? 'N/A' : metrics2[i];

      // Check for 'N/A' values to avoid incorrect percentage calculations
      if (metrics1[i] === 'N/A' || metrics2[i] === 'N/A') {
        diffTextEl.textContent = 'N/A';
      } else {
        const diff = computeDifference(i, metrics1[i], metrics2[i]);
        diffTextEl.textContent = formatDiff(diff);
      }
    });
  };

  const computeDifference = (i, val1, val2) => {
    // Avoid division by zero.
    if (val1 === 0) return 0;
    return isBiggerBetter[i] ? ((val2 - val1) / val1) * 100 : ((val1 - val2) / val1) * 100;
  };

  const formatDiff = (diff) => {
    const absVal = Math.abs(diff).toFixed(1);
    if (diff > 0) {
      return `+${absVal}%`;
    } else if (diff < 0) {
      return `-${absVal}%`;
    } else {
      return `0.0%`;
    }
  };

  const updateAverageScore = (models, metrics1, metrics2) => {
    let sum = 0;
    let count = 0; // Count of categories with non-zero values

    categories.forEach((cat, i) => {
      // Check for 'N/A' values to exclude from average calculation
      if (metrics1[i] !== 'N/A' && metrics2[i] !== 'N/A') {
        const diff = computeDifference(i, metrics1[i], metrics2[i]);
        sum += diff;
        count++;
      }
    });

    const avgScoreEl = document.getElementById('averageScoreValue');
    if (count > 0) {
      const avgDiff = sum / count;
      const avgText = formatDiff(avgDiff);
      avgScoreEl.textContent = `${avgText} (${models.model2})`;
      avgScoreEl.style.color = avgDiff > 0 ? '#4caf50' : avgDiff < 0 ? '#f44336' : '#fff';
    } else {
      avgScoreEl.textContent = 'N/A';
      avgScoreEl.style.color = '#fff';
    }
  };

  const destroyCharts = () => {
    charts.forEach((chart) => {
      chart.destroy();
    });
    setCharts([]);
  };

  // Initialize charts once when the component mounts.
  useEffect(() => {
    if (!isInitialized) {
      createCharts();
      setIsInitialized(true);
    }
    return () => {
      destroyCharts();
    };
  }, []);

  // Update charts whenever selectedModels, selectedDevice, or modelData change.
  useEffect(() => {
    if (isInitialized) {
      updateCharts();
    }
  }, [selectedModels, selectedDevice, modelData]);
/*
  useEffect(() => {
    const exploreNowLink = document.querySelector('.cta-button');
    const handleClick = (event) => {
      event.preventDefault();
      window.open('https://aihub.qualcomm.com/models?domain=Computer+Vision&useCase=Object+Detection', '_blank');
    };

    if (exploreNowLink) {
      exploreNowLink.addEventListener('click', handleClick);
    }

    // Cleanup to remove the event listener on unmount
    return () => {
      if (exploreNowLink) {
        exploreNowLink.removeEventListener('click', handleClick);
      }
    };
  }, []); // The empty dependency array ensures this runs only once on mount
*/
  const getModelLink = (modelName) => {
    const modelInfo = modelData[modelName];
    return modelInfo ? modelInfo.website_url : null; // Assuming link is at index 4
  };

  const getArticleLink = (modelName) => {
    const modelInfo = modelData[modelName];
    return modelInfo ? modelInfo.article_url : null; // Assuming article link is at index 5
  };

  //<Link to="/explore-now" className="cta-button">Explore Now</Link>

  return (
    <div>
      <div className="container">
      <div className="header">
        <div className="mobile-menu-icon" onClick={toggleMobileMenu}>
          {isMobileMenuOpen ? '✕' : '☰'}
        </div>
        <Link to="/" className="logo">Qual Bench AI</Link>
        <div className={`nav-links ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
          <Link to="/model-comparison" onClick={() => setIsMobileMenuOpen(false)}>Model Comparisons</Link>
          <Link to="/detailed-comparison" onClick={() => setIsMobileMenuOpen(false)}><u>Detailed Comparison</u></Link>
          <Link to="/methodology" onClick={() => setIsMobileMenuOpen(false)}>Methodology</Link>
          <Link to="/explore-now" onClick={() => setIsMobileMenuOpen(false)}>Explore Models</Link>
        </div>
        <div className="desktop-spacer"></div>
      </div>

        {/* Device Dropdown */}
        <div className="device-selection">
          <label htmlFor="DeviceSelect">Select Device: </label>
          <select
            id="DeviceSelect"
            value={selectedDevice}
            onChange={(e) => setSelectedDevice(e.target.value)}
          >
            {devices.map((device) => (
              <option key={device.device_id} value={device.device_id}>
                {device.device_name}
              </option>
            ))}
          </select>
        </div>

        {/* Model Selection Dropdowns */}
        <div className="model-selection">
          <select
            id="Model1"
            value={selectedModels.model1}
            onChange={(e) =>
              setSelectedModels({ ...selectedModels, model1: e.target.value })
            }
          >
            {Object.keys(modelData).length > 0 ? (
              Object.keys(modelData).map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))
            ) : (
              <option value="">No Models Available</option>
            )}
          </select>
          <select
            id="Model2"
            value={selectedModels.model2}
            onChange={(e) =>
              setSelectedModels({ ...selectedModels, model2: e.target.value })
            }
          >
            {Object.keys(modelData).length > 0 ? (
              Object.keys(modelData).map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))
            ) : (
              <option value="">No Models Available</option>
            )}
          </select>
        </div>

        {/* Charts Container */}
        <div id="chartsContainer"></div>
      </div>

      {/* Model Links Buttons */}
      <div className="model-links-container">
        <div className="model-links-group">
          <p className="button-title">Try on Qualcomm AI Hub</p>
          {selectedModels.model1 && (
            <a
              href={getModelLink(selectedModels.model1)} // Correctly using getModelLink
              target="_blank"
              rel="noopener noreferrer"
              className="model-link-button"
            >
              {selectedModels.model1}
            </a>
          )}
          {selectedModels.model2 && (
            <a
              href={getModelLink(selectedModels.model2)} // Correctly using getModelLink
              target="_blank"
              rel="noopener noreferrer"
              className="model-link-button"
            >
              {selectedModels.model2}
            </a>
          )}
        </div>
        <div className="article-links-group">
          <p className="button-title">CheckOut PaperWithCode</p>
          {selectedModels.model1 && (
            <a
              href={getArticleLink(selectedModels.model1)} // **Corrected to use getArticleLink**
              target="_blank"
              rel="noopener noreferrer"
              className="model-link-button"
            >
              {selectedModels.model1}
            </a>
          )}
          {selectedModels.model2 && (
            <a
              href={getArticleLink(selectedModels.model2)} // **Corrected to use getArticleLink**
              target="_blank"
              rel="noopener noreferrer"
              className="model-link-button"
            >
              {selectedModels.model2}
            </a>
          )}
        </div>
      </div>

      {/* Numerical Comparison Table */}
      <div className="container-detailed">
        <div id="detailsSection">
          <div className="average-score-row">
            <div>Average Score</div>
            <div id="averageScoreValue" className="score-diff">+0%</div>
          </div>
          <div id="detailRows">
            {categories.map((category, index) => (
              <div key={index} className="detail-row">
                <div className="left-col">
                  <div className="category-name">{category}</div>
                  <div id={`valLeft_${index}`}></div>
                </div>
                <div className="right-col">
                  <div id={`diffText_${index}`} className="diff-text"></div>
                  <div id={`valRight_${index}`}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
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
};

export default DetailedComparisonPage;
