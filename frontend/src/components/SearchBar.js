import React, { useState } from 'react';

const SearchBar = ({ onSearch, loading, placeholder }) => {
  const [input, setInput] = useState('');
  const [error, setError] = useState('');

  const validateInput = (value) => {
    if (!value.trim()) {
      setError('Please enter a product URL or name');
      return false;
    }
    
    // Check if it's a URL
    if (value.includes('http')) {
      try {
        new URL(value);
        if (!value.includes('amazon') && !value.includes('flipkart')) {
          setError('Please enter an Amazon or Flipkart URL');
          return false;
        }
      } catch {
        setError('Please enter a valid URL');
        return false;
      }
    }
    
    setError('');
    return true;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateInput(input) && !loading) {
      onSearch(input.trim());
    }
  };

  const handleExampleClick = (exampleUrl) => {
    setInput(exampleUrl);
    setError('');
    if (!loading) {
      onSearch(exampleUrl);
    }
  };

  const handleClear = () => {
    setInput('');
    setError('');
  };

  const examples = [
    { 
      label: 'Amazon Product', 
      url: 'https://www.amazon.com/dp/B0CHX7W4S6',
      description: 'Amazon product page'
    },
    { 
      label: 'Flipkart Product', 
      url: 'https://www.flipkart.com/apple-iphone-15-pro-max/p/itm92e9c62564334',
      description: 'Flipkart product page'
    },
    { 
      label: 'Search Term', 
      url: 'iPhone 15 Pro Max reviews',
      description: 'Product name search'
    }
  ];

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-wrapper">
          <input
            type="text"
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              setError('');
            }}
            placeholder={placeholder || "Enter Amazon/Flipkart URL or product name..."}
            disabled={loading}
            className={`search-input ${error ? 'error' : ''}`}
            aria-label="Product URL or name"
          />
          {input && (
            <button
              type="button"
              onClick={handleClear}
              className="clear-button"
              aria-label="Clear search"
            >
              ✕
            </button>
          )}
        </div>
        
        <button 
          type="submit" 
          disabled={!input.trim() || loading}
          className={`search-button ${loading ? 'loading' : ''}`}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Analyzing...
            </>
          ) : (
            '🔍 Analyze Sentiment'
          )}
        </button>
      </form>
      
      {error && (
        <div className="search-error">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}
      
      <div className="search-examples">
        <p className="examples-title">Try these examples:</p>
        <div className="example-grid">
          {examples.map((example, index) => (
            <button
              key={index}
              type="button"
              onClick={() => handleExampleClick(example.url)}
              disabled={loading}
              className="example-button"
              title={example.description}
            >
              <span className="example-icon">
                {example.label.includes('Amazon') ? '🛒' : 
                 example.label.includes('Flipkart') ? '📱' : '🔍'}
              </span>
              <span className="example-text">{example.label}</span>
            </button>
          ))}
        </div>
        
        <div className="search-tips">
          <h4>Tips:</h4>
          <ul>
            <li>Paste a full Amazon or Flipkart product URL</li>
            <li>Or type a product name for general sentiment analysis</li>
            <li>Make sure the product has reviews available</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SearchBar;