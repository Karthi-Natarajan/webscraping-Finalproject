// chart.config.js
import { Chart } from 'react-google-charts';

// Google Charts configuration
export const sentimentChartOptions = {
  title: 'Sentiment Distribution',
  width: 500,
  height: 400,
  pieHole: 0.4,
  colors: ['#4CAF50', '#FF5252', '#FFC107'],
  chartArea: { width: '90%', height: '80%' },
  legend: { 
    position: 'bottom', 
    alignment: 'center',
    textStyle: { fontSize: 14 }
  },
  tooltip: { isHtml: true },
};

export const trendChartOptions = {
  title: 'Sentiment Trend Over Time',
  curveType: 'function',
  width: 700,
  height: 400,
  legend: { position: 'bottom' },
  hAxis: {
    title: 'Date',
    format: 'MMM d',
    gridlines: { count: 10 },
  },
  vAxis: {
    title: 'Reviews Count',
    minValue: 0,
    gridlines: { count: 5 },
  },
  colors: ['#4CAF50', '#FF5252', '#FFC107'],
  chartArea: { width: '85%', height: '75%' },
};

export const wordChartOptions = {
  title: 'Top Keywords',
  width: 600,
  height: 400,
  hAxis: {
    title: 'Frequency',
    minValue: 0,
  },
  vAxis: {
    title: 'Words',
  },
  chartArea: { width: '80%', height: '80%' },
  colors: ['#2196F3'],
  bars: 'horizontal',
  legend: { position: 'none' },
};

// Helper function to format sentiment data for charts
export const formatSentimentData = (counts) => {
  return [
    ['Sentiment', 'Count'],
    ['Positive', counts?.positive || 0],
    ['Negative', counts?.negative || 0],
    ['Neutral', counts?.neutral || 0],
  ];
};

// Helper function to format trend data
export const formatTrendData = (trendData) => {
  if (!trendData || trendData.length === 0) {
    return [
      ['Date', 'Positive', 'Negative', 'Neutral'],
      ['No Data', 0, 0, 0]
    ];
  }

  const data = [['Date', 'Positive', 'Negative', 'Neutral']];
  trendData.forEach(item => {
    data.push([
      new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      item.positive || 0,
      item.negative || 0,
      item.neutral || 0,
    ]);
  });
  return data;
};

// Helper function to format word frequency data
export const formatWordData = (words) => {
  if (!words || Object.keys(words).length === 0) {
    return [['Word', 'Frequency']];
  }

  const data = [['Word', 'Frequency']];
  Object.entries(words)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)
    .forEach(([word, count]) => {
      data.push([word, count]);
    });
  return data;
};

// Reusable Chart Component
export const GoogleChart = ({ chartType, data, options, width, height }) => {
  return (
    <Chart
      chartType={chartType}
      data={data}
      options={options}
      width={width || '100%'}
      height={height || '400px'}
    />
  );
};

export default {
  sentimentChartOptions,
  trendChartOptions,
  wordChartOptions,
  formatSentimentData,
  formatTrendData,
  formatWordData,
  GoogleChart
};