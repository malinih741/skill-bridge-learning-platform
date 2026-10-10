import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim()) return setError("Enter your name and email.");
    if (form.password.length < 8) return setError("Password must be at least 8 characters.");
    setError("");
    setBusy(true);
    try {
      await register(form.name.trim(), form.email.trim(), form.password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="container section narrow">
      <h1>Create your account</h1>
      <form className="form" onSubmit={onSubmit} noValidate>
        <label>Full name
          <input name="name" value={form.name} onChange={onChange} autoComplete="name" />
        </label>
        <label>Email
          <input type="email" name="email" value={form.email} onChange={onChange} autoComplete="email" />
        </label>
        <label>Password
          <input type="password" name="password" value={form.password} onChange={onChange} autoComplete="new-password" />
        </label>
        {error && <p className="error" role="alert">{error}</p>}
        <button className="btn" type="submit" disabled={busy}>{busy ? "Creating account…" : "Create account"}</button>
      </form>
      <p>Already registered? <Link to="/login">Log in</Link></p>
    </section>
  );
}
