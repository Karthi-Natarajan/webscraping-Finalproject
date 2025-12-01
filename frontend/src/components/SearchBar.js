import React, { useState } from "react";

export default function SearchBar({ onSearch, loading }) {
  const [value, setValue] = useState("");

  const submit = () => {
    if (!value.trim()) return alert("Please enter a product name or URL");
    onSearch(value.trim());
  };

  return (
    <div className="search-bar">
      <input
        placeholder="Paste Amazon/Flipkart URL or search text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && submit()}
      />
      <button onClick={submit} disabled={loading}>
        {loading ? "Scraping..." : "Search"}
      </button>
    </div>
  );
}
