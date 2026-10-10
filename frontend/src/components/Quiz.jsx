import { useState } from "react";
import { submitQuiz } from "../services/api.js";

export default function Quiz({ quiz }) {
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const allAnswered = quiz.questions.every((q) => answers[q.id] !== undefined);

  const onSubmit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      setResult(await submitQuiz(quiz.id, answers));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const retry = () => {
    setAnswers({});
    setResult(null);
  };

  return (
    <form className="quiz" onSubmit={onSubmit}>
      <h3>{quiz.title}</h3>
      <p className="meta">
        Pass mark: {quiz.pass_mark}%
        {quiz.best_score !== null && ` · Your best score: ${quiz.best_score}%`}
        {quiz.passed && " · Passed"}
      </p>

      {quiz.questions.map((q, i) => {
        const wrong = result && result.results[q.id] === false;
        const right = result && result.results[q.id] === true;
        return (
          <fieldset key={q.id} className={`question ${wrong ? "wrong" : ""} ${right ? "right" : ""}`}>
            <legend>{i + 1}. {q.text}</legend>
            {q.options.map((option, index) => (
              <label key={index} className="option">
                <input
                  type="radio"
                  name={`q-${q.id}`}
                  checked={answers[q.id] === index}
                  disabled={!!result}
                  onChange={() => setAnswers({ ...answers, [q.id]: index })}
                />
                {option}
              </label>
            ))}
            {wrong && <p className="error">Not quite. Review the lesson and try again.</p>}
            {right && <p className="success-text">Correct</p>}
          </fieldset>
        );
      })}

      {error && <p className="error" role="alert">{error}</p>}

      {result ? (
        <div className={result.passed ? "success" : "status status-error"} role="status">
          You scored {result.score}% ({result.correct} of {result.total} correct).{" "}
          {result.passed ? "You passed!" : `You need ${result.pass_mark}% to pass.`}{" "}
          <button type="button" className="btn btn-small" onClick={retry}>Try again</button>
        </div>
      ) : (
        <button className="btn" type="submit" disabled={!allAnswered || busy}>
          {busy ? "Checking…" : "Submit answers"}
        </button>
      )}
    </form>
  );
}
