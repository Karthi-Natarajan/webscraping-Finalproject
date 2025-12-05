import React, { useEffect, useState } from "react";
import { getProducts } from "../api";
import ProductGrid from "../components/ProductGrid";
import Loader from "../components/Loader";
import SiteNav from "../components/SiteNav";   // <-- ADD THIS

export default function Home() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const p = await getProducts();
        setProducts(p || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <>
      {/* NAVBAR visible only on Home page */}
      <SiteNav />

      <div className="container py-5" style={{ marginTop: 100 }}>
        <div className="text-center mb-5">
          <h1 style={{ fontWeight: 800, fontSize: "2.2rem" }}>
            Discover product sentiment
          </h1>
          <p className="text-muted">
            Search for a product to view reviews and interactive sentiment charts.
          </p>
        </div>

        {loading ? (
          <Loader />
        ) : (
          <>
            <h5 className="mb-3">Popular & Suggested</h5>
            <ProductGrid products={products.slice(0, 9)} />
          </>
        )}
      </div>
    </>
  );
}
