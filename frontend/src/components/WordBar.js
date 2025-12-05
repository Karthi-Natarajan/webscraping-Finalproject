import React from 'react';
import { Chart } from 'react-google-charts';

const WordBar = ({ words }) => {
  // Format word data for horizontal bar chart
  const formatWordData = () => {
    if (!words || Object.keys(words).length === 0) {
      return [
        ['Word', 'Frequency', { role: 'style' }],
        ['No Data', 0, '#2196F3']
      ];
    }

    // Convert to array and sort by frequency
    const wordArray = Object.entries(words)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10); // Top 10 words

    const data = [['Word', 'Frequency', { role: 'style' }]];
    
    // Color based on frequency
    const maxFrequency = Math.max(...wordArray.map(([, freq]) => freq));
    
    wordArray.forEach(([word, frequency]) => {
      // Calculate color intensity based on frequency
      const intensity = Math.floor((frequency / maxFrequency) * 100) + 155;
      const color = `rgb(33, 150, ${intensity})`;
      
      data.push([word, frequency, color]);
    });

    return data;
  };

  const options = {
    title: 'Most Frequent Words',
    width: '100%',
    height: 400,
    hAxis: {
      title: 'Frequency',
      minValue: 0,
      gridlines: { count: 5 },
    },
    vAxis: {
      title: 'Words',
    },
    chartArea: { width: '80%', height: '80%' },
    bars: 'horizontal',
    legend: { position: 'none' },
    backgroundColor: 'transparent',
    animation: {
      startup: true,
      duration: 1000,
      easing: 'out',
    },
  };

  const wordData = formatWordData();

  return (
    <div className="chart-card">
      <div className="chart-header">
        <h3>Keyword Analysis</h3>
        <p className="chart-subtitle">Most frequently mentioned words in reviews</p>
      </div>
      <Chart
        chartType="BarChart"
        data={wordData}
        options={options}
        width="100%"
        height="400px"
      />
      <div className="word-cloud-info">
        {wordData.length > 1 && (
          <div className="top-words-list">
            <h4>Top Words:</h4>
            <div className="words-tags">
              {wordData.slice(1, 6).map(([word, frequency], index) => (
                <span key={index} className="word-tag">
                  {word} ({frequency})
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WordBar;