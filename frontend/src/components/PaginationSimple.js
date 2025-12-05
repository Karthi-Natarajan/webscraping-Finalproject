import React from "react";

export default function PaginationSimple({ page, totalPages, onChange }) {
  if (totalPages <= 1) return null;
  const prev = () => onChange(Math.max(1, page - 1));
  const next = () => onChange(Math.min(totalPages, page + 1));
  return (
    <div className="d-flex gap-2 justify-content-center align-items-center my-3">
      <button className="btn btn-outline-secondary btn-sm" onClick={prev} disabled={page <= 1}>Prev</button>
      <div className="mx-2 text-muted">Page {page} / {totalPages}</div>
      <button className="btn btn-outline-secondary btn-sm" onClick={next} disabled={page >= totalPages}>Next</button>
    </div>
  );
}
