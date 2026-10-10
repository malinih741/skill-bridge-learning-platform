import { Link } from "react-router-dom";
import ProgressBar from "./ProgressBar.jsx";

export default function CourseCard({ course }) {
  const hasProgress = typeof course.completed_lessons === "number";
  return (
    <article className="course-card">
      <span className={`badge badge-${course.level.toLowerCase()}`}>{course.level}</span>
      <h3>{course.title}</h3>
      <p>{course.description}</p>
      {hasProgress ? (
        <ProgressBar done={course.completed_lessons} total={course.lessons} />
      ) : (
        <p className="meta">{course.lessons} lessons · {course.weeks} weeks</p>
      )}
      {hasProgress ? (
        <Link to={`/courses/${course.id}/learn`} className="btn">Continue learning</Link>
      ) : (
        <Link to={`/courses/${course.id}`} className="btn btn-outline">View course</Link>
      )}
    </article>
  );
}
