const API = "https://webscraping-finalproject.onrender.com";

export async function getProducts() {
  const res = await fetch(`${API}/products`);
  const data = await res.json();

  // backend returns an array of strings
  return Array.isArray(data) ? data : data.products || [];
}

export async function getReviews(productName) {
  const encoded = encodeURIComponent(productName);
  const res = await fetch(`${API}/reviews?product=${encoded}`);
  const data = await res.json();
  return Array.isArray(data) ? data : data.reviews || [];
}
