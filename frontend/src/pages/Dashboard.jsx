import { Link } from "react-router-dom";
import CourseCard from "../components/CourseCard.jsx";
import Status from "../components/Status.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import useFetch from "../hooks/useFetch.js";
import { getMyCertificates, getMyCourses } from "../services/api.js";

export default function Dashboard() {
  const { user } = useAuth();
  const { data: courses, loading, error } = useFetch(getMyCourses);
  const certificates = useFetch(getMyCertificates);

  return (
    <section className="container section">
      <h1>Welcome, {user.name}</h1>

      {certificates.data && certificates.data.length > 0 && (
        <>
          <h2>My certificates</h2>
          <ul className="cert-list">
            {certificates.data.map((c) => (
              <li key={c.number}>
                <strong>{c.course_title}</strong> · <Link to={`/verify/${c.number}`}>{c.number}</Link>
              </li>
            ))}
          </ul>
        </>
      )}

      <h2>My courses</h2>
      <Status loading={loading} error={error} />
      {courses && courses.length === 0 && (
        <p className="empty">
          You haven't enrolled in any course yet. <Link to="/courses">Browse courses</Link>
        </p>
      )}
      {courses && courses.length > 0 && (
        <div className="grid">
          {courses.map((c) => <CourseCard key={c.id} course={c} />)}
        </div>
      )}
    </section>
  );
}
