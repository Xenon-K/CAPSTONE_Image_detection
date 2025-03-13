import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import Chart from 'chart.js/auto';
import "./ModelComparison.css"; 
import csusmLogo from './csusm-logo.png'; // Import the CSUSM logo
import qualcommLogo from './qualcomm-ai-hub-logo.png'; // Import the Qualcomm AI Hub logo


const ModelComparison = () => {
    const chartRef = useRef(null);
    const chartInstanceRef = useRef(null);
    const [devices, setDevices] = useState([]);
    const [selectedDevice, setSelectedDevice] = useState('');
    const [selectedMetric, setSelectedMetric] = useState('runtime');
    const [selectedSortOrder, setSelectedSortOrder] = useState('default');
    const [chartData, setChartData] = useState({ labels: [], values: [] });

    // Fetch available devices on mount
    useEffect(() => {
        fetch('your_link/api/devices')
            .then(res => res.json())
            .then(data => {
                setDevices(data);
                if (data.length > 0) {
                    setSelectedDevice(data[0].device_id);
                }
            })
            .catch(err => console.error(err));
    }, []);

    // Fetch metric data whenever the selected device, metric or sort order changes
    useEffect(() => {
        if (selectedDevice && selectedMetric) {
            fetch(`your_link/api/metrics?device_id=${selectedDevice}&metric=${selectedMetric}&sort_order=${selectedSortOrder}`)
                .then(res => res.json())
                .then(data => {
                    setChartData(data);
                })
                .catch(err => console.error(err));
        }
    }, [selectedDevice, selectedMetric, selectedSortOrder]);

    // Update the chart when new chartData is received
    useEffect(() => {
        if (chartRef.current) {
            if (chartInstanceRef.current) {
                chartInstanceRef.current.destroy();
            }
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
                                maxRotation: 0,
                                minRotation: 0,
                                font: {
                                    size: function(context) {
                                        const numLabels = context.chart.data.labels.length;
                                        const screenWidth = window.innerWidth;
    
                                        let fontSize = 12;
                                        if (screenWidth < 768) {
                                            fontSize = 8;
                                        }
                                        if (numLabels > 5) {
                                            fontSize -= 2;
                                        }
                                        if (numLabels > 10) {
                                            fontSize -= 2;
                                        }
                                        return fontSize;
                                    }
                                }
                            }
                        },
                      y: {
                        beginAtZero: true
                      }
                    }
                  }
                });
              }
              return () => {
                if (chartInstanceRef.current) {
                  chartInstanceRef.current.destroy();
                }
              };
            }, [chartData]);

    const handleDeviceChange = (e) => {
        setSelectedDevice(e.target.value);
    };

    const handleMetricChange = (e) => {
        setSelectedMetric(e.target.value);
    };

    const handleSortChange = (e) => {
        setSelectedSortOrder(e.target.value);
    };
    
    useEffect(() => {
        const exploreNowLink = document.querySelector('.cta-button');
        if (exploreNowLink) {
          exploreNowLink.addEventListener('click', (event) => {
            event.preventDefault();
            window.open('https://aihub.qualcomm.com/models?domain=Computer+Vision&useCase=Object+Detection', '_blank');
          });
        }
      },);

    return (
        <div className="container">
            {/* Header */}
            <div className="header">
                <Link to="/" className="logo">Qual Bench AI</Link>
                <div className="nav-links">
                    <Link to="/model-comparison">Model Comparisons</Link>
                </div>
                <a href="https://aihub.qualcomm.com/models?domain=Computer+Vision&useCase=Object+Detection" className="cta-button">
                    Explore Now
                </a>
            </div>

            {/* Dropdown Section */}
            <div className="main-section-chart">
                {/* Device Dropdown */}
                <select className="dropdown" value={selectedDevice} onChange={handleDeviceChange}>
                    {devices.map(device => (
                        <option key={device.device_id} value={device.device_id}>
                            {device.device_name} ({device.operating_system})
                        </option>
                    ))}
                </select>

                {/* Metric Dropdown */}
                <select className="dropdown" value={selectedMetric} onChange={handleMetricChange}>
                    <option value="runtime">Runtime (s)</option>
                    <option value="inference_time">Inference Time (ms)</option>
                    <option value="mAP">mAP</option>
                    <option value="memory_usage">Memory Usage (MB)</option>
                    <option value="compute_units">Compute Units</option>
                </select>

                {/* Sort Order Dropdown */}
                <select className="dropdown" value={selectedSortOrder} onChange={handleSortChange}>
                    <option value="default">Default Order</option>
                    <option value="asc">Smallest to Largest</option>
                    <option value="desc">Largest to Smallest</option>
                </select>

                <Link to="/detailed-comparison">
                    <button id="detailedComparison" className="compare-button">Detailed Comparison</button>
                </Link>
            </div>

            {/* Chart Container */}
            <div id="chartContainer">
                <canvas ref={chartRef}></canvas>
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

export default ModelComparison;
