import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <section className="container section">
      <h1>Page not found</h1>
      <p>Check the address or go back home.</p>
      <Link to="/" className="btn">Go home</Link>
    </section>
  );
}
