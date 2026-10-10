import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import ProgressBar from "../components/ProgressBar.jsx";
import Quiz from "../components/Quiz.jsx";
import Status from "../components/Status.jsx";
import useFetch from "../hooks/useFetch.js";
import { completeLesson, getCourseLessons, getCourseQuizzes } from "../services/api.js";

export default function Learn() {
  const { id } = useParams();
  const { data, loading, error } = useFetch(() => getCourseLessons(id), [id]);
  const quizzes = useFetch(() => getCourseQuizzes(id), [id]);
  const [done, setDone] = useState(new Set());
  const [activeId, setActiveId] = useState(null);
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState("");

  useEffect(() => {
    if (!data) return;
    setDone(new Set(data.lessons.filter((l) => l.completed).map((l) => l.id)));
    const firstTodo = data.lessons.find((l) => !l.completed) || data.lessons[0];
    setActiveId(firstTodo ? firstTodo.id : null);
  }, [data]);

  if (error && error.status === 403) {
    return (
      <section className="container section">
        <h1>Enrol first</h1>
        <p>You need to enrol in this course before you can open its lessons.</p>
        <Link to={`/courses/${id}`} className="btn">Go to course page</Link>
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

  const lessons = data.lessons;
  const index = lessons.findIndex((l) => l.id === activeId);
  const lesson = lessons[index];
  const isDone = lesson && done.has(lesson.id);

  const markComplete = async () => {
    setBusy(true);
    setActionError("");
    try {
      await completeLesson(lesson.id);
      setDone(new Set(done).add(lesson.id));
      if (lessons[index + 1]) setActiveId(lessons[index + 1].id);
    } catch (err) {
      setActionError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="container section">
      <p><Link to="/dashboard">← My courses</Link></p>
      <h1>{data.course.title}</h1>
      <ProgressBar done={done.size} total={lessons.length} />

      <div className="learn-grid">
        <ol className="lesson-list" aria-label="Lessons">
          {lessons.map((l) => (
            <li key={l.id}>
              <button
                className={`lesson-link ${l.id === activeId ? "active" : ""}`}
                onClick={() => setActiveId(l.id)}
              >
                <span aria-hidden="true">{done.has(l.id) ? "✓" : "○"}</span> {l.title}
                {done.has(l.id) && <span className="visually-hidden"> (completed)</span>}
              </button>
            </li>
          ))}
        </ol>

        <article className="lesson-body">
          {lesson ? (
            <>
              <h2>{lesson.title}</h2>
              <p className="lesson-text">{lesson.content}</p>
              {actionError && <p className="error" role="alert">{actionError}</p>}
              {isDone ? (
                <p className="success">Lesson completed.</p>
              ) : (
                <button className="btn" onClick={markComplete} disabled={busy}>
                  {busy ? "Saving…" : "Mark as complete"}
                </button>
              )}
            </>
          ) : (
            <p className="empty">This course has no lessons yet.</p>
          )}
        </article>
      </div>

      <h2>Quizzes</h2>
      <Status loading={quizzes.loading} error={quizzes.error} />
      {quizzes.data && quizzes.data.length === 0 && <p className="empty">No quizzes for this course yet.</p>}
      {quizzes.data && quizzes.data.map((q) => <Quiz key={q.id} quiz={q} />)}
    </section>
  );
}
