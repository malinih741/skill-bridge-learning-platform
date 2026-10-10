import { useState } from "react";
import { Link } from "react-router-dom";
import { submitProject } from "../services/api.js";

function Item({ done, children }) {
  return (
    <li className={done ? "check done" : "check"}>
      <span aria-hidden="true">{done ? "✓" : "○"}</span> {children}
      <span className="visually-hidden">{done ? " (done)" : " (not done yet)"}</span>
    </li>
  );
}

export default function CompletionPanel({ courseId, progress, onChanged }) {
  const { lessons, quizzes, project, certificate } = progress;
  const [form, setForm] = useState({
    repo_url: project ? project.repo_url : "",
    notes: project ? project.notes : "",
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const lessonsDone = lessons.total > 0 && lessons.done >= lessons.total;
  const quizzesDone = quizzes.passed >= quizzes.total;
  const approved = project && project.status === "approved";

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await submitProject(courseId, form);
      onChanged();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="panel">
      <h2>Get your certificate</h2>
      <ul className="checklist">
        <Item done={lessonsDone}>Complete every lesson ({lessons.done} of {lessons.total})</Item>
        <Item done={quizzesDone}>Pass every quiz ({quizzes.passed} of {quizzes.total})</Item>
        <Item done={approved}>Final project approved</Item>
      </ul>

      {certificate && (
        <p className="success">
          Congratulations! Your certificate number is <strong>{certificate.number}</strong>.{" "}
          <Link to={`/verify/${certificate.number}`}>View certificate</Link>
        </p>
      )}

      <h3>Final project</h3>
      {approved ? (
        <p className="success">
          Approved.{" "}
          <a href={project.repo_url} target="_blank" rel="noopener noreferrer">Open your project</a>
        </p>
      ) : (
        <>
          {project && project.status === "submitted" && (
            <p className="status">Submitted. Waiting for review. You can update the link below.</p>
          )}
          {project && project.status === "changes_requested" && (
            <p className="status status-error" role="status">
              Changes requested{project.feedback ? `: ${project.feedback}` : "."} Fix it and submit again.
            </p>
          )}
          <form className="form" onSubmit={onSubmit}>
            <label>Project link (for example your GitHub repository)
              <input
                type="url"
                name="repo_url"
                required
                placeholder="https://github.com/your-name/your-project"
                value={form.repo_url}
                onChange={onChange}
              />
            </label>
            <label>Notes for the reviewer (optional)
              <textarea name="notes" rows="3" maxLength="1000" value={form.notes} onChange={onChange} />
            </label>
            {error && <p className="error" role="alert">{error}</p>}
            <button className="btn" type="submit" disabled={busy}>
              {busy ? "Submitting…" : project ? "Update submission" : "Submit project"}
            </button>
          </form>
        </>
      )}
    </div>
  );
}
