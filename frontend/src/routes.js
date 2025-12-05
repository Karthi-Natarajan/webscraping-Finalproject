import React from 'react';
import { Routes, Route } from 'react-router-dom';
import App from './App';
import Home from './pages/Home';
import ProductPage from './pages/ProductPage';
import Dashboard from './pages/Dashboard';

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<App />}>
        <Route index element={<Home />} />
        <Route path="product/:id" element={<ProductPage />} />
        <Route path="dashboard/:id" element={<Dashboard />} />
        {/* Add more routes as needed */}
      </Route>
    </Routes>
  );
};

export default AppRoutes;