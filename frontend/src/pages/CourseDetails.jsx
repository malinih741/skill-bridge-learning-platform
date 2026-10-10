import { Link, useParams } from "react-router-dom";
import { courses } from "../data/courses.js";

export default function CourseDetails() {
  const { id } = useParams();
  const course = courses.find((c) => c.id === Number(id));

  if (!course) {
    return (
      <section className="container section">
        <h1>Course not found</h1>
        <p>This course doesn't exist or isn't published yet.</p>
        <Link to="/courses" className="btn">Back to courses</Link>
      </section>
    );
  }

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

      {/* Week 4: replace with real enrolment (POST /api/courses/{id}/enroll/) */}
      <Link to="/login" className="btn">Log in to enrol</Link>
    </section>
  );
}
