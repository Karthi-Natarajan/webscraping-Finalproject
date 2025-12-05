const BASE_URL = "https://finalproject-backend-el6m.onrender.com";

// Test backend connection
export async function testConnection() {
  try {
    const res = await fetch(`${BASE_URL}/api/db-status`);
    if (!res.ok) throw new Error("Backend connection failed");
    return await res.json();
  } catch (error) {
    throw new Error(`Backend connection failed: ${error.message}`);
  }
}

// Get product metadata
export async function getProduct(productId) {
  try {
    const res = await fetch(`${BASE_URL}/api/product/${productId}`);
    if (!res.ok) throw new Error("Product not found");
    return await res.json();
  } catch (error) {
    throw new Error(`Error getting product: ${error.message}`);
  }
}

// Get reviews for a product
export async function getReviews(productId) {
  try {
    const res = await fetch(`${BASE_URL}/api/${productId}/reviews`);
    if (!res.ok) throw new Error("Error fetching reviews");
    return await res.json();
  } catch (error) {
    throw new Error(`Error fetching reviews: ${error.message}`);
  }
}

// Scrape reviews - CHANGED TO GET METHOD
export async function scrape(keyword, website) {
  try {
    // URL encode the parameters
    const url = `${BASE_URL}/api/scrape?keyword=${encodeURIComponent(keyword)}&website=${website}`;
    console.log('Scraping URL:', url);
    
    const res = await fetch(url);
    
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`Scrape failed: ${res.status} ${errorText}`);
    }
    
    return await res.json();
  } catch (error) {
    throw new Error(`Scrape error: ${error.message}`);
  }
}

// Save reviews to database
export async function saveReviews(productData, reviews) {
  try {
    const res = await fetch(`${BASE_URL}/api/save-reviews`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ product: productData, reviews })
    });
    if (!res.ok) throw new Error("Save reviews failed");
    return await res.json();
  } catch (error) {
    throw new Error(`Save reviews error: ${error.message}`);
  }
}

// Export data
export async function exportData(productId, format = "csv") {
  try {
    const res = await fetch(`${BASE_URL}/api/${productId}/export?format=${format}`);
    if (!res.ok) throw new Error("Export failed");
    return await res.blob();
  } catch (error) {
    throw new Error(`Export error: ${error.message}`);
  }
}

// Default export object for backward compatibility
const api = {
  testConnection,
  getProduct,
  getReviews,
  scrape,
  saveReviews,
  exportData
};

export default api;