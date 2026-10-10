import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Verify() {
  const navigate = useNavigate();
  const [number, setNumber] = useState("");

  const onSubmit = (e) => {
    e.preventDefault();
    const value = number.trim();
    if (value) navigate(`/verify/${encodeURIComponent(value)}`);
  };

  return (
    <section className="container section narrow">
      <h1>Verify a certificate</h1>
      <p className="lead">Enter the certificate number to check that it is real.</p>
      <form className="form" onSubmit={onSubmit}>
        <label>Certificate number
          <input
            value={number}
            onChange={(e) => setNumber(e.target.value)}
            placeholder="SB-XXXXX-XXXXX"
            autoComplete="off"
          />
        </label>
        <button className="btn" type="submit">Verify</button>
      </form>
    </section>
  );
}
