// ChartLoader.js
import { useEffect } from 'react';

const ChartLoader = () => {
  useEffect(() => {
    // Load Google Charts API
    const script = document.createElement('script');
    script.src = 'https://www.gstatic.com/charts/loader.js';
    script.async = true;
    
    script.onload = () => {
      if (window.google && window.google.charts) {
        window.google.charts.load('current', {
          packages: ['corechart', 'line', 'bar']
        });
        console.log('Google Charts loaded successfully');
      }
    };
    
    document.head.appendChild(script);
    
    return () => {
      // Cleanup if needed
      document.head.removeChild(script);
    };
  }, []);
  
  return null; // This is a utility component, doesn't render anything
};

export default ChartLoader;