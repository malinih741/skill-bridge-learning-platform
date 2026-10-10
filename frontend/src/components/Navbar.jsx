import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const close = () => setOpen(false);

  const onLogout = async () => {
    close();
    await logout();
    navigate("/");
  };

  return (
    <header className="nav">
      <div className="container nav-inner">
        <Link to="/" className="brand" onClick={close}>
          <svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true">
            <path d="M2 20 Q14 2 26 20" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
            <path d="M2 24 H26" stroke="#F2B01E" strokeWidth="2.5" strokeLinecap="round" />
          </svg>
          SkillBridge
        </Link>
        <button className="nav-toggle" aria-expanded={open} aria-label="Toggle menu" onClick={() => setOpen(!open)}>
          Menu
        </button>
        <nav className={`nav-links ${open ? "open" : ""}`}>
          <NavLink to="/" end onClick={close}>Home</NavLink>
          <NavLink to="/courses" onClick={close}>Courses</NavLink>
          {user ? (
            <>
              <NavLink to="/dashboard" onClick={close}>My courses</NavLink>
              <span className="nav-user">Hi, {user.name}</span>
              <button className="btn btn-small" onClick={onLogout}>Log out</button>
            </>
          ) : (
            <>
              <NavLink to="/login" onClick={close}>Log in</NavLink>
              <Link to="/register" className="btn btn-small" onClick={close}>Create account</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
