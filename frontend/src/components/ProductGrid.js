import ProductCard from "./ProductCard";

export default function ProductGrid({ products }) {

  return (
    <div className="row g-4">
      {products.map((name, index) => (
        <div className="col-md-4" key={index}>
          <ProductCard product={name} />
        </div>
      ))}
    </div>
  );
}
