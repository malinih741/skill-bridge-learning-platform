import { useState } from "react";
import { Link } from "react-router-dom";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = (e) => {
    e.preventDefault();
    if (!form.email || !form.password) return setError("Enter your email and password.");
    setError("");
    // Week 3: call POST /api/auth/login/
    alert("Login API will be connected in Week 3.");
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
        <button className="btn" type="submit">Log in</button>
      </form>
      <p>New here? <Link to="/register">Create an account</Link></p>
    </section>
  );
}
