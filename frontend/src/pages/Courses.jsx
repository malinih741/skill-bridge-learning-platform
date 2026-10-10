import { useState } from "react";
import CourseCard from "../components/CourseCard.jsx";
import Status from "../components/Status.jsx";
import useFetch from "../hooks/useFetch.js";
import { getCourses } from "../services/api.js";

const levels = ["All", "Beginner", "Intermediate"];

export default function Courses() {
  const { data: courses, loading, error } = useFetch(getCourses);
  const [level, setLevel] = useState("All");
  const [query, setQuery] = useState("");

  const visible = (courses || []).filter(
    (c) =>
      (level === "All" || c.level === level) &&
      c.title.toLowerCase().includes(query.trim().toLowerCase())
  );

  return (
    <section className="container section">
      <h1>Courses</h1>
      <div className="filters">
        <input
          type="search"
          placeholder="Search courses"
          aria-label="Search courses"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="chips" role="group" aria-label="Filter by level">
          {levels.map((l) => (
            <button key={l} className={`chip ${level === l ? "active" : ""}`} onClick={() => setLevel(l)}>
              {l}
            </button>
          ))}
        </div>
      </div>

      <Status loading={loading} error={error} />
      {courses && visible.length === 0 && (
        <p className="empty">No courses match. Try a different search or level.</p>
      )}
      {courses && visible.length > 0 && (
        <div className="grid">
          {visible.map((c) => <CourseCard key={c.id} course={c} />)}
        </div>
      )}
    </section>
  );
}
