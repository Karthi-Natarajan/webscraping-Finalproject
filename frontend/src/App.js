import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import ProductPage from "./pages/ProductPage";
import Dashboard from "./pages/Dashboard";

export default function App(){
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home/>} />
        <Route path="/product/:id" element={<ProductPage/>} />
        <Route path="/dashboard/:id" element={<Dashboard/>} />
      </Routes>
    </BrowserRouter>
  );
}