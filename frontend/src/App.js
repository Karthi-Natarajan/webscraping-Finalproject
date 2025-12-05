import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Components
import ChartLoader from './components/ChartLoader';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import ProductPage from './pages/ProductPage';

// Services
import { testConnection } from './api';

function App() {
  const [backendStatus, setBackendStatus] = useState('checking');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check backend connection on app start
    const checkBackend = async () => {
      try {
        const result = await testConnection();
        setBackendStatus('connected');
        console.log('✅ Backend connection successful:', result);
      } catch (error) {
        setBackendStatus('disconnected');
        console.warn('⚠️ Backend connection failed:', error.message);
      } finally {
        setLoading(false);
      }
    };

    checkBackend();
  }, []);

  if (loading) {
    return (
      <div className="app-loading">
        <div className="spinner"></div>
        <p>Initializing application...</p>
      </div>
    );
  }

  return (
    <Router>
      {/* Load Google Charts API */}
      <ChartLoader />
      
      <div className="app">
        <Header backendStatus={backendStatus} />
        
        <main className="main-content">
          <Routes>
            {/* Using your actual components */}
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/analyze" element={<ProductPage />} /> {/* Redirect analyze to ProductPage */}
            <Route path="/product/:productId" element={<Dashboard />} />
            
            {/* Stub routes for pages you don't have yet */}
            <Route path="/export/:productId" element={<div>Export Page - Coming Soon</div>} />
            <Route path="/settings" element={<div>Settings Page - Coming Soon</div>} />
            <Route path="/404" element={<div>404 - Page Not Found</div>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        
        <Footer />
      </div>
    </Router>
  );
}

export default App;