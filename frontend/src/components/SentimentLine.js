import React from 'react';
import { Chart } from 'react-google-charts';

const SentimentLine = ({ trend }) => {
  // Format trend data for chart
  const formatTrendData = () => {
    if (!trend || trend.length === 0) {
      return [
        ['Date', 'Positive', 'Negative', 'Neutral'],
        ['No Data', 0, 0, 0]
      ];
    }

    const data = [['Date', 'Positive', 'Negative', 'Neutral']];
    
    // Sort trend data by date
    const sortedTrend = [...trend].sort((a, b) => 
      new Date(a.date) - new Date(b.date)
    );

    sortedTrend.forEach(item => {
      const date = new Date(item.date);
      const formattedDate = date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      });
      
      data.push([
        formattedDate,
        item.positive || 0,
        item.negative || 0,
        item.neutral || 0,
      ]);
    });

    return data;
  };

  const options = {
    title: 'Sentiment Trend Over Time',
    curveType: 'function',
    width: '100%',
    height: 400,
    legend: { position: 'bottom' },
    hAxis: {
      title: 'Date',
      gridlines: { count: 10 },
    },
    vAxis: {
      title: 'Number of Reviews',
      minValue: 0,
      gridlines: { count: 5 },
    },
    colors: ['#4CAF50', '#FF5252', '#FFC107'],
    chartArea: { width: '85%', height: '75%' },
    series: {
      0: { lineWidth: 3 },
      1: { lineWidth: 3 },
      2: { lineWidth: 3 },
    },
  };

  return (
    <div className="chart-card">
      <div className="chart-header">
        <h3>Sentiment Timeline</h3>
        <p className="chart-subtitle">How sentiment has changed over time</p>
      </div>
      <Chart
        chartType="LineChart"
        data={formatTrendData()}
        options={options}
        width="100%"
        height="400px"
      />
    </div>
  );
};

export default SentimentLine;