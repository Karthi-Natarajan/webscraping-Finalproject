import React from "react";

export default function StarRating({ value = 0, size = 16 }) {
  const stars = Math.round(Number(value) || 0);
  return (
    <div style={{ display: "inline-flex", gap: 6, alignItems: "center" }}>
      {Array.from({ length: 5 }).map((_, i) => (
        <svg
          key={i}
          width={size}
          height={size}
          viewBox="0 0 24 24"
          style={{ opacity: i < stars ? 1 : 0.25, transform: "translateY(-1px)" }}
        >
          <path
            fill={i < stars ? "#f6c84c" : "#cbd5e1"}
            d="M12 .587l3.668 7.431L24 9.748l-6 5.848L19.335 24 12 19.897 4.665 24 6 15.596 0 9.748l8.332-1.73z"
          />
        </svg>
      ))}
      <span style={{ fontSize: 13, color: "#374151", marginLeft: 6 }}>
        {Number(value) ? Number(value).toFixed(1) : "—"}
      </span>
    </div>
  );
}
