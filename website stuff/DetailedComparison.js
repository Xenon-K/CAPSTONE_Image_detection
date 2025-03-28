import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import Chart from 'chart.js/auto';
import './DetailedComparison.css';
import csusmLogo from './csusm-logo.png';
import qualcommLogo from './qualcomm-ai-hub-logo.png';

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

  // Categories for the metrics.  Added AP metrics.
  const categories = [
    'mAP',
    'Inference Time (ms)',
    'Memory Usage (MB)',
    'Compute Units (NPU)',
    'AP Small',
    'AP Medium',
    'AP Large'
  ];
  // Define if a higher value is better.  Added to isBiggerBetter
  const isBiggerBetter = [true, false, false, true, true, true, true];
  // Maximum values for the y-axis of each chart. Added to yAxisMax
  const yAxisMax = [1, null, null, null, 1, 1, 1];

  // Fetch devices from the backend on component mount.
  useEffect(() => {
    fetch('http://192.168.0.181:5000/api/devices')
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
      fetch(`http://192.168.0.181:5000/api/modeldata?device_id=${selectedDevice}`)
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

  // Helper to get model metrics for the currently selected device.
  // If data is missing, return an array of zeros.  Adjusted to return 7 zeros.
  const getModelMetrics = (modelName) => {
    const metrics = modelData[modelName];
    return metrics ? [
      metrics[0] || 0,
      metrics[1] || 0,
      metrics[2] || 0,
      metrics[3] || 0,
      metrics[6] || 0, // AP Small
      metrics[7] || 0, // AP Medium
      metrics[8] || 0  // AP Large
    ] : [0, 0, 0, 0, 0, 0, 0];
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
      if (leftEl) leftEl.textContent = `${metrics1[i]}`;
      if (rightEl) rightEl.textContent = `${metrics2[i]}`;

      const diffTextEl = document.getElementById(`diffText_${i}`);
      // If either model is missing data, display "missing data"
      if (!modelData[models.model1] || !modelData[models.model2]) {
        if (diffTextEl) diffTextEl.textContent = 'missing data';
      } else {
        const diff = computeDifference(i, metrics1[i], metrics2[i]);
        if (diffTextEl) diffTextEl.textContent = formatDiff(diff);
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
    if (!modelData[models.model1] || !modelData[models.model2]) {
      const avgScoreEl = document.getElementById('averageScoreValue');
      if (avgScoreEl) {
        avgScoreEl.textContent = 'missing data';
        avgScoreEl.style.color = '#fff';
      }
      return;
    }
    let sum = 0;
    categories.forEach((cat, i) => {
      const diff = computeDifference(i, metrics1[i], metrics2[i]);
      sum += diff;
    });
    const avgDiff = sum / categories.length;
    const avgText = formatDiff(avgDiff);
    const avgScoreEl = document.getElementById('averageScoreValue');
    if (avgScoreEl) {
      avgScoreEl.textContent = avgText;
      avgScoreEl.style.color = avgDiff > 0 ? '#4caf50' : avgDiff < 0 ? '#f44336' : '#fff';
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

  const getModelLink = (modelName) => {
    const modelInfo = modelData[modelName];
    return modelInfo ? modelInfo[4] : null; // Assuming link is at index 4
  };

  const getArticleLink = (modelName) => {
    const modelInfo = modelData[modelName];
    return modelInfo ? modelInfo[5] : null; // Assuming article link is at index 5
  };

  return (
    <div>
      <div className="container">
        {/* Header */}
        <div className="header">
          <Link to="/" className="logo">Qual Bench AI</Link>
          <div className="nav-links">
            <Link to="/model-comparison">Model Comparisons</Link>
            <Link to="/detailed-comparison">Detailed Comparison</Link>
          </div>
          <a
            href="https://aihub.qualcomm.com/models?domain=Computer+Vision&useCase=Object+Detection"
            className="cta-button"
          >
            Explore Now
          </a>
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
              href={getModelLink(selectedModels.model1)} // Use anchor tag
              target="_blank"
              rel="noopener noreferrer"
              className="model-link-button" // Keep the class for styling
            >
              {selectedModels.model1}
            </a>
          )}
          {selectedModels.model2 && (
            <a
              href={getModelLink(selectedModels.model2)}  // Use anchor tag
              target="_blank"
              rel="noopener noreferrer"
              className="model-link-button" // Keep the class for styling
            >
              {selectedModels.model2}
            </a>
          )}
        </div>
        <div className="article-links-group">
          <p className="button-title">CheckOut PaperWithCode</p>
          {selectedModels.model1 && (
            <a
              href={getModelLink(selectedModels.model1)} // Use anchor tag
              target="_blank"
              rel="noopener noreferrer"
              className="model-link-button"  // Keep the class for styling
            >
              {selectedModels.model1}
            </a>
          )}
          {selectedModels.model2 && (
            <a
              href={getModelLink(selectedModels.model2)} // Use anchor tag.
              target="_blank"
              rel="noopener noreferrer"
              className="model-link-button"  // Keep the class for styling
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

