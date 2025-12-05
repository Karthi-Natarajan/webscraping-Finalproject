import React from 'react';
import { Chart } from 'react-google-charts';

const SentimentPie = ({ counts }) => {
  const data = [
    ['Sentiment', 'Count'],
    ['Positive', counts?.positive || 0],
    ['Negative', counts?.negative || 0],
    ['Neutral', counts?.neutral || 0],
  ];

  const options = {
    title: 'Sentiment Distribution',
    width: '100%',
    height: 400,
    pieHole: 0.4,
    colors: ['#4CAF50', '#FF5252', '#FFC107'],
    chartArea: { width: '90%', height: '80%' },
    legend: { 
      position: 'bottom', 
      alignment: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: { 
      isHtml: true,
      text: 'value'
    },
  };

  return (
    <div className="chart-card">
      <div className="chart-header">
        <h3>Sentiment Breakdown</h3>
        <div className="sentiment-stats">
          <span className="stat positive">Positive: {counts?.positive || 0}</span>
          <span className="stat negative">Negative: {counts?.negative || 0}</span>
          <span className="stat neutral">Neutral: {counts?.neutral || 0}</span>
        </div>
      </div>
      <Chart
        chartType="PieChart"
        data={data}
        options={options}
        width="100%"
        height="400px"
      />
    </div>
  );
};

export default SentimentPie;