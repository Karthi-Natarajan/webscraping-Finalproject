import React from "react";
import { Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import ProductPage from "./pages/ProductPage";
import Analytics from "./pages/Analytics";

export default function App() {
  return (
    <div style={{ marginTop: "0px" }}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/product/:name" element={<ProductPage />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/analytics/:name" element={<Analytics />} />
      </Routes>
    </div>
  );
}
