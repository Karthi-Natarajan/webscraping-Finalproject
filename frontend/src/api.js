import axios from "axios";

const API_BASE = "http://13.53.110.214:10000/api";


export default {
  scrape: (url, max_pages=3) => axios.post(`${API_BASE}/scrape`, { url, max_pages }),
  sentiment: (text) => axios.post(`${API_BASE}/sentiment`, { text }),
  getReviews: (productId, page=1, per_page=20) => axios.get(`${API_BASE}/product/${productId}/reviews`, { params: { page, per_page } }),
  getStats: (productId) => axios.get(`${API_BASE}/product/${productId}/stats`),
  export: (productId, format="csv") =>
    axios.get(`${API_BASE}/product/${productId}/export`, {
      params: { format },
      responseType: 'blob'
    })
};
