import React from "react";

export default function ReviewCard({ review }) {
  const label = review.sentiment_label || "Neutral";

  const cls =
    label === "Positive"
      ? "sentiment positive"
      : label === "Negative"
      ? "sentiment negative"
      : "sentiment neutral";

  return (
    <div className="review-card">
      <div className="review-header">
        <strong>{review.title || "Review"}</strong>
        <span className={cls}>{label}</span>
      </div>

      <p>{review.text}</p>

      <div style={{ marginTop: "10px", fontSize: "12px", opacity: 0.8 }}>
        ⭐ {review.rating || "N/A"}
      </div>
    </div>
  );
}
