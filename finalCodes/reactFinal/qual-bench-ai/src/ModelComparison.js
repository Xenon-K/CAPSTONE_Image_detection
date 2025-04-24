import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import Chart from 'chart.js/auto';
//import '../styles.css'; // Keep styles in a separate CSS file

const ModelComparison = () => {
    useEffect(() => {
        const ctx = document.getElementById('comparisonChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Model 1', 'Model 2', 'Model 3', 'Model 4', 'Model 5'],
                datasets: [{
                    label: 'Comparison Data',
                    data: [12, 19, 3, 5, 2],
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgb(75, 192, 192)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true } }
            }
        });
    }, []);

    return (
        <div>
            <div className="header">
                <Link to="/" className="logo">Qual Bench AI</Link>
                <div className="nav-links">
                    <Link to="/model-comparison">Model Comparisons</Link>
                </div>
                <a href="https://aihub.qualcomm.com/models?domain=Computer+Vision&useCase=Object+Detection" className="cta-button">
                    Explore Now
                </a>
            </div>
            <div className="main-section">
                <select id="compareUnit">
                    <option value="unit1">Inference Time (ms)</option>
                    <option value="unit2">Unit 2</option>
                </select>
                <Link to="/one-on-one" className="cta-button">Detailed Comparison</Link>
            </div>
            <div id="chartContainer">
                <canvas id="comparisonChart"></canvas>
            </div>
        </div>
    );
};

export default ModelComparison;
