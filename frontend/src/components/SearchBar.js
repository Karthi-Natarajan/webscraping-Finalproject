import React, { useEffect, useState } from "react";
import { getProducts } from "../api";

export default function SearchBar({ onSelect }) {
  const [query, setQuery] = useState("");
  const [allProducts, setAllProducts] = useState([]);
  const [filtered, setFiltered] = useState([]);

  useEffect(() => {
    (async () => {
      const list = await getProducts();
      setAllProducts(list);
    })();
  }, []);

  useEffect(() => {
    if (!query.trim()) return setFiltered([]);

    const r = allProducts.filter((p) =>
      p.toLowerCase().includes(query.toLowerCase())
    );

    setFiltered(r);
  }, [query, allProducts]);

  return (
    <div className="position-relative w-100">
      <input
        className="form-control"
        placeholder="Search a product..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      {filtered.length > 0 && (
        <ul className="list-group position-absolute w-100 z-3 shadow">
          {filtered.map((name, i) => (
            <li
              key={i}
              className="list-group-item list-group-item-action"
              onClick={() => {
                onSelect(name);
                setQuery("");
                setFiltered([]);
              }}
            >
              {name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
