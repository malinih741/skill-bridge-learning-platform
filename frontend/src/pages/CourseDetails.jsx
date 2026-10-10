import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Status from "../components/Status.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import useFetch from "../hooks/useFetch.js";
import { enroll, getCourse } from "../services/api.js";

export default function CourseDetails() {
  const { id } = useParams();
  const { user } = useAuth();
  const { data: course, loading, error } = useFetch(() => getCourse(id), [id, user?.id]);
  const [justEnrolled, setJustEnrolled] = useState(false);
  const [busy, setBusy] = useState(false);
  const [enrollError, setEnrollError] = useState("");

  useEffect(() => {
    setJustEnrolled(false);
    setEnrollError("");
  }, [id]);

  const onEnroll = async () => {
    setBusy(true);
    setEnrollError("");
    try {
      await enroll(id);
      setJustEnrolled(true);
    } catch (err) {
      setEnrollError(err.message);
    } finally {
      setBusy(false);
    }
  };

  if (error && error.status === 404) {
    return (
      <section className="container section">
        <h1>Course not found</h1>
        <p>This course doesn't exist or isn't published yet.</p>
        <Link to="/courses" className="btn">Back to courses</Link>
      </section>
    );
  }

  if (loading || error) {
    return (
      <section className="container section">
        <Status loading={loading} error={error} />
      </section>
    );
  }

  const isEnrolled = justEnrolled || course.is_enrolled;

  return (
    <section className="container section narrow">
      <span className={`badge badge-${course.level.toLowerCase()}`}>{course.level}</span>
      <h1>{course.title}</h1>
      <p className="lead">{course.description}</p>
      <p className="meta">{course.lessons} lessons · {course.weeks} weeks · Final project: {course.project}</p>

      <h2>What you'll learn</h2>
      <ul className="outcomes">
        {course.outcomes.map((o) => <li key={o}>{o}</li>)}
      </ul>

      <h2>Lessons</h2>
      <ol className="outcomes">
        {course.lesson_list.map((l) => <li key={l.id}>{l.title}</li>)}
      </ol>

      {!user && <Link to="/login" className="btn">Log in to enrol</Link>}
      {user && isEnrolled && (
        <p className="success">
          You're enrolled. <Link to={`/courses/${id}/learn`}>Start learning</Link>
        </p>
      )}
      {user && !isEnrolled && (
        <button className="btn" onClick={onEnroll} disabled={busy}>
          {busy ? "Enrolling…" : "Enrol in this course"}
        </button>
      )}
      {enrollError && <p className="error" role="alert">{enrollError}</p>}
    </section>
  );
}
