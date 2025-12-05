import React, { useState, useEffect } from "react";
import { Navbar, Nav, Container, Form, Button, ListGroup } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { getProducts } from "../api";

export default function SiteNav() {
  const navigate = useNavigate();

  const [query, setQuery] = useState("");
  const [products, setProducts] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [dark, setDark] = useState(false);
  const [open, setOpen] = useState(false);

  // Load product list once
  useEffect(() => {
    (async () => {
      const items = await getProducts();
      setProducts(items);
    })();
  }, []);

  // Dark mode toggle
  useEffect(() => {
    document.body.className = dark ? "bg-dark text-light" : "bg-light text-dark";
  }, [dark]);

  // Autocomplete filter
  useEffect(() => {
    if (!query.trim()) return setFiltered([]);

    const q = query.toLowerCase();
    const matches = products.filter(p => p.toLowerCase().includes(q));
    setFiltered(matches.slice(0, 7));

  }, [query, products]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    navigate(`/product/${encodeURIComponent(query.trim())}`);
    setQuery("");
    setFiltered([]);
  };

  const selectSuggestion = (name) => {
    navigate(`/product/${encodeURIComponent(name)}`);
    setQuery("");
    setFiltered([]);
  };

  return (
    <Navbar
      expand="lg"
      fixed="top"
      className={`modern-navbar shadow-sm ${dark ? "dark-nav" : ""}`}
    >
      <Container className="d-flex align-items-center">

        {/* BRAND LOGO */}
        <Navbar.Brand
          onClick={() => navigate("/")}
          className="brand-title"
          style={{ cursor: "pointer" }}
        >
          <span className="logo-icon">🛍️</span> SentimentShop
        </Navbar.Brand>

        <Navbar.Toggle onClick={() => setOpen(!open)} />

        <Navbar.Collapse in={open}>

          {/* CENTER SEARCH */}
          <div className="search-container position-relative mx-auto">
            <Form onSubmit={handleSubmit} className="d-flex">
              <Form.Control
                type="text"
                placeholder="Search products..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="search-input"
              />
              <Button type="submit" className="search-btn">Search</Button>
            </Form>

            {filtered.length > 0 && (
              <ListGroup className="autocomplete-box shadow-sm">
                {filtered.map((name, i) => (
                  <ListGroup.Item
                    key={i}
                    action
                    onClick={() => selectSuggestion(name)}
                  >
                    {name}
                  </ListGroup.Item>
                ))}
              </ListGroup>
            )}
          </div>

          {/* RIGHT SIDE */}
          <Nav className="ms-auto">
            <Nav.Link onClick={() => navigate("/analytics")} className="nav-link-modern">
              Analytics
            </Nav.Link>

            {/* DARK MODE BUTTON */}
            <Button
              onClick={() => setDark(!dark)}
              className="theme-toggle-btn"
              variant="outline-secondary"
            >
              {dark ? "🌙" : "☀️"}
            </Button>
          </Nav>

        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}
