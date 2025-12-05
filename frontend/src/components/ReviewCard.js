import React from 'react';

const ReviewCard = ({ review }) => {
  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return '#4CAF50';
      case 'negative': return '#FF5252';
      case 'neutral': return '#FFC107';
      default: return '#9E9E9E';
    }
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return '😊';
      case 'negative': return '😞';
      case 'neutral': return '😐';
      default: return '❓';
    }
  };

  const getSentimentLabel = (sentiment) => {
    if (!sentiment) return 'Unknown';
    return sentiment.charAt(0).toUpperCase() + sentiment.slice(1);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Date not available';
    
    try {
      const date = new Date(dateString);
      return isNaN(date.getTime()) 
        ? 'Invalid date' 
        : date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
          });
    } catch {
      return 'Invalid date';
    }
  };

  const formatRating = (rating) => {
    if (!rating) return null;
    
    // Handle both string and number ratings
    const numRating = typeof rating === 'string' 
      ? parseFloat(rating.replace(/[^0-9.]/g, '')) 
      : rating;
    
    if (isNaN(numRating)) return null;
    
    // Create star display
    const stars = '⭐'.repeat(Math.round(numRating));
    return (
      <div className="rating-display">
        <span className="stars">{stars}</span>
        <span className="rating-text">({numRating.toFixed(1)}/5)</span>
      </div>
    );
  };

  return (
    <div className="review-card">
      <div className="review-card-header">
        <div className="reviewer-info">
          <span className="reviewer-name">
            {review.reviewer || review.author || 'Anonymous Reviewer'}
          </span>
          <span className="review-date">{formatDate(review.date || review.timestamp)}</span>
        </div>
        
        <div className="review-meta">
          {formatRating(review.rating)}
          <span 
            className="sentiment-badge"
            style={{ backgroundColor: getSentimentColor(review.sentiment) }}
          >
            {getSentimentIcon(review.sentiment)} {getSentimentLabel(review.sentiment)}
          </span>
        </div>
      </div>
      
      {review.title && (
        <h4 className="review-title">{review.title}</h4>
      )}
      
      <div className="review-content">
        <p className="review-text">{review.text || review.content || 'No review text available'}</p>
      </div>
      
      {(review.verified || review.verifiedPurchase) && (
        <div className="review-verified">
          <span className="verified-badge">✓ Verified Purchase</span>
        </div>
      )}
      
      {review.helpful && (
        <div className="review-helpful">
          <span className="helpful-count">
            {review.helpful} {review.helpful === 1 ? 'person' : 'people'} found this helpful
          </span>
        </div>
      )}
    </div>
  );
};

export default ReviewCard;