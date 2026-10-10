import { useState } from "react";
import { Link } from "react-router-dom";

export default function Register() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = (e) => {
    e.preventDefault();
    if (!form.name || !form.email) return setError("Enter your name and email.");
    if (form.password.length < 8) return setError("Password must be at least 8 characters.");
    setError("");
    // Week 3: call POST /api/auth/register/
    alert("Register API will be connected in Week 3.");
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
        <button className="btn" type="submit">Create account</button>
      </form>
      <p>Already registered? <Link to="/login">Log in</Link></p>
    </section>
  );
}
