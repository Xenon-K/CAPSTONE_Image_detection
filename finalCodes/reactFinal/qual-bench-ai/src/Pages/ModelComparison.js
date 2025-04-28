import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import Chart from 'chart.js/auto';
import "./ModelComparison.css";
import csusmLogo from './csusm-logo.png';
import qualcommLogo from './qualcomm-ai-hub-logo.png';

const API_BASE_URL = 'https://qualbenchai-backend-production.up.railway.app'; // Replace with your actual Railway backend URL

const ModelComparison = () => {
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [selectedMetric, setSelectedMetric] = useState('inference_time');
  const [selectedSortOrder, setSelectedSortOrder] = useState('default');
  const [chartData, setChartData] = useState({ labels: [], values: [] });
  const [modelData, setModelData] = useState({});
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/devices`) // Use the API_BASE_URL
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
    if (selectedDevice) {
      fetch(`${API_BASE_URL}/api/metrics?device_id=${selectedDevice}&metric=${selectedMetric}&sort_order=${selectedSortOrder}`) // Use the API_BASE_URL
        .then(res => res.json())
        .then(data => {
          setChartData(data);
        })
        .catch(err => console.error(err));

      fetch(`${API_BASE_URL}/api/modeldata?device_id=${selectedDevice}`) // Use the API_BASE_URL
        .then(res => res.json())
        .then(data => {
          setModelData(data.data);
        })
        .catch(err => console.error(err));
    }
  }, [selectedDevice, selectedMetric, selectedSortOrder]);

  /*
  useEffect(() => {
    if (selectedDevice) {
      fetch(`http://172.25.133.11:5000/api/metrics?device_id=${selectedDevice}&metric=${selectedMetric}&sort_order=${selectedSortOrder}`)
        .then(res => res.json())
        .then(data => {
          setChartData(data);
        })
        .catch(err => console.error(err));

      fetch(`http://172.25.133.11:5000/api/modeldata?device_id=${selectedDevice}`)
        .then(res => res.json())
        .then(data => {
          setModelData(data.data);
        })
        .catch(err => console.error(err));
    }
  }, [selectedDevice, selectedMetric, selectedSortOrder]);
  */
 
  useEffect(() => {
    if (chartRef.current) {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }
      const yAxisMax = selectedMetric === 'mAP' ? 1 : undefined;
      chartInstanceRef.current = new Chart(chartRef.current, {
        type: 'bar',
        data: {
          labels: chartData.labels,
          datasets: [{
            label: 'Comparison Data',
            data: chartData.values,
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgb(75, 192, 192)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              ticks: {
                callback: function(value) {
                  const label = this.getLabelForValue(value);
                  const words = label.split(' ');
                  if (words.length > 2) {
                    return words.reduce((acc, word, index) => {
                      if (index > 0 && index % 2 === 0) {
                        return [...acc, '\n' + word];
                      }
                      return [...acc, word];
                    }, []).join(' ');
                  }
                  return label;
                },
                maxRotation: 45, // Rotate labels by 45 degrees
                minRotation: 45,
                font: {
                  size: 10, // Reduce font size
                },
              },
            },
            y: {
              beginAtZero: true,
              max: yAxisMax,
            },
          },
        },
      });
    }
    return () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }
    };
  }, [chartData, selectedMetric]);

  const handleDeviceChange = (e) => {
    setSelectedDevice(e.target.value);
  };

  const handleMetricChange = (e) => {
    setSelectedMetric(e.target.value);
  };

  const handleSortChange = (e) => {
    setSelectedSortOrder(e.target.value);
  };

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

    return () => {
      if (exploreNowLink) {
        exploreNowLink.removeEventListener('click', handleClick);
      }
    };
  }, []);
*/
  return (
    <div className="container">
      <div className="header">
        <div className="mobile-menu-icon" onClick={toggleMobileMenu}>
          {isMobileMenuOpen ? '✕' : '☰'}
        </div>
        <Link to="/" className="logo">Qual Bench AI</Link>
        <div className={`nav-links ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
          <Link to="/model-comparison" onClick={() => setIsMobileMenuOpen(false)}><u>Model Comparisons</u></Link>
          <Link to="/detailed-comparison" onClick={() => setIsMobileMenuOpen(false)}>Detailed Comparison</Link>
          <Link to="/methodology" onClick={() => setIsMobileMenuOpen(false)}>Methodology</Link>
          <Link to="/explore-now" onClick={() => setIsMobileMenuOpen(false)}>Explore Models</Link>
        </div>
        <div className="desktop-spacer"></div>
      </div>

      <div className="main-section-chart">
        <select className="dropdown" value={selectedDevice} onChange={handleDeviceChange}>
          {devices.map(device => (
            <option key={device.device_id} value={device.device_id}>
              {device.device_name} ({device.operating_system})
            </option>
          ))}
        </select>

        <select className="dropdown" value={selectedMetric} onChange={handleMetricChange}>
          <option value="inference_time">Inference Time (ms)</option>
          <option value="mAP">mAP</option>
          <option value="AP_50">AP 50</option>
          <option value="AP_75">AP 75</option>
          <option value="AP_small">AP Small</option>
          <option value="AP_medium">AP Medium</option>
          <option value="AP_large">AP Large</option>
          <option value="AR">AR</option>
          <option value="AR_50">AR 50</option>
          <option value="AR_75">AR 75</option>
          <option value="AR_small">AR Small</option>
          <option value="AR_medium">AR Medium</option>
          <option value="AR_large">AR Large</option>
          <option value="memory_usage">Memory Usage (MB)</option>
          <option value="min_memory">Minimum Memory Usage (MB)</option>
          <option value="compute_units_cpu">CPU Compute Units</option>
          <option value="compute_units_gpu">GPU Compute Units</option>
          <option value="compute_units_npu">NPU Compute Units</option>
        </select>


        <select className="dropdown" value={selectedSortOrder} onChange={handleSortChange}>
          <option value="default">Default Order</option>
          <option value="asc">Smallest to Largest</option>
          <option value="desc">Largest to Smallest</option>
        </select>
      </div>

      <div id="chartContainer">
        <canvas ref={chartRef}></canvas>
      </div>

      {/* Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Model</th>
              <th>mAP</th>
              <th>Inference Time (ms)</th>
              <th>Peak Memory Usage (MB)</th>
              <th>NPU Compute Units</th>
              <th>CPU Compute Units</th>
              <th>GPU Compute Units</th>
              <th>AP Small</th>
              <th>AP Medium</th>
              <th>AP Large</th>
              <th>Qualcomm AI Hub</th>
              <th>PaperWithCode</th>
            </tr>
          </thead>
          <tbody>
            {chartData.labels.map((label, index) => {
              const data = modelData[label];
              return (
                <tr key={label}>
                  <td>{label}</td>
                  <td>{data && data.mAP !== 0 ? data.mAP : 'N/A'}</td>
                  <td>{data && data.inference_time !== 0 ? data.inference_time : 'N/A'}</td>
                  <td>{data && data.memory_usage !== 0 ? data.memory_usage : 'N/A'}</td>
                  <td>{data && data.compute_units_npu !== 0 ? data.compute_units_npu : 'N/A'}</td>
                  <td>{data && data.compute_units_cpu !== 0 ? data.compute_units_cpu : 'N/A'}</td>
                  <td>{data && data.compute_units_gpu !== 0 ? data.compute_units_gpu : 'N/A'}</td>
                  <td>{data && data.AP_small !== 0 ? data.AP_small : 'N/A'}</td>
                  <td>{data && data.AP_medium !== 0 ? data.AP_medium : 'N/A'}</td>
                  <td>{data && data.AP_large !== 0 ? data.AP_large : 'N/A'}</td>
                  <td>
                    {data && data.website_url ? (
                      <button onClick={() => window.open(data.website_url, '_blank')}>AI Hub</button>
                    ) : (
                      'N/A'
                    )}
                  </td>
                  <td>
                    {data && data.article_url ? (
                      <button onClick={() => window.open(data.article_url, '_blank')}>PaperWithCode</button>
                    ) : (
                      'N/A'
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

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

export default ModelComparison;
