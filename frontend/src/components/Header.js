// src/components/Header.js
import React from 'react';
import { Link } from 'react-router-dom';
import ThemeToggle from './ThemeToggle';

const Header = ({ backendStatus }) => {
  return (
    <header className="header">
      <div className="header-container">
        <div className="logo">
          <Link to="/">
            <h1>Sentiment Analyzer</h1>
          </Link>
          <span className="tagline">AI-Powered Product Review Analysis</span>
        </div>
        
        <div className="header-right">
          <div className={`backend-status ${backendStatus}`}>
            {backendStatus === 'connected' ? '✅ Backend Connected' : 
             backendStatus === 'disconnected' ? '⚠️ Backend Offline' : 
             '⏳ Checking Connection'}
          </div>
          
          <nav className="nav-menu">
            <Link to="/" className="nav-link">Home</Link>
            <Link to="/analyze" className="nav-link">Analyze</Link>
            <Link to="/dashboard" className="nav-link">Dashboard</Link>
            <Link to="/settings" className="nav-link">Settings</Link>
          </nav>
          
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
};

export default Header;