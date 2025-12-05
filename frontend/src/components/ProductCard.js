import React from "react";
import { Card, Button } from "react-bootstrap";
import { Link } from "react-router-dom";

export default function ProductCard({ product }) {
  const name = product; // product is just a STRING

  return (
    <Card className="product-card p-3">
      <div className="d-flex gap-3 align-items-start">

        <span style={{ fontSize: "3rem" }}>📦</span>

        <div style={{ flex: 1 }}>
          <h5 className="mb-1" style={{ fontWeight: 700 }}>{name}</h5>

          <p className="text-muted mb-1">0 reviews</p>

          <div className="d-flex gap-2 align-items-center">
            <Button
              as={Link}
              to={`/product/${encodeURIComponent(name)}`}
              variant="primary"
              size="sm"
            >
              View
            </Button>

            <Button
              variant="outline-secondary"
              size="sm"
              onClick={() =>
                window.open(`https://www.google.com/search?q=${encodeURIComponent(name)}`)
              }
            >
              Search Web
            </Button>
          </div>
        </div>

      </div>
    </Card>
  );
}
