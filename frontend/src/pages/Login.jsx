import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!form.email || !form.password) return setError("Enter your email and password.");
    setError("");
    setBusy(true);
    try {
      await login(form.email, form.password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="container section narrow">
      <h1>Log in</h1>
      <form className="form" onSubmit={onSubmit} noValidate>
        <label>Email
          <input type="email" name="email" value={form.email} onChange={onChange} autoComplete="email" />
        </label>
        <label>Password
          <input type="password" name="password" value={form.password} onChange={onChange} autoComplete="current-password" />
        </label>
        {error && <p className="error" role="alert">{error}</p>}
        <button className="btn" type="submit" disabled={busy}>{busy ? "Logging in…" : "Log in"}</button>
      </form>
      <p>New here? <Link to="/register">Create an account</Link></p>
    </section>
  );
}
