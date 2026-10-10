import { Link } from "react-router-dom";
import CourseCard from "../components/CourseCard.jsx";
import Status from "../components/Status.jsx";
import useFetch from "../hooks/useFetch.js";
import { getCourses } from "../services/api.js";

const steps = [
  { title: "Enrol", text: "Pick a course that matches your level." },
  { title: "Learn", text: "Finish short lessons and track your progress." },
  { title: "Prove it", text: "Pass the quiz and submit a real project." },
  { title: "Get certified", text: "Earn a certificate anyone can verify online." },
];

export default function Home() {
  const { data: courses, loading, error } = useFetch(getCourses);

  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <h1>Learn it. Build it. Get a certificate people can check.</h1>
            <p className="lead">
              Short web-development courses with quizzes and a hands-on project at the end of each one.
            </p>
            <div className="actions">
              <Link to="/courses" className="btn">Browse courses</Link>
              <Link to="/register" className="btn btn-outline">Create free account</Link>
            </div>
          </div>
          <ol className="path" aria-label="How SkillBridge works">
            {steps.map((s) => (
              <li key={s.title}>
                <strong>{s.title}</strong>
                <span>{s.text}</span>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="container section">
        <h2>Start with a beginner course</h2>
        <Status loading={loading} error={error} />
        {courses && (
          <div className="grid">
            {courses.slice(0, 3).map((c) => <CourseCard key={c.id} course={c} />)}
          </div>
        )}
      </section>
    </>
  );
}
