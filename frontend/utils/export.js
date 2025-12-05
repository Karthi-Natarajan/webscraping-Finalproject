import api from '../api';

export const analyzeAndSaveStats = async (productId, reviews) => {
  // Calculate sentiment stats
  const stats = calculateStats(reviews);
  
  // Save to backend
  await api.analyzeSentiment(productId, stats);
  
  return stats;
};

const calculateStats = (reviews) => {
  let positive = 0;
  let negative = 0;
  let neutral = 0;
  let totalRating = 0;
  
  reviews.forEach(review => {
    totalRating += review.rating || 0;
    const sentiment = review.sentiment || 'neutral';
    if (sentiment === 'positive') positive++;
    else if (sentiment === 'negative') negative++;
    else neutral++;
  });
  
  return {
    total: reviews.length,
    positive,
    negative,
    neutral,
    avgRating: reviews.length > 0 ? totalRating / reviews.length : 0,
    positivePercent: reviews.length > 0 ? (positive / reviews.length) * 100 : 0,
    negativePercent: reviews.length > 0 ? (negative / reviews.length) * 100 : 0,
    neutralPercent: reviews.length > 0 ? (neutral / reviews.length) * 100 : 0,
    lastUpdated: new Date().toISOString()
  };
};

export default {
  analyzeAndSaveStats
};