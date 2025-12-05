import React, { useMemo, useState } from "react";
import StarRating from "./StarRating";
import PaginationSimple from "./PaginationSimple";

// small sentiment helper (same logic you used)
function detectSentiment(text = "") {
  const t = (text || "").toLowerCase();
  const positiveWords = ["excellent", "awesome", "fabulous", "mind-blowing", "wow", "love", "perfect"];
  const neutralWords = ["good", "ok", "fine", "decent"];
  if (positiveWords.some(w => t.includes(w))) return "positive";
  if (neutralWords.some(w => t.includes(w))) return "neutral";
  return "negative";
}

export default function ReviewList({ reviews = [], pageSize = 6 }) {
  const [page, setPage] = useState(1);

  const totalPages = Math.max(1, Math.ceil(reviews.length / pageSize));

  const pageItems = useMemo(() => {
    const start = (page - 1) * pageSize;
    return reviews.slice(start, start + pageSize);
  }, [reviews, page, pageSize]);

  if (!reviews || reviews.length === 0) {
    return <div className="p-3 text-muted">No reviews available</div>;
  }

  return (
    <>
      <div className="d-grid gap-3">
        {pageItems.map((r) => {
          const sentiment = detectSentiment(r.review_text);
          const cls = sentiment === "positive" ? "card positive" : sentiment === "neutral" ? "card neutral" : "card negative";

          return (
            <div key={r.review_id ?? r.id ?? Math.random()} className={`${cls} my-2`}>
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <h6 className="fw-bold mb-0">{r.reviewer || r.author_name || "Anonymous"}</h6>
                    <small className="text-muted">{(r.date || r.review_date || "").split("T")[0]}</small>
                  </div>
                  <div>
                    <StarRating value={r.rating ?? 0} size={14} />
                  </div>
                </div>

                <div className="mt-2">
                  <p style={{ whiteSpace: "pre-wrap" }}>{r.review_text}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <PaginationSimple page={page} totalPages={totalPages} onChange={setPage} />
    </>
  );
}
