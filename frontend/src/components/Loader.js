import React from "react";

export default function Loader({ message = "Loading..." }) {
  return (
    <div className="text-center py-5">
      <div className="spinner-border" role="status" style={{ width: 48, height: 48 }}>
        <span className="visually-hidden">Loading...</span>
      </div>
      <div className="mt-2 text-muted">{message}</div>
    </div>
  );
}
